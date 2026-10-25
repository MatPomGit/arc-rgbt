# Playwright acceptance for offline RGB–Thermal Studio

The primary browser E2E suite is implemented with **Python Playwright and real Chromium**.
The existing `tests/test_studio_browser.py` uses DOM injection for fast interaction tests.
The additional `tests/test_studio_playwright_offline.py` exercises the **packaged
`studio.html` through its actual `file://` URL**.

## Covered behaviour

- Opening the packaged offline page with Chromium; initial disabled controls.
- Built-in synthetic example, known visualization pixels, PNG and JSON exports.
- Native little-endian `.npy` uint8/uint16 ingestion, provenance and explicit
  warning that matching dimensions do not establish spatial registration.
- Failure-safe behaviour on corrupt, non-finite, Fortran-order and
  mismatched-dimension input without leaving exports enabled.
- A forced asynchronous file-read race: the previously requested slow file
  must not replace the later successful selection.
- Browser `pageerror` collection and an explicit HTTP(S)-request firewall:
  any attempted external request is blocked and fails the test.

These acceptance tests are **opt-in** and run only when
`ARC_RGBT_BROWSER_TEST=1`. A missing Playwright Python module or Chromium
browser is a test failure during opt-in execution; it must not count as PASS.

## Andromeda, isolated offline verification

Use a **clean, disposable worktree** or ephemeral Windows/VM test environment
without access to production secrets. Do not use permanent Research Autopilot
runners or GitHub-hosted Actions for this validation.

From a clone of `MatPomGit/arc-rgbt` in Windows PowerShell:

```powershell
git fetch origin refs/pull/8/head
$sha = (git rev-parse FETCH_HEAD).Trim()
git worktree add --detach "$env:TEMP\\arc-rgbt-pr8-browser" $sha
Set-Location "$env:TEMP\\arc-rgbt-pr8-browser"

# Use a previously installed Chromium or Chrome binary. Example location:
$chrome = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
& .\\tools\\run-playwright-offline.ps1 -ExpectedSha $sha -ChromiumExecutable $chrome
```

The runner fails closed if the current SHA is wrong, tracked files were edited,
Python dependencies are missing, browser navigation fails, or any check fails.
It never invokes `pip install`, `playwright install`, GitHub Actions or downloads.
The `[browser]` dependency extra in `pyproject.toml` is only a declaration:
preprovision the package and Chromium from your approved **offline** wheelhouse
or preinstalled tools before executing the runner.

The script runs `ruff check src tests tools`, the full standard `pytest -q`
suite with browser tests disabled, and finally both Playwright modules with
`ARC_RGBT_BROWSER_TEST=1`.

If the selected Chromium policy blocks `file://` navigation with
`ERR_BLOCKED_BY_ADMINISTRATOR`, report an **environment BLOCKED** result.
Do not bypass browser policy, silently mark the test as passing, or treat
`page.set_content` tests as proof of real-file behaviour.

## Minimal cross-platform manual invocation

On a properly isolated host with existing Python dependencies:

```bash
export PYTHONPATH=src
export ARC_RGBT_BROWSER_TEST=1
export ARC_RGBT_CHROMIUM_EXECUTABLE=/usr/bin/chromium
python -m pytest -q tests/test_studio_playwright_offline.py tests/test_studio_browser.py
```

No device, model, sensor data, paid service or network connection is required.
The tests verify an exploratory grayscale UI, **not** radiometry, image registration,
object detection accuracy or acquisition hardware.
