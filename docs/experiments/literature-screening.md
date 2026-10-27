# Aerial RGB–thermal literature: screened candidates

This is a **selective screening note**, not a systematic review, verified
bibliography, reproduced benchmark, or evidence of the platform's performance.
It derives from an owner-supplied research export containing 98 records
reviewed on 27 October 2026. Original files, abstracts and extended
third-party text were **not copied** to the public repository.

## Input quality and selection rules

The export has **98 records, 91 distinct case-normalized titles,
75 DOI-bearing rows and 72 distinct DOI strings**. Twenty-three records
lack a DOI. Some identical studies occur as duplicate titles, distinct
links, preprint and published versions; at least three DOI values repeat.

Select references about native optical/thermal imaging, small-object
evaluation, dual-modality fusion, annotated datasets or resource-aware
vision. Exclude promotional comparisons, unsupported quantitative
generalizations, operational pursuit instructions and unrelated
drone-versus-drone surveillance objectives. Each shortlisted DOI is a
**bibliographic candidate** until checked against the publisher's
version of record.

## Shortlist linked to research packages

| Study (year) | DOI / publication record | Relevant issue | Verification |
| --- | --- | --- | --- |
| Illumination-aware image fusion (2022) | [10.1016/j.eswa.2022.117413](https://doi.org/10.1016/j.eswa.2022.117413) | P02: illumination strata and RGB–LWIR comparison | Publisher record inspected |
| Drone-based RGBT dual-feature aggregation (2023) | [10.3390/drones7090585](https://doi.org/10.3390/drones7090585) | P02: multimodal baselines; distinguish tracking from detection | Publisher record inspected |
| Infrared/visible small-object detection (2023) | [10.3390/rs15133214](https://doi.org/10.3390/rs15133214) | P01/P03: small objects, resource claims and input scales | Publisher record inspected |
| Thermal aerial imagery in wooded areas (2023) | [10.3390/s23229216](https://doi.org/10.3390/s23229216) | P01: occlusions, thermal contrast and evaluation splits | Publisher record inspected |
| Low-pixel infrared detection (2020) | [10.1145/3416014.3424600](https://doi.org/10.1145/3416014.3424600) | P01: object footprint sensitivity | Metadata only |
| BIRDSAI aerial thermal video dataset (2020) | [10.1109/WACV45572.2020.9093284](https://doi.org/10.1109/WACV45572.2020.9093284) | P01: dataset design and independent acquisition splits | Metadata only |
| Aerial RGB and IR detection comparison (2023) | [10.1007/s42405-023-00632-1](https://doi.org/10.1007/s42405-023-00632-1) | P01/P02: paired modality data and comparators | Metadata only |
| Thermal imagery and transfer learning (2022) | [10.3390/drones6100290](https://doi.org/10.3390/drones6100290) | P01: thermal domain shift and small-object evaluation | Metadata only |
| Thermal infrared occlusion studies (2021) | [10.3390/drones5030065](https://doi.org/10.3390/drones5030065) | P02: occlusion failure strata, metrics | Metadata only |
| Thermal/visible multimodal fusion (2022) | [10.2352/EI.2022.34.14.COIMG-179](https://doi.org/10.2352/EI.2022.34.14.COIMG-179) | P02: domain-specific fusion comparison; deduplicate versions | Metadata only |
| Multi-sensor object comparison (2022) | [10.3390/drones6110317](https://doi.org/10.3390/drones6110317) | P02: sensor modality ablation | Metadata only |
| Sensors and multi-modal object inference (2023) | [10.3390/s23052746](https://doi.org/10.3390/s23052746) | P02: fusion metrics and reproducibility checks | Metadata only |

“Publisher record inspected” means the DOI/title and broad topic were
checked against an original publisher page. It does **not** mean its
numerical results were independently replicated, the dataset licence
approved, or its claims transferred to `arc-rgbt`.

## Primary-paper screening checklist

For each selected article, record in a future structured study matrix:

- Correct title, authors, publisher, DOI and the version of record.
- Actual acquisition modality: RGB, NIR, MWIR, LWIR or transformed intensity.
- Sensor/native grid, FOV, exposure timing, calibration and data splits.
- Whether the task is detection, tracking, fusion, classification or
  simulation; do not interchange performance metrics.
- Ground truth, negatives, held-out scenes/devices and data licence.
- Confidence intervals, independent sample unit and failure classes.
- Actual hardware workload, end-to-end latency, energy instrumentation
  and whether the inference code/data can be reproduced.

**Do not import as project facts** the source review's context-free
claims of “over 20%” multimodal improvement, fixed detection ranges,
an all-purpose 85% “accuracy”, universal tracking RMSE or embedded FPS.
Even where a paper reports such results, comparability must be
established from its own dataset, metric and operating point.

See [measurement requirements](../guides/evaluation-requirements.md)
and the [P01–P03 programme](publications.md).
