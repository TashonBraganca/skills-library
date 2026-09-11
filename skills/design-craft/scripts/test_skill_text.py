import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]


def normalized(path):
    return " ".join(path.read_text().split())


class SkillTextTests(unittest.TestCase):
    def test_research_gate_triggers_handoff_instead_of_more_unassigned_research(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("RESEARCH GATE PASSED", text)

    def test_completion_record_separates_product_truth_from_construction_reference(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("direct-peer product truths and adjacent-work construction rules", text)

    def test_receipt_does_not_replace_the_full_research_record(self):
        text = (SKILL_ROOT / "references" / "research-pipeline.md").read_text()
        self.assertIn("an index, not a replacement", text)

    def test_direction_waits_for_finished_work_and_candidate_material(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
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

    def test_viable_material_must_be_judged_in_its_supporting_role(self):
        text = normalized(SKILL_ROOT / "SKILL.md")
        self.assertIn("cannot be rejected merely because it does not lead", text)
        self.assertIn("strongest supporting role", text)

    def test_passive_texture_cannot_replace_a_viable_active_spatial_source(self):
        text = normalized(SKILL_ROOT / "SKILL.md")
        self.assertIn("a passive texture does not close that job", text)
        self.assertIn("another active construction does the job better", text)

    def test_lead_video_must_hold_up_at_its_displayed_crop(self):
        text = normalized(SKILL_ROOT / "SKILL.md")
        self.assertIn("becomes visibly soft or generic at its intended crop", text)

    def test_applicable_evidence_families_are_checked_before_direction(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("required comparisons, not required output ingredients", text)
        self.assertIn("retry it with the source's vocabulary", text)

    def test_original_effect_cannot_replace_uninspected_source_families(self):
        text = normalized(SKILL_ROOT / "SKILL.md")
        self.assertIn("does not close an unsearched evidence family", text)

    def test_interaction_research_is_source_neutral_and_job_led(self):
        text = normalized(SKILL_ROOT / "SKILL.md")
        self.assertIn("inspect relevant component and interaction sources", text)
        self.assertIn("Inspect React Bits as a first-class candidate", text)
        self.assertIn("record why the chosen source performs that job better", text)
        self.assertNotIn("Carry at least one suitable React Bits component", text)

    def test_intake_names_action_audience_objection_and_proof(self):
        text = normalized(SKILL_ROOT / "SKILL.md")
        self.assertIn("primary action", text)
        self.assertIn("strongest objection", text)
        self.assertIn("available proof", text)

    def test_build_ends_with_one_visual_reconciliation(self):
        text = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn("one visual reconciliation", text)
        self.assertIn("Repeat the comparison", text)
        self.assertNotIn("Run the project, use every important control", text)

    def test_selection_uses_rendered_comparisons_not_prose(self):
        text = normalized(SKILL_ROOT / "SKILL.md")
        self.assertIn("rendered ensemble candidates", text)
        self.assertIn("strongest alternative", text)
        self.assertIn("same content, viewport, and loaded material", text)

    def test_evidence_gate_precedes_direction_and_asset_promotion(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("--phase evidence", text)
        self.assertIn("Before naming the direction", text)
        self.assertIn("move selected files into the build", text)

    def test_receipt_keeps_the_generated_schema_and_classifies_the_brief(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("write the generated schema to `research/research-receipt.json`", text)
        self.assertIn("Keep its family names and fields", text)
        self.assertIn("Set both brief classifications from the requested implementation", text)

    def test_selected_active_material_keeps_its_defining_behavior(self):
        text = (SKILL_ROOT / "SKILL.md").read_text()
        self.assertIn("Treat each selected active source as a behavior contract", text)
        self.assertIn("A static proxy cannot prove active material", text)
        self.assertIn("compare the source and proof in the same role", text)

    def test_research_completion_runs_the_machine_gate(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("scripts/research_gate.py research/research-receipt.json", text)
        self.assertIn("Implementation begins only after this command prints", text)

    def test_research_handoff_keeps_full_evidence_without_replaying_the_transcript(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("Write the complete receipt once after inspection", text)
        self.assertIn("patch only the fields named by the gate", text)
        self.assertIn("Keep the original evidence on disk", text)
        self.assertIn("Reopen only the files needed for the current decision", text)

    def test_pre_code_proof_uses_the_actual_selected_ensemble(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("Give every shortlisted item a stable ID", text)
        self.assertIn("proof must contain the selected files and behaviors together", text)
        self.assertIn("category names or source families", text)

    def test_selection_records_the_rendered_decision_before_more_proof_technical_work(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("After rendering a candidate, record its proof path and inspection evidence before", text)
        self.assertIn("Do not investigate browser tooling or proof mechanics beyond what decides the composition", text)

    def test_search_queries_follow_observed_construction_evidence(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("camera, geometry, material, movement, or interaction terms observed", text)
        self.assertIn("record the evidence that supplied those terms", text)

    def test_comparison_changes_material_not_only_layout(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("different shortlisted material", text)
        self.assertIn("same assets in a different arrangement", text)

    def test_proof_directly_loads_selected_material(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("directly load each selected file or source entry point", text)
        self.assertIn("handmade imitation does not count", text)

    def test_plan_choreographs_selected_material_before_build(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("placement, entry, response, and exit", text)

    def test_complete_gate_writes_compact_build_handoff(self):
        text = normalized(SKILL_ROOT / "references" / "research-pipeline.md")
        self.assertIn("--handoff research/construction-handoff.json", text)
        self.assertIn("Build from the compact handoff", text)


if __name__ == "__main__":
    unittest.main()
