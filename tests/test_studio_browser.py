"""Opt-in headless-browser acceptance test for the packaged offline UI.

ARC_RGBT_BROWSER_TEST=1 python -m pytest -q tests/test_studio_browser.py
"""

import os
from pathlib import Path

import cv2
import numpy as np
import pytest


@pytest.mark.skipif(os.getenv("ARC_RGBT_BROWSER_TEST") != "1", reason="Opt-in local browser test")
def test_studio_browser_workflow(tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    from arc_rgbt import studio

    assert Path(studio.resources.files("arc_rgbt").joinpath("studio.html")).is_file()

    def save_color(name, width, height, bgr):
        path = tmp_path / name
        image = np.full((height, width, 3), bgr, dtype=np.uint8)
        success, encoded = cv2.imencode(".png", image)
        assert success
        path.write_bytes(encoded.tobytes())
        return str(path)

    red = save_color("rgb.png", 4, 3, (0, 0, 255))
    blue = save_color("thermal.png", 4, 3, (255, 0, 0))
    wrong = save_color("wrong.png", 2, 3, (255, 0, 0))
    with playwright.sync_playwright() as engine:
        browser_args = {"headless": True}
        if os.getenv("ARC_RGBT_CHROMIUM_EXECUTABLE"):
            browser_args["executable_path"] = os.environ["ARC_RGBT_CHROMIUM_EXECUTABLE"]
        browser = engine.chromium.launch(**browser_args)
        try:
            page = browser.new_page(accept_downloads=True)
            exceptions = []
            page.on("pageerror", lambda error: exceptions.append(str(error)))
            studio_html = Path(studio.resources.files("arc_rgbt").joinpath("studio.html"))
            # set_content avoids file:// restrictions imposed by locked-down browsers.
            page.set_content(studio_html.read_text(encoding="utf-8"))
            assert page.locator("#save").is_disabled()
            page.locator("#rgb").set_input_files(red)
            page.locator("#thermal").set_input_files(wrong)
            page.locator("#status.error").wait_for(timeout=3000)
            assert page.locator("#status.error").is_visible()
            assert "Dimension mismatch" in page.locator("#status").inner_text()
            assert page.locator("#save").is_disabled()
            page.locator("#thermal").set_input_files(blue)
            page.wait_for_function("() => !document.getElementById('save').disabled")
            assert page.locator("#save").is_enabled()

            def pixel():
                return page.evaluate("""() => Array.from(document.getElementById('fused')
                  .getContext('2d').getImageData(0, 0, 1, 1).data)""")

            assert pixel() == [36, 36, 36, 255]
            page.locator("#weight").fill("100")
            assert pixel() == [18, 18, 18, 255]
            page.locator("#mode").select_option("difference")
            assert pixel() == [36, 36, 36, 255]
            with page.expect_download() as result:
                page.locator("#metadata").click()
            assert result.value.suggested_filename == "arc-rgbt-fusion.json"
            with page.expect_download() as result:
                page.locator("#save").click()
            assert result.value.suggested_filename == "arc-rgbt-fusion.png"
            page.locator("#rgb").set_input_files({"name": "bad.txt", "mimeType": "text/plain",
                                                   "buffer": b"invalid"})
            assert page.locator("#save").is_disabled()
            assert "choose a nonempty" in page.locator("#status").inner_text()
            assert not exceptions, exceptions
        finally:
            browser.close()
