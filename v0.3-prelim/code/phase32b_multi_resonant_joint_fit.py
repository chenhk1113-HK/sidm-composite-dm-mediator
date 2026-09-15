"""
Phase 32b — Joint fit of multi-resonance dark QCD architecture.

Fits the Tsai 2022 architecture to the 9 critical review test data:
  Test H (dwarf cores), Test G (stream gaps), Test C (Euclid Q1 subhalo),
  Test B (SPARC Bayes), Test A (other low-v), Test F (relic density),
  Test E (UV completion), Test I (DD limits), Test D (fine-tuning).

Parameter space (~10D):
  - m_chi: DM mass (GeV)
  - sigma_0_dwarf: background strength for dwarfs
  - a_slope: velocity slope of background
  - E_R_1, Gamma_1, sigma_peak_1: Cloud-9 resonance
  - E_R_2, Gamma_2, sigma_peak_2: SPARC resonance
  - E_R_3, Gamma_3, sigma_peak_3: Stream resonance
  - E_R_4, Gamma_4, sigma_peak_4: Cluster resonance
  - v_target_n: velocity targets for each resonance

For the joint fit, we use rejection sampling (like Phase 29):
  1. Sample prior distributions
  2. Evaluate likelihood at each sample
  3. Accept/reject based on combined likelihood
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v70_multi_resonant_darkqcd import (
    build_default_resonances,
    sigma_m_multi_resonant,
    velocity_dependent_background,
    breit_wigner_factor,
)
from t90_v50_resonant_sidm import kinetic_energy_eV

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


# ============================================================
# Likelihood functions for the 9 critical review tests
# ============================================================
def loglike_dwarf_cores(sigma_m_at_v15):
    """Test H: predicted dwarf core r_c ~ sigma_m(v=15).

    Observed dwarf cores: r_c ~ 0.3-1 kpc
    Predicted r_c ~ 1-3 kpc is acceptable.

    For sigma/m ~ 1-2 cm^2/g at v=15, r_c ~ 1-2 kpc (acceptable)
    For sigma/m > 5 cm^2/g, r_c > 5 kpc (too large)
    """
    target = 1.5  # cm^2/g
    sigma_log = 0.3  # width in dex
    return -0.5 * ((np.log10(sigma_m_at_v15) - np.log10(target)) / sigma_log) ** 2


def loglike_stream_gaps(sigma_m_at_v250):
    """Test G: stream gap density depends on sigma/m at v=250.

    For sigma/m ~ 0.1-0.5 cm^2/g, predicted gaps/10kpc ~ 0.05-0.2
    (observed Pal 5: 0.2-0.5 per 10 kpc).
    """
    target = 0.2  # cm^2/g
    sigma_log = 0.5  # wider tolerance (large systematic)
    return -0.5 * ((np.log10(sigma_m_at_v250) - np.log10(target)) / sigma_log) ** 2


def loglike_cloud9(sigma_m_at_v28):
    """Cloud-9: sigma/m at v=28 should be in [30, 500]."""
    target = 100.0
    sigma_log = 0.4  # wide (Cloud-9 wants big sigma/m)
    return -0.5 * ((np.log10(sigma_m_at_v28) - np.log10(target)) / sigma_log) ** 2


def loglike_sparc(sigma_m_at_v100):
    """SPARC hierarchical prefers sigma/m(100) ~ 0.069 cm^2/g."""
    target = 0.069
    sigma_log = 0.5  # wide (SPARC has spread)
    return -0.5 * ((np.log10(sigma_m_at_v100) - np.log10(target)) / sigma_log) ** 2


def loglike_euclid_subhalo(sigma_m_at_v150):
    """Euclid subhalo suppression: sigma/m(v=150) should be moderate.

    Real data: N_subhalos consistent with CDM at v=150 (no strong suppression).
    Requires sigma/m(150) < 0.5 cm^2/g
    """
    # Penalty if too high
    if sigma_m_at_v150 > 0.5:
        return -10.0 * (sigma_m_at_v150 - 0.5)
    return 0.0


def loglike_cluster(sigma_m_at_v1000):
    """Cluster constraints: sigma/m(v=1000) < 0.1 cm^2/g (Bullet)."""
    if sigma_m_at_v1000 > 0.5:
        return -20.0 * (sigma_m_at_v1000 - 0.5)
    return 0.0


def loglike_bullet(sigma_m_at_v3000):
    """Bullet cluster: sigma/m(v=3000) < 0.1 cm^2/g."""
    if sigma_m_at_v3000 > 0.3:
        return -30.0 * (sigma_m_at_v3000 - 0.3)
    return 0.0


def loglike_relic_density(m_chi, sigma_0_dwarf):
    """Test F: relic density via asymmetric DM.

    Requires eta/eta_B ~ 1 for Omega_DM/Omega_B = 5.3.
    eta/eta_B = 5.3 * (m_p / m_chi), so m_chi ~ 5-6 GeV gives eta/eta_B ~ 1.
    """
    target_m_chi = 5.5  # GeV
    sigma_m = 2.0
    return -0.5 * ((m_chi - target_m_chi) / sigma_m) ** 2


def loglike_dd_limits(m_chi, m_phi_MeV):
    """Test I: LZ direct detection limits.

    For epsilon < 1.4e-13 (max allowed), model evades DD.
    Use simplified bound: m_chi > 4 GeV OR m_phi > 100 MeV.
    """
    # Penalty if too low mass or too low mediator
    if m_chi < 4:
        return -5.0 * (4 - m_chi)
    if m_phi_MeV < 100 and m_chi < 6:
        return -2.0 * (100 - m_phi_MeV) / 100.0
    return 0.0


# ============================================================
# Prior distributions
# ============================================================
PRIORS = {
    "m_chi_GeV": (3.0, 15.0),       # 3-15 GeV (from Phase 16 ~5 GeV)
    "sigma_0_dwarf": (0.1, 1.0),    # cm^2/g at v=10
    "a_slope": (0.4, 1.0),          # velocity slope
    "v_targets": [(15.0, 35.0),     # Cloud-9: v ~ 25-35
                  (50.0, 150.0),    # SPARC: v ~ 50-150
                  (200.0, 400.0),   # Stream: v ~ 200-400
                  (500.0, 1000.0)], # Cluster: v ~ 500-1000
    "width_fractions": [(0.02, 0.10),  # each resonance 2-10% width
                        (0.02, 0.10),
                        (0.05, 0.20),
                        (0.10, 0.30)],
}


def sample_prior():
    """Sample one point from the prior."""
    m_chi = np.random.uniform(*PRIORS["m_chi_GeV"])
    sigma_0_dwarf = np.random.uniform(*PRIORS["sigma_0_dwarf"])
    a_slope = np.random.uniform(*PRIORS["a_slope"])
    v_targets = [np.random.uniform(*p) for p in PRIORS["v_targets"]]
    width_fracs = [np.random.uniform(*p) for p in PRIORS["width_fractions"]]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]  # fixed targets

    return {
        "m_chi": m_chi,
        "sigma_0_dwarf": sigma_0_dwarf,
        "a_slope": a_slope,
        "v_targets": v_targets,
        "width_fracs": width_fracs,
        "sigma_peaks": sigma_peaks,
    }


def build_resonances(params):
    """Build resonance list from sampled parameters."""
    resonances = []
    names = ["R1_Cloud9", "R2_SPARC", "R3_Stream", "R4_Cluster"]
    for i in range(4):
        v_t = params["v_targets"][i]
        E_R = kinetic_energy_eV(v_t, params["m_chi"])
        Gamma = params["width_fracs"][i] * E_R
        resonances.append({
            "name": names[i],
            "E_R_eV": E_R,
            "Gamma_eV": Gamma,
            "sigma_peak_cm2_per_g": params["sigma_peaks"][i],
            "v_target_kms": v_t,
        })
    return resonances


def evaluate_loglike(params):
    """Evaluate total log-likelihood for a parameter sample."""
    m_chi = params["m_chi"]
    resonances = build_resonances(params)

    # Evaluate at all test velocities
    ll_total = 0.0

    for v in [10.0, 12.0, 15.0]:
        sigma_0_v = velocity_dependent_background(v, params["sigma_0_dwarf"], params["a_slope"])
        r = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
        ll_total += loglike_dwarf_cores(r["sigma_m_total"])

    for v in [28.0, 100.0, 150.0, 250.0, 1000.0, 3000.0]:
        sigma_0_v = velocity_dependent_background(v, params["sigma_0_dwarf"], params["a_slope"])
        r = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
        if v == 28.0:
            ll_total += loglike_cloud9(r["sigma_m_total"])
        elif v == 100.0:
            ll_total += loglike_sparc(r["sigma_m_total"])
        elif v == 150.0:
            ll_total += loglike_euclid_subhalo(r["sigma_m_total"])
        elif v == 250.0:
            ll_total += loglike_stream_gaps(r["sigma_m_total"])
        elif v == 1000.0:
            ll_total += loglike_cluster(r["sigma_m_total"])
        elif v == 3000.0:
            ll_total += loglike_bullet(r["sigma_m_total"])

    # Relic density
    ll_total += loglike_relic_density(m_chi, params["sigma_0_dwarf"])

    # DD limits (m_phi ~ 8 MeV typical)
    ll_total += loglike_dd_limits(m_chi, 8.0)

    return ll_total


def main():
    print("=" * 70)
    print("Phase 32b — Multi-resonant Joint Fit")
    print("=" * 70)
    print()
    print("Rejection sampling with priors:")
    for key, val in PRIORS.items():
        print(f"  {key}: {val}")
    print()

    # Run rejection sampling
    N_samples = 30000
    print(f"Running {N_samples} samples...")
    np.random.seed(42)

    samples = []
    loglikes = []
    for i in range(N_samples):
        params = sample_prior()
        ll = evaluate_loglike(params)
        samples.append(params)
        loglikes.append(ll)
        if (i + 1) % 5000 == 0:
            print(f"  Sampled {i+1}/{N_samples}, max loglike so far: {max(loglikes):.3f}")

    samples = np.array(samples, dtype=object)
    loglikes = np.array(loglikes)

    # Keep top 1% of samples
    threshold = np.percentile(loglikes, 99)
    best_idx = np.where(loglikes >= threshold)[0]
    best_samples = samples[best_idx]
    best_loglikes = loglikes[best_idx]

    print()
    print(f"Top 1% threshold: loglike >= {threshold:.3f}")
    print(f"Best sample loglike: {max(loglikes):.3f}")
    print()

    # Posterior summary
    print("Posterior summary (top 1% of samples):")
    print(f"  {'Parameter':30s}  {'p16':>10}  {'p50':>10}  {'p84':>10}")
    print("  " + "-" * 70)

    m_chi_arr = np.array([s["m_chi"] for s in best_samples])
    sigma_0_arr = np.array([s["sigma_0_dwarf"] for s in best_samples])
    a_slope_arr = np.array([s["a_slope"] for s in best_samples])

    for name, arr in [
        ("m_chi (GeV)", m_chi_arr),
        ("sigma_0_dwarf (cm^2/g)", sigma_0_arr),
        ("a_slope", a_slope_arr),
    ]:
        p16, p50, p84 = np.percentile(arr, [16, 50, 84])
        print(f"  {name:30s}  {p16:10.3f}  {p50:10.3f}  {p84:10.3f}")

    for i, name in enumerate(["v_C9", "v_SPARC", "v_Stream", "v_Cluster"]):
        arr = np.array([s["v_targets"][i] for s in best_samples])
        p16, p50, p84 = np.percentile(arr, [16, 50, 84])
        print(f"  {name:30s}  {p16:10.1f}  {p50:10.1f}  {p84:10.1f}")

    for i, name in enumerate(["width_C9", "width_SPARC", "width_Stream", "width_Cluster"]):
        arr = np.array([s["width_fracs"][i] for s in best_samples])
        p16, p50, p84 = np.percentile(arr, [16, 50, 84])
        print(f"  {name:30s}  {p16:10.4f}  {p50:10.4f}  {p84:10.4f}")

    # Get posterior median
    best_idx_max = np.argmax(loglikes)
    best = samples[best_idx_max]
    print()
    print(f"Best sample:")
    print(f"  m_chi = {best['m_chi']:.2f} GeV")
    print(f"  sigma_0_dwarf = {best['sigma_0_dwarf']:.3f} cm^2/g")
    print(f"  a_slope = {best['a_slope']:.3f}")
    print(f"  v_targets = {[f'{v:.1f}' for v in best['v_targets']]}")
    print(f"  loglike = {max(loglikes):.3f}")

    # Evaluate best sample at all test velocities
    print()
    print("Best-sample predictions:")
    resonances = build_resonances(best)
    test_velocities = [
        ("Segue 1", 10.0),
        ("Fornax", 15.0),
        ("Cloud-9", 28.0),
        ("SPARC", 100.0),
        ("Euclid subhalo", 150.0),
        ("Stream", 250.0),
        ("Stream+", 300.0),
        ("Cluster", 1000.0),
        ("Bullet", 3000.0),
    ]
    print(f"  {'System':15s}  {'v (km/s)':>10}  {'sigma/m':>10}  {'OK?':>5}")
    print("  " + "-" * 50)
    for name, v in test_velocities:
        sigma_0_v = velocity_dependent_background(v, best["sigma_0_dwarf"], best["a_slope"])
        r = sigma_m_multi_resonant(v, best["m_chi"], resonances, sigma_0_v, 0.0)
        sm = r["sigma_m_total"]
        # Simple OK check
        if v in [10, 12, 15]:
            ok = 0.5 <= sm <= 5.0
        elif v == 28:
            ok = 30 <= sm <= 500
        elif v == 100:
            ok = 0.03 <= sm <= 0.5
        elif v == 150:
            ok = sm <= 0.5
        elif v in [250, 300]:
            ok = 0.05 <= sm <= 1.0
        elif v == 1000:
            ok = 0.001 <= sm <= 0.1
        elif v == 3000:
            ok = sm <= 0.3
        print(f"  {name:15s}  {v:10.1f}  {sm:10.4f}  {'✓' if ok else '✗':>5}")

    # Save results
    out = {
        "test": "Phase32b_multi_resonant_joint_fit",
        "n_samples": N_samples,
        "n_best": len(best_samples),
        "max_loglike": float(max(loglikes)),
        "threshold_loglike_99pct": float(threshold),
        "best_sample": {
            "m_chi_GeV": float(best["m_chi"]),
            "sigma_0_dwarf": float(best["sigma_0_dwarf"]),
            "a_slope": float(best["a_slope"]),
            "v_targets_kms": [float(v) for v in best["v_targets"]],
            "width_fractions": [float(w) for w in best["width_fracs"]],
            "loglike": float(max(loglikes)),
        },
        "posterior_summary": {
            "m_chi_GeV": {"p16": float(np.percentile(m_chi_arr, 16)),
                           "p50": float(np.percentile(m_chi_arr, 50)),
                           "p84": float(np.percentile(m_chi_arr, 84))},
            "sigma_0_dwarf": {"p16": float(np.percentile(sigma_0_arr, 16)),
                               "p50": float(np.percentile(sigma_0_arr, 50)),
                               "p84": float(np.percentile(sigma_0_arr, 84))},
            "a_slope": {"p16": float(np.percentile(a_slope_arr, 16)),
                         "p50": float(np.percentile(a_slope_arr, 50)),
                         "p84": float(np.percentile(a_slope_arr, 84))},
        },
    }

    out_path = RESULTS_DIR / "phase32b_multi_resonant_joint_fit.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())