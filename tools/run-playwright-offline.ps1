# Runs all validation offline in an existing, isolated checkout.
# No pip install, no browser download, no GitHub Actions dispatch.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-f]{40}$')]
    [string]$ExpectedSha,
    [string]$ChromiumExecutable = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$head = (& git -C $root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'BLOCKED: cannot resolve local HEAD' }
if ($head -cne $ExpectedSha) {
    throw "BLOCKED: local HEAD $head does not match required SHA $ExpectedSha"
}
$changes = & git -C $root status --porcelain --untracked-files=no
if ($LASTEXITCODE -ne 0) { throw 'BLOCKED: cannot inspect tracked worktree state' }
if ($changes) { throw 'BLOCKED: tracked files are modified; use a disposable clean worktree' }

$python = (Get-Command python -ErrorAction Stop).Source
if ($ChromiumExecutable) {
    if (-not (Test-Path -LiteralPath $ChromiumExecutable -PathType Leaf)) {
        throw "BLOCKED: Chromium executable not found: $ChromiumExecutable"
    }
}

$oldBrowser = $env:ARC_RGBT_BROWSER_TEST
$oldExecutable = $env:ARC_RGBT_CHROMIUM_EXECUTABLE
$oldPythonPath = $env:PYTHONPATH
$oldBytecode = $env:PYTHONDONTWRITEBYTECODE
Push-Location -LiteralPath $root
try {
    if ($ChromiumExecutable) {
        $env:ARC_RGBT_CHROMIUM_EXECUTABLE = $ChromiumExecutable
    }
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $env:PYTHONPATH = Join-Path $root 'src'
    if ($oldPythonPath) { $env:PYTHONPATH += ";$oldPythonPath" }
    Set-Location -LiteralPath $root

    # Import errors must fail the validation, never convert to silent pytest skips.
    & $python -c "import cv2, numpy, pytest, ruff, playwright.sync_api"
    if ($LASTEXITCODE -ne 0) { throw 'BLOCKED: required offline dependencies are missing' }

    Write-Host "Ruff | exact SHA $head"
    & $python -m ruff check src tests tools
    if ($LASTEXITCODE -ne 0) { throw 'FAIL: Ruff' }

    Write-Host 'Unit/integration suite (browser disabled)'
    $env:ARC_RGBT_BROWSER_TEST = '0'
    & $python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'FAIL: full pytest suite' }

    Write-Host 'Playwright Chromium acceptance (real file:// page)'
    $env:ARC_RGBT_BROWSER_TEST = '1'
    & $python -m pytest -q tests/test_studio_browser.py tests/test_studio_playwright_offline.py
    if ($LASTEXITCODE -ne 0) { throw 'FAIL: real Chromium Playwright acceptance' }

    Write-Host "VALIDATION=PASS | SHA=$head | MODE=OFFLINE"
}
finally {
    $env:ARC_RGBT_BROWSER_TEST = $oldBrowser
    $env:ARC_RGBT_CHROMIUM_EXECUTABLE = $oldExecutable
    $env:PYTHONPATH = $oldPythonPath
    $env:PYTHONDONTWRITEBYTECODE = $oldBytecode
    Pop-Location
}
