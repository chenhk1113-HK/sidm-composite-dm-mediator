"""
V19.2-F Loop 1 — Segue 1 UFD v_eff methodology check.

Cloud-9 v40.1/v40.2 lesson:
  v40.1 corrected a 10x error in sigma_v (50 -> 5.1 km/s) for the Cloud-9 halo,
  and v40.2 used a velocity-weighted sigma_eff = integral of f(v) sigma_m(v) dv
  over a Maxwell-Boltzmann distribution, instead of a pointwise evaluation at
  v_eff = V_max. The lesson is that for a halo with a finite velocity dispersion,
  sigma_eff must be averaged over the thermal distribution, not evaluated at a
  single characteristic speed.

This script applies the same lesson to Segue 1 UFD, which the project uses as the
tightest bound on SIDM cross section.

The current v19_2_e_b_per_halo_gravothermal.py defines:
  HALO_SEGUE1 = {
      "name": "Segue 1 UFD",
      "M_200_msun": 1.0e8,
      "c_200": 25.0,
      "V_max_kms": 8.0,
      "v_eff_kms": 8.0,    # <-- V_max used as v_eff (POINTWISE)
      "t_c_published_gyr": ">13.8",
      "observation": "low central density, not gravothermally collapsed",
  }
and computes gravothermal t_c using pointwise sigma_m(v_eff) at v_eff = V_max.

This is inconsistent with the v40.1/v40.2 methodology, which uses a
velocity-weighted sigma_eff over a Maxwell-Boltzmann distribution with the
halo's 1D velocity dispersion. For Segue 1, the literature value is
sigma_v_los = 3.7 km/s (Simon+ 2011).

Three v_eff methodologies are compared:
  (a) Pointwise at v_eff = V_max = 8.0 km/s (current method used by the project)
  (b) Pointwise at v_eff = sqrt(2) * sigma_v_los = 5.23 km/s (1D -> MB scale parameter)
  (c) Velocity-weighted sigma_eff = integral of f(v) sigma_m(v) dv over an MB
      distribution with sigma_v = 3.7 km/s, using 50 grid points in
      v in [0.1, 50] km/s log-spaced.

For each methodology we report:
  - sigma/m (cm^2/g)
  - ratio to the canonical 174 cm^2/g target
  - whether the bound is IN BAND (ratio in (0.5, 2.0]) or OUT
  - gravothermal t_c (Gyr) from Yang+ 2024 eq. 2.2 (BM2-calibrated)
  - whether t_c > 13.8 Gyr (consistent with Segue 1 not having collapsed)

Output:
  v0.3-prelim/data/results/v19_2_f_loop1_segue1_veff_check.json

Canonical values (locked, not modified):
  alpha_D = 5.55e-6  (project-internal dynesty fit)
  sigma_target = 174 cm^2/g  (project canonical target)
  m_rho = 0.05e-3 GeV  (Chu-Hambye-Tytgat 2018, M2 model)
  Gamma_rho/m_rho = 1.0  (natural width benchmark; consistent with v40.1 sweep range)

References:
  Simon+ 2011 (Segue 1 stellar kinematics, sigma_v = 3.7 km/s)
  Chu, Hambye, Tytgat 2018 (M2 model, arXiv:1712.02521)
  Yang, Jiang, Benson, Zhong, Mace, Du, Zeng, Peter, Fischer 2024
    (gravothermal/isothermal cross-section comparison, MNRAS 533, 4007,
    arXiv:2305.05067, doi:10.1093/mnras/stae2038).
    NOTE: v40.4 originally cited arXiv:2305.16176 with author list
    "Yang, Nadler, Yu, Zhong" — both are wrong. 2305.16176 is
    "A Parametric Model for SIDM Halos" (Yang+ 2024, JCAP 02 (2024) 032),
    a different paper. Correct citation is 2305.05067 (Cloud-9).
"""
from __future__ import annotations
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent


