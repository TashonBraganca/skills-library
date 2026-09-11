#!/usr/bin/env python3
"""Validate the evidence handoff before interface implementation begins."""

import argparse
import hashlib
import json
from pathlib import Path


BASE_FAMILIES = {"product_truth", "finished_reference"}
INTERACTION_FAMILIES = {
    "finished_moving_work",
    "time_based_material",
    "spatial_interaction",
    "interaction_implementation",
}
FAMILY_SOURCE_KINDS = {
    "product_truth": {"product-truth", "product-reference"},
    "finished_reference": {"finished-reference"},
    "finished_moving_work": {"motion-reference", "finished-moving-work"},
    "time_based_material": {"video-source", "motion-source", "time-based-material"},
    "spatial_interaction": {"spatial-source"},
    "interaction_implementation": {"interaction-source", "interaction-implementation"},
}
CANDIDATE_SOURCE_KINDS = set().union(*FAMILY_SOURCE_KINDS.values()) | {
    "spatial-material", "image-source", "texture-source", "type-source", "audio-source"
}


def example_receipt():
    attempt = {"source": "", "source_kind": "", "query": "", "query_basis": "",
               "query_basis_evidence": "", "construction_job": "", "evidence": [],
               "candidate_ids": [], "result": "", "observed": ""}
    return {
        "brief": {"interaction_heavy": None, "react_work": None},
        "families": {name: {"applicable": True, "status": "", "attempts": [dict(attempt)]}
                     for name in sorted(BASE_FAMILIES | INTERACTION_FAMILIES)},
        "proof": {"path": "", "kind": "", "inspected": False, "inspection_evidence": "",
                  "included_material": [], "bindings": [], "visual_evidence": ""},
        "combinations": [{"id": "", "candidates": [], "roles": {},
                          "relationship": "", "outcome": "", "proof": ""}],
        "selection_review": {"winner": "", "strongest_alternative": "", "shared_conditions": "",
                             "winning_reason": "", "candidates": [{"id": "", "proof": "",
                             "first_notice": "", "material_interactions": "", "ordinary_without": "",
                             "spatial_temporal_case": ""}]},
        "material_candidates": [{"id": "", "decision": "", "role": "", "source": "",
                                 "source_kind": "", "path": "", "facts": {},
                                 "inspection_evidence": "", "job": "", "relationships": [],
                                 "irreplaceable_property": "", "removal_effect": "",
                                 "implementation_medium": "", "adaptation_boundary": "",
                                 "active": False}],
        "construction_plan": {"spatial_layers": [], "temporal_beats": [],
                              "material_choreography": [{"material_id": "", "placement": "",
                                                         "entry": "", "response": "", "exit": ""}],
                              "responsive_strategy": "", "fallback_strategy": ""},
        "visual_review": {"blind": False, "reviewer": "", "reference_evidence": [],
                          "winner_proof": "", "alternative_proof": "",
                          "inspection_evidence": "", "verdict": "", "rationale": ""},
        "direction_origins": [{"decision": name, "observed_from": "", "evidence": ""}
                              for name in ("colour", "type", "geometry")],
    }


def _exists(value, root):
    if not value:
        return False
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.is_file() and path.stat().st_size > 0


