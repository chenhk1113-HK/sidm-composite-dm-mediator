"""
Phase 7b — Magnetic-moment LZ forward prediction at v0.3-prelim MAP.

Motivation (per roadmap §Phase 7 task 2)
----------------------------------------
The T90 magnetic-moment branch (wip/tier3-magnetic-moment-LZ) found that
μ_χ = 6.10 × 10⁻⁸ μ_N at m_χ = 1000 GeV matches the LZ 248 keV event
(N_pred ≈ 1) but **breaks** the v0.7 6D SIDM fit (drift 2.69 in log Z,
fail per T116). T110 (global 7D fit) found μ_χ → 0 (Door C CLOSED,
Δlog Z = -10.7).

The Phase 7 roadmap specifies re-testing at the v0.3-prelim MAP
(σ/m₀ = 0.72, a = 1.31, log_ε = -56.11, log_α = -28.05, log Z = -2.94
from T39 Tier-3 4D fit).

The v0.3-prelim MAP is fundamentally different from v0.7 MAP:
- T39 Tier-3 4D phenomenological fit, log Z = -2.94
- vs v0.7 6D composite-DM fit, log Z = -163.29
- σ/m₀ = 0.72 vs σ/m₀_derived = 0.273 (12× higher SIDM cross-section)

The LZ magnetic-moment operator is independent of σ/m₀ and a — it depends
only on (μ_χ, m_χ). So the question is:
- At v0.3-prelim MAP, does μ_χ = 6.10e-8 μ_N still give N_pred ≈ 1?
- Does the v0.3-prelim T39 Tier-3 baseline survive (drift < 1.0)?

Phase 7b answers these two questions sequentially.

Kill criterion (per roadmap §Phase 7):
> "No mediator class (vector/scalar/composite/three-portal) can produce
>  the LZ event at σ_DM-nuc ~10⁻⁴³ cm² while fitting the multi-channel
>  data at v0.3-prelim MAP."
> Action if triggered: Abandon LZ event interpretation; treat LZ as Ch14 constraint.

This is the MAGNETIC-MOMENT half of the kill criterion. Sub-tasks 7a
(composite), 7c (Di Mauro), 7d (T95 stream) are separate scripts.

References
----------
- t39_tier3_epsilon_alpha_joint_fit.py (T39 Tier-3 baseline)
- channels_extended.loglike_lz_magnetic_moment (Channel 26, magnetic-moment LZ)
- T116 sequential check framework (t116_sequential_t90_value.py)
- T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md (T90 ship)
- ROADMAP_MISSING_POSTERIORS_2026_09_12.md §Phase 7 (Phase 7 spec)

Verification
------------
    python phase7b_magnetic_moment_v03_map.py
runs the Phase 7b sequential check and prints the verdict.
"""
from __future__ import annotations
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

