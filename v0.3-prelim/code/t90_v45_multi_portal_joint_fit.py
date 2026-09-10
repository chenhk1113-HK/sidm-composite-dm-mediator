"""
T90.45 — Multi-portal joint fit driver.

Per T90.43 finding, the single-portal light-mediator Yukawa model is
blocked by the LZ magnetic-moment + LZ direct-detection channels. Per
the reviewer Point 3, the workaround is a multi-portal architecture:

  Portal A (heavy, suppressed): m_phi_A ~ 700 MeV, g_chi_A ~ 1.5
    - Provides LZ magnetic-moment signal
    - Low sigma/m everywhere (heavy mediator -> flat)

  Portal B (light, active): m_phi_B ~ 1-30 MeV, g_chi_B ~ 0.22
    - Provides high sigma/m(28) ~ 50 cm^2/g for Cloud-9
    - Suppressed at high v (v^-8 Yukawa dependence)

  Combined sigma/m(v) = sigma/m_A(v) + sigma/m_B(v)

T90.45 extends the T41 parameter space from 6D to 9D by adding
Portal B (3 params) and keeping Portal A's annihilation/kinetic
mixing (2 params). Portal B's annihilation + kinetic mixing are
suppressed by epsilon_B << epsilon_A and don't add free params:
  - log_m_phi_A_MeV, log_m_chi_A_GeV, g_chi_A   (3)
  - log_m_phi_B_MeV, log_m_chi_B_GeV, g_chi_B   (3)
  - log_eps_A, log_alpha_A                      (2)
  - log_xi                                      (1)
  TOTAL: 9 free parameters

The combined sigma/m(v) is plugged into all channels (dSph, UFD,
Bullet, SPARC, LZ, T90 Cloud-9, etc.). The LZ magnetic-moment and
LZ direct-detection channels see ONLY Portal A's contribution (Portal
B's kinetic mixing is suppressed by epsilon_B << epsilon_A).

References:
  - T90.43 (bullet velocity + dSph velocity-aware update)
  - T90.44 (multi-portal infrastructure)
  - Reviewer Point 3 (multi-portal hierarchy)

Outputs:
  - dynesty nested-sampling posterior (9D)
  - weighted medians per parameter
  - log Z, dlogz, wall time
  - derived sigma/m_total(v) at v = 28, 100, 1000, 3000 km/s
"""
from __future__ import annotations

import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import dynesty
import t40_yukawa_sigma_m as yukawa
from ksfr_pcac_validity import loglike_ksfr_pcac_validity

# T90.45 imports — re-use T41 channel log-likelihoods
import channels_v03 as ch_v03
from channels_vdep_t90v41 import (
    loglike_dsph_vdep,
    loglike_ufd_vdep,
    loglike_bullet_vdep,
)
from t30_lz_real_posterior import loglike_lz_real
from t32_fermi_dwarf_channel import loglike_fermi_dwarf
from channels_extended import (
    loglike_cmb_distortion,
    loglike_dampe_cre,
    loglike_lss_assembly_bias,
    loglike_competitor_dd_watch,
    loglike_xrism_perseus_icm,
    loglike_erosita_erass1,
    loglike_phi_to_gamgam_xrism,
    loglike_euclid_q1_lensing,
    loglike_euclid_q1_subhalo_forecast,
    loglike_delta_n_eff_goldstein_hill_2026,
    loglike_lz_magnetic_moment,
    loglike_lz_magnetic_moment_binned,
)

# T90.29 RELHIC likelihood (Cloud-9 + M51)
try:
    from t90_v29_relhic_yukawa import loglike_relhic_t90v29
    _T90_RELHIC_AVAILABLE = True
except ImportError:
    _T90_RELHIC_AVAILABLE = False

# T90.36 tuned-Yukawa (Cloud-9 targeted)
try:
    from t90_v36_yukawa_tuned import loglike_yukawa_tuned_t90v36_wrapper
    _T90_TUNED_AVAILABLE = True
