"""T206 — Fit f_H as free parameter on joint 8-channel likelihood (Path C check).

Per reviewer Yangissue.docx recommendation:
  Run MCMC over (f_H_core_forming, f_H_core_collapsed) as free parameters.
  Report the posterior peak and 68% CI.
  Compare to Yang+ 2025 Fig. 2 range.

Three outcomes possible:
  A. Posterior peak at extreme values (f_H ≈ 0.85, 0.30) → empirical support
     for strong segregation → Path B/C viable.
  B. Posterior peak at no-segregation (f_H ≈ 0.75, 0.75) → data do not support
     two-component mechanism → Path A (no-go) is correct.
  C. Broad posterior → data uninformative on f_H → say so honestly.

This is a coarse-grid scan (not full MCMC) for speed. 50×50 grid in
(f_H_cf, f_H_cc) ∈ [0.5, 1.0]² takes ~1 second.
"""
import sys
import json
import math
from pathlib import Path

import numpy as np

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

from phase44_two_component import phase44_sigma_HH_at_v, phase44_two_component_sigma_eff


# ============================================================================
# Channels and published σ_unc (from T205)
# ============================================================================

CHANNELS = [
    # (name, v, σ_unc, obs_value, kind, halo_type, r/r_vir)
    ('UFD v=3',   3,    0.155, 0.155, 'ceiling',  'core_collapsed', 0.20),
    ('UFD v=5',   5,    0.093, 0.093, 'ceiling',  'core_collapsed', 0.20),
    ('UFD v=7',   7,    0.067, 0.067, 'ceiling',  'core_collapsed', 0.20),
    ('UFD v=10', 10,    0.047, 0.047, 'ceiling',  'core_collapsed', 0.20),
    ('dSph v=15',15,    0.032, 0.032, 'ceiling',  'core_collapsed', 0.20),
    ('Cloud-9 v=28', 28, 128.0, 128.0, 'floor',   'core_forming',   0.20),
    ('SPARC v=100', 100, 0.193, 0.193, 'gaussian', 'intermediate',   0.20),
    ('Cluster v=500', 500, 0.00025, 0.00025, 'ceiling', 'core_collapsed', 0.50),
]


def log_likelihood(f_H_cf, f_H_cc):
    """Log-likelihood for joint 8 channels, given f_H_core_forming and f_H_core_collapsed.

    One-sided Gaussian likelihoods (FIXED v18.32 — was backwards in v18.31):

    For ceiling channels (σ/m should be ≤ upper limit obs):
      If σ_eff ≤ obs: no penalty (correctly below the limit)
      If σ_eff > obs: Gaussian penalty normalized by σ_unc

    For floor channels (σ/m should be ≥ lower limit obs):
      If σ_eff ≥ obs: no penalty (correctly above the limit)
      If σ_eff < obs: Gaussian penalty normalized by σ_unc

    For Gaussian channels (σ/m should match value target):
      Standard Gaussian normalized by σ_unc

    Note: σ_unc is the published error budget per channel (T205). For ceiling
    channels, σ_unc is the systematic uncertainty on the upper limit; for floor
    channels, σ_unc is the 1σ floor uncertainty; for Gaussian channels, σ_unc
    is the measurement uncertainty.

    Args:
        f_H_cf: heavy mass fraction in core-forming halos at observation radius
        f_H_cc: heavy mass fraction in core-collapsed halos at observation radius

    Returns:
        log-likelihood (higher = better fit)
    """
    f_H_int = 0.5 * (f_H_cf + f_H_cc)

    halo_fH = {
        'core_forming': f_H_cf,
        'core_collapsed': f_H_cc,
        'intermediate': f_H_int,
    }

    log_L = 0.0
    for name, v, sigma_unc, obs, kind, halo, r_rvir in CHANNELS:
        f_H = halo_fH[halo]
        f_L = 1.0 - f_H
        sigma_HH = phase44_sigma_HH_at_v(v)
        sigma_eff = f_H**2 * sigma_HH

        if kind == 'ceiling':
            # σ_eff should be ≤ obs. Penalize only if σ_eff > obs.
            if sigma_eff > obs:
                z = (sigma_eff - obs) / sigma_unc
                log_L += -0.5 * z**2
            # else: no penalty (σ_eff ≤ obs is acceptable)

        elif kind == 'floor':
            # σ_eff should be ≥ obs. Penalize only if σ_eff < obs.
            if sigma_eff < obs:
                z = (obs - sigma_eff) / sigma_unc
                log_L += -0.5 * z**2
            # else: no penalty (σ_eff ≥ obs is acceptable)

        elif kind == 'gaussian':
            # σ_eff should match obs within σ_unc
            z = (sigma_eff - obs) / sigma_unc
            log_L += -0.5 * z**2

    return log_L


