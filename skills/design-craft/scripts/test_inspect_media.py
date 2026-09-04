import importlib.util
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