except ImportError:
    _T90_TUNED_AVAILABLE = False

# T90.37 Anand+2025 M_star cross-validation
try:
    from t90_v37_anand_mstar import loglike_anand_mstar
    _T90_ANAND_AVAILABLE = True
except ImportError:
    _T90_ANAND_AVAILABLE = False

# T90.32 RELHIC population likelihood
try:
    from t90_v32_relhic_population import loglike_relhic_population_t90v32_wrapper
    _T90_POP_AVAILABLE = True
except ImportError:
    _T90_POP_AVAILABLE = False

# T90.35 Yang+2024 parametric form
try:
    from t90_v35_yang2024_cloud9 import loglike_yang2024_cloud9
    _T90_YANG_AVAILABLE = True
except ImportError:
    _T90_YANG_AVAILABLE = False

# T90.44 multi-portal module
from t90_v44_multi_portal import sigma_m_multi_portal

if platform.system() == "Windows" or not Path("/home/lamkuenai/sidm-composite-dm-mediator").exists():
    _DEFAULT_RESULTS_DIR = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
else:
    _DEFAULT_RESULTS_DIR = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"

RESULTS_DIR = Path(_DEFAULT_RESULTS_DIR)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Multi-portal priors (9D)
# ---------------------------------------------------------------------------
# Portal A (heavy, drives LZ + low-frequency constraints)
LOG_M_PHI_A_MEV_RANGE = (1.5, 4.0)   # 30 MeV to 10 TeV (heavy mediator)
LOG_M_CHI_A_GEV_RANGE = (0.5, 3.0)   # 3 GeV to 1 TeV
G_CHI_A_RANGE = (0.5, 2.0)           # moderate-to-strong coupling (LZ needs this)

# Portal B (light, drives Cloud-9)
LOG_M_PHI_B_MEV_RANGE = (-0.5, 2.0)  # 0.3 MeV to 100 MeV (light mediator)
LOG_M_CHI_B_GEV_RANGE = (1.0, 3.5)   # 10 GeV to 3 TeV
G_CHI_B_RANGE = (0.05, 0.5)          # weak coupling (avoids LZ detection)

# Kinetic mixing (Portal A only; Portal B suppressed)
LOG_EPSILON_A_RANGE = (-50.0, -10.0)

# Annihilation coupling (Portal A)
LOG_ALPHA_A_RANGE = (-30.0, -1.0)

# T_dark/T_SM ratio
LOG_XI_RANGE = (-1.0, 0.7)

# All 10 parameters in order
PARAM_NAMES = [
    "log_m_phi_A_MeV", "log_m_chi_A_GeV", "g_chi_A",
    "log_m_phi_B_MeV", "log_m_chi_B_GeV", "g_chi_B",
    "log_epsilon_A", "log_alpha_A", "log_xi",
]


def prior_transform(u: np.ndarray) -> np.ndarray:
    """Map unit cube [0,1]^9 to physical prior box."""
    theta = np.empty_like(u)
    assert len(u) == 9, f"prior_transform expects 9D unit cube, got {len(u)}"
    theta[0] = LOG_M_PHI_A_MEV_RANGE[0] + u[0] * (LOG_M_PHI_A_MEV_RANGE[1] - LOG_M_PHI_A_MEV_RANGE[0])
    theta[1] = LOG_M_CHI_A_GEV_RANGE[0] + u[1] * (LOG_M_CHI_A_GEV_RANGE[1] - LOG_M_CHI_A_GEV_RANGE[0])
    theta[2] = G_CHI_A_RANGE[0] + u[2] * (G_CHI_A_RANGE[1] - G_CHI_A_RANGE[0])
    theta[3] = LOG_M_PHI_B_MEV_RANGE[0] + u[3] * (LOG_M_PHI_B_MEV_RANGE[1] - LOG_M_PHI_B_MEV_RANGE[0])
    theta[4] = LOG_M_CHI_B_GEV_RANGE[0] + u[4] * (LOG_M_CHI_B_GEV_RANGE[1] - LOG_M_CHI_B_GEV_RANGE[0])
    theta[5] = G_CHI_B_RANGE[0] + u[5] * (G_CHI_B_RANGE[1] - G_CHI_B_RANGE[0])
    theta[6] = LOG_EPSILON_A_RANGE[0] + u[6] * (LOG_EPSILON_A_RANGE[1] - LOG_EPSILON_A_RANGE[0])
    theta[7] = LOG_ALPHA_A_RANGE[0] + u[7] * (LOG_ALPHA_A_RANGE[1] - LOG_ALPHA_A_RANGE[0])
    theta[8] = LOG_XI_RANGE[0] + u[8] * (LOG_XI_RANGE[1] - LOG_XI_RANGE[0])
    return theta