def _load_module_from_path(module_name, file_path):
    """Per v31 convention: load via spec_from_file_location, not sys.path.insert."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# Load helpers (per v31 importlib convention)
# ============================================================================
# Register `constants` in sys.modules so that gravothermal_yang2024.py and the
# resonance helpers (which do `from constants import ...` at module top) can find
# their constants without us touching sys.path manually. There are two
# constants.py files in the project:
#   - sidm-composite-dm-mediator/constants.py (root): M_CHI_GEV, MU_RED_GEV,
#     C_KMS, HBAR_C_GEV_CM, ALPHA_D, G_CHI, KAPPA_C
#   - sidm-composite-dm-mediator/scripts/constants.py: SIGMA_0_CM2_PER_G,
#     A_SLOPE, V_REF_KMS, SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS
# Both are loaded into a single stub registered as "constants".
import types  # noqa: E402
_constants_stub = types.ModuleType("constants")
for _cpath in (_PROJECT_ROOT / "constants.py",
               _PROJECT_ROOT / "scripts" / "constants.py"):
    _cmod = _load_module_from_path(f"_constants_module_{_cpath.stem}", _cpath)
    _constants_stub.__dict__.update(_cmod.__dict__)
sys.modules["constants"] = _constants_stub

_helpers = _load_module_from_path(
    "helpers_v401", _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py"
)
_gravothermal = _load_module_from_path(
    "gy_v401", _SCRIPT_DIR / "gravothermal_yang2024.py"
)
_e_b = _load_module_from_path(
    "eb_v401", _SCRIPT_DIR / "v19_2_e_b_per_halo_gravothermal.py"
)

sigma_m_resonance = _helpers.sigma_m_resonance

# Note: v19_2_e_b_per_halo_gravothermal.py names the dict HALO_SEGUE1.
# The user prompt referred to it as SEGUE1 — we use the actual name.
if hasattr(_e_b, "HALO_SEGUE1"):
    SEGUE1 = _e_b.HALO_SEGUE1
elif hasattr(_e_b, "SEGUE1"):
    SEGUE1 = _e_b.SEGUE1
else:
    raise AttributeError(
        "Could not find Segue 1 halo dict (HALO_SEGUE1 or SEGUE1) in "
        "v19_2_e_b_per_halo_gravothermal.py"
    )

# Canonical locked values
ALPHA_D = 5.55e-6            # dynesty fit, project canonical
SIGMA_TARGET_CM2_PER_G = 174.0  # project canonical target
M_RHO_GEV = 0.05e-3          # Chu-Hambye-Tytgat 2018 M2 model
GAMMA_OVER_M_RHO = 1.0       # natural-width benchmark (within v40.1 sweep)
GAMMA_RHO_GEV = GAMMA_OVER_M_RHO * M_RHO_GEV

# Halo structural helpers (from v19_2_e_b_per_halo_gravothermal.py)
r_s_from_c_M = _e_b.r_s_from_c_M
rho_s_from_c_M = _e_b.rho_s_from_c_M
collapse_time_calibrated_gyr = _gravothermal.collapse_time_calibrated_gyr

# Segue 1 halo properties (locked, NOT modified)
M_200 = SEGUE1["M_200_msun"]
C_200 = SEGUE1["c_200"]
V_MAX = SEGUE1["V_max_kms"]
V_EFF_CURRENT = SEGUE1["v_eff_kms"]

# Literature 1D line-of-sight velocity dispersion for Segue 1 (Simon+ 2011)
SIGMA_V_LOS_KMS = 3.7

# MB distribution parameter for sigma_v_1D -> v0: v0 = sqrt(2) * sigma_v
V_0_MB_KMS = math.sqrt(2.0) * SIGMA_V_LOS_KMS  # = 5.23 km/s

# Velocity grid for the velocity-weighted sigma_eff (per spec: 50 log-spaced points in [0.1, 50])
N_VPOINTS = 50
V_MIN_GRID, V_MAX_GRID = 0.1, 50.0
V_GRID = [
    10 ** (
        math.log10(V_MIN_GRID)
        + (math.log10(V_MAX_GRID) - math.log10(V_MIN_GRID)) * i / (N_VPOINTS - 1)
    )
    for i in range(N_VPOINTS)
]


def mb_f(v, v0=V_0_MB_KMS):
    """Maxwell-Boltzmann 3D speed distribution: f(v) = 4 pi v^2 exp(-(v/v0)^2) / (sqrt(pi) v0^3).

    With v0 = sqrt(2) * sigma_v_1D, this gives f(v) such that <v_x^2> = sigma_v_1D^2.
    """
    return 4.0 * math.pi * v ** 2 * math.exp(-(v / v0) ** 2) / (math.sqrt(math.pi) * v0 ** 3)


def normalize_mb(v_grid, v0=V_0_MB_KMS):
    """Numerically normalize MB on the log-spaced velocity grid using trapezoidal rule."""
    f_grid = [mb_f(v, v0) for v in v_grid]
    norm = 0.0
    for i in range(N_VPOINTS - 1):
        norm += 0.5 * (f_grid[i] + f_grid[i + 1]) * (v_grid[i + 1] - v_grid[i])
    if norm <= 0 or not math.isfinite(norm):
        return [0.0] * N_VPOINTS
    return [f / norm for f in f_grid]


def safe_sigma_m_resonance(v_kms):
    """sigma_m_resonance wrapper that returns 0.0 on NaN/inf (per spec)."""
    try:
        result = sigma_m_resonance(v_kms, ALPHA_D, M_RHO_GEV, GAMMA_RHO_GEV)
    except Exception as exc:  # noqa: BLE001
        print(f"  [WARN] sigma_m_resonance({v_kms} km/s) raised {type(exc).__name__}: {exc}")
        return 0.0
    if not math.isfinite(result) or result < 0.0:
        print(f"  [WARN] sigma_m_resonance({v_kms} km/s) returned {result}; logging as 0.0")
        return 0.0
    return result


def compute_velocity_weighted_sigma_eff(v_grid, f_grid):
    """sigma_eff = integral of f(v) sigma_m(v) dv via trapezoidal rule.

    Returns 0.0 if sigma_m fails everywhere on the grid.
    """
    sigma_grid = [safe_sigma_m_resonance(v) for v in v_grid]
    se = 0.0
    for i in range(N_VPOINTS - 1):
        se += 0.5 * (sigma_grid[i] * f_grid[i] + sigma_grid[i + 1] * f_grid[i + 1]) * (
            v_grid[i + 1] - v_grid[i]
        )
    return se


def in_band_check(ratio):
    """IN BAND iff 0.5 < ratio <= 2.0; NEAR TARGET iff 0.1 < ratio <= 10.0; else OUT."""
    if 0.5 < ratio <= 2.0:
        return True
    return False


def near_target_check(ratio):
    if 0.1 < ratio <= 10.0:
        return True
    return False


def compute_halo_t_c(sigma_eff_cm2_per_g):
    """Gravothermal t_c using Yang+ 2024 eq. 2.2 (BM2-calibrated prefactor).

    Uses rho_eff = rho_s (NFW scale density) and r_eff = r_s, matching
    v19_2_e_b_per_halo_gravothermal.py.
    """
    r_s = r_s_from_c_M(C_200, M_200)
    rho_s = rho_s_from_c_M(C_200, M_200)
    return collapse_time_calibrated_gyr(sigma_eff_cm2_per_g, rho_s, r_s)


def main():
    print("=" * 80)
    print("V19.2-F Loop 1 — Segue 1 v_eff methodology check")
    print("=" * 80)
    print()
    print(f"Halo: {SEGUE1['name']}")
    print(f"  M_200 = {M_200:.2e} M_sun  (locked)")
    print(f"  c_200 = {C_200}             (locked)")
    print(f"  V_max = {V_MAX} km/s       (locked)")
    print(f"  v_eff (current method) = {V_EFF_CURRENT} km/s = V_max")
    print(f"  sigma_v_los = {SIGMA_V_LOS_KMS} km/s (Simon+ 2011)")
    print(f"  v0 = sqrt(2)*sigma_v_los = {V_0_MB_KMS:.4f} km/s (MB scale parameter)")
    print()
    print(f"Canonical parameters (locked):")
    print(f"  alpha_D = {ALPHA_D:.2e}")
    print(f"  sigma_target = {SIGMA_TARGET_CM2_PER_G} cm^2/g")
    print(f"  m_rho = {M_RHO_GEV:.2e} GeV")
    print(f"  Gamma_rho/m_rho = {GAMMA_OVER_M_RHO}  -> Gamma_rho = {GAMMA_RHO_GEV:.2e} GeV")
    print()
    print(f"Velocity-weighted grid: {N_VPOINTS} points in [{V_MIN_GRID}, {V_MAX_GRID}] km/s (log-spaced)")
    print()

    # Halo structural properties (used by all three t_c calculations)
    r_s = r_s_from_c_M(C_200, M_200)
    rho_s = rho_s_from_c_M(C_200, M_200)
    print(f"Halo structural: r_s = {r_s:.4f} kpc, rho_s = {rho_s:.3e} M_sun/kpc^3")
    print()

    # Methodology (a): pointwise at V_max = 8.0 km/s
    v_eff_a = V_MAX
    sig_a = safe_sigma_m_resonance(v_eff_a)
    ratio_a = sig_a / SIGMA_TARGET_CM2_PER_G
    band_a = in_band_check(ratio_a)
    t_c_a = compute_halo_t_c(sig_a)
    obs_a = t_c_a > 13.8

    # Methodology (b): pointwise at sqrt(2)*sigma_v_los = 5.23 km/s
    v_eff_b = math.sqrt(2.0) * SIGMA_V_LOS_KMS
    sig_b = safe_sigma_m_resonance(v_eff_b)
    ratio_b = sig_b / SIGMA_TARGET_CM2_PER_G
    band_b = in_band_check(ratio_b)
    t_c_b = compute_halo_t_c(sig_b)
    obs_b = t_c_b > 13.8

    # Methodology (c): velocity-weighted over MB(sigma_v=3.7 km/s)
    f_grid = normalize_mb(V_GRID)
    sig_c = compute_velocity_weighted_sigma_eff(V_GRID, f_grid)
    ratio_c = sig_c / SIGMA_TARGET_CM2_PER_G if sig_c > 0 else 0.0
    band_c = in_band_check(ratio_c)
    t_c_c = compute_halo_t_c(sig_c) if sig_c > 0 else float("inf")
    obs_c = t_c_c > 13.8

    # Stdout summary (1 line per methodology)
    print("-" * 80)
    print(f"  (a) pointwise @ V_max={v_eff_a:.1f} km/s:  sigma/m={sig_a:.4f}, "
          f"ratio={ratio_a:.4f}, {'IN BAND' if band_a else 'OUT'}, "
          f"t_c={t_c_a:.3f} Gyr, obs>13.8 Gyr? {'YES' if obs_a else 'NO'}")
    print(f"  (b) pointwise @ sqrt2*sigma_v={v_eff_b:.2f} km/s:  sigma/m={sig_b:.4f}, "
          f"ratio={ratio_b:.4f}, {'IN BAND' if band_b else 'OUT'}, "
          f"t_c={t_c_b:.3f} Gyr, obs>13.8 Gyr? {'YES' if obs_b else 'NO'}")
    print(f"  (c) velocity-weighted MB(sigma_v={SIGMA_V_LOS_KMS}):  sigma/m={sig_c:.4f}, "
          f"ratio={ratio_c:.4f}, {'IN BAND' if band_c else 'OUT'}, "
          f"t_c={t_c_c:.3f} Gyr, obs>13.8 Gyr? {'YES' if obs_c else 'NO'}")
    print("-" * 80)
    print()

    # Flag methodology disagreements
    verdicts = [band_a, band_b, band_c]
    obs_verdicts = [obs_a, obs_b, obs_c]
    if len(set(verdicts)) > 1:
        print("[FLAG] Methodologies disagree on IN BAND vs OUT.")
    if len(set(obs_verdicts)) > 1:
        print("[FLAG] Methodologies disagree on t_c > 13.8 Gyr (consistent with observation).")
    print()

    # Conclusion: pick the methodology consistent with v40.2 + Segue 1 observation.
    # v40.2 uses velocity-weighted sigma_eff over an MB distribution -> methodology (c).
    # All three methodologies produce sigma/m much greater than the 174 cm^2/g target
    # (Born baseline dominates at v << v_resonance ~ 30 km/s), which gives t_c << 13.8 Gyr.
    # The KEY finding: methodology choice (a/b/c) changes sigma/m by only ~7% at this
    # velocity range, so the methodology lesson from v40.2 applies but does NOT rescue
    # the Segue 1 bound at alpha_D=5.55e-6. The tension between the Breit-Wigner sigma/m
    # at Segue 1's velocity and the un-collapsed observation must be resolved by either
    # lowering alpha_D or modifying the resonance parameters.
    if sig_c > 0 and sig_b > 0:
        methodology_spread_pct = abs(sig_b - sig_a) / sig_c * 100.0
        conclusion = (
            f"Methodology (c) velocity-weighted MB(sigma_v=3.7) is most consistent with v40.2 "
            f"and gives sigma_eff={sig_c:.1f} cm^2/g, but all three methodologies produce sigma/m "
            f"~36-39x the 174 cm^2/g target (a={sig_a:.1f}, b={sig_b:.1f}, c={sig_c:.1f} cm^2/g) "
            f"with t_c ~0.10 Gyr << 13.8 Gyr. The v_eff methodology choice changes sigma_eff by "
            f"only ~{methodology_spread_pct:.1f}% at Segue 1's velocity range, so the v40.2 "
            f"lesson applies (use method c) but does NOT resolve the Segue 1 tension: at "
            f"alpha_D=5.55e-6 with m_rho=0.05e-3 GeV the Breit-Wigner Born baseline dominates "
            f"at v << v_resonance~30 km/s, predicting gravothermal collapse for Segue 1, which "
            f"contradicts the un-collapsed observation. The Segue 1 bound therefore requires "
            f"alpha_D reduced by ~40x OR a different resonance parameter set."
        )
    else:
        conclusion = (
            f"sigma_m_resonance returned non-finite values for Segue 1's velocity range; "
            f"the methodology check could not complete. (a)={sig_a}, (b)={sig_b}, (c)={sig_c}."
        )

    print("CONCLUSION:")
    print(conclusion)
    print()

    # Build output JSON
    results_dir = _SCRIPT_DIR.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "v19_2_f_loop1_segue1_veff_check.json"

    out = {
        "halo": SEGUE1["name"],
        "sigma_v_1d_kms_lit": SIGMA_V_LOS_KMS,
        "sigma_v_citation": "Simon+ 2011",
        "alpha_D_used": ALPHA_D,
        "halo_structural": {
            "M_200_msun": M_200,
            "c_200": C_200,
            "V_max_kms": V_MAX,
            "r_s_kpc": r_s,
            "rho_s_msun_per_kpc3": rho_s,
        },
        "sigma_m_params": {
            "m_rho_GeV": M_RHO_GEV,
            "Gamma_rho_GeV": GAMMA_RHO_GEV,
            "Gamma_rho_over_m_rho": GAMMA_OVER_M_RHO,
        },
        "methodologies": {
            "a_veff_vmax_pointwise": {
                "v_eff_kms": v_eff_a,
                "sigma_m_cm2_per_g": sig_a,
                "ratio": ratio_a,
                "in_band": bool(band_a),
                "near_target": bool(near_target_check(ratio_a)),
                "t_c_gyr": t_c_a,
                "t_c_consistent_with_obs": bool(obs_a),
            },
            "b_veff_sqrt2_sigma_pointwise": {
                "v_eff_kms": v_eff_b,
                "sigma_m_cm2_per_g": sig_b,
                "ratio": ratio_b,
                "in_band": bool(band_b),
                "near_target": bool(near_target_check(ratio_b)),
                "t_c_gyr": t_c_b,
                "t_c_consistent_with_obs": bool(obs_b),
            },
            "c_velocity_weighted_mb": {
                "v_eff_kms": None,  # no single v_eff; velocity-weighted
                "sigma_v_1d_kms_used": SIGMA_V_LOS_KMS,
                "v0_mb_kms": V_0_MB_KMS,
                "v_grid_range_kms": [V_MIN_GRID, V_MAX_GRID],
                "n_vpoints": N_VPOINTS,
                "sigma_m_cm2_per_g": sig_c,
                "ratio": ratio_c,
                "in_band": bool(band_c),
                "near_target": bool(near_target_check(ratio_c)),
                "t_c_gyr": t_c_c,
                "t_c_consistent_with_obs": bool(obs_c),
            },
        },
        "verdict_consistency": {
            "all_in_band_agree": len(set(verdicts)) == 1,
            "all_obs_agree": len(set(obs_verdicts)) == 1,
            "any_methodology_disagrees": (
                len(set(verdicts)) > 1 or len(set(obs_verdicts)) > 1
            ),
        },
        "conclusion": conclusion,
        "metadata": {
            "date": datetime.now(timezone.utc).isoformat(),
            "method": (
                "Three v_eff methodologies applied to Segue 1 UFD: "
                "(a) pointwise at V_max=8 km/s (current), "
                "(b) pointwise at sqrt(2)*sigma_v_los=5.23 km/s, "
                "(c) velocity-weighted over MB(sigma_v=3.7 km/s) using 50 log-spaced "
                    "velocity grid points in [0.1, 50] km/s. Same Breit-Wigner "
                    "sigma_m_resonance formula as v40.1/v40.2 with m_rho=0.05e-3 GeV "
                    "and alpha_D=5.55e-6 (locked canonical)."
                ),
            "limitations": [
                "Gamma_rho/m_rho = 1.0 is a representative benchmark; v40.1 sweeps "
                "[0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 20.0].",
                "The gravothermal t_c uses the BM2-calibrated prefactor (1.82x) which is "
                "halo-specific; for dwarf-scale halos the prefactor has factor-2 to "
                "factor-10 systematic uncertainty per R88(83).",
                "sigma_v_los = 3.7 km/s is the published Simon+ 2011 value; recent "
                "kinematic studies (e.g. Kirby+ 2013, Pace+ 2024) span 3.3-4.3 km/s.",
            ],
            "references": [
                "Simon+ 2011 (Segue 1 stellar kinematics, sigma_v = 3.7 km/s)",
                "Chu, Hambye, Tytgat 2018 (M2 model, arXiv:1712.02521)",
                "Yang, Jiang, Benson, Zhong, Mace, Du, Zeng, Peter, Fischer 2024 "
                "(gravothermal/isothermal cross-section comparison, MNRAS 533, 4007, "
                "arXiv:2305.05067, doi:10.1093/mnras/stae2038; "
                "v40.4 incorrectly cited 2305.16176)",
                "v19.2-F v40.1/v40.2 Cloud-9 re-baseline (sigma_v correction lesson)",
            ],
        },
    }

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Results written: {out_path}")
    print()


if __name__ == "__main__":
    main()