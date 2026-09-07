import json
import tempfile
import unittest
from pathlib import Path

import research_gate


def valid_receipt(root):
    proof = root / "proof.png"
    proof.write_bytes(b"proof")
    inspected = root / "proof-inspection.txt"
    inspected.write_text("viewed at full composition size")
    asset = root / "active.js"
    asset.write_text("export default function active() {}")
    source_read = root / "active-source-notes.md"
    source_read.write_text("input, response, timing and dependencies inspected")
    return {
        "brief": {"interaction_heavy": True, "react_work": True},
        "families": {
            "product_truth": {"applicable": True, "status": "selected", "attempts": [{"source": "peer", "query": "training recovery", "construction_job": "learn the real daily planning state", "evidence": [str(source_read)]}]},
            "finished_reference": {"applicable": True, "status": "selected", "attempts": [{"source": "adjacent-work", "query": "controlled effort interface", "construction_job": "resolve hierarchy and material placement", "evidence": [str(proof)]}]},
            "finished_moving_work": {"applicable": True, "status": "selected", "attempts": [{"source": "motion", "query": "controlled exertion sequence", "construction_job": "learn a continuous opening and payoff", "evidence": [str(proof)]}]},
            "time_based_material": {"applicable": True, "status": "rejected", "reason": "Both inspected candidates obscured live training state at the required crop.", "attempts": [{"source": "video", "query": "interval pacing footage", "construction_job": "carry exertion through the opening scene", "evidence": [str(proof)]}, {"source": "generated-study", "query": "interval pacing loop", "construction_job": "carry exertion through the opening scene", "evidence": [str(inspected)]}]},
            "spatial_material": {"applicable": True, "status": "selected", "attempts": [{"source": "spatial", "query": "training force field", "construction_job": "make readiness alter the page geometry", "evidence": [str(proof)]}]},
            "react_bits": {"applicable": True, "status": "selected", "attempts": [{"source": "react-bits", "query": "direct manipulation", "construction_job": "control readiness with elastic response", "evidence": [str(asset), str(source_read)]}]},
            "second_interaction_source": {"applicable": True, "status": "selected", "attempts": [{"source": "codrops", "query": "state driven canvas", "construction_job": "connect readiness to the visual field", "evidence": [str(source_read)]}]},
        },
        "proof": {"path": str(proof), "inspected": True, "inspection_evidence": str(inspected)},
        "combinations": [{"candidates": ["spatial_material", "react_bits"], "relationship": "The control changes the field geometry and the training prescription.", "outcome": "selected"}],
        "selected_material": [{"path": str(asset), "facts": {"bytes": asset.stat().st_size, "type": "source"}, "inspection_evidence": str(source_read), "job": "Control the main training state.", "relationships": ["spatial_material"], "irreplaceable_property": "Its overshoot exposes the effort boundary.", "removal_effect": "The field and plan lose their shared response.", "active": True, "behavior_contract": {"input": "horizontal pointer drag", "response": "field and plan change together", "timing": "spring settles after release", "defining_property": "elastic overshoot remains visible", "proof": str(proof)}}],
        "direction_origins": [
            {"decision": "colour", "observed_from": "selected starting material", "evidence": str(proof)},
            {"decision": "type", "observed_from": "finished reference hierarchy", "evidence": str(proof)},
            {"decision": "geometry", "observed_from": "spatial source construction", "evidence": str(proof)},
        ],
    }


class ResearchGateTests(unittest.TestCase):
    def test_example_contains_base_families_and_direction_origins(self):
        receipt = research_gate.example_receipt()
        self.assertEqual(set(receipt["families"]), research_gate.BASE_FAMILIES)
        self.assertEqual({item["decision"] for item in receipt["direction_origins"]},
                         {"colour", "type", "geometry"})

    def test_valid_interaction_receipt_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(research_gate.validate(valid_receipt(Path(folder)), Path(folder)), [])

    def test_missing_spatial_comparison_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            del receipt["families"]["spatial_material"]
            self.assertTrue(any("spatial_material" in error for error in research_gate.validate(receipt, Path(folder))))

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
            receipt["selected_material"][0]["facts"] = {}
            receipt["selected_material"][0]["inspection_evidence"] = ""
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("measured facts" in error for error in errors))
            self.assertTrue(any("inspection evidence" in error for error in errors))

    def test_ensemble_needs_a_tested_relationship(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["combinations"] = []
            self.assertTrue(any("combination" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_active_source_needs_behavior_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["selected_material"][0]["behavior_contract"] = {}
            self.assertTrue(any("behavior contract" in error for error in research_gate.validate(receipt, Path(folder))))

    def test_direction_needs_inspected_origins(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = valid_receipt(Path(folder))
            receipt["direction_origins"] = []
            errors = research_gate.validate(receipt, Path(folder))
            self.assertTrue(any("origin for colour" in error for error in errors))
            self.assertTrue(any("origin for type" in error for error in errors))
            self.assertTrue(any("origin for geometry" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
