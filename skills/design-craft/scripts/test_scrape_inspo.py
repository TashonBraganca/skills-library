import importlib.util
import json
import struct
import tempfile
import unittest
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
    def test_require_page_rejects_non_200_even_with_large_body(self):
        with self.assertRaises(SystemExit):
            scrape._require_page(FakePage(404, "x" * 9000), "https://example.test")

    def test_dribbble_uses_search_route_and_keeps_query_words(self):
        html = '<img src="https://cdn.dribbble.com/userupload/123/file/original-a.png">' + "x" * 6000
        fetcher = type("Fetcher", (), {"fetch": staticmethod(lambda url, **kwargs: FakePage(200, html))})
        with patch.object(scrape, "_browser_fetcher", return_value=fetcher), \
             patch.object(scrape, "_save", return_value=["shot.png"]) as save:
            result = scrape.dribbble("fitness dashboard", 3)
        self.assertEqual(result, ["shot.png"])
        called_url = fetcher.fetch.__func__.__closure__ if False else None
        self.assertIn("original-a.png", save.call_args.args[0][0])

    def test_ranked_items_match_query_instead_of_returning_gallery_order(self):
        items = [
            {"title": "Luxury interiors", "tags": "architecture", "url": "a.mp4"},
            {"title": "Kinetic athlete training", "tags": "sports fitness", "url": "b.mp4"},
        ]
        ranked = scrape._rank_items(items, "fitness athlete")
        self.assertEqual(ranked[0]["url"], "b.mp4")
        self.assertNotIn("a.mp4", [item["url"] for item in ranked])

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


if __name__ == "__main__":
    unittest.main()
