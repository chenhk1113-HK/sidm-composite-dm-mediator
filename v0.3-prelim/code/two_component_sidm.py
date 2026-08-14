#!/usr/bin/env python
"""
Direction B (v0.3, MINIMAL VIABLE): two-component, mass-segregated SIDM.

=============================================================================
!! PLACEHOLDER LIKELIHOODS — NOT A PUBLICATION-QUALITY RESULT !!
=============================================================================
The three channel likelihoods in this module (`loglike_dwarf`,
`loglike_cluster`, `loglike_segregation`) are *simplified Gaussian /
one-sided-Gaussian proxies*. They are stand-ins for the real published
posteriors and are hand-tuned to reproduce only the qualitative shape of the
published constraints:

    - dwarf cores want an effective sigma/m of order a few cm^2/g,
    - clusters want sigma/m < 0.5 cm^2/g,
    - the Yang+ 2026 mechanism requires component 1 to be >~ 10x more
      self-interacting than component 2.

They are NOT derived from likelihood surfaces published by any group, they
carry no calibrated absolute normalisation, and the resulting log Z /
Bayes factor must therefore be read as a *pipeline plumbing check* for
Direction B, not as evidence for or against two-component SIDM.
Replacing these three functions with real published posteriors (or with the
Yang+ 2026 gravothermal-fluid predictions) is the required next step before
any physics claim can be made.
=============================================================================

Physical picture (Yang, Fan, Hou & Tsai 2026)
--------------------------------------------
Yang, Fan, Hou, Tsai (Purple Mountain Observatory, CAS),
"Two component self-interacting dark matter model explains both dwarf galaxy
cores and strong gravitational lensing puzzles", Science Bulletin (2026),
DOI: 10.1016/j.scib.2026.01.077, arXiv:2504.02303.

The dark sector has two species:

    component 1 : heavier particle, STRONG self-interaction
                  (sigma1/m ~ 1-10 cm^2/g)  -> makes dwarf galaxy cores
    component 2 : lighter particle, WEAK self-interaction
                  (sigma2/m ~ 0.1-1 cm^2/g) -> keeps cluster / lensing
                                               constraints satisfied

Because the two species have different masses, the heavier one sinks toward
the centre of a halo (mass segregation), so the *core-forming* physics is
dominated by component 1 while the *cluster-scale / lensing* physics is
dominated (by number and by volume) by component 2. A single-component model
has to satisfy both with one number; the two-component model does not.

Minimal-viable parametrisation used here
----------------------------------------
4 free parameters:

    sigma1  : component-1 cross-section per mass at v_ref  [cm^2/g]
    sigma2  : component-2 cross-section per mass at v_ref  [cm^2/g]
    f1      : mass fraction of the DM in component 1  (component 2 -> 1 - f1)
    a       : single velocity power-law index, shared by both components

Velocity dependence (same functional form as channels_v03.sigma_m_at_v):

    sigma_i(v) = sigma_i * (v / v_ref) ** (-a),      v_ref = 100 km/s

Mass segregation is modelled with ONE extra (fixed, not fitted) parameter
`beta_seg`, which re-weights the two components as a function of velocity
scale:

    g(v)  = (v_ref / v) ** beta_seg          # >1 for dwarfs, <1 for clusters
    w1(v) = f1 * g(v) / (f1 * g(v) + (1 - f1))
    w2(v) = 1 - w1(v)

    sigma_eff(v) = w1(v) * sigma1(v) + w2(v) * sigma2(v)

`w1 + w2 = 1` by construction, so `sigma_eff(v)` is always a convex
combination of `sigma1(v)` and `sigma2(v)` (this is asserted in the tests).
With beta_seg > 0 the heavier / more-interacting component is up-weighted at
dwarf velocities and down-weighted at cluster velocities, which is the
qualitative content of the Yang+ 2026 segregation mechanism: the model can
have a HIGH effective cross-section at dwarf scale and a LOW one at cluster
scale even at a = 0, which a single-component model cannot do.

`beta_seg` is a crude phenomenological stand-in for the full two-fluid
gravothermal solution — another explicit placeholder.

No new dependencies: numpy only (importable without dynesty/scipy).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Velocity scales (km/s) — kept consistent with channels_v03.py
V_REF = 100.0        # reference velocity: all sigma_i are quoted here
V_DWARF = 30.0       # dwarf spheroidal / dwarf-core scale
V_GALAXY = 100.0     # galactic scale
V_CLUSTER = 1500.0   # Bullet-Cluster scale

# ---------------------------------------------------------------------------
# Mass-segregation strength (FIXED, not fitted, in the minimal-viable form).
# beta_seg = 0 recovers the plain convex combination with velocity-independent
# weights; beta_seg > 0 up-weights the heavier component 1 at low velocity.
SEGREGATION_BETA = 0.25

# ---------------------------------------------------------------------------
# Prior ranges for the 4 fitted parameters
LOG_SIGMA1_RANGE = (-2.0, 2.0)   # log10(sigma1 / (cm^2/g))
LOG_SIGMA2_RANGE = (-3.0, 1.0)   # log10(sigma2 / (cm^2/g))
F1_RANGE = (0.01, 0.99)          # mass fraction in component 1
A_RANGE = (-2.0, 2.0)            # shared velocity power-law index

# ---------------------------------------------------------------------------
# PLACEHOLDER channel definitions (see module docstring).
#
# Channel "dSph-effective": proxy for dwarf-galaxy cores.
#   allowed band  : sigma_eff(v_dwarf) in [0.3, 30] cm^2/g
#   peak          : ~3 cm^2/g (centre of the 1-10 cm^2/g range)
DWARF_LOG_PEAK = 0.5        # log10(3.16 cm^2/g)
DWARF_LOG_WIDTH = 0.60      # dex
DWARF_BAND = (0.3, 30.0)    # cm^2/g, hard-ish allowed band
DWARF_WALL_WIDTH = 0.20     # dex, steepness of the band walls

# Channel "Cluster-effective": proxy for the Bullet Cluster bound
#   sigma_eff(v_cluster) < 0.5 cm^2/g  (one-sided, same style as
#   channels_v03.loglike_bullet_v03 which uses Cha+ 2025 ApJ 987 L15)
CLUSTER_LOG_LIMIT = np.log10(0.5)
CLUSTER_LOG_WIDTH = 0.30    # dex

# Channel "Mass segregation": the key Yang+ 2026 requirement
#   sigma1 > 10 * sigma2  (one-sided on log10 of the ratio)
SEGREGATION_LOG_RATIO_MIN = 1.0   # log10(10)
SEGREGATION_LOG_WIDTH = 0.30      # dex


# ---------------------------------------------------------------------------
# Kinematics / effective cross-sections
# ---------------------------------------------------------------------------
def sigma_at_v(sigma_ref, a, v):
    """Single-component velocity-dependent cross-section per mass.

    sigma(v) = sigma_ref * (v / V_REF) ** (-a)

    Array-safe (works on scalars and ndarrays).
    """
    sigma_ref = np.asarray(sigma_ref, dtype=float)
    a = np.asarray(a, dtype=float)
    return sigma_ref * (float(v) / V_REF) ** (-a)


def segregation_factor(v, beta_seg: float = SEGREGATION_BETA):
    """Mass-segregation boost g(v) = (V_REF / v) ** beta_seg.

    g > 1 at dwarf velocities (heavy component 1 sinks to the centre and
    dominates the core), g < 1 at cluster velocities.  g == 1 everywhere for
    beta_seg = 0 (no segregation).
    """
    v = float(v)
    if v <= 0:
        return np.nan
    return (V_REF / v) ** float(beta_seg)


def component_weights(f1, v, beta_seg: float = SEGREGATION_BETA):
    """Velocity-dependent mass-segregation weights (w1, w2), w1 + w2 == 1."""
    f1 = np.asarray(f1, dtype=float)
    g = segregation_factor(v, beta_seg)
    num = f1 * g
    den = num + (1.0 - f1)
    w1 = np.where(den > 0, num / den, np.nan)
    return w1, 1.0 - w1


def sigma_eff(sigma1, sigma2, f1, a, v, beta_seg: float = SEGREGATION_BETA):
    """Effective (segregation-weighted) two-component cross-section at v.

    sigma_eff(v) = w1(v) * sigma1(v) + w2(v) * sigma2(v)

    Guaranteed to lie between sigma1(v) and sigma2(v) (convex combination).
    """
    s1v = sigma_at_v(sigma1, a, v)
    s2v = sigma_at_v(sigma2, a, v)
    w1, w2 = component_weights(f1, v, beta_seg)
    return w1 * s1v + w2 * s2v


def sigma_eff_dwarf(sigma1, sigma2, f1, a, beta_seg: float = SEGREGATION_BETA):
    """Effective cross-section at the dwarf-core velocity scale (30 km/s)."""
    return sigma_eff(sigma1, sigma2, f1, a, V_DWARF, beta_seg)


def sigma_eff_cluster(sigma1, sigma2, f1, a, beta_seg: float = SEGREGATION_BETA):
    """Effective cross-section at the cluster velocity scale (1500 km/s)."""
    return sigma_eff(sigma1, sigma2, f1, a, V_CLUSTER, beta_seg)


def sigma_eff_galaxy(sigma1, sigma2, f1, a, beta_seg: float = SEGREGATION_BETA):
    """Effective cross-section at the galactic velocity scale (100 km/s)."""
    return sigma_eff(sigma1, sigma2, f1, a, V_GALAXY, beta_seg)


def dwarf_to_cluster_contrast(sigma1, sigma2, f1, a,
                              beta_seg: float = SEGREGATION_BETA):
    """sigma_eff(dwarf) / sigma_eff(cluster).

    This is the two-component differentiator: with beta_seg > 0 the ratio
    exceeds the pure velocity-power-law value (V_DWARF/V_CLUSTER)**(-a) that a
    single-component model is stuck with, because segregation additionally
    shifts the weight from the strongly-interacting component 1 at dwarf
    scale to the weakly-interacting component 2 at cluster scale.
    """
    sd = sigma_eff_dwarf(sigma1, sigma2, f1, a, beta_seg)
    sc = sigma_eff_cluster(sigma1, sigma2, f1, a, beta_seg)
    return np.where(sc > 0, sd / sc, np.inf)


def single_component_contrast(a):
    """Dwarf/cluster cross-section ratio available to a single-component model.

    (V_DWARF / V_CLUSTER) ** (-a) — depends on `a` only.
    """
    a = np.asarray(a, dtype=float)
    return (V_DWARF / V_CLUSTER) ** (-a)


def core_radius_proxy(sigma_eff_dwarf_value, rho_core=1.0e7):
    """Very crude dwarf core-radius proxy, r_core ~ sqrt(sigma_eff / rho_core).

    PLACEHOLDER scaling (Robertson+-style rule of thumb, same spirit as
    channels_v03.sparc_loglike_grid which uses r_core = sqrt(sigma/m)).
    Units are not physical; only the monotonic trend is meaningful.
    """
    s = np.asarray(sigma_eff_dwarf_value, dtype=float)
    rho = float(rho_core)
    return np.sqrt(np.where(s > 0, s, np.nan) / rho * 1.0e7)


# ---------------------------------------------------------------------------
# PLACEHOLDER channel likelihoods
# ---------------------------------------------------------------------------
def _safe_log10(x):
    x = np.asarray(x, dtype=float)
    return np.where(x > 0, np.log10(np.where(x > 0, x, 1.0)), -np.inf)


def loglike_dwarf(sigma_eff_dwarf_value):
    """PLACEHOLDER channel 1: dwarf-core effective cross-section.

    Gaussian on log10(sigma_eff) peaked at ~3 cm^2/g (1-10 cm^2/g range),
    plus quadratic walls outside the allowed band [0.3, 30] cm^2/g.
    Peak value is 0 by construction (relative log L only).
    """
    log_s = _safe_log10(sigma_eff_dwarf_value)
    ll = -0.5 * ((log_s - DWARF_LOG_PEAK) / DWARF_LOG_WIDTH) ** 2
    lo, hi = np.log10(DWARF_BAND[0]), np.log10(DWARF_BAND[1])
    below = np.maximum(0.0, lo - log_s)
    above = np.maximum(0.0, log_s - hi)
    ll = ll - 0.5 * (below / DWARF_WALL_WIDTH) ** 2
    ll = ll - 0.5 * (above / DWARF_WALL_WIDTH) ** 2
    return np.where(np.isfinite(log_s), ll, -np.inf)


def loglike_cluster(sigma_eff_cluster_value):
    """PLACEHOLDER channel 2: cluster-scale bound, sigma_eff < 0.5 cm^2/g.

    One-sided Gaussian in log10 (no penalty below the limit), mirroring
    channels_v03.loglike_bullet_v03.
    """
    log_s = _safe_log10(sigma_eff_cluster_value)
    excess = np.maximum(0.0, log_s - CLUSTER_LOG_LIMIT)
    ll = -0.5 * (excess / CLUSTER_LOG_WIDTH) ** 2
    return np.where(np.isfinite(log_s), ll, 0.0)


def loglike_segregation(sigma1, sigma2):
    """PLACEHOLDER channel 3: the Yang+ 2026 mass-segregation requirement.

    Component 1 must be at least ~10x more self-interacting than component 2.
    One-sided Gaussian on log10(sigma1 / sigma2): no penalty for ratio >= 10,
    growing penalty below it.
    """
    s1 = np.asarray(sigma1, dtype=float)
    s2 = np.asarray(sigma2, dtype=float)
    ok = (s1 > 0) & (s2 > 0)
    ratio = np.where(ok, s1 / np.where(ok, s2, 1.0), np.nan)
    log_r = np.where(ok, np.log10(np.where(ok, ratio, 1.0)), -np.inf)
    deficit = np.maximum(0.0, SEGREGATION_LOG_RATIO_MIN - log_r)
    ll = -0.5 * (deficit / SEGREGATION_LOG_WIDTH) ** 2
    return np.where(ok, ll, -np.inf)


def loglike_two_component(sigma1, sigma2, f1, a,
                          beta_seg: float = SEGREGATION_BETA):
    """Total PLACEHOLDER 3-channel log-likelihood for the 2-component model.

    loglike = loglike_dwarf(sigma_eff_dwarf)
            + loglike_cluster(sigma_eff_cluster)
            + loglike_segregation(sigma1, sigma2)

    Array-safe: returns an ndarray for array input, a numpy float for scalars.
    """
    s1 = np.asarray(sigma1, dtype=float)
    s2 = np.asarray(sigma2, dtype=float)
    fr = np.asarray(f1, dtype=float)
    aa = np.asarray(a, dtype=float)

    valid = (
        np.isfinite(s1) & np.isfinite(s2) & np.isfinite(fr) & np.isfinite(aa)
        & (s1 > 0) & (s2 > 0) & (fr >= 0.0) & (fr <= 1.0)
    )

    s1s = np.where(valid, s1, 1.0)
    s2s = np.where(valid, s2, 1.0)
    frs = np.where(valid, fr, 0.5)

    sd = sigma_eff_dwarf(s1s, s2s, frs, aa, beta_seg)
    sc = sigma_eff_cluster(s1s, s2s, frs, aa, beta_seg)

    ll = loglike_dwarf(sd) + loglike_cluster(sc) + loglike_segregation(s1s, s2s)
    return np.where(valid, ll, -np.inf)


def loglike_theta(theta, beta_seg: float = SEGREGATION_BETA) -> float:
    """Scalar log-likelihood for a sampler.

    theta = (log10 sigma1, log10 sigma2, f1, a)
    """
    log_s1, log_s2, f1, a = (float(t) for t in theta)
    ll = float(loglike_two_component(10.0 ** log_s1, 10.0 ** log_s2, f1, a,
                                    beta_seg))
    if not np.isfinite(ll):
        return -1.0e300  # dynesty dislikes true -inf
    return ll


def prior_transform(u):
    """Unit-cube -> (log10 sigma1, log10 sigma2, f1, a)."""
    u = np.asarray(u, dtype=float)
    return np.array([
        LOG_SIGMA1_RANGE[0] + u[0] * (LOG_SIGMA1_RANGE[1] - LOG_SIGMA1_RANGE[0]),
        LOG_SIGMA2_RANGE[0] + u[1] * (LOG_SIGMA2_RANGE[1] - LOG_SIGMA2_RANGE[0]),
        F1_RANGE[0] + u[2] * (F1_RANGE[1] - F1_RANGE[0]),
        A_RANGE[0] + u[3] * (A_RANGE[1] - A_RANGE[0]),
    ])


PRIOR_RANGES = (LOG_SIGMA1_RANGE, LOG_SIGMA2_RANGE, F1_RANGE, A_RANGE)
PARAM_NAMES = ("log_sigma1", "log_sigma2", "f1", "a")


# ---------------------------------------------------------------------------
# dynesty-free evidence estimator (grid quadrature)
#
# Used (a) as a cross-check of the dynesty log Z and (b) so that the smoke
# tests can exercise the whole pipeline in environments without dynesty
# installed. Same integral, same flat priors:
#     Z = (1 / V_prior) * int L dtheta   ->  mean of L over the prior box.
# ---------------------------------------------------------------------------
def grid_evidence(n_per_dim: int = 21, beta_seg: float = SEGREGATION_BETA):
    """Estimate log Z and posterior summaries by 4-D midpoint quadrature.

    Returns dict with log_Z, MAP parameters, weighted percentiles and the
    flattened samples/weights (so callers can reuse the plotting path).
    """
    axes = []
    for lo, hi in PRIOR_RANGES:
        edges = np.linspace(lo, hi, n_per_dim + 1)
        axes.append(0.5 * (edges[:-1] + edges[1:]))
    L1, L2, F, A = np.meshgrid(*axes, indexing="ij")

    ll = loglike_two_component(10.0 ** L1, 10.0 ** L2, F, A, beta_seg)
    ll = np.where(np.isfinite(ll), ll, -np.inf)

    ll_flat = ll.ravel()
    finite = np.isfinite(ll_flat)
    if not finite.any():
        raise RuntimeError("grid_evidence: no finite likelihood on the grid")
    ll_max = float(ll_flat[finite].max())
    # <L> over the prior box (uniform grid weights) -> log Z
    n_cells = ll_flat.size
    log_Z = ll_max + float(np.log(np.exp(ll_flat - ll_max).sum() / n_cells))

    w = np.exp(ll_flat - ll_max)
    w = w / w.sum()
    samples = np.column_stack([L1.ravel(), L2.ravel(), F.ravel(), A.ravel()])
    imap = int(np.argmax(ll_flat))

    return {
        "log_Z": log_Z,
        "log_Z_err": float("nan"),
        "loglike_max": ll_max,
        "MAP": dict(zip(PARAM_NAMES, (float(x) for x in samples[imap]))),
        "samples": samples,
        "weights": w,
        "n_per_dim": int(n_per_dim),
        "method": "grid_quadrature",
    }


def weighted_percentiles(values, weights, qs=(16, 50, 84)):
    """Weighted percentiles of a 1-D sample."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    order = np.argsort(values)
    v, w = values[order], weights[order]
    total = w.sum()
    if total <= 0:
        return [float("nan")] * len(qs)
    cdf = np.cumsum(w) / total
    return [float(np.interp(q / 100.0, cdf, v)) for q in qs]


