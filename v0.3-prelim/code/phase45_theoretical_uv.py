"""
Phase 45 — Theoretical UV mechanism survey (Item 3).

Surveys whether ANY known dark matter microphysics can produce the T90.70
multi-resonant sigma/m(v) architecture with peaks at v=[28, 100, 300, 700] km/s.

Reviews literature candidates:
  1. Single s-channel Breit-Wigner resonance (JHEP 09 (2017) 159)
  2. Multiple mediators with different masses
  3. Hidden valley / composite dark matter
  4. Sommerfeld-enhanced Yukawa
  5. Atomic dark matter (dark photon + dark electron)
  6. Self-interacting dark photon

Verdict: identify which (if any) mechanisms can produce 4 resonances at
the required velocity positions, with realistic particle physics parameters.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

RESULTS_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results")


def breit_wigner_single(v_kms, v_resonance_kms, sigma_peak_cm2_g, width_frac):
    """Single s-channel Breit-Wigner resonance.

    sigma/m(v) = sigma_peak * (width_frac * v_resonance)^2 / ((v^2 - v_resonance^2)^2 + (width_frac * v_resonance^2)^2)

    For non-relativistic scattering: v^2 ~ kinetic energy / mass
    """
    v = np.asarray(v_kms, dtype=float)
    v_res = v_resonance_kms
    width = width_frac * v_res
    # Avoid singularity at v=0
    v = np.maximum(v, 0.01)
    numerator = (width**2) * sigma_peak_cm2_g
    denominator = (v**2 - v_res**2)**2 + width**4
    return numerator / denominator


def sommerfeld_yukawa(v_kms, m_chi_gev, m_med_mev, alpha_x):
    """Sommerfeld-enhanced Yukawa cross section.

    sigma/m(v) = sigma_0 * S(v) where S(v) = Sommerfeld enhancement factor.

    For Yukawa: S(v) ~ pi * alpha_x / (v/v_med) for v << v_med
    """
    v_med = m_med_mev / m_chi_gev * 1000  # km/s (approximate)
    v = np.asarray(v_kms, dtype=float)
    v = np.maximum(v, 0.01)
    sigma_0_base = 4 * np.pi * alpha_x**2 / (m_chi_gev * 1e-3)**2  # cm^2/g (rough)
    S = np.pi * alpha_x * v_med / np.maximum(v, 0.1)  # diverges at low v
    S = np.clip(S, 1.0, 100.0)  # saturate
    return sigma_0_base * S


def find_resonance_velocity(m_chi_gev, m_med_mev):
    """Velocity at which a Breit-Wigner resonance occurs.

    For s-channel: E_CM = sqrt(s) = 2 * m_chi + m_med → resonance at v=0
    For non-relativistic: v_resonance ~ sqrt(m_med * (m_med - 2*m_chi) / m_chi) when m_med ~ 2*m_chi

    But this is for annihilation. For scattering (t-channel), the resonance
    is at the mediator mass pole.
    """
    # For elastic scattering via s-channel, resonance occurs when
    # the kinetic energy matches the mediator mass:
    # 1/2 * m_chi * v^2 ~ m_med → v_resonance = sqrt(2 * m_med / m_chi) * c
    v_res_kms = np.sqrt(2 * m_med_mev * 1e-3 / m_chi_gev) * 3e5  # km/s
    return v_res_kms


def main():
    print("Phase 45 — Theoretical UV mechanism survey")
    print()

    # T90.70 architecture requirements
    v_targets_required = [28.0, 100.0, 300.0, 700.0]  # km/s
    print(f"T90.70 multi-resonant architecture requires sigma/m peaks at:")
    print(f"  v = {v_targets_required} km/s")
    print()

    # 1. SINGLE S-CHANNEL BREIT-WIGNER RESONANCE
    print("=" * 70)
    print("Candidate 1: Single s-channel Breit-Wigner resonance")
    print("=" * 70)
    print("Mechanism: dark matter scatters through a mediator in the s-channel.")
    print("For elastic scattering, resonance at v_resonance ~ sqrt(2*m_med/m_chi) * c")
    print()
    print("Limitations:")
    print("  - One resonance → ONE peak, not 4")
    print("  - To get 4 peaks need 4 different mediators, which is contrived")
    print("  - Required m_med/m_chi ratio for v_resonance ~ 28 km/s with m_chi ~ 7 GeV:")
    for v_res in v_targets_required:
        # 1/2 * m_chi * v^2 ~ m_med * c^2 (for non-relativistic)
        # m_med ~ m_chi * v^2 / (2 * c^2)
        v_cgs = v_res * 1e5  # cm/s
        c_cgs = 3e10  # cm/s
        m_chi_g = 7.0  # GeV
        m_chi_mev = m_chi_g * 1000  # MeV
        m_med_mev = 0.5 * m_chi_mev * (v_cgs / c_cgs)**2
        print(f"    v={v_res} km/s: m_med = {m_med_mev:.4f} MeV (= {m_med_mev/m_chi_mev:.2e} * m_chi)")
    print()
    print("Verdict: 4 separate resonances would require 4 separate mediators.")
    print("  This is technically possible but contrived.")
    print()

    # 2. MULTIPLE MEDIATORS WITH DIFFERENT MASSES
    print("=" * 70)
    print("Candidate 2: Multiple mediators (e.g., hidden sector with mass mixing)")
    print("=" * 70)
    print("Mechanism: 4 different U(1) gauge bosons with different masses")
    print("  - Each gives a separate Yukawa potential")
    print("  - Sum over 4 gives a 'stairs' structure in sigma/m(v)")
    print()
    print("Examples in literature:")
    print("  - Atomic dark matter (dark photon + dark Z', dark electron)")
    print("  - Mirror dark matter with kinetic mixing")
    print("  - String compactifications with multiple light U(1)'s")
    print()
    print("Verdict: Plausible mechanism, but each mediator introduces new params")
    print("  Total particle-physics parameters: ~20+")
    print()

    # 3. HIDDEN VALLEY / COMPOSITE DARK MATTER
    print("=" * 70)
    print("Candidate 3: Hidden valley / composite dark matter")
    print("=" * 70)
    print("Mechanism: dark matter is composite (e.g., dark hadrons)")
    print("  Multiple bound states → multiple scattering channels")
    print("  Each channel has its own resonance peak")
    print()
    print("Examples:")
    print("  - Strongly interacting massive particles (SIMPs)")
    print("  - Dark nucleons with multiple excited states")
    print("  - Confining gauge theories (SU(N)_dark)")
    print()
    print("Verdict: Plausible, well-motivated in BSM physics")
    print("  Number of parameters: similar to standard QCD-like theories")
    print()

    # 4. SOMMERFELD-ENHANCED YUKAWA
    print("=" * 70)
    print("Candidate 4: Sommerfeld-enhanced Yukawa")
    print("=" * 70)
    print("Mechanism: Light mediator gives long-range Yukawa potential")
    print("  Cross section enhanced at low velocity")
    print("  sigma/m(v) ~ 1/v at low v (no resonance peaks)")
    print()
    print("Verdict: Does NOT produce resonance peaks")
    print("  Gives monotonic decrease, not 4-peak structure")
    print("  Could combine with Breit-Wigner to give peaks on top of envelope")
    print()

    # 5. ATOMIC DARK MATTER
    print("=" * 70)
    print("Candidate 5: Atomic dark matter (dark photon + dark electron)")
    print("=" * 70)
    print("Mechanism: dark matter is neutral bound state of dark proton + dark electron")
    print("  Scattering mediated by massless dark photon (Bohr-radius scale)")
    print("  Velocity dependence comes from Bohr momentum")
    print()
    print("Verdict: Gives sigma/m(v) ~ 1/v^4 (geometric cross section)")
    print("  No resonance peaks. Doesn't fit T90.70 architecture.")
    print()

    # 6. SELF-INTERACTING DARK PHOTON
    print("=" * 70)
    print("Candidate 6: Self-interacting massive dark photon")
    print("=" * 70)
    print("Mechanism: dark matter IS the dark photon (massive vector)")
    print("  Self-interaction via non-abelian gauge structure (dark SU(2))")
    print()
    print("Verdict: Possible but requires non-abelian structure")
    print("  Hard to produce 4 distinct resonances")
    print()

    # 7. TSAI 2022 (FALSIFIED)
    print("=" * 70)
    print("Reference: Tsai 2022 (FALSIFIED in our Phase 33b)")
    print("=" * 70)
    print("Tsai's proposal: heavy quarkonium UV completion")
    print("  Predicts GeV-scale mediator → resonance velocities ~400,000 km/s")
    print("  But our T90.70 fits resonances at 28-700 km/s")
    print("  Inconsistent by factor of 1000+")
    print()

    # Compute test: can 4 Breit-Wigner resonances reproduce T90.70 architecture?
    print("=" * 70)
    print("Quantitative test: can 4 Breit-Wigner resonances reproduce T90.70?")
    print("=" * 70)
    print()

    # T90.70 sigma/m at v_targets
    sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
    from t90_v70_multi_resonant_darkqcd import sigma_m_multi_resonant, velocity_dependent_background
    from t90_v50_resonant_sidm import kinetic_energy_eV

    m_chi = 6.58
    sigma_0 = 0.195
    a_slope = 0.7
    v_targets = [28.0, 100.0, 300.0, 700.0]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    width_fracs = [0.05, 0.05, 0.05, 0.10]
    resonances = []
    for i, v_t in enumerate(v_targets):
        E_R = kinetic_energy_eV(v_t, m_chi)
        resonances.append({
            "name": f"R{i}",
            "E_R_eV": E_R,
            "Gamma_eV": width_fracs[i] * E_R,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": v_t,
        })

    print("T90.70 sigma/m at v=15, 28, 100, 300, 700, 1500 km/s:")
    for v in [15, 28, 100, 300, 700, 1500]:
        sigma_0_v = velocity_dependent_background(v, sigma_0, a_slope)
        r = sigma_m_multi_resonant(v, m_chi, resonances, sigma_0_v, 0.0)
        print(f"  v={v:5d} km/s: sigma/m = {r['sigma_m_total']:.3f} cm^2/g")
    print()

    # Check if a SINGLE Breit-Wigner with appropriate parameters could produce
    # the 4-peak structure at the required velocities.
    print("Single Breit-Wigner test: best single resonance to match T90.70")
    print()
    # Fit a single Breit-Wigner to the T90.70 peaks (in log space)
    from scipy.optimize import minimize

    v_fit = np.array([28.0, 100.0, 300.0, 700.0])
    sigma_fit = np.array([100.0, 0.07, 0.1, 0.01])

    def loss(params):
        v_res, sigma_peak, width_frac = params
        sigma_pred = breit_wigner_single(v_fit, v_res, sigma_peak, width_frac)
        return np.sum((np.log10(np.maximum(sigma_pred, 1e-10)) - np.log10(sigma_fit))**2)

    res = minimize(loss, x0=[100.0, 100.0, 0.1], method='Nelder-Mead')
    print(f"Best single-resonance fit: v_res={res.x[0]:.1f} km/s, sigma_peak={res.x[1]:.2f}, width={res.x[2]:.3f}")
    print(f"Loss (sum of squared log10 errors): {res.fun:.2f}")
    print()

    sigma_pred = breit_wigner_single(v_fit, res.x[0], res.x[1], res.x[2])
    print("Single-resonance vs T90.70:")
    for v, t90, single in zip(v_fit, sigma_fit, sigma_pred):
        print(f"  v={v:5.0f} km/s: T90={t90:8.3f}, single-BW={single:.3f}, ratio={single/max(t90, 0.001):.3f}")
    print()

    # Verdict
    if res.fun > 5.0:
        single_bw_verdict = "Single Breit-Wigner CANNOT reproduce T90.70 (loss > 5)"
    else:
        single_bw_verdict = "Single Breit-Wigner CAN approximately reproduce T90.70"

    print(f"Verdict: {single_bw_verdict}")
    print()

    # Save
    out = {
        "test": "Phase45_theoretical_UV_survey",
        "t90_70_requirements": {
            "v_targets_km_s": v_targets_required,
            "sigma_peaks_cm2_g": sigma_peaks,
            "n_resonances": 4,
        },
        "candidates": {
            "1_single_breit_wigner": {
                "description": "Single s-channel Breit-Wigner resonance",
                "verdict": "Cannot produce 4 peaks with single mediator",
                "feasibility": "Poor",
            },
            "2_multiple_mediators": {
                "description": "4 different U(1) gauge bosons",
                "verdict": "Plausible but contrived",
                "feasibility": "Marginal",
            },
            "3_hidden_valley_composite": {
                "description": "Composite dark matter (dark hadrons, SIMPs)",
                "verdict": "Plausible, well-motivated",
                "feasibility": "Good",
            },
            "4_sommerfeld_yukawa": {
                "description": "Sommerfeld-enhanced Yukawa",
                "verdict": "Does NOT produce resonance peaks",
                "feasibility": "Poor",
            },
            "5_atomic_dark_matter": {
                "description": "Atomic dark matter (dark photon + dark electron)",
                "verdict": "Gives 1/v^4, no peaks",
                "feasibility": "Poor",
            },
            "6_self_interacting_dark_photon": {
                "description": "Massive vector with non-abelian self-interaction",
                "verdict": "Hard to produce 4 peaks",
                "feasibility": "Marginal",
            },
        },
        "quantitative_test": {
            "single_BW_loss": float(res.fun),
            "verdict": single_bw_verdict,
        },
        "final_verdict": (
            "T90.70 multi-resonant architecture (4 peaks at v=[28,100,300,700]) "
            "is BEST matched by:\n"
            "  - Hidden valley / composite dark matter (Candidate 3) - well-motivated\n"
            "  - Multiple mediators (Candidate 2) - plausible but contrived\n\n"
            "A SINGLE s-channel Breit-Wigner resonance cannot reproduce 4 peaks.\n"
            "The Tsai 2022 UV completion is INCONSISTENT with the fitted resonance positions.\n\n"
            "Recommended particle-physics home for T90.70: Hidden valley with "
            "multiple bound states, similar to SM meson spectrum but at GeV scale."
        ),
    }

    out_path = RESULTS_DIR / "phase45_theoretical_uv.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results written to: {out_path}")


if __name__ == "__main__":
    main()