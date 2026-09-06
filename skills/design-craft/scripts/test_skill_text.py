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

    def test_direction_waits_for_finished_work_and_candidate_material(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("Do not set the visual direction until", text)

    def test_pre_code_check_names_recurring_generated_defaults(self):
        text = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn("recurring generated defaults", text)

    def test_pipeline_can_generate_brief_specific_candidate_material(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("generate brief-specific candidate material", text)

    def test_pipeline_ranks_combinations_before_direction(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("Rank viable combinations before choosing the direction", text)

    def test_unshippable_reference_does_not_close_its_material_job(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("keep its material job open", text)
        self.assertIn("same displayed role", text)


if __name__ == "__main__":
    unittest.main()
