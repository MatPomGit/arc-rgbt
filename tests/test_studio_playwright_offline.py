"""Opt-in, real-file Playwright acceptance tests for the offline Studio.

Run on an isolated machine with Chromium and playwright already installed.
These tests deliberately navigate file://, rather than simulating HTML with
page.set_content, so packaging, CSP, local uploads and downloads are covered.
"""

import json
import os
import re
from pathlib import Path

import cv2
import numpy as np
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("ARC_RGBT_BROWSER_TEST") != "1",
    reason="Real Chromium acceptance is opt-in (ARC_RGBT_BROWSER_TEST=1)",
)


@pytest.fixture
def offline_page():
    # A missing Python Playwright module is an error during opt-in validation,
    # not a successful test run with all browser checks silently skipped.
    from playwright.sync_api import sync_playwright

    from arc_rgbt import studio

    html = Path(studio.resources.files("arc_rgbt").joinpath("studio.html")).resolve()
    assert html.is_file(), "The packaged offline Studio file is missing"
    outbound = []
    javascript_errors = []
    with sync_playwright() as playwright:
        args = {"headless": True}
        if os.getenv("ARC_RGBT_CHROMIUM_EXECUTABLE"):
            args["executable_path"] = os.environ["ARC_RGBT_CHROMIUM_EXECUTABLE"]
        browser = playwright.chromium.launch(**args)
        try:
            context = browser.new_context(accept_downloads=True)

            def deny_http(route):
                outbound.append(route.request.url)
                route.abort()

            context.route(re.compile(r"^https?://"), deny_http)
            page = context.new_page()
            page.on("pageerror", lambda error: javascript_errors.append(str(error)))
            response = page.goto(html.as_uri(), wait_until="load")
            assert response is not None and response.ok
            assert page.url.startswith("file://")
            yield page, outbound, javascript_errors
            assert not outbound, f"Studio attempted an HTTP request: {outbound}"
            assert not javascript_errors, javascript_errors
        finally:
            browser.close()


def save_npy(path, data):
    np.save(path, data, allow_pickle=False)
    return str(path)


def save_download(download, path):
    download.save_as(str(path))
    return path


def pixel(page, x=0, y=0):
    return page.evaluate(
        """([x,y]) => Array.from(document.getElementById('fused')
        .getContext('2d').getImageData(x,y,1,1).data)""",
        [x, y],
    )


