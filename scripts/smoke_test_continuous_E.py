#!/usr/bin/env python3
"""
smoke_test_continuous_E.py — 15-min smoke test of Path 2.

Goal: confirm a continuous E parameterization can fit the 5 standing
observables (Cloud-9, Draco, Sculptor, Fornax, Cluster) with reasonable
residuals BEFORE committing 2.7 hours to full Path 2.

E-proxy design (3 components):
  log_E = log10(f_b / 0.1) - alpha * log10(host_M_vir / 1e10) + gamma * (t / t_core)
  with alpha = 0.5, gamma = 0.3 (approximate)

Then fit sigma_eff = sigma_eff_P44 * (E / E_REF)^beta to the 5 anchors.
Report: residuals, chi^2, plot.
"""
import json
from pathlib import Path
import numpy as np

REPO = Path(__file__).parent.parent
RESULTS = REPO / "v0.3-prelim" / "data" / "results"
FIGS = REPO / "v0.3-prelim" / "docs" / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Step 1: Define E-proxy
# ============================================================================
def E_proxy(f_b, host_M_vir_over_M_dwarf, t_over_t_core, alpha=0.5, gamma=0.3):
    """
    Continuous E-proxy combining:
    - baryon fraction f_b (higher -> more suppression)
    - host/M_dwarf mass ratio (higher -> more tidal stripping -> more suppression)
    - gravothermal phase t/t_core (higher -> more collapsed -> different sigma)

    Returns log10(E), where E=1 means "no suppression" (RELHIC-like).
    E > 1 means suppression expected (sigma_eff < sigma_eff_P44).
    E < 1 means enhancement expected.

    Reference: RELHIC (Cloud-9) has E_proxy = 1 by definition (log_E = 0).
    Formula:
      log_E = max(0, log10(f_b / f_b_REF)) - alpha * log10(host_ratio)
    where f_b_REF = 1e-3 (Cloud-9 f_b marginal, ~1e-4 below detection).
    """
    f_b_REF = 1e-3  # RELHIC reference (Cloud-9 f_b is below this)
    # f_b below reference => log10(f_b/f_b_REF) < 0
    # But RELHIC should be the *reference*, so clip:
    log_E_b = max(0.0, np.log10(max(f_b, f_b_REF) / f_b_REF))
    # log_E_b = 0 for RELHIC, increases with baryon fraction
    log_E_host = alpha * np.log10(max(host_M_vir_over_M_dwarf, 1.0))
    log_E_phase = gamma * t_over_t_core
    log_E = log_E_b + log_E_host + log_E_phase
    return log_E


# ============================================================================
# Step 2: 5 standing observables with E-proxy values
# ============================================================================
# Format: (name, V_max, sigma_obs, bound, f_b, host_ratio, t_over_t_core)
# Values from published literature (anchored in paper §9 references):
#   f_b for field dSph from Kirby+ 2017 (~0.001-0.005)
#   f_b for cluster from Lin+ 2014 (~0.05-0.15)
#   f_b for RELHIC from Ergo/Cloud-9 paper, marginal baryons (~0.001 or less)
#   host ratio for satellite = host_M_vir / M_dwarf (Fornax ~ 1000)
#   host ratio for field = 1 (isolated)
#   t/t_core: ~0.2 for uncollapsed dSphs, ~1.0 for Cluster, ~0.05 for RELHIC

OBSERVABLES = [
    # (name, V_max, sigma_obs, bound, f_b, host_ratio, t_over_t_core)
    ("Cloud-9 (RELHIC)",  28,   100, "lower", 1e-4, 1.0,    0.05),
    ("Draco (field dSph)", 18,   1.0, "upper", 1e-3, 1.0,    0.20),
    ("Sculptor (field dSph)", 20, 1.0, "upper", 2e-3, 1.0,   0.20),
    ("Fornax (satellite)", 22,   5.0, "upper", 5e-4, 1000.0, 0.30),
    ("Cluster (Bullet)", 500,   0.1, "upper", 0.1,  1.0,    1.0),
]


