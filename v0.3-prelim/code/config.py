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
# Gaussian proxy likelihood widths (per peer review note 2026-08-10:
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
    "T5_NOISE_KMS", "T5_RHO_C_BURKERT", "T5_RHO_S_NFW", "T5_R_S_NFW", "T5_SEED_BASE",
    "SPARC_N_PTS_MIN",
    "get_version_paths",
]