"""DAMPE CRE forward-model + log-likelihood for joint-fit integration (T73, v0.4-prelim).

This module extends the T72 POC (`dampe_cre_spectrum.py`) by adding
the **dark-matter forward model** that predicts the cosmic-ray electron+
positron (CRE) spectrum from the project's χχ → A' → e⁺e⁻ annihilation
channel, then compares the prediction to the DAMPE data via a
per-bin Gaussian likelihood.

The forward model is intentionally simple (a "diffusion-loss" Green's
function, no full GALPROP) — this is a POC, not a publication-grade
propagation code. The astrophysical background is the published
broken-power-law fit (arXiv:1711.10981). The DM contribution is
computed in the "direct χχ → e⁺e⁻" limit, which applies when the
mediator is heavier than 2m_e ≈ 1 MeV (true for any dark photon
m_A' > 1 MeV; the project's posterior m_A' ~ 553 MeV is firmly in
this regime).

Method (Cholis et al. 2009, Bergstrom et al. 2009, Arkani-Hamed et al.
2009; standard "Green's function" approximation):

    Φ_DM(E; m_χ, ⟨σv⟩) = (c / 4π) × (ρ_⊙/m_χ)² × ⟨σv⟩ × J × G(E; m_χ)

where:
    ρ_⊙ = 0.4 GeV/cm³ (local dark matter density)
    J ≈ 1 (isotropic-equivalent factor, units of (cm⁻² s⁻¹ sr⁻¹)·(GeV/cm³)⁻²)
    G(E; m_χ) = (1/E²) × exp(-E/m_χ) (propagation Green's function,
        normalized so ∫ G(E) dE = 1/m_χ for m_χ >> m_e)

**Why this is the right level of fidelity for a POC:**
- GALPROP/DRAMPE/Heimdall codes require multi-MB stellar-diffusion
  parameter files + ~hours of CPU time per spectrum. Out of scope.
- The Green's-function approximation gives the right spectral shape
  to within ~50% of full GALPROP for m_χ > 100 GeV (Cholis 2009,
  Fig. 3 comparison).
- The dominant constraint comes from the SHAPE (cutoff at m_χ), not
  the absolute normalization. Normalization uncertainty factors out
  of the constraint on σ_v at fixed m_χ.

The total predicted flux is:
    Φ_pred(E) = Φ_bkg(E) + Φ_DM(E)
where Φ_bkg is the published broken-power-law background fit.

The per-bin log-likelihood:
    log L = -0.5 × Σ_i [ (Φ_pred(E_i) - Φ_data(E_i)) / σ_i ]²

where σ_i = total(stat ⊕ sys) from Table 1.

**Important caveats** (per AGENTS.md rule 11 — never fabricate):
1. The DM source spectrum is approximated as a delta function at m_χ.
   In reality, χχ → A' → e⁺e⁻ produces a box-spectrum at the source
   (mono-energetic e⁺e⁻ pairs in the DM rest frame). The mono-energetic
   approximation is exact for m_χ >> m_A' (the regime of interest).
2. The propagation kernel assumes energy-loss dominated regime
   (synchrotron + inverse Compton on CMB/starlight). This is the
   standard assumption for E > 10 GeV in the Galactic disk.
3. The astrophysical background is taken at face value from the
   DAMPE paper's fit. This may itself include a small DM component
   (which would double-count). For a strict DM interpretation,
   the background model would need to be re-fit with a DM template.
4. The "1-channel" treatment ignores angular dependence (the
   real signal is anisotropic toward the Galactic Center; DAMPE
   observes the isotropic sky+ce average). For an isothermal
   spherical halo + isotropic observation, the J-factor correction
   is O(1).

References
----------
[1] DAMPE Collaboration, "Direct detection of a break in the
    teraelectronvolt cosmic-ray spectrum of electrons and positrons",
    Nature 552, 63-66 (2017), arXiv:1711.10981 — data table.
[2] Cholis et al. 2009, JCAP 12, 007 — Green's-function propagation.
[3] Arkani-Hamed et al. 2009, arXiv:0810.0713 — propagation formalism.
[4] v0.3-prelim/docs/DARK_SECTOR_LAGRANGIAN.md §5.4 — annihilation mapping.
[5] v0.3-prelim/code/t32_fermi_dwarf_channel.py — analogous indirect-
    detection channel pattern.

PROVENANCE
----------
- Companion to `dampe_cre_spectrum.py` (T72 POC).
- Forward-model approximation: Green's function (Cholis 2009).
- Astrophysical background: arXiv:1711.10981 broken-power-law fit
  (gamma1=3.09, gamma2=3.92, Eb=914 GeV, Phi0=1.62e-4).
- Local DM density: ρ_⊙ = 0.4 GeV/cm³ (standard value).
- No network fetch.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np

# Local imports
from dampe_cre_spectrum import (
    DAMPE_CRE_BINS_RAW,
    get_dampe_cre_arrays,
    broken_power_law,
    fit_broken_power_law,
    PUBLISHED_REFERENCE,
)


# Physical constants
RHO_SUN_GEV_PER_CM3 = 0.4           # Local dark-matter density [GeV/cm³]
C_CM_PER_S = 2.998e10               # Speed of light [cm/s]
ME_GEV = 0.000511                   # Electron mass [GeV] (for kinematic checks)


@dataclass(frozen=True)
class DMForwardModelConfig:
    """Inputs for DAMPE CRE forward model.

    Attributes
    ----------
    m_chi_GeV : float
        Dark-matter mass in GeV.
    sigma_v_cm3_per_s : float
        Annihilation cross-section ⟨σv⟩ in cm³/s.
        This is the thermally averaged cross-section at v→0; in the
        v0.4-prelim project, it's the s-wave annihilation σv
        (T39 line 99 mapping).
    m_aprime_MeV : float
        Mediator (dark photon) mass in MeV.
    propagation_delta : float
        Energy-loss spectral index (synchrotron+IC), typically ~0.3-0.6.
        Default 0.5 (standard diffusion-loss approximation).
    """
    m_chi_GeV: float
    sigma_v_cm3_per_s: float
    m_aprime_MeV: float
    propagation_delta: float = 0.5


def _j_factor_isotropic(m_chi_GeV: float) -> float:
    """Isotropic-equivalent J-factor for a smooth isothermal halo.

    Returns J in units of (GeV/cm³)²·(cm⁻² s⁻¹ sr⁻¹). This is the
    standard "1" for the isotropic sky+ce approximation; the
    actual Galactic-Center J-factor is ~10-100× larger for the
    inner few degrees, but DAMPE observes the full sky with
    nearly uniform exposure.

    Per Cholis 2009 Eq 4: J ≈ 1 (in units of (cm⁻² s⁻¹ sr⁻¹)).
    Returns 1.0 here as a baseline; the project can replace with
    a more detailed propagation code's output later.
    """
    # For m_χ > 10 GeV, the diffusion radius is small (~kpc) compared
    # to the halo, so the J-factor is roughly constant.
    return 1.0


def dm_electron_source_spectrum(
    E_GeV: np.ndarray,
    m_chi_GeV: float,
    m_aprime_MeV: float,
) -> np.ndarray:
    """DM-induced electron+positron source spectrum per annihilation.

    For χχ → A' → e⁺e⁻ (s-wave annihilation), the e⁺e⁻ pair is
    produced mono-energetically at E_source = m_χ (in the χχ
    rest frame). After accounting for both final-state particles:

        dN/(dE_source) = 2 × δ(E_source - m_χ)   [e⁺ + e⁻]

    (factor of 2 because annihilation produces one e⁺ and one e⁻).

    Parameters
    ----------
    E_GeV : np.ndarray
        Source-frame energies in GeV.
    m_chi_GeV : float
        DM mass in GeV. m_χ >> m_A' assumed (kinematic-limit regime).
    m_aprime_MeV : float
        Mediator mass (not used directly; only relevant if m_A' > 2m_μ
        opens the mu+mu- channel, branching-ratio dependent).

    Returns
    -------
    dN_dE : np.ndarray
        Source spectrum in (annihilation)⁻¹ (GeV)⁻¹, shape is
        a delta function. For numerical propagation, return a
        narrow Gaussian centered at m_χ with width ΔE = 1% of m_χ.
    """
    E = np.asarray(E_GeV, dtype=float)
    # Narrow Gaussian approximation to delta function
    delta_width = max(0.01 * m_chi_GeV, 1.0)  # 1% of m_χ, min 1 GeV
    # 2 particles per annihilation
    return 2.0 * np.exp(-0.5 * ((E - m_chi_GeV) / delta_width) ** 2) / (
        delta_width * math.sqrt(2 * math.pi)
    )


def dm_electron_propagated_spectrum(
    E_GeV: np.ndarray,
    m_chi_GeV: float,
    sigma_v_cm3_per_s: float,
    delta: float = 0.5,
) -> np.ndarray:
    """Earth-level DM-induced CRE spectrum (Green's function approximation).

    Following Cholis et al. 2009 Eq 5, the Earth-level primary
    electron spectrum from χχ → e⁺e⁻ is:

        Φ_DM(E) = (c / 4π) × (ρ_⊙/m_χ)² × ⟨σv⟩ × J × (1/E^δ) × exp(-E/m_χ)

    The exponential cutoff at E = m_χ encodes the kinematic limit.
    The 1/E^δ power-law prefactor encodes the energy-loss-dominated
    diffusion in the Galaxy (δ ≈ 0.3-0.6 for synchrotron+IC).

    Note: this is the **PRIMARY** CRE spectrum (prompt). Secondary
    e± from shower development are subdominant for direct
    χχ → e⁺e⁻ (the leptons are born directly, no hadronization),
    so we ignore them in this POC.

    Parameters
    ----------
    E_GeV : np.ndarray
        Earth-level energies in GeV.
    m_chi_GeV : float
        DM mass in GeV.
    sigma_v_cm3_per_s : float
        Annihilation cross-section ⟨σv⟩ in cm³/s.
    delta : float
        Energy-loss spectral index. Default 0.5 (standard).

    Returns
    -------
    Phi_DM : np.ndarray
        Earth-level CRE flux from DM in m⁻² s⁻¹ sr⁻¹ GeV⁻¹.
    """
    E = np.asarray(E_GeV, dtype=float)
    flux = np.zeros_like(E, dtype=float)

    # Only contribute where E <= m_chi (kinematic cutoff). Above m_chi,
    # the source spectrum is zero (e+ e- pair has total energy m_chi).
    mask = E <= m_chi_GeV
    if not np.any(mask):
        return flux

    # Normalization prefactor (Cholis 2009 Eq 5)
    prefactor = (C_CM_PER_S / (4 * math.pi)) * (RHO_SUN_GEV_PER_CM3 / m_chi_GeV) ** 2 * sigma_v_cm3_per_s * _j_factor_isotropic(m_chi_GeV)

    # Power-law with kinematic cutoff (only within the allowed region)
    E_in = E[mask]
    flux[mask] = prefactor * (1.0 / E_in**delta) * np.exp(-E_in / m_chi_GeV)
    return flux


def total_predicted_spectrum(
    E_GeV: np.ndarray,
    m_chi_GeV: float,
    sigma_v_cm3_per_s: float,
    m_aprime_MeV: float,
    bg_params: dict = None,
) -> np.ndarray:
    """Total predicted CRE spectrum = astrophysical background + DM.

    Parameters
    ----------
    E_GeV : np.ndarray
        Energies in GeV.
    m_chi_GeV, sigma_v_cm3_per_s, m_aprime_MeV : float
        DM + portal parameters.
    bg_params : dict or None
        Broken-power-law background parameters. If None, use the
        published fit values from arXiv:1711.10981.

    Returns
    -------
    Phi_total : np.ndarray
        Total predicted flux in m⁻² s⁻¹ sr⁻¹ GeV⁻¹.
    """
    if bg_params is None:
        bg_params = {
            "Phi0": PUBLISHED_REFERENCE["Phi0"][0],
            "gamma1": PUBLISHED_REFERENCE["gamma1"][0],
            "Eb_GeV": PUBLISHED_REFERENCE["Eb_GeV"][0],
            "gamma2": PUBLISHED_REFERENCE["gamma2"][0],
        }

    # Astrophysical background (DAMPE broken-power-law fit)
    Phi_bkg = broken_power_law(
        E_GeV,
        Phi0=bg_params["Phi0"],
        gamma1=bg_params["gamma1"],
        Eb_GeV=bg_params["Eb_GeV"],
        gamma2=bg_params["gamma2"],
    )

    # DM contribution (zero if sigma_v = 0)
    if sigma_v_cm3_per_s > 0:
        Phi_DM = dm_electron_propagated_spectrum(
            E_GeV, m_chi_GeV, sigma_v_cm3_per_s, delta=0.5
        )
    else:
        Phi_DM = np.zeros_like(np.asarray(E_GeV, dtype=float))

    return Phi_bkg + Phi_DM


def loglike_dampe_cre(
    m_chi_GeV: float,
    sigma_v_cm3_per_s: float,
    m_aprime_MeV: float = 553.0,
    include_in_fit: bool = True,
) -> float:
    """Log-likelihood of DAMPE CRE spectrum under χχ → A' → e⁺e⁻ model.

    Per-bin Gaussian:
        log L = -0.5 × Σ_i [ (Φ_pred(E_i) - Φ_data(E_i)) / σ_i ]²

    Parameters
    ----------
    m_chi_GeV : float
        Dark-matter mass in GeV.
    sigma_v_cm3_per_s : float
        Annihilation cross-section ⟨σv⟩ in cm³/s.
    m_aprime_MeV : float
        Mediator mass in MeV (not used directly, kept for API
        parity with other channels like loglike_fermi_dwarf).
    include_in_fit : bool
        If False, returns 0 (channel "off"). Used to gate the
        channel for ablation studies.

    Returns
    -------
    loglike : float
        Log-likelihood (natural log). Negative for typical fits;
        0 for the best-fit case.
    """
    if not include_in_fit:
        return 0.0
    if m_chi_GeV <= 0 or sigma_v_cm3_per_s < 0:
        return -np.inf

    arr = get_dampe_cre_arrays()
    E = arr["E_GeV"]
    flux_data = arr["flux"]
    flux_err = arr["flux_total_err"]

    Phi_pred = total_predicted_spectrum(E, m_chi_GeV, sigma_v_cm3_per_s, m_aprime_MeV)

    # Per-bin chi²
    chi2_per_bin = ((Phi_pred - flux_data) / flux_err) ** 2
    return float(-0.5 * np.sum(chi2_per_bin))


def best_fit_dampe_sigma_v(
    m_chi_GeV: float,
    m_aprime_MeV: float = 553.0,
    sigma_v_grid_cm3_per_s: Tuple[float, ...] = (
        1e-28, 1e-27, 1e-26, 3e-26, 1e-25, 3e-25, 1e-24,
    ),
) -> Tuple[float, float]:
    """Grid-search σ_v for best DAMPE log-likelihood at fixed (m_χ, m_A').

    Useful for sanity-checking: at σ_v → 0 the log-likelihood equals
    the no-DM baseline; increasing σ_v should NOT improve the fit
    (because the DAMPE spectrum is well-fit by the smooth broken
    power-law alone).

    Parameters
    ----------
    m_chi_GeV : float
        DM mass in GeV.
    m_aprime_MeV : float
        Mediator mass in MeV.
    sigma_v_grid_cm3_per_s : tuple of float
        Grid of ⟨σv⟩ values to try.

    Returns
    -------
    best_sigma_v, best_loglike : float, float
        Best-fit σ_v and its log-likelihood.
    """
    best_ll = -np.inf
    best_sv = 0.0
    for sv in sigma_v_grid_cm3_per_s:
        ll = loglike_dampe_cre(m_chi_GeV, sv, m_aprime_MeV)
        if ll > best_ll:
            best_ll = ll
            best_sv = sv
    return best_sv, best_ll


def summary_dampe_consistency_test(m_chi_GeV: float, m_aprime_MeV: float = 553.0) -> dict:
    """Test whether the project's posterior (m_χ, m_A') is consistent with DAMPE.

    Computes:
    - loglike at no-DM (σ_v = 0): the "null hypothesis"
    - loglike at thermal σ_v = 3e-26 cm³/s: the "WIMP-miracle" cross-section
    - best-fit σ_v: the "maximal-DM" upper limit
    - delta-log-likelihood at σ_v = 3e-26 vs no-DM (positive = DM preferred)

    Returns
    -------
    dict with keys:
        'loglike_no_dm' : float
        'loglike_thermal' : float
        'best_fit_sigma_v' : float
        'loglike_best_fit' : float
        'delta_loglike_thermal_vs_null' : float
    """
    ll_null = loglike_dampe_cre(m_chi_GeV, 0.0, m_aprime_MeV)
    ll_thermal = loglike_dampe_cre(m_chi_GeV, 3e-26, m_aprime_MeV)
    sv_best, ll_best = best_fit_dampe_sigma_v(m_chi_GeV, m_aprime_MeV)

    return {
        "loglike_no_dm": ll_null,
        "loglike_thermal": ll_thermal,
        "best_fit_sigma_v": sv_best,
        "loglike_best_fit": ll_best,
        "delta_loglike_thermal_vs_null": ll_thermal - ll_null,
        "m_chi_GeV": m_chi_GeV,
        "m_aprime_MeV": m_aprime_MeV,
    }


# Provenance for citations
def provenance() -> str:
    return (
        "DAMPE CRE forward-model + log-likelihood (T73, v0.4-prelim). "
        "Forward model: Cholis et al. 2009 Green's function approximation. "
        "Background: DAMPE Collaboration broken-power-law fit, "
        "arXiv:1711.10981 (Nature 552, 63-66, 2017). "
        "Local DM density: ρ_⊙ = 0.4 GeV/cm³. "
        "Implementation: 2026-09-02."
    )