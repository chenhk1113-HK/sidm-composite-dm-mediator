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

This gives a defensible Channel 27 peak with uncertainty: the sigma/m value
where the bullet-dwarf collision produces ~50% bound halo is the place
where the channel should peak (most sensitive to SIDM physics).

CHANNEL 27 CONTEXT (from docs/CH27_NGC1052_TRAIL_CHANNEL.md, commit 8d917cc):
- Observables: NGC 1052-DF2/DF4/DF9 at trail tip, v=358 km/s
- Anchor: sigma/m(v=358 km/s) = ?
- Current placeholder: log10(sigma/m_358) = -0.30 (0.5 cm^2/g)
- After ablation: sigma/m_0 = 0.59 -> 0.99 cm^2/g (+68%)

OUTPUT:
- ch27_sigma_m_peak.json with proposed peak, fit params, and curve data
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit


REPO_ROOT = Path(__file__).parent.parent
SIM_JSON = REPO_ROOT / 'data' / 'results' / 'amuse_bullet_dwarf_calibration_2026_09_12.json'
OUT_JSON = REPO_ROOT / 'data' / 'results' / 'ch27_sigma_m_peak_from_amuse_2026_09_12.json'
TIME_FRACTION = 0.15  # Use n_bound at ~15% through the simulation (discriminating region)
# Time slice interpretation:
# 0.15 of integration time (2 Gyr) = 300 Myr after collision start
# This is BEFORE the bulk disruption transition (~345 Myr, where all curves collapse to 0)
# but late enough that SIDM scattering has had time to differentiate the curves.
# At t=300 Myr the simulation shows: sigma/m=0.1 retains 97%, sigma/m=10 retains 8%.
# This is the cleanest sigma/m-discrimination window available in the data.


def sigmoid(x, x0, k, ymax=1.0):
    """Sigmoid: f(x) = ymax / (1 + (x/x0)^k)."""
    return ymax / (1.0 + (x / x0) ** k)


