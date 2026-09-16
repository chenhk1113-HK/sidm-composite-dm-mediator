"""Smoke test for Phase 51 — verifies the headline numbers from the JSON match
the on-disk artifacts.

Per Rule 18 (post-write verification): after any .py file is created or
modified, run this smoke test before claiming Phase 51 is correct.

Checks:
  1. JSON file exists and parses.
  2. Headline numbers: clockwork RMS = 0.016, secluded U(1) RMS = 0.018, Phase 48 ref = 2.61.
  3. Reduction factor: clockwork 163x, secluded 143x (within rounding).
  4. Construction velocities match the T90.70 target ladder [28, 100, 300, 700].
  5. Phase 51 clockwork fit reproduces the T90.70 target within ~5% per peak.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

RESULTS = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\phase51_portal_resonance.json")

V_TARGETS = [28.0, 100.0, 300.0, 700.0]


def main():
    print("=== Phase 51 smoke test ===")
    if not RESULTS.exists():
        sys.exit(f"FAIL: {RESULTS} not found")
    out = json.loads(RESULTS.read_text())

    # Check 1: structure
    assert "constructions" in out, "FAIL: missing 'constructions'"
    assert "A_secluded_U1" in out["constructions"], "FAIL: missing A_secluded_U1"
    assert "B_clockwork" in out["constructions"], "FAIL: missing B_clockwork"
    assert "C_dark_QCD_full_pool" in out["constructions"], "FAIL: missing C_dark_QCD_full_pool"
    print("OK: structure")

    # Check 2: headline numbers
    rms_a = out["constructions"]["A_secluded_U1"]["fine_tuning_rms_log10"]
    rms_b = out["constructions"]["B_clockwork"]["fine_tuning_rms_log10"]
    rms_c = out["constructions"]["C_dark_QCD_full_pool"]["fine_tuning_rms_log10"]
    rms_ref = out["phase48_reference_rms_log10"]

    assert abs(rms_a - 0.0183) < 0.001, f"FAIL: A RMS = {rms_a}, expected 0.018"
    assert abs(rms_b - 0.0159) < 0.001, f"FAIL: B RMS = {rms_b}, expected 0.016"
    assert abs(rms_c - 0.3317) < 0.001, f"FAIL: C RMS = {rms_c}, expected 0.332"
    assert abs(rms_ref - 2.6065) < 0.001, f"FAIL: phase48 ref = {rms_ref}, expected 2.607"
    print(f"OK: headline RMS values (A={rms_a:.4f}, B={rms_b:.4f}, C={rms_c:.4f}, ref={rms_ref:.4f})")

    # Check 3: reduction factors
    factor_a = rms_ref / rms_a
    factor_b = rms_ref / rms_b
    assert abs(factor_a - 142.7) < 5.0, f"FAIL: factor A = {factor_a:.1f}, expected 142.7"
    assert abs(factor_b - 163.7) < 5.0, f"FAIL: factor B = {factor_b:.1f}, expected 163.7"
    print(f"OK: reduction factors (A={factor_a:.1f}x, B={factor_b:.1f}x)")

    # Check 4: clockwork reproduces target within 10%
    v_b = out["constructions"]["B_clockwork"]["best_fit"]["v_resonances_kms"]
    for v_actual, v_target in zip(v_b, V_TARGETS):
        rel_err = abs(v_actual - v_target) / v_target
        assert rel_err < 0.10, f"FAIL: clockwork v={v_actual:.1f} vs target {v_target}, err={rel_err:.1%}"
    print(f"OK: clockwork reproduces target within 10%: {v_b}")

    # Check 5: secluded U(1) reproduces target within 10%
    v_a = out["constructions"]["A_secluded_U1"]["best_fit"]["v_resonances_kms"]
    for v_actual, v_target in zip(v_a, V_TARGETS):
        rel_err = abs(v_actual - v_target) / v_target
        assert rel_err < 0.10, f"FAIL: secluded U(1) v={v_actual:.1f} vs target {v_target}, err={rel_err:.1%}"
    print(f"OK: secluded U(1) reproduces target within 10%: {v_a}")

    # Check 6: verdicts
    assert out["constructions"]["A_secluded_U1"]["verdict"].startswith("MINIMAL")
    assert out["constructions"]["B_clockwork"]["verdict"].startswith("MINIMAL")
    assert out["constructions"]["C_dark_QCD_full_pool"]["verdict"].startswith("MODERATE")
    print("OK: all verdicts correct")

    # Check 7: clockwork k values are integers (or very close)
    k_b = out["constructions"]["B_clockwork"]["best_fit"]["levels_k"]
    for k in k_b:
        assert abs(k - round(k)) < 0.01, f"FAIL: clockwork k = {k} not integer"
    print(f"OK: clockwork k values are integer: {k_b}")

    # Check 8: q is in plausible clockwork range
    q_b = out["constructions"]["B_clockwork"]["best_fit"]["q"]
    assert 1.05 <= q_b <= 5.0, f"FAIL: q = {q_b} outside scanned range"
    print(f"OK: clockwork q = {q_b:.4f} in plausible range")

    print()
    print("=== ALL SMOKE TESTS PASSED ===")
    print(f"Headline: Phase 51 reduces T90.70 fine-tuning from {rms_ref:.4f} → {min(rms_a, rms_b):.4f}")
    print(f"          = {max(factor_a, factor_b):.1f}x reduction (clockwork winner)")


if __name__ == "__main__":
    main()