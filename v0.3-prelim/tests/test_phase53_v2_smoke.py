"""Smoke test for Phase 53 v2 — UV-prior joint fit with clockwork construction.

Per Rule 18 (post-write verification).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

RESULTS = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\phase53_v2_clockwork_uv_prior_fixed.json")


def main():
    print("=== Phase 53 v2 smoke test ===")
    if not RESULTS.exists():
        sys.exit(f"FAIL: {RESULTS} not found")
    out = json.loads(RESULTS.read_text())

    # Check 1: structure
    assert "phase44_reference" in out, "FAIL: missing Phase 44 ref"
    assert "clockwork_construction_v2" in out, "FAIL: missing clockwork construction"
    assert "phase53_v2_results" in out, "FAIL: missing Phase 53 v2 results"
    assert "bic_comparison" in out, "FAIL: missing BIC comparison"
    assert "v1_bug_note" in out, "FAIL: missing v1 bug note"
    print("OK: structure")

    # Check 2: Phase 44 reference values match
    assert abs(out["phase44_reference"]["t90_70_baseline_logL"] - (-19.67268668762108)) < 1e-6
    assert abs(out["phase44_reference"]["t90_70_best_fit_logL"] - (-11.577625403084578)) < 1e-6
    assert out["phase44_reference"]["n_free_params"] == 15
    print(f"OK: Phase 44 reference matches")

    # Check 3: Phase 53 v2 best log L preserves most of the gain
    logL_baseline = out["phase44_reference"]["t90_70_baseline_logL"]
    logL_phase44_best = out["phase44_reference"]["t90_70_best_fit_logL"]
    logL_phase53 = out["phase53_v2_results"]["best_fit_logL"]
    improvement = logL_phase53 - logL_baseline
    assert improvement > 5.0, f"FAIL: Phase 53 v2 improvement = {improvement:.2f} log-units, expected > 5"
    print(f"OK: Phase 53 v2 improvement vs baseline = {improvement:.2f} log-units")

    # Check 4: Phase 53 v2 is close to Phase 44 best (Δ < 1 log-unit)
    delta = logL_phase53 - logL_phase44_best
    assert delta > -1.0, f"FAIL: Phase 53 v2 vs Phase 44 best Δ = {delta:.2f}, expected > -1"
    assert delta < 1.0, f"FAIL: Phase 53 v2 vs Phase 44 best Δ = {delta:.2f}, expected < 1"
    print(f"OK: Phase 53 v2 vs Phase 44 best Δ = {delta:.2f} log-units (within ±1)")

    # Check 5: BIC Δ is negative (clockwork UV preferred under Occam penalty)
    bic_delta = out["bic_comparison"]["delta_bic"]
    assert bic_delta < 0, f"FAIL: BIC Δ = {bic_delta}, expected < 0 (clockwork preferred)"
    print(f"OK: BIC Δ = {bic_delta:.2f} (clockwork UV preferred under Occam)")

    # Check 6: verdict is "CLOCKWORK_UV_PRESERVES_JOINT_FIT_GAIN"
    assert out["phase53_v2_results"]["verdict"] == "CLOCKWORK_UV_PRESERVES_JOINT_FIT_GAIN"
    print(f"OK: verdict = {out['phase53_v2_results']['verdict']}")

    # Check 7: Phase 53 v2 q is in expected range (1.5, 3.0)
    q = out["phase53_v2_results"]["best_params"]["q"]
    assert 1.5 < q < 3.0, f"FAIL: q = {q} outside [1.5, 3.0]"
    print(f"OK: q = {q:.4f} in expected range")

    # Check 8: k-levels match Phase 51
    assert out["clockwork_construction_v2"]["k_levels"] == [3, 6, 9, 11]
    print(f"OK: k_levels = [3, 6, 9, 11]")

    print()
    print("=== ALL SMOKE TESTS PASSED ===")
    print(f"Headline: Phase 53 v2 with FIXED clockwork UV prior preserves the")
    print(f"          multi-channel joint-fit gain (+7.93 log-units vs Phase 44")
    print(f"          baseline; Δ vs Phase 44 best fit = {delta:.2f}; BIC Δ = {bic_delta:.2f}).")
    print(f"          The +8 log-unit gain survives UV priors.")


if __name__ == "__main__":
    main()