# WIMpy is required for loglike_lz_magnetic_moment
VENV_BIN = Path(r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/.venv-sidm-bench/Scripts/python.exe")
if str(VENV_BIN.parent) not in sys.path:
    sys.path.insert(0, str(VENV_BIN.parent))

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Lazy WIMpy import (only required at run time, not at import)
WIMPY_AVAILABLE = False
try:
    from WIMpy import DMUtils as DMU  # noqa: F401
    WIMPY_AVAILABLE = True
except ImportError:
    pass

from t39_tier3_epsilon_alpha_joint_fit import loglike_joint as t39_loglike_joint
from channels_extended import loglike_lz_magnetic_moment


# v0.3-prelim MAP (T39 Tier-3 4D fit)
V03_MAP = {
    "sigma_m_0": 0.720,
    "a": 1.31,
    "log_epsilon": -56.113,
    "log_alpha": -28.047,
    "log_Z_baseline": -2.941,  # integrated log evidence from T39 Tier-3 dynesty fit
}
V03_MAP_THETA = (
    math.log10(V03_MAP["sigma_m_0"]),  # = -0.143
    V03_MAP["a"],                        # = 1.31
    V03_MAP["log_epsilon"],              # = -56.11
    V03_MAP["log_alpha"],                 # = -28.05
)

# T90 magnetic-moment workable value
T90_MU_CHI_MU_N = 6.10e-8
T90_M_CHI_GEV = 1000.0
T90_LOG_Z_PUBLISHED = -163.29  # v0.7 6D fit log Z (for comparison only)

# Phase 7b mass anchors
M_CHI_V03_LIST = [200.0, 500.0, 1000.0, 2000.0]  # sweep m_chi at v0.3-prelim MAP

# Sequential check thresholds (per T116 framework)
DRIFT_THRESHOLD = 2.0       # |log Z drift| < 2.0 = "preserved" (T116 threshold)
N_PRED_LOW = 0.5            # N_pred must be > 0.5 (under-prediction fails)
N_PRED_HIGH = 5.0           # N_pred must be < 5.0 (over-prediction fails)


def compute_lz_magnetic_moment_at_v03_map(m_chi_GeV: float, mu_chi_mu_N: float = T90_MU_CHI_MU_N) -> dict:
    """Compute LZ magnetic-moment contribution at v0.3-prelim MAP.

    Returns a dict with N_pred, log L, and a verdict flag.
    """
    ll_lz_mag = loglike_lz_magnetic_moment(m_chi_GeV, mu_chi_mu_N)
    # Predicted N (re-derive from log L; log L = -N_pred + log(N_pred) when N_obs = 1)
    # Solve: log_likelihood = -N + log(N) for N given log_likelihood.
    # This is monotonic in N for N in [0.5, ...], use bisection
    from scipy.optimize import brentq
    if ll_lz_mag <= -1.0:
        # find N such that -N + log(N) = ll_lz_mag
        try:
            n_pred = brentq(lambda n: -n + math.log(n) - ll_lz_mag, 0.5, 100.0)
        except Exception:
            n_pred = 0.0
    elif ll_lz_mag == 0.0:
        n_pred = 0.0
    else:
        n_pred = float("nan")
    in_range = bool(N_PRED_LOW <= n_pred <= N_PRED_HIGH)
    return {
        "m_chi_GeV": m_chi_GeV,
        "mu_chi_mu_N": mu_chi_mu_N,
        "log_L_lz_mag": float(ll_lz_mag),
        "N_pred": float(n_pred),
        "in_reasonable_range": in_range,
    }


def run_t39_tier3_with_fixed_mu(mu_chi_mu_N: float, m_chi_GeV: float = T90_M_CHI_GEV,
                                 nlive: int = 200) -> dict:
    """Re-run T39 Tier-3 4D fit with LZ magnetic-moment added at FIXED μ_χ.

    Returns integrated log Z from the dynesty fit, plus the per-point log L
    breakdown at MAP.
    """
    print(f"\nRe-running T39 Tier-3 dynesty with μ_χ = {mu_chi_mu_N:.3e} μ_N, m_χ = {m_chi_GeV} GeV")
    print(f"  (nlive = {nlive}; this is the published-style fit, ~30-60s wall)")

    def modified_loglike(theta):
        ll_t39 = t39_loglike_joint(theta)
        if not np.isfinite(ll_t39):
            return -np.inf
        ll_lz_mag = loglike_lz_magnetic_moment(m_chi_GeV, mu_chi_mu_N)
        return ll_t39 + ll_lz_mag

    # Use dynesty directly (same as T39 Tier-3 main)
    import dynesty
    from t39_tier3_epsilon_alpha_joint_fit import prior_transform_4

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=modified_loglike,
        prior_transform=prior_transform_4,
        ndim=4, nlive=nlive, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=0.1, print_progress=False)
    wall = time.time() - t0

    res = sampler.results
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()

    return {
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "wall_seconds": wall,
        "MAP": MAP,
        "log_L_at_MAP": modified_loglike(MAP),
        "log_L_baseline_at_MAP": t39_loglike_joint(MAP),
        "log_L_lz_mag_at_MAP": loglike_lz_magnetic_moment(m_chi_GeV, mu_chi_mu_N),
    }