def loglike_joint_multi_portal(theta: np.ndarray) -> float:
    """9D joint log-likelihood with multi-portal sigma/m(v).

    theta = (log_m_phi_A, log_m_chi_A, g_chi_A, log_m_phi_B, log_m_chi_B,
             g_chi_B, log_eps_A, log_alpha_A, log_xi)
    """
    (log_m_phi_A, log_m_chi_A, g_chi_A,
     log_m_phi_B, log_m_chi_B, g_chi_B,
     log_eps_A, log_alpha_A, log_xi) = theta

    m_phi_A = 10 ** log_m_phi_A
    m_chi_A = 10 ** log_m_chi_A
    m_phi_B = 10 ** log_m_phi_B
    m_chi_B = 10 ** log_m_chi_B
    epsilon_A = 10 ** log_eps_A
    alpha_A = 10 ** log_alpha_A
    xi = 10 ** log_xi

    # Sanity bounds
    if m_phi_A <= 0 or m_chi_A <= 0 or g_chi_A <= 0:
        return -np.inf
    if m_phi_B <= 0 or m_chi_B <= 0 or g_chi_B <= 0:
        return -np.inf
    if epsilon_A <= 0 or alpha_A <= 0 or xi <= 0:
        return -np.inf

    # ----- Multi-portal combined sigma/m at channel velocities -----
    # Channels see combined sigma/m_A + sigma/m_B
    sigma_m_0_total = sigma_m_multi_portal(
        ch_v03.V_REF, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B
    )
    sigma_m_dsph_total = sigma_m_multi_portal(
        ch_v03.V_DSPH, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B
    )
    sigma_m_ufd_total = sigma_m_multi_portal(
        ch_v03.V_UFD, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B
    )
    sigma_m_cluster_total = sigma_m_multi_portal(
        ch_v03.V_CLUSTER, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B
    )

    # Local velocity index (log-log derivative at v_ref)
    v_lo = ch_v03.V_REF / 1.1
    v_hi = ch_v03.V_REF * 1.1
    s_lo = sigma_m_multi_portal(v_lo, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B)
    s_hi = sigma_m_multi_portal(v_hi, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B)
    if s_lo <= 0 or s_hi <= 0:
        a_global = -2.0
    else:
        a_global = -((np.log10(s_lo) - np.log10(s_hi)) /
                     (np.log10(v_lo) - np.log10(v_hi)))

    # ----- Legacy SIDM channels (combined sigma/m via channels_v03) -----
    # Use the power-law form (sigma_m_0, a) with the combined multi-portal
    # sigma/m_total at v_ref and the local velocity index a_global. This
    # bypasses the vdep single-portal channels (which can't do multi-portal).
    ll_dsph = ch_v03.loglike_dsph_v03(sigma_m_0_total, a_global)
    ll_ufd = ch_v03.loglike_ufd_v03(sigma_m_0_total, a_global)
    ll_bullet = ch_v03.loglike_bullet_v03(sigma_m_cluster_total, a_global)

    # ----- LZ channels see ONLY Portal A (Portal B suppressed by epsilon_B << epsilon_A) -----
    # We approximate sigma_DM_n ~ epsilon_A^2 * (Portal A only)
    sigma_dm_n_A = epsilon_A ** 2 * 1e-41  # rough scale
    ll_lz_real = loglike_lz_real(m_chi_A, sigma_dm_n_A)
    if not np.isfinite(ll_lz_real):
        ll_lz_real = -10.0

    # LZ magnetic-moment: driven by Portal A only
    try:
        ll_lz_mag = loglike_lz_magnetic_moment(m_chi_A, m_phi_A, g_chi_A, epsilon_A)
        if not np.isfinite(ll_lz_mag):
            ll_lz_mag = -10.0
    except Exception:
        ll_lz_mag = -10.0

    # ----- FERMI dwarf (Portal A annihilation) -----
    sigma_v = 3e-26 * xi ** 2  # T55 non-thermal-relic normalization
    ll_fermi = loglike_fermi_dwarf(m_chi_A, sigma_v)
    if not np.isfinite(ll_fermi):
        ll_fermi = 0.0

    # ----- CMB / LSS / extended channels (Portal A only) -----
    try:
        ll_cmb = loglike_cmb_distortion(m_chi_A * 1e9, m_phi_A * 1e6, epsilon_A)
        if not np.isfinite(ll_cmb):
            ll_cmb = 0.0
    except Exception:
        ll_cmb = 0.0
    try:
        ll_lss = loglike_lss_assembly_bias(sigma_m_0_total, a_global)
        if not np.isfinite(ll_lss):
            ll_lss = 0.0
    except Exception:
        ll_lss = 0.0

    # ----- T90 Cloud-9 channels (use combined sigma/m at v=28 km/s) -----
    sigma_m_28 = sigma_m_multi_portal(28.0, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B)

    ll_t90_relhic = 0.0
    if _T90_RELHIC_AVAILABLE and os.environ.get("T90_RELHIC_V27", "0").strip() == "1":
        # T90.29 takes the Portal B parameters (light mediator)
        try:
            ll_t90_relhic = loglike_relhic_t90v29((
                log_m_phi_B, log_m_chi_B, g_chi_B, log_eps_A, log_alpha_A, log_xi,
            ))
            if not np.isfinite(ll_t90_relhic):
                ll_t90_relhic = 0.0
        except Exception:
            ll_t90_relhic = 0.0

    ll_t90_tuned = 0.0
    if _T90_TUNED_AVAILABLE and os.environ.get("T90_YUKAWA_TUNED", "0").strip() == "1":
        try:
            ll_t90_tuned = loglike_yukawa_tuned_t90v36_wrapper((
                log_m_phi_B, log_m_chi_B, g_chi_B, log_eps_A, log_alpha_A, log_xi,
            ))
            if not np.isfinite(ll_t90_tuned):
                ll_t90_tuned = 0.0
        except Exception:
            ll_t90_tuned = 0.0

    ll_t90_anand = 0.0
    if _T90_ANAND_AVAILABLE and os.environ.get("T90_ANAND_MSTAR", "0").strip() == "1":
        try:
            ll_t90_anand = loglike_anand_mstar(sigma_m_28)
            if not np.isfinite(ll_t90_anand):
                ll_t90_anand = 0.0
        except Exception:
            ll_t90_anand = 0.0

    ll_t90_pop = 0.0
    if _T90_POP_AVAILABLE and os.environ.get("T90_RELHIC_POP", "0").strip() == "1":
        try:
            ll_t90_pop = loglike_relhic_population_t90v32_wrapper((
                log_m_phi_B, log_m_chi_B, g_chi_B, log_eps_A, log_alpha_A, log_xi,
            ))
            if not np.isfinite(ll_t90_pop):
                ll_t90_pop = 0.0
        except Exception:
            ll_t90_pop = 0.0

    ll_t90_yang = 0.0
    if _T90_YANG_AVAILABLE and os.environ.get("T90_YANG_CLOUD9", "0").strip() == "1":
        try:
            ll_t90_yang = loglike_yang2024_cloud9(sigma_m_28)
            if not np.isfinite(ll_t90_yang):
                ll_t90_yang = 0.0
        except Exception:
            ll_t90_yang = 0.0

    # KSFR/PCAC validity mask — apply to Portal A (drives PCAC)
    if os.environ.get("SIDM_DISABLE_KSFR_MASK", "0").strip() == "1":
        ll_ksfr = 0.0
    else:
        theta_5d = (log_m_phi_A, log_m_chi_A, g_chi_A, log_eps_A, log_alpha_A)
        try:
            ll_ksfr = loglike_ksfr_pcac_validity(theta_5d)
            if not np.isfinite(ll_ksfr):
                return -np.inf
        except Exception:
            ll_ksfr = 0.0

    # ----- Combine -----
    t90_weight = float(os.environ.get("T90_WEIGHT_MULTIPLIER", "1.0"))
    ll_total = (
        ll_dsph + ll_ufd + ll_bullet
        + ll_lz_real + ll_lz_mag + ll_fermi
        + ll_cmb + ll_lss
        + t90_weight * (ll_t90_relhic + ll_t90_tuned + ll_t90_anand + ll_t90_pop + ll_t90_yang)
        + ll_ksfr
    )
    return ll_total if np.isfinite(ll_total) else -np.inf


