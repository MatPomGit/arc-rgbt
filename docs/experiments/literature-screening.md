# Aerial RGB–thermal literature: screened candidates

This page is a **selective bibliographic screening**, not a systematic
review, confirmed dataset licence or independent reproduction of results.
The source is a user-provided literature export and historical technical
review, screened on 27 October 2026. Original third-party abstracts,
full texts and internal design documents are not stored in this repository.

## Source audit and limitations

The export contains **98 rows**, **91 distinct case-normalized titles**,
**75 DOI-bearing rows** and **72 distinct case-normalized DOI values**.
There are **23 rows without a DOI**. It includes multiple records for the
same work and mixes preliminary, published and secondary metadata.
These counts describe the *export*, not the number of eligible studies.

Relevant items address optical/thermal pixel footprint, documented
RGB–LWIR fusion, aerial thermal datasets, frame-level failure modes and
resource-aware inference. References were selected for questions P01–P03,
not to support generic quantitative performance promises.

## Shortlist, by research question

“Publisher” means the publication's publisher page was checked for
*identity and topic*, not for independently reproducible results.
“Institutional” means an author/institutional bibliography or university
publication record supports identity; a primary-publisher check may still
be required. “Export only” means metadata have **not** yet been
independently confirmed.

| Publication / subject (year) | Identifier | Role in arc-rgbt | Identity check |
| --- | --- | --- | --- |
| Golcarenarenji et al., illumination-aware fusion (2022) | [10.1016/j.eswa.2022.117413](https://doi.org/10.1016/j.eswa.2022.117413) | P02: illumination conditions and fusion baselines | Publisher |
| Gao et al., dual-feature RGBT **tracking** (2023) | [10.3390/drones7090585](https://doi.org/10.3390/drones7090585) | P02: tracking-specific methods; **not** a detector evaluation | Publisher |
| Infrared/visible YOLOv7-Tiny detection (2023) | [10.3390/rs15133214](https://doi.org/10.3390/rs15133214) | P01/P03: small objects and input/compute budgets | Publisher |
| Ramírez-Ayala et al., wooded-area thermal imagery (2023) | [10.3390/s23229216](https://doi.org/10.3390/s23229216) | P01: occlusion and dataset stratification | Publisher |
| Low-pixel infrared detection (2020) | [10.1145/3416014.3424600](https://doi.org/10.1145/3416014.3424600) | P01: low-resolution candidate, pending record check | Export only |
| Bondi et al., BIRDSAI aerial thermal dataset (2020) | [10.1109/WACV45572.2020.9093284](https://doi.org/10.1109/WACV45572.2020.9093284) | P01: acquisition and independent sequence splits; licence pending | Institutional |
| Bae et al., RGB/IR human detection (**2024 journal issue**) | [10.1007/s42405-023-00632-1](https://doi.org/10.1007/s42405-023-00632-1) | P01/P02: sensor pairing and image-generation domain shift | Institutional |
| Mantau et al., thermal aerial transfer learning (2022) | [10.3390/drones6100290](https://doi.org/10.3390/drones6100290) | P01: modality-separated training and metric definitions | Publisher |
| Yeom, aerial thermal tracking (2021) | [10.3390/drones5030065](https://doi.org/10.3390/drones5030065) | P02: single-modality comparison and failure strata | Publisher |
| Yang et al., drone-acquired RGB/IR imagery fusion (2022) | [10.2352/EI.2022.34.14.COIMG-179](https://doi.org/10.2352/EI.2022.34.14.COIMG-179) | P02/P03: synthetic infrared data versus field tests | Publisher |
| Hu et al., lightweight visible/IR image fusion (2024) | [10.5194/isprs-archives-XLVIII-1-2024-225-2024](https://doi.org/10.5194/isprs-archives-XLVIII-1-2024-225-2024) | P02/P03: algorithmic fusion and documented deployment context | Publisher |
| Rudol and Doherty, visible/thermal aerial imaging (2008) | [10.1109/AERO.2008.4526559](https://doi.org/10.1109/AERO.2008.4526559) | P01/P02: historical optical/thermal validation context | Institutional |

**Important correction:** the imported Bae entry is labelled 2023, but
the university's record gives a **2024** journal publication (volume 25,
pages 164–175); the DOI suffix retains “2023”. Prefer the final article
metadata. The export also contains inconsistent/duplicate author records,
so it should not be treated as the canonical source for authorship.

**Scope corrections:** DOI
`10.3390/drones6110317` concerns *detecting flying drones* using
different sensors, whereas `10.3390/s23052746` concerns
*millimeter-wave radar and video* fusion. Neither is a direct
RGB–thermal airborne-imaging baseline; both were removed from the
previous shortlist. Duplicate records for Yang et al. with the same
case-normalized DOI count as **one** study.

## How to validate a citation for a manuscript

Before interpreting or citing an empirical result:

1. Confirm the version of record, title, authors, year and DOI from
   the publisher; keep preprint/published versions linked.
2. Inspect the *actual* modalities: visible RGB, NIR, MWIR, LWIR,
   estimated thermal imagery or radar; these are not interchangeable.
3. Separate detection, tracking, classification, pixel fusion and
   analytical simulation; report the metric used by the source.
4. Record native image grids, target footprint, optics, calibration,
   exposure timestamps, data split, annotation quality and licence.
5. Distinguish measured physical hardware latency/energy from host
   profiling and from author-reported device specifications.
6. Record conditions and uncertainty; never transfer a study's reported
   accuracy/range/FPS or comparative gain to other hardware.

The short descriptions in the table are **topic labels**, not verbatim
publication titles. They do not imply an independent audit of the
underlying experiments.

See [measurement requirements](../guides/evaluation-requirements.md),
[evidence rules](../concepts/evidence.md) and
[P01–P03 study programme](publications.md).
