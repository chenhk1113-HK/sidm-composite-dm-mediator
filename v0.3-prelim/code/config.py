"""
Central configuration for sidm-composite-dm-mediator.

All paths, constants, prior ranges, sampler hyperparameters, and
observational velocity scales live here. Other modules import from
config — no hardcoded duplicates.

Generated in response to peer review (2026-08-10):
    "Hardcoded absolute paths everywhere; zero configuration system"
"""
from __future__ import annotations
from pathlib import Path
import os

# ---------------------------------------------------------------------------
# Filesystem paths
#
# Auto-detect: try WSL path first (where the heavy compute runs), fall back
# to Windows path (where Telegram delivery / file management happens).
# Override via env vars DM_SIDM_DATA_ROOT / DM_SIDM_RESULTS_ROOT / DM_SIDM_PLOTS_ROOT.
# ---------------------------------------------------------------------------

def _detect_root() -> Path:
    """Find the project root on this host."""
    # Windows path (canonical for Telegram MEDIA: + Windows tools)
    win = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
    if win.exists():
        return win
    # WSL path (where dynesty runs)
    wsl = Path("/home/lamkuenai/sidm-composite-dm-mediator")
    if wsl.exists():
        return wsl
    raise FileNotFoundError("sidm-composite-dm-mediator project root not found")


PROJECT_ROOT = Path(os.environ.get("DM_SIDM_PROJECT_ROOT", _detect_root()))

# Subdirectories
V01 = PROJECT_ROOT / "v0.1-prelim"
V02 = PROJECT_ROOT / "v0.2-prelim"
V03 = PROJECT_ROOT / "v0.3-prelim"

DATA_DIR = V01 / "data" / "Rotmod_LTG"  # SPARC rotmod files live in v0.1
RESULTS_DIR_V01 = V01 / "data" / "results"
RESULTS_DIR_V02 = V02 / "data" / "results"
RESULTS_DIR_V03 = V03 / "data" / "results"
PLOTS_DIR_V02 = V02 / "plots"
PLOTS_DIR_V03 = V03 / "plots"
DOCS_DIR_V01 = V01 / "docs"
DOCS_DIR_V02 = V02 / "docs"
DOCS_DIR_V03 = V03 / "docs"

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

G_KPC_KMS = 4.302e-6  # kpc km^2 / (M_sun s^2) — Newton's G in convenient units

# Velocity scales for each observational channel (km/s)
V_REF = 100.0    # Reference velocity at which sigma/m_0 is quoted
V_UFD = 10.0     # Ultra-faint dwarf v_max
V_DSPH = 30.0    # MW classical dSph v_max
V_GALAXY = 100.0 # Normal galaxy (== V_REF, by construction)
V_CLUSTER = 1500.0  # Bullet Cluster v_max

# ---------------------------------------------------------------------------
# Halo profile density priors (log10 M_sun / kpc^3)
# ---------------------------------------------------------------------------

VDEP_LOG_RHO_RANGE = (2.0, 10.0)  # v-dep Burkert rho_c range

# ---------------------------------------------------------------------------
# dynesty sampler hyperparameters (locked across versions for fair model comparison)
# ---------------------------------------------------------------------------

NLIVE = 500       # number of live points (use 200 for faster exploratory runs)
DLOGZ = 0.10      # stopping criterion on log evidence

# ---------------------------------------------------------------------------
# SIDM posterior fit ranges (log10 sigma/m, velocity power-law a)
# ---------------------------------------------------------------------------

LOG_SIGMA_M_RANGE = (-3.0, 2.5)  # log10(cm^2/g) at v_ref = 100 km/s
A_RANGE = (-2.0, 2.0)            # velocity power-law index

# ---------------------------------------------------------------------------
# Channel-specific Gaussian proxy widths (per peer review note 2026-08-10:
# "crude Gaussian approximations" — these are placeholders until
# published posterior chains are obtained).
# ---------------------------------------------------------------------------

# dSph (Horigome+ 2025 bimodal posterior) — peak positions and widths
DSPH_PEAK_LOG_SM = (-1.0, 1.0)    # bimodal peaks at sigma/m = 0.1 and 10 cm^2/g
DSPH_PEAK_WIDTH = 0.4              # dex width of each peak
DSPH_DIP_CENTER = 0.0             # log10(sigma/m) ~ 1 cm^2/g
DSPH_DIP_WIDTH = 0.15             # dex width of exclusion dip
DSPH_DIP_STRENGTH = 5.0           # penalty multiplier at dip

