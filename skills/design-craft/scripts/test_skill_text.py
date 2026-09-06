import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]


class SkillTextTests(unittest.TestCase):
    def test_research_gate_triggers_handoff_instead_of_more_unassigned_research(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("Once these conditions are met, write the receipt and begin implementation", text)

    def test_completion_record_separates_product_truth_from_construction_reference(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("direct-peer product truths and adjacent-work construction rules", text)

    def test_receipt_does_not_replace_the_full_research_record(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("an index, not a replacement", text)


if __name__ == "__main__":
    unittest.main()
