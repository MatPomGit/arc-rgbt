# P01 local end-to-end runner (Windows / Fedora)

The **validation-only** entrypoint is `publications/P01/analyses/run_local_pipeline.py`.
It reuses the existing multipart FLIR COCO reader, source-video split checks,
scratch Faster R-CNN / MobileNetV3 training, TorchScript inference, and
source-GT-relative COCO scoring. It does **not** open held-out test data or
authorise Tier B physical sensor claims. It does not create a new annotation
workstream.

## Windows: double-click P01.bat

From the repository root, launch `P01.bat`. It delegates to the shared
standard-library `research_console.py`, which works before creating a venv.
Its current numbered menu is:

1. Install/update Python dependencies: create `.venv` with Python 3.12,
   `pip install -e ".[torch]"` and confirm Torch imports. No system-wide pip.
2. Configure the local FLIR directory and optional *verified* download manifest.
   The setting survives restarts in `%LOCALAPPDATA%\\arc-rgbt\\settings.json`.
   When a verified manifest is available, download and hash-check missing
   original ZIP parts. The official portal may require registration/terms,
   so no direct archive URL is fabricated or access control bypassed.
3. Diagnose Torch, TorchVision, CUDA and existing archive filenames.
4. Choose an algorithm and device, acknowledge lawful research use, then
   perform training and validation. Each run gets its own immutable folder.
5. Publish an existing result summary to the GitHub results PR, without
   repeating training. Requires `gh auth login`; blocked while another
   PR is open. Never uploads raw data, predictions or weights.
6. Show recent runs, statuses, failing stages, and open their diagnostic folders.
7. Open the official FLIR source-access page in the browser.
8. Retry pending diagnostic uploads after GitHub access or PR restrictions clear.
0. Exit.

The experiment registry in `research_console.EXPERIMENTS` centralises the
addition of future algorithms. Each profile identifies the experiment
entrypoint and dataset ID; installation, execution history, diagnostic logs
and result-publication controls remain shared. A new dataset gets its own
persisted location under `dataset_dirs`. Profiles must point to trusted
repository code, not user-supplied arbitrary commands.

### Automatic diagnostics synchronization

After **every completed or failed menu operation**, the console attempts to
record a small structured diagnostic JSON in the GitHub `p01-validation-results`
branch and associated reviewable PR. Each JSON contains UTC timestamps with
millisecond precision, elapsed durations, stage identifiers, sampled training
progress/ETA, process exit codes and the SHA-256 and byte length of the local
console log. The telemetry is restricted to an explicit allowlist and capped
at **96 KiB per run**. It never includes full console text, tracebacks,
device data, local filesystem paths, secrets, weights, images or predictions.

The shared repository's **one active PR** rule still applies. While the
pipeline implementation PR is open, or when GitHub CLI is unavailable or
unauthenticated, diagnostic uploads are **deferred**, not silently discarded.
The local `sync_pending.txt` explains the reason. After the PR is merged,
use menu option 8 to retry. `sync_success.json` records completed uploads.
A failed run does not trigger a retraining attempt.

The console displays a 25-character percentage bar during **training
minibatches**, with ETA computed from actual batches processed. ETA is an
estimate for the remaining training batches, **not** a promise of when
validation inference or all artifact writing will finish. Other stages appear
by name in the console and logs; no fake progress percentage is assigned to
stages whose work units are unavailable.

The remote metadata is sufficient to locate the failed stage and establish
timing/provenance, but **not always to diagnose an exception's root cause**
without inspecting the complete local traceback. This is intentional because
the GitHub repository is public.

### Debugging and local directory structure

A typical local run creates:

```text
%USERPROFILE%\\ArcRGBT_runs\\logs\\20261123T120000Z_ab12cd34\\
    status.json              latest status, operation, error stage and return code
    events.jsonl             time-stamped transitions, one JSON per line
    console.log              full command stdout/stderr, including epoch progress
    artifacts\\
        pipeline_stage.json  most recent internal stage, including failures
        preflight\\          source/split manifests (local)
        training\\           checkpoint, predictions, provenance (local)
        validation_metrics.json
        summary.json         small, publication-eligible validation record
    result.json              SHA-256 and local summary location (on success)
```

