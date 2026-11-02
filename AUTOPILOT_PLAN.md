# arc-rgbt research work plan

**Version 1.3.1 · updated 2026-11-02.** Six CORE planned studies P01–P06 and two OPTIONAL HOLD studies P07–P08. This file owns work packages, not a second copy of research methods: use [RESEARCH.md](RESEARCH.md), the individual protocols and machine-readable [PROJECT_STATE.yaml](PROJECT_STATE.yaml).

## Current execution queue and issue milestones

**Execution ownership:** [Issue #21, M0–M6](https://github.com/MatPomGit/arc-rgbt/issues/21) is the current checklist and dependency index; linked issues #10, #17–#19, #22–#29 specify atomic agent runs, acceptance evidence and blocked tasks. Use this tracker before selecting the next run. This Markdown file owns work-package definitions; `PROJECT_STATE.yaml` remains the machine-readable scientific gate authority. An issue marked complete must not automatically promote a dataset or optional publication.

**P01 current priority (2026-11-02):** see the mandatory dated execution queue below. Existing M3OT [#22](https://github.com/MatPomGit/arc-rgbt/issues/22) and common data contracts [#23](https://github.com/MatPomGit/arc-rgbt/issues/23) remain shared prerequisites, not permission to divert the active P01 stream. All tasks remain subject to the one-active-PR rule. Empirical M2–M4 work still depends on independently admitted actual data/hardware; P07/P08 remain M6 OPTIONAL HOLD.


## Mandatory agent execution plan: P01 Sensors (2026-11-02)

**READ ON EVERY RUN AND BEFORE ANY ISSUE/PR SELECTION:** [AGENTS.md](AGENTS.md), [PROJECT_STATE.yaml](PROJECT_STATE.yaml), **this entire current plan**, then [issue #21, the dated M0-M6 tracker](https://github.com/MatPomGit/arc-rgbt/issues/21), current open issues, current PRs and the applicable P01 protocol. Follow the **latest reviewed issue dependencies and STOP/GO gates**, not stale narrative or arbitrary next-issue numbers. This file owns the execution queue and cost assumptions; issues own small tasks; protocol owns methods; PROJECT_STATE owns actual scientific gate status. If they disagree, STOP and reconcile before research execution. Record which plan version and SHA were read in the run log/PR description. The read requirement applies again after any substantive plan change and on each new agent run.

**Owner-approved planning assumption:** the university will cover the APC for the P01 submission to *Sensors*. Treat this as a funding assumption, **not payment made or university administrative approval already issued**. Current editorial estimate is 2600 CHF before any adjustments (check actual price and billing requirements before submission). APC is **not a scientific blocker** and must not motivate lower-quality methodology or premature submission. Agents may not pay, enter financial commitments, send emails, contact editors or submit manuscripts without separate action authorization.

**Current scientific state:** #42 and #43 merged; [PR #44](https://github.com/MatPomGit/arc-rgbt/pull/44) is an open draft with a synthetic-only cluster confidence-interval coverage audit. P01 remains **UNFROZEN / G01 DATA BLOCKED**. Never convert CI PASS into dataset or scientific GO; no numerical physical detection limits have been measured.

### Next executable actions (top-down priority, bounded, revisit at each run)

| Order / due | Existing task | Concrete next action | Stop/exit evidence |
| --- | --- | --- | --- |
| 0 / immediately | [PR #44](https://github.com/MatPomGit/arc-rgbt/pull/44) | Read current PR head, reviewer findings and tests; complete independent methods review, address defects on its existing branch before opening any additional implementation PR | Review verdict on exact SHA; never merge as empirical GO |
| 1 / Nov 05 | [#45](https://github.com/MatPomGit/arc-rgbt/issues/45) + [#49](https://github.com/MatPomGit/arc-rgbt/issues/49) | Verify lawful original LWIR dataset/source candidates and independently reproduce synthetic CI undercoverage; use **parallel research tasks, not parallel feature PRs** | Rights/source shortlist; independently reviewed interval methods |
| 2 / Nov 07 | [#46](https://github.com/MatPomGit/arc-rgbt/issues/46) + [#50](https://github.com/MatPomGit/arc-rgbt/issues/50) | Verify original LWIR spectral/native-grid geometry, settle paired acquisition estimand, confounding, H0/H1 and test alpha | Signed-off *candidate* decision sheet and source geometry evidence |
| 3 / Nov 09-10 | [#47](https://github.com/MatPomGit/arc-rgbt/issues/47), [#51](https://github.com/MatPomGit/arc-rgbt/issues/51), [#48](https://github.com/MatPomGit/arc-rgbt/issues/48) | Complete GT/negative-frame convention, FP/frame/IoU/threshold rules, authentic independent group counts and sample-size feasibility using non-test material | Exclusion sheet, operating-point draft and source-informed precision gate |
| 4 / Nov 11-13 | [#52](https://github.com/MatPomGit/arc-rgbt/issues/52), [#53](https://github.com/MatPomGit/arc-rgbt/issues/53), parent [#35](https://github.com/MatPomGit/arc-rgbt/issues/35) | Verify *Sensors* fit and method novelty; prepare **unsent** ~250-word abstract; independent review + explicit author FROZEN / CONDITIONAL_DESIGN / NO-GO | Dated decision and protocol SHA; unresolved source conditions remain BLOCKED |
| 5 / Nov 20-Dec 11 | [#54](https://github.com/MatPomGit/arc-rgbt/issues/54) -> [#55](https://github.com/MatPomGit/arc-rgbt/issues/55) -> [#56](https://github.com/MatPomGit/arc-rgbt/issues/56) -> [#57](https://github.com/MatPomGit/arc-rgbt/issues/57), parent [#36](https://github.com/MatPomGit/arc-rgbt/issues/36) | Independently audit exact licensed original release, hashes, near-duplicates, source-disjoint split, complete GT and negative-frame support | Source-specific G01 admission PASS / RESTRICTED / BLOCKED by Dec 11 |
| 6 / Dec 18-Jan 15 | [#58](https://github.com/MatPomGit/arc-rgbt/issues/58) -> [#59](https://github.com/MatPomGit/arc-rgbt/issues/59) -> [#60](https://github.com/MatPomGit/arc-rgbt/issues/60), parent [#37](https://github.com/MatPomGit/arc-rgbt/issues/37) | Only after G01 PASS and **actual source-specific preregistration**, freeze model and validation threshold, evaluate one untouched held-out test, run frozen acquisition-group inference | Hash-backed real LWIR results with unmodified held-out threshold; negative findings included |
| 7 / Jan 29-Feb 26 | [#61](https://github.com/MatPomGit/arc-rgbt/issues/61), [#38](https://github.com/MatPomGit/arc-rgbt/issues/38), [#62](https://github.com/MatPomGit/arc-rgbt/issues/62), [#39](https://github.com/MatPomGit/arc-rgbt/issues/39) | Produce claim-linked figures/manuscript and independently reproduce all key evidence | Scientific GO/NO-GO, methods and originality reviewed |
| 8 / Mar 05-19; publisher Mar 31 | [#40](https://github.com/MatPomGit/arc-rgbt/issues/40) | Final unsent package, university billing paperwork confirmation, editorial instructions, explicit author submission decision | Publication approval distinct from CI and from university funding assumption |

**Critical path:** independently admissible original LWIR source and sufficient acquisition groups -> defensible CI/inference and author freeze -> source/split G01 -> validation-only threshold -> untouched held-out outcome -> independent reproduction -> author submission decision. If source evidence fails by Dec 11, report scientific NO-GO for native physical limits; consider legal new independent measurements (only with separate authorization) or explicitly narrower *descriptive/simulation* article with re-evaluated novelty/venue. Never fabricate physical data or reclassify simulation as sensor proof.

**Execution discipline:** complete and review current PR first; use the current issue rather than creating duplicates; one bounded JUMP at a time; independent review, exact-SHA validation, cleanup of merged branches, no speculative new branches. Concurrency may be increased for independent GitHub-hosted validation **jobs**, not automatically for Git branches/PRs or uncontrolled agent tasks. Maintain existing security policy and approvals in AGENTS.md.

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
