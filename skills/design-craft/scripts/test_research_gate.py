import json
import tempfile
import unittest
from pathlib import Path

import research_gate


def valid_receipt(root):
    proof = root / "proof.png"
    proof.write_bytes(b"proof")
    runnable_proof = root / "proof.html"
    runnable_proof.write_text("<canvas></canvas><button>change state</button>")
    alternative = root / "alternative.png"
    alternative.write_text('<video src="film.mp4"></video><script type="module" src="active.js"></script>')
    supporting = root / "supporting.png"
    supporting.write_text('<video src="film.mp4"></video><script type="module" src="spatial.js"></script>')
    inspected = root / "proof-inspection.txt"
    inspected.write_text("viewed at full composition size")
    asset = root / "active.js"
    asset.write_text("export default function active() {}")
    spatial = root / "spatial.js"
    spatial.write_text("export default function spatial() {}")
    film = root / "film.mp4"
    film.write_bytes(b"video")
    runnable_proof.write_text('<canvas></canvas><button>change state</button><script type="module" src="active.js"></script><script type="module" src="spatial.js"></script>')
    source_read = root / "active-source-notes.md"
    source_read.write_text("input, response, timing and dependencies inspected")
    receipt = {
        "brief": {"interaction_heavy": True, "react_work": True},
        "families": {
            "product_truth": {"applicable": True, "status": "selected", "attempts": [{"source": "peer", "query": "training recovery", "construction_job": "learn the real daily planning state", "evidence": [str(source_read)]}]},
            "finished_reference": {"applicable": True, "status": "selected", "attempts": [{"source": "adjacent-work", "query": "controlled effort interface", "construction_job": "resolve hierarchy and material placement", "evidence": [str(proof)]}]},
            "finished_moving_work": {"applicable": True, "status": "selected", "attempts": [{"source": "motion", "query": "controlled exertion sequence", "construction_job": "learn a continuous opening and payoff", "evidence": [str(proof)]}]},
            "time_based_material": {"applicable": True, "status": "rejected", "reason": "Both inspected candidates obscured live training state at the required crop.", "attempts": [{"source": "video", "query": "interval pacing footage", "construction_job": "carry exertion through the opening scene", "evidence": [str(proof)]}, {"source": "generated-study", "query": "interval pacing loop", "construction_job": "carry exertion through the opening scene", "evidence": [str(inspected)]}]},
            "spatial_interaction": {"applicable": True, "status": "selected", "attempts": [{"source": "spatial", "query": "training force field", "construction_job": "make readiness alter the page geometry", "evidence": [str(proof)]}]},
            "interaction_implementation": {"applicable": True, "status": "selected", "attempts": [{"source": "react-bits", "query": "direct manipulation", "construction_job": "control readiness with elastic response", "evidence": [str(asset), str(source_read)]}, {"source": "codrops", "query": "state driven canvas", "construction_job": "connect readiness to the visual field", "evidence": [str(source_read)]}]},
        },
        "proof": {"path": str(runnable_proof), "kind": "runnable", "inspected": True,
                  "inspection_evidence": str(inspected), "included_material": ["control", "field"],
                  "bindings": [
                      {"material_id": "control", "implementation_path": str(runnable_proof), "load_reference": "active.js", "kind": "direct"},
                      {"material_id": "field", "implementation_path": str(runnable_proof), "load_reference": "spatial.js", "kind": "direct"},
                  ]},
        "combinations": [{"id": "field-led", "candidates": ["control", "field"], "roles": {"control": "supporting", "field": "lead"}, "relationship": "The control changes the field geometry and the training prescription.", "outcome": "selected", "proof": str(proof)}, {"id": "film-led", "candidates": ["control", "film"], "roles": {"control": "supporting", "film": "lead"}, "relationship": "The control changes the film treatment while the field geometry is absent.", "outcome": "rejected", "proof": str(alternative)}, {"id": "film-supporting", "candidates": ["control", "field", "film"], "roles": {"control": "supporting", "field": "lead", "film": "supporting"}, "relationship": "The film supports the displaced field but weakens the field and control relationship.", "outcome": "rejected", "proof": str(supporting)}],
        "selection_review": {"winner": "field-led", "strongest_alternative": "film-led", "shared_conditions": "Same content, viewport, loaded assets, and product state.", "winning_reason": "The field-led construction makes readiness spatially legible and binds the control to the prescription.", "candidates": [{"id": "field-led", "proof": str(proof), "first_notice": "The changing field grade and runner relationship.", "material_interactions": "Dragging the control changes field geometry and the prescription together.", "ordinary_without": "Without the field, the control becomes a familiar isolated slider.", "spatial_temporal_case": "The field opens flat, rises with effort, and settles after release."}, {"id": "film-led", "proof": str(alternative), "first_notice": "The moving training film and load response.", "material_interactions": "The control changes the film treatment while the field is absent.", "ordinary_without": "Without the film, the control becomes an isolated slider.", "spatial_temporal_case": "The film establishes time, but it cannot make readiness spatially legible."}]},
        "material_candidates": [
            {"id": "control", "decision": "selected", "role": "supporting", "source": "react-bits", "source_kind": "interaction-source", "path": str(asset), "facts": {"bytes": asset.stat().st_size, "type": "source"}, "inspection_evidence": str(source_read), "job": "Control the main training state.", "relationships": ["field"], "irreplaceable_property": "Its overshoot exposes the effort boundary.", "removal_effect": "The field and plan lose their shared response.", "implementation_medium": "React component with spring motion", "adaptation_boundary": "Preserve direct manipulation and visible elastic overshoot in the combined state change.", "active": True, "behavior_contract": {"input": "horizontal pointer drag", "response": "field and plan change together", "timing": "spring settles after release", "defining_property": "elastic overshoot remains visible", "proof": str(runnable_proof)}},
            {"id": "field", "decision": "selected", "role": "lead", "source": "github-3d", "source_kind": "spatial-source", "path": str(spatial), "facts": {"bytes": spatial.stat().st_size, "type": "source"}, "inspection_evidence": str(source_read), "job": "Make readiness alter the page geometry.", "relationships": ["control"], "irreplaceable_property": "Its displacement turns readiness into visible grade.", "removal_effect": "The control loses the surface that explains its state.", "implementation_medium": "WebGL displaced mesh", "adaptation_boundary": "Preserve depth, mesh displacement, and state-driven geometry rather than drawing a flat proxy.", "active": True, "behavior_contract": {"input": "readiness state change", "response": "surface grade changes with the prescription", "timing": "surface settles after the control", "defining_property": "state remains spatially legible", "proof": str(runnable_proof)}},
            {"id": "film", "decision": "rejected", "role": "lead", "source": "training-film", "source_kind": "video-source", "path": str(film), "facts": {"bytes": film.stat().st_size, "type": "video", "width": 1280, "height": 720}, "inspection_evidence": str(source_read), "job": "Carry effort through moving track footage.", "relationships": ["control"], "irreplaceable_property": "The camera movement makes exertion continuous.", "removal_effect": "The alternative loses its temporal evidence.", "implementation_medium": "HTML video", "adaptation_boundary": "Preserve the moving athlete and track geometry in the intended crop.", "display": {"width": 640, "height": 360, "treatment": "literal"}, "active": True, "behavior_contract": {"input": "training load change", "response": "film treatment changes with load", "timing": "continuous loop with immediate response", "defining_property": "athlete motion remains visible", "proof": str(alternative)}}
        ],
        "construction_plan": {"spatial_layers": ["control changes displaced field"], "temporal_beats": ["field opens flat", "drag raises grade", "release settles the field"], "material_choreography": [{"material_id": "control", "placement": "The control crosses the field edge.", "entry": "It appears with the initial prescription.", "response": "Its drag changes the field and copy together.", "exit": "It settles into the chosen readiness state."}, {"material_id": "field", "placement": "The field occupies the central reading plane.", "entry": "It opens from a flat resting grade.", "response": "It rises and twists with readiness input.", "exit": "It settles while preserving the selected grade."}], "responsive_strategy": "Recompose the field below the control while preserving direct manipulation.", "fallback_strategy": "Render the same state-driven grade as SVG when WebGL is unavailable."},
        "visual_review": {"blind": True, "reviewer": "independent-vision-reviewer", "reference_evidence": [str(proof)], "winner_proof": str(proof), "alternative_proof": str(alternative), "inspection_evidence": str(inspected), "verdict": "winner", "rationale": "The field-led proof binds state, depth, and control more clearly than the film-led alternative."},
        "direction_origins": [
            {"decision": "colour", "observed_from": "selected starting material", "evidence": str(proof)},
            {"decision": "type", "observed_from": "finished reference hierarchy", "evidence": str(proof)},
            {"decision": "geometry", "observed_from": "spatial source construction", "evidence": str(proof)},
        ],
    }
    source_kinds = {
        "product_truth": "product-truth",
        "finished_reference": "finished-reference",
        "finished_moving_work": "motion-reference",
        "time_based_material": "video-source",
        "spatial_interaction": "spatial-source",
        "interaction_implementation": "interaction-source",
    }
    for family_name, family in receipt["families"].items():
        for attempt in family["attempts"]:
            attempt["result"] = "viable"
            attempt["observed"] = "The candidate was opened and its relevant construction behavior was inspected."
            attempt["source_kind"] = source_kinds[family_name]
            attempt["query_basis"] = "Observed movement, geometry, camera, material, or product behavior from inspected evidence."
            attempt["query_basis_evidence"] = str(source_read)
            if family_name == "time_based_material":
                attempt["candidate_ids"] = ["film"]
            elif family_name == "spatial_interaction":
                attempt["candidate_ids"] = ["field"]
            elif family_name == "interaction_implementation":
                attempt["candidate_ids"] = ["control"]
    return receipt


