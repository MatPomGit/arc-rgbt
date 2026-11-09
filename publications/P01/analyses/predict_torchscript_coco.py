"""Validation-only offline COCO predictions from a trusted local TorchScript model.

This adapter performs *validation* inference only. It never opens test/holdout,
downloads checkpoints, authenticates source rights or infers native LWIR optics.
The TorchScript contract is explicitly post-NMS [N,6] or [1,N,6] tensor:
(x1,y1,x2,y2,score,model_class_index) on letterboxed input pixels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path, PurePosixPath

import cv2
import numpy as np
from run_coco_reference import digest, source_group

MAX_COCO_BYTES = 256 * 1024 * 1024
MAX_IMAGE_BYTES = 16 * 1024 * 1024
MAX_PIXELS = 4_000_000
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png"}


def safe_image(root: Path, name: object) -> Path:
    """Reject absolute, traversal, symlink-escape and unsupported source paths."""
    if (not isinstance(name, str) or not name or "\\" in name or "\x00" in name
            or ":" in name or len(name) > 1024):
        raise ValueError("Invalid image file_name")
    relative = PurePosixPath(name)
    if (relative.is_absolute() or any(part in ("", ".", "..") for part in name.split("/"))
            or relative.suffix.lower() not in SUPPORTED_SUFFIXES):
        raise ValueError("Unsafe or unsupported image file_name")
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("Missing image or path outside declared image root")
    if not 0 < path.stat().st_size <= MAX_IMAGE_BYTES:
        raise ValueError("Image size outside safe bounds")
    return path


def load_validation(annotations: Path, manifest: Path, class_name: str) -> tuple[list[dict], int]:
    """Bind exact validation COCO metadata to the pre-test split manifest."""
    if not 0 < annotations.stat().st_size <= MAX_COCO_BYTES:
        raise ValueError("Annotation file outside size bounds")
    source = json.loads(annotations.read_text(encoding="utf-8"))
    plan = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(source, dict) or not isinstance(plan, dict):
        raise ValueError("Invalid source or manifest")
    if (plan.get("status") != "PROVISIONAL_VIDEO_PROXY_SPLIT"
            or plan.get("split_mode") != "preserve"
            or plan.get("selected_class") != class_name
            or plan.get("heldout_opened") is not False
            or plan.get("source_annotation_sha256", {}).get("validation") != digest(annotations)):
        raise ValueError("Manifest not eligible or not bound to exact validation annotations")
    if plan.get("validation_threshold_exposure_meets_software_floor") is not True:
        raise ValueError("Validation exposure does not satisfy candidate software minimums")
    categories, images = source.get("categories"), source.get("images")
    if not isinstance(categories, list) or not isinstance(images, list) or not images:
        raise ValueError("Missing COCO categories or images")
    eligible = [cat["id"] for cat in categories
                if isinstance(cat, dict) and cat.get("name") == class_name
                and type(cat.get("id")) is int]
    if len(eligible) != 1:
        raise ValueError("Source class must map to one unique integer category")
    expected = {}
    for row in plan.get("frame_manifest", []):
        if not isinstance(row, dict):
            raise ValueError("Malformed pre-test frame manifest")
        if row.get("split") == "validation":
            key = row.get("frame_id")
            if not isinstance(key, str) or not re.fullmatch(r"validation:[0-9]+", key):
                raise ValueError("Invalid validation frame manifest key")
            if key in expected or not isinstance(row.get("source_video_id"), str):
                raise ValueError("Duplicate or missing manifest group")
            expected[key] = row["source_video_id"]
    if len(expected) != len(images):
        raise ValueError("Source validation images do not match the original split manifest")
    records = []
    seen = set()
    for image in images:
        if not isinstance(image, dict):
            raise ValueError("Invalid COCO image")
        image_id = image.get("id")
        width, height = image.get("width"), image.get("height")
        if (type(image_id) is not int or image_id < 0 or image_id in seen
                or type(width) is not int or type(height) is not int
                or width <= 0 or height <= 0 or width * height > MAX_PIXELS):
            raise ValueError("Invalid COCO ID or image dimensions")
        seen.add(image_id)
        key = f"validation:{image_id}"
        if expected.get(key) != source_group(image):
            raise ValueError("Validation group mismatch against pre-test manifest")
        records.append({
            "id": image_id, "file_name": image.get("file_name"),
            "width": width, "height": height,
        })
    return sorted(records, key=lambda x: x["id"]), eligible[0]


def letterbox(gray: np.ndarray, height: int, width: int, channels: int) -> tuple[np.ndarray, tuple]:
    """Preserve aspect ratio and return an invertible source-grid mapping."""
    if (gray.ndim != 2 or gray.dtype != np.uint8 or gray.size > MAX_PIXELS
            or channels not in (1, 3) or height <= 0 or width <= 0
            or height * width > MAX_PIXELS):
        raise ValueError("Only bounded uint8 single-channel thermal source is supported")
    h, w = gray.shape
    scale = min(height / h, width / w)
    rw = max(1, min(width, round(w * scale)))
    rh = max(1, min(height, round(h * scale)))
    left, top = (width - rw) // 2, (height - rh) // 2
    canvas = np.zeros((height, width), dtype=np.uint8)
    canvas[top:top + rh, left:left + rw] = cv2.resize(
        gray, (rw, rh), interpolation=cv2.INTER_LINEAR
    )
    array = canvas.astype(np.float32) / 255.0
    if channels == 3:
        array = np.repeat(array[None, :, :], 3, axis=0)
    else:
        array = array[None, :, :]
    return array[None, :, :, :], (left, top, rw / w, rh / h)


def decode_predictions(rows: np.ndarray, image_id: int, source_size: tuple[int, int],
                       mapping: tuple, model_class_index: int,
                       category_id: int) -> list[dict]:
    """Map post-NMS model boxes back to source-export coordinates, fail closed."""
    if rows.ndim == 3 and rows.shape[0] == 1:
        rows = rows[0]
    if rows.ndim != 2 or rows.shape[1] != 6 or len(rows) > 1000:
        raise ValueError("TorchScript output must be [N,6] or [1,N,6] with <=1000 rows")
    if not np.isfinite(rows).all():
        raise ValueError("Nonfinite detector output")
    left, top, scale_x, scale_y = mapping
    width, height = source_size
    detections = []
    for x1, y1, x2, y2, score, class_index in rows:
        if (not 0 <= score <= 1 or class_index < 0
                or class_index != int(class_index)):
            raise ValueError("Invalid score or model class index")
        if int(class_index) != model_class_index:
            continue
        x1, x2 = (x1 - left) / scale_x, (x2 - left) / scale_x
        y1, y2 = (y1 - top) / scale_y, (y2 - top) / scale_y
        if (x2 <= x1 or y2 <= y1
                or x1 < -1e-4 or y1 < -1e-4
                or x2 > width + 1e-4 or y2 > height + 1e-4):
            raise ValueError("Detector box outside source image; no silent clipping")
        x1, x2 = max(0.0, float(x1)), min(float(width), float(x2))
        y1, y2 = max(0.0, float(y1)), min(float(height), float(y2))
        detections.append({
            "image_id": image_id, "category_id": category_id,
            "bbox": [x1, y1, x2 - x1, y2 - y1],
            "score": float(score),
        })
    return sorted(detections, key=lambda item: (
        -item["score"], *item["bbox"]
    ))


def predict(annotations: Path, manifest: Path, image_root: Path,
            checkpoint: Path, expected_checkpoint_sha256: str, class_name: str,
            model_class_index: int, model_height: int, model_width: int,
            channels: int, device: str, output_dir: Path) -> dict:
    """Generate source-reference-compatible predictions without holdout access."""
    root = Path(__file__).resolve().parents[3]
    output = output_dir.resolve()
    if output.is_relative_to(root) or output.exists():
        raise ValueError("Output directory must be new and outside the repository")
    paths = [annotations.resolve(), manifest.resolve(), checkpoint.resolve()]
    if len(set(paths)) != 3 or output in paths:
        raise ValueError("Distinct annotation, manifest and checkpoint paths are required")
    if (not re.fullmatch(r"[0-9a-f]{64}", expected_checkpoint_sha256)
            or digest(checkpoint) != expected_checkpoint_sha256):
        raise ValueError("Checkpoint SHA-256 mismatch")
    if (checkpoint.suffix.lower() != ".pt" or model_class_index < 0
            or model_height <= 0 or model_width <= 0
            or channels not in (1, 3) or device not in ("cpu", "cuda")):
        raise ValueError("Invalid TorchScript configuration")
    images, source_category = load_validation(annotations, manifest, class_name)
    image_root = image_root.resolve()
    if not image_root.is_dir():
        raise ValueError("Image root does not exist")
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("Local torch required; no download is performed") from exc
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA requested but unavailable")
    # TorchScript executes model-defined operations: use only a trusted local file.
    model = torch.jit.load(str(checkpoint), map_location=device)
    model.eval()
    all_predictions = []
    images_digest = hashlib.sha256()
    with torch.inference_mode():
        for record in images:
            image_path = safe_image(image_root, record["file_name"])
            raw = image_path.read_bytes()
            if not raw.startswith((b"\xff\xd8", b"\x89PNG\r\n\x1a\n")):
                raise ValueError("Image is not a JPEG or PNG")
            gray = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            if (gray is None or gray.ndim != 2 or gray.dtype != np.uint8
                    or gray.shape != (record["height"], record["width"])):
                raise ValueError("Image requires predeclared 8-bit grayscale preprocessing")
            tensor, transform = letterbox(gray, model_height, model_width, channels)
            predictions = model(torch.from_numpy(tensor).to(device))
            if not isinstance(predictions, torch.Tensor):
                raise ValueError("Expected one TorchScript tensor, not a tuple/dict")
            rows = predictions.detach().cpu().numpy()
            all_predictions.extend(decode_predictions(
                rows, record["id"], (record["width"], record["height"]),
                transform, model_class_index, source_category,
            ))
            images_digest.update(
                json.dumps([record["id"], digest(image_path)], separators=(",", ":")).encode()
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    # Stage both artifacts privately; rename only after both are complete.
    with tempfile.TemporaryDirectory(prefix="p01-validation-", dir=output.parent) as temp:
        stage = Path(temp)
        prediction_path = stage / "predictions.json"
        prediction_path.write_text(
            json.dumps(all_predictions, indent=2, allow_nan=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        report = {
            "schema_version": 1,
            "status": "VALIDATION_PREDICTIONS_ONLY_UNADMITTED",
            "scientific_claim": "none",
            "split_role": "validation",
            "heldout_opened": False,
            "author_protocol_frozen_verified": False,
            "source_rights_verified": False,
            "original_native_lwir_geometry_verified": False,
            "independent_acquisitions_verified": False,
            "checkpoint_training_independence_verified": False,
            "source_annotation_sha256": digest(annotations),
            "source_manifest_sha256": digest(manifest),
            "checkpoint_sha256": expected_checkpoint_sha256,
            "input_image_digest_chain_sha256": images_digest.hexdigest(),
            "predictor_sha256": digest(Path(__file__)),
            "predictions_sha256": digest(prediction_path),
            "frames": len(images),
            "source_gt_category_id": source_category,
            "target_class": class_name,
            "model_class_index": model_class_index,
            "predicted_target_boxes": len(all_predictions),
            "model": "trusted_local_torchscript_post_nms",
            "model_input": {
                "width": model_width, "height": model_height,
                "channels": channels, "pixel_normalization": "uint8 / 255",
                "resize": "letterbox_aspect_preserved_pad_0",
                "box_format": "xyxy_on_letterboxed_model_input",
                "device": device, "torch_version": str(torch.__version__),
            },
            "limitations": [
                "No held-out evaluation, test threshold selection or empirical G01 admission",
                "Source labels, image export grid and video IDs remain unverified proxies",
                "Checkpoint train/validation isolation requires external provenance",
                "No automatic downloads, native optical physics or physical range inference",
            ],
        }
        (stage / "provenance.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        stage.rename(output)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-annotations", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--checkpoint-sha256", required=True)
    parser.add_argument("--class-name", default="car")
    parser.add_argument("--model-class-index", type=int, required=True)
    parser.add_argument("--input-height", type=int, required=True)
    parser.add_argument("--input-width", type=int, required=True)
    parser.add_argument("--channels", choices=(1, 3), type=int, default=3)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = predict(
            args.validation_annotations, args.manifest, args.image_root,
            args.checkpoint, args.checkpoint_sha256, args.class_name,
            args.model_class_index, args.input_height, args.input_width,
            args.channels, args.device, args.output_dir,
        )
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        parser.exit(1, f"P01 offline validation inference: {type(exc).__name__}: {exc}\n")
    print(json.dumps({
        "status": report["status"], "frames": report["frames"],
        "boxes": report["predicted_target_boxes"],
        "predictions_sha256": report["predictions_sha256"],
        "heldout_opened": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
