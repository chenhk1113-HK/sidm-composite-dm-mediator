"""v40.1 RE-BASELINE: Cloud-9 sigma_v correction.

Project used sigma_v = 50 km/s (MW-mass halo). Actual Cloud-9:
  W50 = 12 km/s -> sigma_v (1D) = 5.1 km/s (Anand+ 2025 ApJL 993 L55)
  v_circ at r=1.4 kpc (Cloud-9 radius) ~ 21 km/s
  v_max (NFW M=5e9, c=15) ~ 10 km/s

Re-runs the v35 velocity-weighted analysis at the correct Cloud-9 sigma_v
range [5, 8, 10, 12] km/s. This replaces the v33-v39 "dwarf" verdict
which was computed at sigma_v = 50 km/s (10x too high).
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


_constants = _load_module_from_path("constants_v401", _PROJECT_ROOT / "constants.py")
_helpers = _load_module_from_path("helpers_v401",
                                 _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py")

C_KMS = _constants.C_KMS
sigma_m_resonance = _helpers.sigma_m_resonance

M_CHI_GEV = 1.0
M_RHO_GEV = 0.05e-3
V_TARGET_KMS = 29.4  # KEPT from project for reference (likely v_circ derived)
SIGMA_TARGET = 174.0  # KEPT from project — project-internal, not from Cloud-9 paper
ALPHA_D_CLOUD9 = 5.55e-6  # KEPT from project — project-internal dynesty fit

# ACTUAL Cloud-9 velocity dispersion: sigma_v (1D) = 5.1 km/s
SIGMA_V_CLOUD9 = 5.1
SIGMA_V_CLOUD9_HALO = 8.8  # sigma_3D for full halo (sqrt(3)*sigma_1D)
# For MB distribution, the v35 code uses v0 = sqrt(2) * sigma_v (sigma_1D convention)
# So sigma_v parameter in compute_sigma_eff = 5.1 (1D)

# Velocity grid
N_VPOINTS = 200
V_MIN, V_MAX = 0.5, 1000.0
V_GRID = [10 ** (math.log10(V_MIN) + (math.log10(V_MAX) - math.log10(V_MIN)) * i / (N_VPOINTS - 1))
         for i in range(N_VPOINTS)]


def mb_f(v, sigma_v, v0):
    return 4 * math.pi * v ** 2 * math.exp(-(v / v0) ** 2) / (math.sqrt(math.pi) * v0 ** 3)


def normalize(f_func, sigma_v, **kwargs):
    f_grid = [f_func(v, sigma_v, **kwargs) for v in V_GRID]
    norm = 0.0
    for i in range(N_VPOINTS - 1):
        norm += 0.5 * (f_grid[i] + f_grid[i + 1]) * (V_GRID[i + 1] - v_grid[i] if False else V_GRID[i + 1] - V_GRID[i])
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
    # === PART 1: Cloud-9 point check at correct sigma_v ===
    print("=" * 80)
    print("PART 1: Cloud-9 point check at CORRECT sigma_v (W50=12 km/s -> sigma_v=5.1 km/s)")
    print("=" * 80)

    sigma_v_values = [5.1, 8.0, 10.0, 12.0, 30.0, 50.0, 100.0]  # include old wrong values for comparison
    gammas = [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 20.0]

    all_results = {}
    for sv in sigma_v_values:
        v0 = math.sqrt(2) * sv
        f_grid = normalize(mb_f, sv, v0=v0)
        print(f"\n  sigma_v = {sv} km/s (v0 = {v0:.2f} km/s):")
        print(f"    {'Gamma/rho':<10} | {'sigma_eff':<12} | {'ratio':<8} | region")
        sv_data = {}
        for gf in gammas:
            Gamma_rho = gf * M_RHO_GEV
            se = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, f_grid)
            r_t = se / SIGMA_TARGET
            region = classify(r_t)
            sv_data[f"gf_{gf}"] = {
                "sigma_eff": se, "ratio": r_t, "region": region
            }
            print(f"    {gf:<10} | {se:<12.4f} | {r_t:<8.4f} | {region}")
        all_results[f"sv_{sv}"] = sv_data

    # === PART 2: IN BAND windows at correct sigma_v ===
    print()
    print("=" * 80)
    print("PART 2: IN BAND alpha_D windows at CORRECT sigma_v (5.1 km/s)")
    print("=" * 80)

    N_ALPHA = 200
    ALPHA_GRID = [10 ** (math.log10(1e-10) + (math.log10(1.0) - math.log10(1e-10)) * i / (N_ALPHA - 1))
                  for i in range(N_ALPHA)]

    sv = 5.1
    v0 = math.sqrt(2) * sv
    f_grid = normalize(mb_f, sv, v0=v0)

    print(f"\n  sigma_v = {sv} km/s (Cloud-9):")
    print(f"    {'Gamma/rho':<10} | {'window [min, max]':<35} | C9 in? | width factor")
    print("    " + "-" * 70)
    windows = {}
    for gf in gammas:
        Gamma_rho = gf * M_RHO_GEV
        in_band = []
        for a in ALPHA_GRID:
            se = compute_sigma_eff(a, Gamma_rho, f_grid)
            rt = se / SIGMA_TARGET
            if 0.5 < rt <= 2.0:
                in_band.append(a)
        if in_band:
            lo, hi = in_band[0], in_band[-1]
            cloud9_in = lo <= ALPHA_D_CLOUD9 <= hi
            factor = hi / lo
            window_str = f"[{lo:.2e}, {hi:.2e}]"
            print(f"    {gf:<10} | {window_str:<35} | {str(cloud9_in):<5} | {factor:.2f}x")
            windows[f"gf_{gf}"] = {"window": [lo, hi], "cloud9_in": cloud9_in, "factor": factor}
        else:
            print(f"    {gf:<10} | none{'':<30} | False | N/A")
            windows[f"gf_{gf}"] = {"window": None, "cloud9_in": False}

    # === PART 3: Pointwise sigma/m(v=29.4) for reference ===
    print()
    print("=" * 80)
    print("PART 3: Pointwise sigma/m(v=29.4) at Cloud-9 alpha_D (for reference)")
    print("=" * 80)
    for gf in gammas:
        Gamma_rho = gf * M_RHO_GEV
        sigma_pw = sigma_m_resonance(V_TARGET_KMS, ALPHA_D_CLOUD9, M_RHO_GEV, Gamma_rho)
        r_t = sigma_pw / SIGMA_TARGET
        region = classify(r_t)
        print(f"  Gamma/rho={gf}: sigma/m(29.4) = {sigma_pw:.2f}, ratio = {r_t:.4f} ({region})")

    # Save JSON
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v40_1_rebaseline.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "alpha_D_Cloud9": ALPHA_D_CLOUD9,
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "m_rho_GeV": M_RHO_GEV,
            "cloud9_paper": "Anand+ 2025 ApJL 993 L55",
            "cloud9_W50_kms": 12.0,
            "sigma_v_Cloud9_1D_kms": SIGMA_V_CLOUD9,
            "sigma_v_Cloud9_3D_kms": SIGMA_V_CLOUD9_HALO,
            "correction": "Project's sigma_v=50 was 10x too high for actual Cloud-9"
        },
        "cloud9_point_check_at_correct_sigma_v": all_results,
        "in_band_windows_at_sigma_v_5.1": windows,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