# ============================================================================
# Phase 44 baseline sigma_eff (recomputed from build_population_sigma_eff_map)
# ============================================================================
import sys
sys.path.insert(0, str(Path(__file__).parent))
from build_population_sigma_eff_map import load_phase44_params, sigma_eff_two_comp

p44 = load_phase44_params()


def sigma_eff_phase44(V_max):
    halo_type = "core_forming" if V_max < 100 else "cuspy"
    r = 0.05 if halo_type == "core_forming" else 0.1
    return sigma_eff_two_comp(V_max, halo_type, r, p44)


# ============================================================================
# Step 3: Fit sigma_eff = sigma_eff_P44 * (E / E_REF)^beta
# ============================================================================
def fit_continuous_E(observables, beta_init=-0.5):
    """
    Fit a single power-law: sigma_eff = sigma_eff_P44 * 10^(beta * log_E)
    where log_E is the continuous E-proxy.

    For Cloud-9 (RELHIC, lower bound), fit to lower bound as constraint.
    For others (upper bound), fit to upper bound as constraint.

    Return (beta, residuals_dict, log_E_values).
    """
    log_E_arr = []
    target_arr = []  # log10(sigma_target)
    weight_arr = []
    sigma_p44_arr = []
    names = []

    for name, V, sigma_obs, bound, f_b, host_ratio, t_tc in observables:
        logE = E_proxy(f_b, host_ratio, t_tc)
        s44 = sigma_eff_phase44(V)
        if bound == "lower":
            target = np.log10(sigma_obs)  # need sigma_eff >= this
        else:
            target = np.log10(sigma_obs)  # need sigma_eff <= this
        log_E_arr.append(logE)
        target_arr.append(target)
        weight_arr.append(1.0)
        sigma_p44_arr.append(s44)
        names.append(name)

    log_E = np.array(log_E_arr)
    target = np.array(target_arr)
    weight = np.array(weight_arr)
    sigma_p44 = np.array(sigma_p44_arr)
    log_sigma_p44 = np.log10(sigma_p44)

    # Fit: log10(sigma) = log10(sigma_p44) + beta * log_E
    # i.e. beta = (target - log_sigma_p44) weighted by log_E / log_E^2

    # Try a grid search over beta (avoids linear algebra issues with log_E ~ 0)
    best_beta = None
    best_chi2 = np.inf
    for beta in np.linspace(-3.0, 1.0, 401):
        predicted = log_sigma_p44 + beta * log_E
        # For lower bound (Cloud-9), violation = (sigma_pred - sigma_obs) < 0
        # For upper bound, violation = (sigma_pred - sigma_obs) > 0
        violations = []
        for i, (name, _, _, b, _, _, _) in enumerate(observables):
            if b == "lower":
                # sigma_pred < sigma_obs = bad
                v = max(0, np.log10(sigma_obs) - predicted[i])
            else:
                # sigma_pred > sigma_obs = bad
                v = max(0, predicted[i] - np.log10(sigma_obs))
            violations.append(v)
        chi2 = sum(w * v**2 for w, v in zip(weight, violations))
        # Also penalize large residuals from sigma_p44 (don't drift too far)
        reg = 0.01 * np.sum((predicted - log_sigma_p44) ** 2)
        chi2 += reg
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_beta = beta

    # Compute residuals at best beta
    predicted = log_sigma_p44 + best_beta * log_E
    residuals = {}
    for i, (name, _, sigma_obs, b, _, _, _) in enumerate(observables):
        # Convert to linear residuals: factor by which prediction exceeds/undercuts
        predicted_lin = 10 ** predicted[i]
        if b == "lower":
            ratio = predicted_lin / sigma_obs  # >= 1 means PASS
        else:
            ratio = predicted_lin / sigma_obs  # <= 1 means PASS
        residuals[name] = {
            "log_E": log_E[i],
            "log_sigma_p44": log_sigma_p44[i],
            "predicted_log10": predicted[i],
            "predicted_lin": predicted_lin,
            "sigma_obs": sigma_obs,
            "bound": b,
            "ratio": ratio,
            "PASS": (ratio >= 1) if b == "lower" else (ratio <= 1),
        }

    return best_beta, residuals, log_E