def main():
    # Coarse grid scan (f_H_cf, f_H_cc) ∈ [0.05, 1.00]²
    # Extended lower bound because data prefer f_H_core_collapsed small
    grid_n = 50
    f_H_cf_grid = np.linspace(0.50, 1.00, grid_n)
    f_H_cc_grid = np.linspace(0.05, 1.00, grid_n)

    log_L_grid = np.zeros((grid_n, grid_n))
    for i, fcf in enumerate(f_H_cf_grid):
        for j, fcc in enumerate(f_H_cc_grid):
            log_L_grid[i, j] = log_likelihood(fcf, fcc)

    # Find peak
    idx_peak = np.unravel_index(np.argmax(log_L_grid), log_L_grid.shape)
    fcf_peak = f_H_cf_grid[idx_peak[0]]
    fcc_peak = f_H_cc_grid[idx_peak[1]]
    log_L_peak = log_L_grid[idx_peak]

    # 68% CI: find points within Δlog L = -0.5 of peak
    threshold = log_L_peak - 0.5
    mask_68 = log_L_grid >= threshold
    fcf_68 = f_H_cf_grid[mask_68.any(axis=1)]
    fcc_68 = f_H_cc_grid[mask_68.any(axis=0)]

    print(f"\n=== T206: Path C check — fit f_H on joint 8 channels ===\n")
    print(f"Grid: {grid_n}x{grid_n} over (f_H_cf, f_H_cc) ∈ [0.50, 1.00]")
    print(f"Peak log L: {log_L_peak:.3f}")
    print(f"Peak f_H_core_forming: {fcf_peak:.3f}")
    print(f"Peak f_H_core_collapsed: {fcc_peak:.3f}")
    print(f"68% CI f_H_core_forming: [{fcf_68.min():.3f}, {fcf_68.max():.3f}]")
    print(f"68% CI f_H_core_collapsed: [{fcc_68.min():.3f}, {fcc_68.max():.3f}]")
    print()

    # Compare to Yang+ 2025 Fig. 2
    print(f"=== Yang+ 2025 Fig. 2 reference range ===")
    print(f"  f_L (number fraction of light) ∈ [0.3, 0.6] at r = 0.2 r_vir")
    print(f"  => f_H (mass fraction) ∈ [0.40, 0.70] (mass_ratio=3, equal-number ICs)")
    print()
    print(f"=== Comparison ===")
    if 0.40 <= fcf_peak <= 0.70 and 0.40 <= fcc_peak <= 0.70:
        print(f"  Peak (f_H_cf={fcf_peak:.3f}, f_H_cc={fcc_peak:.3f}) is INSIDE Yang+ 2025 range.")
        print(f"  Conclusion: data support moderate segregation consistent with Yang+.")
    elif fcc_peak < 0.40:
        print(f"  Peak f_H_core_collapsed = {fcc_peak:.3f} is BELOW Yang+ range (lower bound 0.40).")
        print(f"  Conclusion: data prefer stronger segregation than Yang+ 2025.")
    elif fcf_peak > 0.70:
        print(f"  Peak f_H_core_forming = {fcf_peak:.3f} is ABOVE Yang+ range (upper bound 0.70).")
        print(f"  Conclusion: data prefer weaker segregation in core-forming halos.")
    else:
        print(f"  Peak is at edge of parameter space; check boundary.")

    # Save results
    output = {
        'grid_n': grid_n,
        'peak_f_H_core_forming': float(fcf_peak),
        'peak_f_H_core_collapsed': float(fcc_peak),
        'peak_log_L': float(log_L_peak),
        'ci68_f_H_core_forming': [float(fcf_68.min()), float(fcf_68.max())],
        'ci68_f_H_core_collapsed': [float(fcc_68.min()), float(fcc_68.max())],
        'yang_f_H_range_at_r02': [0.40, 0.70],
        'channels': [
            {'name': n, 'v': v, 'halo': h, 'r_rvir': r}
            for n, v, _, _, _, h, r in CHANNELS
        ],
    }
    out_path = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t206_f_H_fit.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
