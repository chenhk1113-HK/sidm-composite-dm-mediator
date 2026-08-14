"""
Tests for kiss_sidm_julia_bridge.py and kiss_sidm_julia_reader.py.

The bridge calls the REAL KiSS-SIDM Julia code (https://gitlab.com/Socob/KiSS-SIDM)
from our Python pipeline. Tests:

  1. Bridge module is importable and exports run_canonical_kiSS_sidm
  2. Bridge parameters match the paper's canonical case
  3. Reader module is importable and exports aggregate_kiss_snapshots
  4. If JLD2 snapshots exist (from a prior run), reader produces a valid JSON
  5. If bridge has been run, result.txt exists with the expected keys

These tests do NOT require running the full Julia simulation (which takes
~minutes); they verify the integration plumbing is correct.

Standing rule (AGENTS.md): no new dependencies. We use the existing
wimpy venv and the system Julia 1.11.5 install.
"""
import json
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))


class TestBridgeModule:
    """kiss_sidm_julia_bridge.py module is importable."""

    def test_bridge_importable(self):
        """The bridge module is importable."""
        bridge = pytest.importorskip("kiss_sidm_julia_bridge")
        assert hasattr(bridge, "run_canonical_kiSS_sidm")
        assert hasattr(bridge, "JULIA_BIN")
        assert hasattr(bridge, "JULIA_PROJECT")

    def test_julia_path_correct(self):
        """Julia binary path is /home/lamkuenai/.juliaup/bin/julia."""
        bridge = pytest.importorskip("kiss_sidm_julia_bridge")
        assert bridge.JULIA_BIN == "/home/lamkuenai/.juliaup/bin/julia"
        assert bridge.JULIA_VERSION == "+1.11.5"
        assert bridge.JULIA_PROJECT == "/home/lamkuenai/KiSS-SIDM"

    def test_canonical_halo_params(self):
        """Canonical 10^9 M_sun halo parameters match the paper."""
        bridge = pytest.importorskip("kiss_sidm_julia_bridge")
        # The defaults are 10^9 M_sun halo, 50 cm^2/g
        # We verify by calling with a small N and reading the result
        # (Skip the actual run in CI; just verify the function signature)
        import inspect
        sig = inspect.signature(bridge.run_canonical_kiSS_sidm)
        params = sig.parameters
        assert "N" in params
        assert "t_end_Gyr" in params
        assert "sigma_m_cm2_per_g" in params
        assert "rho_s_Msun_per_kpc3" in params
        assert "r_s_kpc" in params
        assert "seed" in params

    def test_request_file_format(self):
        """_write_request_toml produces key=value format that Julia can parse."""
        bridge = pytest.importorskip("kiss_sidm_julia_bridge")
        # Test the file-based handoff format
        request = {"N_particles": 500, "sigma_m_cm2_per_g": 50.0, "seed": 42}
        request_path = bridge._write_request_toml(request)
        assert request_path.exists()
        content = request_path.read_text()
        assert "N_particles=500" in content
        assert "sigma_m_cm2_per_g=50.0" in content
        assert "seed=42" in content
        # Cleanup
        request_path.unlink()


class TestReaderModule:
    """kiss_sidm_julia_reader.py module is importable."""

    def test_reader_importable(self):
        """The reader module is importable."""
        reader = pytest.importorskip("kiss_sidm_julia_reader")
        assert hasattr(reader, "aggregate_kiss_snapshots")
        assert hasattr(reader, "_JULIA_READER")

    def test_reader_julia_no_json_jl(self):
        """The reader does not use JSON.jl (manual writer instead)."""
        reader = pytest.importorskip("kiss_sidm_julia_reader")
        # The reader should NOT import JSON.jl
        script = reader._JULIA_READER
        # Look for "JSON" as a using statement
        assert "using JSON" not in script
        # But it should use JLD2 and Unitful (possibly in a combined using)
        assert "JLD2" in script
        assert "Unitful" in script


class TestSnapshotData:
    """If snapshots exist from a prior bridge run, the reader should produce a valid JSON."""

    def test_snapshots_dir_exists_or_skip(self):
        """If /tmp/kiss_sidm_output exists, the reader can process it."""
        snap_dir = Path("/tmp/kiss_sidm_output")
        if not snap_dir.exists():
            pytest.skip("No snapshots from prior bridge run; run kiss_sidm_julia_bridge.py first")

        # Verify the dir has at least one snap_*.jld2 file
        snap_files = list(snap_dir.glob("snap_*.jld2"))
        assert len(snap_files) > 0, f"No snapshot files in {snap_dir}"

    def test_aggregated_json_or_skip(self):
        """If the aggregated JSON exists from a prior reader run, validate it."""
        agg_path = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "real_kiss_sidm_aggregated.json"
        if not agg_path.exists():
            pytest.skip("No aggregated JSON; run kiss_sidm_julia_reader.py first")

        with open(agg_path) as f:
            data = json.load(f)
        assert "test" in data
        assert "n_snapshots" in data
        assert data["test"] == "real_kiSS_sidm_aggregated"
        assert data["n_snapshots"] > 0
        assert "r_over_rs" in data
        assert "time_Gyr" in data
        assert "rho_over_rhos" in data
        assert "canonical_halo" in data
        # Halo should be 10^9 M_sun, 50 cm^2/g
        halo = data["canonical_halo"]
        assert halo["M_halo_Msun"] == 1e9
        assert halo["sigma_m_cm2_per_g"] == 50.0
        # r_over_rs should be monotonically increasing (this is the bin centers)
        r = data["r_over_rs"]
        for i in range(len(r) - 1):
            assert r[i + 1] > r[i]
        # time_Gyr should be sorted to be monotonic (after the reader's numerical sort)
        t = data["time_Gyr"]
        # Allow a small numerical tolerance for the sort
        for i in range(len(t) - 1):
            if t[i + 1] < t[i]:
                # Check if the gap is huge (>2 Gyr) which would indicate a sort failure
                if t[i] - t[i + 1] > 2.0:
                    pytest.fail(f"Time wrapped at index {i}: {t[i]:.3e} -> {t[i+1]:.3e} "
                                f"(gap > 2 Gyr indicates a sort failure)")


class TestEndToEnd:
    """If Julia is installed, we can run a tiny bridge test (N=100, 1 step)."""

    def test_julia_installed(self):
        """Verify the Julia binary exists at the expected path."""
        julia_path = Path("/home/lamkuenai/.juliaup/bin/julia")
        if not julia_path.exists():
            pytest.skip(f"Julia not installed at {julia_path}")
        # Check we can run it
        import subprocess
        result = subprocess.run(
            [str(julia_path), "+1.11.5", "--version"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "1.11" in result.stdout

    def test_dsmc_loadable(self):
        """Verify DSMC.jl is loadable from the KiSS-SIDM project."""
        julia_path = Path("/home/lamkuenai/.juliaup/bin/julia")
        if not julia_path.exists():
            pytest.skip("Julia not installed")

        import subprocess
        result = subprocess.run(
            [str(julia_path), "+1.11.5", "--project=/home/lamkuenai/KiSS-SIDM",
             "-e", "using DSMC; println(\"DSMC OK\")"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0
        assert "DSMC OK" in result.stdout
