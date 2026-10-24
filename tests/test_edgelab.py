import numpy as np
import pytest

from arc_rgbt.edgelab import profile_cpu


def test_host_reference_not_mcu(tmp_path):
    model = tmp_path / "model.bin"
    model.write_bytes(b"binary-file")
    metrics = profile_cpu(np.ones((32, 32), np.float32), 3, model)
    assert metrics["model_file_bytes"] == len(b"binary-file")
    assert metrics["latency_median_ms"] >= 0
    assert metrics["device_class"] == "host_cpu"
    assert "not a device" in metrics["limitations"]
    with pytest.raises(ValueError):
        profile_cpu(np.ones((8, 8)), 0)
