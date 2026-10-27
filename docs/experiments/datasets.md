# Dataset candidates and admission criteria

**Screened: 2026-10-27. Status: candidate inventory, not approved experimental data.**

This is the central catalogue of external dataset candidates for
[research P01–P03](publications.md). It is **not** a download index,
training-data mirror, executable import schema, dataset licence grant,
or claim that the project has acquired real measurements. The existing
`datasets/manifests/` files contain **synthetic reference fixtures**,
not accepted field datasets. Dataset selection is tracked under
[RGBT-02 / A02_DATA](https://github.com/MatPomGit/arc-rgbt/blob/main/AUTOPILOT_PLAN.md)
and [Issue #10](https://github.com/MatPomGit/arc-rgbt/issues/10).

## Candidate catalogue

The counts below describe what the **dataset owners report** for the cited
release; actual archives, annotations, sensor metadata and usable subsets
have not been independently inspected. “Pair” means a supplied association,
**not** independently verified same-exposure synchronization or calibrated
pixel-to-pixel geometry.

| Dataset and primary source | Modalities, scope and owner-reported scale | Possible study use | Admission / rights status |
| --- | --- | --- | --- |
| [LLVIP](https://github.com/bupt-ai-cz/LLVIP) | Visible and infrared, low-light pedestrian scenes; **15,488 pairs** in the updated 30,976-image release | P01: detection under degraded visible lighting; P02: paired late-fusion baseline | **Restricted non-commercial use** with attribution and privacy obligations; verify official [terms](https://github.com/bupt-ai-cz/LLVIP/blob/main/Term%20of%20Use%20and%20License.md) and exact annotation release; no automatic redistribution |
| [KAIST Multispectral Pedestrian](https://soonminhwang.github.io/rgbt-ped-detection/) | Vehicle-mounted visible/thermal, day/night; approximately **95,000 pairs**, owner-reported 640×480 | P01: measured low-resolution inputs; P02: paired detections and scene holdouts | Identity documented; **archive rights and current permitted use still require confirmation**; documented image pairing is not a measured clock-offset record |
| [DroneVehicle](https://github.com/VisDrone/DroneVehicle) | Aerial RGB/infrared, **28,439 pairs**, five vehicle categories with oriented boxes | P01: aerial small-object geometry; P02: modality comparison | **HOLD**: image/annotation licensing unresolved in the [owner's open discussion](https://github.com/VisDrone/DroneVehicle/issues/58). Reported 100-pixel white borders must not become artificial native-image evidence |
| [FLIR ADAS](https://oem.flir.com/en-gb/solutions/automotive/adas-dataset-form/) | Road-scene thermal and RGB, still/video annotations; owner reports **26,442 annotated frames** in the described offering, including 16-bit pre-AGC thermal frames | P01: thermal detector and bit-depth comparison; possible separate-modality control | **HOLD**: download registration and actual use/redistribution terms must be reviewed; same-scene RGB/thermal must **not** be assumed to be geometrically registered |
| [EPFL RGB–NIR Scene Dataset](https://www.epfl.ch/labs/ivrl/research/downloads/rgb-nir-scene-dataset/) | **477 RGB/NIR image sets**, 9 scene categories; aligned processed TIFF (1024×768) | NIR branch: registration, domain comparison or paired-image sanity checks | Rights still to verify; **NIR is not LWIR**; no directly applicable detector bounding-box labels claimed |

For LLVIP, the 2021 [paper](https://openaccess.thecvf.com/content/ICCV2021W/RLQ/html/Jia_LLVIP_A_Visible-Infrared_Paired_Dataset_for_Low-Light_Vision_ICCVW_2021_paper.html)
describes **16,836 original pairs**; the official repository documents a
subsequent filtered **15,488-pair** release and later annotation
corrections. Record the exact version instead of mixing these totals.

KAIST's official documentation discusses aligned image pairs and multiple
evaluation conventions. Reusing published results without matching the
split, label revision and protocol invalidates a direct numerical comparison.
DroneVehicle has **oriented** bounding boxes and padded images; note both
before converting to the project's current axis-aligned Bench schema.

## Study suitability, not interchangeability

- **P01 (native spatial limits):** prefer external labelled data with
  recoverable *native* sensor frames and independent source scenes.
  Resizing a high-resolution image can test a controlled algorithmic
  perturbation but **cannot replace** measured low-resolution optics.
- **P02 (registration and fusion):** require reliable modality pairing,
  a declared coordinate frame, independent scene-level holdouts and
  quality estimates not fitted to test labels. A paired image folder
  is **not proof of exposure-time clock synchronization** or measured
  calibration residuals.
- **P03 (embedded trade-offs):** datasets supply fixed evaluation
  workloads and labels. CPU timing, a dataset's FPS or the author-reported
  sensor rate is **not** physical target RAM, flash, energy or latency.
- **NIR subgroup:** analyze RGB/NIR separately from RGB/LWIR;
  different spectral response means these are not substitute modalities.

No candidate above has been promoted to independently verified,
legally cleared physical experimental evidence. Consult the canonical
[measurement requirements](../guides/evaluation-requirements.md),
[data contracts](../reference/data-contracts.md) and
[study protocols](publications.md).

## Admission checklist for A02_DATA / B01_REAL_DATA

Record the following **before** obtaining, importing or reporting a dataset:

1. **Source and rights:** canonical owner, stable dataset release,
   publication, access date, original licence or signed terms;
   permitted training, publication, derivative annotations,
   redistribution and commercial use; privacy and consent constraints.
2. **Acquisition and modalities:** actual visible/NIR/MWIR/LWIR bands,
   native pixel grids, original bit depths, pre-/post-AGC radiometry,
   camera identity, optics and processing/resampling history.
3. **Pairing and calibration:** modality IDs, matching source sequence,
   *exposure* timestamps and clock domain (or explicit `unknown`),
   original geometric calibration, registration residuals, valid masks.
4. **Annotations:** task and categories, box conventions (axis-aligned
   vs oriented), missing/negative-label policy, annotation version,
   quality audit and conversion tests.
5. **Split and provenance:** independent acquisition session,
   scene/device/subject grouping, duplicate and near-duplicate audit,
   separated train/validation/test assignment and immutable input hashes.
6. **Validation:** preregistered metrics and exclusions, pilot failures,
   independent review, traceable code SHA and a decision:
   **approved**, **restricted**, **needs review** or **rejected**.

A public download URL or a research-paper citation is **not** itself
permission to use, copy or distribute a dataset.

### Metadata record (documentation example only)

The following illustrates a dataset screening record, **not an
implemented input format** for `bench-rgbt`, E01 or E02:

```yaml
dataset_id: example_candidate
version: not_verified
owner_source_url: https://example.org/original-dataset
modality_bands: [rgb, thermal_band_unverified]
native_geometry: unknown
bit_depth_and_processing: unknown
exposure_clock: unknown
spatial_registration: unknown
annotation_version: unknown
scene_grouped_split: not_verified
licence_and_redistribution: needs_review
privacy_review: needs_review
raw_data_imported: false
approval: needs_review
```

Keep completed metadata and approved small manifest files versioned, but
**do not commit raw imagery, restricted annotations, private information,
third-party weights or downloaded archives**. Never add an automatic
downloader as a prerequisite of the offline tests.

## Next decision

**RGBT-02 remains open:** verify the primary licence and an independently
auditable subset for at least one RGB/thermal dataset, plus a separate
NIR candidate if studied; freeze the exact image/annotation version and
scene-based split. Until that is documented and reviewed, the
[scientific status](https://github.com/MatPomGit/arc-rgbt/blob/main/PROJECT_STATE.yaml)
remains `independent_sensor_dataset: not_yet_verified`.