# UFD (Sanchez-Almeida+ 2025)
UFD_LOG_SM_MEAN = 0.92            # sigma/m = 10^0.92 cm^2/g
UFD_LOG_SM_SIGMA = 1.37           # 1-sigma width in dex

# Bullet Cluster (Cha+ 2025)
BULLET_LOG_SM_LIMIT = -0.30103    # log10(0.5) = upper limit at 95% CL
BULLET_TAIL_WIDTH = 0.30          # one-sided Gaussian tail width

# Gravitational lensing substructure (Yang+ 2026 PRL — Channel 6)
# Channel 6: σ/m peak at log10(50) cm^2/g = 1.7, 0.3 dex width
LENS_SIGMA_M_LOG_PEAK = 1.7       # log10(cm^2/g) — middle of 30-100 range
LENS_SIGMA_M_LOG_WIDTH = 0.3      # dex — covers the 30-100 range

# MW satellite upper limit (Hayashi+ 2025 — Channel 7)
DSPH_SIGMA_M_UPPER_LIMIT = 0.2    # cm^2/g — Hayashi+ 2025 95% upper limit
DSPH_VMAX_KMS = 18.0              # characteristic UFD velocity in the paper

# Cluster upper limit (O'Donnell+ 2026 PRD — Channel 8)
CLUSTER_VMAX_KMS = 2090.0         # MACS J0138-2155 interaction velocity
CLUSTER_SIGMA_M_UPPER_LIMIT = 0.613  # cm^2/g — O'Donnell+ 2026 PRD 95% CL

# Draco dSph upper limit (Read+ 2018 — Channel 9)
DRACO_SIGMA_M_UPPER_LIMIT = 0.57  # cm^2/g — Read+ 2018 99% CL upper limit
DRACO_VMAX_KMS = 20.0             # Draco internal velocity scale

# 11-cluster double radio relic (Lee+ 2026 — Channel 10)
RADIO_RELIC_SIGMA_M_UPPER_LIMIT = 0.22   # cm^2/g — Lee+ 2026 68% upper limit
RADIO_RELIC_VMAX_KMS = 1000.0            # characteristic cluster merger velocity

# eROSITA eRASS1 cluster density profile catalog (T88.B — Channel 21)
# Bulbul et al. 2024 (eROSITA-DE eRASS1 cluster cosmology catalog, A&A 685 A106,
# arXiv:2402.08452, 5259 clusters, M = 5e12 to 2e15 Msun, Western Galactic
# hemisphere). Velocity scale = 500 km/s (intermediate-mass groups/clusters).
# Core-formation threshold for SIDM profiles (Brinckmann+ 2018, Robertson+ 2018,
# Mastromarino 2024 thesis): if sigma/m(v=500) > ~0.5 cm^2/g, eRASS1 clusters
# should show a population of CORED density profiles (vs CDM cusps). Below this
# threshold, profiles look indistinguishable from CDM within eRASS1 measurement
# errors. Implemented as a SOFT one-sided Gaussian upper limit, matching the
# pattern of Channel 8 (radio relic) and Channel 10 (double radio relic).
EROSITA_VMAX_KMS = 500.0                    # characteristic cluster v_max
EROSITA_SIGMA_M_UPPER_LIMIT = 0.5           # cm^2/g — core-formation threshold
EROSITA_TAIL_WIDTH = 0.30                   # dex — soft Gaussian tail width

# XRISM Resolve φ→γγ decay line null-channel (Bulbul+ 2024 §3, R15B P6b audit — Channel 22 documented null)
# At v0.7 ε ~ 1e-37, the predicted decay photon energy E_gamma = m_phi/2 is in the 100-500 MeV
# range, ABOVE XRISM Resolve's band of 0.3-12 keV by 4-5 orders of magnitude. Combined with
# τ_phi ~ 4e32 yr (vs Hubble time 1.4e10 yr), the channel is doubly null: wrong energy band
# AND impossibly long lifetime. Ship as audit trail; not a real constraint.
XRISM_RESOLVE_BAND_LOW_KEV = 0.3          # XRISM Resolve low-energy cutoff
XRISM_RESOLVE_BAND_HIGH_KEV = 12.0        # XRISM Resolve high-energy cutoff
XRISM_RESOLVE_EFFECTIVE_AREA_CM2 = 160.0  # ~160 cm^2 at 6 keV (XRISM Resolve spec)
XRISM_RESOLVE_FOV_ARCMIN2 = 1.0           # ~1 sq.arcmin effective FOV at Perseus
XRISM_PHI_DECAY_PERSIAN_FOV_KPC3 = 1.0e5  # ~100 kpc^3 effective volume at Perseus (D=74 Mpc)
XRISM_PHI_DECAY_HARD_CAP_EPS = 1.0e-30    # numerical breakdown cap on epsilon
XRISM_PHI_DECAY_PREFACTOR_GEV2 = 1.0e-10  # portal prefactor (model-dependent, see doc)

