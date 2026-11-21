"""Read original FLIR v2 COCO labels from 12 ZIP chunks without images.

Treat .zip.00 through .zip.11 as consecutive byte ranges of one ZIP file.
Only train and validation COCO members are read; holdout remains untouched.
No downloads, image extraction, model inference or archive modifications.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

MAX_JSON_BYTES = 256 * 1024 * 1024
MEMBERS = {
    "train": "images_thermal_train/coco.json",
    "validation": "images_thermal_val/coco.json",
}


class MultipartZip(io.RawIOBase):
    """Seekable read-only virtual concatenation of numbered ZIP parts."""

    def __init__(self, parts: list[Path]) -> None:
        super().__init__()
        self.files = [path.open("rb") for path in parts]
        self.offsets = [0]
        for path in parts:
            self.offsets.append(self.offsets[-1] + path.stat().st_size)
        self.position = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            target = offset
        elif whence == 1:
            target = self.position + offset
        elif whence == 2:
            target = self.offsets[-1] + offset
        else:
            raise ValueError("Unsupported seek origin")
        if target < 0:
            raise ValueError("Negative archive seek")
        self.position = target
        return target

    def read(self, size: int = -1) -> bytes:
        if self.position >= self.offsets[-1]:
            return b""
        if size < 0:
            raise ValueError("Unbounded archive reads are forbidden")
        remaining = min(size, self.offsets[-1] - self.position)
        chunks = []
        while remaining:
            index = bisect.bisect_right(self.offsets, self.position) - 1
            count = min(remaining, self.offsets[index + 1] - self.position)
            part = self.files[index]
            part.seek(self.position - self.offsets[index])
            chunk = part.read(count)
            if not chunk:
                raise OSError("Truncated multipart ZIP")
            chunks.append(chunk)
            remaining -= len(chunk)
            self.position += len(chunk)
        return b"".join(chunks)

    def close(self) -> None:
        if not self.closed:
            for part in self.files:
                part.close()
        super().close()


def source_parts(directory: Path) -> list[Path]:
    parts = [
        directory / f"FLIR_ADAS_v2.zip.{index:02d}"
        for index in range(12)
    ]
    if any(not part.is_file() or not part.stat().st_size for part in parts):
        raise ValueError("Expected 12 nonempty FLIR_ADAS_v2.zip.00-.11 parts")
    return parts


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def find_unique_member(names: list[str], suffix: str) -> str:
    candidates = [
        name for name in names
        if name == suffix or name.endswith("/" + suffix)
    ]
    if len(candidates) != 1:
        alternatives = [
            name for name in names if name.lower().endswith("coco.json")
        ]
        raise ValueError(
            f"Expected exactly one {suffix}; found {len(candidates)}. "
            f"COCO members found: {alternatives[:20]}"
        )
    return candidates[0]


def extract_source_labels(parts_dir: Path, output: Path) -> dict:
    """Write only source annotations and hash evidence outside Git."""
    parts = source_parts(parts_dir)
    if output.exists():
        raise ValueError("Evidence output exists; choose a new directory")
    with MultipartZip(parts) as source, zipfile.ZipFile(source) as archive:
        names = archive.namelist()
        members = {
            role: find_unique_member(names, suffix)
            for role, suffix in MEMBERS.items()
        }
        for member in members.values():
            size = archive.getinfo(member).file_size
            if not 0 < size <= MAX_JSON_BYTES:
                raise ValueError(f"Unsafe source annotation size: {member}")
        output.mkdir(parents=True)
        annotations = {}
        for role, member in members.items():
            destination = output / (
                "train_coco.json" if role == "train" else "val_coco.json"
            )
            with archive.open(member) as src, destination.open("xb") as dest:
                shutil.copyfileobj(src, dest, 1024 * 1024)
            annotations[role] = {
                "archive_member": member,
                "filename": destination.name,
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
    evidence = {
        "schema_version": 1,
        "source_identity": "FLIR_ADAS_v2_multipart_candidate",
        "parts": [
            {
                "filename": part.name,
                "bytes": part.stat().st_size,
                "sha256": sha256(part),
            }
            for part in parts
        ],
        "source_annotations": annotations,
        "rights_verified": False,
        "source_acquisition_independence_verified": False,
        "native_sensor_grid_verified": False,
        "heldout_opened": False,
        "images_extracted": False,
        "detector_executed": False,
    }
    (output / "source_manifest.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parts-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = args.output_dir.resolve()
    if output.is_relative_to(root):
        parser.error("Output must be outside repository")
    try:
        evidence = extract_source_labels(args.parts_dir, output)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root / "src") + os.pathsep + env.get(
            "PYTHONPATH", ""
        )
        subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("build_coco_group_manifest.py")),
                "--train-annotations",
                str(output / "train_coco.json"),
                "--validation-annotations",
                str(output / "val_coco.json"),
                "--release-id",
                "FLIR-ADAS-v2-UNVERIFIED",
                "--output",
                str(output / "p01_group_manifest.json"),
            ],
            check=True,
            env=env,
        )
        report = json.loads(
            (output / "p01_group_manifest.json").read_text(encoding="utf-8")
        )
    except (
        OSError, ValueError, RuntimeError, zipfile.BadZipFile,
        subprocess.CalledProcessError,
    ) as exc:
        parser.exit(1, f"P01 multipart: {type(exc).__name__}: {exc}\n")
    print(json.dumps({
        "status": report["status"],
        "train_frames": report["per_split"]["train"]["frames"],
        "validation_frames": report["per_split"]["validation"]["frames"],
        "validation_paired_video_proxy_groups": report["per_split"][
            "validation"
        ]["paired_small_reference_video_proxy_groups"],
        "evidence_directory": str(output),
        "heldout_opened": evidence["heldout_opened"],
        "detector_executed": evidence["detector_executed"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
