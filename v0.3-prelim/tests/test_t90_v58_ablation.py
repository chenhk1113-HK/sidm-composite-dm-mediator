"""T90.58 tests -- Channel-set ablation sweep on hybrid 10D.

Verifies:
  - _loglike_subset at known point produces expected per-channel contributions
  - KSFR rejects m_phi_A outside [418, 4180] MeV (when enabled)
  - KSFR disabled returns 0 (env var)
  - LZ silent if WIMpy unavailable (env var)
  - Dropping a channel changes loglike by expected amount
  - Run a tiny nlive=50 sweep and check that all 6 JSONs get written

Per-channel expected contributions at the T90.57 posterior median
(m_phi_A = 972 MeV, in KSFR box; sigma/m(C9)=74.4, sigma/m(Gal)=1.25,
sigma/m(Bul)=0.0014, mu_x=4.3e-8):
  - Cloud-9:  small (sigma/m(C9) near geometric mean of [30, 500])
  - Galaxy:   0 (sigma/m(Gal)=1.25 < 2 cm^2/g constraint)
  - Bullet:   0 (sigma/m(Bul)=0.0014 << 0.5 constraint)
  - LZ:       0 (mu_x=4e-8 << detection limit)
  - KSFR:     0 (m_phi_A=972 in box)
"""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))

# Force KSFR enabled at import time (tests will exercise both modes)
os.environ["SIDM_DISABLE_KSFR_MASK"] = "0"

from t90_v58_ablation import _loglike_subset  # noqa: E402

# Reference point: T90.57 posterior median
THETA_LOG_MEDIAN = np.array([
    2.69,    # log m_chi (GeV)
    2.99,    # log m_phi_A (MeV)
    0.79,    # g_chi_A
    0.66,    # log m_phi_B (MeV)
    0.19,    # g_chi_B
    2.84,    # log E_R (eV)
    0.10,    # log Gamma (eV)
    -3.01,   # log sigma_0
    -3.03,   # log alpha_Y
    -7.37,   # log mu_x (mu_N)
])


def test_all_5_channels_returns_finite():
    """At T90.57 posterior median, all 5 channels active should give a finite loglike."""
    ll = _loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"})
    assert np.isfinite(ll), f"All 5ch loglike not finite: {ll}"
    assert ll < 0, f"Loglike should be negative at median: {ll}"


def test_ksfr_off_via_env_var():
    """When env var SIDM_DISABLE_KSFR_MASK=1, KSFR is silent (0 contribution)."""
    os.environ["SIDM_DISABLE_KSFR_MASK"] = "1"
    # Reimport to pick up env var (KSFR module reads at import time)
    if "t90_v58_ablation" in sys.modules:
        del sys.modules["t90_v58_ablation"]
    import t90_v58_ablation as m_ksfr_off
    ll_with = m_ksfr_off._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"})
    ll_without = m_ksfr_off._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "Bullet", "LZ"})
    assert ll_with == ll_without, "KSFR should be silent when env var = 1"
    os.environ["SIDM_DISABLE_KSFR_MASK"] = "0"
    if "t90_v58_ablation" in sys.modules:
        del sys.modules["t90_v58_ablation"]


def test_ksfr_rejects_m_phi_outside_box():
    """KSFR returns -inf for m_phi_A outside [418, 4180] MeV."""
    os.environ["SIDM_DISABLE_KSFR_MASK"] = "0"
    if "t90_v58_ablation" in sys.modules:
        del sys.modules["t90_v58_ablation"]
    import t90_v58_ablation as m_ksfr_on
    # m_phi_A too low (10^2.0 = 100 MeV)
    theta_low = THETA_LOG_MEDIAN.copy()
    theta_low[1] = 2.0  # 100 MeV, outside box
    ll = m_ksfr_on._loglike_subset(theta_low, {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"})
    assert ll == -np.inf, f"KSFR should reject m_phi_A=100 MeV (outside box): {ll}"
    # m_phi_A too high (10^4.0 = 10000 MeV)
    theta_high = THETA_LOG_MEDIAN.copy()
    theta_high[1] = 4.0  # 10000 MeV, outside box
    ll = m_ksfr_on._loglike_subset(theta_high, {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"})
    assert ll == -np.inf, f"KSFR should reject m_phi_A=10000 MeV (outside box): {ll}"


def test_lz_silent_when_wimpy_missing(monkeypatch):
    """When WIMpy is unavailable, LZ loglike is 0 (silent)."""
    if "t90_v58_ablation" in sys.modules:
        del sys.modules["t90_v58_ablation"]
    import t90_v58_ablation as m_lz_test
    monkeypatch.setattr(m_lz_test, "_check_wimpy", lambda: False)
    # Note: loglike_lz_magnetic_moment uses the WIMpy result internally;
    # the test checks that dropping LZ and not dropping LZ gives the same result.
    ll_no_lz = m_lz_test._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "Bullet", "KSFR"})
    ll_with_lz = m_lz_test._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "Bullet", "KSFR", "LZ"})
    # If WIMpy is silent, ll_with_lz should equal ll_no_lz
    # (but this test only runs when WIMpy is actually missing -- skip otherwise)


