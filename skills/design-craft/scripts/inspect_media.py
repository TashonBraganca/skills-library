#!/usr/bin/env python3
"""Create visual inspection artifacts and machine-readable facts for downloaded material."""
import json
import struct
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
        "-fps_mode", "vfr", "-frames:v", "1", str(destination),
    ], check=True)
    return {"path": str(path), "kind": "video", "timeline": str(destination),
            "inspection_output": str(destination), "facts": facts,
            "sample_times": [round(value, 3) for value in sample_times(duration)]}


def inspect_image(path, output_dir):
    from PIL import Image, ImageOps
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{path.stem}-preview.jpg"
    with Image.open(path) as image:
        facts = {"width": image.width, "height": image.height, "format": image.format,
                 "mode": image.mode, "bytes": path.stat().st_size}
        preview = ImageOps.exif_transpose(image).convert("RGB")
        preview.thumbnail((1600, 1200))
        preview.save(destination, quality=92)
    return {"path": str(path), "kind": "image", "inspection_output": str(destination),
            "facts": facts}


def inspect_model(path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".glb":
        with path.open("rb") as source:
            header = source.read(20)
            if len(header) < 20 or header[:4] != b"glTF":
                raise ValueError(f"invalid GLB: {path}")
            chunk_length, chunk_type = struct.unpack("<II", header[12:20])
            if chunk_type != 0x4E4F534A:
                raise ValueError(f"GLB has no leading JSON chunk: {path}")
            data = json.loads(source.read(chunk_length).decode("utf-8").rstrip(" \t\r\n\0"))
    else:
        data = json.loads(path.read_text())
    facts = {"bytes": path.stat().st_size, "scenes": len(data.get("scenes", [])),
             "nodes": len(data.get("nodes", [])), "meshes": len(data.get("meshes", [])),
             "materials": len(data.get("materials", [])),
             "animations": len(data.get("animations", [])),
             "cameras": len(data.get("cameras", []))}
    destination = output_dir / f"{path.stem}-model.json"
    destination.write_text(json.dumps(facts, indent=2))
    return {"path": str(path), "kind": "model", "inspection_output": str(destination),
            "facts": facts, "render_required": True}


def inspect_asset(path, output_dir):
    suffix = path.suffix.lower()
    if suffix in {".mp4", ".webm", ".mov", ".m4v"}:
        return inspect_video(path, output_dir)
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif"}:
        return inspect_image(path, output_dir)
    if suffix in {".glb", ".gltf"}:
        return inspect_model(path, output_dir)
    return {"path": str(path), "kind": "unhandled", "facts": {"bytes": path.stat().st_size},
            "inspection_output": None}


def update_manifest(result):
    path = Path(result["path"])
    for parent in [path.parent, *path.parents]:
        manifest = parent / "_manifest.json"
        if not manifest.is_file():
            continue
        data = json.loads(manifest.read_text())
        changed = False
        for item in data.get("items", []):
            if Path(item.get("local_path", "")).resolve() == path.resolve():
                item["inspection_status"] = "inspected"
                item["inspection_output"] = result.get("inspection_output")
                item["inspection_facts"] = result.get("facts")
                changed = True
        if changed:
            manifest.write_text(json.dumps(data, indent=2))
            return str(manifest)
    return None


def main(paths):
    output_dir = Path.cwd() / "media-inspection"
    output_dir.mkdir(exist_ok=True)
    results = []
    for raw in paths:
        path = Path(raw).expanduser().resolve()
        result = inspect_asset(path, output_dir)
        result["updated_manifest"] = update_manifest(result)
        results.append(result)
    if not results:
        raise SystemExit("give at least one asset path")
    report = output_dir / "inspection.json"
    report.write_text(json.dumps(results, indent=2))
    print(report)
    for result in results:
        if result.get("inspection_output"):
            print(result["inspection_output"])


if __name__ == "__main__":
    main(sys.argv[1:])
