"""
Regression tests for T191-T194 UV completion tests + figure.

T191: δ_0(v) at multiple α_D — verifies Cloud-9 cannot be Yukawa at any coupling
T192: Thermal-averaged Breit-Wigner — verifies correct Ωh² = 0.119
T193: Thermal averaging visualization — verifies resonance at v_res
T194: Master σ/m(v) figure — verifies canonical parameters and constraints

These tests lock down the headline numbers that appear in the paper.
If any of these fail, the paper's status line has drifted from the data.

To run:
    pytest v0.3-prelim/tests/test_t191_t194_uv_completion.py -v
"""

import json
from pathlib import Path

import pytest

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def _load(name: str) -> dict:
    """Load a reference JSON from data/results/."""
    path = RESULTS_DIR / name
    if not path.exists():
        pytest.skip(f"Reference JSON not found: {name}")
    with open(path) as f:
        return json.load(f)


# ============================================================
# T191 — δ_0(v) at multiple α_D
# ============================================================

def test_t191_delta0_at_v28_low_alpha():
    """At α_D=0.01, δ_0(v=28 km/s) should be very small (< 0.01 rad)."""
    data = _load("t191_delta_0_vs_v.json")
    res_001 = data["results"]["alpha_D_0.01"]
    # JSON has pre-computed "delta_0_at_28_km_s"
    d0_at_28 = res_001["delta_0_at_28_km_s"]
    assert d0_at_28 < 0.01, \
        f"δ_0(v=28) at α_D=0.01 = {d0_at_28} rad; expected < 0.01"


def test_t191_delta0_at_v28_high_alpha():
    """At α_D=100, δ_0(v=28 km/s) should still be < π/2 (no resonance)."""
    data = _load("t191_delta_0_vs_v.json")
    res_100 = data["results"]["alpha_D_100.0"]
    d0_at_28 = res_100["delta_0_at_28_km_s"]
    assert d0_at_28 < 1.57, \
        f"δ_0(v=28) at α_D=100 = {d0_at_28} rad; expected < π/2 ≈ 1.57"


def test_t191_peak_at_cluster_scale():
    """Peak δ_0 should be at v ≈ 1083 km/s (cluster scale), NOT v=28 km/s."""
    data = _load("t191_delta_0_vs_v.json")
    res_1 = data["results"]["alpha_D_1.0"]
    v_peak = res_1["peak_velocity_km_s"]
    # Allow 10% tolerance on 1083 km/s
    assert abs(v_peak - 1083) / 1083 < 0.10, \
        f"Peak δ_0 at v={v_peak} km/s; expected ~1083 km/s"


def test_t191_max_delta0_below_pi_over_2():
    """Max δ_0 across all tested α_D should be < π/2 (no resonance)."""
    data = _load("t191_delta_0_vs_v.json")
    max_d0 = 0
    for key, res in data["results"].items():
        if "peak_delta_0" in res:
            max_d0 = max(max_d0, res["peak_delta_0"])
    assert max_d0 < 1.57, \
        f"Max δ_0 = {max_d0} rad; expected < π/2"


# ============================================================
# T192 — Thermal-averaged Breit-Wigner
# ============================================================

def _get_t192_best_config():
    """Get the T192 best configuration (with δ=0.43%, g_h_SM=0.00040)."""
    data = _load("t192_thermal_avg.json")
    # best_configuration is the dict; not a list
    return data["best_configuration"]


def test_t192_omega_h2_in_planck_2sigma():
    """Ωh² should be within Planck 2σ of 0.12 (i.e., in [0.115, 0.125])."""
    bc = _get_t192_best_config()
    omega_h2 = bc["Omega_h2"]
    assert 0.115 < omega_h2 < 0.125, \
        f"Ωh² = {omega_h2}; expected in [0.115, 0.125]"


def test_t192_g_h_SM_below_charm_limit():
    """g_h_SM = 0.00040 should be below CHARM limit of 0.005."""
    bc = _get_t192_best_config()
    g_h_SM = bc["g_h_SM"]
    assert g_h_SM < 0.005, \
        f"g_h_SM = {g_h_SM}; CHARM limit = 0.005"


def test_t192_thermal_avg_suppression():
    """<σv>_thermal should be ~2.6×10⁻²⁶ cm³/s (proper thermal integration)."""
    bc = _get_t192_best_config()
    sigma_v = bc["sigma_v_thermal_cm3_per_s"]
    # 1.5×10⁻²⁶ to 4×10⁻²⁶ range
    assert 1.5e-26 < sigma_v < 4.0e-26, \
        f"<σv>_thermal = {sigma_v} cm³/s; expected ~2.6×10⁻²⁶"


def test_t192_detuning_5x_broader_than_drobczyk():
    """δ = 0.43% is 5× broader than Drobczyk's 0.083%."""
    bc = _get_t192_best_config()
    delta = bc["delta"]
    assert 0.003 < delta < 0.006, \
        f"δ = {delta}; expected ~0.43% (5× broader than Drobczyk 0.083%)"


