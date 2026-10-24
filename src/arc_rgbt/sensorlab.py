"""Frontal-plane camera geometry with explicit millimetre, micrometre, metre units."""

from __future__ import annotations

import argparse
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from arc_rgbt.common import exact_keys, load_yaml, positive_integer, positive_number, save_json


@dataclass(frozen=True)
class Camera:
    width_px: int
    height_px: int
    pixel_pitch_um: float
    focal_length_mm: float

    @classmethod
    def from_yaml(cls, path: str | Path) -> Camera:
        data = load_yaml(path)
        exact_keys(data, {"width_px", "height_px", "pixel_pitch_um", "focal_length_mm"})
        return cls(
            positive_integer(data["width_px"], "width_px"),
            positive_integer(data["height_px"], "height_px"),
            positive_number(data["pixel_pitch_um"], "pixel_pitch_um"),
            positive_number(data["focal_length_mm"], "focal_length_mm"),
        )


def geometry(cam: Camera, range_m: float, object_width_m: float, object_height_m: float) -> dict:
    for name, val in asdict(cam).items():
        (positive_integer if name.endswith("_px") else positive_number)(val, name)
    d = positive_number(range_m, "range_m")
    ow = positive_number(object_width_m, "object_width_m")
    oh = positive_number(object_height_m, "object_height_m")
    sensor_width_m = cam.width_px * cam.pixel_pitch_um * 1e-6
    sensor_height_m = cam.height_px * cam.pixel_pitch_um * 1e-6
    focal_m = cam.focal_length_mm * 1e-3
    fov_h = math.degrees(2 * math.atan(sensor_width_m / (2 * focal_m)))
    fov_v = math.degrees(2 * math.atan(sensor_height_m / (2 * focal_m)))
    gsd = d * cam.pixel_pitch_um * 1e-6 / focal_m
    pw, ph = ow / gsd, oh / gsd
    return {
        "camera": asdict(cam), "range_m": d, "fov_horizontal_deg": fov_h,
        "fov_vertical_deg": fov_v, "gsd_m_per_pixel": gsd,
        "object_width_native_px": pw, "object_height_native_px": ph,
        "object_area_native_px2": pw * ph,
        "object_frame_coverage_fraction": min(1.0, ow / (gsd * cam.width_px))
        * min(1.0, oh / (gsd * cam.height_px)),
        "assumptions": "pinhole, square pixels, frontal planar target, no lens distortion",
        "data_origin": "analytical_estimate",
    }


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--camera", required=True)
    p.add_argument("--range-m", type=float, required=True)
    p.add_argument("--object-width-m", type=float, required=True)
    p.add_argument("--object-height-m", type=float, required=True)
    p.add_argument("--output", default="reports/sensorlab.json")
    a = p.parse_args(argv)
    print(save_json(a.output, geometry(Camera.from_yaml(a.camera), a.range_m,
                                      a.object_width_m, a.object_height_m)))


if __name__ == "__main__":
    main()
