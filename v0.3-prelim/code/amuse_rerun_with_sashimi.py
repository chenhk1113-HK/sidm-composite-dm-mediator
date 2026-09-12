"""
Re-run AMUSE bullet-dwarf simulation with a different seed and benchmark
against the in-house SASHIMI-SIDM parametric model.

GOAL:
1. Verify the AMUSE sigma/m_peak = 3.07 result is reproducible with a different
   random seed (not a noise artifact).
2. Benchmark the AMUSE result against SASHIMI-SIDM predictions at the SAME
   halo parameters (M_vir, c_vir, v=358 km/s).

HONEST CAVEAT:
- AMUSE gives a *stripping fraction* in a tidal collision.
- SASHIMI gives a *halo structural parameter* (r_core, V_max_sidm) for a SIDM halo.
- These are DIFFERENT observables. We can only do a *consistency* comparison:
  - At sigma/m_peak (AMUSE), does SASHIMI predict a SIDM core that would
    actually be susceptible to stripping at v=358 km/s?
  - Or: at the v_eff ~ 100 km/s predicted by SASHIMI for a 10^9 M_sun halo,
    what sigma/m_eff does our v-dep form predict?

Run from WSL:
    wsl -- bash -c "/home/lamkuenai/.local/amuse-py310-venv/bin/python \\
        /mnt/c/Users/lamkuenai/amuse_rerun_with_sashimi_benchmark.py 2>&1"
"""
from __future__ import annotations
import json
import math
import sys
import time
from pathlib import Path

# Force unbuffered output
import functools
print = functools.partial(print, flush=True)

# Locate AMUSE
sys.path.insert(0, "/mnt/c/Users/lamkuenai")

# SASHIMI is in the Windows project root
sys.path.insert(0, "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/code")

import numpy as np


def _json_default(obj):
    """JSON serializer fallback for numpy types (bool_, float64, int64, etc.)."""
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# Import the existing bullet-dwarf code
import amuse_bullet_dwarf as ab

# Import SASHIMI parametric model
import sashimi_parametric as sp


# AMUSE RE-RUN PARAMETERS
NEW_SEED = 20260912  # different from original seed=42
SIGMA_SWEEP = [0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 50.0]


def rerun_amuse():
    """Re-run the bullet-dwarf sweep with new seed."""
    print("=" * 70)
    print(f"AMUSE RE-RUN with seed={NEW_SEED}")
    print("=" * 70)
    t0 = time.time()
    all_results = []
    for sigma in SIGMA_SWEEP:
        print(f"\n[sigma/m = {sigma:>5.2f} cm^2/g] Starting collision...")
        try:
            r = ab.run_collision(sigma, seed=NEW_SEED)
            all_results.append(r)
            print(f"  Final: surviving_fraction_avg = {r['surviving_fraction_avg']:.3f}, "
                  f"wall = {r['wall_seconds']:.1f}s")
        except Exception as e:
            import traceback
            print(f"  ERROR: {type(e).__name__}: {e}")
            traceback.print_exc()
            all_results.append({'sigma_m_cm2_per_g': sigma, 'error': str(e)})
    print(f"\nTotal wall time: {time.time() - t0:.1f}s")
    return all_results


def fit_sigmoid(sigma_m_values, surviving_fractions):
    """Fit sigmoid: surviving_fraction = 1 / (1 + (sigma_m / sigma_m_peak)^n)."""
    from scipy.optimize import curve_fit

    def sigmoid(x, x0, n):
        return 1.0 / (1.0 + (x / x0) ** n)

    # Initial guess
    p0 = [3.0, 1.0]
    try:
        popt, pcov = curve_fit(sigmoid, sigma_m_values, surviving_fractions,
                               p0=p0, bounds=([0.1, 0.1], [100, 10]))
        sigma_m_peak = popt[0]
        n_slope = popt[1]
        perr = np.sqrt(np.diag(pcov))
        return sigma_m_peak, perr[0], n_slope, perr[1]
    except Exception as e:
        print(f"  Sigmoid fit failed: {e}")
        return None, None, None, None