def _file_hash(value, root):
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolved_path(value, root):
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _load_json(value, root):
    if not _exists(value, root):
        return None
    try:
        return json.loads(_resolved_path(value, root).read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _direct_binding_loads_selected_file(binding, candidate, root):
    implementation = _resolved_path(binding.get("implementation_path"), root)
    if not implementation.is_file():
        return False
    reference = str(binding.get("load_reference", "")).strip()
    if not reference or reference not in implementation.read_text(encoding="utf-8", errors="ignore"):
        return False
    loaded = Path(reference).expanduser()
    if not loaded.is_absolute():
        loaded = implementation.parent / loaded
    return loaded.resolve() == _resolved_path(candidate.get("path"), root)


def _required_families(receipt):
    brief = receipt.get("brief", {})
    required = set(BASE_FAMILIES)
    if brief.get("interaction_heavy") or brief.get("react_work"):
        required.update(INTERACTION_FAMILIES)
    return required


def _attempt_is_inspected(attempt, root, family_name=None):
    source = str(attempt.get("source", "")).strip()
    source_kind = str(attempt.get("source_kind", "")).strip()
    query = str(attempt.get("query", "")).strip()
    job = str(attempt.get("construction_job", "")).strip()
    evidence = [value for value in attempt.get("evidence", []) if _exists(value, root)]
    observed = str(attempt.get("observed", "")).strip()
    query_basis = str(attempt.get("query_basis", "")).strip()
    query_basis_evidence = attempt.get("query_basis_evidence")
    compatible_kind = (family_name is None
                       or source_kind in FAMILY_SOURCE_KINDS.get(family_name, set()))
    return (bool(source) and compatible_kind and bool(query) and len(query_basis) >= 24
            and _exists(query_basis_evidence, root) and len(job) >= 16 and bool(evidence)
            and attempt.get("result") == "viable" and len(observed) >= 24)


def validate_evidence(receipt, root):
    root = Path(root).resolve()
    errors = []
    brief = receipt.get("brief", {})
    for field in ("interaction_heavy", "react_work"):
        if not isinstance(brief.get(field), bool):
            errors.append(f"brief classification {field!r} must be explicitly true or false")
    families = receipt.get("families", {})
    for name in sorted(_required_families(receipt)):
        family = families.get(name)
        if not isinstance(family, dict) or not family.get("applicable", False):
            errors.append(f"required evidence family {name!r} is missing or marked inapplicable")
            continue
        status = family.get("status")
        attempts = family.get("attempts", [])
        if status not in {"selected", "rejected"}:
            errors.append(f"evidence family {name!r} has no selected or rejected decision")
        valid_attempts = []
        for attempt in attempts:
            source = str(attempt.get("source", "")).strip()
            source_kind = str(attempt.get("source_kind", "")).strip()
            query = str(attempt.get("query", "")).strip()
            job = str(attempt.get("construction_job", "")).strip()
            evidence = [value for value in attempt.get("evidence", []) if _exists(value, root)]
            observed = str(attempt.get("observed", "")).strip()
            compatible_kind = source_kind in FAMILY_SOURCE_KINDS.get(name, set())
            if source and not compatible_kind:
                errors.append(f"evidence family {name!r} has incompatible source kind {source_kind!r}")
            if _attempt_is_inspected(attempt, root, name):
                valid_attempts.append(source)
        if not valid_attempts:
            errors.append(f"evidence family {name!r} has no inspected source attempt")
        if status == "rejected":
            if len(set(valid_attempts)) < 2:
                errors.append(f"rejected evidence family {name!r} needs two distinct inspected sources")
            if len(str(family.get("reason", "")).strip()) < 24:
                errors.append(f"rejected evidence family {name!r} needs a specific construction reason")
    return errors


def validate(receipt, root):
    root = Path(root).resolve()
    errors = validate_evidence(receipt, root)

    proof = receipt.get("proof", {})
    if not proof.get("inspected"):
        errors.append("visual proof was not inspected")
    if not _exists(proof.get("path"), root):
        errors.append("visual proof file is missing")
    if not _exists(proof.get("inspection_evidence"), root):
        errors.append("visual proof inspection evidence is missing")

    visual_evidence = _load_json(proof.get("visual_evidence"), root)
    if not visual_evidence:
        errors.append("visual proof has no measured pixel evidence")
    else:
        winner_render = visual_evidence.get("winner", {})
        for name in ("winner", "without_lead", "response"):
            record = visual_evidence.get(name, {})
            if (not _exists(record.get("path"), root)
                    or _file_hash(record.get("path"), root) != record.get("sha256")):
                errors.append(f"visual proof {name.replace('_', ' ')} render is missing or changed after inspection")
        if winner_render.get("width", 0) < 320 or winner_render.get("height", 0) < 240:
            errors.append("visual proof render is too small to judge")
        if winner_render.get("luminance_stddev", 0) < 4:
            errors.append("visual proof render is blank or nearly uniform")
        if visual_evidence.get("lead_changed_fraction", 0) < 0.01:
            errors.append("selected lead is visually inert in the combined proof")
        if receipt.get("brief", {}).get("interaction_heavy") and visual_evidence.get("response_changed_fraction", 0) < 0.005:
            errors.append("selected active material has no visible response in the combined proof")

    candidates = receipt.get("material_candidates", [])
    if not isinstance(candidates, list):
        errors.append("material candidates must be a list")
        candidates = []
    if not candidates:
        errors.append("no material candidates are recorded")
    candidate_ids = [str(item.get("id", "")).strip() for item in candidates]
    if any(not item_id for item_id in candidate_ids):
        errors.append("every material candidate needs a stable ID")
    if len(set(candidate_ids)) != len(candidate_ids):
        errors.append("material candidate IDs must be unique")
    selected = [item for item in candidates if item.get("decision") == "selected"]
    selected_ids = [str(item.get("id", "")).strip() for item in selected]
    if not selected:
        errors.append("no material candidate is selected")
    selected_leads = {str(item.get("id", "")).strip() for item in selected if item.get("role") == "lead"}
    if visual_evidence and visual_evidence.get("material_id") not in selected_leads:
        errors.append("visual proof pixel evidence does not measure the selected lead")
    active_selected = []
    for index, item in enumerate(candidates):
        label = f"material candidate {index + 1}"
        if item.get("decision") not in {"selected", "rejected"}:
            errors.append(f"{label} has no selected or rejected decision")
        if item.get("role") not in {"lead", "supporting"}:
            errors.append(f"{label} has no lead or supporting role")
        if item.get("source_kind") not in CANDIDATE_SOURCE_KINDS:
            errors.append(f"{label} has no recognized source kind")
        if not _exists(item.get("path"), root):
            errors.append(f"{label} file is missing")
        if not item.get("facts"):
            errors.append(f"{label} has no measured facts")
        if not _exists(item.get("inspection_evidence"), root):
            errors.append(f"{label} has no inspection evidence")
        if len(str(item.get("job", "")).strip()) < 16:
            errors.append(f"{label} has no concrete construction job")
        if not item.get("relationships"):
            errors.append(f"{label} has no relationship to another selected item or core state")
        elif item.get("decision") == "selected":
            related = {str(value).strip() for value in item.get("relationships", [])}
            allowed = (set(selected_ids) - {str(item.get("id", "")).strip()}) | {"core-state"}
            if not related.intersection(allowed):
                errors.append(f"{label} has no valid selected relationship")
        if len(str(item.get("irreplaceable_property", "")).strip()) < 16:
            errors.append(f"{label} does not name what makes this exact material hard to replace")
        if len(str(item.get("removal_effect", "")).strip()) < 16:
            errors.append(f"{label} does not state what breaks when it is removed")
        if len(str(item.get("implementation_medium", "")).strip()) < 3:
            errors.append(f"{label} has no implementation medium")
        if len(str(item.get("adaptation_boundary", "")).strip()) < 24:
            errors.append(f"{label} has no adaptation boundary for the property implementation must preserve")
        if item.get("active"):
            contract = item.get("behavior_contract", {})
            for field in ("input", "response", "timing", "defining_property"):
                if len(str(contract.get(field, "")).strip()) < 12:
                    errors.append(f"{label} behavior contract has no {field.replace('_', ' ')}")
            if not _exists(contract.get("proof"), root):
                errors.append(f"{label} behavior contract has no runnable or frame proof")
            if item.get("decision") == "selected":
                active_selected.append(item)
        facts = item.get("facts", {})
        display = item.get("display", {})
        if (item.get("decision") == "selected" and item.get("role") == "lead"
                and all(isinstance(facts.get(key), (int, float)) for key in ("width", "height"))):
            if not all(isinstance(display.get(key), (int, float)) and display.get(key) > 0
                       for key in ("width", "height")):
                errors.append(f"{label} has no intended display size")
            elif (display.get("treatment") == "literal"
                  and (display["width"] > facts["width"] or display["height"] > facts["height"])):
                errors.append(f"{label} upscales lead media in a literal displayed role")
    if receipt.get("brief", {}).get("interaction_heavy") and not active_selected:
        errors.append("interaction-heavy work has no selected active material")
    if receipt.get("brief", {}).get("react_work"):
        interaction = receipt.get("families", {}).get("interaction_implementation", {})
        react_bits_attempts = [
            attempt for attempt in interaction.get("attempts", [])
            if str(attempt.get("source", "")).strip().lower().replace("_", "-") == "react-bits"
            and _attempt_is_inspected(attempt, root)
        ]
        if not react_bits_attempts:
            errors.append("React work has no inspected React Bits candidate")

    active_ids = {str(item.get("id", "")).strip() for item in active_selected
                  if str(item.get("id", "")).strip()}
    proof_kind = str(proof.get("kind", "")).strip()
    if active_ids and proof_kind not in {"runnable", "frames"}:
        errors.append("active material needs a runnable or frame-based combined proof")
    if receipt.get("brief", {}).get("react_work") and proof_kind != "runnable":
        errors.append("React work needs a runnable combined proof")
    proof_path = proof.get("path")
    for item in active_selected:
        material_id = str(item.get("id", "")).strip()
        contract_proof = item.get("behavior_contract", {}).get("proof")
        if (not _exists(contract_proof, root) or not proof_path
                or _resolved_path(contract_proof, root) != _resolved_path(proof_path, root)):
            errors.append(f"active material {material_id!r} must demonstrate its behavior in the same combined proof")

    known_ids = {item_id for item_id in candidate_ids if item_id}
    proof_ids = {str(item).strip() for item in proof.get("included_material", []) if str(item).strip()}
    missing_from_proof = sorted(set(selected_ids) - proof_ids)
    if missing_from_proof:
        errors.append("visual proof does not include selected material: " + ", ".join(missing_from_proof))
    extra_in_proof = sorted(proof_ids - set(selected_ids))
    if extra_in_proof:
        errors.append("visual proof includes material that was not selected: " + ", ".join(extra_in_proof))

    by_id = {str(item.get("id", "")).strip(): item for item in candidates if str(item.get("id", "")).strip()}
    bindings = proof.get("bindings", [])
    binding_ids = [str(binding.get("material_id", "")).strip() for binding in bindings]
    for material_id in selected_ids:
        if binding_ids.count(material_id) != 1:
            errors.append(f"selected material {material_id!r} needs exactly one proof binding")
    for binding in bindings:
        material_id = str(binding.get("material_id", "")).strip()
        if material_id not in set(selected_ids):
            errors.append(f"proof binding names unselected material {material_id!r}")
            continue
        if binding.get("kind") != "direct":
            errors.append(f"proof binding for {material_id!r} must directly load the selected source")
        elif not _direct_binding_loads_selected_file(binding, by_id[material_id], root):
            errors.append(f"proof binding for {material_id!r} does not load its selected file")

    for family_name in ("time_based_material", "spatial_interaction", "interaction_implementation"):
        family = receipt.get("families", {}).get(family_name, {})
        for attempt in family.get("attempts", []):
            if not _attempt_is_inspected(attempt, root, family_name):
                continue
            linked = {str(value).strip() for value in attempt.get("candidate_ids", []) if str(value).strip()}
            if not linked or not linked.issubset(known_ids):
                errors.append(f"viable {family_name!r} attempt has no material candidate decision")

    combinations = receipt.get("combinations", [])
    tested = []
    combination_ids = set()
    selected_combination_ids = set()
    combination_proofs = {}
    combination_roles = {}
    for item in combinations:
        combination_id = str(item.get("id", "")).strip()
        candidate_set = {str(value).strip() for value in item.get("candidates", []) if str(value).strip()}
        if not combination_id or len(candidate_set) < 2 or len(str(item.get("relationship", "")).strip()) < 24 or item.get("outcome") not in {"selected", "rejected"}:
            continue
        if combination_id in combination_ids:
            errors.append("material combination IDs must be unique")
            continue
        if not candidate_set.issubset(known_ids):
            errors.append("combination candidates must be material candidate IDs")
            continue
        roles = item.get("roles", {})
        if (not isinstance(roles, dict) or set(roles) != candidate_set
                or any(role not in {"lead", "supporting"} for role in roles.values())):
            errors.append(f"material combination {combination_id!r} must assign a lead or supporting role to every candidate")
            continue
        if not _exists(item.get("proof"), root):
            errors.append("selected material combination proof is missing")
            continue
        tested.append(item)
        combination_ids.add(combination_id)
        combination_proofs[combination_id] = _file_hash(item.get("proof"), root)
        combination_roles[combination_id] = roles
        if item.get("outcome") == "selected":
            selected_combination_ids.add(combination_id)
    if not tested:
        errors.append("no material combination has a tested relationship, proof, and outcome")
    rejected_combination_material = set().union(*(
        {str(value).strip() for value in item.get("candidates", []) if str(value).strip()}
        for item in tested if item.get("outcome") == "rejected"
    )) if any(item.get("outcome") == "rejected" for item in tested) else set()
    viable_linked_ids = set()
    for family_name in ("time_based_material", "spatial_interaction", "interaction_implementation"):
        for attempt in receipt.get("families", {}).get(family_name, {}).get("attempts", []):
            if _attempt_is_inspected(attempt, root, family_name):
                viable_linked_ids.update(str(value).strip() for value in attempt.get("candidate_ids", []))
    for item in candidates:
        candidate_id = str(item.get("id", "")).strip()
        if (item.get("decision") == "rejected" and candidate_id in viable_linked_ids
                and candidate_id not in rejected_combination_material):
            errors.append(f"viable rejected candidate {candidate_id!r} needs a tested alternative proof")
        if (item.get("decision") == "rejected" and item.get("role") == "lead"
                and candidate_id in viable_linked_ids):
            supporting_trials = [
                combination_roles.get(str(combination.get("id", "")).strip(), {}).get(candidate_id)
                for combination in tested if combination.get("outcome") == "rejected"
            ]
            if "supporting" not in supporting_trials:
                errors.append(f"viable rejected lead candidate {candidate_id!r} needs a tested supporting role")

    review = receipt.get("selection_review", {})
    winner = str(review.get("winner", "")).strip()
    alternative = str(review.get("strongest_alternative", "")).strip()
    review_candidates = review.get("candidates", [])
    if (len(str(review.get("shared_conditions", "")).strip()) < 24
            or len(str(review.get("winning_reason", "")).strip()) < 24
            or not winner or not alternative or winner == alternative):
        errors.append("selection review must compare a winner and strongest alternative under shared conditions")
    if winner and winner not in selected_combination_ids:
        errors.append("selection review winner must match a selected material combination")
    if alternative and alternative not in combination_ids:
        errors.append("selection review strongest alternative must match a tested material combination")
    if (visual_evidence and winner in combination_proofs
            and visual_evidence.get("winner", {}).get("sha256") != combination_proofs[winner]):
        errors.append("visual proof pixel evidence does not measure the selected combination render")
    combination_sets = {
        str(item.get("id", "")).strip(): {
            str(value).strip() for value in item.get("candidates", []) if str(value).strip()
        }
        for item in tested
    }
    if winner in combination_sets and combination_sets[winner] != set(selected_ids):
        errors.append("selection review winner must contain exactly the selected material candidates")
    if winner in combination_roles:
        declared_roles = {str(item.get("id", "")).strip(): item.get("role") for item in selected}
        if combination_roles[winner] != declared_roles:
            errors.append("selection review winner roles must match the selected material roles")
    if (winner in combination_sets and alternative in combination_sets
            and combination_sets[winner] == combination_sets[alternative]):
        errors.append("selection review must compare different material sets")
    reviewed_ids = set()
    proof_hashes = []
    for candidate in review_candidates:
        candidate_id = str(candidate.get("id", "")).strip()
        if candidate_id not in {winner, alternative}:
            continue
        reviewed_ids.add(candidate_id)
        if not _exists(candidate.get("proof"), root):
            errors.append(f"selection review candidate proof is missing for {candidate_id!r}")
        else:
            candidate_hash = _file_hash(candidate.get("proof"), root)
            proof_hashes.append(candidate_hash)
            if candidate_id in combination_proofs and candidate_hash != combination_proofs[candidate_id]:
                errors.append(f"selection review candidate proof does not match tested combination {candidate_id!r}")
        for field in ("first_notice", "material_interactions", "ordinary_without", "spatial_temporal_case"):
            if len(str(candidate.get(field, "")).strip()) < 24:
                errors.append(f"selection review candidate {candidate_id!r} has no {field.replace('_', ' ')}")
    if {winner, alternative} - reviewed_ids:
        errors.append("selection review is missing the winner or strongest alternative")
    if len(proof_hashes) >= 2 and len(set(proof_hashes)) != len(proof_hashes):
        errors.append("selection review candidate proofs are byte-identical")

    plan = receipt.get("construction_plan", {})
    if (not isinstance(plan.get("spatial_layers"), list) or not plan.get("spatial_layers")
            or not isinstance(plan.get("temporal_beats"), list) or len(plan.get("temporal_beats")) < 2
            or len(str(plan.get("responsive_strategy", "")).strip()) < 24
            or len(str(plan.get("fallback_strategy", "")).strip()) < 24):
        errors.append("construction plan must define spatial layers, temporal beats, responsive behavior, and fallback behavior")
    choreography = plan.get("material_choreography", [])
    choreography_ids = [str(item.get("material_id", "")).strip() for item in choreography]
    if set(choreography_ids) != set(selected_ids) or len(choreography_ids) != len(selected_ids):
        errors.append("construction plan must choreograph every selected material exactly once")
    for item in choreography:
        for field in ("placement", "entry", "response", "exit"):
            if len(str(item.get(field, "")).strip()) < 24:
                errors.append(f"construction plan choreography has no {field} for {item.get('material_id')!r}")

    visual = receipt.get("visual_review", {})
    reference_evidence = visual.get("reference_evidence", [])
    visual_valid = (
        visual.get("blind") is True
        and len(str(visual.get("reviewer", "")).strip()) >= 8
        and bool(reference_evidence)
        and all(_exists(value, root) for value in reference_evidence)
        and _exists(visual.get("winner_proof"), root)
        and _exists(visual.get("alternative_proof"), root)
        and _exists(visual.get("inspection_evidence"), root)
        and visual.get("verdict") in {"winner", "alternative", "neither"}
        and len(str(visual.get("rationale", "")).strip()) >= 24
    )
    if not visual_valid:
        errors.append("blind visual review must inspect the compared proofs against fixed reference evidence")
    else:
        if winner in combination_proofs and _file_hash(visual.get("winner_proof"), root) != combination_proofs[winner]:
            errors.append("blind visual review winner proof does not match the selected combination")
        if alternative in combination_proofs and _file_hash(visual.get("alternative_proof"), root) != combination_proofs[alternative]:
            errors.append("blind visual review alternative proof does not match the strongest alternative")

    origins = receipt.get("direction_origins", [])
    covered = {item.get("decision") for item in origins
               if item.get("decision") in {"colour", "type", "geometry"}
               and len(str(item.get("observed_from", "")).strip()) >= 16
               and _exists(item.get("evidence"), root)}
    for decision in sorted({"colour", "type", "geometry"} - covered):
        errors.append(f"visual direction has no inspected origin for {decision}")
    return errors


def build_handoff(receipt, root):
    """Return the compact, validated construction brief used by the build stage."""
    errors = validate(receipt, root)
    if errors:
        raise ValueError("invalid research receipt: " + "; ".join(errors))
    selected = [item for item in receipt["material_candidates"] if item.get("decision") == "selected"]
    review = receipt["selection_review"]
    return {
        "brief": receipt["brief"],
        "selected_material": selected,
        "proof": receipt["proof"],
        "selection": {
            "winner": review["winner"],
            "winning_reason": review["winning_reason"],
        },
        "construction_plan": receipt["construction_plan"],
        "direction_origins": receipt["direction_origins"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", nargs="?", help="Path to research-receipt.json")
    parser.add_argument("--root", help="Root used to resolve relative evidence paths")
    parser.add_argument("--example", action="store_true", help="Print a blank receipt")
    parser.add_argument("--handoff", help="Write a compact validated construction handoff")
    parser.add_argument("--phase", choices=("evidence", "complete"), default="complete",
                        help="Validate evidence before direction or the complete research handoff")
    args = parser.parse_args()
    if args.example:
        print(json.dumps(example_receipt(), indent=2))
        return
    if not args.receipt:
        parser.error("receipt is required unless --example is used")
    receipt_path = Path(args.receipt).expanduser().resolve()
    root = Path(args.root).expanduser().resolve() if args.root else receipt_path.parent.parent
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    errors = validate_evidence(data, root) if args.phase == "evidence" else validate(data, root)
    if errors:
        print("EVIDENCE GATE FAILED" if args.phase == "evidence" else "RESEARCH GATE FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    if args.phase == "complete" and args.handoff:
        handoff_path = Path(args.handoff).expanduser().resolve()
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        handoff_path.write_text(json.dumps(build_handoff(data, root), indent=2) + "\n", encoding="utf-8")
    print("EVIDENCE GATE PASSED" if args.phase == "evidence" else "RESEARCH GATE PASSED")


if __name__ == "__main__":
    main()