def main():
    print("=" * 78)
    print("Phase 7b — Magnetic-moment LZ forward prediction at v0.3-prelim MAP")
    print("=" * 78)
    print()
    print(f"v0.3-prelim MAP (T39 Tier-3 4D fit, baseline log Z = {V03_MAP['log_Z_baseline']:.3f}):")
    print(f"  σ/m₀ = {V03_MAP['sigma_m_0']} cm²/g, a = {V03_MAP['a']}")
    print(f"  log ε = {V03_MAP['log_epsilon']:.3f}, log α = {V03_MAP['log_alpha']:.3f}")
    print()
    print(f"T90 magnetic-moment workable value: μ_χ = {T90_MU_CHI_MU_N:.3e} μ_N at m_χ = {T90_M_CHI_GEV} GeV")
    print(f"  (At v0.7 MAP this gives N_pred ≈ 1 but breaks v0.7 baseline per T116.)")
    print()

    if not WIMPY_AVAILABLE:
        print("WARNING: WIMpy not available; cannot compute LZ magnetic-moment log L.")
        print("         Run this script via the .venv-sidm-bench venv Python.")
        return None

    # ---- Step 1: Sweep m_chi at v0.3-prelim MAP with μ_χ = T90 value ----
    print(f"{'='*78}")
    print("STEP 1: Sweep m_chi at v0.3-prelim MAP with μ_χ = T90 workable value")
    print(f"{'='*78}")
    print(f"{'m_chi (GeV)':>12} | {'log L (LZ mag)':>15} | {'N_pred':>8} | {'in [0.5, 5.0]':>14}")
    print("-" * 60)
    sweep_results = []
    for m_chi in M_CHI_V03_LIST:
        ll_lz_mag = loglike_lz_magnetic_moment(m_chi, T90_MU_CHI_MU_N)
        # Direct inversion: log L = -N + log(N) for N_obs=1
        # The function -N + log(N) has its maximum at N=1 (value -1). For ll <= -1,
        # the unique solution is N >= 1; for ll == -1 exactly, N = 1 exactly.
        # For ll == 0.0 (no LZ mag contribution), N_pred = 0.
        from scipy.optimize import brentq
        if ll_lz_mag < -1.0:
            try:
                n_pred = brentq(lambda n: -n + np.log(n) - ll_lz_mag, 1.001, 1000.0)
            except Exception:
                # Fall back: if ll is very negative, N_pred is huge
                n_pred = 100.0
        elif abs(ll_lz_mag + 1.0) < 1e-6:
            n_pred = 1.0  # at the maximum, N_pred = 1
        elif ll_lz_mag == 0.0:
            n_pred = 0.0  # mu_x = 0 → no contribution
        else:
            # ll > -1 means -1 < log L < 0: two solutions (small N below 1, large N above 1)
            # Pick the larger solution (since the operator gives "broad spectrum" at high recoil)
            try:
                n_pred_small = brentq(lambda n: -n + np.log(n) - ll_lz_mag, 0.01, 1.0)
                n_pred = n_pred_small
            except Exception:
                n_pred = 0.0
        in_range = bool(0.5 <= n_pred <= 5.0)
        r = {
            "m_chi_GeV": m_chi,
            "mu_chi_mu_N": T90_MU_CHI_MU_N,
            "log_L_lz_mag": float(ll_lz_mag),
            "N_pred": float(n_pred),
            "in_reasonable_range": in_range,
        }
        sweep_results.append(r)
        print(f"{r['m_chi_GeV']:>12.1f} | {r['log_L_lz_mag']:>15.3f} | {r['N_pred']:>8.3f} | {str(r['in_reasonable_range']):>14}")

    # ---- Step 2: Re-run T39 Tier-3 dynesty with μ_χ fixed at T90 value, m_chi=1000 GeV ----
    print()
    print(f"{'='*78}")
    print(f"STEP 2: Re-run T39 Tier-3 dynesty with μ_χ fixed at T90 value")
    print(f"{'='*78}")
    t39_with_mu = run_t39_tier3_with_fixed_mu(T90_MU_CHI_MU_N, T90_M_CHI_GEV, nlive=200)

    drift = t39_with_mu["log_Z"] - V03_MAP["log_Z_baseline"]
    preservation_pass = abs(drift) < DRIFT_THRESHOLD
    print()
    print(f"  log Z (baseline T39 Tier-3):   {V03_MAP['log_Z_baseline']:.3f}")
    print(f"  log Z (T39 Tier-3 + LZ mag):   {t39_with_mu['log_Z']:.3f} ± {t39_with_mu['log_Z_err']:.3f}")
    print(f"  drift:                          {drift:+.3f}")
    print(f"  preservation (|drift| < {DRIFT_THRESHOLD}): {'PASS' if preservation_pass else 'FAIL'}")
    print(f"  wall: {t39_with_mu['wall_seconds']:.1f}s")

    # ---- Step 3: Tuned μ_χ that gives N_pred ≈ 1 at m_chi=1000 GeV ----
    print()
    print(f"{'='*78}")
    print(f"STEP 3: Find μ_χ that gives N_pred ≈ 1 at m_chi=1000 GeV")
    print(f"{'='*78}")
    from scipy.optimize import brentq

    def n_pred_minus_one(log_mu_x):
        mu_x = 10 ** log_mu_x
        ll = loglike_lz_magnetic_moment(T90_M_CHI_GEV, mu_x)
        if ll <= -1.0:
            try:
                n = brentq(lambda n: -n + math.log(n) - ll, 0.5, 100.0)
                return n - 1.0
            except Exception:
                return 100.0
        return 100.0  # way off

    # The buggy block below has been replaced by the proper scan in Step 3 below.
    # log_mu_x_tuned = brentq(n_pred_minus_one, -10, -4)
    # mu_x_tuned = 10 ** log_mu_x_tuned
    # ll_at_tuned = loglike_lz_magnetic_moment(T90_M_CHI_GEV, mu_x_tuned)
    # n_pred_at_tuned = brentq(lambda n: -n + math.log(n) - ll_at_tuned, 0.5, 100.0) if ll_at_tuned <= -1.0 else 0
    # print(f"  tuned μ_χ = {mu_x_tuned:.3e} μ_N gives N_pred ≈ {n_pred_at_tuned:.3f}")
    # print(f"  (for comparison, T90 value was {T90_MU_CHI_MU_N:.3e})")

    # ---- Step 3: Tuned μ_χ that gives N_pred ≈ 1 at m_chi=1000 GeV ----
    print()
    print(f"{'='*78}")
    print(f"STEP 3: Find μ_χ that gives N_pred ≈ 1 at m_chi=1000 GeV")
    print(f"{'='*78}")
    from scipy.optimize import brentq

    mu_x_tuned = float("nan")
    n_pred_at_tuned = float("nan")
    try:
        # Search over a wide range; use root-finding on (N_pred - 1) via the inverted Poisson.
        def n_pred_from_mu(log_mu_x):
            mu_x = 10 ** log_mu_x
            ll = loglike_lz_magnetic_moment(T90_M_CHI_GEV, mu_x)
            if ll < -1.0:
                try:
                    return brentq(lambda n: -n + np.log(n) - ll, 1.001, 1000.0)
                except Exception:
                    return float("nan")
            elif abs(ll + 1.0) < 1e-6:
                return 1.0
            elif ll == 0.0:
                return 0.0
            return float("nan")

        # Scan to find sign change in (N_pred - 1) over log_mu_x
        log_mu_x_grid = np.linspace(-12, -3, 50)
        n_preds = np.array([n_pred_from_mu(x) for x in log_mu_x_grid])
        # Filter NaN
        valid = np.isfinite(n_preds)
        if valid.sum() >= 2 and (n_preds[valid].min() < 1.0 < n_preds[valid].max()):
            # Find sign change around 1.0
            sign_changes = np.where(np.diff(np.sign(n_preds[valid] - 1.0)) != 0)[0]
            if len(sign_changes) > 0:
                idx = sign_changes[0]
                log_mu_x_tuned = brentq(
                    lambda lx: n_pred_from_mu(lx) - 1.0,
                    log_mu_x_grid[valid][idx], log_mu_x_grid[valid][idx + 1],
                )
                mu_x_tuned = 10 ** log_mu_x_tuned
                n_pred_at_tuned = n_pred_from_mu(log_mu_x_tuned)
                print(f"  tuned μ_χ = {mu_x_tuned:.3e} μ_N gives N_pred ≈ {n_pred_at_tuned:.3f}")
                print(f"  (for comparison, T90 value was {T90_MU_CHI_MU_N:.3e})")
            else:
                print(f"  No sign change in N_pred - 1 over scan; skipping tuning step.")
        else:
            print(f"  N_pred scan did not bracket 1.0; skipping tuning step.")
            print(f"  N_pred grid: min = {n_preds[valid].min():.3f}, max = {n_preds[valid].max():.3f}" if valid.any() else "  All N_pred values are NaN.")
    except Exception as e:
        print(f"  Step 3 failed: {e}")
        print(f"  Skipping tuning step (verdict can still be reached from Step 1+2).")

    # ---- Step 4: Verdict ----
    print()
    print(f"{'='*78}")
    print(f"VERDICT (Phase 7b, magnetic-moment at v0.3-prelim MAP)")
    print(f"{'='*78}")
    kill_triggered = (not preservation_pass) or (not any(r["in_reasonable_range"] for r in sweep_results))
    if kill_triggered:
        print(f"  KILL CRITERION TRIGGERED — magnetic-moment CANNOT explain LZ event at v0.3-prelim MAP.")
        if not preservation_pass:
            print(f"    Reason 1: T39 Tier-3 baseline log Z drifts by {drift:+.3f} (threshold |drift| < {DRIFT_THRESHOLD})")
        if not any(r["in_reasonable_range"] for r in sweep_results):
            print(f"    Reason 2: No m_chi in [200, 2000] GeV gives N_pred in [0.5, 5.0] at μ_χ = {T90_MU_CHI_MU_N:.3e}")
        print()
        print("  Per roadmap §Phase 7: 'Action if triggered: Abandon LZ event interpretation;")
        print("  treat LZ as Ch14 constraint.'")
    else:
        print(f"  KILL CRITERION NOT TRIGGERED — magnetic-moment IS workable at v0.3-prelim MAP.")
        print(f"    T39 Tier-3 baseline preserved (drift {drift:+.3f}).")
        print(f"    At least one m_chi gives N_pred in [0.5, 5.0].")
        print(f"    tuned μ_χ = {mu_x_tuned:.3e} μ_N at m_chi = {T90_M_CHI_GEV} GeV gives N_pred ≈ {n_pred_at_tuned:.3f}.")
        print()
        print(f"  This is the ONLY remaining sub-task with a non-trivial prior for survival.")
        print(f"  Phase 7b outcome: magnetic-moment interpretation viable at v0.3-prelim MAP.")

    # ---- Save results ----
    result = {
        "phase": "7b",
        "date": "2026-09-13",
        "title": "Magnetic-moment LZ forward prediction at v0.3-prelim MAP",
        "v03_MAP": V03_MAP,
        "v03_MAP_theta": list(V03_MAP_THETA),
        "t90_reference": {
            "mu_chi_mu_N": T90_MU_CHI_MU_N,
            "m_chi_GeV": T90_M_CHI_GEV,
            "log_Z_v07_published": T90_LOG_Z_PUBLISHED,
        },
        "step_1_sweep": sweep_results,
        "step_2_t39_with_fixed_mu": t39_with_mu,
        "step_2_drift": drift,
        "step_2_preservation_pass": preservation_pass,
        "step_3_tuned": {
            "mu_chi_mu_N": float(mu_x_tuned),
            "N_pred": float(n_pred_at_tuned),
        },
        "kill_triggered": kill_triggered,
        "decision": (
            "KILL — magnetic-moment sub-task triggers kill criterion at v0.3-prelim MAP"
            if kill_triggered else
            "PROCEED — magnetic-moment IS workable at v0.3-prelim MAP, kill criterion NOT triggered"
        ),
        "wimpy_available": WIMPY_AVAILABLE,
    }

    out_path = SCRIPT_DIR.parent / "data" / "results" / "phase7b_magnetic_moment_v03_map.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print()
    print(f"Results written to: {out_path}")
    return result


if __name__ == "__main__":
    main()
