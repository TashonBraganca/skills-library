#!/usr/bin/env python3
"""Create full-timeline video storyboards and machine-readable media facts."""
import json
import subprocess
import sys
from pathlib import Path


def sample_times(duration, count=6):
    if duration <= 0:
        return []
    edge = min(0.15, duration / 20)
    if count == 1:
        return [duration / 2]
    span = max(0, duration - edge * 2)
    return [edge + span * index / (count - 1) for index in range(count)]


def probe(path):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name,bit_rate:format=duration,size",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def inspect_video(path, output_dir):
    facts = probe(path)
    duration = float(facts["format"]["duration"])
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{path.stem}-timeline.jpg"
    rate = facts["streams"][0].get("r_frame_rate", "24/1")
    numerator, denominator = (float(part) for part in rate.split("/"))
    fps = numerator / denominator
    frames = [round(stamp * fps) for stamp in sample_times(duration)]
    filters = "+".join(f"eq(n\\,{frame})" for frame in frames)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(path),
        "-vf", f"select='{filters}',scale=480:-1,tile=3x2",
        "-vsync", "vfr", "-frames:v", "1", str(destination),
    ], check=True)
    return {"path": str(path), "timeline": str(destination), "facts": facts,
            "sample_times": [round(value, 3) for value in sample_times(duration)]}


def main(paths):
    output_dir = Path.cwd() / "media-inspection"
    output_dir.mkdir(exist_ok=True)
    results = []
    for raw in paths:
        path = Path(raw).expanduser().resolve()
        if path.suffix.lower() in {".mp4", ".webm", ".mov"}:
            results.append(inspect_video(path, output_dir))
    if not results:
        raise SystemExit("give at least one video path")
    report = output_dir / "inspection.json"
    report.write_text(json.dumps(results, indent=2))
    print(report)
    for result in results:
        print(result["timeline"])


if __name__ == "__main__":
    main(sys.argv[1:])
