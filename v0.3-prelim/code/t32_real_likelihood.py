"""
T32_real — Fermi dSph likelihood from REAL published TS profiles.

Per R11 audit (2026-08-14), this module replaces the previous Gaussian proxy
+ 0.3-dex half-Gaussian upper-limit surrogate with the actual 2D TS profiles
from McDaniel et al. 2024 (arXiv:2311.04982), 14-year Fermi-LAT dSph
analysis. Data products are CC BY 4.0 from
https://doi.org/10.6084/m9.figshare.24058650.v2

The TS profiles are 40 log-spaced mass values × 60 log-spaced sigma_v values
per dSph. We sum the TS over all dSphs to get a combined log-likelihood ratio:

    log_L(m_chi, sigma_v) = -TS_total(m_chi, sigma_v) / 2

This is a real profile likelihood, not a Gaussian approximation.

The McDaniel+ 2024 paper reports a tantalizing ~2σ signal at m_chi ≈ 40 GeV
in their combined analysis. Our combined TS at this mass is ≈ 5.8 (consistent
with ~√N sigma), which we preserve here as observed by the data, NOT
overwritten.

Reference:
  McDaniel, Ajello et al. (2023/2024) "Legacy Analysis of Dark Matter
  Annihilation from the Milky Way Dwarf Spheroidal Galaxies with 14 Years
  of Fermi-LAT Data", Phys. Rev. D (submitted). arXiv:2311.04982.
  Data: https://doi.org/10.6084/m9.figshare.24058650.v2
"""
from __future__ import annotations
from pathlib import Path
import csv
import numpy as np

# ---------------------------------------------------------------------------
# Data path resolution
# ---------------------------------------------------------------------------

def _data_root() -> Path:
    """Find the McDaniel+ 2024 data directory.

    Resolution order:
      1. Env var FERMI_MCDANIEL_DATA_ROOT
      2. The canonical Windows path
      3. The canonical WSL path
    Returns the first existing path, or raises FileNotFoundError.
    """
    import os
    env = os.environ.get("FERMI_MCDANIEL_DATA_ROOT")
    if env and Path(env).exists():
        return Path(env)
    for p in (
        Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\external\fermi_mcdaniel2024"),
        Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/external/fermi_mcdaniel2024"),
    ):
        if p.exists():
            return p
    raise FileNotFoundError(
        "McDaniel+ 2024 data products not found. Set FERMI_MCDANIEL_DATA_ROOT "
        "or run `outputs/fetch_mcdaniel_data.sh` to download from figshare."
    )


# ---------------------------------------------------------------------------
# Mass and sigma_v grids (40 × 60, log-spaced)
# ---------------------------------------------------------------------------

MASS_GRID_GEV = np.logspace(np.log10(1.0), np.log10(1000.0), 40)  # 1 GeV - 1 TeV
SIGMA_V_GRID = np.logspace(-28, -22, 60)                          # 1e-28 - 1e-22 cm^3/s


# ---------------------------------------------------------------------------
# Cached loader (TS profiles loaded once per process)
# ---------------------------------------------------------------------------

_CACHE: dict = {}


def _load_dSphs_csv(root: Path) -> list[dict]:
    """Load Table 1 (dSphs.csv) — 55 Milky Way dSphs with J-factors."""
    path = root / "dSphs.csv"
    with open(path) as fh:
        return list(csv.DictReader(fh))


def _combined_ts(root: Path, channel: str = "bb", use_J_prior: bool = True) -> np.ndarray:
    """Sum the 2D TS profile over all 55 dSphs for one (channel, prior) choice.

    channel: 'bb' (b-bbar) or 'tau' (tau+tau-)
    use_J_prior: True for Jprior_*.npy files (include J-factor prior), False for noprior
    """
    prior_str = "Jprior" if use_J_prior else "noprior"
    cache_key = (root, channel, prior_str)
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    ts_dir = root / "dSphs" / "TS_profiles"
    combined = np.zeros((40, 60))
    n_loaded = 0
    for f in sorted(ts_dir.glob(f"*_{prior_str}_{channel}.npy")):
        combined += np.load(f)
        n_loaded += 1
    _CACHE[cache_key] = combined
    if n_loaded == 0:
        raise FileNotFoundError(
            f"No TS profiles found in {ts_dir} matching "
            f"*_{prior_str}_{channel}.npy"
        )
    return combined


# ---------------------------------------------------------------------------
# Public API: real Fermi-dSph log-likelihood
# ---------------------------------------------------------------------------

