# Agent operating contract

## Scope and safety
- Vendor-independent open research code only. Do not mention or infer any industrial partner, product, contact or confidential project.
- No paid APIs. Do not download datasets or models.
- Never commit reports, weights, secrets, user data or local paths.
- Implement functionality, not empty directories or stubs.
- Tie every benchmark claim to labelled evidence with explicit provenance.
- Keep it simple (KISS): no speculative abstractions, no duplicate implementations, docs or configs. Prefer editing existing files over creating new ones.
- Small commits. Report concrete failures; do not hide or soften them.

## Pipeline
- Follow the [shared delivery pipeline](https://github.com/MatPomGit/research-autopilot/blob/41ddb950a363df2ef78850ac9766c130880b2fd9/docs/architecture/DELIVERY_PIPELINE.md). Research Autopilot is the sole controller.
- Act autonomously within existing user authorization. Do not ask again for authorization already given.


### Mandatory current plan (every agent, every run)
- **Always read the latest [AUTOPILOT_PLAN.md](AUTOPILOT_PLAN.md), including its dated `Mandatory agent execution plan`, BEFORE selecting, reserving, implementing, reviewing or merging any work.** Also read `PROJECT_STATE.yaml`, the [M0-M6 issue tracker #21](https://github.com/MatPomGit/arc-rgbt/issues/21), the active issue, open PRs and the applicable scientific protocol. Record the plan version/SHA in the run evidence. Re-read after plan changes; never rely on an old cached summary.
- Follow the plan's ordered priorities, prerequisites, deadlines and STOP/GO criteria. Current P01 sequence is [#45-#62](https://github.com/MatPomGit/arc-rgbt/issues/21) under #35-#40; an outdated priority sentence elsewhere does not override the current dated plan. Research gates and independent review remain mandatory, including FROZEN/CONDITIONAL/NO-GO distinctions.
- Use [GitHub Actions cost policy](AUTOPILOT_PLAN.md#github-actions-free-use-and-billing-policy-verified-2026-11-02): public standard GitHub-hosted runner minutes are free without a monthly cap, but larger runners/storage/paid integrations are not automatically free. Preserve existing self-hosted trust and isolation constraints.
- **Zero-cost clarification:** standard GitHub-hosted GitHub Actions in this public repository are approved under `zero-cost`, including repeat CI checks and reruns needed for quality; do not refuse necessary free validation to save minutes. Owner declares GitHub Education educator benefits. Those benefits do not automatically make paid large runners, private-repository overages, artifacts/storage overages or paid APIs free. Check actual eligibility before use. Keep all existing security, trusted-runner and payment rules unchanged.
- For P01 *Sensors*, university APC funding is a **planning assumption**, not payment or separate authorization to commit funds or submit. See the current plan. Do not change any security rule, payment permission, scientific gate or deployment requirement on this basis.

## P01 execution: automation-first authority (author decision 2026-11-07)

Read the latest [AUTOPILOT_PLAN.md](AUTOPILOT_PLAN.md) v1.4.0 or later and [P01 protocol](publications/P01/protocol/README.md) on every run. This author directive overrides old P01 instructions that require human QA on supplied reference labels.

- Agent performs data integration, scientific code, experiments, analysis, plots and manuscript wherever tools and lawful data access permit; reuse existing common data contracts and code.
- No added two-reviewer label checks, blind review forms/galleries, manual image-classification campaigns, label reconciliation or standalone dataset/database QA unless author explicitly approves that distinct study.
- A normal local-only dataset handoff is one short reproducible Fedora command with local files/GPU and small hash-backed results, not repeated owner labour or raw-data upload. Never claim an experiment happened when the command was not executed.
- Dataset-label-relative recall/FP/frame is permissible with clear annotation limitations. Claims about physical native sensor limits require distinct provenance/optics/independent-acquisition evidence. Do not claim unsupported G01 PASS or scientific GO.
- Independent code/numerical/manuscript review and author protocol/submission decisions remain; they are not surrogate label review.
- Security, licensing, no held-out tuning, zero-spend, one active PR and no automatic publication remain unchanged.

## Submission-first editorial rule (author directive, 2026-11-07)

- Follow the canonical [research submission policy](RESEARCH.md#submission-first-publication-policy-author-directive-2026-11-07): a scientifically defensible, completed manuscript should move promptly to author-approved submission instead of indefinite polishing merely out of fear of rejection. A realistic journal with even modest eligible points (e.g. 20) is preferable to never submitting; rejection can be followed by revision and resubmission.
- Prepare journal-fit alternatives, manuscript, checklists and an explicit submit/revise decision for the author. Never bypass evidence/ethics/novelty gates, claim guaranteed points, send a submission, contact a publisher or authorize costs without the author's explicit approval.

## Finish before starting

- Read the active [research issue and milestone tracker M0–M6](https://github.com/MatPomGit/arc-rgbt/issues/21) **after** `PROJECT_STATE.yaml` and `AUTOPILOT_PLAN.md`. Follow dependency and evidence gates in the linked issue before selecting a task. Use the existing issue (and PR, if any) rather than opening a duplicate.
- Check M0 rights/data prerequisites before any empirical study. M6 P07/P08 tasks are OPTIONAL HOLD: issue checkboxes or dates do not authorize promotion, physical experiments or submission.
- Before any feature, read the full current PR inventory and existing task ownership.
- Finish the repository's existing PR first; reuse its branch for repairs.
- Limits: one active PR per repository, five across the managed portfolio. Drafts, testing, review and repair all count as active. A blocked PR does not free a slot.
- Priority order:
  1. Security and dependency blockers
  2. Repairs
  3. Validation and review
  4. Authorized merge and branch cleanup
  5. New features
- No separate report-only PR per validation run.

## Validation
- Use reusable validators from a trusted controller revision.
- One bounded batch per host, isolated execution, exact source SHAs, separate result per check.
- Statuses: PASS, FAIL, BLOCKED, UNAVAILABLE, NOT_RUN. Only PASS is a pass.
- Syntax checks do not establish scientific validity or teaching-material correctness.

## Merge and cleanup
- Merge when all applicable checks, reviews and current GitHub rules pass, within existing authorization.
- Delete a branch only if it is confirmed merged and owned, its current SHA is verified, and no dependent PR needs it.
- Merge does not authorize deployment or publication.

## Blocked work
- Record: reason, required exit condition, next safe action.
- Continue unrelated authorized repairs. Do not start another feature in the blocked repository.

## Reporting
- Report: completed merges, remaining PR age, blockers, and what was actually verified (and what was not).
- PR creation count is not a progress metric.

## Documentation ownership
- Keep `README.md` as entry/navigation; `docs/` owns technical methods and CLI contracts.
- Keep publication-specific preregistration rules only under `publications/P*/protocol/`; `AUTOPILOT_PLAN.md` owns work packages and `PROJECT_STATE.yaml` machine status.
- Treat P01–P06 as planned, not empirically established. P07 and P08 are optional HOLD: never activate them until G07/G08 independently pass and PROJECT_STATE.yaml is changed after review.
- Avoid salami slicing: require a distinct primary outcome, adequate independent evidence and novelty review before a new paper is treated as submission-ready.
- Link to canonical material rather than repeating methods, flags, formulas or scientific claims.
- Keep editable Markdown, not generated HTML/build assets. Each MkDocs page must be in `mkdocs.yml` and pass the documentation checks.

## Dodatkowy kontrakt operacyjny (2026-10-31)
- Przed każdym zadaniem stosuj powyższy kontrakt, aktualny plan projektu i wymagane bramki naukowe. Nie publikuj wewnętrznych procedur agentów, orkiestracji ani harmonogramów w MkDocs/GitHub Pages.
- Weryfikuj exact SHA, pochodzenie danych, wymagane zatwierdzenia GitHub i różnicę między merge, badaniem a wdrożeniem.
