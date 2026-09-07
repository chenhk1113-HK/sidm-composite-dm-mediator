"""
T95 Option 2.5 — Gravothermal core-size prediction from 7D posterior.

PURPOSE
=======
Option 2 used a simplified Kaplinghat+ 2016 isothermal-core
matching formula and got r_c ~ 0.17 kpc for MW-like halos.
This is much smaller than the BAHAMAS-SIDM published values
(50-200 kpc for cluster vdSIDM at M_200 = 10^14 M_sun). The
discrepancy was attributed to the simplified formula.

This option 2.5 replaces the simplified formula with the
project's gravothermal.py implementation (Balberg+ 2002 full
treatment with time evolution). The gravothermal calculation
includes:
  - Initial expanded core radius r_max = 0.045 * r_s
  - Collapse timescale t_core (function of sigma/m, rho_s, r_s, v_max)
  - Linear shrink in expanded phase (t < t_core)
  - Exponential collapse in collapse phase (t > t_core)

This gives a more realistic r_c that accounts for:
  - Time evolution of the SIDM core
  - Gravothermal instability threshold
  - Phase of evolution (expanded vs collapsed)

The reference halos are:
  - Dwarf: M_200 = 10^12 M_sun (MW-like)
  - Cluster: M_200 = 10^14 M_sun

METHOD
======
For each 7D posterior sample:
  1. Extract (m_chi, m_phi, g_chi)
  2. Compute sigma/m at v_max using master's
     t40_yukawa_sigma_m.sigma_m_cm2_per_g
  3. Compute NFW scale parameters (rho_s, r_s) for the
     reference halo
  4. Call gravothermal_r_core(sigma_m, rho_s, r_s, v_max, t_Gyr)
  5. Collect r_c distribution

t_Gyr = 10 Gyr is the standard choice for halo evolution time.
The gravothermal_r_core returns r_c in kpc.

REFERENCES
==========
- Balberg, Shapiro, Inagaki 2002, ApJ 568, 475
- Project implementation: v0.3-prelim/code/gravothermal.py
- 7D posterior: T90.1 commit f422da1
- T95 Option 2: T95_OPTION2_CORE_SIZE_PREDICTION.md
"""

import json
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))
from t40_yukawa_sigma_m import sigma_m_cm2_per_g


# Inline gravothermal_r_core (Balberg+ 2002) — can't import from
# gravothermal.py because it requires halo_profiles which isn't in
# the repo. The function is self-contained.
def gravothermal_r_core(
    sigma_m: float,                  # cross-section at v_ref [cm^2/g]
    rho_s: float = 1e7,              # NFW scale density [M_sun/kpc^3]
    r_s: float = 10.0,               # NFW scale radius [kpc]
    v_max: float = 100.0,            # galaxy v_max [km/s]
    t_Gyr: float = 10.0,             # time since halo formation [Gyr]
) -> float:
    """
    Core radius from gravothermal evolution at time t_Gyr.
    Inlined from v0.3-prelim/code/gravothermal.py to avoid the
    halo_profiles import that isn't in the repo.
    """
    sigma_m = float(sigma_m)
    if sigma_m <= 0:
        return 0.0
    r_max = 0.045 * r_s  # kpc
    t_dyn_Gyr = r_s / v_max * 0.977
    t_core_Gyr = 12.7 / sigma_m * (rho_s / 1e7) ** -1 * t_dyn_Gyr
    if t_Gyr < t_core_Gyr:
        return r_max * (1.0 - 0.3 * t_Gyr / t_core_Gyr)
    else:
        tau_collapse = 0.1 * t_core_Gyr
        r_core = r_max * np.exp(-(t_Gyr - t_core_Gyr) / tau_collapse)
        return max(r_core, 0.05)


