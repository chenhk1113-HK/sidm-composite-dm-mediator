"""
T88.B — eROSITA eRASS1 Cluster Density Profile Catalog (Channel 21)

Forward model for the eROSITA-DE eRASS1 cluster density profile
constraint on sigma/m at v ~ 500 km/s.

Source: Bulbul et al. 2024 (eROSITA-DE eRASS1 cluster cosmology catalog,
A&A 685 A106, arXiv:2402.08452, cited 240+ times). 5,259 clusters with
mass measurements from X-ray hydrostatic equilibrium. Mass range:
5e12 to 2e15 M_sun. Western Galactic hemisphere only (German eROSITA
contribution halted Feb 2024, but eRASS1 data is permanent).

Physics (the SIDM signal):
- SIDM thermalizes the inner halo on a timescale t_th ~ 1/(sigma/m * rho * v)
- For ~Gyr-old clusters with rho_core ~ 1e-26 g/cm^3, thermalization requires
  sigma/m > ~0.5 cm^2/g at v=500 km/s (Brinckmann+ 2018, Robertson+ 2018,
  Mastromarino 2024 thesis).
- Below threshold: SIDM profiles look like CDM cusps (eRASS1 cannot tell).
- Above threshold: a population of CORED profiles appears.

Channel signature: (sigma_m_0, a) where
  sigma/m(v=500) = sigma_m_0 * (V_REF / v_500)^a
                 = sigma_m_0 * 10^(-a * log10(500/100))
                 = sigma_m_0 * 10^(-0.699 * a)
(velocity power-law parametrization, project standard).

Implementation: SOFT one-sided Gaussian UPPER LIMIT at sigma/m(v=500) =
EROSITA_SIGMA_M_UPPER_LIMIT (0.5 cm^2/g), matching the pattern of
Channel 8 (O'Donnell+ 2026 radio relic) and Channel 10 (Lee+ 2026 double
radio relic).

This is NOT a discovery channel — it constrains sigma/m at v=500 km/s,
which is well above the v0.7 posterior's typical sigma/m_0 ~ 0.27 cm^2/g
(unless a > 0, i.e. velocity dependence is weak). At the v0.7 MAP
(sigma_m_0=0.28, a~0.16), sigma/m(v=500) ~ 0.21 cm^2/g, BELOW the
threshold, so the channel is silent at the standing posterior.

This is the velocity-gap filler identified by the R15B dataset
reassessment (Tier-1 highest cost/impact proposal).

No-network contract (skill P9): all data is hardcoded as constants.
"""

from __future__ import annotations

import math
from typing import Tuple

from config import (
    EROSITA_SIGMA_M_UPPER_LIMIT,
    EROSITA_TAIL_WIDTH,
    EROSITA_VMAX_KMS,
    V_REF,
)

# ---------------------------------------------------------------------------
# Hardcoded eRASS1 observation constants (no-network contract, skill P9)
# ---------------------------------------------------------------------------

# Citation provenance
EROSITA_EBOSS_CATALOG = "Bulbul+ 2024 (eROSITA-DE eRASS1 cluster catalog)"
EROSITA_ARXIV_ID = "arXiv:2402.08452"
EROSITA_DOI = "10.1051/0004-6361/20248264"
EROSITA_N_CLUSTERS = 5259
EROSITA_MASS_RANGE_MSUN = (5.0e12, 2.0e15)

# Core-formation threshold: derived from SIDM thermalization theory
# (Brinckmann+ 2018, Robertson+ 2018), not from a single observation.
# This is a SIMPLE one-sided constraint; the literature has tighter
# constraints from double radio relics (sigma/m < 0.22 at 95% CL, Lee+ 2026)
# but those are at v > 1000 km/s. eROSITA's v ~ 500 km/s fills a gap.
EROSITA_CITATION_CORE_THRESHOLD = "Brinckmann+ 2018 (arXiv:1712.04387); Robertson+ 2018 (arXiv:1712.05803); Mastromarino 2024 (Bologna thesis)"


# ---------------------------------------------------------------------------
# Forward model: convert T41 (sigma_m_0, a) → sigma/m at v=500 km/s
# ---------------------------------------------------------------------------


def sigma_m_at_v_erosita(sigma_m_0: float, a: float) -> float:
    """Project-standard power-law velocity scaling.

    sigma/m(v) = sigma_m_0 * (v / V_REF)^(-a)
              = sigma_m_0 * (V_REF / v)^(+a)
              = sigma_m_0 * (V_REF / v_erosita)^a

    Parameters
    ----------
    sigma_m_0 : float
        sigma/m at V_REF = 100 km/s (cm^2/g)
    a : float
        velocity power-law index (a > 0 means sigma/m DECREASES with v)

    Returns
    -------
    float : sigma/m at v = EROSITA_VMAX_KMS (500 km/s), cm^2/g
    """
    if sigma_m_0 <= 0 or not math.isfinite(sigma_m_0):
        return 0.0
    if not math.isfinite(a):
        return 0.0
    return sigma_m_0 * (V_REF / EROSITA_VMAX_KMS) ** a