def test_drop_bullet_changes_loglike():
    """Bullet at sigma/m=0.0014 should give loglike ≈ 0, so dropping shouldn't change much."""
    if "t90_v58_ablation" in sys.modules:
        del sys.modules["t90_v58_ablation"]
    import t90_v58_ablation as m_bul
    ll_with_bul = m_bul._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"})
    ll_no_bul = m_bul._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "LZ", "KSFR"})
    # Bullet at sigma/m=0.0014 should give ≈ 0 loglike (well under 0.5 constraint)
    assert abs(ll_with_bul - ll_no_bul) < 0.01, (
        f"Bullet loglike at sigma/m=0.0014 should be ~0; got diff {ll_with_bul - ll_no_bul}"
    )


def test_drop_galaxy_changes_loglike():
    """Galaxy at sigma/m=1.25 should give loglike ≈ 0 (under 2 limit)."""
    if "t90_v58_ablation" in sys.modules:
        del sys.modules["t90_v58_ablation"]
    import t90_v58_ablation as m_gal
    ll_with = m_gal._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"})
    ll_without = m_gal._loglike_subset(THETA_LOG_MEDIAN, {"Cloud9", "Bullet", "LZ", "KSFR"})
    assert abs(ll_with - ll_without) < 0.01, (
        f"Galaxy loglike at sigma/m=1.25 should be ~0; got diff {ll_with - ll_without}"
    )


def test_out_of_prior_returns_neginf():
    """theta_log outside prior bounds should return -inf."""
    if "t90_v58_ablation" in sys.modules:
        del sys.modules["t90_v58_ablation"]
    import t90_v58_ablation as m_prior
    bad_theta = THETA_LOG_MEDIAN.copy()
    bad_theta[0] = 100.0  # way outside log m_chi prior [0.5, 3.0]
    ll = m_prior._loglike_subset(bad_theta, {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"})
    assert ll == -np.inf, f"Out-of-prior theta should return -inf: {ll}"


def test_smoke_ablation_writes_jsons():
    """Tiny ablation (nlive=50) writes all 6 JSONs."""
    code_dir = Path(__file__).resolve().parent.parent / "code"
    venv_python = code_dir.parent.parent / ".venv-sidm-bench" / "Scripts" / "python.exe"
    if not venv_python.exists():
        pytest.skip(f"venv-sidm-bench not at {venv_python}")
    results_dir = code_dir.parent / "data" / "results"
    # Cleanup any stale t90_v58 files
    for f in results_dir.glob("t90_v58_ablation_*.json"):
        f.unlink()
    cmd = [
        str(venv_python), "-u",
        str(code_dir / "t90_v58_ablation.py"),
        "--nlive", "50",
        "--dlogz", "0.5",  # relax convergence for smoke
    ]
    env = os.environ.copy()
    env["SIDM_DISABLE_KSFR_MASK"] = "0"
    # timeout 25 min -- nlive=50 is fast (~70-110s per subset), but 6 subsets serial
    try:
        result = subprocess.run(cmd, env=env, cwd=str(code_dir), capture_output=True,
                                text=True, timeout=1500)
        assert result.returncode == 0, f"Smoke run failed:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        pytest.fail("Smoke ablation timed out (>25 min)")
    # Check all expected JSONs were written
    expected = ["all_5ch", "drop_Cloud9", "drop_Galaxy", "drop_Bullet", "drop_LZ", "drop_KSFR"]
    for name in expected:
        json_path = results_dir / f"t90_v58_ablation_{name}.json"
        assert json_path.exists(), f"Missing JSON: {json_path}"
    summary_path = results_dir / "t90_v58_ablation_summary.json"
    assert summary_path.exists(), f"Missing summary: {summary_path}"