if __name__ == "__main__":
    print("Direction B minimal-viable two-component SIDM (PLACEHOLDER likelihoods)")
    print(f"  beta_seg = {SEGREGATION_BETA}")
    for v in (V_DWARF, V_GALAXY, V_CLUSTER):
        g = segregation_factor(v)
        w1, _ = component_weights(0.5, v)
        print(f"  v={v:7.1f} km/s: g={g:.3f}  w1(f1=0.5)={float(w1):.3f}")

    s1, s2, f1, a = 5.0, 0.2, 0.5, 0.0
    print(f"\n  sigma1={s1}, sigma2={s2}, f1={f1}, a={a}:")
    print(f"    sigma_eff(dwarf)   = {float(sigma_eff_dwarf(s1, s2, f1, a)):.3f} cm^2/g")
    print(f"    sigma_eff(galaxy)  = {float(sigma_eff_galaxy(s1, s2, f1, a)):.3f} cm^2/g")
    print(f"    sigma_eff(cluster) = {float(sigma_eff_cluster(s1, s2, f1, a)):.3f} cm^2/g")
    print(f"    dwarf/cluster contrast = {float(dwarf_to_cluster_contrast(s1, s2, f1, a)):.3f}")
    print(f"    single-component contrast at a=0 = {float(single_component_contrast(a)):.3f}")
    print(f"    log L = {float(loglike_two_component(s1, s2, f1, a)):.4f}")

    g = grid_evidence(n_per_dim=21)
    print(f"\n  grid log Z (21^4 cells) = {g['log_Z']:.3f}   max log L = {g['loglike_max']:.3f}")
    print(f"  grid MAP = {g['MAP']}")
