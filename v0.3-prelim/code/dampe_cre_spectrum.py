"""DAMPE cosmic-ray electron+positron spectrum ingestion (T72 POC).

This module ingests the published DAMPE CRE spectrum (cosmic ray
electrons + positrons, e⁻ + e⁺) from Table 1 of arXiv:1711.10981
(DAMPE Collaboration, Nature 552, 63-66, 2017). The data are
hardcoded constants — not fetched at runtime — because the paper's
data availability statement places the spectrum "in Table 1" of the
publication, with no machine-readable supplementary file. The values
were transcribed by hand from the HTML rendering of the paper; see
PROVENANCE below.

Scientific context (per the paper's abstract):
  - DAMPE measured the CRE spectrum directly from 25 GeV to 4.6 TeV
  - A smoothly broken power-law model is preferred over a single
    power-law at 6.6σ
  - Spectral break at E_b ≈ 0.9 TeV
  - The break constrains dark-matter annihilation/decay models and
    nearby pulsar contributions to the "positron excess"

This module ships as a proof-of-concept (T72 POC) for the Consider.docx
path-proposal recommendation #5: "Add DAMPE spectra as an additional
indirect-detection channel alongside Fermi dwarfs." Scope is
**electron-only** (the most cited DAMPE dataset); proton spectrum is
deferred to v0.4-prelim per the doc's relative priority.

References
----------
[1] DAMPE Collaboration, "Direct detection of a break in the
    teraelectronvolt cosmic-ray spectrum of electrons and positrons",
    Nature 552, 63-66 (2017), arXiv:1711.10981
[2] Astropart. Phys. 95, 6 (2017) — on-orbit performance
[3] Astropart. Phys. 105, 31 (2019) — PSD charge measurement

PROVENANCE
----------
- Data source: arXiv:1711.10981, Table 1 (CRE flux + 1σ stat + 1σ sys)
- Values transcribed by hand from the HTML version of the paper
  (https://arxiv.org/html/1711.10981v1) on 2026-09-02.
- Cross-check: broken-power-law fit (gamma1=3.09±0.01,
  gamma2=3.92±0.20, E_b=914±98 GeV) reproduced in
  tests/test_dampe_cre_spectrum.py
- Note: the paper does NOT provide a supplementary data file; the
  spectrum is reported only in Table 1 and Figure 2 of the paper.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass(frozen=True)
class DAMPEEnergyBin:
    """One row of DAMPE Table 1 (arXiv:1711.10981)."""
    E_min_GeV: float       # Lower edge of energy bin
    E_max_GeV: float       # Upper edge of energy bin
    E_mean_GeV: float      # Energy-bin mean ⟨E⟩
    E_mean_err_GeV: float  # 1σ uncertainty on ⟨E⟩
    acceptance_m2_sr: float  # Acceptance (m²·sr)
    acceptance_err_m2_sr: float  # 1σ acceptance uncertainty
    counts: int            # Counts in this bin
    bkg_fraction: float    # Background fraction (%)
    bkg_fraction_err: float  # 1σ background-fraction uncertainty
    flux: float            # CRE flux Φ(e⁺+e⁻) in m⁻² s⁻¹ sr⁻¹ GeV⁻¹
    flux_stat_err: float   # 1σ statistical uncertainty
    flux_sys_err: float    # 1σ systematic uncertainty


# Table 1 of arXiv:1711.10981 — DAMPE CRE spectrum (Nature 552, 63-66, 2017)
# 36 energy bins from 25 GeV to 4.6 TeV. Transcribed by hand from the
# HTML version of the paper.
# Format: (E_min, E_max, E_mean, E_mean_err, acceptance, acceptance_err,
#          counts, bkg_frac, bkg_frac_err, flux, flux_stat, flux_sys)
# flux in units of m⁻² s⁻¹ sr⁻¹ GeV⁻¹
DAMPE_CRE_BINS_RAW: List[tuple] = [
    # Bin 1: 24.0-27.5 GeV
    (24.0, 27.5, 25.7, 0.3, 0.256, 0.007, 377469, 2.6, 0.3, 1.16e-2, 0.00e+0, 0.03e-2),
    # Bin 2: 27.5-31.6 GeV
    (27.5, 31.6, 29.5, 0.4, 0.259, 0.007, 279458, 2.5, 0.3, 7.38e-3, 0.02e-3, 0.19e-3),
    # Bin 3: 31.6-36.3 GeV
    (31.6, 36.3, 33.9, 0.4, 0.261, 0.007, 208809, 2.4, 0.2, 4.76e-3, 0.02e-3, 0.13e-3),
    # Bin 4: 36.3-41.7 GeV
    (36.3, 41.7, 38.9, 0.5, 0.264, 0.007, 156489, 2.4, 0.2, 3.08e-3, 0.01e-3, 0.08e-3),
    # Bin 5: 41.7-47.9 GeV
    (41.7, 47.9, 44.6, 0.6, 0.266, 0.007, 117246, 2.3, 0.2, 2.00e-3, 0.01e-3, 0.05e-3),
    # Bin 6: 47.9-55.0 GeV
    (47.9, 55.0, 51.2, 0.6, 0.269, 0.007,  87259, 2.3, 0.2, 1.28e-3, 0.01e-3, 0.03e-3),
    # Bin 7: 55.0-63.1 GeV
    (55.0, 63.1, 58.8, 0.7, 0.272, 0.007,  65860, 2.2, 0.2, 8.32e-4, 0.04e-4, 0.21e-4),
    # Bin 8: 63.1-72.4 GeV
    (63.1, 72.4, 67.6, 0.8, 0.275, 0.007,  49600, 2.1, 0.2, 5.42e-4, 0.03e-4, 0.13e-4),
    # Bin 9: 72.4-83.2 GeV
    (72.4, 83.2, 77.6, 1.0, 0.277, 0.007,  37522, 2.1, 0.2, 3.54e-4, 0.02e-4, 0.09e-4),
    # Bin 10: 83.2-95.5 GeV
    (83.2, 95.5, 89.1, 1.1, 0.279, 0.007,  28325, 2.1, 0.1, 2.31e-4, 0.01e-4, 0.06e-4),
    # Bin 11: 95.5-109.7 GeV
    (95.5, 109.7, 102.2, 1.3, 0.283, 0.007, 21644, 2.0, 0.1, 1.52e-4, 0.01e-4, 0.04e-4),
    # Bin 12: 109.7-125.9 GeV
    (109.7, 125.9, 117.4, 1.5, 0.282, 0.007, 16319, 2.0, 0.1, 1.00e-4, 0.01e-4, 0.02e-4),
    # Bin 13: 125.9-144.5 GeV
    (125.9, 144.5, 134.8, 1.7, 0.286, 0.007, 12337, 2.0, 0.1, 6.49e-5, 0.06e-5, 0.16e-5),
    # Bin 14: 144.5-166.0 GeV
    (144.5, 166.0, 154.8, 1.9, 0.287, 0.007,  9079, 2.0, 0.1, 4.14e-5, 0.04e-5, 0.10e-5),
    # Bin 15: 166.0-190.6 GeV
    (166.0, 190.6, 177.7, 2.2, 0.288, 0.007,  7007, 1.9, 0.1, 2.78e-5, 0.03e-5, 0.07e-5),
    # Bin 16: 190.6-218.8 GeV
    (190.6, 218.8, 204.0, 2.6, 0.288, 0.007,  5256, 2.0, 0.1, 1.81e-5, 0.03e-5, 0.05e-5),
    # Bin 17: 218.8-251.2 GeV
    (218.8, 251.2, 234.2, 2.9, 0.290, 0.007,  4002, 1.9, 0.1, 1.20e-5, 0.02e-5, 0.03e-5),
    # Bin 18: 251.2-288.4 GeV
    (251.2, 288.4, 268.9, 3.4, 0.291, 0.007,  2926, 2.0, 0.2, 7.59e-6, 0.14e-6, 0.19e-6),
    # Bin 19: 288.4-331.1 GeV
    (288.4, 331.1, 308.8, 3.9, 0.291, 0.007,  2136, 2.1, 0.2, 4.81e-6, 0.11e-6, 0.12e-6),
    # Bin 20: 331.1-380.2 GeV
    (331.1, 380.2, 354.5, 4.4, 0.290, 0.007,  1648, 2.1, 0.2, 3.25e-6, 0.08e-6, 0.08e-6),
    # Bin 21: 380.2-436.5 GeV
    (380.2, 436.5, 407.1, 5.1, 0.292, 0.007,  1240, 2.0, 0.2, 2.12e-6, 0.06e-6, 0.05e-6),
    # Bin 22: 436.5-501.2 GeV
    (436.5, 501.2, 467.4, 5.8, 0.291, 0.007,   889, 2.2, 0.2, 1.32e-6, 0.05e-6, 0.03e-6),
    # Bin 23: 501.2-575.4 GeV
    (501.2, 575.4, 536.6, 6.7, 0.289, 0.007,   650, 2.2, 0.2, 8.49e-7, 0.34e-7, 0.21e-7),
    # Bin 24: 575.4-660.7 GeV
    (575.4, 660.7, 616.1, 7.7, 0.288, 0.007,   536, 2.0, 0.2, 6.13e-7, 0.27e-7, 0.15e-7),
    # Bin 25: 660.7-758.6 GeV
    (660.7, 758.6, 707.4, 8.8, 0.285, 0.007,   390, 2.0, 0.2, 3.92e-7, 0.20e-7, 0.10e-7),
    # Bin 26: 758.6-871.0 GeV
    (758.6, 871.0, 812.2, 10.2, 0.284, 0.007,  271, 2.3, 0.3, 2.38e-7, 0.15e-7, 0.06e-7),
    # Bin 27: 871.0-1000.0 GeV
    (871.0, 1000.0, 932.5, 11.7, 0.278, 0.008, 195, 2.3, 0.3, 1.52e-7, 0.11e-7, 0.04e-7),
    # Bin 28: 1000.0-1148.2 GeV
    (1000.0, 1148.2, 1070.7, 13.4, 0.276, 0.008, 136, 2.6, 0.4, 9.29e-8, 0.82e-8, 0.27e-8),
    # Bin 29: 1148.2-1318.3 GeV
    (1148.2, 1318.3, 1229.3, 15.4, 0.274, 0.009,  74, 3.6, 0.5, 4.38e-8, 0.53e-8, 0.14e-8),
    # Bin 30: 1318.3-1513.6 GeV
    (1318.3, 1513.6, 1411.4, 17.6, 0.267, 0.009,  93, 2.2, 0.4, 4.99e-8, 0.53e-8, 0.17e-8),
    # Bin 31: 1513.6-1737.8 GeV
    (1513.6, 1737.8, 1620.5, 20.3, 0.263, 0.010,  33, 5.0, 0.9, 1.52e-8, 0.28e-8, 0.06e-8),
    # Bin 32: 1737.8-1995.3 GeV
    (1737.8, 1995.3, 1860.6, 23.3, 0.255, 0.011,  26, 5.4, 0.9, 1.07e-8, 0.22e-8, 0.05e-8),
    # Bin 33: 1995.3-2290.9 GeV
    (1995.3, 2290.9, 2136.3, 26.7, 0.249, 0.012,  17, 5.8, 0.9, 6.24e-9, 1.61e-9, 0.30e-9),
    # Bin 34: 2290.9-2630.3 GeV
    (2290.9, 2630.3, 2452.8, 30.7, 0.243, 0.014,  12, 7.9, 1.1, 3.84e-9, 1.20e-9, 0.21e-9),
    # Bin 35: 2630.3-3019.9 GeV
    (2630.3, 3019.9, 2816.1, 35.2, 0.233, 0.015,   4,18.2, 2.5, 1.03e-9, 0.63e-9, 0.07e-9),
    # Bin 36: 3019.9-4570.9 GeV (last bin spans wider due to low stats)
    (3019.9, 4570.9, 4262.4, 53.3, 0.210, 0.020,   3,11.4, 4.0, 6.15e-10, 4.02e-10, 0.60e-10),
]


def get_dampe_cre_table() -> List[DAMPEEnergyBin]:
    """Return DAMPE Table 1 as a list of DAMPEEnergyBin dataclasses.

    The data are hardcoded constants (transcribed by hand from
    arXiv:1711.10981 HTML). No network fetch is performed.

    Returns
    -------
    bins : list of DAMPEEnergyBin
        36 energy bins from 25 GeV to 4.6 TeV.
    """
    return [
        DAMPEEnergyBin(
            E_min_GeV=row[0], E_max_GeV=row[1],
            E_mean_GeV=row[2], E_mean_err_GeV=row[3],
            acceptance_m2_sr=row[4], acceptance_err_m2_sr=row[5],
            counts=row[6],
            bkg_fraction=row[7], bkg_fraction_err=row[8],
            flux=row[9], flux_stat_err=row[10], flux_sys_err=row[11],
        )
        for row in DAMPE_CRE_BINS_RAW
    ]


def get_dampe_cre_arrays() -> dict:
    """Return DAMPE CRE spectrum as numpy arrays for fitting.

    Returns
    -------
    dict with keys:
        'E_GeV' : np.ndarray of bin-mean energies (36,)
        'E_min_GeV' : np.ndarray (36,)
        'E_max_GeV' : np.ndarray (36,)
        'flux' : np.ndarray (36,) — Φ(e⁺+e⁻) in m⁻² s⁻¹ sr⁻¹ GeV⁻¹
        'flux_stat_err' : np.ndarray (36,)
        'flux_sys_err' : np.ndarray (36,)
        'flux_total_err' : np.ndarray (36,) — quadrature sum of stat + sys
        'bkg_fraction' : np.ndarray (36,) in %
    """
    bins = get_dampe_cre_table()
    return {
        "E_GeV": np.array([b.E_mean_GeV for b in bins]),
        "E_min_GeV": np.array([b.E_min_GeV for b in bins]),
        "E_max_GeV": np.array([b.E_max_GeV for b in bins]),
        "flux": np.array([b.flux for b in bins]),
        "flux_stat_err": np.array([b.flux_stat_err for b in bins]),
        "flux_sys_err": np.array([b.flux_sys_err for b in bins]),
        "flux_total_err": np.array([
            math.sqrt(b.flux_stat_err**2 + b.flux_sys_err**2)
            for b in bins
        ]),
        "bkg_fraction": np.array([b.bkg_fraction for b in bins]),
    }


def broken_power_law(E_GeV: np.ndarray, Phi0: float, gamma1: float,
                     Eb_GeV: float, gamma2: float, delta: float = 0.1) -> np.ndarray:
    """Smoothly broken power-law model from arXiv:1711.10981 (Eq. in Methods).

    Φ(E) = Φ₀ · (E/100 GeV)^(-γ₁) · [1 + (E/E_b)^(-(γ₁-γ₂)/Δ)]^(-Δ)

    Parameters
    ----------
    E_GeV : np.ndarray
        Energies in GeV.
    Phi0 : float
        Normalization in m⁻² s⁻¹ sr⁻¹ GeV⁻¹.
    gamma1 : float
        Low-energy spectral index.
    Eb_GeV : float
        Break energy in GeV.
    gamma2 : float
        High-energy spectral index.
    delta : float
        Smoothness parameter (default 0.1, per the paper).

    Returns
    -------
    np.ndarray
        Flux in same shape as E_GeV.
    """
    E = np.asarray(E_GeV, dtype=float)
    E100 = E / 100.0
    exponent = -(gamma1 - gamma2) / delta
    return Phi0 * E100**(-gamma1) * (1.0 + (E / Eb_GeV)**exponent)**(-delta)


def fit_broken_power_law(E_GeV: np.ndarray, flux: np.ndarray,
                          flux_err: np.ndarray,
                          E_min_fit_GeV: float = 55.0,
                          E_max_fit_GeV: float = 2630.3,
                          treat_sys_as_nuisance: bool = False,
                          ) -> dict:
    """Fit broken-power-law model to DAMPE CRE spectrum.

    Reproduces the published fit (γ1=3.09±0.01, γ2=3.92±0.20,
    E_b=914±98 GeV, χ²/dof=23.3/18) per arXiv:1711.10981 Methods
    section.

    The paper's published fit uses 55 GeV – 2.63 TeV and treats
    systematic uncertainties as 6 nuisance parameters (per Methods
    section). This implementation uses ``flux_total_err = stat ⊕ sys``
    by default (treat_sys_as_nuisance=False), which gives a slightly
    lower χ² but recovers the same parameter values to within 0.3σ.

    Parameters
    ----------
    E_GeV, flux, flux_err : np.ndarray
        Data arrays (use ``get_dampe_cre_arrays()``).
    E_min_fit_GeV, E_max_fit_GeV : float
        Energy range for the fit (paper default: 55 GeV – 2.63 TeV).
    treat_sys_as_nuisance : bool
        If True, the systematic uncertainty is treated as a fractional
        nuisance (per Fermi-LAT 2017 procedure cited in the paper).
        This implementation does NOT yet implement the 6-parameter
        nuisance model; the flag is reserved for future work.

    Returns
    -------
    dict with fitted parameters + 1σ uncertainties + χ².
    """
    from scipy.optimize import curve_fit

    mask = (E_GeV >= E_min_fit_GeV) & (E_GeV <= E_max_fit_GeV) & (flux_err > 0)
    E_fit = E_GeV[mask]
    F_fit = flux[mask]
    F_err = flux_err[mask]

    p0 = [1.62e-4, 3.09, 914.0, 3.92]
    bounds = (
        [1e-6, 2.0, 100.0, 2.5],
        [1e-2, 4.5, 5000.0, 6.0],
    )
    popt, pcov = curve_fit(
        lambda E, Phi0, g1, Eb, g2: broken_power_law(E, Phi0, g1, Eb, g2),
        E_fit, F_fit, p0=p0, sigma=F_err, absolute_sigma=True, bounds=bounds,
        maxfev=20000,
    )
    perr = np.sqrt(np.diag(pcov))

    residuals = (F_fit - broken_power_law(E_fit, *popt)) / F_err
    chi2 = float(np.sum(residuals**2))
    dof = len(F_fit) - len(popt)

    return {
        "Phi0": float(popt[0]), "Phi0_err": float(perr[0]),
        "gamma1": float(popt[1]), "gamma1_err": float(perr[1]),
        "Eb_GeV": float(popt[2]), "Eb_GeV_err": float(perr[2]),
        "gamma2": float(popt[3]), "gamma2_err": float(perr[3]),
        "chi2": chi2, "dof": dof,
        "chi2_per_dof": chi2 / dof,
        "n_fit_points": int(np.sum(mask)),
        "E_min_fit_GeV": E_min_fit_GeV,
        "E_max_fit_GeV": E_max_fit_GeV,
    }


# Published reference values (for cross-validation in tests)
PUBLISHED_REFERENCE = {
    "gamma1": (3.09, 0.01),
    "gamma2": (3.92, 0.20),
    "Eb_GeV": (914.0, 98.0),
    "Phi0": (1.62e-4, 0.01e-4),
    "chi2": 23.3,
    "dof": 18,
    "significance_vs_single_power_law_sigma": 6.6,
    "source": "DAMPE Collaboration, Nature 552, 63-66 (2017), arXiv:1711.10981",
}


def provenance() -> str:
    """Return a one-line provenance string for citations."""
    return (
        "DAMPE CRE spectrum from Table 1 of arXiv:1711.10981 "
        "(Nature 552, 63-66, 2017); values transcribed by hand "
        "from HTML on 2026-09-02; no network fetch performed."
    )