def test_file_uri_starts_offline_and_exports_synthetic_png(offline_page, tmp_path):
    page, _, _ = offline_page
    assert page.title() == "RGB–Thermal Studio | arc-rgbt"
    assert page.locator("#save").is_disabled()
    page.get_by_role("button", name="Try an example").click()
    page.wait_for_function("() => !document.getElementById('save').disabled")
    assert "Synthetic example loaded" in page.locator("#status").inner_text()
    assert pixel(page, 60, 40) == [203, 203, 203, 255]

    with page.expect_download() as result:
        page.locator("#metadata").click()
    downloaded = save_download(result.value, tmp_path / "sample-metadata.json")
    metadata = json.loads(downloaded.read_text(encoding="utf-8"))
    assert result.value.suggested_filename == "arc-rgbt-fusion.json"
    assert metadata["data_origin"] == "simulated"
    assert metadata["spatial_registration"] == "external_unverified"
    assert metadata["radiometric_calibration"] is False
    assert metadata["input_grid_px"] == [160, 120]

    with page.expect_download() as result:
        page.locator("#save").click()
    png = save_download(result.value, tmp_path / "sample-fusion.png")
    raw = np.frombuffer(png.read_bytes(), dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    assert result.value.suggested_filename == "arc-rgbt-fusion.png"
    assert image is not None and image.shape[:2] == (120, 160)
    assert int(image[40, 60, 0]) == 203

    page.get_by_role("button", name="Clear images").click()
    assert page.locator("#save").is_disabled()
    assert page.locator("#weight").is_disabled()
    assert page.locator("#rgbPreview").get_attribute("src") is None


def test_native_npy_pair_and_scientific_metadata(offline_page, tmp_path):
    page, _, _ = offline_page
    rgb = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    thermal = np.array([[65535, 0], [0, 65535]], dtype=np.uint16)
    rgb_path = save_npy(tmp_path / "rgb.npy", rgb)
    thermal_path = save_npy(tmp_path / "thermal.npy", thermal)
    page.locator("#rgb").set_input_files(rgb_path)
    page.locator("#thermal").set_input_files(thermal_path)
    page.wait_for_function("() => !document.getElementById('save').disabled")
    status = page.locator("#status").inner_text()
    assert "Matching dimensions" in status
    assert "spatial alignment unverified" in status
    assert pixel(page, 0, 0) == [128, 128, 128, 255]
    page.locator("#weight").fill("100")
    assert pixel(page, 0, 0) == [255, 255, 255, 255]
    page.locator("#mode").select_option("difference")
    assert pixel(page, 0, 0) == [255, 255, 255, 255]

    with page.expect_download() as result:
        page.locator("#metadata").click()
    meta = json.loads(
        save_download(result.value, tmp_path / "native.json").read_text(encoding="utf-8")
    )
    assert meta["data_origin"] == "user_supplied"
    assert meta["thermal"]["raw_dtype"] == "<u2"
    assert meta["thermal"]["raw_min"] == 0
    assert meta["thermal"]["raw_max"] == 65535
    assert meta["thermal"]["normalization"] == "per_frame_min_max"
    assert meta["method"] == "difference"


def test_corrupted_and_unsupported_npy_fail_closed(offline_page, tmp_path):
    page, _, _ = offline_page
    good = save_npy(tmp_path / "good.npy", np.ones((3, 4), dtype=np.uint16))
    page.locator("#rgb").set_input_files(good)
    page.locator("#thermal").set_input_files(good)
    page.wait_for_function("() => !document.getElementById('save').disabled")

    invalid = tmp_path / "corrupt.npy"
    invalid.write_bytes(b"NOT AN NPY FILE")
    nonfinite = save_npy(tmp_path / "nan.npy", np.full((3, 4), np.nan))
    fortran = save_npy(
        tmp_path / "fortran.npy", np.asfortranarray(np.arange(12).reshape(3, 4))
    )
    wrong = save_npy(tmp_path / "wrong.npy", np.zeros((2, 4), dtype=np.uint8))
    cases = [
        (str(invalid), "Invalid NumPy"),
        (nonfinite, "non-finite"),
        (fortran, "C-order"),
        (wrong, "Dimension mismatch"),
    ]
    for filename, diagnostic in cases:
        page.locator("#thermal").set_input_files(filename)
        page.locator("#status.error").wait_for()
        assert diagnostic in page.locator("#status").inner_text()
        assert page.locator("#save").is_disabled()
        assert page.locator("#metadata").is_disabled()
        page.locator("#thermal").set_input_files(good)
        page.wait_for_function("() => !document.getElementById('save').disabled")


def test_stale_async_upload_cannot_replace_newer_thermal_frame(offline_page, tmp_path):
    page, _, _ = offline_page
    rgb = save_npy(tmp_path / "rgb.npy", np.zeros((2, 2), dtype=np.uint8))
    slow = save_npy(tmp_path / "slow.npy", np.zeros((2, 2), dtype=np.uint16))
    fast = save_npy(tmp_path / "fast.npy", np.ones((2, 2), dtype=np.uint16))
    page.locator("#rgb").set_input_files(rgb)
    page.evaluate(
        """() => {
            const original = File.prototype.arrayBuffer;
            File.prototype.arrayBuffer = function() {
                if (this.name !== 'slow.npy') return original.call(this);
                const captured = this;
                return new Promise(resolve => {
                    window.releaseBlockedUpload = () => original.call(captured).then(resolve);
                });
            };
        }"""
    )
    page.locator("#thermal").set_input_files(slow)
    page.wait_for_function("() => typeof window.releaseBlockedUpload === 'function'")
    page.locator("#thermal").set_input_files(fast)
    page.wait_for_function(
        "() => !document.getElementById('save').disabled && "
        "document.getElementById('thermalinfo').textContent.includes('fast.npy')"
    )
    page.evaluate("() => window.releaseBlockedUpload()")
    assert "fast.npy" in page.locator("#thermalinfo").inner_text()
    assert "slow.npy" not in page.locator("#thermalinfo").inner_text()
    assert page.locator("#save").is_enabled()
