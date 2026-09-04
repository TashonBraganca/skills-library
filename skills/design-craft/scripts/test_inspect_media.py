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


if __name__ == "__main__":
    unittest.main()
