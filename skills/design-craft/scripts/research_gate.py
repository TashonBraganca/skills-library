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
    "spatial_material",
    "interaction_implementation",
}
FAMILY_SOURCE_KINDS = {
    "product_truth": {"product-truth", "product-reference"},
    "finished_reference": {"finished-reference"},
    "finished_moving_work": {"motion-reference", "finished-moving-work"},
    "time_based_material": {"video-source", "motion-source", "time-based-material"},
    "spatial_material": {"spatial-source", "spatial-material"},
    "interaction_implementation": {"interaction-source", "interaction-implementation"},
}


def example_receipt():
    attempt = {"source": "", "source_kind": "", "query": "", "construction_job": "", "evidence": [],
               "result": "", "observed": ""}
    return {
        "brief": {"interaction_heavy": None, "react_work": None},
        "families": {name: {"applicable": True, "status": "", "attempts": [dict(attempt)]}
                     for name in sorted(BASE_FAMILIES | INTERACTION_FAMILIES)},
        "proof": {"path": "", "kind": "", "inspected": False, "inspection_evidence": "",
                  "included_material": []},
        "combinations": [{"id": "", "candidates": [], "relationship": "", "outcome": "", "proof": ""}],
        "selection_review": {"winner": "", "strongest_alternative": "", "shared_conditions": "",
                             "winning_reason": "", "candidates": [{"id": "", "proof": "",
                             "first_notice": "", "material_interactions": "", "ordinary_without": "",
                             "spatial_temporal_case": ""}]},
        "selected_material": [{"id": "", "source": "", "path": "", "facts": {}, "inspection_evidence": "",
                               "job": "", "relationships": [], "irreplaceable_property": "",
                               "removal_effect": "", "implementation_medium": "",
                               "adaptation_boundary": "", "active": False}],
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


def _required_families(receipt):
    brief = receipt.get("brief", {})
    required = set(BASE_FAMILIES)
    if brief.get("interaction_heavy") or brief.get("react_work"):
        required.update(INTERACTION_FAMILIES)
    return required


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
            if (source and compatible_kind and query and len(job) >= 16 and evidence
                    and attempt.get("result") == "viable" and len(observed) >= 24):
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

    selected = receipt.get("selected_material", [])
    if not selected:
        errors.append("no selected material is recorded")
    selected_ids = [str(item.get("id", "")).strip() for item in selected]
    if any(not item_id for item_id in selected_ids):
        errors.append("every selected material needs a stable ID")
    if len(set(selected_ids)) != len(selected_ids):
        errors.append("selected material IDs must be unique")
    active_selected = []
    for index, item in enumerate(selected):
        label = f"selected material {index + 1}"
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
        if len(str(item.get("irreplaceable_property", "")).strip()) < 16:
            errors.append(f"{label} does not name what makes this exact material hard to replace")
        if len(str(item.get("removal_effect", "")).strip()) < 16:
            errors.append(f"{label} does not state what breaks when it is removed")
        if len(str(item.get("implementation_medium", "")).strip()) < 3:
            errors.append(f"{label} has no implementation medium")
        if len(str(item.get("adaptation_boundary", "")).strip()) < 24:
            errors.append(f"{label} has no adaptation boundary for the property implementation must preserve")
        if item.get("active"):
            active_selected.append(item)
            contract = item.get("behavior_contract", {})
            for field in ("input", "response", "timing", "defining_property"):
                if len(str(contract.get(field, "")).strip()) < 12:
                    errors.append(f"{label} behavior contract has no {field.replace('_', ' ')}")
            if not _exists(contract.get("proof"), root):
                errors.append(f"{label} behavior contract has no runnable or frame proof")
    if receipt.get("brief", {}).get("interaction_heavy") and not active_selected:
        errors.append("interaction-heavy work has no selected active material")
    if receipt.get("brief", {}).get("react_work"):
        react_bits_selected = [item for item in active_selected
                               if str(item.get("source", "")).strip().lower().replace("_", "-") == "react-bits"]
        if not react_bits_selected:
            errors.append("React work has no selected active React Bits behavior")

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

    known_ids = {item_id for item_id in selected_ids if item_id}
    proof_ids = {str(item).strip() for item in proof.get("included_material", []) if str(item).strip()}
    missing_from_proof = sorted(known_ids - proof_ids)
    if missing_from_proof:
        errors.append("visual proof does not include selected material: " + ", ".join(missing_from_proof))

    combinations = receipt.get("combinations", [])
    tested = []
    combination_ids = set()
    selected_combination_ids = set()
    combination_proofs = {}
    for item in combinations:
        combination_id = str(item.get("id", "")).strip()
        candidates = {str(value).strip() for value in item.get("candidates", []) if str(value).strip()}
        if not combination_id or len(candidates) < 2 or len(str(item.get("relationship", "")).strip()) < 24 or item.get("outcome") not in {"selected", "rejected"}:
            continue
        if combination_id in combination_ids:
            errors.append("material combination IDs must be unique")
            continue
        if not candidates.issubset(known_ids):
            errors.append("combination candidates must be selected material IDs")
            continue
        if not _exists(item.get("proof"), root):
            errors.append("selected material combination proof is missing")
            continue
        tested.append(item)
        combination_ids.add(combination_id)
        combination_proofs[combination_id] = _file_hash(item.get("proof"), root)
        if item.get("outcome") == "selected":
            selected_combination_ids.add(combination_id)
    if not tested:
        errors.append("no material combination has a tested relationship, proof, and outcome")

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

    origins = receipt.get("direction_origins", [])
    covered = {item.get("decision") for item in origins
               if item.get("decision") in {"colour", "type", "geometry"}
               and len(str(item.get("observed_from", "")).strip()) >= 16
               and _exists(item.get("evidence"), root)}
    for decision in sorted({"colour", "type", "geometry"} - covered):
        errors.append(f"visual direction has no inspected origin for {decision}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", nargs="?", help="Path to research-receipt.json")
    parser.add_argument("--root", help="Root used to resolve relative evidence paths")
    parser.add_argument("--example", action="store_true", help="Print a blank receipt")
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
    print("EVIDENCE GATE PASSED" if args.phase == "evidence" else "RESEARCH GATE PASSED")


if __name__ == "__main__":
    main()
