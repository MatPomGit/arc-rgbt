"""Render local, reviewer-separated FLIR thermal QA image packages.

Read-only source archive access; no test annotations, models or network.
The package is NOT evidence of human review or dataset admission.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import cv2
import numpy as np

from build_flir_qa_inventory import (
    JoinedParts,
    _coco_key,
    _index_key,
    _json_entry,
    _unique,
    build_inventory,
)
from reconcile_blinded_qa import FIELDS, _order, _plan

MAX_SAMPLE = 250
MAX_IMAGE_BYTES = 16 * 1024 * 1024


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_jpeg(z: zipfile.ZipFile, prefix: str, filename: str) -> bytes:
    if not isinstance(filename, str):
        raise ValueError("Missing source image file_name")
    p = PurePosixPath(filename)
    if (p.is_absolute() or ".." in p.parts or not p.parts
            or p.suffix.lower() not in (".jpg", ".jpeg")):
        raise ValueError("Unsafe or non-JPEG image filename")
    name = filename if filename.startswith(prefix + "/") else prefix + "/" + filename
    if name not in z.namelist():
        matches = [x for x in z.namelist() if x.startswith(prefix + "/")
                   and PurePosixPath(x).name == p.name]
        if len(matches) != 1:
            raise ValueError(f"Thermal JPEG not uniquely found: {filename}")
        name = matches[0]
    info = z.getinfo(name)
    if not 0 < info.file_size <= MAX_IMAGE_BYTES:
        raise ValueError("Unexpected source JPEG size")
    return z.read(name)  # Selected member CRC verified; nothing extracted.


def _display_image(data: bytes, width: int, height: int) -> np.ndarray:
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[:2] != (height, width) or img.dtype != np.uint8:
        raise ValueError("Invalid source JPEG encoding, bit depth or dimensions")
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.ndim == 3 and img.shape[2] == 3:
        return img
    raise ValueError("Unexpected JPEG channels")


def _overlay(image: np.ndarray, anns: list[dict], target: str,
             target_only: bool) -> np.ndarray:
    out = image.copy()
    mapping = {"car"} if target == "car" else {"person", "rider"}
    for a in anns:
        labels = a.get("labels")
        box = a.get("boundingBox")
        if (not isinstance(labels, list) or
                any(not isinstance(v, str) for v in labels) or not isinstance(box, dict)):
            raise ValueError("Malformed original annotation")
        highlight = bool(mapping.intersection(labels))
        if target_only and not highlight:
            continue
        try:
            x, y, w, h = (float(box[k]) for k in ("x", "y", "w", "h"))
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError("Missing annotation bbox") from exc
        if not np.isfinite((x, y, w, h)).all() or w <= 0 or h <= 0:
            raise ValueError("Invalid annotation coordinates")
        color = (0, 230, 0) if highlight else (160, 160, 160)
        x1, y1, x2, y2 = round(x), round(y), round(x + w), round(y + h)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        if labels:
            cv2.putText(out, ",".join(labels)[:40], (max(x1, 0), max(14, y1 - 3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)
    return out


def _png(image: np.ndarray) -> bytes:
    ok, data = cv2.imencode(".png", image)
    if not ok:
        raise OSError("Could not render PNG")
    return data.tobytes()


def _check_review_sheet(path: Path, expected_order: list[str]) -> None:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or tuple(reader.fieldnames) != FIELDS:
            raise ValueError("Reviewer sheet columns do not match template")
        records = list(reader)
    actual = []
    for record in records:
        if None in record or any(value is None for value in record.values()):
            raise ValueError("Malformed reviewer CSV record")
        if any(record[field] for field in FIELDS[1:]):
            raise ValueError("Review already filled; refusing to replace it")
        actual.append(record["frame_id"])
    if actual != expected_order:
        raise ValueError("Reviewer sheet frame IDs/order differ from sample plan")


def _html_page(rows: list[tuple[str, str]], split: str, target: str) -> str:
    sections = []
    for seq, (frame_id, stem) in enumerate(rows, 1):
        fid = html.escape(frame_id, quote=True)
        sections.append(
            f'<section><h2>{seq:02d}. {fid}</h2>'
            f'<img alt="Oryginalny obraz termiczny" src="images/{stem}_raw.png">'
            '<details><summary>Pokaż bounding boxy klasy docelowej</summary>'
            f'<img alt="Oryginalne ramki obiektów docelowych" src="images/{stem}_target.png">'
            '</details><details><summary>Pokaż wszystkie oryginalne ramki</summary>'
            f'<img alt="Wszystkie ramki" src="images/{stem}_all.png"></details>'
            '</section>'
        )
    return (
        '<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>FLIR P01: niezależne QA</title><style>'
        'body{font:16px/1.55 system-ui,sans-serif;max-width:900px;margin:2rem auto;'
        'padding:0 1rem;background:#f6f6f6;color:#222}'
        'section{margin:1.5rem 0;padding:1rem;background:white;border:1px solid #ddd}'
        'img{display:block;width:100%;max-width:640px;height:auto;margin:1rem auto}'
        'summary{cursor:pointer}h2{font-size:1rem;overflow-wrap:anywhere}'
        '</style></head><body><h1>Niezależna ocena adnotacji – FLIR ADAS v2</h1>'
        f'<p>Zbiór: {html.escape(split)}; klasa: {html.escape(target)}. '
        'Oceń najpierw surowy obraz termiczny JPEG (AGC), a następnie '
        'otwórz nakładki oryginalnych adnotacji. Zielone ramki: docelowe '
        '(person obejmuje w tym podglądzie oryginalne person/rider); '
        'szare: pozostałe. Wypełnij review.csv samodzielnie, bez '
        'wyników detektora i bez konsultowania ocen drugiego recenzenta. '
        'Podgląd nie dowodzi kompletności etykiet ani pochodzenia oryginalnej siatki LWIR.</p>'
        + "\n".join(sections) + '</body></html>\n'
    )


def render(archive_dir: Path, plan_path: Path, reviewer_a: Path, reviewer_b: Path,
           output: Path, *, split: str, target: str) -> dict:
    if split not in ("train", "val") or target not in ("person", "car"):
        raise ValueError("Only train/val and person/car supported")
    plan, plan_hash, frames = _plan(plan_path)
    if len(frames) > MAX_SAMPLE:
        raise ValueError("Sample exceeds 250 frames")
    if any(not frame.startswith(split + ":") or frame.count(":") != 2
           for frame in frames):
        raise ValueError("Unexpected frame ID or source split")
    if output.exists():
        raise FileExistsError("Output exists; refusing overwrite")
    repo_root = Path(__file__).resolve().parents[3]
    if output.resolve().is_relative_to(repo_root):
        raise ValueError("Output must be outside Git repository")
    if not output.parent.is_dir():
        raise ValueError("Output parent directory does not exist")
    order_a = _order(frames, plan_hash, "A")
    order_b = _order(frames, plan_hash, "B")
    _check_review_sheet(reviewer_a, order_a)
    _check_review_sheet(reviewer_b, order_b)
    parts = [archive_dir / f"FLIR_ADAS_v2.zip.{i:02d}" for i in range(12)]
    temp = Path(tempfile.mkdtemp(prefix=".qa-local-", dir=output.parent))
    try:
        with zipfile.ZipFile(JoinedParts(parts)) as z:
            if len(z.namelist()) != len(set(z.namelist())):
                raise ValueError("Duplicate ZIP entry")
            prefix = f"images_thermal_{split}"
            index, index_sha = _json_entry(z, f"{prefix}/index.json")
            coco, coco_sha = _json_entry(z, f"{prefix}/coco.json")
            inventory, _ = build_inventory(
                index, coco, split=split, target=target,
                index_sha=index_sha, coco_sha=coco_sha
            )
            canonical = json.dumps(
                {**inventory, "frames": sorted(inventory["frames"],
                                               key=lambda x: x["frame_id"])},
                sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
            if (plan.get("source_release") != inventory["source_release"]
                    or plan.get("inventory_sha256") != _sha(canonical)):
                raise ValueError("Plan does not match source annotation version")
            original = _unique(index["frames"], _index_key)
            exported = _unique(coco["images"], _coco_key)
            photos = {}
            image_hashes = []
            for fid in frames:
                partition, video_id, number = fid.split(":")
                if partition != split or not number.isdecimal():
                    raise ValueError("Invalid selected frame ID")
                key = (video_id, int(number))
                if key not in original or key not in exported:
                    raise ValueError("Plan refers to an absent frame")
                row = exported[key]
                raw_bytes = _source_jpeg(z, prefix, row["file_name"])
                image = _display_image(raw_bytes, row["width"], row["height"])
                anns = original[key]["annotations"]
                photos[fid] = {
                    "raw": _png(image),
                    "target": _png(_overlay(image, anns, target, target_only=True)),
                    "all": _png(_overlay(image, anns, target, target_only=False)),
                }
                image_hashes.append({"frame_id": fid, "source_jpeg_sha256": _sha(raw_bytes)})
        for reviewer, order, source_csv in (
            ("A", order_a, reviewer_a), ("B", order_b, reviewer_b)
        ):
            dest = temp / ("reviewer_" + reviewer)
            images = dest / "images"
            images.mkdir(parents=True)
            shutil.copyfile(source_csv, dest / "review.csv")
            page_rows = []
            for seq, fid in enumerate(order, 1):
                stem = f"{seq:03d}"
                page_rows.append((fid, stem))
                for mode in ("raw", "target", "all"):
                    (images / f"{stem}_{mode}.png").write_bytes(photos[fid][mode])
            (dest / "index.html").write_text(
                _html_page(page_rows, split, target), encoding="utf-8"
            )
            (dest / "README.txt").write_text(
                "Open index.html offline. Fill review.csv independently for all "
                "listed frames. Open source GT overlays after viewing each raw "
                "frame. Do not share ratings with the other assessor.\n",
                encoding="utf-8"
            )
        manifest = {
            "schema_version": 1, "status": "REVIEW_MEDIA_PREPARED_ONLY",
            "plan_sha256": plan_hash, "source_index_sha256": index_sha,
            "source_coco_sha256": coco_sha,
            "split": split, "target": target,
            "selected_frames": len(frames),
            "reviewer_folders": ["reviewer_A", "reviewer_B"],
            "source_image_sha256": image_hashes,
            "test_labels_inspected": False,
            "human_reviews_completed": False,
            "source_rights_verified": False,
            "native_grid_verified": False,
            "empirical_admission": False,
        }
        (temp / "package_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        os.rename(temp, output)
        return {
            "status": manifest["status"], "selected_frames": len(frames),
            "reviewer_folders": manifest["reviewer_folders"],
            "human_reviews_completed": False, "empirical_admission": False
        }
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive_dir", type=Path)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--split", choices=("train", "val"), default="val")
    parser.add_argument("--target", choices=("car", "person"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    info = render(args.archive_dir, args.plan, args.reviewer_a, args.reviewer_b,
                  args.output, split=args.split, target=args.target)
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
