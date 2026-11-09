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

## P01 source-rights triage (2026-11-04, issue #45)

The owner-controlled text linked below was re-read on 2026-11-04; this
triage does **not** verify the downloaded archive's licence, optical
metadata, ground-truth completeness, or independent acquisition IDs.
`CONDITIONAL` permits only further *screening*, not experimental admission.
No dataset, annotation archive or model was downloaded.

| Candidate | Primary-source evidence checked 2026-11-04 | P01 suitability and missing evidence | Screening decision |
| --- | --- | --- | --- |
| **KAIST** (first ground-based candidate) | [Maintainer's licence](https://github.com/SoonminHwang/rgbt-ped-detection/blob/master/LICENSE.md) expressly applies default **CC BY-NC-SA 4.0** to repository source code and dataset; named BSD exceptions cover specified code files. | A useful RGB/thermal pedestrian cohort, but **not aerial**. Need exact release/archive terms, native *thermal* sensor grid versus aligned export, class/negative-frame annotation audit and source/drive identifiers. No inferred flight or robot deployment outcome. | **CONDITIONAL SOURCE SCREENING**, G01 **BLOCKED** |
| **LLVIP** (backup, ground low-light) | [Owner terms](https://github.com/bupt-ai-cz/LLVIP/blob/main/Term%20of%20Use%20and%20License.md) permit non-commercial research/publications with citation, prohibit commercial use and privacy identification, and reserve ungranted rights; the owner describes **26 acquisition scenes**. | Scene grouping is a candidate only; individual independent acquisition count and paired-bin support remain unverified. Need exact image/label release, LWIR band/native detector grid, complete negative labels and rights for any derivatives. | **CONDITIONAL SOURCE SCREENING**, G01 **BLOCKED** |
| **DroneVehicle** (aerial fallback) | [Owner repository discussion #58](https://github.com/VisDrone/DroneVehicle/issues/58) was still **open**, with zero comments at inspection, requesting image and annotation terms. | Relevant UAV geometry but original archive image/annotation licence remains unresolved; thermal spectral band, native grid, border/crop processing and independent flights need verification. | **HOLD RIGHTS**, no data import |
| **CART** (aerial context only) | [Owner repository](https://github.com/aerorobotics/caltech-aerial-rgbt-dataset) identified; previously documented conflict between non-commercial language and CC BY-SA remains unresolved. | Original rights require clarification; segmentation labels are not automatically complete detection boxes. Native grid and independent groups remain unverified. | **HOLD LICENCE/ANNOTATIONS** |
| **FLIR ADAS v2** (road-scene LWIR candidate) | [Manufacturer's current dataset specifications](https://oem.flir.com/en-gb/solutions/automotive/adas-dataset-form/) and [dated v2 release announcement (2022-01-19)](https://www.oem.flir.com/en-150/about/news/expanded-teledyne-flir-starter-thermal-dataset-for-adas-and-autonomous-vehicle-testing/) identify the offering and COCO annotation format; the publicly displayed page **does not grant the project rights to an exact archive revision**. | Requires original registration/download terms applicable to images **and annotations**, a release/version and hash record, real source scene/session identifiers, export-grid/optics mapping and checkpoint training lineage. COCO format alone does not guarantee `video_id`. | **HOLD UNVERIFIED ORIGINAL ARCHIVE RIGHTS AND GROUPING**, G01 BLOCKED |

**Decision for #45:** prioritize KAIST original-release verification; LLVIP
is the next legally documented academic candidate, while DroneVehicle is
the most relevant aerial option *only after rights clarification*. These
are **screening priorities**, not a final choice of a scientifically
admissible P01 source. None is currently established to supply the
independent, original-grid LWIR acquisition groups needed for D1/D2 or
a reliable source-informed power calculation. Issue #45 remains open
until exact archive and annotation terms are verified; #46-#48 and #36
own geometry, ground truth, grouping and G01 admission.

### P01 owner annotation-release control (2026-11-06; #45/#47)

These **immutable owner-repository snapshots** were inspected without
downloading image archives. They pin public documentation, **not** the
image/annotation release or independently verified native LWIR geometry.

| Candidate | Pinned owner evidence | Effect on source admission |
| --- | --- | --- |
| KAIST | [Owner README](https://github.com/SoonminHwang/rgbt-ped-detection/blob/f238a6103dce54a063fd6438d5f0d4dec8359f76/README.md) (blob `fa572999e02639493a414cf0d1b3c39aeff5bce3`) describes the 640 x 480 vehicle-mounted multispectral release, manual pedestrian/people/cyclist annotations and downloadable archive **MD5**; [owner licence](https://github.com/SoonminHwang/rgbt-ped-detection/blob/f238a6103dce54a063fd6438d5f0d4dec8359f76/LICENSE.md) (blob `98ebb42a60638241524724b5d3df642f7e806acc`) states default CC BY-NC-SA 4.0 and named BSD code exceptions. | Pin original versus sanitized/improved **label edition** with release hashes, map classes and ignores, compare original-grid bbox coordinates, and verify empty frames independently. The published MD5 is an integrity reference, not proof of annotation completeness. |
| LLVIP | [Owner README](https://github.com/bupt-ai-cz/LLVIP/blob/c1a655cce437ebfd990a97b04fc48fbb99f4c47b/README.md) (blob `7435ad3ea8d291188287a893d62b93ce8d442150`) notes the **2023-02-21** correction of omitted pedestrians and imprecise boxes and distinct raw unregistered frames/videos; [terms](https://github.com/bupt-ai-cz/LLVIP/blob/c1a655cce437ebfd990a97b04fc48fbb99f4c47b/Term%20of%20Use%20and%20License.md) (blob `2e8ce668cda533e83aef26a1fc0f7c8803843432`) state 26 collection scenes and non-commercial/privacy restrictions. | Unspecified/older labels cannot certify negative frames. Pin corrected label and image releases together, examine native-versus-registered transforms; 26 owner-named scenes are **not** 26 proven independent acquisition groups. |

**Decision:** KAIST and LLVIP stay CONDITIONAL. Neither exact dataset
release/annotation SHA-256 nor original negative-frame completeness has
been independently verified. The snapshots improve documentation
traceability only; #45-#48 and G01 remain open.

### Immutable evidence required for source-rights clearance

A source may move beyond conditional screening only when an evidence record
identifies the **exact owner-issued image and annotation release**, its
publisher-controlled terms, the rights applicable to the intended research,
and the independent native-grid and acquisition audits. An ordinary GitHub
`main` or `master` licence link is a mutable screening pointer and cannot
substitute for a pinned revision.

| P01 candidate | Owner terms commit/tag and recorded UTC access date | Exact image release SHA-256 | Exact annotation release SHA-256 | Rights freeze |
| --- | --- | --- | --- | --- |
| KAIST | **PENDING** immutable owner terms revision | **PENDING** | **PENDING** | BLOCKED: repository terms alone are insufficient |
| LLVIP | **PENDING** immutable owner terms revision | **PENDING** | **PENDING** | BLOCKED: verify original redistribution and use terms |
| DroneVehicle | **PENDING** rights-holder statement | **PENDING** | **PENDING** | HOLD: owner image/label terms unresolved |
| CART | **PENDING** reconciliation of owner terms | **PENDING** | **PENDING** | HOLD: stated terms conflict |
| FLIR ADAS | **PENDING** original archive terms | **PENDING** | **PENDING** | HOLD: access terms unverified |

Before changing any entry to PASS, store the complete owner-issued licence
text or authenticated immutable source reference, exact revision/date,
archive and annotation release identifiers plus their separate SHA-256
digests, applicable derivative/publication permissions, and a dated reviewer
decision in #45. Source geometry and independently verified acquisition
IDs belong to #46/#48; annotation/negative-frame coverage belongs to #47.
The evidence table remains incomplete until those original source materials
are lawfully inspected. **No actual dataset or annotation archive was
downloaded for this remediation.**

### FLIR Tau 2 manufacturer model-level geometry (checked 2026-11-06)

Teledyne FLIR's [ADAS dataset specifications](https://oem.flir.com/en-gb/solutions/automotive/adas-dataset-form/)
identify a **Tau 2 thermal camera with 640 x 512 detector**, 13 mm
f/1.0 optics, approximately 45-degree horizontal and 37-degree vertical
field of view, plus thermal 14-bit pre-AGC TIFF and 8-bit AGC JPEG
exports. The [Tau 2 manufacturer's product specification](https://www.flir.eu/products/tau-2?segment=oem&vertical=lwir)
identifies an **LWIR 7.5-13.5 micrometre** band and **17 micrometre
pixel pitch** for the camera model. These are verifiable model-level
specifications, not independent authentication that every file in the
operator's 12-part local archive came from exactly that model,
firmware, optical chain or unaltered native coordinate grid.

**Release identity mismatch to resolve before P01 admission:**
the manufacturer lists **9,711 thermal still images** for
training/validation, **9,233 visible still images**, and separately
**7,498 matched video frames** among the 26,442 annotated frames.
Those are distinct denominators, not interchangeable train/validation
numbers. The operator-reported local annotation index inventory
recorded via PR #65 contains **10,742 + 1,144 = 11,886 thermal
frame keys**; a secondary research paper reports the same
10,742/1,144 division, but that is **not** independent proof of the
owner-issued release, its licence or the mapping from still/video
frames. Whether the difference represents repackaging, release
edition, filtered labels, video-frame inclusion or something else
remains **UNKNOWN**. Do not silently combine these counts; require
source-specific release notes, actual annotation and archive hashes,
image/annotation file identities and documented original-to-COCO
coordinate correspondence before using physical/native footprints.

**Group-ID compatibility is a concrete preflight risk:** `video_id`
and `extra_info.video_id` are **nonstandard optional metadata**,
not guaranteed by a MSCOCO-format label declaration. The
manufacturer's public page does not document such a field for every
image, and a labelled still frame is not necessarily an independently
identified camera session. The P01 code therefore fails closed on
missing group keys or contradictory two-field identities and checks
source-video proxy overlaps; it must **not synthesize acquisition
independence from frame IDs, basename patterns or equal pixel sizes**.
If the actual release has owner-authored sequence/session metadata
outside COCO, the project must link those records with immutable
hashes before proposing the real group split. At present:
`GROUP_IDENTITIES_UNKNOWN`, `DATA_RIGHTS_HOLD`,
`NATIVE_GRID_PROVENANCE_UNKNOWN`.
Neither the camera datasheet nor equal TIFF pixel dimensions
establish independently verified annotation geometry, full negative
coverage or physical acquisition identity. Current P01 status remains
**G01 BLOCKED** and #46 remains open.

## P01 native-geometry screening contract (2026-11-05; #46)

The dimensions of a distributed image, an aligned RGB/thermal pair, and the
native photosensitive detector grid are different quantities. P01's proposed
`sqrt(w_native * h_native)` bins require bounding boxes referenced to the
**original LWIR detector grid** or a fully documented, independently checked
inverse transform. An annotation on an aligned, cropped, padded or resized
export cannot be relabelled native merely because its file dimensions are
known. A thermal-looking or infrared image does not establish the LWIR band.

| Source | Current geometry evidence | Native LWIR band, detector grid, pixel pitch/optics | Export transformations and box convention | P01 decision |
| --- | --- | --- | --- | --- |
| KAIST | Owner reports paired 640 x 480 imagery; distributed dimensions are not proof of the original thermal focal-plane grid. | **UNKNOWN** until original sensor specification and release mapping are pinned. | **UNKNOWN** whether original annotations describe raw, aligned, cropped or resampled LWIR; visible versus amodal boxes unverified. | **CONDITIONAL SCREENING**, not eligible for physical-footprint inference yet. |
| LLVIP | Owner reports paired visible/infrared scenes; pair membership is not native-grid provenance. | **UNKNOWN** for original thermal band, sensor grid, pitch and optics. | **UNKNOWN** for resampling, pairing transform and occluded/amodal labels. | **CONDITIONAL SCREENING**, not admitted. |
| DroneVehicle | Owner describes aerial visible/infrared oriented boxes; reported white borders may alter exported coordinates. | **UNKNOWN** for native thermal grid, band, pitch and optics. | **UNKNOWN** original-to-export crop/pad transform and conversion of oriented boxes to a physical footprint. | **HOLD RIGHTS AND GEOMETRY**. |
| CART | Owner describes aerial RGB/thermal segmentation and geographic/time splits. | **UNKNOWN** for independently verified original LWIR grid, pitch and optics. | Segmentation polygons are not validated detector boxes; original-to-export mapping **UNKNOWN**. | **HOLD RIGHTS AND ANNOTATIONS**. |
| FLIR ADAS | Owner describes thermal imagery and pre-AGC frames; exact original archive is not inspected. | **UNKNOWN** for the specific release's source detector grid and optics. | **UNKNOWN** box-coordinate provenance, crop/AGC and full negative-frame labels. | **HOLD RELEASE TERMS AND GEOMETRY**. |

**Source-specific evidence required before changing a decision:** (1) exact
archive/release and owner-controlled, immutable sensor documentation; (2)
spectral response or verified LWIR sensor identity; (3) original detector
width/height, optics, pixel pitch where available, bit depth and AGC status;
(4) an explicit coordinate chain from detector pixels to distributed images
and GT, including scale, crop, padding, warps and interpolation; (5) visible
versus amodal box convention, orientation and annotation completeness; (6)
an independently reproducible check on original files with release hashes.
If a coordinate chain is unavailable, report distributed-image footprint
only as an **export-grid proxy** and exclude it from the confirmatory
native-footprint estimand. Do not infer metric range or optical resolution
from exported pixel dimensions. Screening is metadata-only; G01 remains
BLOCKED and #46 remains open until original-source verification.

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

## Acquisition-group split preflight and metrics

The `arc-rgbt split` command produces deterministic metadata-only **proposals** that preserve declared flight/scene groups; optional `--device-disjoint` groups sources by device too. It does not inspect pixels, source archive, metadata truth or near-duplicates. Details and current metric limits (single-IoU AP, FP/frame, HOTA/IDF1 deferred) are in [data contracts](../reference/data-contracts.md). **M0 source admission and G06 remain pending**.

## Local image leakage preflight

After independent confirmation of rights for a locally held subset, `arc-rgbt near-duplicates` can re-hash user-provided JPEG/PNG files and flag same-band, cross-split dHash similarities for **manual review**. Its [read-only contract](../reference/data-contracts.md) requires an image-path map tied to exact admission frame IDs and rejects hash mismatch. It is not a substitute for original M3OT flight logs or complete source-image review; no source files are bundled in the repository.

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
