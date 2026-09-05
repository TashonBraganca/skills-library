import importlib.util
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("inspect_media.py")
SPEC = importlib.util.spec_from_file_location("inspect_media", MODULE_PATH)
media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media)


class MediaInspectionTests(unittest.TestCase):
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
        import json
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


if __name__ == "__main__":
    unittest.main()
