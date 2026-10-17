"""v40.2 SIMPLIFIED FINE-GRID: linear interpolation, no bisection.

Fix for the v40.1 N1 contradiction: at Gamma/rho=6.0, the 200-pt grid's
last IN BAND sample was at 5.29e-6 but the point check at 5.55e-6 gave
ratio=1.84. The 200-pt grid undersampled.

Approach: 500-pt grid + linear interpolation between adjacent IN BAND/non-IN BAND
points to get sub-grid-resolution window boundaries. Much faster than bisection.
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


_constants = _load_module_from_path("constants_v402s", _PROJECT_ROOT / "constants.py")
_helpers = _load_module_from_path("helpers_v402s",
                                 _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py")

sigma_m_resonance = _helpers.sigma_m_resonance

M_RHO_GEV = 0.05e-3
SIGMA_TARGET = 174.0
ALPHA_D_CLOUD9 = 5.55e-6

N_VPOINTS = 200
V_MIN, V_MAX = 0.5, 1000.0
V_GRID = [10 ** (math.log10(V_MIN) + (math.log10(V_MAX) - math.log10(V_MIN)) * i / (N_VPOINTS - 1))
         for i in range(N_VPOINTS)]


def mb_f(v, sigma_v, v0):
    return 4 * math.pi * v ** 2 * math.exp(-(v / v0) ** 2) / (math.sqrt(math.pi) * v0 ** 3)


def normalize(sigma_v, v0):
    f_grid = [mb_f(v, sigma_v, v0) for v in V_GRID]
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


def find_window_linear(sigma_v, Gamma_rho, f_grid, n_alpha=500):
    """Find IN BAND window via 500-pt grid + linear interpolation between
    adjacent (IN_BAND, OUT) points."""
    log_lo, log_hi = math.log10(1e-10), math.log10(1.0)
    alphas = [10 ** (log_lo + (log_hi - log_lo) * i / (n_alpha - 1))
              for i in range(n_alpha)]
    # Compute ratios
    ratios = []
    for a in alphas:
        se = compute_sigma_eff(a, Gamma_rho, f_grid)
        ratios.append(se / SIGMA_TARGET)
    # Find indices where ratio is in (0.5, 2.0]
    in_band_indices = [i for i, r in enumerate(ratios) if 0.5 < r <= 2.0]
    if not in_band_indices:
        return None, None, 0
    first = in_band_indices[0]
    last = in_band_indices[-1]
    # Linear interpolation: find exact alpha where ratio = 0.5 (lower) and ratio = 2.0 (upper)
    if first == 0:
        true_lower = alphas[0]
    else:
        r_lo = ratios[first - 1]
        r_hi = ratios[first]
        a_lo = alphas[first - 1]
        a_hi = alphas[first]
        m = (r_hi - r_lo) / (math.log10(a_hi) - math.log10(a_lo))
        c = r_lo - m * math.log10(a_lo)
        log_a_lower = (0.5 - c) / m
        true_lower = 10 ** log_a_lower
    if last == n_alpha - 1:
        true_upper = alphas[-1]
    else:
        r_lo = ratios[last]
        r_hi = ratios[last + 1]
        a_lo = alphas[last]
        a_hi = alphas[last + 1]
        m = (r_hi - r_lo) / (math.log10(a_hi) - math.log10(a_lo))
        c = r_lo - m * math.log10(a_lo)
        log_a_upper = (2.0 - c) / m
        true_upper = 10 ** log_a_upper
    return true_lower, true_upper, len(in_band_indices)


def classify(r_t):
    if 0.5 < r_t <= 2.0:
        return "IN BAND"
    if 0.1 < r_t <= 10.0:
        return "NEAR TARGET"
    return "OUT"


def main():
    sv = 5.1
    v0 = math.sqrt(2) * sv
    f_grid = normalize(sv, v0)

    gammas = [0.01, 0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
    windows = {}
    point_check = {}

    print("=" * 90)
    print("v40.2 FINE-GRID FIX (linear interp): True IN BAND boundaries at sigma_v=5.1 km/s (Cloud-9)")
    print("=" * 90)
    print(f"\n{'Gamma/rho':<10} | {'window (v40.1 200-pt)':<28} | {'window (v40.2 500-pt interp)':<35} | C9 in (v40.2)")
    print("-" * 95)
    for gf in gammas:
        Gamma_rho = gf * M_RHO_GEV
        # Part 1: point check at Cloud-9
        se_c9 = compute_sigma_eff(ALPHA_D_CLOUD9, Gamma_rho, f_grid)
        r_t = se_c9 / SIGMA_TARGET
        region = classify(r_t)
        point_check[gf] = {"sigma_eff": se_c9, "ratio": r_t, "region": region}
        # v40.1 window (200-pt)
        n_old = 200
        alphas_old = [10 ** (math.log10(1e-10) + (math.log10(1.0) - math.log10(1e-10)) * i / (n_old - 1))
                      for i in range(n_old)]
        in_old = [alphas_old[i] for i in range(n_old)
                  if 0.5 < compute_sigma_eff(alphas_old[i], Gamma_rho, f_grid) / SIGMA_TARGET <= 2.0]
        lo_old = in_old[0] if in_old else None
        hi_old = in_old[-1] if in_old else None
        # v40.2 window (500-pt + linear interp)
        lo_new, hi_new, n_pts = find_window_linear(sv, Gamma_rho, f_grid, n_alpha=500)
        cloud9_in_old = (lo_old is not None) and (lo_old <= ALPHA_D_CLOUD9 <= hi_old)
        cloud9_in_new = (lo_new is not None) and (lo_new <= ALPHA_D_CLOUD9 <= hi_new)
        windows[gf] = {
            "v40_1_200pt_window": [lo_old, hi_old] if lo_old else None,
            "v40_1_cloud9_in": cloud9_in_old,
            "v40_2_500pt_interp_window": [lo_new, hi_new] if lo_new else None,
            "v40_2_cloud9_in": cloud9_in_new,
            "n_fine_points": n_pts,
        }
        old_str = f"[{lo_old:.2e}, {hi_old:.2e}]" if lo_old else "none"
        new_str = f"[{lo_new:.2e}, {hi_new:.2e}]" if lo_new else "none"
        c9 = "YES" if cloud9_in_new else "no"
        marker = " <-- FIXED (C9 now IN)" if (cloud9_in_new and not cloud9_in_old) else ""
        print(f"{gf:<10} | {old_str:<28} | {new_str:<35} | {c9}{marker}")

    # Save
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v40_2_finegrid.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "alpha_D_Cloud9": ALPHA_D_CLOUD9,
            "sigma_target": SIGMA_TARGET,
            "sigma_v_Cloud9": 5.1,
            "n_alpha_fine": 500,
            "method": "500-pt log-spaced grid + linear interpolation between adjacent IN_BAND/OUT points"
        },
        "point_check_at_Cloud9": {str(k): v for k, v in point_check.items()},
        "fine_windows": {str(k): v for k, v in windows.items()},
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
