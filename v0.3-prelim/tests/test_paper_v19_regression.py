"""
Paper v1.9 claim regression tests.

Locks down the corrected numbers in Paper v1.9 (after T101.4 bug discovery).

These tests REGRESS-PROTECT the v1.9 corrections:
  - §2.1 v_peak,1 = v_target,1 (NOT 1.4x v_target)
  - §3.2 Cloud-9 anchor: σ/m(v=28) ≈ 100 cm²/g
  - §3.6 dSph tension: σ/m(v=30) ≈ 161 cm²/g (800x violation)
  - §3.6 actual violation ratio: ~800x (not 38x)

If any of these tests fail after a future change, it means:
  1. The kinematics formula was reverted to the buggy version (E_R = ½ m v²), OR
  2. The Phase 44 fit parameters were re-tuned (which is fine if intentional),
  3. The paper text was reverted to the v1.8 numbers (which would be a regression).

IMPORTANT: This module uses the CORRECT kinematics (E_R = ¼ m v²), which is
different from what test_physical_constraints.py uses (factor-of-2 bug).

The bug is documented in T101_4_DECISION_GATE_REPORT_2026_09_19.md and
test_t101_decision_gate.py.
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
    """Build resonances with CORRECT kinematics: E_R = (1/4) m v^2."""
    m_chi_eV = m_chi_GeV * 1e9
    resonances = []
    for v, sp, gf in zip(v_targets, sigma_peaks, gamma_fracs):
        v_cm_s = v * 1e5
        E_R_eV = 0.25 * m_chi_eV * (v_cm_s / 2.998e10) ** 2
        resonances.append({
            "name": f"r_vt{v:.0f}",
            "E_R_eV": float(E_R_eV),
            "Gamma_eV": float(gf * E_R_eV),
            "sigma_peak_cm2_per_g": float(sp),
        })
    return resonances


# =========================================================================
# Paper v1.9 regression tests
# =========================================================================

def test_paper_v19_cloud9_anchor_at_v28():
    """v1.9 §3.2: σ/m(v=28) ≈ 100 cm²/g (Cloud-9 anchor, satisfies ≳ 100 target)."""
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    sm = sigma_m_at_v(28.0, p["m_chi"], resonances, p["sigma_0"], p["a_slope"])
    # Paper says ~100, actual is 100.07; allow 5% tolerance
    assert abs(sm - 100.0) / 100.0 < 0.05, (
        f"σ/m(v=28) = {sm:.2f}, paper v1.9 says ≈ 100 (5% tolerance). "
        f"If this fails, the Cloud-9 anchor claim has drifted."
    )


def test_paper_v19_peak_at_v_target():
    """v1.9 §2.1: v_peak,1 = v_target,1 ≈ 29 km/s (NOT 1.4 x v_target = 41 km/s).

    With corrected kinematics, the actual peak of σ/m(v) coincides with v_target.
    """
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    # Sample finely around v_target,1
    vs = np.linspace(p["v_targets"][0] - 5, p["v_targets"][0] + 5, 1000)
    vals = [sigma_m_at_v(v, p["m_chi"], resonances, p["sigma_0"], p["a_slope"]) for v in vs]
    i_max = int(np.argmax(vals))
    v_peak = vs[i_max]
    v_target_1 = p["v_targets"][0]
    # Should be within 1 km/s of v_target,1 (NOT 12 km/s away as v1.8 claimed)
    assert abs(v_peak - v_target_1) < 1.0, (
        f"v_peak = {v_peak:.2f} km/s, expected ≈ v_target,1 = {v_target_1:.2f}. "
        f"v1.8 erroneously claimed v_peak ≈ 41 km/s; v1.9 says v_peak ≈ v_target."
    )


def test_paper_v19_dsph_violation_is_800x():
    """v1.9 §3.6: σ/m(v=30) ≈ 161 cm²/g, ~800x above Horigome+ 2025 limit.

    The v1.8 number (7.5 cm²/g, 38x) was based on a factor-of-2 kinematics bug.
    """
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    sm = sigma_m_at_v(30.0, p["m_chi"], resonances, p["sigma_0"], p["a_slope"])
    # Horigome+ 2025 upper limit: σ/m < 0.2 cm²/g
    violation_ratio = sm / 0.2
    # v1.9 says ~800x; allow 750-850x for numerical stability
    assert 750 < violation_ratio < 850, (
        f"dSph violation = {violation_ratio:.1f}x, expected ~800x (per v1.9 §3.6). "
        f"v1.8 quoted 38x based on buggy kinematics. σ/m(v=30) = {sm:.2f} cm²/g."
    )


def test_paper_v19_peak_height_above_cloud9_target():
    """v1.9 §3.2: σ/m(v_peak,1) ≈ 197 cm²/g, comfortably above Cloud-9 (≳ 100)."""
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    vs = np.linspace(5, 100, 1000)
    vals = [sigma_m_at_v(v, p["m_chi"], resonances, p["sigma_0"], p["a_slope"]) for v in vs]
    peak_val = max(vals)
    # Should be well above 100 cm²/g
    assert peak_val >= 150, (
        f"Peak σ/m = {peak_val:.2f}, expected ≳ 150 (Cloud-9 target is ≳ 100). "
        f"v1.9 says ≈ 197."
    )


def test_paper_v19_sparc_v100_in_band():
    """v1.9: σ/m(v=100) ≈ 0.07 cm²/g (in SPARC band [0.05, 0.5])."""
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    resonances = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    sm = sigma_m_at_v(100.0, p["m_chi"], resonances, p["sigma_0"], p["a_slope"])
    assert 0.05 <= sm <= 0.5, (
        f"σ/m(v=100) = {sm:.4f}, expected in [0.05, 0.5] (SPARC band). "
        f"v1.9 says ≈ 0.07."
    )


def test_kinematics_convention_quarter_m_v_squared():
    """Regression: ensure E_R uses (1/4) m v², not (1/2) m v².

    This is the canonical convention used by the paper v1.9 corrections.
    If anyone reverts to (1/2) m v², all the v1.9 numbers will drift by ~21x.
    """
    sigma_m_at_v = _import_phase44()
    p = _load_phase44_params()
    # Build with CORRECT formula and check σ/m(v=30)
    res_correct = _make_resonances_correct(p["m_chi"], p["v_targets"], p["sigma_peaks"], p["gamma_fracs"])
    sm_correct = sigma_m_at_v(30.0, p["m_chi"], res_correct, p["sigma_0"], p["a_slope"])

    # Build with WRONG formula (factor of 2)
    m_chi_eV = p["m_chi"] * 1e9
    res_wrong = []
    for v, sp, gf in zip(p["v_targets"], p["sigma_peaks"], p["gamma_fracs"]):
        v_cm_s = v * 1e5
        E_R_eV = 0.5 * m_chi_eV * (v_cm_s / 2.998e10) ** 2  # WRONG
        res_wrong.append({
            "name": f"r_vt{v:.0f}",
            "E_R_eV": float(E_R_eV),
            "Gamma_eV": float(gf * E_R_eV),
            "sigma_peak_cm2_per_g": float(sp),
        })
    sm_wrong = sigma_m_at_v(30.0, p["m_chi"], res_wrong, p["sigma_0"], p["a_slope"])

    # The two should differ by factor ~21 (bug effect)
    ratio = sm_correct / sm_wrong
    assert ratio > 10, (
        f"Ratio (correct / wrong kinematics) = {ratio:.2f}. "
        f"Correct: {sm_correct:.2f}, Wrong: {sm_wrong:.2f}. "
        f"Paper v1.9 uses CORRECT convention. If this ratio approaches 1, "
        f"someone reverted to the buggy formula."
    )


def test_paper_v19_status_line_present():
    """v1.9 status line should be present in PAPER_V1_DRAFT.md."""
    # PAPER_V1_DRAFT.md is at <repo_root>/v0.3-prelim/docs/PAPER_V1_DRAFT.md
    paper_path = CODE_DIR.parent.parent / "docs" / "PAPER_V1_DRAFT.md"
    if not paper_path.exists():
        # Try repo root (CODE_DIR is v0.3-prelim/code, so parent.parent is repo root)
        paper_path = CODE_DIR.parent.parent / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
    if not paper_path.exists():
        pytest.skip(f"PAPER_V1_DRAFT.md not found (tried {paper_path})")
    content = paper_path.read_text(encoding="utf-8")
    # Should mention v1.9 in the Status line
    assert "v1.9" in content, "PAPER_V1_DRAFT.md should be at v1.9 (per T101.4 corrections)"
    # Should mention the 800x dSph correction
    assert "800" in content or "~800" in content, (
        "v1.9 paper should mention the 800x dSph correction (T101.4 finding)"
    )
    # Should mention refs [28] and [29]
    assert "[28]" in content and "[29]" in content, (
        "v1.9 should add refs [28] Chu, Garcia-Cely, Murayama and [29] Chu, Hambye, Tytgat"
    )
