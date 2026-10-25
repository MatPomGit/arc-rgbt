import numpy as np
import pytest

from arc_rgbt import degradesim, fusionlab, registration


def test_degradesim_extensionless_output_has_correct_sidecar(tmp_path):
    source = tmp_path / "source.npy"
    np.save(source, np.full((8, 8), 0.4, dtype=np.float32), allow_pickle=False)
    config = tmp_path / "degradation.yaml"
    config.write_text("width_px: 4\nheight_px: 4\n", encoding="utf-8")
    output = tmp_path / "native"
    degradesim.main(["--config", str(config), "--input", str(source),
                     "--output", str(output)])
    assert (tmp_path / "native.npy").is_file()
    assert (tmp_path / "native.npy.json").is_file()
    assert not (tmp_path / "native.json").exists()


def test_fusionlab_extensionless_output_has_correct_sidecar(tmp_path):
    source = tmp_path / "input.npy"
    np.save(source, np.full((8, 8), 0.3, dtype=np.float32), allow_pickle=False)
    fusionlab.main(["--rgb", str(source), "--thermal", str(source),
                    "--output", str(tmp_path / "fusion")])
    assert (tmp_path / "fusion.npy").is_file()
    assert (tmp_path / "fusion.npy.json").is_file()
    assert not (tmp_path / "fusion.json").exists()


@pytest.mark.parametrize("module,arguments", [
    (degradesim, ["--config", "config", "--input", "input"]),
    (fusionlab, ["--rgb", "input", "--thermal", "input"]),
])
def test_invalid_output_suffix_rejected_before_io(module, arguments, tmp_path):
    with pytest.raises(SystemExit) as exc:
        module.main([*arguments, "--output", str(tmp_path / "wrong.txt")])
    assert exc.value.code == 2


def test_fusionlab_rejects_empty_pair():
    with pytest.raises(ValueError, match="nonempty"):
        fusionlab.fuse_images(np.empty((0, 5)), np.empty((0, 5)))


def test_translation_requires_spatial_information():
    flat = np.ones((32, 32), dtype=np.float32)
    with pytest.raises(ValueError, match="texture"):
        fusionlab.register_translation(flat, flat)

def test_registration_extensionless_output_has_correct_sidecar(tmp_path):
    import json

    rgb = tmp_path / "rgb.npy"
    thermal = tmp_path / "thermal.npy"
    matrix = tmp_path / "homography.json"
    np.save(rgb, np.ones((8, 8), dtype=np.float32), allow_pickle=False)
    np.save(thermal, np.ones((8, 8), dtype=np.float32), allow_pickle=False)
    matrix.write_text(json.dumps([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), encoding="utf-8")
    registration.main([
        "--rgb", str(rgb), "--thermal", str(thermal),
        "--homography", str(matrix), "--calibration-origin", "simulated",
        "--output", str(tmp_path / "registered"),
    ])
    assert (tmp_path / "registered.npz").is_file()
    assert (tmp_path / "registered.npz.json").is_file()
    assert not (tmp_path / "registered.json").exists()
    with np.load(tmp_path / "registered.npz", allow_pickle=False) as result:
        assert result["valid"].all()


def test_registration_rejects_explicit_invalid_output_extension(tmp_path):
    with pytest.raises(SystemExit) as exc:
        registration.main([
            "--rgb", "missing", "--thermal", "missing",
            "--homography", "missing", "--calibration-origin", "simulated",
            "--output", str(tmp_path / "wrong.txt"),
        ])
    assert exc.value.code == 2