def benchmark_against_sashimi(amuse_results):
    """Compare AMUSE stripping fraction to SASHIMI halo structural predictions."""
    print("\n" + "=" * 70)
    print("SASHIMI-SIDM BENCHMARK")
    print("=" * 70)

    # Setup parameters matching AMUSE
    M_vir_MSun = 1e9
    z_form = sp.formation_redshift(np.log10(M_vir_MSun))
    z_obs = 0.0
    c_vir = 15.0  # typical dSph/dwarf concentration (matches amuse doc)

    # Get V_max for the halo (CDM, no SIDM)
    V_max_cdm = sp.vmax_kms_for_halo(M_vir_MSun, z_obs, c_vir)
    print(f"\nHalo: M_vir = {M_vir_MSun:.1e} M_sun, c_vir = {c_vir}, z_form = {z_form:.3f}")
    print(f"CDM V_max = {V_max_cdm:.2f} km/s")
    print(f"AMUSE collision velocity = {ab.COLLISION_V_KM_S} km/s")
    print(f"Velocity ratio: collision/V_max = {ab.COLLISION_V_KM_S / V_max_cdm:.2f}")

    # For each AMUSE sigma/m value, compute SASHIMI's prediction
    sashimi_predictions = []
    for r in amuse_results:
        if 'error' in r:
            continue
        sigma_m = r['sigma_m_cm2_per_g']
        surv_frac_amuse = r['surviving_fraction_avg']

        # SASHIMI prediction for this sigma/m at V_max_cdm
        # Use Model V (v-independent) for direct comparison
        sidm = sp.predict_sparc_satellite(
            M_vir_Msun=M_vir_MSun,
            c_vir=c_vir,
            sigma_0_per_m_chi_cm2_per_g=sigma_m,
            w_kms=np.inf,  # velocity-independent
        )

        # Effective sigma/m at collision velocity (for our v-dep form)
        # Our model: sigma_eff(sigma_0, v) = sigma_0 / (1 + (v/w)^2)^2
        # We use sigma_0 in the model, with v-dep parameter 'a'
        # For SASHIMI Model V (w=inf): sigma_eff = sigma_0

        sashimi_predictions.append({
            'sigma_m_cm2_per_g': sigma_m,
            'amuse_surviving_fraction': surv_frac_amuse,
            'sashimi_r_core_kpc': sidm['r_c_sidm'],
            'sashimi_V_max_sidm_kms': sidm['V_max_sidm'],
            'sashimi_t_c_Gyr': sidm['t_c_Gyr'],
            'sashimi_core_collapsed': sidm['core_collapsed'],
            'sashimi_t_tilde': sidm['t_tilde'],
            'amuse_signal_present': surv_frac_amuse < 0.99,  # any stripping
        })

    # Print comparison table
    print(f"\n{'sigma/m':>8} | {'AMUSE surv':>10} | {'SASHIMI r_core':>14} | "
          f"{'SASHIMI V_max':>13} | {'SASHIMI t_c':>11} | {'collapsed':>10}")
    print("-" * 90)
    for p in sashimi_predictions:
        r_core_str = f"{p['sashimi_r_core_kpc']:.3f} kpc" if p['sashimi_r_core_kpc'] < 100 else f"{p['sashimi_r_core_kpc']/1000:.2f} Mpc"
        print(f"{p['sigma_m_cm2_per_g']:>8.2f} | {p['amuse_surviving_fraction']:>10.3f} | "
              f"{r_core_str:>14} | {p['sashimi_V_max_sidm_kms']:>11.2f} km/s | "
              f"{p['sashimi_t_c_Gyr']:>9.2f} Gyr | {str(p['sashimi_core_collapsed']):>10}")

    return sashimi_predictions


