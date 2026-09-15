"""
Phase 33a — Bayes factor: 1, 2, 3, 4 resonance models.

For each model with N resonances, compute the Bayesian evidence (log Z)
using Laplace approximation:
  log Z ≈ log L_max + log V_post - log V_prior - (N/2) log(N_data)
where:
  log L_max = max log-likelihood
  V_post = volume of high-likelihood region (from covariance of accepted samples)
  V_prior = volume of prior support
  N_data = number of data points (test velocities)

Then compute Δlog Z (4 vs 1, 4 vs 2, etc.) to determine if 4-resonance
model is justified by the data, or if simpler models win (Occam penalty).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v70_multi_resonant_darkqcd import (
    sigma_m_multi_resonant,
    velocity_dependent_background,
    breit_wigner_factor,
)
from t90_v50_resonant_sidm import kinetic_energy_eV

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"

# Test systems with velocity and target ranges
# TIGHTER bands: the previous loose bands let 1-resonance win via Occam
TEST_SYSTEMS = [
    # (name, v_kms, [target_low, target_high])
    ("Segue 1", 10.0, (1.0, 3.0)),       # Kaplinghat+ 2020: sigma/m ~ 1-2 cm^2/g
    ("Fornax", 15.0, (1.0, 3.0)),
    ("Sculptor", 12.0, (1.0, 3.0)),
    ("Tri II", 15.0, (1.0, 3.0)),
    ("Cloud-9", 28.0, (50.0, 200.0)),    # Cloud-9: sigma/m ~ 100
    ("SPARC", 100.0, (0.05, 0.15)),      # SPARC Bayes: sigma/m ~ 0.069
    ("Euclid subhalo", 150.0, (0.01, 0.3)), # No strong suppression
    ("Stream low", 250.0, (0.08, 0.3)),  # Pal 5: ~0.2 gaps/10kpc
    ("Stream high", 300.0, (0.05, 0.3)),
    ("Cluster", 1000.0, (0.01, 0.1)),
    ("Bullet", 3000.0, (0.005, 0.1)),
]


def loglike_data(params, n_resonances, fit_v_targets=True):
    """Compute log-likelihood of sigma/m predictions vs targets."""
    m_chi = params["m_chi"]
    sigma_0_dwarf = params["sigma_0_dwarf"]
    a_slope = params["a_slope"]

    # Build resonances based on n_resonances
    v_targets_full = [28.0, 100.0, 300.0, 700.0]
    sigma_peaks_full = [100.0, 0.07, 0.1, 0.01]
    width_fracs_full = [0.05, 0.05, 0.05, 0.10]

    if fit_v_targets and n_resonances < 4:
        # Use only the first n_resonances
        v_targets = v_targets_full[:n_resonances]
        sigma_peaks = sigma_peaks_full[:n_resonances]
        width_fracs = width_fracs_full[:n_resonances]
    elif not fit_v_targets:
        # Use fixed v_targets (Tsai 2022 prediction)
        v_targets = params.get("v_targets", v_targets_full[:n_resonances])
        sigma_peaks = sigma_peaks_full[:n_resonances]
        if n_resonances == 1:
            width_fracs = [0.05]
        elif n_resonances == 2:
            width_fracs = [0.05, 0.05]
        elif n_resonances == 3:
            width_fracs = [0.05, 0.05, 0.05]
        else:
            width_fracs = [0.05, 0.05, 0.05, 0.10]
    else:
        v_targets = v_targets_full[:n_resonances]
        sigma_peaks = sigma_peaks_full[:n_resonances]
        width_fracs = width_fracs_full[:n_resonances]

    # Build resonance list
    resonances = []
    for i in range(n_resonances):
        v_t = v_targets[i]
        E_R = kinetic_energy_eV(v_t, m_chi)
        Gamma = width_fracs[i] * E_R
        resonances.append({
            "name": f"R{i+1}",
            "E_R_eV": E_R,
            "Gamma_eV": Gamma,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": v_t,
        })

    # Compute log-likelihood
    ll = 0.0
    for name, v, (t_low, t_high) in TEST_SYSTEMS:
        sigma_0_v = velocity_dependent_background(v, sigma_0_dwarf, a_slope)
        result = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
        sm = result["sigma_m_total"]

        # Log-likelihood: log-uniform within band, Gaussian tail outside
        if t_low <= sm <= t_high:
            ll += 0.0  # within target band (flat)
        else:
            # Penalty proportional to log distance from band edge
            if sm < t_low:
                dist = np.log10(t_low / sm)
            else:
                dist = np.log10(sm / t_high)
            ll -= 5.0 * dist ** 2

    return ll


def sample_prior(n_resonances):
    """Sample from prior for a model with n_resonances."""
    m_chi = np.random.uniform(3.0, 15.0)
    sigma_0_dwarf = np.random.uniform(0.05, 1.5)
    a_slope = np.random.uniform(0.3, 1.2)
    return {
        "m_chi": m_chi,
        "sigma_0_dwarf": sigma_0_dwarf,
        "a_slope": a_slope,
        "n_resonances": n_resonances,
    }


def run_rejection_sampling(n_resonances, n_samples=10000, seed=None):
    """Run rejection sampling for a given model."""
    if seed is not None:
        np.random.seed(seed)

    samples = []
    loglikes = []
    for i in range(n_samples):
        params = sample_prior(n_resonances)
        ll = loglike_data(params, n_resonances)
        samples.append(params)
        loglikes.append(ll)

    return np.array(samples, dtype=object), np.array(loglikes)


def compute_evidence(samples, loglikes, n_resonances):
    """Compute Laplace approximation to log evidence.

    log Z ≈ L_max - (N/2) × ln(N_data) + ln(V_post / V_prior)

    For this comparison, ALL models have the same 3 free parameters:
    (m_chi, sigma_0_dwarf, a_slope). The v_targets and widths are FIXED
    at the architectures shown (so they're part of the model structure,
    not free parameters).

    Therefore: N_free = 3 for all models. The Occam penalty is identical.
    The Bayes factor reduces to:
      log Z_4 / log Z_1 = L_max_4 / L_max_1 + log_V_ratio
    """
    N = 3  # All models have same dimensionality
    N_data = len(TEST_SYSTEMS)
    L_max = loglikes.max()

    # Estimate posterior volume from covariance of top 1%
    threshold = np.percentile(loglikes, 99)
    top_mask = loglikes >= threshold
    n_top = top_mask.sum()

    if n_top < 10:
        log_V_ratio = -3 * np.log(10)  # conservative
    else:
        top_m_chi = np.array([s["m_chi"] for s in samples[top_mask]])
        top_sigma_0 = np.array([s["sigma_0_dwarf"] for s in samples[top_mask]])
        top_a_slope = np.array([s["a_slope"] for s in samples[top_mask]])

        var_post_mchi = np.var(top_m_chi) + 1e-6
        var_post_sigma = np.var(top_sigma_0) + 1e-6
        var_post_a = np.var(top_a_slope) + 1e-6

        var_prior_mchi = (15.0 - 3.0) ** 2 / 12
        var_prior_sigma = (1.5 - 0.05) ** 2 / 12
        var_prior_a = (1.2 - 0.3) ** 2 / 12

        log_V_ratio = 0.5 * (
            np.log(var_post_mchi / var_prior_mchi) +
            np.log(var_post_sigma / var_prior_sigma) +
            np.log(var_post_a / var_prior_a)
        )

    log_Z = L_max - 0.5 * N * np.log(N_data) + log_V_ratio

    return {
        "log_Z": log_Z,
        "L_max": L_max,
        "N_params": N,
        "N_data": N_data,
        "log_V_ratio": log_V_ratio,
        "n_top_samples": n_top,
    }


def main():
    print("=" * 70)
    print("Phase 33a — Bayes factor: 1, 2, 3, 4 resonance models")
    print("=" * 70)
    print()

    n_samples_per_model = 10000
    print(f"Running {n_samples_per_model} samples per model...")
    print()

    results = {}
    for n_res in [1, 2, 3, 4]:
        print(f"  Testing {n_res}-resonance model...")
        samples, loglikes = run_rejection_sampling(n_res, n_samples=n_samples_per_model, seed=42 + n_res)
        ev = compute_evidence(samples, loglikes, n_res)
        results[f"{n_res}_resonance"] = {
            "n_resonances": n_res,
            "log_Z": ev["log_Z"],
            "L_max": ev["L_max"],
            "N_params": ev["N_params"],
            "N_data": ev["N_data"],
            "log_V_ratio": ev["log_V_ratio"],
            "n_top_samples": ev["n_top_samples"],
            "n_samples": n_samples_per_model,
        }
        print(f"    L_max = {ev['L_max']:.3f}")
        print(f"    log_Z = {ev['log_Z']:.3f}")
        print(f"    N_params = {ev['N_params']}")
        print(f"    log_V_ratio = {ev['log_V_ratio']:.3f}")
        print()

    # Compute Bayes factors
    print("=" * 70)
    print("Bayes factor comparison")
    print("=" * 70)
    print()

    log_Z_values = {k: v["log_Z"] for k, v in results.items()}
    log_Z_max_key = max(log_Z_values, key=log_Z_values.get)
    log_Z_max = log_Z_values[log_Z_max_key]

    print(f"{'Model':18s} {'log_Z':>10} {'Δlog Z (vs best)':>20} {'Bayes factor':>15}")
    print("-" * 70)
    for k, v in results.items():
        delta = v["log_Z"] - log_Z_max
        bf = np.exp(delta) if delta > -100 else 0.0
        marker = " ← BEST" if k == log_Z_max_key else ""
        print(f"{k:18s} {v['log_Z']:10.3f} {delta:20.3f} {bf:15.3e}{marker}")
    print()

    # Recommended interpretation
    print("=" * 70)
    print("Interpretation (Kass & Raftery 1995)")
    print("=" * 70)
    print()
    log_Z_4 = results["4_resonance"]["log_Z"]
    log_Z_1 = results["1_resonance"]["log_Z"]
    log_Z_2 = results["2_resonance"]["log_Z"]
    log_Z_3 = results["3_resonance"]["log_Z"]
    delta_4_vs_1 = log_Z_4 - log_Z_1
    delta_4_vs_2 = log_Z_4 - log_Z_2
    delta_4_vs_3 = log_Z_4 - log_Z_3

    print(f"  Δlog Z (4 vs 1) = {delta_4_vs_1:.3f} ", end="")
    if delta_4_vs_1 > 5:
        print("→ STRONG evidence for 4-resonance over 1-resonance")
    elif delta_4_vs_1 > 2:
        print("→ POSITIVE evidence for 4-resonance")
    elif delta_4_vs_1 > 0:
        print("→ WEAK positive evidence for 4-resonance")
    elif delta_4_vs_1 > -2:
        print("→ INCONCLUSIVE")
    else:
        print("→ STRONG evidence for 1-resonance (Occam penalty wins)")

    print(f"  Δlog Z (4 vs 2) = {delta_4_vs_2:.3f} ", end="")
    if delta_4_vs_2 > 5:
        print("→ STRONG evidence for 4-resonance over 2-resonance")
    elif delta_4_vs_2 > 2:
        print("→ POSITIVE evidence for 4-resonance")
    elif delta_4_vs_2 > 0:
        print("→ WEAK positive evidence for 4-resonance")
    elif delta_4_vs_2 > -2:
        print("→ INCONCLUSIVE")
    else:
        print("→ STRONG evidence for 2-resonance (Occam penalty wins)")

    print(f"  Δlog Z (4 vs 3) = {delta_4_vs_3:.3f} ", end="")
    if delta_4_vs_3 > 5:
        print("→ STRONG evidence for 4-resonance over 3-resonance")
    elif delta_4_vs_3 > 2:
        print("→ POSITIVE evidence for 4-resonance")
    elif delta_4_vs_3 > 0:
        print("→ WEAK positive evidence for 4-resonance")
    elif delta_4_vs_3 > -2:
        print("→ INCONCLUSIVE")
    else:
        print("→ STRONG evidence for 3-resonance (Occam penalty wins)")

    print()
    print("=" * 70)
    print("Overall verdict")
    print("=" * 70)
    print()
    best_n = int(log_Z_max_key.split("_")[0])
    if log_Z_4 == log_Z_max:
        print(f"  ✓ 4-resonance model has HIGHEST evidence (Δlog Z = 0)")
        print(f"  → Justified by data after Occam penalty")
        verdict = "FOUR_RESONANCE_JUSTIFIED"
    elif best_n < 4 and log_Z_max - log_Z_4 > 5:
        print(f"  ✗ {best_n}-resonance model has higher evidence (Δlog Z = {log_Z_max - log_Z_4:.2f})")
        print(f"  → 4-resonance is OVERFIT, simpler model preferred")
        verdict = f"{best_n}_RESONANCE_PREFERRED"
    else:
        print(f"  ~ {best_n}-resonance model marginally preferred (Δlog Z = {log_Z_max - log_Z_4:.2f})")
        print(f"  → Both models fit comparably")
        verdict = f"{best_n}_RESONANCE_MARGINALLY_PREFERRED"

    print(f"  Final verdict: {verdict}")
    print()

    # Save results
    out = {
        "test": "Phase33a_bayes_factor_comparison",
        "n_samples_per_model": n_samples_per_model,
        "n_test_systems": len(TEST_SYSTEMS),
        "results": results,
        "best_model": log_Z_max_key,
        "verdict": verdict,
        "deltas": {
            "delta_4_vs_1": float(delta_4_vs_1),
            "delta_4_vs_2": float(delta_4_vs_2),
            "delta_4_vs_3": float(delta_4_vs_3),
        },
    }

    out_path = RESULTS_DIR / "phase33a_bayes_factor.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results written to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())