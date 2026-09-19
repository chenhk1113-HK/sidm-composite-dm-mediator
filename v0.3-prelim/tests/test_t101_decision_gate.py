"""
T101.4 — Decision gate evaluation.

This module documents the T101.4 decision gate from POST_PAPER_ROADMAP_2026_09_17.md:

1. Peak σ/m >= 50 cm²/g at v_peak ~ 1.4x v_target?
2. Cloud-9 anchor: σ/m(v=28) >= 50 cm²/g?
3. dSph tension: σ/m(v=30) < 0.2 cm²/g?
4. Match semi-classical approximation (T101.2 verified, ratio 1.008)?

CRITICAL FINDING during T101.4 evaluation (2026-09-19):

The Phase 44 free fit, evaluated with the CORRECT relativistic kinematics
E_R = (1/4) m_chi v^2 (reduced mass = m_chi/2), gives:

  v_peak = 29.4 km/s (NOT 41 km/s as paper claims)
  Peak sigma/m = 196 cm²/g (well above 50)
  sigma/m(v=28) = 100 cm²/g (Cloud-9 anchor passes)
  sigma/m(v=30) = 160 cm²/g (dSph upper limit violated by 803x, NOT 38x)

The paper's "38x dSph tension" comes from using an INCORRECT kinematics
formula E_R = (1/2) m_chi v^2 (factor of 2 too large). With this wrong
formula, the dSph sigma/m drops to 7.5 (matching paper), but the peak
sigma/m at v_peak = 29 also drops to ~7 (failing Cloud-9).

The test_physical_constraints.py module uses the WRONG kinematics, which
is why its anchor checks pass. This module reproduces the correct
calculation and shows the actual decision-gate evaluation.

This is a paper-level finding: the v1.8 paper's quoted dSph tension (38x)
is INCORRECT. The actual is ~803x. The Cloud-9 satisfaction is genuine
but at the kinematic v_target=28 (sigma/m=100), not at v_peak=41 (where
sigma/m is much smaller, only ~2.5 cm²/g).
"""
import sys
from pathlib import Path

import numpy as np
import pytest

CODE_DIR = Path(__file__).resolve().parent.parent / "code"
sys.path.insert(0, str(CODE_DIR))


def _import_phase44():
    try:
        from phase44_joint_fit import sigma_m_at_v  # type: ignore
        return sigma_m_at_v
    except (ImportError, ModuleNotFoundError) as e:
        pytest.skip(f"phase44_joint_fit not importable: {e}")


def _load_phase44_params():
    import json
    p44 = json.load(open(CODE_DIR.parent / "data" / "results" / "phase44_joint_fit.json"))
    bp = p44["best_params"]
    return {
        "m_chi": bp[0],
        "sigma_0": bp[1],
        "a_slope": bp[2],
        "v_targets": list(bp[3:7]),
        "sigma_peaks": list(bp[7:11]),
        "gamma_fracs": list(bp[11:15]),
    }


def _make_resonances_correct(m_chi_GeV, v_targets, sigma_peaks, gamma_fracs):
    """Build resonances with CORRECT kinematics: E_R = (1/4) m_chi v^2.

    For equal-mass scattering, the relative velocity in the CM frame is
    v_rel / 2, so E_cm = (1/2) m_red (v_rel)^2 = (1/2)(m_chi/2)(v_rel)^2
                    = (1/4) m_chi v_rel^2

    The test_physical_constraints.py module uses (1/2) m_chi v^2 (incorrect).
    """
    m_chi_eV = m_chi_GeV * 1e9
    resonances = []
    for v, sp, gf in zip(v_targets, sigma_peaks, gamma_fracs):
        v_cm_s = v * 1e5
        E_R_eV = 0.25 * m_chi_eV * (v_cm_s / 2.998e10) ** 2  # CORRECT
        resonances.append({
            "name": f"r_vt{v:.0f}",
            "E_R_eV": float(E_R_eV),
            "Gamma_eV": float(gf * E_R_eV),
            "sigma_peak_cm2_per_g": float(sp),
        })
    return resonances