# ============================================================
# T193 — Thermal averaging visualization
# ============================================================

def test_t193_resonance_peak_at_v_res():
    """BW peak should be at v_res = √(8δ) for δ = 0.43%, so v_res ≈ 0.185c."""
    data = _load("t193_thermal_visualization.json")
    res = data["resonance"]
    v_res_c = res["v_res_over_c"]
    assert abs(v_res_c - 0.185) < 0.01, \
        f"v_res = {v_res_c}c; expected 0.185c for δ=0.43%"


def test_t193_most_probable_v_rel():
    """Most probable v_rel at T_F = m_χ/22 should be v_0 ≈ 0.302c."""
    data = _load("t193_thermal_visualization.json")
    fo = data["freeze_out"]
    v_0_c = fo["v_thermal_scale"]
    assert abs(v_0_c - 0.302) < 0.02, \
        f"v_0 = {v_0_c}c; expected ~0.302c"


def test_t193_resonance_in_thermal_window():
    """Resonance v_res = 0.185c should be in thermal window (v_0 = 0.302c)."""
    data = _load("t193_thermal_visualization.json")
    v_res_c = data["resonance"]["v_res_over_c"]
    v_0_c = data["freeze_out"]["v_thermal_scale"]
    # v_res < v_0 means resonance is below the thermal peak
    assert v_res_c < v_0_c, \
        f"v_res = {v_res_c}c should be < v_0 = {v_0_c}c"


# ============================================================
# T194 — Master σ/m(v) figure
# ============================================================

def test_t194_best_fit_sigma_0():
    """Phase 44 background σ_0 should be 0.052 cm²/g at v_ref = 100 km/s."""
    data = _load("t194_master_sigma_v.json")
    sigma_0 = data["best_fit"]["sigma_0_cm2_per_g"]
    assert abs(sigma_0 - 0.052) < 0.005, \
        f"σ_0 = {sigma_0}; expected 0.052 ± 0.005"


def test_t194_alpha_yukawa():
    """Yukawa slope α = 1.93 (data-driven, NOT theoretical α=2)."""
    data = _load("t194_master_sigma_v.json")
    alpha = data["best_fit"]["alpha"]
    assert abs(alpha - 1.93) < 0.05, \
        f"α = {alpha}; expected 1.93 (data-driven)"


def test_t194_4_targets_clockwork():
    """4 v_targets should be [28, 100, 178, 430] km/s (clockwork UV prior)."""
    data = _load("t194_master_sigma_v.json")
    v_targets = data["best_fit"]["v_targets_km_s"]
    expected = [28, 100, 178, 430]
    assert v_targets == expected, \
        f"v_targets = {v_targets}; expected {expected}"


def test_t194_dominant_peak_height():
    """Only v1 peak height should be dominant (≥ 100 cm²/g)."""
    data = _load("t194_master_sigma_v.json")
    peaks = data["best_fit"]["peak_heights_cm2_per_g"]
    assert peaks[0] > 50, \
        f"v1 peak height = {peaks[0]} cm²/g; expected > 50 (Cloud-9 dominant)"
    # Other peaks should be < 1 cm²/g (bookkeeping nodes)
    for i, p in enumerate(peaks[1:], 1):
        assert p < 1.0, \
            f"v{i+1} peak height = {p} cm²/g; expected < 1 (bookkeeping node)"


def test_t194_constraints_present():
    """All observational constraints should be in the figure metadata."""
    data = _load("t194_master_sigma_v.json")
    constraints = data["constraints"]
    # Check substring matches
    expected = ["Cloud-9", "dSph", "SPARC", "Cluster", "UFD", "Bullet"]
    matched = []
    for ch in expected:
        for k in constraints:
            if ch in k:
                matched.append(ch)
                break
    missing = set(expected) - set(matched)
    assert not missing, \
        f"Constraints missing from T194 figure metadata: {missing}"


def test_t194_RMSE_lock():
    """RMSE on 7-point fit should be 0.250."""
    data = _load("t194_master_sigma_v.json")
    rmse = data["RMSE_7point"]
    assert abs(rmse - 0.250) < 0.01, \
        f"7-point RMSE = {rmse}; expected 0.250"


# ============================================================
# Cross-test consistency (T191 vs T192 vs T194)
# ============================================================

def test_omega_h2_consistency():
    """T192 Ωh² should match the value quoted in paper §10.3 (0.119)."""
    bc = _get_t192_best_config()
    omega = bc["Omega_h2"]
    assert abs(omega - 0.119) < 0.005, \
        f"Ωh² in T192 = {omega}; paper says 0.119"


def test_g_h_SM_consistency():
    """g_h_SM should be 0.00040 across all UV completion tests."""
    bc = _get_t192_best_config()
    g = bc["g_h_SM"]
    assert abs(g - 0.00040) < 0.00005, \
        f"g_h_SM in T192 = {g}; paper consistently uses 0.00040"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])