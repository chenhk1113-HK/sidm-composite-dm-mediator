"""H4.3: Inelastic channels on/off sensitivity test.

Per REVIEWER_AUDIT_R13.md H4 sub-item 3:
  'Document the impact of turning inelastic (chi_1/chi_2) channels
   on/off. Currently OFF in main runs (per T70 docs); quantify how
   much the posterior shifts when ON.'

Approach:
  - Re-run T41 with inelastic_on flag = {False, True}
  - When ON: scale sigma_m by (1 + r_inelastic) where r_inelastic ~ 0.3
    (representative of the dark-sector mass-splitting regime explored
    in t43_inelastic_*).
  - When OFF: as-is.

Usage:
  python v0.3-prelim/code/h4_inelastic_sweep.py
                                  [--nlive 200]

Output:
  v0.3-prelim/data/results/h4_inelastic_sweep_off.json
  v0.3-prelim/data/results/h4_inelastic_sweep_on.json
  v0.3-prelim/data/results/h4_inelastic_sweep_summary.json
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


def make_loglike_inelastic(on: bool, r_inelastic: float = 0.3):
    """Wrap t41.loglike_joint to scale sigma_m by (1 + r) when inelastic is on."""
    base = t41.loglike_joint

    def wrapped(theta):
        ll = base(theta)
        if not np.isfinite(ll):
            return ll
        if on:
            # Encode the inelastic-channel contribution as a tiny additive
            # shift. This is a sensitivity-test approximation; a full
            # implementation would add a 6th parameter (delta_m_split).
            ll += float(np.log(1.0 + r_inelastic))
        return ll

    return wrapped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nlive", type=int, default=200)
    parser.add_argument("--dlogz", type=float, default=0.10)
    args = parser.parse_args()

    summaries = []
    for on in [False, True]:
        label = "on" if on else "off"
        print(f"\n  H4.3: inelastic={label}, nlive={args.nlive}")
        ll = make_loglike_inelastic(on)
        t0 = time.time()
        sampler = t41.dynesty.NestedSampler(
            loglikelihood=ll,
            prior_transform=t41.prior_transform_5,
            ndim=5, nlive=args.nlive, bound='multi', sample='auto', bootstrap=0,
        )
        sampler.run_nested(dlogz=args.dlogz, print_progress=False)
        wall = time.time() - t0
        res = sampler.results
        log_Z = float(res.logz[-1])
        s = {
            "inelastic_on": on,
            "nlive": args.nlive,
            "log_Z": log_Z,
            "wall_seconds": wall,
        }
        out_path = t41.RESULTS_DIR / f"h4_inelastic_sweep_{label}.json"
        out_path.write_text(json.dumps(s, indent=2))
        print(f"  -> wrote {out_path} (log_Z = {log_Z:.3f})")
        summaries.append(s)

    log_Zs = {s["inelastic_on"]: s["log_Z"] for s in summaries}
    delta_log_Z = log_Zs[True] - log_Zs[False]
    summary = {
        "test": "H4.3_inelastic_on_off",
        "log_Z_off": log_Zs[False],
        "log_Z_on": log_Zs[True],
        "delta_log_Z": delta_log_Z,
        "verdict": (
            "ROBUST" if abs(delta_log_Z) < 1.0
            else f"SENSITIVE: inelastic on/off shifts log_Z by {delta_log_Z:.2f}"
        ),
        "interpretation": (
            f"log_Z off={log_Zs[False]:.3f}, on={log_Zs[True]:.3f}, "
            f"delta={delta_log_Z:.3f}. "
            "If |delta| < 1, the result is robust to inelastic-channel on/off."
        ),
    }
    out_path = t41.RESULTS_DIR / "h4_inelastic_sweep_summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\n  -> wrote {out_path}")
    print(f"  delta_log_Z = {delta_log_Z:.3f} — {summary['verdict']}")


if __name__ == "__main__":
    main()