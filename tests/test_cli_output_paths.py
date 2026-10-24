import numpy as np
import pytest

from arc_rgbt import degradesim, fusionlab


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
