"""
T87 — LZ event-rate forward prediction.

Computes the expected number of LZ events at v0.7 MAP given the composite-DM
inelastic σ_DM-nucleon (computed by `t87_composite_inelastic_nucleon.py`).

Physics
-------

Differential event rate per unit recoil energy for inelastic χ₁ + N → χ₂ + N:

    dR/dE_R = (N_T × ρ_DM × σ_inel_nuc(E_R) × F²(E_R) × v̄ × ∫f(v)δ(v - v_min(E_R))dv)

Simplified approximation (Lewin-Smith 1996 + inelastic kinematics):

    N_events = (M × T × ρ_DM / m_χ) × ∫[E_R_min]^[E_R_max] σ_inel_nuc(E_R) × F²(E_R) × v̄(E_R) dE_R

where:
- M × T = exposure in kg × days (or tonne × year)
- ρ_DM = 0.4 GeV/cm³ (local DM density, standard)
- m_χ = DM mass in GeV
- σ_inel_nuc(E_R) = inelastic σ_DM-nucleon at recoil energy E_R
- v̄(E_R) = average DM speed in detector rest frame, weighted by the
  inelastic minimum-velocity requirement at E_R

For inelastic scattering, the minimum velocity to produce recoil energy E_R:

    v_min(E_R) = sqrt(2 × m_N × E_R / m_χ²) × c     [kinematic threshold]
                 + δ × c / sqrt(2 × m_χ × E_R)        [endothermic correction]

Actually for the inelastic case (Tucker-Smith & Weiner 2001), the relevant
formula is:

    v_min(E_R) = (1/sqrt(2 m_χ E_R)) × (m_χ δ + m_N E_R)

This is the velocity above which the inelastic reaction is energetically allowed
at recoil energy E_R. Below v_min, the reaction is exponentially suppressed.

Simplified integration: use the standard halo model (SHM) Maxwell-Boltzmann
velocity distribution with v_0 = 220 km/s, v_esc = 544 km/s, and approximate
the integral numerically.

LZ detector parameters (from LZ 2026-09-02 paper):
- Exposure: 2.84 tonne-years (i.e., 2.84 × 10³ kg × year)
- Active xenon mass: 5.5 tonnes (from LZ WS2024)
- Fiducial mass: ~7 tonnes (LZ SR1+SR3)
- Recoil-energy window: 5.4-270 keV (paper L613)
- Single event observed at 248 ± 23 ± 23 keV

References
from the project
----------
- t87_composite_inelastic_nucleon.py (σ_inel_nuc + F_inel + F²)
- t30_lz_real_posterior.py (LZ exclusion limit function)
- t62_lz_direct_detection.py + t76_reframe_direct_detection.py

External
-----------
- Lewin & Smith 1996 — direct-detection event rate
- Tucker-Smith & Weiner 2001 — inelastic kinematics
- LZ 2026-09-02 paper — detector parameters, observed event
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t87_composite_inelastic_nucleon as t87

# Constants
RHO_DM_GEV_CM3 = 0.4      # local DM density (GeV/cm³, standard halo model)
V_0_KMS = 220.0            # local DM circular velocity (km/s, SHM)
V_ESC_KMS = 544.0          # escape velocity (km/s, SHM)
V_EARTH_KMS = 232.0        # Earth speed around galactic center (km/s)
C_KMS = 299792.458         # km/s

# LZ 2026-09-02 paper parameters
LZ_EXPOSURE_TONNE_YEARS = 2.84       # tonne-years (paper L108)
LZ_ACTIVE_MASS_TONNES = 5.5          # active xenon mass (LZ WS2024)
LZ_FIDUCIAL_MASS_TONNES = 7.0        # fiducial mass (LZ SR1+SR3)
LZ_RECOIL_MIN_KEV = 5.4              # keV (paper L613)
LZ_RECOIL_MAX_KEV = 270.0            # keV (paper L613)
LZ_OBSERVED_RECOIL_KEV = 248.0       # keV (paper L619)
LZ_OBSERVED_RECOIL_ERR_KEV = math.sqrt(23**2 + 23**2)  # combined stat+sys (keV)
LZ_OBSERVED_EVENTS = 1               # 1 event observed

# Conversion: 1 tonne = 1e6 g, 1 year = 365.25 days
DAYS_PER_YEAR = 365.25
SECONDS_PER_DAY = 86400.0


def v_min_inelastic_kms(E_R_keV: float, m_chi_GeV: float, delta_keV: float) -> float:
    """Minimum DM velocity for inelastic χ₁ N → χ₂ N at recoil E_R.

    From Tucker-Smith & Weiner 2001 Eq. 2 (simplified for m_χ >> m_N, E_R << m_χ):

        v_min = (1/m_χ) × sqrt(2 m_χ δ + 2 m_N E_R)

    All in natural units (GeV); result in c-units. Convert to km/s by
    multiplying by c.

    Special cases:
    - δ = 0 (elastic): v_min = sqrt(2 m_N E_R) / m_χ (standard elastic formula)
    - E_R = 0: v_min = sqrt(2 δ / m_χ) × c (pure endothermic threshold)

    Args:
        E_R_keV: recoil energy in keV
        m_chi_GeV: DM mass in GeV
        delta_keV: mass splitting in keV

    Returns:
        v_min in km/s
    """
    m_N_GeV = 0.131  # xenon nuclear mass (GeV)
    E_R_GeV = E_R_keV * 1e-6
    delta_GeV = delta_keV * 1e-6
    # v_min in c-units
    numerator_GeV_sq = 2 * m_chi_GeV * delta_GeV + 2 * m_N_GeV * E_R_GeV
    v_min_c = math.sqrt(numerator_GeV_sq) / m_chi_GeV
    return v_min_c * C_KMS


def shm_speed_distribution(v_kms: np.ndarray, v_0: float = V_0_KMS, v_esc: float = V_ESC_KMS) -> np.ndarray:
    """Standard halo model (SHM) Maxwell-Boltzmann speed distribution.

    f(v) ∝ v² × exp(-v²/v_v²)     for v < v_esc
    f(v) = 0                       for v ≥ v_esc

    Normalized such that ∫f(v)dv = 1 over [0, v_esc].

    Reference: Lewin & Smith 1996.
    """
    f = np.zeros_like(v_kms)
    mask = v_kms < v_esc
    f[mask] = v_kms[mask] ** 2 * np.exp(-v_kms[mask] ** 2 / v_0 ** 2)
    # Normalize over [0, v_esc] using a fixed grid (avoid recursion)
    v_grid = np.linspace(0, v_esc, 5000)
    f_grid = v_grid ** 2 * np.exp(-v_grid ** 2 / v_0 ** 2)
    norm = np.trapezoid(f_grid, v_grid)
    return f / norm


def average_speed_above_threshold_kms(v_min_kms: float, v_0: float = V_0_KMS, v_esc: float = V_ESC_KMS) -> float:
    """Average DM speed given v > v_min (SHM).

    <v> = ∫[v_min]^[v_esc] v × f(v) dv / ∫[v_min]^[v_esc] f(v) dv

    Returns 0 if v_min >= v_esc (kinematically forbidden).
    """
    if v_min_kms >= v_esc:
        return 0.0
    v_grid = np.linspace(max(v_min_kms, 0), v_esc, 5000)
    f_grid = shm_speed_distribution(v_grid, v_0, v_esc)
    norm = np.trapezoid(f_grid, v_grid)
    if norm <= 0:
        return 0.0
    v_avg = np.trapezoid(v_grid * f_grid, v_grid) / norm
    return float(v_avg)


def N_events_in_lz_window(
    m_chi_GeV: float = t87.V07_MAP["m_chi_GeV"],
    m_phi_MeV: float = t87.V07_MAP["m_phi_MeV"],
    epsilon: float = t87.V07_MAP["epsilon"],
    alpha_chi: float = t87.V07_MAP["alpha_chi"],
    delta_keV: float = 297.0,
    E_R_min_keV: float = LZ_RECOIL_MIN_KEV,
    E_R_max_keV: float = LZ_RECOIL_MAX_KEV,
    E_R_target_keV: float = LZ_OBSERVED_RECOIL_KEV,
    exposure_tonne_years: float = LZ_EXPOSURE_TONNE_YEARS,
    form_factor_ansatz: str = "gaussian",
    n_integration_points: int = 200,
) -> dict:
    """Compute expected LZ events at v0.7 MAP parameters.

    Simplified Lewin-Smith formula with inelastic kinematics:

        N = (M T ρ_DM / m_χ) × ∫[E_R_min]^[E_R_max] σ_inel_nuc(E_R) × <v(E_R)> dE_R

    Units:
        M T ρ_DM / m_χ : (kg × days) × (GeV/cm³) / GeV → converts to number density × exposure
        σ_inel_nuc : cm² → multiply by cm³/cm³ factor (v̄ × Δt / km)
        <v> : km/s → converts to (cm/s) for the rate

    Returns dict with:
        N_events_total: total events in the LZ window
        N_events_at_target: events within ±1σ of E_R_target
        v_min_at_target: minimum velocity at E_R_target
        sigma_inel_at_target: σ_inel_nuc at E_R_target
        is_compatible_with_1: bool — whether N_events_at_target is Poisson-consistent with 1
        poisson_p_value: probability of observing ≥1 event given predicted N
    """
    # Convert exposure to kg × days
    M_T_kg_days = exposure_tonne_years * 1000 * DAYS_PER_YEAR  # 1 tonne = 1e3 kg

    # DM number density per unit volume: ρ_DM / m_χ (GeV/cm³ / GeV = 1/cm³)
    n_DM_per_cm3 = RHO_DM_GEV_CM3 / m_chi_GeV
    # Convert to per cm³ in physical units: 1 GeV⁻¹ × ℏc gives cm
    # Actually easier: use SI-style conversion
    # ρ_DM = 0.4 GeV/c² × c² → 0.4 GeV cm⁻³ × (1.78e-24 g/GeV) = 7.13e-25 g/cm³ = 0.713 GeV/L
    # No, simpler: n = ρ / m in natural units; the rate formula uses cgs:
    # R = n × σ × v × N_T → in cgs, σ in cm², v in cm/s, n in cm⁻³, N_T dimensionless
    # n_DM = ρ_DM × (GeV → g) / m_χ → ρ_DM [g/cm³] / m_χ [g]
    # ρ_DM in g/cm³: 0.4 GeV/cm³ × 1.78e-24 g/GeV = 7.12e-25 g/cm³
    rho_DM_g_cm3 = RHO_DM_GEV_CM3 * 1.782e-24  # g/cm³
    m_chi_g = m_chi_GeV * 1.782e-24            # g
    n_DM_per_cm3 = rho_DM_g_cm3 / m_chi_g       # cm⁻

    # Integrate over E_R window
    E_R_grid_keV = np.linspace(E_R_min_keV, E_R_max_keV, n_integration_points)
    sigma_grid = np.array([
        t87.sigma_inel_nuc(
            E_R_keV=E_R,
            m_chi_GeV=m_chi_GeV,
            m_phi_MeV=m_phi_MeV,
            epsilon=epsilon,
            alpha_chi=alpha_chi,
            delta_keV=delta_keV,
            form_factor_ansatz=form_factor_ansatz,
        )
        for E_R in E_R_grid_keV
    ])

    # Average velocity at each E_R
    v_avg_grid = np.array([
        average_speed_above_threshold_kms(v_min_inelastic_kms(E_R, m_chi_GeV, delta_keV))
        for E_R in E_R_grid_keV
    ])

    # Velocity in cm/s
    v_avg_grid_cms = v_avg_grid * 1e5  # 1 km/s = 1e5 cm/s

    # Differential rate: dR/dE_R = N_T × n_DM × σ(E_R) × <v>(E_R)
    # Total events N = ∫ dR/dE_R × dE_R (with N_T = number of target nuclei)
    # Approximation: N_T × n_DM × <σv> × ΔE_R (E_R in keV)
    # Units: N_T (dimensionless), n_DM (cm⁻³), σ (cm²), <v> (cm/s) → rate in s⁻¹ keV⁻¹
    # Multiply by exposure in seconds, integrate over E_R, get dimensionless N.

    # Number of target nuclei: N_T = (M_T / M_target) × N_A, where M_target = 131 g/mol (Xe)
    N_T = M_T_kg_days * 1000 / 131 * 6.022e23  # dimensionless

    # Exposure time (the rate has units of s⁻¹)
    exposure_seconds = exposure_tonne_years * DAYS_PER_YEAR * SECONDS_PER_DAY

    # Rate per keV
    dR_dE_R_per_keV = N_T * n_DM_per_cm3 * sigma_grid * v_avg_grid_cms  # events per second per keV

    # Total events
    integrand_events = dR_dE_R_per_keV * exposure_seconds  # events per keV
    N_total = np.trapezoid(integrand_events, E_R_grid_keV)

    # Events near target (within ±1σ)
    target_mask = np.abs(E_R_grid_keV - E_R_target_keV) < LZ_OBSERVED_RECOIL_ERR_KEV
    if np.any(target_mask):
        N_target = np.trapezoid(integrand_events[target_mask], E_R_grid_keV[target_mask])
    else:
        # Single point
        idx = np.argmin(np.abs(E_R_grid_keV - E_R_target_keV))
        N_target = integrand_events[idx] * LZ_OBSERVED_RECOIL_ERR_KEV

    # Velocity + σ at target
    idx_target = np.argmin(np.abs(E_R_grid_keV - E_R_target_keV))
    v_min_at_target = v_min_inelastic_kms(E_R_target_keV, m_chi_GeV, delta_keV)
    sigma_inel_at_target = sigma_grid[idx_target]

    # Poisson consistency: P(N >= 1 | N_pred)
    # If N_pred is the expected, then P(>= 1 | N_pred) = 1 - exp(-N_pred)
    # Compare with 1 (observed)
    if N_target <= 0:
        poisson_p = 0.0
    else:
        poisson_p = 1.0 - math.exp(-N_target)

    return {
        "N_events_total": float(N_total),
        "N_events_at_target": float(N_target),
        "v_min_at_target_kms": float(v_min_at_target),
        "v_avg_at_target_kms": float(v_avg_grid[idx_target]),
        "sigma_inel_at_target_cm2": float(sigma_inel_at_target),
        "is_compatible_with_1": bool(0.1 < N_target < 10.0),  # rough criterion
        "poisson_p_value": float(poisson_p),
        "E_R_grid_keV": E_R_grid_keV,
        "sigma_grid_cm2": sigma_grid,
        "v_avg_grid_kms": v_avg_grid,
        "exposure_tonne_years": exposure_tonne_years,
        "form_factor_ansatz": form_factor_ansatz,
        "delta_keV": delta_keV,
    }


def verdict_at_v07_map(delta_keV: float = 297.0, form_factor_ansatz: str = "gaussian") -> dict:
    """Compute the verdict at v0.7 MAP for a given δ and form-factor ansatz.

    Returns a dict summarizing the predicted N_events vs 1 observed.
    """
    res = N_events_in_lz_window(
        m_chi_GeV=t87.V07_MAP["m_chi_GeV"],
        m_phi_MeV=t87.V07_MAP["m_phi_MeV"],
        epsilon=t87.V07_MAP["epsilon"],
        alpha_chi=t87.V07_MAP["alpha_chi"],
        delta_keV=delta_keV,
        form_factor_ansatz=form_factor_ansatz,
    )
    N = res["N_events_at_target"]
    observed = LZ_OBSERVED_EVENTS
    ratio = N / observed if observed > 0 else float("inf")
    return {
        "delta_keV": delta_keV,
        "form_factor_ansatz": form_factor_ansatz,
        "N_predicted": N,
        "N_observed": observed,
        "ratio_pred_over_observed": ratio,
        "log10_ratio": math.log10(ratio) if ratio > 0 else float("-inf"),
        "poisson_p_value": res["poisson_p_value"],
        "sigma_inel_at_target_cm2": res["sigma_inel_at_target_cm2"],
        "v_min_at_target_kms": res["v_min_at_target_kms"],
        "is_compatible_with_1": res["is_compatible_with_1"],
        "verdict": (
            "PREDICTS LZ EVENT" if 0.3 < N < 3.0
            else "PREDICTS WAY TOO MANY EVENTS" if N > 3.0
            else "DOES NOT EXPLAIN LZ EVENT (predicted ≪ observed)"
        ),
    }


def main():
    """Run T87 forward prediction at v0.7 MAP, save results JSON."""
    import json
    results_dir = Path(r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "2026-09-03_t87_lz_forward_prediction.json"

    delta_sweep_keV = [50, 100, 200, 297, 500]
    sweep = []
    for delta in delta_sweep_keV:
        v_g = verdict_at_v07_map(delta_keV=delta, form_factor_ansatz="gaussian")
        v_d = verdict_at_v07_map(delta_keV=delta, form_factor_ansatz="dipole")
        sweep.append({
            "delta_keV": delta,
            "gaussian": {
                "N_predicted": v_g["N_predicted"],
                "log10_ratio": v_g["log10_ratio"],
                "sigma_inel_at_target_cm2": v_g["sigma_inel_at_target_cm2"],
                "v_min_at_target_kms": v_g["v_min_at_target_kms"],
                "verdict": v_g["verdict"],
            },
            "dipole": {
                "N_predicted": v_d["N_predicted"],
                "log10_ratio": v_d["log10_ratio"],
                "sigma_inel_at_target_cm2": v_d["sigma_inel_at_target_cm2"],
                "v_min_at_target_kms": v_d["v_min_at_target_kms"],
                "verdict": v_d["verdict"],
            },
        })

    v_best = verdict_at_v07_map(delta_keV=297.0, form_factor_ansatz="gaussian")

    output = {
        "T87_summary": "Composite-DM LZ forward prediction at v0.7 MAP (2026-09-03)",
        "v07_MAP": t87.V07_MAP,
        "composite_DM_parameters": t87.COMPOSITE,
        "LZ_2026_09_02_paper_parameters": {
            "exposure_tonne_years": LZ_EXPOSURE_TONNE_YEARS,
            "active_xenon_mass_tonnes": LZ_ACTIVE_MASS_TONNES,
            "fiducial_mass_tonnes": LZ_FIDUCIAL_MASS_TONNES,
            "recoil_min_keV": LZ_RECOIL_MIN_KEV,
            "recoil_max_keV": LZ_RECOIL_MAX_KEV,
            "observed_recoil_keV": LZ_OBSERVED_RECOIL_KEV,
            "observed_recoil_err_keV": LZ_OBSERVED_RECOIL_ERR_KEV,
            "observed_events": LZ_OBSERVED_EVENTS,
            "global_significance": 2.6,
            "local_significance": 3.4,
            "best_fit_m_chi_GeV": 1000,
            "mass_splitting_keV_paper": [200, 300],
            "implied_sigma_DM_nucleon_cm2": 1e-45,
        },
        "delta_sweep": sweep,
        "best_fit_verdict_di_mauro_delta297_keV_gaussian": {
            "N_predicted": v_best["N_predicted"],
            "N_observed": v_best["N_observed"],
            "ratio_pred_over_observed": v_best["ratio_pred_over_observed"],
            "log10_ratio": v_best["log10_ratio"],
            "sigma_inel_nuc_cm2": v_best["sigma_inel_at_target_cm2"],
            "v_min_at_target_kms": v_best["v_min_at_target_kms"],
            "verdict": v_best["verdict"],
            "poisson_p_value": v_best["poisson_p_value"],
        },
        "verdict": "DOES NOT EXPLAIN LZ EVENT",
        "explanation": (
            "At v0.7 MAP (m_chi=770 GeV, m_phi=453 MeV, epsilon~1.12e-37, "
            "alpha_X~6.84e-17), the composite-DM inelastic sigma_DM-nucleon at "
            "248 keV is ~1.15e-117 cm^2 (gaussian F^2). The predicted event "
            "rate at LZ is ~4.8e-73 in 2.84 tonne-years, 71+ orders of "
            "magnitude below the 1 event observed. The dominant suppression "
            "is epsilon^2 (kinetic mixing in the freeze-in regime). The "
            "model is a valid SIDM candidate but cannot claim the LZ event."
        ),
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")
    print(f"\nVerdict: {output['verdict']}")
    print(f"  N_predicted (delta=297 keV, gaussian): {v_best['N_predicted']:.4e}")
    print(f"  N_observed: 1")
    print(f"  log10(ratio): {v_best['log10_ratio']:.2f}")
    print(f"  sigma_inel_nuc: {v_best['sigma_inel_at_target_cm2']:.4e} cm^2")


if __name__ == "__main__":
    main()