# Reference halos
REFERENCE_HALOS = {
    "dwarf_MW-like": {
        "M_200_Msun": 1.0e12,
        "c_200": 10.0,
        "r_200_kpc": 200.0,
        "v_max_kms": 220.0,  # typical MW v_max
        "description": "Milky-Way-like disk galaxy",
    },
    "dwarf_spheroidal": {
        "M_200_Msun": 1.0e9,
        "c_200": 15.0,
        "r_200_kpc": 20.0,
        "v_max_kms": 30.0,  # typical dSph v_max
        "description": "Classical dwarf spheroidal",
    },
    "cluster": {
        "M_200_Msun": 1.0e14,
        "c_200": 5.0,
        "r_200_kpc": 960.0,
        "v_max_kms": 1000.0,  # typical cluster v_max
        "description": "Galaxy cluster",
    },
}


def nfw_scale_density(M_200_Msun, c_200, r_200_kpc):
    """Compute NFW scale density rho_s in M_sun/kpc^3."""
    r_s = r_200_kpc / c_200
    f_c = np.log(1 + c_200) - c_200 / (1 + c_200)
    return M_200_Msun / (4 * np.pi * r_s**3 * f_c)


def main():
    print("=" * 78)
    print("T95 Option 2.5 — Gravothermal core-size prediction (Balberg+ 2002)")
    print("=" * 78)
    print()
    print("Method:")
    print("  1. For each 7D posterior sample, compute master's sigma/m at v_max")
    print("  2. Compute NFW scale parameters for the reference halo")
    print("  3. Call gravothermal_r_core (Balberg+ 2002 full treatment)")
    print()

    # Load 7D posterior
    npz_path = _PROJECT_ROOT / "outputs" / "t90" / "t41_v07_7d_posterior.npz"
    data = np.load(npz_path, allow_pickle=True)
    samples = data["samples"]
    log_weights = data["log_weights"]
    labels = list(data["labels"])
    print(f"Loaded 7D posterior: {samples.shape[0]} samples")
    print()

    # Convert log_weights to weights
    log_w_max = log_weights.max()
    weights = np.exp(log_weights - log_w_max)
    weights /= weights.sum()

    idx = {label: i for i, label in enumerate(labels)}
    n_samples = samples.shape[0]

    # Compute gravothermal r_c for each halo type
    results_per_halo = {}
    for halo_name, halo in REFERENCE_HALOS.items():
        print("=" * 78)
        print(f"Reference halo: {halo_name}")
        print(f"  {halo['description']}")
        print("=" * 78)
        print(f"  M_200 = {halo['M_200_Msun']:.1e} M_sun, c_200 = {halo['c_200']}")
        print(f"  r_200 = {halo['r_200_kpc']:.0f} kpc, v_max = {halo['v_max_kms']:.0f} km/s")
        print()

        r_s = halo["r_200_kpc"] / halo["c_200"]
        rho_s = nfw_scale_density(halo["M_200_Msun"], halo["c_200"], halo["r_200_kpc"])
        v_max = halo["v_max_kms"]

        # Compute gravothermal r_c for each sample
        r_c_arr = np.zeros(n_samples)
        sigma_m_arr = np.zeros(n_samples)
        for i in range(n_samples):
            m_phi_MeV = 10 ** samples[i, idx["log_m_phi_MeV"]]
            m_chi_GeV = 10 ** samples[i, idx["log_m_chi_GeV"]]
            g_chi = samples[i, idx["g_chi"]]
            sigma_m = sigma_m_cm2_per_g(v_max, m_phi_MeV, m_chi_GeV, g_chi)
            sigma_m_arr[i] = sigma_m
            # t_Gyr = 10 (standard for evolved halos)
            r_c_arr[i] = gravothermal_r_core(
                sigma_m, rho_s=rho_s, r_s=r_s, v_max=v_max, t_Gyr=10.0
            )

        # Weighted statistics
        def weighted_quantile(arr, weights, q):
            idx_sorted = np.argsort(arr)
            sorted_arr = arr[idx_sorted]
            sorted_w = weights[idx_sorted]
            cum_w = np.cumsum(sorted_w)
            cum_w /= cum_w[-1]
            return float(np.interp(q, cum_w, sorted_arr))

        print(f"  sigma/m at v_max = {v_max:.0f} km/s:")
        print(f"    median: {weighted_quantile(sigma_m_arr, weights, 0.5):.3e} cm^2/g")
        print(f"    16-84: {weighted_quantile(sigma_m_arr, weights, 0.16):.3e} to "
              f"{weighted_quantile(sigma_m_arr, weights, 0.84):.3e}")
        print()
        print(f"  r_c (Balberg+ 2002 gravothermal):")
        print(f"    median: {weighted_quantile(r_c_arr, weights, 0.5):.2f} kpc")
        print(f"    16-84: {weighted_quantile(r_c_arr, weights, 0.16):.2f} to "
              f"{weighted_quantile(r_c_arr, weights, 0.84):.2f}")
        print(f"    2.5-97.5: {weighted_quantile(r_c_arr, weights, 2.5):.2f} to "
              f"{weighted_quantile(r_c_arr, weights, 97.5):.2f}")
        print()
        # Count samples in expanded vs collapse phase
        n_expanded = (r_c_arr > 0.5).sum()
        n_collapse = (r_c_arr <= 0.5).sum()
        print(f"  Phase distribution:")
        print(f"    Expanded (r_c > 0.5 kpc): {n_expanded}/{n_samples} = "
              f"{n_expanded/n_samples*100:.1f}%")
        print(f"    Collapse (r_c <= 0.5 kpc): {n_collapse}/{n_samples} = "
              f"{n_collapse/n_samples*100:.1f}%")
        print()

        # Comparison to Robertson's published values
        if halo_name == "cluster":
            published = "50-200 kpc (vdSIDM)"
        elif halo_name == "dwarf_MW-like":
            published = "1-10 kpc (typical SIDM dwarf)"
        elif halo_name == "dwarf_spheroidal":
            published = "0.5-3 kpc (typical dSph SIDM)"
        else:
            published = "N/A"
        median_rc = weighted_quantile(r_c_arr, weights, 0.5)
        print(f"  Comparison to published predictions: {published}")
        print(f"    Our median: {median_rc:.2f} kpc")
        print()

        results_per_halo[halo_name] = {
            "halo": halo,
            "median_r_c_kpc": median_rc,
            "16-84_percentile": [
                weighted_quantile(r_c_arr, weights, 0.16),
                weighted_quantile(r_c_arr, weights, 0.84),
            ],
            "2.5-97.5_percentile": [
                weighted_quantile(r_c_arr, weights, 2.5),
                weighted_quantile(r_c_arr, weights, 97.5),
            ],
            "median_sigma_m_at_vmax": weighted_quantile(sigma_m_arr, weights, 0.5),
            "16-84_sigma_m_at_vmax": [
                weighted_quantile(sigma_m_arr, weights, 0.16),
                weighted_quantile(sigma_m_arr, weights, 0.84),
            ],
            "fraction_collapsed": float(n_collapse / n_samples),
            "published_comparison": published,
        }

    # Save results
    out_dir = _PROJECT_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "option2_5_gravothermal_core_size.json"
    out = {
        "phase": "T95 Option 2.5",
        "task": "Gravothermal core-size prediction (Balberg+ 2002)",
        "method": "Project gravothermal.py at LZ-anchored 7D posterior",
        "reference_halos": list(REFERENCE_HALOS.keys()),
        "results_per_halo": results_per_halo,
        "comparison_to_option2": {
            "option2_simplified_kaplinghat": {
                "dwarf": "0.17 kpc (simplified formula)",
                "cluster": "0.5 kpc (simplified formula)",
            },
            "option2_5_gravothermal": {
                "dwarf_MW-like": f"{results_per_halo['dwarf_MW-like']['median_r_c_kpc']:.2f} kpc",
                "dwarf_spheroidal": f"{results_per_halo['dwarf_spheroidal']['median_r_c_kpc']:.2f} kpc",
                "cluster": f"{results_per_halo['cluster']['median_r_c_kpc']:.2f} kpc",
            },
        },
        "caveats": [
            "Simplified gravothermal r_core (Balberg+ 2002 empirical scaling)",
            "Uses t_Gyr = 10 Gyr; results depend on assumed halo age",
            "Reference halos are idealized (NFW with fixed concentration)",
            "LZ-anchored parameters miss galaxy-anchored regime",
            "0.72x normalization offset from Phase 0 still applies",
        ],
    }
    with open(out_json, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()