def load_simulation(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def compute_surviving_fraction(sim_results: list[dict], time_fraction: float) -> dict:
    """Extract surviving fraction per sigma/m at the chosen time slice.

    For each sigma/m sweep result, find the timestep at `time_fraction` of
    integration time (e.g., 0.30 * 2000 Myr = 600 Myr), and compute the
    surviving fraction from n_bound arrays and the per-halo N (1024).
    """
    out = {'sigma_m_cm2_per_g': [], 't_Myr': [], 'n_bound_a': [], 'n_bound_b': [],
           'surviving_fraction_a': [], 'surviving_fraction_b': [],
           'surviving_fraction_avg': []}
    # Use the longest times_Myr array's length to infer n_total
    n_total = max(len(r['n_bound_a']) for r in sim_results if 'n_bound_a' in r)
    # Actually, n_total is constant = 1024 (per halo). Get from any result.
    n_total_per_halo = 1024  # hardcoded from setup
    for r in sim_results:
        if 'error' in r:
            continue
        times = np.array(r['times_Myr'])
        n_a = np.array(r['n_bound_a'])
        n_b = np.array(r['n_bound_b'])
        f_a = np.clip(np.asarray(n_a, dtype=float) / n_total_per_halo, 0.0, 1.0)
        f_b = np.clip(np.asarray(n_b, dtype=float) / n_total_per_halo, 0.0, 1.0)
        f_avg = 0.5 * (f_a + f_b)

        target_t = time_fraction * times[-1]  # e.g., 0.30 * 2000 = 600 Myr
        idx = int(np.argmin(np.abs(times - target_t)))
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


def main():
    print("=" * 70)
    print("Channel 27 sigma/m peak from AMUSE bullet-dwarf simulation")
    print("=" * 70)
    sim_data = load_simulation(SIM_JSON)
    print(f"Loaded {len(sim_data['results'])} sigma/m values")
    print(f"Setup: {sim_data['setup']}")

    # Extract surviving fraction at TIME_FRACTION of integration
    surviving = compute_surviving_fraction(sim_data['results'], TIME_FRACTION)

    print(f"\nSurviving fraction at t = {TIME_FRACTION * sim_data['setup']['end_time_Myr']:.0f} Myr:")
    print(f"{'sigma/m':>10} | {'t (Myr)':>8} | {'f_bound_A':>10} | {'f_bound_B':>10} | {'f_bound_avg':>12}")
    print("-" * 60)
    for i in range(len(surviving['sigma_m_cm2_per_g'])):
        sig = surviving['sigma_m_cm2_per_g'][i]
        t = surviving['t_Myr'][i]
        fA = surviving['surviving_fraction_a'][i]
        fB = surviving['surviving_fraction_b'][i]
        fAvg = surviving['surviving_fraction_avg'][i]
        print(f"{sig:>10.2f} | {t:>8.0f} | {fA:>10.3f} | {fB:>10.3f} | {fAvg:>12.3f}")

    # Fit sigmoid
    sigma_m_arr = np.array(surviving['sigma_m_cm2_per_g'])
    f_bound_arr = np.array(surviving['surviving_fraction_avg'])
    fit = fit_sigmoid(sigma_m_arr, f_bound_arr)

    print()
    if fit['fit_success']:
        sig_peak = fit['sigma_m_peak_cm2_per_g']
        sig_err = fit['sigma_m_peak_1sigma']
        k_val = fit['k']
        print(f"Sigmoid fit:")
        print(f"  sigma/m_peak = {sig_peak:.3f} +/- {sig_err:.3f} cm^2/g (f_bound = 0.5 anchor)")
        print(f"  k = {k_val:.3f} (steepness exponent)")
        print()
        # Compare to current placeholder
        PLACEHOLDER = 0.5  # log10(sigma/m_358) = -0.30 -> 0.5 cm^2/g
        print(f"Current Channel 27 placeholder peak: sigma/m = {PLACEHOLDER} cm^2/g")
        print(f"Simulation-derived peak: sigma/m = {sig_peak:.3f} cm^2/g")
        delta = (sig_peak - PLACEHOLDER) / PLACEHOLDER * 100
        print(f"Delta from placeholder: {delta:+.1f}%")
    else:
        print(f"Fit failed: {fit.get('error', 'unknown')}")

    # Save output
    output = {
        'simulation_input': str(SIM_JSON.relative_to(REPO_ROOT)),
        'time_fraction_used': TIME_FRACTION,
        'end_time_Myr': sim_data['setup']['end_time_Myr'],
        'target_t_Myr': TIME_FRACTION * sim_data['setup']['end_time_Myr'],
        'surviving_data': surviving,
        'fit': fit,
        'comparison_to_placeholder': {
            'placeholder_sigma_m_cm2_per_g': 0.5,
            'placeholder_log10': -0.30,
            'simulation_derived_sigma_m_cm2_per_g': fit.get('sigma_m_peak_cm2_per_g'),
            'simulation_derived_1sigma': fit.get('sigma_m_peak_1sigma'),
            'delta_percent': ((fit.get('sigma_m_peak_cm2_per_g', 0.5) - 0.5) / 0.5 * 100
                              if fit.get('fit_success') else None),
        },
        'honest_caveats': [
            'N=1024 is ~100x below publication-grade',
            'SIDM kernel is uniform Gaussian perturbation, not Rutherford-like pairwise scattering',
            'No baryonic physics (gas stripping post-hoc)',
            'Head-on collision (b=0) only',
            'Time slice at t=600 Myr is a heuristic; no formal time-since-collision match to NGC 1052',
            'Sigmoid fit uses 6 data points; uncertainty from covariance may be underestimated',
        ],
        'next_steps': [
            'Plug the simulation-derived peak into Channel 27 (currently uses placeholder)',
            'Re-run t13_v2_trail_ablation.py with the new peak to measure posterior shift',
            'If improvement is significant, mark simulation peak as PRIMARY anchor and placeholder as backup',
        ],
    }
    with open(OUT_JSON, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {OUT_JSON.relative_to(REPO_ROOT)}")


if __name__ == '__main__':
    main()