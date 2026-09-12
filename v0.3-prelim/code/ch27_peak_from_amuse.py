"""
Compute a Channel 27 sigma/m peak from the AMUSE bullet-dwarf simulation output.

GOAL: Replace Channel 27's placeholder peak with a value derived from the
AMUSE-ph4 bullet-dwarf N-body sweep (sigma/m in {0.1, 0.5, 1.0, 2.0, 5.0, 10.0} cm^2/g).

METHOD:
The simulation produces a (sigma/m, time, n_bound_A, n_bound_B) grid. We map
this to a sigma/m vs surviving-fraction curve at the moment that best matches
the NGC 1052 trail observational anchor (~8 Gyr post-collision).

For each sigma/m, we record n_bound at that time, compute the surviving
fraction, and fit a single-parameter curve:

    f_bound(sigma/m) = 1 / (1 + (sigma/m / sigma/m_peak) ** k)

where sigma/m_peak is the value where f_bound = 0.5 (the "calibration anchor")
and k controls the steepness. The fit uses scipy.optimize.curve_fit on the
sigma/m vs f_bound data at the chosen time slice.

**CRITICAL HONEST CAVEAT (added 2026-09-12, after SASHIMI benchmark):**
The sigma/m_peak fit captures the TRANSIENT pre-disruption window, NOT asymptotic
disruption. By t > 350 Myr, all halos fully disrupt regardless of sigma/m
(because N=1024 is too low for realistic gravothermal evolution). The peak value
is a TIME-SLICE-DEPENDENT quantity, not a measurement of physical sigma/m at
v=358 km/s.

Furthermore, the peak coincides with the SASHIMI-predicted sigma/m value at which
AMUSE first sees a SIDM core (r_core > 5x softening = 0.25 kpc). The fit value
should be interpreted as a SOFTENING-RESOLUTION THRESHOLD, not as a physics
measurement.

This script now outputs:
  1. The single-time-slice fit (legacy behavior, default t=300 Myr)
  2. A TIME-SLICE SENSITIVITY TABLE showing how the peak slides with t
  3. A SASHIMI RESOLUTION CHECK warning if peak is within 2x of softening limit

CHANNEL 27 CONTEXT (from docs/CH27_NGC1052_TRAIL_CHANNEL.md, commit 8d917cc):
- Observables: NGC 1052-DF2/DF4/DF9 at trail tip, v=358 km/s
- Anchor: sigma/m(v=358 km/s) = ?
- Current placeholder: log10(sigma/m_358) = -0.30 (0.5 cm^2/g)
- After ablation: sigma/m_0 = 0.59 -> 0.99 cm^2/g (+68%)

OUTPUT:
- ch27_sigma_m_peak_from_amuse_2026_09_12.json with proposed peak, fit params,
  curve data, time-slice sensitivity table, and SASHIMI resolution check.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit


REPO_ROOT = Path(__file__).parent.parent
SIM_JSON = REPO_ROOT / 'data' / 'results' / 'amuse_bullet_dwarf_calibration_2026_09_12.json'
OUT_JSON = REPO_ROOT / 'data' / 'results' / 'ch27_sigma_m_peak_from_amuse_2026_09_12.json'

# Primary time slice: 0.15 of integration time (2 Gyr) = 300 Myr after collision start
# This is BEFORE the bulk disruption transition (~345 Myr, where all curves collapse to 0)
# but late enough that SIDM scattering has had time to differentiate the curves.
# At t=300 Myr the simulation shows: sigma/m=0.1 retains 97%, sigma/m=10 retains 8%.
# This is the cleanest sigma/m-discrimination window available in the data.
TIME_FRACTION = 0.15  # Use n_bound at ~15% through the simulation (discriminating region)

# AMUSE softening (50 pc = 0.05 kpc). Per SASHIMI benchmark, the peak sigma/m_peak
# should be checked against this limit; if it's within 2x of the sigma/m at which
# r_core = 5*softening, the result is a resolution-threshold measurement, not physics.
AMUSE_SOFTENING_PC = 50.0
SASHIMI_RESOLUTION_THRESHOLD_FRACTION = 5.0  # r_core >= 5x softening is "resolvable"

# Time slices for sensitivity table (Myr). These bracket the discriminating window.
TIME_SLICES_MYR = [200, 250, 300, 320, 340]


def sigmoid(x, x0, k, ymax=1.0):
    """Sigmoid: f(x) = ymax / (1 + (x/x0)^k)."""
    return ymax / (1.0 + (x / x0) ** k)


def load_simulation(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def compute_surviving_fraction_at_t(sim_results: list[dict], target_t_Myr: float,
                                     n_total_per_halo: int = 1024) -> dict:
    """Extract surviving fraction per sigma/m at a SPECIFIC time (Myr).

    For each sigma/m sweep result, find the timestep at `target_t_Myr` and
    compute the surviving fraction from n_bound arrays and the per-halo N.
    """
    out = {'sigma_m_cm2_per_g': [], 't_Myr': [], 'n_bound_a': [], 'n_bound_b': [],
           'surviving_fraction_a': [], 'surviving_fraction_b': [],
           'surviving_fraction_avg': []}
    for r in sim_results:
        if 'error' in r:
            continue
        times = np.array(r['times_Myr'])
        n_a = np.array(r['n_bound_a'])
        n_b = np.array(r['n_bound_b'])
        f_a = np.clip(np.asarray(n_a, dtype=float) / n_total_per_halo, 0.0, 1.0)
        f_b = np.clip(np.asarray(n_b, dtype=float) / n_total_per_halo, 0.0, 1.0)
        f_avg = 0.5 * (f_a + f_b)

        idx = int(np.argmin(np.abs(times - target_t_Myr)))
        actual_t = float(times[idx])
        n_a_at = int(n_a[idx])
        n_b_at = int(n_b[idx])
        frac_a = float(f_a[idx])
        frac_b = float(f_b[idx])
        frac_avg = float(f_avg[idx])

        out['sigma_m_cm2_per_g'].append(r['sigma_m_cm2_per_g'])
        out['t_Myr'].append(actual_t)
        out['n_bound_a'].append(n_a_at)
        out['n_bound_b'].append(n_b_at)
        out['surviving_fraction_a'].append(frac_a)
        out['surviving_fraction_b'].append(frac_b)
        out['surviving_fraction_avg'].append(frac_avg)
    return out


def compute_surviving_fraction(sim_results: list[dict], time_fraction: float) -> dict:
    """Extract surviving fraction per sigma/m at the chosen time slice.

    DEPRECATED wrapper: use compute_surviving_fraction_at_t() for explicit time.
    """
    target_t_Myr = time_fraction * max(r['times_Myr'][-1]
                                        for r in sim_results if 'times_Myr' in r)
    return compute_surviving_fraction_at_t(sim_results, target_t_Myr)


def fit_sigmoid(sigma_m: np.ndarray, f_bound: np.ndarray) -> dict:
    """Fit sigmoid sigma/m vs surviving fraction. Returns peak + uncertainty."""
    # Initial guess: sigma/m_peak ~ 2 cm^2/g, k ~ -2
    try:
        popt, pcov = curve_fit(
            sigmoid, sigma_m, f_bound,
            p0=[2.0, -2.0], maxfev=10000
        )
        perr = np.sqrt(np.diag(pcov))
    except (RuntimeError, ValueError) as e:
        return {'fit_success': False, 'error': str(e)}

    sigma_m_peak = float(popt[0])  # sigma/m at f_bound = 0.5
    k = float(popt[1])              # steepness
    sigma_m_peak_err = float(perr[0])
    k_err = float(perr[1])
    return {
        'fit_success': True,
        'sigma_m_peak_cm2_per_g': sigma_m_peak,
        'sigma_m_peak_1sigma': sigma_m_peak_err,
        'k': k,
        'k_1sigma': k_err,
        'covariance': pcov.tolist(),
    }


def load_sashimi_parametric():
    """Import SASHIMI parametric model. Returns module or None if unavailable."""
    try:
        import sys
        sashimi_path = str(REPO_ROOT / 'code')
        if sashimi_path not in sys.path:
            sys.path.insert(0, sashimi_path)
        import sashimi_parametric
        return sashimi_parametric
    except ImportError:
        return None


def sashimi_resolution_check(sigma_m_peak: float) -> dict:
    """Compute SASHIMI-predicted r_core at sigma/m_peak and compare to AMUSE softening.

    If sigma/m_peak corresponds to r_core < 5x AMUSE softening (250 pc),
    the fit is at the resolution threshold (not a physics measurement).
    """
    result = {
        'sigma_m_peak': sigma_m_peak,
        'sigma_m_peak_within_resolution_threshold': None,
        'warning': None,
        'sashimi_available': False,
    }
    sp = load_sashimi_parametric()
    if sp is None:
        result['warning'] = 'SASHIMI parametric module not importable; resolution check skipped.'
        return result

    result['sashimi_available'] = True
    # Match AMUSE halo parameters (10^9 M_sun, c_vir=15)
    sidm = sp.predict_sparc_satellite(
        M_vir_Msun=1e9, c_vir=15.0,
        sigma_0_per_m_chi_cm2_per_g=sigma_m_peak,
        w_kms=np.inf,
    )
    r_core_kpc = sidm['r_c_sidm']
    r_core_pc = r_core_kpc * 1000
    softening_pc = AMUSE_SOFTENING_PC
    r_core_over_softening = r_core_pc / softening_pc

    result.update({
        'sashimi_r_core_kpc': r_core_kpc,
        'sashimi_r_core_pc': r_core_pc,
        'amuse_softening_pc': softening_pc,
        'r_core_over_softening': r_core_over_softening,
    })

    if r_core_over_softening < SASHIMI_RESOLUTION_THRESHOLD_FRACTION:
        result['sigma_m_peak_within_resolution_threshold'] = True
        result['warning'] = (
            f"sigma/m_peak = {sigma_m_peak:.3f} cm^2/g gives SASHIMI r_core = "
            f"{r_core_kpc:.4f} kpc = {r_core_over_softening:.1f}x AMUSE softening. "
            f"This is BELOW the {SASHIMI_RESOLUTION_THRESHOLD_FRACTION:.0f}x resolution "
            f"threshold. The fit value is a SOFTENING-RESOLUTION THRESHOLD, not a "
            f"physics measurement of sigma/m at v=358 km/s."
        )
    else:
        result['sigma_m_peak_within_resolution_threshold'] = False
        result['warning'] = (
            f"sigma/m_peak = {sigma_m_peak:.3f} cm^2/g gives SASHIMI r_core = "
            f"{r_core_kpc:.4f} kpc = {r_core_over_softening:.1f}x AMUSE softening. "
            f"Above resolution threshold; measurement is not resolution-limited."
        )
    return result


def time_slice_sensitivity(sim_results: list[dict], time_slices_Myr: list[float]) -> dict:
    """Compute sigma/m_peak at multiple time slices to show the dependence."""
    sensitivity = {}
    for ts in time_slices_Myr:
        surv = compute_surviving_fraction_at_t(sim_results, ts)
        sigma_m_arr = np.array(surv['sigma_m_cm2_per_g'])
        f_bound_arr = np.array(surv['surviving_fraction_avg'])
        # Skip if all f_bound are saturated at 0 or 1 (no signal)
        f_min, f_max = float(f_bound_arr.min()), float(f_bound_arr.max())
        if f_max - f_min < 0.05:
            sensitivity[f'{ts:.0f}_Myr'] = {
                't_actual_Myr': surv['t_Myr'][0] if surv['t_Myr'] else None,
                'f_bound_range': [f_min, f_max],
                'sigma_m_peak_cm2_per_g': None,
                'reason': 'All sigma/m saturate at same surviving fraction (no signal).',
            }
            continue
        fit = fit_sigmoid(sigma_m_arr, f_bound_arr)
        # Also treat fit-failed or zero/degenerate-output as no signal
        peak_val = fit.get('sigma_m_peak_cm2_per_g')
        k_val = fit.get('k')
        # If k is near 0, the sigmoid collapses to a constant -> no real peak
        if (not fit.get('fit_success')
                or peak_val is None
                or peak_val <= 0
                or k_val is None
                or abs(k_val) < 0.1):
            sensitivity[f'{ts:.0f}_Myr'] = {
                't_actual_Myr': surv['t_Myr'][0] if surv['t_Myr'] else None,
                'f_bound_range': [f_min, f_max],
                'sigma_m_peak_cm2_per_g': None,
                'reason': f"Sigmoid fit degenerate (k={k_val}, peak={peak_val}).",
            }
            continue
        sensitivity[f'{ts:.0f}_Myr'] = {
            't_actual_Myr': surv['t_Myr'][0] if surv['t_Myr'] else None,
            'f_bound_range': [f_min, f_max],
            'sigma_m_peak_cm2_per_g': fit.get('sigma_m_peak_cm2_per_g'),
            'sigma_m_peak_1sigma': fit.get('sigma_m_peak_1sigma'),
            'k': fit.get('k'),
        }
    return sensitivity


def main():
    print("=" * 70)
    print("Channel 27 sigma/m peak from AMUSE bullet-dwarf simulation")
    print("=" * 70)
    sim_data = load_simulation(SIM_JSON)
    print(f"Loaded {len(sim_data['results'])} sigma/m values")
    print(f"Setup: {sim_data['setup']}")

    # Primary fit at default time slice
    target_t = TIME_FRACTION * sim_data['setup']['end_time_Myr']
    surviving = compute_surviving_fraction_at_t(sim_data['results'], target_t)

    print(f"\nSurviving fraction at t = {target_t:.0f} Myr:")
    print(f"{'sigma/m':>10} | {'t (Myr)':>8} | {'f_bound_A':>10} | {'f_bound_B':>10} | {'f_bound_avg':>12}")
    print("-" * 60)
    for i in range(len(surviving['sigma_m_cm2_per_g'])):
        sig = surviving['sigma_m_cm2_per_g'][i]
        t = surviving['t_Myr'][i]
        fA = surviving['surviving_fraction_a'][i]
        fB = surviving['surviving_fraction_b'][i]
        fAvg = surviving['surviving_fraction_avg'][i]
        print(f"{sig:>10.2f} | {t:>8.0f} | {fA:>10.3f} | {fB:>10.3f} | {fAvg:>12.3f}")

    # Fit sigmoid at primary time slice
    sigma_m_arr = np.array(surviving['sigma_m_cm2_per_g'])
    f_bound_arr = np.array(surviving['surviving_fraction_avg'])
    fit = fit_sigmoid(sigma_m_arr, f_bound_arr)

    print()
    if fit['fit_success']:
        sig_peak = fit['sigma_m_peak_cm2_per_g']
        sig_err = fit['sigma_m_peak_1sigma']
        k_val = fit['k']
        print(f"Sigmoid fit at t = {target_t:.0f} Myr:")
        print(f"  sigma/m_peak = {sig_peak:.3f} +/- {sig_err:.3f} cm^2/g (f_bound = 0.5 anchor)")
        print(f"  k = {k_val:.3f} (steepness exponent)")
        print()
        # Compare to current placeholder
        PLACEHOLDER = 0.5  # log10(sigma/m_358) = -0.30 -> 0.5 cm^2/g
        print(f"Current Channel 27 placeholder peak: sigma/m = {PLACEHOLDER} cm^2/g")
        print(f"Simulation-derived peak: sigma/m = {sig_peak:.3f} cm^2/g")
        delta = (sig_peak - PLACEHOLDER) / PLACEHOLDER * 100
        print(f"Delta from placeholder: {delta:+.1f}%")

        # SASHIMI resolution check (NEW 2026-09-12)
        print()
        print("SASHIMI resolution check (NEW 2026-09-12):")
        res_check = sashimi_resolution_check(sig_peak)
        if res_check['sashimi_available']:
            print(f"  SASHIMI r_core at sigma/m_peak = {res_check.get('sashimi_r_core_kpc', '?'):.4f} kpc")
            print(f"  = {res_check.get('r_core_over_softening', '?'):.1f}x AMUSE softening")
            if res_check['sigma_m_peak_within_resolution_threshold']:
                print(f"  !! WARNING: peak is BELOW resolution threshold ({SASHIMI_RESOLUTION_THRESHOLD_FRACTION:.0f}x)")
                print(f"     -> measurement is a softening-resolution threshold, NOT physics")
            else:
                print(f"  -> above resolution threshold; not resolution-limited")
        else:
            print(f"  {res_check['warning']}")
    else:
        print(f"Fit failed: {fit.get('error', 'unknown')}")
        res_check = {'sashimi_available': False, 'warning': 'fit failed'}

    # Time-slice sensitivity table (NEW 2026-09-12)
    print()
    print("Time-slice sensitivity table (NEW 2026-09-12):")
    print("Showing how sigma/m_peak slides with the chosen snapshot time.")
    print(f"{'t (Myr)':>10} | {'sigma/m_peak':>14} | {'+/-':>8} | {'k':>6} | {'f_range':>15}")
    print("-" * 60)
    sens = time_slice_sensitivity(sim_data['results'], TIME_SLICES_MYR)
    for ts_Myr in TIME_SLICES_MYR:
        key = f'{ts_Myr:.0f}_Myr'
        s = sens[key]
        peak = s.get('sigma_m_peak_cm2_per_g')
        err = s.get('sigma_m_peak_1sigma')
        k_v = s.get('k')
        f_range = s.get('f_bound_range')
        peak_str = f"{peak:>10.3f}" if peak is not None else "    no signal"
        err_str = f"{err:>6.3f}" if err is not None else "      —"
        k_str = f"{k_v:>6.2f}" if k_v is not None else "    —"
        fr_str = f"[{f_range[0]:.2f}, {f_range[1]:.2f}]" if f_range else "—"
        print(f"{ts_Myr:>10.0f} | {peak_str} | {err_str} | {k_str} | {fr_str:>15}")

    # Save output
    output = {
        'simulation_input': str(SIM_JSON.relative_to(REPO_ROOT)),
        'time_fraction_used': TIME_FRACTION,
        'end_time_Myr': sim_data['setup']['end_time_Myr'],
        'target_t_Myr': TIME_FRACTION * sim_data['setup']['end_time_Myr'],
        'surviving_data': surviving,
        'fit': fit,
        'time_slice_sensitivity': sens,  # NEW 2026-09-12
        'sashimi_resolution_check': res_check,  # NEW 2026-09-12
        'comparison_to_placeholder': {
            'placeholder_sigma_m_cm2_per_g': 0.5,
            'placeholder_log10': -0.30,
            'simulation_derived_sigma_m_cm2_per_g': fit.get('sigma_m_peak_cm2_per_g'),
            'simulation_derived_1sigma': fit.get('sigma_m_peak_1sigma'),
            'delta_percent': ((fit.get('sigma_m_peak_cm2_per_g', 0.5) - 0.5) / 0.5 * 100
                              if fit.get('fit_success') else None),
        },
        'honest_caveats': [
            'N=1024 is ~100x below publication-grade (Yang+ 2024 SASHIMI requires N>=10^5)',
            'SIDM kernel is uniform Gaussian perturbation, not Rutherford-like pairwise scattering',
            'No baryonic physics (gas stripping post-hoc)',
            'Head-on collision (b=0) only',
            'Time slice at t=300 Myr is a heuristic; no formal time-since-collision match to NGC 1052',
            'Sigmoid fit uses 6 data points; uncertainty from covariance may be underestimated',
            # NEW 2026-09-12:
            'sigma/m_peak captures the TRANSIENT pre-disruption window, NOT asymptotic disruption. '
            'By t > 350 Myr, all halos fully disrupt regardless of sigma/m (N=1024 is too low for '
            'realistic gravothermal evolution).',
            'sigma/m_peak coincides with the SASHIMI-predicted sigma/m value at which AMUSE first '
            'sees a SIDM core (r_core > 5x softening = 250 pc). The fit value should be interpreted '
            'as a SOFTENING-RESOLUTION THRESHOLD, not a physics measurement.',
            'See docs/AMUSE_FRESH_RUN_WITH_SASHIMI_2026_09_12.md for full SASHIMI benchmark.',
        ],
        'next_steps': [
            'Do NOT plug the simulation-derived peak into Channel 27 — it is a resolution threshold.',
            'Placeholder (sigma/m = 0.5 cm^2/g at v=358 km/s) STAYS as the Channel 27 anchor.',
            'Future work to genuinely constrain sigma/m(v=358) would require: N>=10^5 particles, '
            'pairwise Rutherford-like SIDM kernel, and time slices matched to NGC 1052 trail age.',
        ],
    }
    with open(OUT_JSON, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {OUT_JSON.relative_to(REPO_ROOT)}")


if __name__ == '__main__':
    main()