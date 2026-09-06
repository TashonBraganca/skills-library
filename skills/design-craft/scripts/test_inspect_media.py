import importlib.util
import json
import struct
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("inspect_media.py")
SPEC = importlib.util.spec_from_file_location("inspect_media", MODULE_PATH)
media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media)


class MediaInspectionTests(unittest.TestCase):
    def test_directory_input_expands_supported_media_recursively(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "assets"
            nested = folder / "nested"
            nested.mkdir(parents=True)
            (folder / "clip.mp4").write_bytes(b"video")
            (nested / "still.png").write_bytes(b"image")
            (nested / "light.hdr").write_bytes(b"texture")
            (nested / "notes.txt").write_text("ignore")
            paths = media.expand_inputs([str(folder)])
            self.assertEqual(paths, [(folder / "clip.mp4").resolve(),
                                     (nested / "light.hdr").resolve(),
                                     (nested / "still.png").resolve()])

    def test_hdr_inspection_creates_a_tonemapped_preview(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "light.hdr"
            path.write_bytes(b"hdr")
            destination = Path(root) / "inspection" / "light-texture-preview.jpg"
            with patch.object(media.subprocess, "run") as run:
                report = media.inspect_texture(path, Path(root) / "inspection")
            self.assertEqual(report["inspection_output"], str(destination))
            self.assertEqual(report["facts"]["format"], "hdr")
            run.assert_called_once()

    def test_samples_cover_opening_middle_and_ending(self):
        samples = media.sample_times(20, 6)
        self.assertLess(samples[0], 1)
        self.assertTrue(any(8 < sample < 12 for sample in samples))
        self.assertGreater(samples[-1], 19)
        self.assertEqual(samples, sorted(samples))

    def test_inspection_creates_its_output_directory(self):
        facts = {"format": {"duration": "10", "size": "1"},
                 "streams": [{"r_frame_rate": "24/1", "width": 10, "height": 10}]}
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "missing" / "frames"
            with patch.object(media, "probe", return_value=facts), \
                 patch.object(media.subprocess, "run"):
                report = media.inspect_video(Path(root) / "clip.mp4", output)
            self.assertTrue(output.is_dir())
            self.assertEqual(Path(report["timeline"]).parent, output)

    def test_image_inspection_reports_dimensions_and_writes_preview(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "still.png"
            Image.new("RGB", (640, 360), "navy").save(path)
            report = media.inspect_asset(path, Path(root) / "inspection")
            self.assertEqual(report["facts"]["width"], 640)
            self.assertTrue(Path(report["inspection_output"]).is_file())

    def test_inspection_updates_the_download_manifest(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "inspo" / "photos"
            folder.mkdir(parents=True)
            path = folder / "still.png"
            Image.new("RGB", (80, 40), "red").save(path)
            manifest = folder / "_manifest.json"
            manifest.write_text(json.dumps({"items": [{"local_path": str(path),
                                                        "inspection_status": "pending"}]}))
            report = media.inspect_asset(path, Path(root) / "inspection")
            updated = media.update_manifest(report)
            item = json.loads(manifest.read_text())["items"][0]
            self.assertEqual(updated, str(manifest))
            self.assertEqual(item["inspection_status"], "inspected")
            self.assertTrue(item["inspection_output"].endswith("-preview.jpg"))

    def test_model_inspection_uses_rendered_preview_when_available(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "athlete.glb"
            model_json = json.dumps({"scenes": [{}], "nodes": [{}], "meshes": [{}],
                                     "materials": [{}], "animations": [{}]}).encode()
            model_json += b" " * ((4 - len(model_json) % 4) % 4)
            path.write_bytes(b"glTF" + struct.pack("<II", 2, 20 + len(model_json)) +
                             struct.pack("<II", len(model_json), 0x4E4F534A) + model_json)
            preview = Path(root) / "inspection" / "athlete-model-preview.png"
            with patch.object(media, "render_model", return_value=preview):
                report = media.inspect_model(path, Path(root) / "inspection")
            self.assertEqual(report["inspection_output"], str(preview))
            self.assertNotIn("render_required", report)

    def test_failed_model_render_is_not_marked_inspected(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "inspo" / "models"
            folder.mkdir(parents=True)
            path = folder / "scene.gltf"
            path.write_text(json.dumps({"scenes": [{}], "nodes": [], "meshes": []}))
            manifest = folder / "_manifest.json"
            manifest.write_text(json.dumps({"items": [{"local_path": str(path),
                                                        "inspection_status": "pending"}]}))
            with patch.object(media, "render_model", return_value=None):
                report = media.inspect_model(path, Path(root) / "inspection")
            media.update_manifest(report)
            item = json.loads(manifest.read_text())["items"][0]
            self.assertEqual(item["inspection_status"], "needs_visual_inspection")
            self.assertIn("inspection_error", item)


if __name__ == "__main__":
    unittest.main()