# Euclid Q1 strong-lensing cluster catalog (Bergamini+ 2026 - XXXIII, Channel 23)
# Source: A&A 711 A33, arXiv:2503.15330, DOI 10.1051/0004-6361/202554577
# 14 grade-A strong-lensing clusters (P_lens=1) from 63.1 deg^2 Euclid Q1 field
# Mass profiles derived from gravitational lensing arcs and multiple images.
EUCLID_Q1_VMAX_KMS = 1000.0                   # characteristic cluster v_max
EUCLID_Q1_N_GRADE_A_CLUSTERS = 14            # P_lens=1 grade-A clusters
EUCLID_Q1_SIGMA_M_UPPER_LIMIT = 0.5          # cm^2/g - same core-formation threshold as eROSITA
EUCLID_Q1_TAIL_WIDTH = 0.30                  # dex - matches Channels 8/10/21

# Euclid Q1 subhalo dN/dM FORECAST channel (T88.E, Channel 24)
# **FORECAST** via LensPop pipeline. Euclid Q1 measurement not yet available;
# expected with DR1 at end of 2026. Label honestly as forecast.
# Velocity regime: v ~ 150 km/s (intermediate between UFD and cluster scales).
EUCLID_Q1_SUBHALO_VMAX_KMS = 150.0                  # characteristic subhalo v_max
EUCLID_Q1_SUBHALO_SIGMA_M_LOWER = 0.05             # cm^2/g - too little evaporation (CDM-like)
EUCLID_Q1_SUBHALO_SIGMA_M_UPPER = 0.10             # cm^2/g - too much evaporation (no subhalos)
EUCLID_Q1_SUBHALO_TAIL_WIDTH = 0.30                # dex - matches Channels 8/10/21/23
EUCLID_Q1_SUBHALO_FORECAST_LABEL = "FORECAST_via_LensPop"

# NGC 1052-DF2/DF4 + FCC 224/240 dark-matter-free UDG (van Dokkum+ 2018-2026 — Channel 11)
# T70: Gaussian consistency check centered at v0.3-prelim MAP, 2 dex width
DM_FREE_UDG_RATE_PEAK = 0.0       # log-likelihood peak (centered at MAP)
DM_FREE_UDG_RATE_WIDTH = 2.0      # dex — 2 order of magnitude Gaussian width

# Cosmic-web radio synchrotron 40x excess (Pinetti+ 2025-26 — Channel 12)
# T70: Gaussian UPPER LIMIT on dark photon kinetic mixing at log10(eps_upper) = -11
COSMIC_WEB_RADIO_LOG_EPSILON_UPPER = -11.0   # log10(eps_upper) where over-prediction begins

# SIDM quantum-statistical lower mass bound (T70.1 — Channel 13)
# Lower bound on fermionic DM mass (Tremaine-Gunn 1979 + dynamical friction)
TREMAINE_GUNN_MASS_BOUND_EV = 100.0    # eV — fermionic DM (Pauli exclusion)
# Lower bound on bosonic ULDM mass (Rogers & Peiris 2021 Lyman-alpha)
ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV = 2.0e-20   # eV — bosonic ULDM (95% CL)
# Actual floor enforced: max of the two bounds (Tremaine-Gunn is binding for SIDM)
SIDM_MASS_CLASSICAL_FLOOR_EV = max(
    TREMAINE_GUNN_MASS_BOUND_EV,
    ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV,
)

# ---------------------------------------------------------------------------
# Mock-data validation (T5 full)
# ---------------------------------------------------------------------------

T5_NOISE_KMS = 5.0        # km/s velocity uncertainty
T5_RHO_C_BURKERT = 10**7.5  # M_sun/kpc^3, core density for SIDM mocks
T5_RHO_S_NFW = 1e7        # M_sun/kpc^3, scale density for CDM mocks
T5_R_S_NFW = 10.0         # kpc, scale radius for CDM mocks
T5_SEED_BASE = 42         # base RNG seed for reproducibility

# ---------------------------------------------------------------------------
# SPARC per-galaxy data quality
# ---------------------------------------------------------------------------

SPARC_N_PTS_MIN = 20      # minimum data points per galaxy for inclusion


