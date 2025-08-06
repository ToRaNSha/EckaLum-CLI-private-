import importlib.util
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODULE_PATH = ROOT / "EckaLum_cli_v0.3.0-B12.py"
spec = importlib.util.spec_from_file_location("eckalum", MODULE_PATH)
eckalum = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eckalum)


def test_date_seed_base12():
    ts = datetime(2025, 1, 1)
    expected = int(ts.strftime("%Y%m%d"), 12)
    assert eckalum._date_seed(ts) == expected


def test_gate_map_length():
    assert len(eckalum.GATE_MAP) == 12
    assert set(eckalum.GATE_MAP.keys()) == set(range(12))


def test_sample_spectrum_deterministic():
    ts = datetime(2025, 5, 22)
    spec1 = eckalum.sample_spectrum(ts)
    spec2 = eckalum.sample_spectrum(ts)
    import numpy as np

    np.testing.assert_allclose(spec1, spec2)
    assert spec1.shape == (88,)
    assert min(spec1) >= 0 and max(spec1) <= 1


def test_dominant_gate_range():
    ts = datetime(2025, 3, 15)
    spec = eckalum.sample_spectrum(ts)
    gate = eckalum.dominant_gate(spec)
    assert gate in range(12)
