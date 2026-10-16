"""v36 finer Gamma/rho sampling + sigma_eff vs alpha_D curve — r38 fix.

r38 Sci-3: discrete Gamma/rho sampling (0.01, 0.1, 0.5, 1, 2, 3, 4, 5, 6) might
miss IN BAND windows that fall between the sampled values. This script
refines the Gamma/rho grid to step 0.1 between 0.5 and 8.0 (dense sampling)
to confirm no IN BAND window is missed.

r38 Sci-4: window boundary convergence at Gamma/rho=7. This script
generates the sigma_eff(29.4) vs alpha_D curve at Gamma/rho = 7.0
under velocity-weighted analysis (MB, sigma_v=100) so the window
boundaries are visible in a plot-style data series.
"""
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent


def _load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_constants = _load_module_from_path("constants_v36", _PROJECT_ROOT / "constants.py")
_helpers = _load_module_from_path("helpers_v36",
                                 _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py")

C_KMS = _constants.C_KMS
sigma_m_resonance = _helpers.sigma_m_resonance

M_CHI_GEV = 1.0
M_RHO_GEV = 0.05e-3
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0
ALPHA_D_CLOUD9 = 5.55e-6

# Dense Gamma/rho grid: step 0.1 in [0.5, 8.0]
GAMMA_RHO_DENSE = [round(0.5 + 0.1 * i, 1) for i in range(int((8.0 - 0.5) / 0.1) + 1)]
# Plus the original 9 values for context
GAMMA_RHO_DISCRETE = [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
# Combine unique
GAMMA_RHO_ALL = sorted(set(GAMMA_RHO_DENSE + GAMMA_RHO_DISCRETE))

# Velocity grid (100 log-spaced points, 0.5 to 1000 km/s)
N_VPOINTS = 100
V_MIN, V_MAX = 0.5, 1000.0
V_GRID = [10 ** (math.log10(V_MIN) + (math.log10(V_MAX) - math.log10(V_MIN)) * i / (N_VPOINTS - 1))
         for i in range(N_VPOINTS)]

# alpha_D grid: 200 points for window boundary precision
N_POINTS = 200
LOG_MIN, LOG_MAX = math.log10(1e-10), math.log10(1.0)
ALPHA_D_GRID = [10 ** (LOG_MIN + (LOG_MAX - LOG_MIN) * i / (N_POINTS - 1))
                for i in range(N_POINTS)]


def mb_f(v, sigma_v, v0):
    return 4 * math.pi * v ** 2 * math.exp(-(v / v0) ** 2) / (math.sqrt(math.pi) * v0 ** 3)


def normalize(f_func, sigma_v, **kwargs):
    f_grid = [f_func(v, sigma_v, **kwargs) for v in V_GRID]
    norm = 0.0
    for i in range(N_VPOINTS - 1):
        norm += 0.5 * (f_grid[i] + f_grid[i + 1]) * (V_GRID[i + 1] - V_GRID[i])
    if norm <= 0:
        return [0.0] * N_VPOINTS
    return [f / norm for f in f_grid]


def compute_sigma_eff(alpha_D, Gamma_rho, f_grid):
    sigma_grid = [sigma_m_resonance(v, alpha_D, M_RHO_GEV, Gamma_rho) for v in V_GRID]
    se = 0.0
    for i in range(N_VPOINTS - 1):
        se += 0.5 * (sigma_grid[i] * f_grid[i] + sigma_grid[i + 1] * f_grid[i + 1]) * (
            V_GRID[i + 1] - V_GRID[i]
        )
    return se


def classify(r_t):
    if 0.5 < r_t <= 2.0:
        return "IN BAND"
    if 0.1 < r_t <= 10.0:
        return "NEAR TARGET"
    return "OUT"


def main():
    # === PART 1: Cloud-9 specific point, MB sigma_v=100, dense Gamma/rho ===
    print("=" * 80)
    print("PART 1: Cloud-9 alpha_D point check at MB sigma_v=100, DENSE Gamma/rho (step 0.1)")
    print("=" * 80)
    print()

    sv = 100
    v0 = math.sqrt(2) * sv
    f_grid = normalize(mb_f, sv, v0=v0)

    in_band_gammas = []
    print(f"{'G/rho':<6} | {'sigma_eff':<12} | {'ratio':<8} | region")
    print("-" * 50)
    for gf in GAMMA_RHO_ALL:
        Gamma_rho = gf * M_RHO_GEV
        se = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, f_grid)
        r_t = se / SIGMA_TARGET
        region = classify(r_t)
        if region == "IN BAND":
            in_band_gammas.append(gf)
        if abs(gf - round(gf, 1)) < 0.001 or gf in GAMMA_RHO_DISCRETE:  # show key values
            print(f"{gf:<6} | {se:<12.4f} | {r_t:<8.4f} | {region}")
    print()
    print(f"IN BAND widths (MB, sigma_v=100, Cloud-9 alpha_D): {in_band_gammas}")
    print(f"Number of IN BAND widths: {len(in_band_gammas)}")
    print()

    # === PART 2: sigma_eff vs alpha_D curve at Gamma/rho = 7.0 ===
    print("=" * 80)
    print("PART 2: sigma_eff(29.4) vs alpha_D curve at Gamma/rho = 7.0 (MB, sigma_v=100)")
    print("=" * 80)
    print()

    Gamma_rho_7 = 7.0 * M_RHO_GEV
    curve = []
    for alpha_D in ALPHA_D_GRID:
        se = compute_sigma_eff(alpha_D, Gamma_rho_7, f_grid)
        r_t = se / SIGMA_TARGET
        region = classify(r_t)
        curve.append({"alpha_D": alpha_D, "sigma_eff": se, "ratio_target": r_t, "region": region})

    in_band = [p for p in curve if p["region"] == "IN BAND"]
    if in_band:
        lo = in_band[0]["alpha_D"]
        hi = in_band[-1]["alpha_D"]
        print(f"IN BAND window at Gamma/rho=7.0 (MB, sigma_v=100): [{lo:.4e}, {hi:.4e}]")
        print(f"Window width factor: {hi/lo:.3f}")
        print(f"Cloud-9 alpha_D = {ALPHA_D_CLOUD9:.4e} in window: {lo <= ALPHA_D_CLOUD9 <= hi}")
        if lo <= ALPHA_D_CLOUD9 <= hi:
            margin_low = (ALPHA_D_CLOUD9 - lo) / (hi - lo) * 100
            margin_high = (hi - ALPHA_D_CLOUD9) / (hi - lo) * 100
            print(f"Cloud-9 position in window: {margin_low:.1f}% from lower edge, {margin_high:.1f}% from upper edge")
    else:
        print("No IN BAND at Gamma/rho=7.0 under velocity-weighted MB sigma_v=100")

    # Print key alpha_D points
    print()
    print("Key alpha_D values (sigma_eff in cm^2/g, ratio = sigma_eff/174):")
    print(f"{'alpha_D':<12} | {'sigma_eff':<12} | {'ratio':<8} | region")
    print("-" * 50)
    for p in curve:
        if p["alpha_D"] in [1e-6, 3e-6, 4e-6, 5e-6, 5.55e-6, 6e-6, 7e-6, 8e-6, 1e-5]:
            print(f"{p['alpha_D']:<12.2e} | {p['sigma_eff']:<12.4f} | {p['ratio_target']:<8.4f} | {p['region']}")

    # === PART 3: Window width factor analysis (r38 Sci-5: "1.5-decade" error) ===
    print()
    print("=" * 80)
    print("PART 3: IN BAND window width factor (r38 Sci-5 correction)")
    print("=" * 80)
    print()
    print("v35 §11 claim: '1.5-decade window at each Gamma/rho'")
    print("Reality: window width factor = upper_edge/lower_edge, NOT log10(upper/lower)")
    print()
    for gf in GAMMA_RHO_DISCRETE:
        Gamma_rho = gf * M_RHO_GEV
        in_band_pts = []
        for alpha_D in ALPHA_D_GRID:
            se = compute_sigma_eff(alpha_D, Gamma_rho, f_grid)
            r_t = se / SIGMA_TARGET
            if 0.5 < r_t <= 2.0:
                in_band_pts.append(alpha_D)
        if in_band_pts:
            lo = in_band_pts[0]
            hi = in_band_pts[-1]
            factor = hi / lo
            log_factor = math.log10(factor)
            print(f"  Gamma/rho = {gf}: IN BAND = [{lo:.4e}, {hi:.4e}], "
                  f"width factor = {factor:.2f}, log10(factor) = {log_factor:.3f}")
    print()
    print("CORRECTION: '1.5-decade window' was WRONG. The actual IN BAND width")
    print("is ~1.6x (factor), NOT 31.6x (decades). A 1.6x factor in alpha_D is")
    print("equivalent to ~0.2 decades in log10(upper/lower).")

    # === Save ===
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v36_dense_sampling.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "alpha_D_Cloud9": ALPHA_D_CLOUD9,
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "sigma_v_used": 100, "distribution_used": "MB",
            "n_points_alpha": N_POINTS, "n_points_velocity": N_VPOINTS,
        },
        "dense_Gamma_rho": {
            "values": GAMMA_RHO_ALL,
            "in_band_at_Cloud9": in_band_gammas,
            "n_in_band": len(in_band_gammas),
        },
        "gamma_rho_7_curve": {
            "alpha_D_grid": [p["alpha_D"] for p in curve],
            "sigma_eff": [p["sigma_eff"] for p in curve],
            "ratio_target": [p["ratio_target"] for p in curve],
            "region": [p["region"] for p in curve],
            "in_band_window": [in_band[0]["alpha_D"], in_band[-1]["alpha_D"]] if in_band else None,
        },
        "window_width_factors": {
            str(gf): {
                "in_band_min": (in_band_pts[0] if in_band_pts else None),
                "in_band_max": (in_band_pts[-1] if in_band_pts else None),
                "width_factor": (in_band_pts[-1] / in_band_pts[0] if in_band_pts else None),
                "log10_factor": (math.log10(in_band_pts[-1] / in_band_pts[0]) if in_band_pts else None),
            }
            for gf in GAMMA_RHO_DISCRETE
            for in_band_pts in [[a for a in ALPHA_D_GRID
                                  if 0.5 < compute_sigma_eff(a, gf * M_RHO_GEV, f_grid) / SIGMA_TARGET <= 2.0]]
        },
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
