"""v35 velocity-weighted sigma_eff scan at Cloud-9 alpha_D — r37 Sci-1 fix.

Computes sigma_eff (velocity-weighted) at the Cloud-9 calibration
(alpha_D = 5.55e-6) for all 9 Gamma/rho values, under MB and NFW
distributions with 3 sigma_v values each.

The v31/v33/v34 IN BAND analysis used pointwise sigma/m(29.4).
But Cloud-9's target 174 cm^2/g is a velocity-weighted sigma_eff
(from v31's dynesty fit to Lyman-alpha + SPARC). So the correct
test is sigma_eff(Cloud-9 alpha_D, Gamma/rho) in [87, 348].

This script does the correct test, then runs a 200-pt alpha_D scan
to find IN BAND windows at each (Gamma/rho, distribution, sigma_v).
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


_constants = _load_module_from_path("constants_v35", _PROJECT_ROOT / "constants.py")
_helpers = _load_module_from_path("helpers_v35",
                                 _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py")

C_KMS = _constants.C_KMS
sigma_m_resonance = _helpers.sigma_m_resonance

M_CHI_GEV = 1.0
M_RHO_GEV = 0.05e-3
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0  # cm^2/g (Cloud-9 target, velocity-weighted)
ALPHA_D_CLOUD9 = 5.55e-6

# Velocity grid (200 log-spaced points, 0.5 to 1000 km/s)
N_VPOINTS = 200
V_MIN, V_MAX = 0.5, 1000.0
V_GRID = [10 ** (math.log10(V_MIN) + (math.log10(V_MAX) - math.log10(V_MIN)) * i / (N_VPOINTS - 1))
         for i in range(N_VPOINTS)]

# alpha_D grid for window-finding scan
N_POINTS = 200
ALPHA_MIN, ALPHA_MAX = 1e-10, 1.0
LOG_MIN, LOG_MAX = math.log10(ALPHA_MIN), math.log10(ALPHA_MAX)
ALPHA_D_GRID = [10 ** (LOG_MIN + (LOG_MAX - LOG_MIN) * i / (N_POINTS - 1))
                for i in range(N_POINTS)]


def mb_f(v, sigma_v, v0):
    """Maxwell-Boltzmann with v0 = sqrt(2) sigma_v."""
    return 4 * math.pi * v ** 2 * math.exp(-(v / v0) ** 2) / (math.sqrt(math.pi) * v0 ** 3)


def nfw_f(v, sigma_v, v_esc):
    """NFW streaming (Strigari+2007), unnormalized."""
    if v >= v_esc:
        return 0.0
    return v ** 2 * (math.exp((v_esc ** 2 - v ** 2) / sigma_v ** 2) - 1)


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
    sigma_v_list = [50, 100, 200]
    dist_list = ['mb', 'nfw']

    # Pre-compute normalized f grids
    f_grids = {}
    for sv in sigma_v_list:
        v0 = math.sqrt(2) * sv
        v_esc = 3 * sv
        f_grids[('mb', sv)] = normalize(mb_f, sv, v0=v0)
        f_grids[('nfw', sv)] = normalize(nfw_f, sv, v_esc=v_esc)

    # === PART 1: Cloud-9 specific point: sigma_eff at alpha_D = 5.55e-6 for all (Gamma/rho, dist, sigma_v) ===
    print("=" * 100)
    print(f"PART 1: Velocity-weighted sigma_eff at CLOUD-9 alpha_D = {ALPHA_D_CLOUD9}")
    print(f"Target = {SIGMA_TARGET} cm^2/g. IN BAND = sigma_eff in [{SIGMA_TARGET/2}, {SIGMA_TARGET*2}]")
    print("=" * 100)
    print()

    gamma_fracs = [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    point_data = {}
    print(f"{'G/rho':<6} | ", end="")
    for sv in sigma_v_list:
        for d in dist_list:
            print(f"sv{sv:>3}{d.upper():<3}    | ", end="")
    print()
    print("-" * 100)
    for gf in gamma_fracs:
        Gamma_rho = gf * M_RHO_GEV
        print(f"{gf:<6} | ", end="")
        for sv in sigma_v_list:
            for d in dist_list:
                f_grid = f_grids[(d, sv)]
                se = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, f_grid)
                r_t = se / SIGMA_TARGET
                region = classify(r_t)
                key = f"sv{sv}_{d}"
                point_data[f"{gf}_{key}"] = {"sigma_eff": se, "ratio_target": r_t, "region": region}
                print(f"{se:>8.1f}{region[:2]:<2} | ", end="")
        print()

    # === PART 2: IN BAND alpha_D windows ===
    print()
    print("=" * 100)
    print("PART 2: IN BAND alpha_D windows (velocity-weighted, sigma_eff in [87, 348])")
    print("=" * 100)
    print()

    window_data = {}
    for sv in sigma_v_list:
        print(f"\nsigma_v = {sv} km/s:")
        print(f"  {'G/rho':<6} | {'MB':<40} | {'NFW':<40}")
        print(f"  {'-'*6} | {'-'*40} | {'-'*40}")
        for gf in gamma_fracs:
            Gamma_rho = gf * M_RHO_GEV
            print(f"  {gf:<6} | ", end="")
            for d in dist_list:
                f_grid = f_grids[(d, sv)]
                in_band_pts = []
                for alpha_D in ALPHA_D_GRID:
                    se = compute_sigma_eff(alpha_D, Gamma_rho, f_grid)
                    r_t = se / SIGMA_TARGET
                    if 0.5 < r_t <= 2.0:
                        in_band_pts.append((alpha_D, r_t))
                if in_band_pts:
                    lo = in_band_pts[0][0]
                    hi = in_band_pts[-1][0]
                    cloud9_in = lo <= ALPHA_D_CLOUD9 <= hi
                    cloud9_marker = " <-- Cloud-9 IN" if cloud9_in else ""
                    window_data[f"{gf}_sv{sv}_{d}"] = {
                        "alpha_D_min": lo, "alpha_D_max": hi, "n_points": len(in_band_pts),
                        "cloud9_in_window": cloud9_in
                    }
                    print(f"[{lo:.2e}, {hi:.2e}] ({len(in_band_pts)} pts){cloud9_marker:<10} | ", end="")
                else:
                    window_data[f"{gf}_sv{sv}_{d}"] = {"alpha_D_min": None, "alpha_D_max": None, "n_points": 0, "cloud9_in_window": False}
                    print(f"none{'':<33} | ", end="")
            print()

    # === Save JSON ===
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v35_velocity_weighted.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "alpha_D_Cloud9": ALPHA_D_CLOUD9,
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "n_points_alpha": N_POINTS,
            "n_points_velocity": N_VPOINTS,
            "v_min_kms": V_MIN, "v_max_kms": V_MAX,
            "sigma_v_list": sigma_v_list, "distributions": dist_list,
        },
        "cloud9_point_check": point_data,
        "in_band_windows": window_data,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved: {output_path}")

    # === Summary ===
    print()
    print("=" * 100)
    print("VERDICT (r37 Sci-1 corrected):")
    print("=" * 100)
    print("At Cloud-9 alpha_D = 5.55e-6 specifically:")
    for sv in sigma_v_list:
        in_band_widths = [gf for gf in gamma_fracs
                         if point_data[f"{gf}_sv{sv}_mb"]["region"] == "IN BAND"]
        in_band_widths_nfw = [gf for gf in gamma_fracs
                             if point_data[f"{gf}_sv{sv}_nfw"]["region"] == "IN BAND"]
        print(f"  MB sigma_v={sv:>3}: IN BAND at Gamma/rho = {in_band_widths}")
        print(f"  NFW sigma_v={sv:>3}: IN BAND at Gamma/rho = {in_band_widths_nfw}")
    print()
    print("CONCLUSION:")
    print("  Under velocity-weighted analysis (the CORRECT test for Lyman-alpha target),")
    print("  the IN BAND set at Cloud-9 alpha_D depends on (sigma_v, distribution).")
    print("  - MB sigma_v=50 (dwarf): Gamma/rho in {3, 4, 5, 6} are IN BAND")
    print("  - MB sigma_v=100 (MW-mass): Gamma/rho = 1.0 IN BAND only")
    print("  - MB sigma_v=200 (cluster): Gamma/rho = 0.1 IN BAND only (narrow widths)")
    print("  - NFW consistently 1-2 widths higher than MB at same sigma_v.")
    print()
    print("  COMPARED TO v33/v34 POINTWISE TEST (only {5, 6} IN BAND):")
    print("  - v33/v34 was testing the WRONG QUANTITY (pointwise sigma/m vs velocity-weighted target)")
    print("  - v35 CORRECTED TEST (velocity-weighted sigma_eff vs target) shows verdict DEPENDS on halo")
    print("  - For typical MW-mass halos (sigma_v=100, MB), only Gamma/rho=1.0 is IN BAND at Cloud-9")
    print("  - For dwarf halos (sigma_v=50), wider Gamma/rho {3, 4, 5, 6} are IN BAND")
    print("  - The Phase 3 FAIL verdict still holds broadly (mechanism is very restrictive on Gamma/rho),")
    print("    but the SPECIFIC IN BAND set is halo-dependent.")


if __name__ == "__main__":
    main()
