#!/usr/bin/env python3
"""Create visual inspection artifacts and machine-readable facts for downloaded material."""
import base64
import http.server
import json
import socketserver
import struct
import subprocess
import sys
import threading
from pathlib import Path


SUPPORTED_MEDIA = {".mp4", ".webm", ".mov", ".m4v", ".png", ".jpg", ".jpeg",
                   ".webp", ".avif", ".gif", ".glb", ".gltf"}


def expand_inputs(raw_paths):
    paths = []
    for raw in raw_paths:
        path = Path(raw).expanduser().resolve()
        if path.is_dir():
            paths.extend(candidate for candidate in sorted(path.rglob("*"))
                         if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_MEDIA)
        else:
            paths.append(path)
    return paths


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
    report_path = output_dir / f"{path.stem}-model.json"
    report_path.write_text(json.dumps(facts, indent=2))
    preview_path = render_model(path, output_dir)
    result = {"path": str(path), "kind": "model", "model_report": str(report_path),
              "inspection_output": str(preview_path) if preview_path else str(report_path),
              "facts": facts}
    if preview_path is None:
        result["render_required"] = True
        result["render_error"] = "Chrome could not render a visual preview of this model."
    return result


def render_model(path, output_dir):
    """Render a GLB in Chrome so model selection is based on pixels, not metadata."""
    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if not chrome.is_file() or path.suffix.lower() != ".glb":
        return None
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    html_path = output_dir / f"{path.stem}-model-preview.html"
    preview_path = output_dir / f"{path.stem}-model-preview.png"
    html_path.write_text(f"""<!doctype html><html><head><meta charset=\"utf-8\"><style>
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#e9e6df}}
canvas{{display:block}}</style><script type=\"importmap\">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"}}}}</script></head><body><script type=\"module\">
import * as THREE from 'three'; import {{GLTFLoader}} from 'three/addons/loaders/GLTFLoader.js';
const scene=new THREE.Scene(); scene.background=new THREE.Color(0xe9e6df);
const camera=new THREE.PerspectiveCamera(35,1200/900,.01,1000);
const renderer=new THREE.WebGLRenderer({{antialias:true,alpha:false}}); renderer.setSize(1200,900); renderer.setPixelRatio(1); renderer.outputColorSpace=THREE.SRGBColorSpace; document.body.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x5f6770,2.7)); const key=new THREE.DirectionalLight(0xffffff,3); key.position.set(3,5,4); scene.add(key);
const bytes=Uint8Array.from(atob('{payload}'),c=>c.charCodeAt(0));
new GLTFLoader().parse(bytes.buffer,'',g=>{{
 const model=g.scene; scene.add(model); const box=new THREE.Box3().setFromObject(model); const size=box.getSize(new THREE.Vector3()); const center=box.getCenter(new THREE.Vector3()); model.position.sub(center);
 const largest=Math.max(size.x,size.y,size.z)||1; camera.position.set(largest*1.35,largest*.55,largest*2.6); camera.lookAt(0,0,0); camera.near=largest/100; camera.far=largest*100; camera.updateProjectionMatrix();
 if(g.animations.length){{const mixer=new THREE.AnimationMixer(model); mixer.clipAction(g.animations[0]).play(); mixer.update(Math.min(.6,g.animations[0].duration*.25));}}
 renderer.render(scene,camera); document.body.dataset.ready='true';
}},undefined,e=>{{document.body.dataset.error=String(e)}});
</script></body></html>""", encoding="utf-8")
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            return

    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(output_dir), **kwargs)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_address[1]}/{html_path.name}"
        result = subprocess.run([
            str(chrome), "--headless=new", "--hide-scrollbars", "--use-gl=angle",
            "--use-angle=swiftshader-webgl", "--enable-unsafe-swiftshader",
            "--window-size=1200,900", "--virtual-time-budget=12000",
            f"--screenshot={preview_path}", url,
        ], capture_output=True, text=True, timeout=30)
        server.shutdown()
    rendered_pixels = False
    if preview_path.is_file():
        from PIL import Image
        with Image.open(preview_path).convert("RGB") as image:
            rendered_pixels = any(high - low > 20 for low, high in image.getextrema())
    if result.returncode or not preview_path.is_file() or not rendered_pixels:
        preview_path.unlink(missing_ok=True)
        return None
    return preview_path


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
                item["inspection_status"] = (
                    "needs_visual_inspection" if result.get("render_required")
                    or result.get("kind") == "unhandled" else "inspected"
                )
                item["inspection_output"] = result.get("inspection_output")
                item["inspection_facts"] = result.get("facts")
                if result.get("render_error"):
                    item["inspection_error"] = result["render_error"]
                changed = True
        if changed:
            manifest.write_text(json.dumps(data, indent=2))
            return str(manifest)
    return None


def main(paths):
    output_dir = Path.cwd() / "media-inspection"
    output_dir.mkdir(exist_ok=True)
    results = []
    for path in expand_inputs(paths):
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
