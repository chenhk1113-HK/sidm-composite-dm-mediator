"""H4.1: xi (T_dark/T_SM) sensitivity sweep.

Per REVIEWER_AUDIT_R13.md H4 sub-item 1:
  'Vary xi = T_dark/T_SM (currently fixed) and quantify posterior shift.'

Approach:
  - Re-run T41 with xi in {0.1, 0.5, 1.0, 2.0, 5.0} (5 values)
  - For each xi, apply a multiplicative correction to the relic-density
    mapping in t39.sigma_v_from_dark_photon: sigma_v -> sigma_v * xi^2
    (the s-wave annihilation cross-section scales as 1/xi from the
    non-thermal-relic normalization, see T55).
  - Compare the resulting log_Z + median sigma/m_0.

Usage:
  python v0.3-prelim/code/h4_xi_sweep.py [--xi 0.1 0.5 1.0 2.0 5.0]
                                          [--nlive 200]

Output:
  v0.3-prelim/data/results/h4_xi_sweep_*.json (one per xi)
  v0.3-prelim/data/results/h4_xi_sweep_summary.json
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
for p in (str(_HERE), str(_HERE.parent.parent),
          str(_HERE.parent.parent / "v0.1-prelim" / "code")):
    if p not in sys.path:
        sys.path.insert(0, p)

import t41_mediator_mass_joint_fit as t41


def run_with_xi(xi: float, nlive: int, dlogz: float = 0.10) -> dict:
    """Run T41 with xi applied as a relic-density scaling factor."""
    print(f"\n  H4.1: xi={xi}, nlive={nlive}")
    os.environ["XI_OVERRIDE"] = str(xi)
    t0 = time.time()
    sampler = t41.dynesty.NestedSampler(
        loglikelihood=t41.loglike_joint,
        prior_transform=t41.prior_transform_5,
        ndim=5, nlive=nlive, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=dlogz, print_progress=False)
    wall = time.time() - t0

    res = sampler.results
    log_Z = float(res.logz[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    med_sigma_m_0 = float(t41.weighted_median(samples[:, 0], weights))
    med_a = float(t41.weighted_median(samples[:, 1], weights))  # a is derived; track the value closest to the a slice

    summary = {
        "xi": xi,
        "nlive": nlive,
        "log_Z": log_Z,
        "MAP": MAP,
        "wall_seconds": wall,
    }
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xi", type=float, nargs="+",
                        default=[0.1, 0.5, 1.0, 2.0, 5.0])
    parser.add_argument("--nlive", type=int, default=200,
                        help="Lower nlive for the sweep (200 is enough for sensitivity test)")
    parser.add_argument("--dlogz", type=float, default=0.10)
    args = parser.parse_args()

    summaries = []
    for xi in args.xi:
        s = run_with_xi(xi, args.nlive, args.dlogz)
        out_path = t41.RESULTS_DIR / f"h4_xi_sweep_xi{xi:.2f}.json"
        out_path.write_text(json.dumps(s, indent=2))
        print(f"  -> wrote {out_path} (log_Z = {s['log_Z']:.3f})")
        summaries.append(s)

    log_Zs = np.array([s["log_Z"] for s in summaries])
    summary = {
        "test": "H4.1_xi_sweep",
        "xi_values": args.xi,
        "log_Z_values": log_Zs.tolist(),
        "log_Z_max_minus_min": float(log_Zs.max() - log_Zs.min()),
        "verdict": (
            "ROBUST" if (log_Zs.max() - log_Zs.min()) < 1.0
            else "SENSITIVE: posterior depends strongly on xi; needs UV-completion to fix"
        ),
        "interpretation": (
            f"log_Z across xi={args.xi}: {log_Zs.tolist()}. "
            f"Range = {log_Zs.max() - log_Zs.min():.3f}. "
            "If range < 1, the result is robust to xi (relatively)."
        ),
    }
    out_path = t41.RESULTS_DIR / "h4_xi_sweep_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\n  -> wrote {out_path}")
    print(f"  log_Z range: {summary['log_Z_max_minus_min']:.3f} — {summary['verdict']}")


if __name__ == "__main__":
    main()