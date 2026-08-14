#!/usr/bin/env python
"""
v0.3 T18 — Direction B joint fit: 4-parameter two-component (mass-segregated) SIDM.

=============================================================================
!! PLACEHOLDER LIKELIHOODS — NOT A PUBLICATION-QUALITY RESULT !!
=============================================================================
This fit uses the three simplified proxy channels defined in
`two_component_sidm.py` (dwarf-core Gaussian, one-sided cluster bound,
one-sided mass-segregation requirement). They are hand-built stand-ins for
real published posteriors. The log Z values and Bayes factors reported here
are a *plumbing / feasibility check* of the Direction B parameter space, NOT
evidence for or against two-component SIDM.
=============================================================================

Model (Yang, Fan, Hou & Tsai 2026, Sci. Bull., DOI 10.1016/j.scib.2026.01.077,
arXiv:2504.02303): two DM species with different masses; the heavier one is
strongly self-interacting (makes dwarf cores) and the lighter one is weakly
self-interacting (respects cluster / lensing bounds). Mass segregation
up-weights the heavy component at dwarf velocities.

Fitted parameters (4):
    log10 sigma1  in (-2, 2)      component-1 cross-section at v_ref=100 km/s
    log10 sigma2  in (-3, 1)      component-2 cross-section at v_ref
    f1            in (0.01, 0.99) mass fraction in component 1
    a             in (-2, 2)      shared velocity power-law index

Three evidences are computed and compared:

  (A) 2-component, 4 params, 3 placeholder channels          <- the new model
  (B) 1-component nested reference: same 3 channels but with
      sigma1 == sigma2 enforced (2 params: log sigma, a).
      This is the STATISTICALLY VALID nested comparison for (A), but note it
      is partly circular: the segregation channel *encodes* the Yang+ 2026
      requirement sigma1 > 10 sigma2, which sigma1 == sigma2 can never meet.
  (C) 1-component, 2 channels only (dwarf + cluster, no segregation channel;
      2 params). This asks the honest physics question: can ONE velocity-
      dependent cross-section satisfy both placeholder constraints at once?
      Comparing (A) to (C) is not a strict Bayes factor (different channel
      sets), so it is reported as a diagnostic only.

Also reported: the difference against the v0.3 5-channel single-component
fit (t8_v03_posterior.json). That comparison is INCOMMENSURATE — t8 uses a
different (partly real, partly calibrated) channel set with different
absolute normalisation — and is reported only because the project brief asks
for it. Treat it as a magnitude sanity check, not a Bayes factor.

Reuses t8_v03_joint_fit.py as the structural template.
No new dependencies (numpy + dynesty; falls back to grid quadrature if
dynesty is unavailable).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_CODE_DIR))

import two_component_sidm as tcs  # noqa: E402

# Paths are derived from __file__ so the script runs identically from the
# Windows checkout, from /mnt/c under WSL, and from a native WSL clone.
_V03_DIR = _CODE_DIR.parent
RESULTS_DIR = _V03_DIR / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

T8_POSTERIOR = RESULTS_DIR / "t8_v03_posterior.json"

NLIVE = 200      # 4-D space; 500 is unnecessarily slow, 200 converges fine
DLOGZ = 0.10

# Single-component reference priors: exactly the 2-component prior restricted
# to the sigma1 == sigma2 surface.
SINGLE_LOG_SIGMA_RANGE = tcs.LOG_SIGMA1_RANGE
SINGLE_A_RANGE = tcs.A_RANGE


# ---------------------------------------------------------------------------
# Likelihoods
# ---------------------------------------------------------------------------
def loglike_2comp(theta) -> float:
    """4-param two-component log L (3 placeholder channels)."""
    return tcs.loglike_theta(theta)


def loglike_1comp_nested(theta) -> float:
    """2-param single-component log L, SAME 3 channels, sigma1 == sigma2."""
    log_s, a = float(theta[0]), float(theta[1])
    return tcs.loglike_theta((log_s, log_s, 0.5, a))


def loglike_1comp_2channel(theta) -> float:
    """2-param single-component log L, dwarf + cluster channels only."""
    log_s, a = float(theta[0]), float(theta[1])
    sigma = 10.0 ** log_s
    sd = tcs.sigma_at_v(sigma, a, tcs.V_DWARF)
    sc = tcs.sigma_at_v(sigma, a, tcs.V_CLUSTER)
    ll = float(tcs.loglike_dwarf(sd)) + float(tcs.loglike_cluster(sc))
    return ll if np.isfinite(ll) else -1.0e300


def make_prior_transform(ranges):
    lo = np.array([r[0] for r in ranges], dtype=float)
    hi = np.array([r[1] for r in ranges], dtype=float)

    def prior_transform(u):
        return lo + np.asarray(u, dtype=float) * (hi - lo)

    return prior_transform


# ---------------------------------------------------------------------------
# Samplers
# ---------------------------------------------------------------------------
def _grid_logz(loglike_fn, ranges, n_per_dim: int):
    """Uniform-prior midpoint quadrature: log Z = log <L>_prior."""
    axes = []
    for lo, hi in ranges:
        edges = np.linspace(lo, hi, n_per_dim + 1)
        axes.append(0.5 * (edges[:-1] + edges[1:]))
    mesh = np.meshgrid(*axes, indexing="ij")
    pts = np.column_stack([m.ravel() for m in mesh])
    ll = np.array([loglike_fn(p) for p in pts], dtype=float)
    ll = np.where(ll > -1.0e299, ll, -np.inf)
    finite = np.isfinite(ll)
    if not finite.any():
        raise RuntimeError("grid: no finite likelihood")
    ll_max = float(ll[finite].max())
    log_Z = ll_max + float(np.log(np.exp(ll - ll_max).sum() / ll.size))
    w = np.exp(ll - ll_max)
    w /= w.sum()
    return {
        "log_Z": log_Z,
        "log_Z_err": float("nan"),
        "loglike_max": ll_max,
        "samples": pts,
        "weights": w,
        "sampler": f"grid_quadrature_{n_per_dim}^{len(ranges)}",
        "wall_seconds": 0.0,
    }


def run_fit(loglike_fn, ranges, nlive: int, label: str,
            grid_fallback_n: int = 21, verbose: bool = True):
    """Run a dynesty nested-sampling fit; fall back to grid quadrature."""
    ndim = len(ranges)
    try:
        import dynesty
    except ImportError:
        if verbose:
            print(f"  [{label}] dynesty unavailable -> grid quadrature fallback")
        return _grid_logz(loglike_fn, ranges, grid_fallback_n)

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike_fn,
        prior_transform=make_prior_transform(ranges),
        ndim=ndim, nlive=nlive, bound="multi", sample="auto", bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    weights = np.exp(res.logwt - res.logz[-1])
    return {
        "log_Z": float(res.logz[-1]),
        "log_Z_err": float(res.logzerr[-1]),
        "loglike_max": float(np.max(res.logl)),
        "samples": np.asarray(res.samples),
        "weights": weights,
        "sampler": f"dynesty_nlive{nlive}",
        "wall_seconds": float(wall),
    }


def summarize(fit, names):
    """MAP + weighted 16/50/84 percentiles per parameter."""
    samples, weights = fit["samples"], fit["weights"]
    imap = int(np.argmax(weights))
    out = {"MAP": {}, "percentiles": {}}
    for j, nm in enumerate(names):
        out["MAP"][nm] = float(samples[imap, j])
        p16, p50, p84 = tcs.weighted_percentiles(samples[:, j], weights)
        out["percentiles"][nm] = {"p16": p16, "p50": p50, "p84": p84}
    return out


def verdict(delta_logz, err=0.0):
    """Jeffreys-style verdict on a log-evidence difference."""
    d = float(delta_logz)
    if not np.isfinite(d):
        return "undetermined"
    if abs(d) < max(1.0, 3.0 * err):
        return "equivalent (no significant preference)"
    if d >= 5.0:
        return "two-component strongly preferred"
    if d >= 1.0:
        return "two-component mildly preferred"
    if d <= -5.0:
        return "two-component strongly disfavored"
    return "two-component mildly disfavored"


# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--nlive", type=int, default=NLIVE)
    ap.add_argument("--out", type=str, default="t18_two_component_fit.json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    verbose = not args.quiet
    ranges_2c = list(tcs.PRIOR_RANGES)
    ranges_1c = [SINGLE_LOG_SIGMA_RANGE, SINGLE_A_RANGE]

    if verbose:
        print("[T18] Direction B: two-component (mass-segregated) SIDM fit")
        print("  *** PLACEHOLDER likelihoods — feasibility check, not a result ***")
        print(f"  Reference: Yang, Fan, Hou & Tsai 2026, Sci. Bull.,")
        print(f"             DOI 10.1016/j.scib.2026.01.077 (arXiv:2504.02303)")
        print(f"  Channels: dSph-effective + Cluster-effective + Mass-segregation")
        print(f"  Priors: log10 s1 {ranges_2c[0]}, log10 s2 {ranges_2c[1]}, "
              f"f1 {ranges_2c[2]}, a {ranges_2c[3]}")
        print(f"  beta_seg (fixed) = {tcs.SEGREGATION_BETA}")
        print(f"  nlive = {args.nlive}, dlogz = {DLOGZ}\n")

    # (A) two-component, 4 params
    fit_2c = run_fit(loglike_2comp, ranges_2c, args.nlive, "2comp", verbose=verbose)
    sum_2c = summarize(fit_2c, tcs.PARAM_NAMES)
    if verbose:
        print(f"  (A) 2-component (4 par, 3 ch): log Z = {fit_2c['log_Z']:.3f} "
              f"+/- {fit_2c['log_Z_err']:.3f}   [{fit_2c['sampler']}, "
              f"{fit_2c['wall_seconds']:.1f}s]")

    # (B) nested single-component reference, same 3 channels
    fit_1c_nested = run_fit(loglike_1comp_nested, ranges_1c, args.nlive,
                            "1comp-nested", verbose=verbose)
    sum_1c_nested = summarize(fit_1c_nested, ("log_sigma", "a"))
    if verbose:
        print(f"  (B) 1-component nested (2 par, 3 ch): "
              f"log Z = {fit_1c_nested['log_Z']:.3f} "
              f"+/- {fit_1c_nested['log_Z_err']:.3f}")

    # (C) single-component, dwarf + cluster channels only
    fit_1c_2ch = run_fit(loglike_1comp_2channel, ranges_1c, args.nlive,
                         "1comp-2ch", verbose=verbose)
    sum_1c_2ch = summarize(fit_1c_2ch, ("log_sigma", "a"))
    if verbose:
        print(f"  (C) 1-component 2-channel (2 par, 2 ch): "
              f"log Z = {fit_1c_2ch['log_Z']:.3f} "
              f"+/- {fit_1c_2ch['log_Z_err']:.3f}")

    # Grid cross-check of (A)
    grid = tcs.grid_evidence(n_per_dim=21)
    if verbose:
        print(f"  grid cross-check of (A): log Z = {grid['log_Z']:.3f} "
              f"(21^4 midpoint quadrature)")

    # t8 5-channel single-component (incommensurate; brief asks for it)
    t8 = None
    if T8_POSTERIOR.exists():
        t8 = json.loads(T8_POSTERIOR.read_text())

    # Bayes factors
    err_2c = fit_2c["log_Z_err"] if np.isfinite(fit_2c["log_Z_err"]) else 0.0
    bf = {}
    d_nested = fit_2c["log_Z"] - fit_1c_nested["log_Z"]
    err_nested = float(np.hypot(
        err_2c,
        fit_1c_nested["log_Z_err"] if np.isfinite(fit_1c_nested["log_Z_err"]) else 0.0))
    bf["vs_1comp_nested_same_3_channels"] = {
        "delta_log_Z": float(d_nested),
        "delta_log_Z_err": err_nested,
        "verdict": verdict(d_nested, err_nested),
        "validity": ("STRICT nested Bayes factor (identical channel set and "
                     "data); but partly circular — the segregation channel "
                     "encodes sigma1 > 10 sigma2 which sigma1 == sigma2 "
                     "cannot satisfy by construction."),
    }
    d_2ch = fit_2c["log_Z"] - fit_1c_2ch["log_Z"]
    bf["vs_1comp_dwarf_plus_cluster_only"] = {
        "delta_log_Z": float(d_2ch),
        "verdict": verdict(d_2ch),
        "validity": ("DIAGNOSTIC only — different channel sets (3 vs 2), so "
                     "not a strict Bayes factor. Answers: can one velocity-"
                     "dependent sigma satisfy both placeholder constraints?"),
    }
    if t8 is not None:
        d_t8 = fit_2c["log_Z"] - float(t8["log_Z"])
        bf["vs_t8_v03_5channel_single_component"] = {
            "t8_log_Z": float(t8["log_Z"]),
            "t8_log_Z_err": float(t8.get("log_Z_err", float("nan"))),
            "delta_log_Z": float(d_t8),
            "verdict": verdict(d_t8),
            "validity": ("INCOMMENSURATE — t8 uses a different (5-channel, "
                         "partly real / partly calibrated) likelihood with a "
                         "different absolute normalisation. Reported as a "
                         "magnitude sanity check only, NOT a Bayes factor."),
        }

    if verbose:
        print("\n  Bayes factors (log Z difference, 2-comp minus 1-comp):")
        for k, v in bf.items():
            print(f"    {k}: {v['delta_log_Z']:+.3f}  -> {v['verdict']}")

    # MAP physical interpretation
    m = sum_2c["MAP"]
    s1, s2 = 10.0 ** m["log_sigma1"], 10.0 ** m["log_sigma2"]
    f1, a = m["f1"], m["a"]
    sd = float(tcs.sigma_eff_dwarf(s1, s2, f1, a))
    sg = float(tcs.sigma_eff_galaxy(s1, s2, f1, a))
    sc = float(tcs.sigma_eff_cluster(s1, s2, f1, a))
    contrast = float(tcs.dwarf_to_cluster_contrast(s1, s2, f1, a))
    contrast_1c = float(tcs.single_component_contrast(a))

    if verbose:
        print(f"\n  (A) MAP: sigma1={s1:.3f}, sigma2={s2:.4f} cm^2/g, "
              f"f1={f1:.3f}, a={a:+.3f}")
        print(f"       sigma1/sigma2 = {s1 / s2:.1f}  "
              f"(segregation channel wants >= 10)")
        print(f"       sigma_eff(v=30,   dwarf)   = {sd:.4f} cm^2/g")
        print(f"       sigma_eff(v=100,  galaxy)  = {sg:.4f} cm^2/g")
        print(f"       sigma_eff(v=1500, cluster) = {sc:.4f} cm^2/g")
        print(f"       dwarf/cluster contrast = {contrast:.2f} "
              f"(single-component ceiling at same a: {contrast_1c:.2f})")

        print(f"\n  1D marginalized posterior on log10(sigma1):")
        hist, edges = np.histogram(fit_2c["samples"][:, 0], bins=20,
                                   weights=fit_2c["weights"])
        centers = 0.5 * (edges[:-1] + edges[1:])
        hmax = hist.max() if hist.max() > 0 else 1.0
        for c, h in zip(centers, hist):
            print(f"    log sigma1 = {c:+5.2f}  p = {h:.3f}  "
                  f"{'#' * int(40 * h / hmax)}")

    out = {
        "test": "T18_v03_two_component_direction_B",
        "PLACEHOLDER_WARNING": (
            "The three channel likelihoods (dSph-effective, Cluster-effective, "
            "Mass-segregation) are SIMPLIFIED GAUSSIAN PROXIES, not real "
            "published posteriors. All log Z values and Bayes factors below "
            "are a pipeline feasibility check for Direction B, NOT a "
            "publication-quality result and NOT evidence for or against "
            "two-component SIDM."),
        "model": {
            "name": "two-component mass-segregated SIDM (minimal viable)",
            "reference": ("Yang, Fan, Hou, Tsai, Science Bulletin (2026), "
                          "DOI 10.1016/j.scib.2026.01.077, arXiv:2504.02303"),
            "n_params": 4,
            "params": list(tcs.PARAM_NAMES),
            "priors": {
                "log_sigma1": list(tcs.LOG_SIGMA1_RANGE),
                "log_sigma2": list(tcs.LOG_SIGMA2_RANGE),
                "f1": list(tcs.F1_RANGE),
                "a": list(tcs.A_RANGE),
            },
            "fixed": {"beta_seg": tcs.SEGREGATION_BETA,
                      "v_ref_km_s": tcs.V_REF},
            "velocity_scales_km_s": {"dwarf": tcs.V_DWARF,
                                     "galaxy": tcs.V_GALAXY,
                                     "cluster": tcs.V_CLUSTER},
        },
        "channels": {
            "1_dSph_effective": ("PLACEHOLDER Gaussian on log10 sigma_eff(30 "
                                 "km/s), peak 10^0.5 cm^2/g, width 0.6 dex, "
                                 "walls outside [0.3, 30] cm^2/g"),
            "2_cluster_effective": ("PLACEHOLDER one-sided Gaussian, "
                                    "sigma_eff(1500 km/s) < 0.5 cm^2/g, "
                                    "0.30 dex"),
            "3_mass_segregation": ("PLACEHOLDER one-sided Gaussian on "
                                   "log10(sigma1/sigma2) >= 1 (Yang+ 2026 "
                                   "requirement), 0.30 dex"),
        },
        "fit_2component": {
            "log_Z": fit_2c["log_Z"], "log_Z_err": fit_2c["log_Z_err"],
            "loglike_max": fit_2c["loglike_max"],
            "sampler": fit_2c["sampler"],
            "wall_seconds": fit_2c["wall_seconds"],
            "n_samples": int(len(fit_2c["samples"])),
            "MAP": sum_2c["MAP"], "percentiles": sum_2c["percentiles"],
            "MAP_derived": {
                "sigma1_cm2_per_g": float(s1),
                "sigma2_cm2_per_g": float(s2),
                "sigma1_over_sigma2": float(s1 / s2),
                "sigma_eff_dwarf_30": sd,
                "sigma_eff_galaxy_100": sg,
                "sigma_eff_cluster_1500": sc,
                "dwarf_to_cluster_contrast": contrast,
                "single_component_contrast_at_same_a": contrast_1c,
            },
        },
        "fit_1component_nested_same_channels": {
            "log_Z": fit_1c_nested["log_Z"],
            "log_Z_err": fit_1c_nested["log_Z_err"],
            "loglike_max": fit_1c_nested["loglike_max"],
            "sampler": fit_1c_nested["sampler"],
            "MAP": sum_1c_nested["MAP"],
            "percentiles": sum_1c_nested["percentiles"],
            "note": "sigma1 == sigma2 enforced; 2 free params (log sigma, a).",
        },
        "fit_1component_dwarf_plus_cluster_only": {
            "log_Z": fit_1c_2ch["log_Z"],
            "log_Z_err": fit_1c_2ch["log_Z_err"],
            "loglike_max": fit_1c_2ch["loglike_max"],
            "sampler": fit_1c_2ch["sampler"],
            "MAP": sum_1c_2ch["MAP"],
            "percentiles": sum_1c_2ch["percentiles"],
            "note": ("segregation channel dropped; asks whether one "
                     "velocity-dependent sigma can satisfy dwarf + cluster."),
        },
        "grid_crosscheck_2component": {
            "log_Z": grid["log_Z"], "loglike_max": grid["loglike_max"],
            "method": grid["method"], "n_per_dim": grid["n_per_dim"],
        },
        "bayes_factors": bf,
        "caveats": [
            "All three channel likelihoods are placeholders (see PLACEHOLDER_WARNING).",
            "beta_seg is a fixed phenomenological stand-in for the full "
            "two-fluid gravothermal solution of Yang+ 2026, not a fitted or "
            "published quantity.",
            "The nested comparison (B) is partly circular: the segregation "
            "channel is built from the Yang+ 2026 requirement, so a "
            "single-component model is penalised by construction.",
            "The comparison against t8_v03_posterior.json is incommensurate "
            "(different channel set / normalisation) and is a magnitude "
            "sanity check only.",
            "Bayes factors here depend on the (arbitrary) prior ranges; the "
            "4-param model pays a larger Occam factor than the 2-param one.",
        ],
    }

    out_path = RESULTS_DIR / args.out
    out_path.write_text(json.dumps(out, indent=2))
    np.savez(RESULTS_DIR / "t18_two_component_samples.npz",
             samples=fit_2c["samples"], weights=fit_2c["weights"])
    if verbose:
        print(f"\n  output -> {out_path}")
    return out


if __name__ == "__main__":
    main()
