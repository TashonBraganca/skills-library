#!/usr/bin/env python3
"""Validate the evidence handoff before interface implementation begins."""

import argparse
import json
from pathlib import Path


BASE_FAMILIES = {"product_truth", "finished_reference"}
INTERACTION_FAMILIES = {
    "finished_moving_work",
    "time_based_material",
    "spatial_material",
    "interaction_implementation",
}


def example_receipt():
    attempt = {"source": "", "query": "", "construction_job": "", "evidence": []}
    return {
        "brief": {"interaction_heavy": False, "react_work": False},
        "families": {name: {"applicable": True, "status": "", "attempts": [dict(attempt)]}
                     for name in sorted(BASE_FAMILIES)},
        "proof": {"path": "", "inspected": False, "inspection_evidence": "",
                  "included_material": []},
        "combinations": [{"candidates": [], "relationship": "", "outcome": "", "proof": ""}],
        "selected_material": [{"id": "", "path": "", "facts": {}, "inspection_evidence": "",
                               "job": "", "relationships": [], "irreplaceable_property": "",
                               "removal_effect": "", "active": False}],
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


def _required_families(receipt):
    brief = receipt.get("brief", {})
    required = set(BASE_FAMILIES)
    if brief.get("interaction_heavy") or brief.get("react_work"):
        required.update(INTERACTION_FAMILIES)
    return required


def validate(receipt, root):
    root = Path(root).resolve()
    errors = []
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
            query = str(attempt.get("query", "")).strip()
            job = str(attempt.get("construction_job", "")).strip()
            evidence = [value for value in attempt.get("evidence", []) if _exists(value, root)]
            if source and query and len(job) >= 16 and evidence:
                valid_attempts.append(source)
        if not valid_attempts:
            errors.append(f"evidence family {name!r} has no inspected source attempt")
        if status == "rejected":
            if len(set(valid_attempts)) < 2:
                errors.append(f"rejected evidence family {name!r} needs two distinct inspected sources")
            if len(str(family.get("reason", "")).strip()) < 24:
                errors.append(f"rejected evidence family {name!r} needs a specific construction reason")

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
        if item.get("active"):
            contract = item.get("behavior_contract", {})
            for field in ("input", "response", "timing", "defining_property"):
                if len(str(contract.get(field, "")).strip()) < 12:
                    errors.append(f"{label} behavior contract has no {field.replace('_', ' ')}")
            if not _exists(contract.get("proof"), root):
                errors.append(f"{label} behavior contract has no runnable or frame proof")

    known_ids = {item_id for item_id in selected_ids if item_id}
    proof_ids = {str(item).strip() for item in proof.get("included_material", []) if str(item).strip()}
    missing_from_proof = sorted(known_ids - proof_ids)
    if missing_from_proof:
        errors.append("visual proof does not include selected material: " + ", ".join(missing_from_proof))

    combinations = receipt.get("combinations", [])
    tested = []
    for item in combinations:
        candidates = {str(value).strip() for value in item.get("candidates", []) if str(value).strip()}
        if len(candidates) < 2 or len(str(item.get("relationship", "")).strip()) < 24 or item.get("outcome") not in {"selected", "rejected"}:
            continue
        if not candidates.issubset(known_ids):
            errors.append("combination candidates must be selected material IDs")
            continue
        if not _exists(item.get("proof"), root):
            errors.append("selected material combination proof is missing")
            continue
        tested.append(item)
    if not tested:
        errors.append("no material combination has a tested relationship, proof, and outcome")

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
    args = parser.parse_args()
    if args.example:
        print(json.dumps(example_receipt(), indent=2))
        return
    if not args.receipt:
        parser.error("receipt is required unless --example is used")
    receipt_path = Path(args.receipt).expanduser().resolve()
    root = Path(args.root).expanduser().resolve() if args.root else receipt_path.parent.parent
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    errors = validate(data, root)
    if errors:
        print("RESEARCH GATE FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("RESEARCH GATE PASSED")


if __name__ == "__main__":
    main()