Installations and dataset acquisitions also receive their own log folder.
A failed experiment is never recorded as a successful training result.
The console shows the last 15 run statuses and opens the selected directory
in Windows Explorer. Failed steps retain their outputs, with no silent retry.
No raw images, tokens, local paths, or weight files are committed to GitHub.

## Requirements


Python 3.12+, free disk space for the original 12 ZIP parts and the local
training outputs; compatible PyTorch/TorchVision and CUDA driver on Andromeda.
A CPU run is available but potentially slow. From the repository root:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[torch]"
```

On Fedora, use `python3 -m venv .venv` and
`.venv/bin/python -m pip install -e '.[torch]'`.
Install only from trusted package indexes; verify that
`python -c "import torch; print(torch.cuda.is_available())"` returns
`True` on Andromeda before choosing CUDA.

Place the **original** `FLIR_ADAS_v2.zip.00` through
`FLIR_ADAS_v2.zip.11` in a local directory outside the checkout.
Before running, confirm source terms and permitted research use. The project
still records source rights and native optics as unverified.

### Run on Windows

```powershell
.venv\Scripts\python.exe publications/P01/analyses/run_local_pipeline.py --parts-dir "D:\FLIR_ADAS_v2" --work-dir "D:\P01_runs\run_001" --rights-acknowledged --device cuda --publish
```

### Run on Fedora

```bash
.venv/bin/python publications/P01/analyses/run_local_pipeline.py --parts-dir "$HOME/data/FLIR_ADAS_v2" --work-dir "$HOME/p01_runs/run_001" --rights-acknowledged --device cuda --publish
```

Each work directory must be new and outside Git. No `--publish` means local
results only. To enable publishing, install and authenticate the GitHub CLI
(`gh auth login`) with permission to write to this repository and open PRs.
Publication creates/updates the single `p01-validation-results` branch and
opens a PR if needed. It never automatically merges, uploads images, uploads
weights or grants scientific GO. Only a bounded, sanitised `summary.json`
is put into `publications/P01/results/runs/`; the full GT, predictions,
checkpoint, loss traces and run artifacts remain local.

### Optional first-time source acquisition

No dataset URL is hardcoded or guessed. If the original parts are absent,
supply `--download-manifest PATH` containing exactly 12 mappings,
`FLIR_ADAS_v2.zip.00` ... `FLIR_ADAS_v2.zip.11`, each with an
independently verified original-source HTTPS `url` and lowercase
64-hex `sha256`. Example entry:

```json
{
  "FLIR_ADAS_v2.zip.00": {
    "url": "https://verified-source.example/part-00",
    "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  }
}
```

The example is **not** a functioning download URL or authenticated checksum.
Do not treat it as evidence of FLIR release identity or rights. The runner
requires all 12 entries, checks HTTPS host and byte hashes and refuses
unverified/partial inputs. If a part fails, it stops without training.
Avoid checking manifest URLs with authentication tokens into Git.

### Evidence and limitations

Local files: `preflight/source_manifest.json`,
`preflight/p01_group_manifest.json`, `training/training_provenance.json`,
`training/validation_predictions/predictions.json`,
`training/validation_candidate.json`, `validation_metrics.json`,
`summary.json` and the local `.pt` checkpoint.

Metrics are **validation candidate only**, against provided source labels.
Apparent FP/frame can include unannotated objects. Neither video IDs nor
export-grid boxes demonstrate independent acquisitions, native optics or
physical sensor detection limits. Train and validation are checked for
source-video proxy leakage by existing code. Holdout/test is never opened.
Threshold changes must not be selected based on test data. A frozen
protocol and author approval are separately required for a confirmatory
held-out experiment. The run is not complete until real local data and GPU
(or CPU) execute the code successfully.

If GitHub publication fails due to missing credentials or another open PR,
local evidence is retained. Retry from BAT menu option 4, or run
`python publications/P01/analyses/run_local_pipeline.py --publish-summary PATH`
with a previously completed `summary.json`, without retraining.
The publisher checks the validation-only evidence schema and rejects unexpected
summary fields. Only a small SHA-addressed result JSON is committed, using a PR.
 No external emails, expenses, or
publisher submission occur.
