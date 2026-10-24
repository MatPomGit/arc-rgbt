import json

import numpy as np

from arc_rgbt import bench, degradesim, edgelab, fusionlab, sensorlab


def test_five_cli_examples(tmp_path, capsys):
    image = np.zeros((240, 320), np.float32)
    image[60:110, 80:120] = 0.9
    p = tmp_path / "input.npy"
    np.save(p, image)
    camera = tmp_path / "cam.yaml"
    camera.write_text("width_px: 80\nheight_px: 60\npixel_pitch_um: 17\nfocal_length_mm: 3.1\n")
    sensorlab.main(["--camera", str(camera), "--range-m", "10", "--object-width-m", "1",
                    "--object-height-m", "1", "--output", str(tmp_path / "sensor.json")])
    assert (tmp_path / "sensor.json").exists()
    scenario = tmp_path / "degrade.yaml"
    scenario.write_text("width_px: 80\nheight_px: 60\nnoise_sigma: 0.01\nseed: 3\n")
    degradesim.main(["--input", str(p), "--config", str(scenario),
                     "--output", str(tmp_path / "native.npy")])
    native = str(tmp_path / "native.npy")
    fusioncfg = tmp_path / "fusion.yaml"
    fusioncfg.write_text("method: gradient\nthermal_weight: 0.4\nregister: false\n")
    fusionlab.main(["--config", str(fusioncfg), "--rgb", native, "--thermal", native,
                    "--output", str(tmp_path / "fused.npy")])
    sample = {"data_origin": "simulated", "config": {"purpose": "CLI smoke test"},
              "frames": [{"id": "x", "ground_truth": [{"label": "object", "bbox": [1, 1, 3, 3]}],
                          "predictions": [{"label": "object", "bbox": [1, 1, 3, 3],
                                           "score": 0.9}]}]}
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps(sample))
    bench.main(["--dataset", str(dataset), "--output", str(tmp_path / "bench")])
    cpucfg = tmp_path / "cpu.yaml"
    cpucfg.write_text("class: host_cpu\nrepeats: 2\n")
    edgelab.main(["--input", native, "--config", str(cpucfg),
                  "--output", str(tmp_path / "edge.json")])
    assert (tmp_path / "edge.json").exists()
    assert (tmp_path / "bench" / "bench.html").exists()
    assert (tmp_path / "fused.npy").exists()
    assert capsys.readouterr().out