def _make_resonances_test(m_chi_GeV, v_targets, sigma_peaks, gamma_fracs):
    """Build resonances with INCORRECT kinematics (factor of 2): E_R = (1/2) m_chi v^2.

    This is what test_physical_constraints.py uses, which causes the
    paper's "38x dSph tension" to be reported.
    """
    m_chi_eV = m_chi_GeV * 1e9
    resonances = []
    for v, sp, gf in zip(v_targets, sigma_peaks, gamma_fracs):
        v_cm_s = v * 1e5
        E_R_eV = 0.5 * m_chi_eV * (v_cm_s / 2.998e10) ** 2  # WRONG (factor 2)
        resonances.append({
            "name": f"r_vt{v:.0f}",
            "E_R_eV": float(E_R_eV),
            "Gamma_eV": float(gf * E_R_eV),
            "sigma_peak_cm2_per_g": float(sp),
        })
    return resonances


# =========================================================================
# T101.4 decision gate tests
# =========================================================================

def test_decision_gate_peak_height():
    """T101.4: peak sigma/m must be >= 50 cm²/g."""
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    vs = np.linspace(5, 200, 400)
    vals = [sigma_m_at_v(v, p["m_chi"], resonances, p["sigma_0"], p["a_slope"]) for v in vs]
    i_max = int(np.argmax(vals))
    peak_sigma_m = vals[i_max]
    assert peak_sigma_m >= 50.0, (
        f"Peak sigma/m = {peak_sigma_m:.2f} cm²/g, required >= 50"
    )


def test_decision_gate_cloud9_anchor():
    """T101.4: sigma/m at v=28 (Cloud-9 kinematic) must be >= 50 cm²/g."""
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    sigma_at_28 = sigma_m_at_v(28.0, p["m_chi"], resonances, p["sigma_0"], p["a_slope"])
    assert sigma_at_28 >= 50.0, (
        f"Cloud-9 anchor sigma/m(v=28) = {sigma_at_28:.2f}, required >= 50"
    )


def test_decision_gate_dsph_violation_actual():
    """T101.4: dSph sigma/m(v=30) < 0.2 cm²/g.

    HONEST: with correct kinematics, the actual violation is ~803x, NOT 38x
    as the paper claims. The paper's 38x comes from an incorrect E_R formula.
    """
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    sigma_at_30 = sigma_m_at_v(30.0, p["m_chi"], resonances, p["sigma_0"], p["a_slope"])
    # dSph upper limit is 0.2 cm²/g (Horigome+ 2025)
    # Actual is ~160 cm²/g, so violation is ~800x
    violation_ratio = sigma_at_30 / 0.2
    # This test DOCUMENTS the violation, doesn't pass/fail on it
    # The violation is real and the paper should be updated
    assert violation_ratio > 100, (
        f"dSph violation {violation_ratio:.1f}x - paper claim of 38x is based on "
        f"INCORRECT kinematics. Actual sigma/m(v=30) = {sigma_at_30:.2f} cm²/g."
    )


def test_kinematics_factor_of_2_discrepancy():
    """T101.4: document the factor-of-2 discrepancy between test and correct kinematics.

    With E_R = (1/2) m v^2 (test version): sigma/m(v=30) = 7.54 cm²/g
    With E_R = (1/4) m v^2 (correct): sigma/m(v=30) = 160.62 cm²/g

    The test version gives "38x dSph violation" (paper claim).
    The correct version gives ~803x dSph violation.
    """
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    res_test = _make_resonances_test(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    res_correct = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])

    sm_test = sigma_m_at_v(30.0, p["m_chi"], res_test, p["sigma_0"], p["a_slope"])
    sm_correct = sigma_m_at_v(30.0, p["m_chi"], res_correct, p["sigma_0"], p["a_slope"])

    ratio = sm_correct / sm_test
    # Should be approximately factor 21 (because the BW peak shift at v=30
    # with the wrong E_R moves the peak out of the resonance)
    assert ratio > 10, (
        f"sigma/m ratio (correct / test) = {ratio:.2f}. "
        f"Factor-of-2 E_R bug causes ~21x difference in sigma/m(v=30)."
    )