# ---------------------------------------------------------------------------
# Channel 21 log-likelihood: one-sided Gaussian upper limit
# ---------------------------------------------------------------------------


def loglike_erosita_erass1(sigma_m_0: float, a: float) -> float:
    """Channel 21: eROSITA eRASS1 cluster density profile constraint.

    Soft one-sided Gaussian upper limit on sigma/m(v=500). Below the
    threshold EROSITA_SIGMA_M_UPPER_LIMIT = 0.5 cm^2/g, returns 0 (no
    constraint — SIDM profiles look like CDM cusps and eRASS1 cannot
    tell them apart). Above the threshold, Gaussian penalty in dex.

    Parameters
    ----------
    sigma_m_0 : float
        sigma/m at V_REF = 100 km/s (cm^2/g)
    a : float
        velocity power-law index

    Returns
    -------
    float : log likelihood (relative units). 0 if within; negative if above.
    """
    if sigma_m_0 <= 0 or not math.isfinite(sigma_m_0):
        return -math.inf
    if not math.isfinite(a):
        return -math.inf

    sigma_m_v500 = sigma_m_at_v_erosita(sigma_m_0, a)
    log_sigma = math.log10(sigma_m_v500)
    log_upper = math.log10(EROSITA_SIGMA_M_UPPER_LIMIT)

    # Below threshold: silent (within eRASS1 measurement noise).
    if log_sigma < log_upper:
        return 0.0

    # Above threshold: one-sided Gaussian penalty, in dex.
    excess = log_sigma - log_upper
    chi2 = (excess / EROSITA_TAIL_WIDTH) ** 2
    return -0.5 * chi2


# ---------------------------------------------------------------------------
# Diagnostic helpers
# ---------------------------------------------------------------------------


def summary_erosita_erass1_consistency_test(
    sigma_m_0_grid: Tuple[float, ...] = (0.01, 0.05, 0.1, 0.2, 0.28, 0.5, 1.0, 3.0, 10.0),
    a_grid: Tuple[float, ...] = (-0.5, 0.0, 0.16, 0.5, 1.0),
) -> str:
    """Print a grid of sigma/m(v=500) and log L values for sanity-checking."""
    lines = [
        "T88.B Channel 21 consistency test (eROSITA eRASS1)",
        "=" * 70,
        f"  threshold: sigma/m(v={EROSITA_VMAX_KMS}) = {EROSITA_SIGMA_M_UPPER_LIMIT} cm^2/g",
        f"  tail width (dex): {EROSITA_TAIL_WIDTH}",
        "",
    ]
    header = f"{'sigma_m_0':>10s} | " + " | ".join(
        f"a={a:+.2f}" for a in a_grid
    )
    lines.append(header)
    lines.append("-" * len(header))

    for sm in sigma_m_0_grid:
        cells = []
        for a in a_grid:
            sm_v500 = sigma_m_at_v_erosita(sm, a)
            ll = loglike_erosita_erass1(sm, a)
            cells.append(f"{sm_v500:.3f} ({ll:+.2f})")
        lines.append(f"{sm:>10.3f} | " + " | ".join(cells))

    lines.append("")
    lines.append("Cells show sigma/m(v=500) cm^2/g and (log L contribution).")
    lines.append("log L = 0 (silent) when sigma/m(v=500) < 0.5 cm^2/g.")
    lines.append("log L < 0 (penalty) when sigma/m(v=500) > 0.5 cm^2/g.")
    return "\n".join(lines)


def provenance() -> str:
    """One-line citation string for the channel."""
    return (
        f"T88.B Channel 21 (eROSITA eRASS1): "
        f"{EROSITA_EBOSS_CATALOG} ({EROSITA_ARXIV_ID}, "
        f"DOI {EROSITA_DOI}, {EROSITA_N_CLUSTERS} clusters, "
        f"M = {EROSITA_MASS_RANGE_MSUN[0]:.1e}-{EROSITA_MASS_RANGE_MSUN[1]:.1e} M_sun). "
        f"Core-formation threshold: {EROSITA_CITATION_CORE_THRESHOLD}."
    )


# ---------------------------------------------------------------------------
# __main__ smoke test (no pytest required)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(provenance())
    print()
    print(summary_erosita_erass1_consistency_test())