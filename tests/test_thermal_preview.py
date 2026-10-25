import json

import numpy as np
import pytest

from arc_rgbt.thermal_preview import main, preview, run


def test_uint16_preserves_input_and_produces_known_intensities():
    raw = np.array([[0, 1000], [2000, 4000]], dtype=np.uint16)
    before = raw.copy()
    view, meta = preview(raw, display_range=(0, 4000))
    assert view.dtype == np.uint8
    assert view.tolist() == [[0, 64], [128, 255]]
    assert np.array_equal(raw, before)
    assert meta["raw_dtype"] == "<u2"
    assert meta["raw_max"] == 4000
    assert meta["physical_units"] == "unknown"


def test_float_constant_has_explicit_display_status():
    view, meta = preview(np.full((3, 3), 301.5, dtype=np.float32))
    assert np.all(view == 127)
    assert meta["display_constant"]


@pytest.mark.parametrize("bad", [
    np.array([], dtype=np.float32),
    np.array([1, 2], dtype=np.uint16),
    np.array([[complex(2, 3)]]),
    np.array([[np.nan]]),
    np.array([[np.inf]]),
    np.array([[True]]),
    np.array([[2**60]], dtype=np.uint64),
    np.empty((0, 3)),
])
def test_invalid_source_rejected(bad):
    with pytest.raises(ValueError):
        preview(bad)


@pytest.mark.parametrize("bounds", [(0, 0), (1, -1), (float("nan"), 2),
                                     (0, float("inf")), (True, 2)])
def test_invalid_display_range_rejected(bounds):
    with pytest.raises(ValueError, match="display_range"):
        preview(np.ones((2, 2)), display_range=bounds)


def test_bounded_staged_export_and_provenance(tmp_path):
    raw = np.arange(80, dtype=np.uint16).reshape(8, 10)
    path = tmp_path / "thermal.npy"
    np.save(path, raw, allow_pickle=False)
    target = tmp_path / "report"
    meta = run(path, target, percentiles=(5, 95))
    assert (target / "preview.png").is_file()
    assert (target / "metadata.json").is_file()
    recorded = json.loads((target / "metadata.json").read_text())
    assert recorded == meta
    assert len(recorded["source_sha256"]) == 64
    assert recorded["source_name"] == "thermal.npy"
    with pytest.raises(FileExistsError):
        run(path, target)
    assert np.array_equal(np.load(path, allow_pickle=False), raw)


def test_invalid_file_does_not_publish_directory(tmp_path):
    source = tmp_path / "bad.npy"
    source.write_bytes(b"bad data")
    with pytest.raises(ValueError):
        run(source, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_float64_extreme_range_no_overflow_or_silent_black_frame():
    raw = np.array([[-1e308, 0.0, 1e308]], dtype=np.float64)
    with np.errstate(all="raise"):
        image, meta = preview(raw, display_range=(-1e308, 1e308))
    assert image.tolist() == [[0, 128, 255]]
    assert meta["raw_max"] == 1e308


def test_cli_help_and_conflicting_controls(capsys, tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "--percentiles" in capsys.readouterr().out
    with pytest.raises(SystemExit) as exc:
        main(["--input", "missing.npy", "--range", "1", "2",
              "--percentiles", "3", "98"])
    assert exc.value.code == 2

def test_default_percentiles_handle_extreme_finite_float64():
    raw = np.array([[-1e308, 0.0, 1e308]], dtype=np.float64)
    with np.errstate(all="raise"):
        view, meta = preview(raw)
    assert meta["display_low"] < 0 < meta["display_high"]
    assert np.isfinite([meta["display_low"], meta["display_high"]]).all()
    assert view.tolist() == [[0, 128, 255]]
