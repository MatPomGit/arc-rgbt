# E00: Thermal native resolution sweep

**Implemented, synthetic-only.** Run `arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00`.

The experiment generates 20 seeded grayscale scenes with two labelled luminous rectangles per frame, creates degraded native arrays at 8x8, 16x12, 32x24, 80x60, 160x120, 256x192 and 320x240, and evaluates a fixed-threshold, connected-component **class-agnostic localization** baseline against synthetic bounding boxes. Each resolution yields one identical source-scene collection and deterministic noise seed. GT is projected and rounded outward into native pixels; this may enlarge subpixel objects. Predictive labels are deliberately `object`, not `person` or `vehicle`.

The resulting CSV/HTML rows describe native pixels independently of 640x480 nearest-neighbour display previews. Neither optical PSF nor the detector is physically calibrated. `manifest.json` records configuration, version, Git SHA if available and per-resolution degradation details. Results are generated on demand and not tracked.


## Unrounded geometric observability (P01)

The native-pixel box produced by outward integer rounding is **not** evidence that a
target occupies one resolvable sensor pixel. E00 additionally reports:
`median_unrounded_bbox_area_native_px2`, obtained by continuously scaling source
annotation dimensions without quantization, and
`fraction_objects_subpixel_axis`, the fraction of objects whose unrounded
footprint is below one pixel along at least one axis.

These are deterministic **geometric diagnostics**, not sensor measurements or
probabilities of detection. E00's class-agnostic rectangles cannot support
claims about recognizing people, vehicles, or physical thermal cameras.