class ResearchGateTests(unittest.TestCase):
    def test_compact_handoff_keeps_selected_material_and_drops_research_bulk(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            handoff = research_gate.build_handoff(receipt, Path(folder))
            self.assertEqual([item["id"] for item in handoff["selected_material"]], ["control", "field"])
            self.assertNotIn("families", handoff)
            self.assertNotIn("film", json.dumps(handoff))
            self.assertEqual(handoff["selection"]["winner"], "field-led")

    def test_compact_handoff_refuses_an_invalid_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["proof"]["bindings"] = []
            with self.assertRaises(ValueError):
                research_gate.build_handoff(receipt, Path(folder))

    def test_malformed_candidate_shape_fails_without_crashing(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["material_candidates"] = {"field": "not a list"}
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("material candidates must be a list" in error for error in errors))

    def test_example_contains_every_canonical_family_and_unset_classification(self):
        receipt = research_gate.example_receipt()
        self.assertEqual(set(receipt["families"]),
                         research_gate.BASE_FAMILIES | research_gate.INTERACTION_FAMILIES)
        self.assertIsNone(receipt["brief"]["interaction_heavy"])
        self.assertIsNone(receipt["brief"]["react_work"])
        self.assertEqual({item["decision"] for item in receipt["direction_origins"]},
                         {"colour", "type", "geometry"})

    def test_evidence_phase_requires_explicit_brief_classification(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["brief"]["react_work"] = None
            errors = research_gate.validate_evidence(receipt, Path(folder))
            self.assertTrue(any("react_work" in error for error in errors))

    def test_valid_interaction_receipt_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(research_gate.validate(valid_receipt(Path(folder)), Path(folder)), [])

    def test_evidence_phase_passes_before_selection_fields_exist(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            partial = {"brief": receipt["brief"], "families": receipt["families"]}
            self.assertEqual(research_gate.validate_evidence(partial, Path(folder)), [])

    def test_evidence_phase_blocks_missing_family_before_direction(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            del receipt["families"]["spatial_interaction"]
            errors = research_gate.validate_evidence(receipt, Path(folder))
            self.assertTrue(any("spatial_interaction" in error for error in errors))

    def test_empty_or_unrelated_search_does_not_count_as_inspected_source(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            attempt = receipt["families"]["spatial_interaction"]["attempts"][0]
            attempt["result"] = "empty_or_unrelated"
            attempt["observed"] = "The search returned an unrelated torrent repository."
            errors = research_gate.validate_evidence(receipt, Path(folder))
            self.assertTrue(any("no inspected source attempt" in error for error in errors))

    def test_evidence_source_kind_must_match_the_family_it_closes(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            for attempt in receipt["families"]["spatial_interaction"]["attempts"]:
                attempt["source_kind"] = "finished-reference"
            errors = research_gate.validate_evidence(receipt, Path(folder))
            self.assertTrue(any("spatial_interaction" in error and "source kind" in error for error in errors))

    def test_passive_texture_cannot_close_spatial_interaction_family(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["families"]["spatial_interaction"]["attempts"][0]["source_kind"] = "spatial-material"
            errors = research_gate.validate_evidence(receipt, Path(folder))
            self.assertTrue(any("spatial_interaction" in error and "source kind" in error for error in errors))

    def test_missing_spatial_comparison_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            del receipt["families"]["spatial_interaction"]
            self.assertTrue(any("spatial_interaction" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_react_work_requires_interaction_evidence_without_naming_a_library(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            del receipt["families"]["interaction_implementation"]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("interaction_implementation" in error for error in errors))
            self.assertFalse(any("react_bits" in error for error in errors))

    def test_react_work_inspects_react_bits_before_selecting_another_behavior(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["material_candidates"][0]["source"] = "custom-css"
            self.assertEqual(research_gate.validate(receipt, Path(folder)), [])

    def test_react_work_cannot_skip_react_bits_inspection(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["families"]["interaction_implementation"]["attempts"] = [
                attempt for attempt in receipt["families"]["interaction_implementation"]["attempts"]
                if attempt["source"] != "react-bits"
            ]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("React Bits" in error for error in errors))

    def test_interaction_heavy_work_selects_active_material(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            for item in receipt["material_candidates"]:
                item["active"] = False
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("active material" in error for error in errors))

    def test_uninspected_proof_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["proof"]["inspected"] = False
            self.assertTrue(any("proof" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_single_attempt_cannot_close_rejected_family(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["families"]["time_based_material"]["attempts"] = receipt["families"]["time_based_material"]["attempts"][:1]
            self.assertTrue(any("two distinct" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_selected_material_needs_facts_and_inspection(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["material_candidates"][0]["facts"] = {}
            receipt["material_candidates"][0]["inspection_evidence"] = ""
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("measured facts" in error for error in errors))
            self.assertTrue(any("inspection evidence" in error for error in errors))

    def test_ensemble_needs_a_tested_relationship(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["combinations"] = []
            self.assertTrue(any("combination" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_selection_review_compares_rendered_combinations(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["selection_review"] = {}
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("selection review" in error for error in errors))

    def test_selection_review_winner_matches_selected_combination(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["selection_review"]["winner"] = "invented-winner"
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("winner" in error for error in errors))

    def test_selection_review_needs_two_real_proofs_under_shared_conditions(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["selection_review"]["candidates"][1]["proof"] = "missing.png"
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("candidate proof" in error for error in errors))

    def test_selection_review_rejects_identical_candidate_renders(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["selection_review"]["candidates"][1]["proof"] = receipt["selection_review"]["candidates"][0]["proof"]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("byte-identical" in error for error in errors))

    def test_selection_review_proof_matches_tested_combination(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["selection_review"]["candidates"][0]["proof"] = receipt["selection_review"]["candidates"][1]["proof"]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("does not match" in error for error in errors))

    def test_combination_candidates_must_be_shortlisted_material_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["combinations"][0]["candidates"] = ["spatial_material", "react_bits"]
            self.assertTrue(any("material candidate IDs" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_selected_combination_needs_visual_proof(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["combinations"][0]["proof"] = ""
            self.assertTrue(any("combination proof" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_visual_proof_contains_every_selected_material(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["proof"]["included_material"] = ["control"]
            self.assertTrue(any("visual proof does not include" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_active_source_needs_behavior_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["material_candidates"][0]["behavior_contract"] = {}
            self.assertTrue(any("behavior contract" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_combined_proof_demonstrates_every_active_material(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["material_candidates"][1]["behavior_contract"]["proof"] = ""
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("field" in error and "combined proof" in error for error in errors))

    def test_combined_proof_cannot_delegate_behavior_to_separate_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            receipt = valid_receipt(root)
            separate = root / "separate-demo.html"
            separate.write_text("<canvas></canvas>")
            receipt["material_candidates"][0]["behavior_contract"]["proof"] = str(separate)
            errors = research_gate.validate(receipt, root)
            self.assertTrue(any("same combined proof" in error for error in errors))

    def test_react_work_requires_a_runnable_combined_proof(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["proof"]["kind"] = "frames"
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("runnable combined proof" in error for error in errors))

    def test_selected_material_records_implementation_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            del receipt["material_candidates"][1]["implementation_medium"]
            del receipt["material_candidates"][1]["adaptation_boundary"]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("implementation medium" in error for error in errors))
            self.assertTrue(any("adaptation boundary" in error for error in errors))

    def test_selected_material_relationship_names_another_selected_item_or_core_state(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["material_candidates"][0]["relationships"] = ["invented-item"]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("selected relationship" in error for error in errors))

    def test_direction_needs_inspected_origins(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["direction_origins"] = []
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("origin for colour" in error for error in errors))
            self.assertTrue(any("origin for type" in error for error in errors))
            self.assertTrue(any("origin for geometry" in error for error in errors))

    def test_legacy_selected_only_receipt_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["selected_material"] = receipt.pop("material_candidates")
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("material candidates" in error for error in errors))

    def test_every_selected_material_has_a_real_proof_binding(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["proof"]["bindings"] = receipt["proof"]["bindings"][:1]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("proof binding" in error for error in errors))

    def test_direct_binding_resolves_to_the_selected_file(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["proof"]["bindings"][0]["load_reference"] = "spatial.js"
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("does not load its selected file" in error for error in errors))

    def test_lead_video_cannot_be_upscaled_in_a_literal_role(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            film = receipt["material_candidates"][2]
            film["decision"] = "selected"
            film["display"] = {"width": 1600, "height": 900, "treatment": "literal"}
            receipt["combinations"][0]["candidates"].append("film")
            receipt["proof"]["included_material"].append("film")
            receipt["proof"]["bindings"].append({"material_id": "film", "implementation_path": receipt["proof"]["path"], "load_reference": "film.mp4", "kind": "direct"})
            Path(receipt["proof"]["path"]).write_text(Path(receipt["proof"]["path"]).read_text() + '<video src="film.mp4"></video>')
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("upscales lead media" in error for error in errors))

    def test_viable_material_attempt_links_to_a_candidate_decision(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            del receipt["families"]["spatial_interaction"]["attempts"][0]["candidate_ids"]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("candidate decision" in error for error in errors))

    def test_viable_rejected_candidate_is_tested_in_an_alternative_proof(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["combinations"] = receipt["combinations"][:1]
            receipt["selection_review"]["strongest_alternative"] = "missing"
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("rejected candidate" in error for error in errors))

    def test_rejected_lead_candidate_is_tested_in_a_supporting_role(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["combinations"] = [item for item in receipt["combinations"] if item["id"] != "film-supporting"]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("supporting role" in error for error in errors))

    def test_winner_and_alternative_compare_different_material_sets(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["combinations"][1]["candidates"] = ["control", "field"]
            receipt["combinations"][1]["roles"] = {"control": "supporting", "field": "lead"}
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("different material sets" in error for error in errors))

    def test_construction_plan_is_required_before_handoff(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["construction_plan"] = {}
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("construction plan" in error for error in errors))

    def test_construction_plan_choreographs_every_selected_material(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["construction_plan"]["material_choreography"] = receipt["construction_plan"]["material_choreography"][:1]
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("choreograph" in error for error in errors))

    def test_visual_review_is_blind_and_uses_the_compared_proofs(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["visual_review"]["blind"] = False
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("blind visual review" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