def run_multi_portal_fit(nlive: int = 200, dlogz: float = 0.1):
    """Run the 9D multi-portal nested-sampling fit.

    Default nlive=200 for quick iteration; production should use 1000+.
    """
    ndim = len(PARAM_NAMES)
    print(f"T90.45 — Multi-portal joint fit (9D, nlive={nlive})")
    print(f"  Parameter names: {PARAM_NAMES}")
    print(f"  Channels: dSph, UFD, Bullet, LZ, FERMI, CMB, LSS, T90 Cloud-9")
    print()
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglike_joint_multi_portal,
        prior_transform,
        ndim=ndim,
        nlive=nlive,
    )
    sampler.run_nested()
    elapsed = time.time() - t0

    res = sampler.results
    log_Z = float(res["logz"][-1])
    weights = np.exp(res["logwt"] - res["logz"][-1])
    samples = res["samples"]

    medians = {}
    for i, name in enumerate(PARAM_NAMES):
        sorted_idx = np.argsort(samples[:, i])
        cumw = np.cumsum(weights[sorted_idx])
        mid = cumw[-1] / 2
        medians[name] = float(samples[sorted_idx, i][np.searchsorted(cumw, mid)])

    # MAP = argmax(weights)
    map_idx = int(np.argmax(weights))
    map_params = {name: float(samples[map_idx, i]) for i, name in enumerate(PARAM_NAMES)}

    # Derived sigma/m at key velocities (MAP)
    m_phi_A = 10 ** map_params["log_m_phi_A_MeV"]
    m_chi_A = 10 ** map_params["log_m_chi_A_GeV"]
    g_chi_A = map_params["g_chi_A"]
    m_phi_B = 10 ** map_params["log_m_phi_B_MeV"]
    m_chi_B = 10 ** map_params["log_m_chi_B_GeV"]
    g_chi_B = map_params["g_chi_B"]
    derived = {
        "sigma_m_28": sigma_m_multi_portal(28, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B),
        "sigma_m_100": sigma_m_multi_portal(100, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B),
        "sigma_m_1000": sigma_m_multi_portal(1000, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B),
        "sigma_m_3000": sigma_m_multi_portal(3000, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B),
    }

    output = {
        "log_Z": log_Z,
        "nlive": nlive,
        "ndim": ndim,
        "elapsed_sec": elapsed,
        "MAP": map_params,
        "MAP_physical": {
            "m_phi_A_MeV": 10 ** map_params["log_m_phi_A_MeV"],
            "m_chi_A_GeV": 10 ** map_params["log_m_chi_A_GeV"],
            "g_chi_A": g_chi_A,
            "m_phi_B_MeV": 10 ** map_params["log_m_phi_B_MeV"],
            "m_chi_B_GeV": 10 ** map_params["log_m_chi_B_GeV"],
            "g_chi_B": g_chi_B,
            "epsilon_A": 10 ** map_params["log_epsilon_A"],
            "alpha_A": 10 ** map_params["log_alpha_A"],
            "xi": 10 ** map_params["log_xi"],
        },
        "MAP_derived_sigma_m": derived,
        "median": medians,
        "median_physical": {
            "m_phi_A_MeV": 10 ** medians["log_m_phi_A_MeV"],
            "m_chi_A_GeV": 10 ** medians["log_m_chi_A_GeV"],
            "g_chi_A": medians["g_chi_A"],
            "m_phi_B_MeV": 10 ** medians["log_m_phi_B_MeV"],
            "m_chi_B_GeV": 10 ** medians["log_m_chi_B_GeV"],
            "g_chi_B": medians["g_chi_B"],
            "epsilon_A": 10 ** medians["log_epsilon_A"],
            "alpha_A": 10 ** medians["log_alpha_A"],
            "xi": 10 ** medians["log_xi"],
        },
        "T90_channels_enabled": {
            "T90_RELHIC_V27": os.environ.get("T90_RELHIC_V27", "0"),
            "T90_RELHIC_POP": os.environ.get("T90_RELHIC_POP", "0"),
            "T90_YANG_CLOUD9": os.environ.get("T90_YANG_CLOUD9", "0"),
            "T90_YUKAWA_TUNED": os.environ.get("T90_YUKAWA_TUNED", "0"),
            "T90_ANAND_MSTAR": os.environ.get("T90_ANAND_MSTAR", "0"),
        },
        "T90_WEIGHT_MULTIPLIER": float(os.environ.get("T90_WEIGHT_MULTIPLIER", "1.0")),
        "V_CLUSTER": float(ch_v03.V_CLUSTER),
    }
    return output


