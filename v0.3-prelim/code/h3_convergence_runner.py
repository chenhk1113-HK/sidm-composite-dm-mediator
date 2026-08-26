"""H3 closure: Sampler convergence test (R13 review).

Per REVIEWER_AUDIT_R13.md H3:
  'Run main analysis with at least two different nlive values; compare
   posterior contours. Report whether contours are stable. Add this
   result to documentation.'

Implementation: re-run T41 with nlive = {200, 500, 1000}, compare:
  - log_Z (should be stable across nlive to within dlogz = 0.10)
  - MAP position (should not drift)
  - Posterior median (should be stable)
  - Posterior width (should narrow with nlive as expected)

Usage:
  python v0.3-prelim/code/h3_convergence_runner.py [--nlive 200 500 1000]
                                                    [--dlogz 0.10]

Output:
  v0.3-prelim/data/results/h3_convergence_*.json (one per nlive)
  v0.3-prelim/data/results/h3_convergence_summary.json (aggregated)
"""
from __future__ import annotations
import argparse
import json
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


def run_one_nlive(nlive: int, dlogz: float = 0.10) -> dict:
    """Run T41 with a specific nlive, return the summary."""
    print(f"\n{'='*60}")
    print(f"  H3: running T41 with nlive={nlive}, dlogz={dlogz}")
    print(f"{'='*60}")
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
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    med = {k: float(t41.weighted_median(samples[:, i], weights))
           for i, k in enumerate(["log_m_phi_MeV", "log_m_chi_GeV", "g_chi",
                                   "log_epsilon", "log_alpha"])}

    summary = {
        "nlive": nlive,
        "dlogz": dlogz,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": MAP,
        "median": med,
        "wall_seconds": wall,
        "n_iterations": len(res.logz),
    }
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nlive", type=int, nargs="+", default=[200, 500, 1000])
    parser.add_argument("--dlogz", type=float, default=0.10)
    args = parser.parse_args()

    summaries = []
    for nlive in args.nlive:
        summary = run_one_nlive(nlive, args.dlogz)
        out_path = t41.RESULTS_DIR / f"h3_convergence_nlive{nlive}.json"
        out_path.write_text(json.dumps(summary, indent=2))
        print(f"  -> wrote {out_path} (log_Z = {summary['log_Z']:.3f}, "
              f"wall = {summary['wall_seconds']:.1f}s)")
        summaries.append(summary)

    # Aggregate comparison
    if len(summaries) >= 2:
        log_Zs = np.array([s["log_Z"] for s in summaries])
        log_Z_stable = (log_Zs.max() - log_Zs.min()) <= args.dlogz
        med_keys = list(summaries[0]["median"].keys())
        med_diffs = {k: max(abs(s["median"][k] - summaries[0]["median"][k])
                            for s in summaries)
                     for k in med_keys}
        n_iterations = [s["n_iterations"] for s in summaries]

        agg = {
            "test": "H3_convergence_test",
            "nlive_values": args.nlive,
            "dlogz_target": args.dlogz,
            "log_Z_values": log_Zs.tolist(),
            "log_Z_max_minus_min": float(log_Zs.max() - log_Zs.min()),
            "log_Z_stable_to_dlogz": bool(log_Z_stable),
            "median_max_drift": med_diffs,
            "n_iterations": n_iterations,
            "n_iterations_scale": (n_iterations[-1] / n_iterations[0]) if n_iterations[0] > 0 else None,
            "verdict": "STABLE" if log_Z_stable else "UNSTABLE",
            "interpretation": (
                f"log_Z across nlive={args.nlive}: {log_Zs.tolist()}. "
                f"Range = {log_Zs.max() - log_Zs.min():.3f}, target = {args.dlogz}. "
                f"{'STABLE: posterior evidence converged within dlogz.' if log_Z_stable else 'UNSTABLE: posterior evidence did NOT converge.'}"
            ),
        }
    else:
        agg = {"test": "H3_convergence_test", "summaries": summaries}

    out_path = t41.RESULTS_DIR / "h3_convergence_summary.json"
    out_path.write_text(json.dumps(agg, indent=2))
    print(f"\n  -> wrote {out_path}")
    print(f"  log_Z stable to dlogz={args.dlogz}? {agg.get('log_Z_stable_to_dlogz', 'N/A')}")


if __name__ == "__main__":
    main()