import importlib.util
import io
import json
import struct
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("scrape_inspo.py")
SPEC = importlib.util.spec_from_file_location("scrape_inspo", MODULE_PATH)
scrape = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scrape)


class FakePage:
    def __init__(self, status=200, html=""):
        self.status = status
        self.html_content = html


class ScraperRegressionTests(unittest.TestCase):
    def test_route_registry_covers_every_cli_branch(self):
        import ast
        tree = ast.parse(MODULE_PATH.read_text())
        commands = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare) or not isinstance(node.left, ast.Name) or node.left.id != "cmd":
                continue
            for comparator in node.comparators:
                values = comparator.elts if isinstance(comparator, (ast.Tuple, ast.List)) else [comparator]
                commands.update(value.value for value in values
                                if isinstance(value, ast.Constant) and isinstance(value.value, str))
        commands.discard("routes")
        self.assertEqual(commands, set(scrape.ROUTE_REGISTRY))

    def test_route_kinds_match_the_research_receipt_vocabulary(self):
        self.assertEqual(scrape.ROUTE_REGISTRY["video"]["kind"], "video-source")
        self.assertEqual(scrape.ROUTE_REGISTRY["photo"]["kind"], "image-source")
        self.assertEqual(scrape.ROUTE_REGISTRY["t21"]["kind"], "interaction-source")

    def test_output_root_can_be_bound_to_an_isolated_run(self):
        with tempfile.TemporaryDirectory() as root, \
             patch.dict("os.environ", {"DESIGN_CRAFT_INSPO_DIR": root}):
            self.assertEqual(scrape._output_root(), str(Path(root).resolve()))

    def test_require_page_rejects_non_200_even_with_large_body(self):
        with self.assertRaises(SystemExit):
            scrape._require_page(FakePage(404, "x" * 9000), "https://example.test")

    def test_dribbble_uses_search_route_and_keeps_query_words(self):
        html = '<img src="https://cdn.dribbble.com/userupload/123/file/original-a.png">' + "x" * 6000
        fetcher = type("Fetcher", (), {"fetch": staticmethod(lambda url, **kwargs: FakePage(200, html))})
        with tempfile.TemporaryDirectory() as root, \
             patch.object(scrape, "OUT", root), \
             patch.object(scrape, "_browser_fetcher", return_value=fetcher), \
             patch.object(scrape, "_save", return_value=["shot.png"]) as save:
            result = scrape.dribbble("fitness dashboard", 3)
        self.assertEqual(result, ["shot.png"])
        called_url = fetcher.fetch.__func__.__closure__ if False else None
        self.assertIn("original-a.png", save.call_args.args[0][0])

    def test_dribbble_retries_a_challenge_with_the_dynamic_browser(self):
        html = '<img src="https://cdn.dribbble.com/userupload/123/file/original-a.png">' + "x" * 6000
        stealth = type("Stealth", (), {"fetch": staticmethod(
            lambda url, **kwargs: FakePage(202, "challenge"))})
        dynamic = type("Dynamic", (), {"fetch": staticmethod(
            lambda url, **kwargs: FakePage(200, html))})
        with tempfile.TemporaryDirectory() as root, \
             patch.object(scrape, "OUT", root), \
             patch.object(scrape, "_browser_fetcher",
                          side_effect=lambda name: stealth if name == "StealthyFetcher" else dynamic), \
             patch.object(scrape, "_save", return_value=["shot.png"]):
            self.assertEqual(scrape.dribbble("fitness", 3), ["shot.png"])

    def test_dribbble_keeps_motion_with_its_shot_page_and_title(self):
        html = """
        <li class="shot-thumbnail">
          <div class="js-thumbnail-base" data-video-teaser-large="https://cdn.dribbble.com/userupload/7/file/large-demo.mp4">
            <img src="https://cdn.dribbble.com/userupload/7/file/still-demo.png" alt="Kinetic product story">
          </div>
          <a class="shot-thumbnail-link" href="/shots/77-Kinetic-product-story">View</a>
          <div class="shot-title">Kinetic product story</div>
        </li>
        """ + "x" * 6000
        records = scrape._dribbble_items(html)
        video = next(item for item in records if item["url"].endswith(".mp4"))
        self.assertEqual(video["caption"], "Kinetic product story")
        self.assertEqual(video["page_url"], "https://dribbble.com/shots/77-Kinetic-product-story")

    def test_ranked_items_match_query_instead_of_returning_gallery_order(self):
        items = [
            {"title": "Luxury interiors", "tags": "architecture", "url": "a.mp4"},
            {"title": "Kinetic athlete training", "tags": "sports fitness", "url": "b.mp4"},
        ]
        ranked = scrape._rank_items(items, "fitness athlete")
        self.assertEqual(ranked[0]["url"], "b.mp4")
        self.assertNotIn("a.mp4", [item["url"] for item in ranked])

    def test_video_candidates_rank_caption_before_download(self):
        items = [
            {"url": "beauty.mp4", "caption": "Beauty product at a table",
             "page_url": "https://video.test/search/athlete-sprint-training"},
            {"url": "toy.mp4", "caption": "Toy unboxing in a close up shot"},
            {"url": "runner.mp4", "caption": "Athlete sprint training on a track"},
        ]
        ranked = scrape._rank_video_candidates(
            items, "track athlete sprint training close up stadium slow motion")
        self.assertEqual([item["url"] for item in ranked], ["runner.mp4"])

    def test_coverr_renditions_share_one_asset_key(self):
        high = "https://cdn.coverr.co/videos/clip-6488/1080p.mp4"
        low = "https://cdn.coverr.co/videos/clip-6488/360p.mp4"
        self.assertEqual(scrape._video_asset_key(high), scrape._video_asset_key(low))

    def test_gallery_fallback_keeps_adjacent_candidates_for_inspection(self):
        items = [
            {"title": "Kinetic fibre field", "url": "field.mp4"},
            {"title": "Scroll-linked product film", "url": "film.mp4"},
        ]
        candidates = scrape._rank_or_adjacent(items, "fitness recovery")
        self.assertEqual(candidates, items)

    def test_sixtyfps_route_downloads_motion_evidence_with_context(self):
        html = """
        <article><a href='/interaction/pulse-control'>
          <h2>Elastic pulse control</h2>
          <video src='https://framerusercontent.com/assets/pulse-control.mp4'></video>
        </a></article>
        """ + "x" * 4000
        fetcher = type("Fetcher", (), {"fetch": staticmethod(
            lambda url, **kwargs: FakePage(200, html))})
        with tempfile.TemporaryDirectory() as root, \
             patch.object(scrape, "OUT", root), \
             patch.object(scrape, "_browser_fetcher", return_value=fetcher), \
             patch.object(scrape, "_save", return_value=["pulse-control.mp4"]) as save:
            result = scrape.spa("sixtyfps", "elastic pulse control", 2)
        self.assertEqual(result, ["pulse-control.mp4"])
        self.assertIn("pulse-control.mp4", save.call_args.args[0][0])

    def test_palette_inputs_accept_exact_files_and_directories(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            first = root / "first.png"
            second = root / "second.jpg"
            ignored = root / "notes.txt"
            first.write_bytes(b"png")
            second.write_bytes(b"jpg")
            ignored.write_text("notes")
            self.assertEqual(
                scrape._palette_inputs([str(first), str(root)]),
                [first, second],
            )

    def test_palette_description_does_not_reject_a_single_hue(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "single-hue.png"
            Image.new("RGB", (100, 100), (190, 30, 30)).save(path)
            output = io.StringIO()
            with redirect_stdout(output):
                scrape.palettes([str(path)])
        records = json.loads(output.getvalue())
        self.assertEqual(records[0]["src"], str(path))
        self.assertEqual(records[0]["hue_spread"], 0.0)

    def test_react_bits_matches_natural_language_component_request(self):
        self.assertEqual(scrape._best_name("Magnet component", ["Magnet", "PixelTrail"]), "Magnet")

    def test_font_search_uses_tokens_not_exact_phrase(self):
        fonts = [
            {"name": "Satoshi", "category": "sans serif"},
            {"name": "Bespoke Stencil", "category": "display condensed"},
        ]
        ranked = scrape._rank_records(fonts, "condensed athletic display")
        self.assertEqual(ranked[0]["name"], "Bespoke Stencil")

    def test_nearest_media_card_does_not_absorb_sibling_cards(self):
        from lxml import html
        tree = html.fromstring("""
          <main><article><h2>Fitness kinetic study</h2><video src='fit.mp4'></video></article>
          <article><h2>Luxury hotel</h2><video src='hotel.mp4'></video></article></main>
        """)
        card = scrape._nearest_media_card(tree.xpath("//video")[0])
        self.assertIn("Fitness kinetic study", card["title"])
        self.assertNotIn("Luxury hotel", card["title"])

    def test_nearest_media_card_reads_lazy_video_and_resolves_page(self):
        from lxml import html
        tree = html.fromstring("""
          <article><a title='Zero' href='/sites/zero/'>
            <video data-src='https://cdn.test/zero.mp4'></video>
          </a><h2>Zero kinetic portfolio</h2></article>
        """)
        card = scrape._nearest_media_card(tree.xpath("//video")[0], "https://landing.test/")
        self.assertEqual(card["url"], "https://cdn.test/zero.mp4")
        self.assertEqual(card["page_url"], "https://landing.test/sites/zero/")

    def test_nearest_media_card_chooses_one_source_and_resolves_it(self):
        from lxml import html
        tree = html.fromstring("""
          <article><a href='/sites/zero/'>
            <video><source data-src='/media/zero.webm'><source src='/media/zero.mp4'></video>
          </a><h2>Zero kinetic portfolio</h2></article>
        """)
        card = scrape._nearest_media_card(tree.xpath("//video")[0], "https://landing.test/")
        self.assertEqual(card["url"], "https://landing.test/media/zero.webm")

    def test_video_card_keeps_context_when_it_contains_decorative_images(self):
        from lxml import html
        tree = html.fromstring("""
          <main><article><a href='/shots/pulse'>
            <img src='logo.png'><h2>Elastic pulse control</h2>
            <video src='pulse.mp4'></video><img src='badge.png'>
          </a></article><article><video src='other.mp4'></video></article></main>
        """)
        card = scrape._nearest_media_card(tree.xpath("//video")[0], "https://60fps.design/")
        self.assertIn("Elastic pulse control", card["title"])
        self.assertEqual(card["page_url"], "https://60fps.design/shots/pulse")

    def test_openverse_filters_semantically_unrelated_results(self):
        records = [
            {"title": "Waterfall in autumn", "tags": [{"name": "forest"}], "url": "water.jpg"},
            {"title": "Athlete in motion", "tags": [{"name": "runner"}], "url": "runner.jpg"},
        ]
        ranked = scrape._rank_openverse_results(records, "athlete editorial motion")
        self.assertEqual([item["url"] for item in ranked], ["runner.jpg"])

    def test_polyhaven_candidate_keeps_visual_and_physical_facts(self):
        record = scrape._polyhaven_candidate("models", "runner_statue", {
            "name": "Runner Statue", "description": "A scanned bronze runner",
            "thumbnail_url": "https://cdn.test/runner.png", "polycount": 12000,
            "dimensions": [1, 2, 3], "max_resolution": [4096, 4096],
        })
        self.assertEqual(record["preview_url"], "https://cdn.test/runner.png")
        self.assertEqual(record["polycount"], 12000)
        self.assertEqual(record["description"], "A scanned bronze runner")

    def test_photo_fallback_keeps_subject_instead_of_style_word(self):
        self.assertEqual(
            scrape._photo_queries("athlete editorial motion"),
            ["athlete editorial motion", "athlete motion", "athlete"],
        )

    def test_polyhaven_hdri_url_uses_the_real_case_sensitive_path(self):
        self.assertEqual(
            scrape._polyhaven_hdri_url("studio_small_09"),
            "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/studio_small_09_2k.hdr",
        )

    def test_21st_extracts_component_pages_and_previews_not_category_links(self):
        html = """
        <a href='/community/components/s/chart'>Charts</a>
        <a href='/@maker/components/vector-field/default'>
          <img src='https://cdn.21st.dev/maker/vector-field/default/preview.png'
               alt='Vector field interactive chart'>
          <h3>Vector Field</h3>
        </a>
        """
        items = scrape._t21_items(html, "https://21st.dev/community/components/s/chart")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["page_url"],
                         "https://21st.dev/@maker/components/vector-field/default")
        self.assertEqual(items[0]["url"],
                         "https://cdn.21st.dev/maker/vector-field/default/preview.png")

    def test_image_facts_measure_dimensions_instead_of_guessing_from_name(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "unknown.bin.png"
            Image.new("RGB", (321, 123)).save(path)
            facts = scrape._asset_facts(str(path))
        self.assertEqual((facts["width"], facts["height"]), (321, 123))
        self.assertEqual(facts["kind"], "image")

    def test_glb_facts_expose_scene_contents(self):
        document = json.dumps({"scenes": [{}], "nodes": [{}, {}], "meshes": [{}],
                               "materials": [{}, {}], "animations": [{}]}).encode()
        document += b" " * ((4 - len(document) % 4) % 4)
        payload = (b"glTF" + struct.pack("<II", 2, 20 + len(document))
                   + struct.pack("<II", len(document), 0x4E4F534A) + document)
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "scene.glb"
            path.write_bytes(payload)
            facts = scrape._asset_facts(str(path))
        self.assertEqual(facts["meshes"], 1)
        self.assertEqual(facts["animations"], 1)

    def test_github3d_relevance_rejects_category_only_repository(self):
        category_only = {"name": "TrainSync", "description": "Athlete training and recovery app",
                         "topics": [], "stargazers_count": 1}
        spatial = {"name": "BodyField", "description": "Interactive Three.js shader field",
                   "topics": ["webgl"], "stargazers_count": 1}
        self.assertEqual(scrape._github3d_relevance(category_only, "athlete training")[0], 0)
        self.assertGreater(scrape._github3d_relevance(spatial, "athlete training")[0], 0)

    def test_github3d_broadens_by_dropping_overconstrained_terms(self):
        calls = []
        candidate = {"name": "KineticField", "description": "Interactive Three.js sculpture",
                     "topics": ["threejs", "webgl"], "stargazers_count": 42,
                     "html_url": "https://github.com/example/kinetic-field", "homepage": "",
                     "language": "JavaScript"}

        def fake_github(url):
            calls.append(url)
            return {"items": [candidate]} if "kinetic%20threejs" in url else {"items": []}

        with tempfile.TemporaryDirectory() as root, patch.object(scrape, "OUT", root), \
             patch.object(scrape, "_gh", side_effect=fake_github), redirect_stdout(io.StringIO()):
            scrape.github3d("abstract kinetic sculpture glb", 6)
        self.assertTrue(any("kinetic%20threejs" in url for url in calls))

    def test_github3d_reports_request_failure_instead_of_empty_results(self):
        with patch.object(scrape, "_gh", side_effect=RuntimeError("rate limited")):
            with self.assertRaisesRegex(SystemExit, "search failed"):
                scrape.github3d("kinetic sculpture", 6)

    def test_repository_inventory_keeps_large_models_and_html(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "index.html").write_text("<main></main>")
            Path(root, "hero.glb").write_bytes(b"x" * 400_000)
            Path(root, ".git").mkdir()
            Path(root, ".git", "ignored.glb").write_bytes(b"x")
            records = scrape._repository_inventory(root)
        paths = {record["path"] for record in records}
        self.assertIn("index.html", paths)
        self.assertIn("hero.glb", paths)
        self.assertNotIn(".git/ignored.glb", paths)

    def test_caption_uses_nearby_structured_name_not_raw_markup(self):
        url = "https://cdn.test/runner.mp4"
        document = '{"contentUrl":"' + url + '","name":"Runner crosses the city"}'
        self.assertEqual(scrape._caption_near_url(document, url), "Runner crosses the city")

    def test_caption_prefers_nearest_title_before_url_over_next_record(self):
        url = "https://cdn.test/cliff/1080p.mp4"
        document = ('{"title":"Silhouette on coastal cliffs","urls":{"mp4":"' + url +
                    '"}}, {"title":"Motion control","description":"Athlete sprint tool"}')
        self.assertEqual(scrape._caption_near_url(document, url),
                         "Silhouette on coastal cliffs")

    def test_save_reuses_a_source_url_across_query_folders(self):
        with tempfile.TemporaryDirectory() as root, patch.object(scrape, "OUT", root):
            first = Path(root, "video-first")
            first.mkdir()
            asset = first / "clip.mp4"
            asset.write_bytes(b"x" * 4000)
            digest = __import__("hashlib").md5(asset.read_bytes()).hexdigest()
            Path(first, "_manifest.json").write_text(json.dumps({"items": [{
                "local_path": str(asset), "source_url": "https://cdn.test/clip.mp4",
                "content_md5": digest,
            }]}))
            saved = scrape._save(["https://cdn.test/clip.mp4"], "video-second", 1)
        self.assertEqual(saved, [str(asset)])

    def test_save_uses_response_type_when_url_has_no_extension(self):
        class Headers:
            @staticmethod
            def get_content_type():
                return "image/jpeg"

        class Response:
            headers = Headers()

            @staticmethod
            def read():
                return b"\xff\xd8\xff" + b"x" * 4000

        with tempfile.TemporaryDirectory() as root, patch.object(scrape, "OUT", root), \
             patch.object(scrape.urllib.request, "urlopen", return_value=Response()):
            saved = scrape._save(["https://cdn.test/image?id=7"], "selected", 1)
        self.assertEqual(Path(saved[0]).suffix, ".jpg")

    def test_save_rejects_html_page_as_direct_asset(self):
        class Headers:
            @staticmethod
            def get_content_type():
                return "text/html"

        class Response:
            headers = Headers()

            @staticmethod
            def read():
                return b"<html>" + b"x" * 4000

        with tempfile.TemporaryDirectory() as root, patch.object(scrape, "OUT", root), \
             patch.object(scrape.urllib.request, "urlopen", return_value=Response()):
            self.assertEqual(scrape._save(["https://example.test/page"], "selected", 1), [])


if __name__ == "__main__":
    unittest.main()