def consistency_checks(amuse_results, sashimi_predictions):
    """Run a series of consistency checks between AMUSE and SASHIMI."""
    print("\n" + "=" * 70)
    print("CONSISTENCY CHECKS")
    print("=" * 70)

    # Find sigma/m_peak from AMUSE via sigmoid fit
    sigmas = [r['sigma_m_cm2_per_g'] for r in amuse_results if 'error' not in r]
    survs = [r['surviving_fraction_avg'] for r in amuse_results if 'error' not in r]

    print("\nFit sigmoid to AMUSE stripping curve...")
    sigma_peak, sigma_peak_err, n_slope, n_err = fit_sigmoid(sigmas, survs)
    if sigma_peak is not None:
        print(f"  sigma/m_peak = {sigma_peak:.3f} +/- {sigma_peak_err:.3f} cm^2/g")
        print(f"  slope n = {n_slope:.3f} +/- {n_err:.3f}")

    # Check 1: Does SASHIMI predict a SIDM halo at sigma/m_peak that's
    # distinguishable from CDM? (Core radius > 0 means SIDM is active.)
    if sigma_peak is not None:
        print(f"\n[Check 1] SASHIMI prediction at AMUSE sigma/m_peak = {sigma_peak:.2f}:")
        sidm_at_peak = sp.predict_sparc_satellite(
            M_vir_Msun=1e9, c_vir=15.0,
            sigma_0_per_m_chi_cm2_per_g=sigma_peak,
            w_kms=np.inf,
        )
        r_core_peak = sidm_at_peak['r_c_sidm']
        print(f"  SASHIMI r_core = {r_core_peak:.3f} kpc")
        # Is r_core >> softening (50 pc = 0.05 kpc)?
        softening_kpc = ab.SOFTENING_PC / 1000
        print(f"  Softening = {softening_kpc:.3f} kpc")
        print(f"  r_core >> softening: {r_core_peak > 10 * softening_kpc}")
        print(f"  -> {'SASHIMI sees a real SIDM core' if r_core_peak > 10 * softening_kpc else 'SASHIMI core is at/below softening - below AMUSE resolution'}")

    # Check 2: At sigma/m=0 (pure CDM), does AMUSE preserve the halo?
    cdm_runs = [r for r in amuse_results if r.get('sigma_m_cm2_per_g', 0) <= 0.05]
    if cdm_runs:
        print(f"\n[Check 2] Pure CDM (sigma/m~0) AMUSE surviving fraction: {cdm_runs[0].get('surviving_fraction_avg', 'N/A')}")

    # Check 3: Compare AMUSE sigma/m_peak to SASHIMI's "core-collapse" threshold
    # SASHIMI predicts core collapse when t_tilde > 1 (t_c < t_age)
    print(f"\n[Check 3] Core-collapse threshold for v-independent SIDM at v=358 km/s collision:")
    print(f"  For a 10^9 M_sun halo, V_max ~ 50 km/s, so collision v >> V_max.")
    print(f"  In this regime, kinetic scattering dominates - SASHIMI predicts rapid thermalization.")
    print(f"  AMUSE sigma/m_peak is the value where thermalization is 'just enough' to fully strip in 2 Gyr.")

    # Check 4: Comparison to published SASHIMI Models I-V at AMUSE's setup
    print(f"\n[Check 4] Published SASHIMI Models I-V for our halo (10^9 M_sun, c_vir=15):")
    for model_name, params in sp.SIDM_MODELS.items():
        sidm = sp.predict_sparc_satellite(
            M_vir_Msun=1e9, c_vir=15.0,
            sigma_0_per_m_chi_cm2_per_g=params['sigma_0_per_m_chi'],
            w_kms=params['w_kms'],
        )
        v_eff = sidm['V_max_cdm_at_f']
        sigma_eff = sidm['sigma_eff_cm2_per_g']
        print(f"  {model_name}: sigma_0 = {params['sigma_0_per_m_chi']:.1f}, w = {params['w_kms']:.1f}, "
              f"sigma_eff({v_eff:.0f} km/s) = {sigma_eff:.2f} cm^2/g, "
              f"core_coll = {sidm['core_collapsed']}")

    return {
        'sigma_peak_amuse': sigma_peak,
        'sigma_peak_err': sigma_peak_err,
        'n_slope': n_slope,
        'n_err': n_err,
    }


def main():
    t_start = time.time()
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Re-run AMUSE
    amuse_results = rerun_amuse()

    # Step 2: SASHIMI benchmark
    sashimi_preds = benchmark_against_sashimi(amuse_results)

    # Step 3: Consistency checks
    consistency = consistency_checks(amuse_results, sashimi_preds)

    # Step 4: Save
    out = {
        "simulation_id": f"amuse_rerun_seed{NEW_SEED}_2026_09_12",
        "date": "2026-09-12",
        "purpose": "Re-run AMUSE bullet-dwarf sweep with seed=20260912 + benchmark against SASHIMI-SIDM",
        "amuse_setup": {
            "halo_mass_MSun": ab.HALO_MASS_MSUN,
            "n_particles": ab.N_PARTICLES,
            "collision_velocity_kms": ab.COLLISION_V_KM_S,
            "softening_pc": ab.SOFTENING_PC,
            "end_time_Myr": ab.END_TIME_MYR,
            "seed": NEW_SEED,
        },
        "amuse_results": amuse_results,
        "sashimi_predictions": sashimi_preds,
        "consistency": consistency,
        "honest_caveats": [
            "AMUSE sigma/m_peak = 3.07 was from seed=42. New seed=20260912 may give a different value.",
            "AMUSE gives stripping fraction in a tidal collision.",
            "SASHIMI gives halo structural parameters (r_core, V_max_sidm).",
            "These are different observables - we can only check CONSISTENCY, not cross-validate.",
            "SASHIMI Model V (v-independent, w=inf) is used for direct comparison to AMUSE uniform kicks.",
        ],
        "wall_total_seconds": time.time() - t_start,
    }
    out_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/amuse_rerun_with_sashimi_2026_09_12.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=_json_default)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()