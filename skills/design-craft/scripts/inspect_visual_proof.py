#!/usr/bin/env python3
"""Measure whether selected material visibly changes a rendered construction proof."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _open_rgb(path):
    image = Image.open(path).convert("RGB")
    if image.width < 320 or image.height < 240:
        raise ValueError(f"render is too small to judge: {image.width}x{image.height}")
    return image


def _changed_fraction(left, right):
    if left.size != right.size:
        raise ValueError("compared renders must have the same dimensions")
    difference = ImageChops.difference(left, right).convert("L")
    changed = sum(difference.histogram()[8:])
    return changed / (left.width * left.height)


def inspect(winner_path, without_lead_path, response_path, material_id):
    winner = _open_rgb(winner_path)
    without_lead = _open_rgb(without_lead_path)
    response = _open_rgb(response_path)
    luminance = ImageStat.Stat(winner.convert("L"))
    return {
        "material_id": material_id,
        "winner": {"path": str(winner_path), "sha256": _sha256(winner_path),
                   "width": winner.width, "height": winner.height,
                   "luminance_stddev": round(luminance.stddev[0], 4)},
        "without_lead": {"path": str(without_lead_path), "sha256": _sha256(without_lead_path)},
        "response": {"path": str(response_path), "sha256": _sha256(response_path)},
        "lead_changed_fraction": round(_changed_fraction(winner, without_lead), 6),
        "response_changed_fraction": round(_changed_fraction(winner, response), 6),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--winner", type=Path, required=True)
    parser.add_argument("--without-lead", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--material-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.winner, args.without_lead, args.response, args.material_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