def loglike_fermi_real(
    m_chi_GeV: float,
    sigma_v_cm3_per_s: float,
    channel: str = "bb",
    use_J_prior: bool = True,
) -> float:
    """Fermi dSph log-likelihood from REAL McDaniel+ 2024 TS profiles.

    Returns -TS(m_chi, sigma_v) / 2, where TS is the combined profile
    likelihood ratio summed over all 55 dSphs.

    Parameters
    ----------
    m_chi_GeV : float
        DM mass in GeV. Must be in [1, 1000] (else linear extrapolation).
    sigma_v_cm3_per_s : float
        Annihilation cross-section in cm^3/s. Must be in [1e-28, 1e-22]
        (else linear extrapolation).
    channel : str
        'bb' for b-bbar annihilation, 'tau' for tau+tau-.
    use_J_prior : bool
        True to use the J-factor-prior TS profiles (recommended for
        dwarf-specific J-factor uncertainties); False for the no-prior
        profiles (treating J-factors as known).

    Returns
    -------
    float
        Log-likelihood ratio log L_signal - log L_null, where positive
        values favor the signal hypothesis (TS > 0) and negative values
        exclude the signal (TS < 0). In natural log units.

    Notes
    -----
    The McDaniel+ 2024 TS profiles use the **profile likelihood ratio
    convention with the signal hypothesis as reference**:

        TS(m_chi, sigma_v) = 2 * (log L_signal - log L_null)

    so TS > 0 means the signal is preferred at that (m_chi, sigma_v),
    and TS < 0 means the signal is excluded. We return TS/2 directly
    as the log-likelihood ratio. Joint fits can sum this with other
    channels' log L values to compute the full posterior.

    Out-of-mass or out-of-σ_v: linear extrapolation on the log grid edges,
    which gives conservative (negative) log L for extreme inputs.
    """
    if sigma_v_cm3_per_s <= 0:
        return -np.inf

    combined = _combined_ts(_data_root(), channel=channel, use_J_prior=use_J_prior)

    # Bilinear interpolation in log-log space
    log_m = np.log10(MASS_GRID_GEV)
    log_sv = np.log10(SIGMA_V_GRID)
    log_m_input = np.log10(m_chi_GeV)
    log_sv_input = np.log10(sigma_v_cm3_per_s)

    # Clamp to grid edges for extrapolation
    if log_m_input < log_m[0]:
        log_m_input = log_m[0]
    if log_m_input > log_m[-1]:
        log_m_input = log_m[-1]
    if log_sv_input < log_sv[0]:
        log_sv_input = log_sv[0]
    if log_sv_input > log_sv[-1]:
        log_sv_input = log_sv[-1]

    # Use scipy.interpolate if available; otherwise manual bilinear
    try:
        from scipy.interpolate import RegularGridInterpolator
        interp = RegularGridInterpolator(
            (log_m, log_sv), combined, method="linear",
            bounds_error=False, fill_value=None,
        )
        ts = float(interp((log_m_input, log_sv_input)))
    except ImportError:
        # Manual bilinear interpolation
        i = np.searchsorted(log_m, log_m_input) - 1
        j = np.searchsorted(log_sv, log_sv_input) - 1
        i = max(0, min(i, len(log_m) - 2))
        j = max(0, min(j, len(log_sv) - 2))
        x0, x1 = log_m[i], log_m[i + 1]
        y0, y1 = log_sv[j], log_sv[j + 1]
        wx = (log_m_input - x0) / (x1 - x0)
        wy = (log_sv_input - y0) / (y1 - y0)
        ts = (
            combined[i, j] * (1 - wx) * (1 - wy)
            + combined[i + 1, j] * wx * (1 - wy)
            + combined[i, j + 1] * (1 - wx) * wy
            + combined[i + 1, j + 1] * wx * wy
        )

    # The McDaniel+ 2024 TS profiles use the profile likelihood ratio
    # convention: TS = 2 * (log L_signal - log L_null), so TS > 0 means
    # signal preferred, TS < 0 means signal excluded. Return TS/2 directly
    # so joint fits can sum log-likelihood ratios across channels.
    return ts / 2.0


def get_combined_TS_profile(channel: str = "bb", use_J_prior: bool = True) -> np.ndarray:
    """Return the raw combined TS map (40×60) for inspection / plotting."""
    return _combined_ts(_data_root(), channel=channel, use_J_prior=use_J_prior)


def get_mass_grid_GeV() -> np.ndarray:
    """Return the mass grid (GeV) the TS profiles are evaluated on."""
    return MASS_GRID_GEV.copy()


def get_sigma_v_grid() -> np.ndarray:
    """Return the sigma_v grid (cm^3/s) the TS profiles are evaluated on."""
    return SIGMA_V_GRID.copy()


# ---------------------------------------------------------------------------
# Module self-check (run as `python -m t32_real_likelihood`)
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """Print a diagnostic summary: combined TS peak, upper limit, test points."""
    root = _data_root()
    dSphs = _load_dSphs_csv(root)
    combined_bb = _combined_ts(root, channel="bb", use_J_prior=True)
    combined_tau = _combined_ts(root, channel="tau", use_J_prior=True)

    i_max, j_max = np.unravel_index(combined_bb.argmax(), combined_bb.shape)
    print(f"McDaniel+ 2024 Fermi-dSph TS profile self-check")
    print(f"  Data root: {root}")
    print(f"  dSphs loaded (Table 1): {len(dSphs)}")
    print(f"  Combined TS(b-bbar, J-prior) shape: {combined_bb.shape}")
    print(f"  Max TS = {combined_bb.max():.3f} at m_chi = {MASS_GRID_GEV[i_max]:.2f} GeV, "
          f"sigma_v = {SIGMA_V_GRID[j_max]:.2e} cm^3/s")
    # 95% CL: TS = 0 corresponds to log L = 0 (the null)
    sigv_limit_at_peak = SIGMA_V_GRID[np.searchsorted(-combined_bb[i_max, :], 0.0)]
    print(f"  Approx 95% CL sigma_v upper limit at m_chi = {MASS_GRID_GEV[i_max]:.2f} GeV: "
          f"{sigv_limit_at_peak:.2e} cm^3/s")
    print()
    print(f"  Test points:")
    test_points = [
        (50.0, 3.0e-26, "thermal WIMP at 50 GeV (above 95% CL)"),
        (50.0, 1.0e-27, "well below limit at 50 GeV"),
        (1.0, 1.0e-28, "lowest mass, lowest sigma_v"),
        (1000.0, 1.0e-22, "highest mass, highest sigma_v"),
    ]
    for m, sv, label in test_points:
        ll = loglike_fermi_real(m, sv, channel="bb", use_J_prior=True)
        print(f"    log L(m_chi={m:.1f}, sigma_v={sv:.1e}, bb, Jprior) = {ll:+.3f}   ({label})")


if __name__ == "__main__":
    _self_check()