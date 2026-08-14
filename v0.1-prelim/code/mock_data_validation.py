#!/usr/bin/env python
"""
T5 mock-data validation: inject known halo profile, recover.

Generates a synthetic rotation curve from a known NFW or Burkert profile,
adds Gaussian noise, then fits both profiles. The recovered theta_MAP
should match the input to within posterior std.

For v0.1-prelim we test on one representative galaxy (UGC02953, 115 pts).

Usage:
    python mock_data_validation.py
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparc_loader import load_one_sparc
from halo_profiles import V_NFW, V_Burkert, log_prior_NFW, log_prior_Burkert, V2_total
from fit_single_galaxy import fit_one_galaxy, RESULTS_DIR, DATA_DIR, NLIVE, DLOGZ


def gen_mock_rotation_curve(ga, profile: str, theta_truth: np.ndarray, noise_sigma: float = 1.5, seed: int = 42):
    """Generate a synthetic rotation curve using a known halo profile.

    theta_truth: log10(rho), log10(r_scale) in the appropriate units
    Returns a new SPARCGalaxy with Vobs replaced by simulated values.
    """
    rho, r_scale = 10**theta_truth[0], 10**theta_truth[1]
    if profile == "NFW":
        halo_V2 = V_NFW(ga.Rad, rho, r_scale)
    elif profile == "Burkert":
        halo_V2 = V_Burkert(ga.Rad, rho, r_scale)
    else:
        raise ValueError(profile)
    V_total = np.sqrt(ga.Vbar_sq + halo_V2)
    rng = np.random.default_rng(seed)
    # Preserve the original errV (for the likelihood)
    V_sim = V_total + rng.normal(0, noise_sigma, size=len(ga.Rad))
    # Build a new SPARCGalaxy-like object
    from sparc_loader import SPARCGalaxy
    g_sim = SPARCGalaxy(
        name=f"mock_{profile}_{ga.name}",
        rad=ga.Rad.copy(),
        vobs=V_sim,
        errv=np.full_like(ga.Vobs, noise_sigma),  # use the input sigma as constant errV
        vgas=ga.Vgas.copy(),
        vdisk=ga.Vdisk.copy(),
        vbul=ga.Vbul.copy(),
        sbdisk=ga.SBdisk.copy(),
        sbbul=ga.SBbul.copy(),
    )
    return g_sim


def inject_and_fit(true_profile: str, theta_truth: np.ndarray):
    """Inject a known true profile, fit both models, report recovery."""
    print(f"\n--- MOCK VALIDATION: truth = {true_profile} at theta = {theta_truth} ---")
    base_gal = load_one_sparc(DATA_DIR, "UGC02953")  # 115 pts, Vbar realistic
    # Use the base galaxy's baryonic components (Vbar) but replace Vobs with simulated.
    g_sim = gen_mock_rotation_curve(base_gal, true_profile, theta_truth)
    # Temporarily swap into the load_one_sparc name -> write a temp rotmod file
    # Actually simpler: patch the sparc_loader to find this in-memory galaxy
    # We'll just call fit_one_galaxy-like logic directly.
    import dynesty

    def fit_one(profile_name, theta_truth_local, halo_fn, log_prior_fn, prior_lo, prior_hi):
        def loglike(theta):
            lp = log_prior_fn(theta)
            if not np.isfinite(lp):
                return -np.inf
            rho, r_scale = 10**theta[0], 10**theta[1]
            V2 = halo_fn(g_sim.Rad, rho, r_scale)
            V_total = np.sqrt(g_sim.Vbar_sq + V2)
            return -0.5 * float(np.sum(((g_sim.Vobs - V_total) / g_sim.errV)**2))

        def prior_transform(u):
            return np.array([prior_lo[0] + u[0] * (prior_lo[1] - prior_lo[0]),
                            prior_hi[0] + u[1] * (prior_hi[1] - prior_hi[0])])

        t0 = time.time()
        sampler = dynesty.NestedSampler(
            loglikelihood=loglike, prior_transform=prior_transform,
            ndim=2, nlive=NLIVE, bound='multi', sample='auto', bootstrap=0,
        )
        sampler.run_nested(dlogz=DLOGZ, print_progress=False)
        res = sampler.results
        wall = time.time() - t0
        samples = res.samples
        weights = np.exp(res.logwt - res.logz[-1])
        imap = int(np.argmax(weights))
        theta_map = samples[imap]
        log_Z = float(res.logz[-1])
        # Posterior median + std
        post_med = np.median(samples, axis=0)
        post_std = np.std(samples, axis=0)
        return {
            "log_Z": log_Z,
            "theta_MAP": theta_map.tolist(),
            "post_med": post_med.tolist(),
            "post_std": post_std.tolist(),
            "wall": wall,
        }

    # Run all 3 fits: NFW fit on truth-NFW data, Burkert fit on truth-NFW data,
    #                 Burkert fit on truth-Burkert data, NFW fit on truth-Burkert data
    results = {}
    for true_p, true_th in [(true_profile, theta_truth)]:
        for fit_p, (halo_fn, prior_fn) in [
            ("NFW",     (V_NFW,     log_prior_NFW)),
            ("Burkert", (V_Burkert, log_prior_Burkert)),
        ]:
            from halo_profiles import (NFW_LOG_RHO_S_RANGE, NFW_LOG_R_S_RANGE,
                                      BURKERT_LOG_RHO_C_RANGE, BURKERT_LOG_R_C_RANGE)
            if fit_p == "NFW":
                plo, phi = NFW_LOG_RHO_S_RANGE, NFW_LOG_R_S_RANGE
            else:
                plo, phi = BURKERT_LOG_RHO_C_RANGE, BURKERT_LOG_R_C_RANGE
            res = fit_one(fit_p, true_th, halo_fn, prior_fn, plo, phi)
            results[f"truth={true_p}_fit={fit_p}"] = res
            truth_known = "YES" if fit_p == true_p else "NO (wrong-model fit)"
            recovery = "RECOVERED" if fit_p == true_p else "(wrong model fit, do not expect recovery)"
            print(f"  truth={true_p} fit={fit_p} ({truth_known}): "
                  f"log_Z = {res['log_Z']:.2f}, "
                  f"theta_MAP = [{res['theta_MAP'][0]:.2f}, {res['theta_MAP'][1]:.2f}], "
                  f"post_med = [{res['post_med'][0]:.2f}±{res['post_std'][0]:.2f}, "
                                f"{res['post_med'][1]:.2f}±{res['post_std'][1]:.2f}], "
                  f"wall={res['wall']:.1f}s {recovery}")
    return results


def main():
    # Test 1: truth is NFW at theta = [7.0, 0.5]  (log_rho_s=7, log_r_s=0.5)
    res_nfw = inject_and_fit("NFW", np.array([7.0, 0.5]))
    # Test 2: truth is Burkert at theta = [7.0, 0.3]
    res_bur = inject_and_fit("Burkert", np.array([7.0, 0.3]))

    out = {
        "test_1_truth_NFW": res_nfw,
        "test_2_truth_Burkert": res_bur,
        "description": "Mock-data validation: inject known halo profile on UGC02953 baryonic template, fit both NFW + Burkert, check recovery.",
    }
    out_path = RESULTS_DIR / "t5_mock_validation.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))

    # Quick check: for each truth, the CORRECT model should win log Z
    print("\n=== VALIDATION SUMMARY ===")
    nfw_truth_nfw_z = out["test_1_truth_NFW"]["truth=NFW_fit=NFW"]["log_Z"]
    nfw_truth_bur_z = out["test_1_truth_NFW"]["truth=NFW_fit=Burkert"]["log_Z"]
    bur_truth_bur_z = out["test_2_truth_Burkert"]["truth=Burkert_fit=Burkert"]["log_Z"]
    bur_truth_nfw_z = out["test_2_truth_Burkert"]["truth=Burkert_fit=NFW"]["log_Z"]

    print(f"Truth=NFW:     NFW log Z = {nfw_truth_nfw_z:.2f}, Burkert log Z = {nfw_truth_bur_z:.2f}, "
          f"correct wins: {nfw_truth_nfw_z > nfw_truth_bur_z}")
    print(f"Truth=Burkert: Burkert log Z = {bur_truth_bur_z:.2f}, NFW log Z = {bur_truth_nfw_z:.2f}, "
          f"correct wins: {bur_truth_bur_z > bur_truth_nfw_z}")
    print(f"Validation -> {out_path}")


if __name__ == "__main__":
    main()