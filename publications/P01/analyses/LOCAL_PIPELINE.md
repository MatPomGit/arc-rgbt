# P01 local end-to-end runner (Windows / Fedora)

The **validation-only** entrypoint is `publications/P01/analyses/run_local_pipeline.py`.
It reuses the existing multipart FLIR COCO reader, source-video split checks,
scratch Faster R-CNN / MobileNetV3 training, TorchScript inference, and
source-GT-relative COCO scoring. It does **not** open held-out test data or
authorise Tier B physical sensor claims. It does not create a new annotation
workstream.

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

If `--publish` fails due to missing GitHub credentials, local evidence
is retained; rerun publication only after inspecting the failure, without
restarting a completed training run. No external emails, expenses, or
publisher submission occur.