# ============================================================================
# Step 4: Output
# ============================================================================
def main():
    print("=" * 70)
    print("SMOKE TEST: Continuous E-proxy fit (15-min budget)")
    print("=" * 70)
    print()

    # Step 2: show E-proxy values
    print("Step 1+2: E-proxy for 5 standing observables")
    print()
    print(f"{'name':<28} {'V_max':>6} {'f_b':>10} {'host_ratio':>11} {'t/t_core':>9} {'log10(E)':>9}")
    for name, V, sigma_obs, bound, f_b, host_ratio, t_tc in OBSERVABLES:
        logE = E_proxy(f_b, host_ratio, t_tc)
        print(f"{name:<28} {V:>6.0f} {f_b:>10.1e} {host_ratio:>11.0f} {t_tc:>9.2f} {logE:>9.3f}")
    print()

    # Step 3: fit
    print("Step 3: Fit sigma_eff = sigma_eff_P44 * (E)^beta")
    beta, residuals, log_E = fit_continuous_E(OBSERVABLES)
    print(f"  Best-fit beta = {beta:.3f}")
    print()

    print("Step 4: Residuals")
    print()
    print(f"{'name':<28} {'log_E':>7} {'log_sigma_p44':>14} {'predicted':>10} {'sigma_obs':>9} {'ratio':>7} {'verdict':>8}")
    for name, r in residuals.items():
        verdict = "PASS" if r["PASS"] else "FAIL"
        print(f"{name:<28} {r['log_E']:>7.3f} {r['log_sigma_p44']:>14.3f} {r['predicted_lin']:>10.3f} {r['sigma_obs']:>9.2f} {r['ratio']:>7.3f} {verdict:>8}")
    print()

    # Verdict
    n_pass = sum(1 for r in residuals.values() if r["PASS"])
    n_fail = sum(1 for r in residuals.values() if not r["PASS"])
    print(f"Continuous E fit: {n_pass} PASS, {n_fail} FAIL out of 5")
    print()

    # Save
    out = {
        "metadata": {
            "description": "Smoke test of continuous E-proxy fit on 5 standing observables",
            "approach": "sigma_eff = sigma_eff_P44 * 10^(beta * log_E)",
            "E_proxy_definition": "log_E = log10(f_b/0.1) - 0.5*log10(host_ratio) + 0.3*(t/t_core)",
        },
        "best_fit_beta": beta,
        "residuals": residuals,
        "verdict": f"{n_pass} PASS, {n_fail} FAIL",
    }
    out_path = RESULTS / "phase4c_smoke_test_continuous_E.json"
    def _convert(o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=_convert)
    print(f"Saved: {out_path}")

    # Plot
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        names = list(residuals.keys())
        Vs = [o[1] for o in OBSERVABLES]
        logEs = [residuals[n]["log_E"] for n in names]
        sigmas_p44 = [residuals[n]["log_sigma_p44"] for n in names]
        sigmas_pred = [residuals[n]["predicted_lin"] for n in names]

        for i, name in enumerate(names):
            color = "green" if residuals[name]["PASS"] else "red"
            ax.scatter(Vs[i], sigmas_pred[i], c=color, s=150, edgecolors='black', zorder=3)
            ax.annotate(f"{residuals[name]['bound'][0]}", (Vs[i], sigmas_pred[i]),
                        textcoords="offset points", xytext=(8, 8), fontsize=12, fontweight='bold')
            ax.scatter(Vs[i], 10**sigmas_p44[i], c='blue', marker='x', s=100, alpha=0.5, zorder=2)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('V_max (km/s)')
        ax.set_ylabel('sigma_eff (cm^2/g)')
        ax.set_title(f"Continuous E-proxy fit (smoke test, beta={beta:.2f})\nGreen=PASS, Red=FAIL, x=Phase 4A prediction")
        ax.grid(True, alpha=0.3, which='both')

        out_png = FIGS / "fig7_smoke_test_continuous_E.png"
        plt.tight_layout()
        plt.savefig(out_png, dpi=120)
        print(f"Saved: {out_png}")
    except ImportError:
        print("matplotlib not available, skipping plot")


if __name__ == "__main__":
    main()