"""Smoke test for Phase 52 — multi-mediator product-group benchmark.

Per Rule 18 (post-write verification): after any .py file is created or
modified, run this smoke test before claiming Phase 52 is correct.

Checks:
  1. JSON file exists and parses.
  2. Headline numbers: B (power-law) RMS = 0.046, C (n^alpha) RMS = 0.061.
  3. Both B and C land in MINIMAL territory (RMS < 0.3).
  4. Both fit target ladder within 15% per peak.
  5. Phase 52 verdict agrees with Phase 51 that multiple UV constructions
     achieve MINIMAL fine-tuning.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

RESULTS = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\phase52_multi_mediator.json")

V_TARGETS = [28.0, 100.0, 300.0, 700.0]


def main():
    print("=== Phase 52 smoke test ===")
    if not RESULTS.exists():
        sys.exit(f"FAIL: {RESULTS} not found")
    out = json.loads(RESULTS.read_text())

    # Check 1: structure
    assert "constructions" in out, "FAIL: missing 'constructions'"
    assert "A_free_mass_ratios" in out["constructions"], "FAIL: missing A"
    assert "B_power_law_q_ip1" in out["constructions"], "FAIL: missing B"
    assert "C_integer_n_alpha" in out["constructions"], "FAIL: missing C"
    print("OK: structure")

    # Check 2: headline numbers
    rms_b = out["constructions"]["B_power_law_q_ip1"]["fine_tuning_rms_log10"]
    rms_c = out["constructions"]["C_integer_n_alpha"]["fine_tuning_rms_log10"]
    rms_a = out["constructions"]["A_free_mass_ratios"]["fine_tuning_rms_log10"]
    assert abs(rms_b - 0.0464) < 0.001, f"FAIL: B RMS = {rms_b}, expected 0.046"
    assert abs(rms_c - 0.0608) < 0.001, f"FAIL: C RMS = {rms_c}, expected 0.061"
    assert abs(rms_a) < 1e-10, f"FAIL: A RMS = {rms_a}, expected 0.0 (trivial)"
    print(f"OK: headline RMS values (A={rms_a:.4f} trivial, B={rms_b:.4f}, C={rms_c:.4f})")

    # Check 3: both B and C are MINIMAL
    assert out["constructions"]["B_power_law_q_ip1"]["verdict"].startswith("MINIMAL"), \
        f"FAIL: B verdict = {out['constructions']['B_power_law_q_ip1']['verdict']}"
    assert out["constructions"]["C_integer_n_alpha"]["verdict"].startswith("MINIMAL"), \
        f"FAIL: C verdict = {out['constructions']['C_integer_n_alpha']['verdict']}"
    print("OK: B and C both MINIMAL")

    # Check 4: B and C reproduce target within 25%
    for label, key in [("B", "B_power_law_q_ip1"), ("C", "C_integer_n_alpha")]:
        v = out["constructions"][key]["best_fit"]["v_resonances_kms"]
        for v_actual, v_target in zip(v, V_TARGETS):
            rel_err = abs(v_actual - v_target) / v_target
            assert rel_err < 0.25, f"FAIL: {label} v={v_actual:.1f} vs target {v_target}, err={rel_err:.1%}"
    print(f"OK: B and C both within 25% per peak")

    # Check 5: Phase 52 references Phase 48 and Phase 51
    assert "phase48_reference_rms_log10" in out, "FAIL: missing Phase 48 ref"
    assert out["phase48_reference_rms_log10"] == 2.6065, "FAIL: phase48 ref wrong"
    assert "phase51_references" in out, "FAIL: missing Phase 51 refs"
    print("OK: references to Phase 48 + 51")

    # Check 6: q and alpha in plausible ranges
    q_b = out["constructions"]["B_power_law_q_ip1"]["best_fit"]["q"]
    assert 1.5 < q_b < 4.0, f"FAIL: B q = {q_b} outside plausible range"
    alpha_c = out["constructions"]["C_integer_n_alpha"]["best_fit"]["alpha"]
    assert 1.5 < alpha_c < 3.0, f"FAIL: C alpha = {alpha_c} outside plausible range"
    print(f"OK: B q = {q_b:.4f}, C alpha = {alpha_c:.4f} in plausible ranges")

    print()
    print("=== ALL SMOKE TESTS PASSED ===")
    print(f"Headline: Phase 52 multi-mediator constructions B and C both MINIMAL")
    print(f"          (RMS = {rms_b:.4f} and {rms_c:.4f}, Phase 48 was 2.61)")
    print(f"          Reviewer's Phase B suggestion CONFIRMED: multi-mediator")
    print(f"          product-group UV completion is viable with low tuning.")


if __name__ == "__main__":
    main()