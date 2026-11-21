"""Train a scratch car-only LWIR baseline on FLIR train, score validation only.

No pretrained weights, remote downloads, reannotation or test/holdout access.
This optional TorchVision workflow runs on an authorized local machine and
reuses the existing validation TorchScript adapter and threshold selector.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

import cv2
import numpy as np

from predict_torchscript_coco import predict
from read_flir_multipart_coco import MultipartZip, source_parts
from run_coco_reference import digest, validation_candidate

SOURCE_SPLITS = {"train": "images_thermal_train", "validation": "images_thermal_val"}
MAX_IMAGE_BYTES = 16 * 1024 * 1024
MAX_IMAGE_PIXELS = 4_000_000


def archive_relative_name(name: object) -> str:
    """Treat COCO names as untrusted relative image paths."""
    if (not isinstance(name, str) or not name or len(name) > 1024
            or "\\" in name or ":" in name or "\x00" in name):
        raise ValueError("Invalid source file_name")
    path = PurePosixPath(name)
    if (path.is_absolute() or any(x in ("", ".", "..") for x in name.split("/"))
            or path.suffix.lower() not in (".jpg", ".jpeg", ".png")):
        raise ValueError("Unsafe or unsupported source image path")
    return str(path)


class FlirImages:
    """Seekable multipart archive with explicit train/validation-only image index."""

    def __init__(self, parts_dir: Path) -> None:
        self.source = MultipartZip(source_parts(parts_dir))
        self.archive = zipfile.ZipFile(self.source)
        self.members = {role: {} for role in SOURCE_SPLITS}
        for member in self.archive.namelist():
            for role, folder in SOURCE_SPLITS.items():
                prefix = f"{folder}/"
                # Original archive may have one leading FLIR_ADAS_v2/ directory.
                fragments = member.split("/" + prefix, 1)
                if len(fragments) == 2:
                    rel = fragments[1]
                elif member.startswith(prefix):
                    rel = member[len(prefix):]
                else:
                    continue
                if rel.lower().endswith((".jpg", ".jpeg", ".png")):
                    if rel in self.members[role]:
                        raise ValueError("Ambiguous duplicate image name in archive")
                    self.members[role][rel] = member

    def member(self, role: str, filename: str) -> str:
        relative = archive_relative_name(filename)
        choices = [relative]
        if not relative.startswith("data/"):
            choices.append("data/" + relative)
        matched = {self.members[role][c] for c in choices if c in self.members[role]}
        if len(matched) != 1:
            raise ValueError(f"No unique {role} thermal image for COCO {relative!r}")
        return matched.pop()

    def read(self, role: str, filename: str) -> bytes:
        member = self.member(role, filename)
        info = self.archive.getinfo(member)
        if not 0 < info.file_size <= MAX_IMAGE_BYTES:
            raise ValueError("Image outside bounded JPEG/PNG size")
        return self.archive.read(member)

    def close(self) -> None:
        self.archive.close()
        self.source.close()

    def __enter__(self) -> FlirImages:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def decode_thermal(data: bytes, height: int, width: int) -> np.ndarray:
    if not data.startswith((b"\xff\xd8", b"\x89PNG\r\n\x1a\n")):
        raise ValueError("Not a source JPEG/PNG image")
    raw = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if (raw is None or raw.ndim != 2 or raw.dtype != np.uint8
            or raw.shape != (height, width) or raw.size > MAX_IMAGE_PIXELS):
        raise ValueError("Only original-grid 8-bit grayscale source is supported")
    return raw


def coco_records(path: Path, *, role: str, target: str = "car") -> list[dict]:
    if role not in SOURCE_SPLITS:
        raise ValueError("Only original train/validation roles are supported")
    if not 0 < path.stat().st_size <= 256 * 1024 * 1024:
        raise ValueError("COCO annotations outside size bounds")
    coco = json.loads(path.read_text(encoding="utf-8"))
    categories = [c["id"] for c in coco["categories"] if c.get("name") == target]
    if len(categories) != 1:
        raise ValueError("Expected one car category")
    category = categories[0]
    grouped: dict[int, list[list[float]]] = defaultdict(list)
    image_index = {}
    for image in coco["images"]:
        key = image["id"]
        if type(key) is not int or key in image_index:
            raise ValueError("Invalid or duplicate image ID")
        width, height = image["width"], image["height"]
        if (type(width) is not int or type(height) is not int
                or width <= 0 or height <= 0 or width * height > MAX_IMAGE_PIXELS):
            raise ValueError("Invalid source grid")
        image_index[key] = {
            "id": key, "file_name": archive_relative_name(image["file_name"]),
            "width": width, "height": height, "boxes": grouped[key],
        }
    for ann in coco["annotations"]:
        if ann["image_id"] not in image_index:
            raise ValueError("Orphan source annotation")
        if ann["category_id"] != category:
            continue
        if ann.get("ignore", 0) or ann.get("iscrowd", 0):
            raise ValueError("Source car crowd/ignore policy is not frozen")
        box = ann["bbox"]
        if (not isinstance(box, list) or len(box) != 4
                or any(type(v) not in (int, float) or not np.isfinite(v) for v in box)):
            raise ValueError("Invalid source car bbox")
        x, y, w, h = box
        record = image_index[ann["image_id"]]
        if (x < 0 or y < 0 or w <= 0 or h <= 0
                or x + w > record["width"] or y + h > record["height"]):
            raise ValueError("Car bbox outside source export grid")
        grouped[ann["image_id"]].append([x, y, x + w, y + h])
    records = [image_index[key] for key in sorted(image_index)]
    if any((row["height"], row["width"]) != (512, 640) for row in records):
        raise ValueError("Scratch baseline requires original 512x640 export grid")
    return records


class CarTrainDataset:
    def __init__(self, records: list[dict], archive: FlirImages) -> None:
        self.records = records
        self.archive = archive

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int):
        import torch

        image = self.records[index]
        gray = decode_thermal(
            self.archive.read("train", image["file_name"]),
            image["height"], image["width"],
        )
        rgb = np.repeat(gray[None], 3, axis=0).copy()
        boxes = torch.tensor(image["boxes"], dtype=torch.float32).reshape(-1, 4)
        return (
            torch.from_numpy(rgb).float() / 255.0,
            {
                "boxes": boxes,
                "labels": torch.ones(len(boxes), dtype=torch.int64),
                "image_id": torch.tensor(image["id"], dtype=torch.int64),
            },
        )


def verify_preflight(evidence_dir: Path) -> dict:
    source = json.loads((evidence_dir / "source_manifest.json").read_text())
    manifest = json.loads((evidence_dir / "p01_group_manifest.json").read_text())
    if (manifest.get("status") != "PROVISIONAL_VIDEO_PROXY_SPLIT"
            or manifest.get("split_mode") != "preserve"
            or manifest.get("heldout_opened") is not False
            or manifest.get("selected_class") != "car"):
        raise ValueError("Source manifest is not an eligible original train/val proposal")
    for role, name in (("train", "train_coco.json"), ("validation", "val_coco.json")):
        expected = manifest["source_annotation_sha256"][role]
        if (digest(evidence_dir / name) != expected
                or source["source_annotations"][role]["sha256"] != expected):
            raise ValueError("Source annotation SHA-256 mismatch")
    return manifest


def make_detector():
    from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_fpn

    detector = fasterrcnn_mobilenet_v3_large_fpn(
        weights=None, weights_backbone=None, num_classes=2,
        min_size=512, max_size=640,
    )
    detector.roi_heads.score_thresh = 0.001
    detector.roi_heads.detections_per_img = 300
    return detector


def make_post_nms_wrapper(model):
    import torch

    class PostNMS(torch.nn.Module):
        def __init__(self, detector):
            super().__init__()
            self.detector = detector

        def forward(self, batch: torch.Tensor) -> torch.Tensor:
            if torch.jit.is_scripting():
                _, prediction = self.detector([batch[0]])
            else:
                prediction = self.detector([batch[0]])
            selected = prediction[0]
            mask = selected["labels"] == 1
            boxes = selected["boxes"][mask]
            scores = selected["scores"][mask]
            # Model class index 0; source COCO car class ID is separate.
            return torch.cat((boxes, scores[:, None], torch.zeros_like(scores[:, None])), 1)

    return PostNMS(model)


def train_and_validate(parts_dir: Path, evidence_dir: Path, output_dir: Path, *,
                       epochs: int, batch_size: int, device: str, seed: int,
                       rights_acknowledged: bool) -> dict:
    if not rights_acknowledged:
        raise ValueError("Explicit original dataset terms acknowledgment required")
    if epochs <= 0 or epochs > 100 or batch_size <= 0 or batch_size > 8:
        raise ValueError("Invalid training budget")
    root = Path(__file__).resolve().parents[3]
    output_dir = output_dir.resolve()
    if output_dir.exists() or output_dir.is_relative_to(root):
        raise ValueError("Training output must be new and outside the repository")
    manifest = verify_preflight(evidence_dir)
    import torch
    import torchvision
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA requested but unavailable; no CPU fallback")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if device == "cuda":
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    records = coco_records(evidence_dir / "train_coco.json", role="train")
    # Validation is only used for a fixed, post-training operating point.
    val_records = coco_records(evidence_dir / "val_coco.json", role="validation")
    if (len(records) != manifest["per_split"]["train"]["frames"]
            or len(val_records) != manifest["per_split"]["validation"]["frames"]):
        raise ValueError("Preflight census differs from source annotations")
    output_dir.mkdir(parents=True)
    with FlirImages(parts_dir) as archive:
        # Confirm all files are identified by the source-referenced split before
        # running any optimization; never iterate over or open test/holdout.
        for role, rows in (("train", records), ("validation", val_records)):
            for item in rows:
                archive.member(role, item["file_name"])
        dataset = CarTrainDataset(records, archive)

        def collate(batch):
            return tuple(zip(*batch))

        loader = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True, num_workers=0,
            collate_fn=collate, generator=torch.Generator().manual_seed(seed),
        )
        model = make_detector().to(device)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9)
        losses = []
        for epoch in range(epochs):
            model.train()
            total_loss = 0.0
            for images, targets in loader:
                images = [item.to(device) for item in images]
                targets = [{key: value.to(device) for key, value in row.items()}
                           for row in targets]
                optimizer.zero_grad(set_to_none=True)
                result = model(images, targets)
                loss = sum(result.values())
                if not torch.isfinite(loss):
                    raise RuntimeError("Non-finite training loss")
                loss.backward()
                optimizer.step()
                total_loss += float(loss.detach().cpu())
            losses.append({"epoch": epoch + 1, "train_mean_loss": total_loss / len(loader)})
            print(json.dumps(losses[-1]), flush=True)
        model.eval()
        checkpoint = output_dir / "scratch_car_post_nms.pt"
        scripted = torch.jit.script(make_post_nms_wrapper(model).eval())
        torch.jit.save(scripted, str(checkpoint))
        # Existing predictor reads real on-disk validation images. We only
        # materialize annotated validation JPEGs, preserving COCO file_name.
        val_root = output_dir / "validation_images"
        image_chain = hashlib.sha256()
        for item in val_records:
            data = archive.read("validation", item["file_name"])
            decode_thermal(data, item["height"], item["width"])
            rel = archive_relative_name(item["file_name"])
            path = val_root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(data)
            image_chain.update(f"{item['id']}:".encode())
            image_chain.update(hashlib.sha256(data).digest())
    checkpoint_sha = digest(checkpoint)
    val_predictions = predict(
        evidence_dir / "val_coco.json", evidence_dir / "p01_group_manifest.json",
        val_root, checkpoint, checkpoint_sha, "car", 0,
        512, 640, 3, device, output_dir / "validation_predictions",
    )
    candidate, _ = validation_candidate(
        evidence_dir / "val_coco.json",
        output_dir / "validation_predictions" / "predictions.json", "car",
    )
    (output_dir / "validation_candidate.json").write_text(
        json.dumps(candidate, sort_keys=True, indent=2, allow_nan=False) + "\n"
    )
    result = {
        "schema_version": 1,
        "status": "VALIDATION_CANDIDATE_ONLY_UNFROZEN",
        "model": "scratch_torchvision_frcnn_mobilenetv3_single_car",
        "source_rights_acknowledged_by_operator": rights_acknowledged,
        "legal_admission_independently_verified": False,
        "source_acquisitions_independent_verified": False,
        "heldout_opened": False,
        "test_tuned": False,
        "checkpoint_training_split": "source_train_only",
        "checkpoint_sha256": checkpoint_sha,
        "model_class_index": 0,
        "validation_threshold_candidate": candidate["validation_threshold"],
        "validation_predictions_sha256": val_predictions["predictions_sha256"],
        "input_annotation_sha256": manifest["source_annotation_sha256"],
        "input_preflight_manifest_sha256": digest(evidence_dir / "p01_group_manifest.json"),
        "validation_source_images_chain_sha256": image_chain.hexdigest(),
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        "device": device,
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "training_loss_by_epoch": losses,
    }
    (output_dir / "training_provenance.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parts-dir", type=Path, required=True)
    parser.add_argument("--preflight-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--rights-acknowledged", action="store_true")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261121)
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    args = parser.parse_args(argv)
    try:
        report = train_and_validate(
            args.parts_dir, args.preflight_dir, args.output_dir,
            epochs=args.epochs, batch_size=args.batch_size,
            device=args.device, seed=args.seed,
            rights_acknowledged=args.rights_acknowledged,
        )
    except (OSError, ValueError, RuntimeError, KeyError, ImportError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"P01 scratch LWIR: {type(exc).__name__}: {exc}\n")
    print(json.dumps({
        "status": report["status"],
        "checkpoint_sha256": report["checkpoint_sha256"],
        "validation_threshold": report["validation_threshold_candidate"],
        "heldout_opened": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