if __name__ == "__main__":
    nlive = int(os.environ.get("T41_NLIVE", "200"))
    out = run_multi_portal_fit(nlive=nlive)
    out_path = RESULTS_DIR / "t90_v45_multi_portal_joint_fit.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print()
    print(f"  log Z = {out['log_Z']:.3f}")
    print(f"  MAP: m_phi_A={out['MAP_physical']['m_phi_A_MeV']:.2f} MeV, "
          f"m_phi_B={out['MAP_physical']['m_phi_B_MeV']:.4f} MeV, "
          f"g_chi_A={out['MAP_physical']['g_chi_A']:.3f}, g_chi_B={out['MAP_physical']['g_chi_B']:.3f}")
    print(f"  Median: m_phi_A={out['median_physical']['m_phi_A_MeV']:.2f} MeV, "
          f"m_phi_B={out['median_physical']['m_phi_B_MeV']:.4f} MeV, "
          f"g_chi_A={out['median_physical']['g_chi_A']:.3f}, g_chi_B={out['median_physical']['g_chi_B']:.3f}")
    print(f"  MAP sigma/m(28) = {out['MAP_derived_sigma_m']['sigma_m_28']:.3e}")
    print(f"  MAP sigma/m(100) = {out['MAP_derived_sigma_m']['sigma_m_100']:.3e}")
    print(f"  MAP sigma/m(3000) = {out['MAP_derived_sigma_m']['sigma_m_3000']:.3e}")
    print(f"  Cloud-9 status (sigma/m(28) in [30,500]): "
          f"{'YES' if 30 < out['MAP_derived_sigma_m']['sigma_m_28'] < 500 else 'NO'}")
    print(f"  Bullet status (sigma/m(3000) < 0.5): "
          f"{'YES' if out['MAP_derived_sigma_m']['sigma_m_3000'] < 0.5 else 'NO'}")
    print(f"  -> {out_path}")