"""T41 v0.7 — 7D joint fit with magnetic-magnetic-moment μ_x as free parameter.

This is the T90.1 Phase C ship — Reviewer 1 caveat C1:
"μ_x is tuned by hand, not fitted. A proper Bayesian comparison would
require promoting it to a free parameter and re-running a higher-dimensional
nested sampling."

Approach:
- Inherits the canonical 6D T41 joint fit (loglike_joint + prior_transform_6).
- Adds log_mu_x as the 7th dimension. The 7D prior transform maps a uniform
  u[6] to log_mu_x in the wide prior range [-15, -4] (μ_x in [10⁻¹⁵, 10⁻⁴] μ_N).
- The 7D loglike wraps the 6D loglike_joint and sets the env var
  T90_MAGNETIC_MOMENT_MU_X from the 7th theta element so that the existing
  Channel 26 wiring in t41_mediator_mass_joint_fit.loglike_joint fires with
  the sampled μ_x.

This script does NOT modify the canonical 6D T41 main run on master — it is
a Tier-3 branch experiment. To run:

    export T90_MAGNETIC_MOMENT_MU_X=$(env | grep -v T90 | head -1)  # placeholder
    .venv-sidm-bench/Scripts/python.exe t41_v07_magnetic_moment_7d.py

Default nlive=200 (matches canonical T41 for fair comparison).

Wall time budget (per T90 Phase 3): ~5-30 min at nlive=200.

Output: t41_v07_7d_results.json + t41_v07_7d_posterior.h5 in
        v0.3-prelim/outputs/t90/

Reviewer 1 caveat C1 addressed.
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Make t41 importable
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))

import t41_mediator_mass_joint_fit as t41
from dynesty import NestedSampler

# 7D prior transform — adds log_mu_x as the 7th parameter.
# log_mu_x range: [-15, -4] → μ_x in [10⁻¹⁵, 10⁻⁴] μ_N.
# The lower bound (10⁻¹⁵ μ_N ≈ 5×10⁻¹⁸ μ_B) is well below the magnetic-moment
# operator's expected reach. The upper bound (10⁻⁴ μ_N ≈ 5×10⁻⁷ μ_B) is above
# the published XENONnT/PandaX bounds (~10⁻¹⁰ μ_B at 1 TeV); values above
# this are essentially excluded by data, so the prior beyond it contributes
# nothing to the posterior.
LOG_MU_X_RANGE = (-15.0, -4.0)


def prior_transform_7(u):
    """7D prior transform (T90.1, T41 v0.7).

    theta = (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon,
             log_alpha, log_xi, log_mu_x)

    The first 6 dimensions match t41.prior_transform_6 exactly. The 7th
    dimension (log_mu_x) is uniform in the prior range [-15, -4].
    """
    if len(u) != 7:
        raise ValueError(f"prior_transform_7 expects 7-D u, got {len(u)}")
    # Reuse the canonical 6D transform
    theta_6 = t41.prior_transform_6(list(u[:6]))
    # Append log_mu_x
    log_mu_x = LOG_MU_X_RANGE[0] + u[6] * (LOG_MU_X_RANGE[1] - LOG_MU_X_RANGE[0])
    return theta_6 + [log_mu_x]


def loglike_joint_7d(theta):
    """7D log-likelihood wrapper.

    Reads log_mu_x from theta[6], converts to mu_x (in μ_N), sets the
    env var T90_MAGNETIC_MOMENT_MU_X, then calls the 6D loglike_joint.

    The 6D loglike_joint already handles the env-var gating (returns 0
    if T90_MAGNETIC_MOMENT_MU_X is unset, computes Poisson loglike if set).
    """
    if len(theta) != 7:
        raise ValueError(f"loglike_joint_7d expects 7-D theta, got {len(theta)}")
    log_mu_x = theta[6]
    mu_x = 10.0 ** log_mu_x
    # Set env var for the duration of this call. We use os.environ
    # because the 6D loglike_joint reads it at call time.
    os.environ["T90_MAGNETIC_MOMENT_MU_X"] = repr(mu_x)
    try:
        ll = t41.loglike_joint(theta[:6])
    finally:
        # Don't unset; let the next call set its own value. But
        # explicitly unset to keep master behavior intact for any
        # subsequent test or import.
        os.environ.pop("T90_MAGNETIC_MOMENT_MU_X", None)
    return ll


def main():
    print("=" * 80)
    print("T41 v0.7 — 7D joint fit with magnetic-moment μ_x as free parameter")
    print("=" * 80)
    print("7 parameters (T90.1: log_mu_x promoted from fixed to free):")
    print("  log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha, ")
    print("  log_xi, log_mu_x")
    print(f"  log_mu_x:      [{LOG_MU_X_RANGE[0]}, {LOG_MU_X_RANGE[1]}]")
    print(f"    (mu_x in [1e-15, 1e-4] μ_N; wide range covering current bounds)")
    print()

    nlive = int(os.environ.get("T41_NLIVE", "200"))
    print(f"nlive={nlive} (matches canonical T41 for fair 7D vs 6D comparison)")
    print(f"prior_transform_7 + loglike_joint_7d")
    print()

    t0 = time.time()
    sampler = NestedSampler(
        loglikelihood=loglike_joint_7d,
        prior_transform=prior_transform_7,
        ndim=7,
        nlive=nlive,
        bound="multi",
        sample="auto",
        bootstrap=0,
    )
    sampler.run_nested(dlogz=0.1)
    elapsed = time.time() - t0

    res = sampler.results
    final_logz = float(res.logz[-1])
    final_logzerr = float(res.logzerr[-1])
    final_info = float(res.information[-1])
    print()
    print("=" * 80)
    print("T41 v0.7 7D results")
    print("=" * 80)
    print(f"Wall time:        {elapsed:.1f} sec ({elapsed/60:.2f} min)")
    print(f"log Z (evidence): {final_logz:.3f} ± {final_logzerr:.3f}")
    print(f"log Z (info):     {final_info:.3f}")
    print()

    # MAP estimate from samples
    log_w = res.logwt - res.logwt.max()
    w = np.exp(log_w)
    w /= w.sum()
    samples_equal = res.samples  # importance-sampled
    median = np.array([
        np.median(samples_equal[:, k])
        for k in range(7)
    ])
    print("Median (log-space):")
    labels = [
        "log_m_phi_MeV", "log_m_chi_GeV", "g_chi", "log_epsilon",
        "log_alpha", "log_xi", "log_mu_x",
    ]
    for k, label in enumerate(labels):
        print(f"  {label:<16} = {median[k]:.3f}")
    print()
    print(f"  -> mu_x median = 10^{median[6]:.2f} mu_N = {10**median[6]:.2e} mu_N")
    print(f"  -> mu_x median in mu_B = {10**median[6]/1836.15267:.2e} mu_B")
    print()

    # Save results
    out_dir = _THIS_DIR.parent / "outputs" / "t90"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "tier": "T90.1",
        "phase": "C",
        "run_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "nlive": nlive,
        "ndim": 7,
        "wall_time_sec": elapsed,
        "log_evidence": final_logz,
        "log_evidence_err": final_logzerr,
        "log_evidence_info": final_info,
        "median_params": {
            labels[k]: float(median[k]) for k in range(7)
        },
        "mu_x_median_muN": float(10 ** median[6]),
        "mu_x_median_muB": float(10 ** median[6] / 1836.15267),
        "prior_range_log_mu_x": list(LOG_MU_X_RANGE),
    }
    out_json = out_dir / "t41_v07_7d_results.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote: {out_json}")

    # Save posterior samples (NumPy .npz — no h5py dependency)
    try:
        out_npz = out_dir / "t41_v07_7d_posterior.npz"
        np.savez(
            out_npz,
            samples=samples_equal,
            log_weights=res.logwt,
            log_evidence_per_iter=res.logz,
            labels=np.array(labels, dtype=object),
        )
        print(f"Wrote: {out_npz}")
    except Exception as e:
        print(f"Posterior save failed: {e}")

    return summary


if __name__ == "__main__":
    main()