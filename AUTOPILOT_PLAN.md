# arc-rgbt research work plan

**Version 1.4.0 · updated 2026-11-07.** Six CORE planned studies P01–P06 and two OPTIONAL HOLD studies P07–P08. This file owns work packages, not a second copy of research methods: use [RESEARCH.md](RESEARCH.md), the individual protocols and machine-readable [PROJECT_STATE.yaml](PROJECT_STATE.yaml).

## Current execution queue and issue milestones

**Execution ownership:** [Issue #21, M0–M6](https://github.com/MatPomGit/arc-rgbt/issues/21) is the current checklist and dependency index; linked issues #10, #17–#19, #22–#29 specify atomic agent runs, acceptance evidence and blocked tasks. Use this tracker before selecting the next run. This Markdown file owns work-package definitions; `PROJECT_STATE.yaml` remains the machine-readable scientific gate authority. An issue marked complete must not automatically promote a dataset or optional publication.

**P01 current priority (2026-11-07):** see the mandatory dated execution queue below. Existing M3OT [#22](https://github.com/MatPomGit/arc-rgbt/issues/22) and common data contracts [#23](https://github.com/MatPomGit/arc-rgbt/issues/23) remain shared prerequisites, not permission to divert the active P01 stream. All tasks remain subject to the one-active-PR rule. Empirical M2–M4 work still depends on independently admitted actual data/hardware; P07/P08 remain M6 OPTIONAL HOLD.


## Mandatory agent execution plan: P01 Sensors (2026-11-07; automation-first)

**Author directive (2026-11-07):** prioritize autonomous research on authorized existing labelled datasets. Do not create two-reviewer forms or galleries, manual source-image relabelling, adjudication, extra dataset QA workstreams, or new human dependencies without explicit author authorization. Existing labels are the reference provided by the source, NOT independently verified complete ground truth. This supersedes older P01 manual-QA instructions in historical issues.

### Research design and evidence classes

**Tier A (default, dataset-relative):** Measure detector recall vs. supplied GT over source-recorded target-footprint bins on real FLIR ADAS v2 (or permitted alternative). Report FP/frame and AP relative to supplied GT; an unlabelled target may be counted as an apparent FP. RGB only secondary, fusion mainly P02. Lock class/ignore rules, checkpoint, split, footprint strata, validation threshold and uncertainty choices before viewing held-out outcomes. Group by actual source acquisition/session when verifiable; video IDs alone are only proxies. If independence/power cannot be justified, label estimates DESCRIPTIVE_ONLY rather than false-confirmatory.

**Tier B (conditional physical claim):** Original native LWIR grid, sensor/optics provenance, meaningful acquisition independence and available source documentation must support physical sensor-limit interpretation. Without evidence keep physical limits, causal pixel effects, sensor range and robot-deployment claims BLOCKED. A genuine Tier A benchmark may proceed under its narrower scope; shifting claim class or primary endpoint requires author sign-off and a prospective protocol before untouched test access. Synthetic E00 is separately marked SIMULATED.

### Agent operations and controls

1. Read newest plan, issues #21/#24/#35-#40, applicable P01 protocol, active issues/PRs, source and code. Reuse existing shared validator #23 and current PR; only one active PR in this repo. Do not fragment branches or produce report-only changes.
2. Agent autonomously prepares methods, existing-dataset integration, split manifest, experiment code/config, statistical computation, plots, literature and manuscript; reuse validation code. New tests are limited to essential changed scientific computations; do not invent standalone database/dataset testing without author permission.
3. For source data/GPU only on local Fedora, prepare ONE short safe offline command (or at most a few pasteable commands) to run approved evaluation, producing hashes, small CSV/JSON outputs outside Git; no manual classification, raw-image upload, paid downloads or model spend. Never claim the remote dataset was inspected.
4. Require lawful source access, immutable version/hashes, train/validation/test group isolation, no held-out threshold tuning, truthful measurement provenance, and precise distinctions between code PASS, dataset admission, physical evidence and author scientific GO.
5. Output real measurement tables and figures with axes, denominators, metrics, uncertainty appropriate to groups, false positives relative to source GT, negative results, model/config/data SHA and a claims-to-evidence map. Independent review at the end means numerical reproduction, code and manuscript scientific scrutiny, not reannotating the source.
6. Human involvement: final primary protocol/claim decision; optionally one minimal local command; final author decision to submit. No recurrent reviewer assignments or spreadsheet chores. Never email/contact publishers, spend or submit without explicit authorization.

### Same milestone dates, rebuilt deliverables

| Gate | Due | Deliverable, automated where possible |
| --- | --- | --- |
| #35 | 2026-11-13 | Reviewable hypothesis, reference-label and FP/frame conventions, expected uncertainty, dataset-relative vs physical claim decision, fit/novelty abstract (unsent). Link #45-#53. One explicit author protocol decision only. |
| #36 | 2026-12-11 | Permitted source/release/hash record; automatic acquisition/group-disjoint split and counts, light schema compatibility, documented Tier A/Tier B feasibility. #10/#23 shared; #22 only if M3OT used; #54-#57. No human label QA. |
| #37 | 2027-01-15 | #58 validation-only model/threshold lock and short offline launcher; #59 single untouched test evaluation; #60 real metrics, uncertainty, error analysis and hashes. If Tier B blocked, Tier A may run with prospectively restricted claims. |
| #38 | 2027-02-05 | Complete manuscript v0.1, automatically derived tables/figures, references and honest limitations. #52/#61. Write non-results sections in parallel. |
| #39 | 2027-02-26 | #62 independent numerical reproduction and paper/code/novelty review under #29, not manual annotation rechecks. |
| #40 | 2027-03-19 | Verified UNSENT submission bundle and explicit author GO/NO-GO; publisher deadline 2027-03-31. |

**Immediate priority (2026-11-07):** finish #35/#47/#48/#50/#51 with existing GT and real source information; #45/#46 license/original optics via existing documentation; build #54-#57 automatic splits/feasibility; reuse #58-#60 for actual experiment. #49 only necessary inference-method check, no expanding synthetic QA. #52 desk fit/novelty without emailing. Historical completed checks are evidence, not a mandate for extra work.

**Decision boundaries:** Tier A external-data benchmark is not Tier B physical proof. If insufficient independent groups, report descriptive results and constraints; do not impose human reannotation as an agent-created block. PROJECT_STATE.yaml G01 remains unchanged until evidence-backed scientific decision. No fabricated results or automatic GO. Report each run concisely: accomplished artifacts+SHA, next autonomous task, real blockers/minimal terminal command, schedule deviation.

## GitHub Actions free-use and billing policy (verified 2026-11-02)

The repository is **public**. Standard GitHub-hosted runner labels (including `ubuntu-latest`, `windows-latest`, standard macOS and GitHub-provided standard ARM64 labels) have **$0 Actions compute cost, without a monthly minutes cap** in public repositories. The commonly quoted private-repo 2000/3000-minute monthly allowances DO NOT cap this public-repository standard-runner usage. Self-hosted runner usage currently also incurs no GitHub Actions runtime charge, but electricity, hardware and local maintenance are not free. Larger GitHub-hosted runners, external paid APIs, private-repo minutes, artifact/package storage beyond the relevant allowance, and other metered services may incur charges. No paid runners, service purchases or unlimited storage without explicit budget authorization. If repository visibility changes, re-evaluate this policy *before* running jobs.

**Zero-cost rule (explicit):** Standard GitHub Actions execution on GitHub-hosted standard runners in this PUBLIC repository, including regular CI, repeat tests, documentation checks and necessary re-runs, is an **approved zero-cost activity** and DOES NOT conflict with the project's `zero-cost` / `zero-spend` policy. There is **no monthly Actions-minute quota to conserve for this public standard-runner use**. Agents may invoke these free workflows as often as reasonably required to validate changes and exact SHA, subject to GitHub technical limits, acceptable use, security policy, workflow triggers and repository permissions. Free compute does not authorize paid tools or unlimited artifacts/storage.

**Education entitlement (owner-declared):** The repository owner has the **GitHub Education educator/teacher package**. GitHub Education teacher benefits can include access to free GitHub Team (on eligible, separately enabled organizations) and educator Copilot Pro. Do not infer that any particular benefit, organization entitlement, private-repository allowance or additional service is active or free without checking the actual account/organization billing settings. **The zero-cost permission for standard-runner CI here follows from repository PUBLIC visibility, independent of Education.** Educator benefits are additional potential allowances, not authorization to spend.

**Reviewed workflow labels (2026-11-02):** `.github/workflows/research-pr-validation.yml` and `pages.yml` use `ubuntu-latest` (standard public hosted runner); `offline-tests.yml` and `docs-check.yml` use a trusted `[self-hosted, linux, x64]` runner and are `workflow_dispatch` plus main-ref guarded. **Do not loosen these existing trust boundaries solely for free CI usage.** PR code must never execute on persistent self-hosted runners.

**Operational rule:** use standard GitHub-hosted ephemeral runners for trustworthy or isolated PR lint/unit/docs checks, with exact head SHA, least permissions, pinned actions, short job timeouts and cancel-in-progress for superseded PR runs. More free runs are allowed when they improve reliability; don't intentionally spam or overload public infrastructure. Preserve storage limits through minimal retained artifacts and short retention; monitor GitHub concurrency, service usage and billing controls. Avoid charging Copilot/LLM APIs, large-runner labels and other metered providers just because Actions minutes are free.

Official sources (checked 2026-11-02):
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/limits
- https://docs.github.com/en/education/about-github-education/github-education-for-teachers/about-github-education-for-teachers
- https://docs.github.com/en/education/about-github-education/github-education-for-teachers/apply-to-github-education-as-a-teacher
- https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/

## Work packages

| ID | Work | Acceptance gate | Stream |
| --- | --- | --- | --- |
| RGBT-01 | Freeze P01/P02 outcomes, negative controls and independent splits | Versioned, reviewable P01/P02 protocols | P01/P02 |
| RGBT-02 | Audit RGB/LWIR/NIR candidate datasets, licences, labels and provenance | Accepted lawful release with verified native modality and scene grouping | P01/P02/P04/P05/P06 |
| RGBT-03 | Measure exposure-clock alignment and RGB/LWIR registration | Independent time skew, residuals and valid overlap | P02; prerequisite P08 |
| RGBT-04 | Evaluate native resolution/degradation against real data | Independent low-resolution labelled scenes; uncertainty separate from synthetic E00 | P01 |
| RGBT-05 | Compare RGB, thermal, fixed and adaptive fusion | Held-out measured calibration, fair operating points and independent reliability weights | P02 |
| RGBT-06 | Instrument a named constrained target | Physical device RAM/flash/latency/energy logs and perception metrics | P03; prerequisite P07 |
| RGBT-07 | Independent evidence and non-overlap publication GO/NO-GO | Paper-specific auditable evidence and scientific novelty review, no automatic submission | P01–P08 |
| RGBT-08 | Predeclare modality failures and selective risk policy | [G04](publications/P04/protocol/README.md): held-out fault-stratified labels and risk/coverage baselines | P04 |
| RGBT-09 | Verify and test genuine cross-sensor transfer | [G05](publications/P05/protocol/README.md): two independent labelled sensor domains and leakage-free holdout | P05 |
| RGBT-10 | Test multi-object temporal identity consistency | [G06](publications/P06/protocol/README.md): real paired sequences, ground-truth track IDs and HOTA audit | P06 |
| RGBT-11 | **OPTIONAL HOLD:** adaptive sensing/compute and measured policy energy | [G07](publications/P07/protocol/README.md): P03 physical benchmark + adaptive hardware measurements + non-overlap PASS | P07 |
| RGBT-12 | **OPTIONAL HOLD:** propagated calibration uncertainty risk bounds | [G08](publications/P08/protocol/README.md): real geometric/clock uncertainty + coverage + non-overlap PASS | P08 |

## Priorities and dependencies

1. RGBT-01/02 data rights, versioned protocol and labels precede external-dataset performance claims. Documentation-only planning P04–P06 can proceed without empirical claims.
2. RGBT-03 underpins P02 and any later P08. RGBT-04/05/08/09 require genuinely labelled, independent scenes. RGBT-10 requires real identity-labelled, correctly paired sequences; still imagery is inadequate.
3. RGBT-06 must precede P03 physical efficiency claims. **RGBT-11/P07 is blocked** until all G07 conditions pass and are reviewed.
4. **RGBT-12/P08 is blocked** until all G08 conditions pass and are reviewed. Synthetic E02 skew/overlap does not satisfy measured uncertainty or risk-bound coverage.
5. RGBT-07 enforces independent manuscript-level claims; integrate any overlapping or unsupported findings into parent articles instead of salami slicing.

## Evidence, costs and autonomy

Use no paid APIs. Do not auto-download datasets/weights, run untrusted PR code on persistent self-hosted runners, or infer physical effects from synthetic E00–E02 or host EdgeLab. Check dataset rights/privacy, annotate negative-frame completeness, isolate scenes/devices, record acquisition/calibration evidence, code SHA and measurement uncertainty. Human/physical studies or manuscript submission require their own authorization and scientific GO.

An OPTIONAL HOLD entry is a **blocked candidate**, not queued execution, and must not be automatically promoted based on a documentation change. Scope is [RESEARCH.md](RESEARCH.md); methods are in [publication protocols](publications/P07/protocol/README.md), [measurement rules](docs/guides/evaluation-requirements.md) and [evidence policy](docs/concepts/evidence.md).
