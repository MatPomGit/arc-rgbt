# Dataset candidates and admission criteria

**Screened: 2026-10-29. Status: primary-source metadata screening only; no downloaded archive or experimental dataset has been admitted.**

This is the central catalogue of external dataset candidates for
[research P01–P08](publications.md). It is **not** a download index,
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
| [KAIST Multispectral Pedestrian](https://soonminhwang.github.io/rgbt-ped-detection/) | Vehicle-mounted visible/thermal, day/night; approximately **95,000 pairs**, owner-reported 640×480 | P01/P02/P04: pedestrian detection in non-aerial scenes; possible P05 domain cohort | **Licence identified: default CC BY-NC-SA 4.0** in [maintainer LICENSE.md](https://github.com/SoonminHwang/rgbt-ped-detection/blob/master/LICENSE.md), with BSD exceptions for specified code; **archive version, labels and permitted derivatives not yet inspected**. Image pairing is not measured exposure synchronization |
| [M3OT (Nie et al., 2025)](https://www.nature.com/articles/s41597-025-06204-0) | **Two-UAV aerial RGB/thermal multi-object tracking**, owner-reported 10,790 paired RGB–IR images / 21,580 modality frames, ~220k boxes; [institutional dataset record](https://rgu-repository.worktribe.com/output/3195645/m3ot-a-multi-drone-multi-modality-dataset-for-multi-object-tracking-dataset) | **First P06 candidate** (identity tracking); P01/P02 only under provenance limits | **Institutional record specifies CC BY 4.0**, but exact hosted archive/version and annotation terms still need independent check. Authors report **manual temporal matching and affine/crop spatial alignment**, not hardware exposure-clock validation; **not admitted** |
| [CART / Caltech Aerial RGB–Thermal](https://data.caltech.edu/records/cks6g-ps927) | UAV RGB/LWIR, GPS/IMU, thermal and paired semantic segmentation, geographical/time splits; [owner code](https://github.com/aerorobotics/caltech-aerial-rgbt-dataset) | P02 registration/domain analysis, possible P05; **not** direct box-labelled P06 multi-object tracking | **HOLD: rights clarification**. The [owner README](https://github.com/aerorobotics/caltech-aerial-rgbt-dataset) says both “non-commercial only” and **CC BY-SA 4.0**, which normally permits commercial use; obtain unambiguous dataset-archive terms. No direct detector boxes/track IDs verified |
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

## Primary-source rights and task triage (2026-10-29)

This review checks public owner/institution/publisher **statements**, not archives. A *named licence* is not evidence that the exact downloaded version, annotation files, labels, native capture geometry or data-processing provenance meets an experimental protocol. No raw data or metadata archives were downloaded in this pass.

| Candidate | What was directly checked | Remaining gate and decision |
| --- | --- | --- |
| **M3OT** | [Scientific Data](https://www.nature.com/articles/s41597-025-06204-0) documents two-UAV thermal/RGB tracking, independent annotation for modalities and GT/COCO formats; [institutional dataset catalogue](https://rgu-repository.worktribe.com/output/3195645/m3ot-a-multi-drone-multi-modality-dataset-for-multi-object-tracking-dataset) lists CC BY 4.0 and an approximately 10.2 GB archive | **P06 PRIORITY / CONDITIONAL**: verify the actual Figshare package's ownership and licence, checksums, identity-track consistency, modality/frame IDs, sequence/flight-disjoint splits and calibration limitations. Direct Figshare record was not independently accessible during screening; no licence equivalence inferred from the paper's open-access licence |
| **KAIST** | [Maintainer licence](https://github.com/SoonminHwang/rgbt-ped-detection/blob/master/LICENSE.md) states default **CC BY-NC-SA 4.0**, while certain listed code is BSD; [owner benchmark](https://soonminhwang.github.io/rgbt-ped-detection/) documents vehicle-mounted pairs | **CONDITIONAL ACADEMIC**: validate downloaded archive licence/version, exact label and split revisions; non-commercial / attribution / share-alike obligations remain. Not an aerial evaluation dataset |
| **LLVIP** | [Owner terms](https://github.com/bupt-ai-cz/LLVIP/blob/main/Term%20of%20Use%20and%20License.md) expressly allow non-commercial research and publications, require attribution and restrict privacy-invasive uses; do **not** presume redistribution rights | **CONDITIONAL ACADEMIC**: verify release 15,488 vs original 16,836 pairs, annotations, acquisition sequences and night/day grouping. Published pairs do not establish calibrated exposure times |
| **CART** | [Owner repository](https://github.com/aerorobotics/caltech-aerial-rgbt-dataset) documents source imagery, GPS/IMU, rectification and segmentation; it calls data *non-commercial only* while naming CC BY-SA 4.0 | **HOLD LICENCE-CONFLICT**: ask rights holder which conditions apply to images, labels and derivatives. Reconcile this before dataset use; segmentation classes “person”/“vehicles” are not a substitute for detection boxes, and “synchronized” does not give measured exposure-offset uncertainty |
| **DroneVehicle** | [Owner's licence clarification issue #58](https://github.com/VisDrone/DroneVehicle/issues/58) still requests archive/image/label terms | **HOLD LICENCE-UNKNOWN**. Do not interpret code repo licence as a dataset licence |
| **FLIR ADAS** | Original FLIR download terms require separate scrutiny; third-party annotation licences do not override original image terms | **HOLD RIGHTS**; verify actual distributor terms and alignment before use |

**Spectral and geometric cautions:** distinguish thermal LWIR from NIR, manual affine alignment from calibrated intrinsics/extrinsics, and sequence start/end alignment from hardware *exposure timestamps*. M3OT's processed/cropped grid is not a substitute for native optical pixel footprint in P01. KAIST and LLVIP are ground-camera cohorts; any P05 comparison with aerial sources additionally changes viewpoint, object classes and scene distributions, so a sensor-specific generalization claim requires a design that separates these confounders.

**Next admissibility step:** begin with **M3OT P06**: inspect the exact legal release and annotations without redistribution, build a metadata-only sequence/ID/GT audit with immutable file hashes, then preregister HOTA and scene/flight splits. Parallel metadata validation for KAIST and LLVIP can support P01/P02/P04; no general B01 admission or G06 PASS is claimed.

## Study suitability, not interchangeability

**Expanded publication screening (2026-10-28):** P04 needs independently labelled failure-stratified negatives and actual fault evidence, not only synthetic corruptions. P05 needs at least two genuinely independent sensor/domain cohorts and comparable annotations, not two resizes of the same original. P06 needs paired time sequences with stable identity labels, not independent still images. M3OT is now the first P06 candidate on **primary-source metadata**; archive-specific rights, original identity labels, timing and native capture metadata still require inspection. P07/P08 remain OPTIONAL HOLD and demand instrumented hardware/calibration evidence beyond dataset downloads.


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

## Offline metadata-only preflight

Use `arc-rgbt admission --input FILE` to validate declared source metadata, track-ID duplication, modality-specific boxes and scene/flight split leakage. The [implemented contract](../reference/data-contracts.md) and synthetic demo are separate from the real `.npy` sequence checker. This audit never opens source imagery or annotations. Structural PASS **does not** certify source hashes, dataset rights, native optics, or exposure clocks and cannot promote B01 or G06. Archive rights and genuine tracking labels remain tasks [#22](https://github.com/MatPomGit/arc-rgbt/issues/22) and [#23](https://github.com/MatPomGit/arc-rgbt/issues/23).

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