def get_version_paths(version: str) -> dict:
    """Return dict of paths for a given version ('v01', 'v02', 'v03')."""
    if version == "v01":
        return {
            "root": V01,
            "code": V01 / "code",
            "data": V01 / "data",
            "docs": DOCS_DIR_V01,
            "plots": V01 / "plots",
            "results": RESULTS_DIR_V01,
        }
    if version == "v02":
        return {
            "root": V02,
            "code": V02 / "code",
            "data": V02 / "data",
            "docs": DOCS_DIR_V02,
            "plots": PLOTS_DIR_V02,
            "results": RESULTS_DIR_V02,
        }
    if version == "v03":
        return {
            "root": V03,
            "code": V03 / "code",
            "data": V03 / "data",
            "docs": DOCS_DIR_V03,
            "plots": PLOTS_DIR_V03,
            "results": RESULTS_DIR_V03,
        }
    raise ValueError(f"unknown version: {version!r}")


__all__ = [
    "PROJECT_ROOT", "V01", "V02", "V03",
    "DATA_DIR", "RESULTS_DIR_V01", "RESULTS_DIR_V02", "RESULTS_DIR_V03",
    "PLOTS_DIR_V02", "PLOTS_DIR_V03",
    "DOCS_DIR_V01", "DOCS_DIR_V02", "DOCS_DIR_V03",
    "G_KPC_KMS",
    "V_REF", "V_UFD", "V_DSPH", "V_GALAXY", "V_CLUSTER",
    "VDEP_LOG_RHO_RANGE",
    "NLIVE", "DLOGZ",
    "LOG_SIGMA_M_RANGE", "A_RANGE",
    "DSPH_PEAK_LOG_SM", "DSPH_PEAK_WIDTH",
    "DSPH_DIP_CENTER", "DSPH_DIP_WIDTH", "DSPH_DIP_STRENGTH",
    "UFD_LOG_SM_MEAN", "UFD_LOG_SM_SIGMA",
    "BULLET_LOG_SM_LIMIT", "BULLET_TAIL_WIDTH",
    "LENS_SIGMA_M_LOG_PEAK", "LENS_SIGMA_M_LOG_WIDTH",
    "DSPH_SIGMA_M_UPPER_LIMIT", "DSPH_VMAX_KMS",
    "CLUSTER_VMAX_KMS", "CLUSTER_SIGMA_M_UPPER_LIMIT",
    "DRACO_SIGMA_M_UPPER_LIMIT", "DRACO_VMAX_KMS",
    "RADIO_RELIC_SIGMA_M_UPPER_LIMIT", "RADIO_RELIC_VMAX_KMS",
    "EROSITA_VMAX_KMS", "EROSITA_SIGMA_M_UPPER_LIMIT", "EROSITA_TAIL_WIDTH",
    "XRISM_RESOLVE_BAND_LOW_KEV", "XRISM_RESOLVE_BAND_HIGH_KEV",
    "XRISM_RESOLVE_EFFECTIVE_AREA_CM2", "XRISM_RESOLVE_FOV_ARCMIN2",
    "XRISM_PHI_DECAY_PERSIAN_FOV_KPC3", "XRISM_PHI_DECAY_HARD_CAP_EPS",
    "XRISM_PHI_DECAY_PREFACTOR_GEV2",
    "EUCLID_Q1_VMAX_KMS", "EUCLID_Q1_N_GRADE_A_CLUSTERS",
    "EUCLID_Q1_SIGMA_M_UPPER_LIMIT", "EUCLID_Q1_TAIL_WIDTH",
    "EUCLID_Q1_SUBHALO_VMAX_KMS", "EUCLID_Q1_SUBHALO_SIGMA_M_LOWER",
    "EUCLID_Q1_SUBHALO_SIGMA_M_UPPER", "EUCLID_Q1_SUBHALO_TAIL_WIDTH",
    "EUCLID_Q1_SUBHALO_FORECAST_LABEL",
    "DM_FREE_UDG_RATE_PEAK", "DM_FREE_UDG_RATE_WIDTH",
    "COSMIC_WEB_RADIO_LOG_EPSILON_UPPER",
    "TREMAINE_GUNN_MASS_BOUND_EV",
    "ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV",
    "SIDM_MASS_CLASSICAL_FLOOR_EV",
    "T5_NOISE_KMS", "T5_RHO_C_BURKERT", "T5_RHO_S_NFW", "T5_R_S_NFW", "T5_SEED_BASE",
    "SPARC_N_PTS_MIN",
    "get_version_paths",
]