"""v40 extended scan: Gamma/rho = 7, 8, 10, 20 + window sensitivity (r40 items 5, 6).

Re-runs the v35 velocity-weighted analysis at extended Gamma/rho values
and tests convergence at higher velocity-grid resolution (500, 1000 pts).
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


_constants = _load_module_from_path("constants_v40", _PROJECT_ROOT / "constants.py")
_helpers = _load_module_from_path("helpers_v40",
                                 _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py")

C_KMS = _constants.C_KMS
sigma_m_resonance = _helpers.sigma_m_resonance

M_CHI_GEV = 1.0
M_RHO_GEV = 0.05e-3
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0
ALPHA_D_CLOUD9 = 5.55e-6


def make_v_grid(n_vpoints, v_min=0.5, v_max=1000.0):
    return [10 ** (math.log10(v_min) + (math.log10(v_max) - math.log10(v_min)) * i / (n_vpoints - 1))
            for i in range(n_vpoints)]


def mb_f(v, sigma_v, v0):
    return 4 * math.pi * v ** 2 * math.exp(-(v / v0) ** 2) / (math.sqrt(math.pi) * v0 ** 3)


def nfw_f(v, sigma_v, v_esc):
    if v >= v_esc:
        return 0.0
    return v ** 2 * (math.exp((v_esc ** 2 - v ** 2) / sigma_v ** 2) - 1)


def normalize(f_func, v_grid, sigma_v, **kwargs):
    f_grid = [f_func(v, sigma_v, **kwargs) for v in v_grid]
    norm = 0.0
    for i in range(len(v_grid) - 1):
        norm += 0.5 * (f_grid[i] + f_grid[i + 1]) * (v_grid[i + 1] - v_grid[i])
    if norm <= 0:
        return [0.0] * len(v_grid)
    return [f / norm for f in f_grid]


def compute_sigma_eff(alpha_D, Gamma_rho, v_grid, f_grid):
    sigma_grid = [sigma_m_resonance(v, alpha_D, M_RHO_GEV, Gamma_rho) for v in v_grid]
    se = 0.0
    for i in range(len(v_grid) - 1):
        se += 0.5 * (sigma_grid[i] * f_grid[i] + sigma_grid[i + 1] * f_grid[i + 1]) * (
            v_grid[i + 1] - v_grid[i]
        )
    return se


def classify(r_t):
    if 0.5 < r_t <= 2.0:
        return "IN BAND"
    if 0.1 < r_t <= 10.0:
        return "NEAR TARGET"
    return "OUT"


def main():
    # === PART 1: Extended Gamma/rho at Cloud-9, MB sigma_v=50 (dwarf = Cloud-9 scale) ===
    print("=" * 80)
    print("PART 1: Extended Gamma/rho scan at Cloud-9 alpha_D, MB sigma_v=50 (DWARF = Cloud-9 scale)")
    print("=" * 80)
    N_V = 200
    V_GRID = make_v_grid(N_V)
    sv = 50
    v0 = math.sqrt(2) * sv
    f_grid = normalize(mb_f, V_GRID, sv, v0=v0)

    ALPHA_GRID = [10 ** (math.log10(1e-10) + (math.log10(1.0) - math.log10(1e-10)) * i / 199)
                  for i in range(200)]

    extended_gammas = [0.01, 0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 7.5, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
    extended_data = {}
    print(f"\n{'Gamma/rho':<10} | {'sigma_eff':<12} | {'ratio':<8} | region | IN BAND window | C9 in?")
    print("-" * 80)
    for gf in extended_gammas:
        Gamma_rho = gf * M_RHO_GEV
        se_c9 = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, V_GRID, f_grid)
        r_t = se_c9 / SIGMA_TARGET
        region = classify(r_t)
        # IN BAND window
        in_band_pts = []
        for a in ALPHA_GRID:
            se = compute_sigma_eff(a, Gamma_rho, V_GRID, f_grid)
            rt = se / SIGMA_TARGET
            if 0.5 < rt <= 2.0:
                in_band_pts.append(a)
        if in_band_pts:
            lo, hi = in_band_pts[0], in_band_pts[-1]
            cloud9_in = lo <= ALPHA_D_CLOUD9 <= hi
            window_str = f"[{lo:.2e}, {hi:.2e}]"
            window_factor = hi / lo
        else:
            window_str = "none"
            cloud9_in = False
            window_factor = None
        extended_data[f"Gamma_rho_{gf}"] = {
            "sigma_eff_at_cloud9": se_c9,
            "ratio_target": r_t,
            "region": region,
            "in_band_window": [lo, hi] if in_band_pts else None,
            "window_factor": window_factor,
            "cloud9_in_window": cloud9_in,
        }
        marker = " <-- C9 IN" if cloud9_in else ""
        print(f"{gf:<10} | {se_c9:<12.3f} | {r_t:<8.4f} | {region:<12} | {window_str:<25} |{marker}")

    # === PART 2: Convergence test - sigma_v=50 MB at multiple grid sizes ===
    print()
    print("=" * 80)
    print("PART 2: Velocity grid convergence at MB sigma_v=50 (DWARF) - r40 Sci item 6")
    print("=" * 80)
    convergence_data = {}
    print(f"\n{'N_vpts':<8} | {'Gamma/rho':<10} | {'sigma_eff':<12} | {'drift vs 1000pt':<15}")
    print("-" * 60)
    # Reference at 1000 pts
    V_GRID_1000 = make_v_grid(1000)
    f_1000 = normalize(mb_f, V_GRID_1000, sv, v0=v0)
    se_ref = {}
    for gf in [1, 2, 3, 4, 5, 6]:
        Gamma_rho = gf * M_RHO_GEV
        se_ref[gf] = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, V_GRID_1000, f_1000)
    for n_vpts in [50, 100, 200, 500, 1000]:
        V_GRID_N = make_v_grid(n_vpts)
        f_N = normalize(mb_f, V_GRID_N, sv, v0=v0)
        for gf in [1, 2, 3, 4, 5, 6]:
            Gamma_rho = gf * M_RHO_GEV
            se = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, V_GRID_N, f_N)
            drift = abs(se - se_ref[gf]) / se_ref[gf] * 100 if se_ref[gf] > 0 else 0
            print(f"{n_vpts:<8} | {gf:<10} | {se:<12.4f} | {drift:<15.4f}")
            convergence_data[f"n{n_vpts}_Gamma{gf}"] = {
                "sigma_eff": se, "drift_pct_vs_1000pt": drift
            }

    # === PART 3: Convergence test - NFW at sigma_v=100 ===
    print()
    print("=" * 80)
    print("PART 3: NFW convergence at sigma_v=100 (r40 Sci item 6 - high-v tail concern)")
    print("=" * 80)
    nfw_data = {}
    sv = 100
    v_esc = 3 * sv
    for n_vpts in [100, 200, 500, 1000]:
        V_GRID_N = make_v_grid(n_vpts)
        f_N = normalize(nfw_f, V_GRID_N, sv, v_esc=v_esc)
        print(f"\n  N_vpts = {n_vpts}:")
        for gf in [1, 2, 3, 4, 5, 6]:
            Gamma_rho = gf * M_RHO_GEV
            se = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, V_GRID_N, f_N)
            r_t = se / SIGMA_TARGET
            region = classify(r_t)
            nfw_data[f"n{n_vpts}_Gamma{gf}_nfw"] = {"sigma_eff": se, "ratio": r_t, "region": region}
            print(f"    Gamma/rho={gf}: sigma_eff = {se:.4f}, ratio = {r_t:.4f} ({region})")

    # Save JSON
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v40_extended.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "alpha_D_Cloud9": ALPHA_D_CLOUD9,
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "m_chi_GeV": M_CHI_GEV,
            "m_rho_GeV": M_RHO_GEV,
            "extended_gammas": extended_gammas,
            "description": "v40 r40 Sci items 5, 6: extended Gamma/rho scan + convergence tests"
        },
        "extended_scan_MB_sigma50_dwarf": extended_data,
        "convergence_MB_sigma50": convergence_data,
        "convergence_NFW_sigma100": nfw_data,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
