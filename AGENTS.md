# Agent operating contract

Scope: vendor-independent open research code only. Do not mention or infer any industrial partner, products, contacts or confidential projects. Avoid paid APIs. Do not download datasets/models or commit reports, weights, secrets, user data or local paths. Implement functionality rather than directories alone. Keep all benchmark claims tied to labelled evidence and explicit provenance. Use small commits, report concrete failures

## Complete delivery before starting new work

Follow the [shared delivery pipeline](https://github.com/MatPomGit/research-autopilot/blob/41ddb950a363df2ef78850ac9766c130880b2fd9/docs/architecture/DELIVERY_PIPELINE.md). Research Autopilot remains the sole controller.

Before starting a feature, read the complete current PR inventory and existing task ownership. Finish the repository's existing PR first. Reuse its branch for repairs.

Limit autonomous feature work to one active PR per repository and five across the managed portfolio. Count drafts, testing, review and repair as active work. A blocked PR does not free a feature slot.

Prioritize repairs, validation, review, authorized merge and branch cleanup before new features. Handle security and dependency blockers first. Do not create a separate report-only PR for each validation run.

Use reusable validators from a trusted controller revision. Run one bounded batch per host, with isolated execution, exact source SHAs and separate check results. Record FAIL, BLOCKED, UNAVAILABLE and NOT_RUN without treating them as PASS. Syntax checks do not establish scientific validity or teaching-material correctness.

After the applicable checks, reviews and current GitHub rules pass, merge within existing user authorization. Do not request the same authorization again. Delete only a confirmed merged, owned branch after verifying its current SHA and that no dependent PR needs it. Merge does not authorize deployment or publication.

For blocked work, record the reason, required exit condition and next safe action. Continue unrelated authorized repairs without starting another feature in the blocked repository. Report completed merges, remaining PR age and blockers; do not use PR creation count as the progress metric.
