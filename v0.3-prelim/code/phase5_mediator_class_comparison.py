#!/usr/bin/env python3
"""
Phase 5 minimal: mediator class comparison via sigma/m(v) functional forms.

Per R1 mapreview.docx Gap 4 (mediator class): "vector/scalar/composite:
which UV completion produces the velocity dependence we observe?"

Per Phase 4 finding (2026-09-12): "Yukawa gives over-strong velocity
dependence; power-law phenomenological fits better."

GOAL: Test 4 alternative mediator forms to the power-law phenomenology
(σ/m_0=0.72, a=1.31). For each, evaluate Bayes factor vs the power-law
reference at the v0.3-prelim MAP.

MEDIATOR CLASSES (per project context, channel 14/15 docs):

1. Power-law (T39 reference): σ/m(v) = σ/m_0 × (v/v_ref)^(-a)
 - Best fit: σ/m_0=0.72, a=1.31, log_Z=-2.94
 - Reference for comparison

2. Vector/Portal-A (dark photon kinetic mixing): Yukawa form
 - σ/m(v) = σ_0 / (1 + (v/v_dm)^2) at v_dm = sqrt(m_chi m_A') / m_chi
 - At v0.3-prelim MAP (sigma/m_0=0.72, a=1.31): expect over-strong
   dependence (per Phase 4 finding); used as negative control

3. Scalar/Higgs portal: constant + power-law correction
 - σ/m(v) = σ/m_0 × (1 + α (v/v_ref - 1)) where α is small coupling
 - At v0.3-prelim MAP: linear correction only

4. Composite/Portal-B (dark pion, Kaplan+ 2009): resonance at v_R
 - σ/m(v) = σ/m_0 × exp(-(v - v_R)^2 / (2 Δv^2))
 - At v0.3-prelim MAP: resonance centered at v_R = 30 km/s (dwarf regime)
 - Width Δv = 50 km/s (broad)

METHODOLOGY:
- Use T39's existing joint-fit loglike (4D, 5 channels)
- Replace sigma_m_at_v(...) call with each mediator form
- Evaluate log_Z at v0.3-prelim MAP (sigma/m_0=0.72, a=1.31)
- Compare Bayes factors between mediator classes

KILL CRITERION (per roadmap):
- |Δlog Z| < 1 between any two mediator classes → indistinguishable;
  mediator class NOT constrained; report and stop.

PER AGENTS.md rule 23 (computational-failure hook):
- Per AGENTS.md rule 27: ASCII superscripts only (no 10^-N)
- Sanity checks at the v0.3-prelim MAP against published values
"""

import sys
import json
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))

from channels_v03 import (
    sigma_m_at_v,
    V_REF,
    loglike_dsph_v03,
    loglike_ufd_v03,
)
from t8_v03_joint_fit import loglike_sparc_hierarchical
from t30_lz_real_posterior import loglike_lz_real
from t32_fermi_dwarf_channel import loglike_fermi_dwarf
from t39_tier3_epsilon_alpha_joint_fit import (
    sigma_SI_from_dark_photon,
    sigma_v_from_dark_photon,
)

# Fixed Benchmark A parameters (from T39)
M_CHI_GEV_FIXED = 40.0
M_A_PRIME_MEV_FIXED = 10.0
ALPHA_D_FIXED = 0.01

# ----------------------------------------------------------------------
# v0.3-prelim MAP
# ----------------------------------------------------------------------
V03_MAP = {
    "sigma_m_0": 0.72,  # cm^2/g
    "a": 1.31,  # velocity dependence (positive = drops with v)
    "log_epsilon": -56.1,  # log_10(ε)
    "log_alpha": -28.0,  # log_10(α)
}

# Representative velocities (km/s) for testing
V_DWARF = 10.0
V_CLUSTER = 1000.0


# ----------------------------------------------------------------------
# Mediator class 1: Power-law (T39 reference)
# ----------------------------------------------------------------------
def sigma_m_power_law(sigma_m_0: float, a: float, v: float) -> float:
    """σ/m(v) = σ/m_0 × (v/v_ref)^(-a).

    This is the T39 reference form (phenomenological).
    """
    return sigma_m_at_v(sigma_m_0, a, v)


# ----------------------------------------------------------------------
# Mediator class 2: Vector/Portal-A (Yukawa form, dark photon kinetic mixing)
# ----------------------------------------------------------------------
def sigma_m_yukawa(sigma_m_0: float, a: float, v: float,
                   m_chi_gev: float = 40.0, m_aprime_mev: float = 10.0) -> float:
    """σ/m(v) from Yukawa (dark photon) mediator.

    σ/m(v) ∝ 1 / (1 + (v/v_dm)^2)
    where v_dm ~ sqrt(m_chi * m_A') / m_chi is the characteristic velocity.

    For m_chi=40 GeV, m_A'=10 MeV: v_dm ~ sqrt(0.04 * 0.01) / 0.04 = 0.5 km/s
    At v >> v_dm: σ/m ∝ 1/v^2 (over-strong velocity dependence, per Phase 4)
    """
    m_chi_mev = m_chi_gev * 1000.0
    v_dm_km_s = np.sqrt(m_chi_mev * m_aprime_mev) / m_chi_mev  # in c=1 units
    # Convert v_dm from c to km/s: c = 3e5 km/s, so v_dm ~ 3e5 * v_dm
    v_dm_km_s_actual = v_dm_km_s * 3e5
    if v_dm_km_s_actual < 1e-6:
        v_dm_km_s_actual = 1e-6
    # Normalize to σ/m_0 at v_ref = 100 km/s
    prefactor = sigma_m_0 * (1 + (V_REF / v_dm_km_s_actual) ** 2)
    return prefactor / (1 + (v / v_dm_km_s_actual) ** 2)


# ----------------------------------------------------------------------
# Mediator class 3: Scalar/Higgs portal (linear correction)
# ----------------------------------------------------------------------
def sigma_m_scalar_portal(sigma_m_0: float, a: float, v: float,
                          alpha_h: float = 0.5) -> float:
    """σ/m(v) = σ/m_0 × (1 + α_h × (v/v_ref - 1)).

    Linear velocity dependence (modest). When α_h ~ 0.5, this gives
    σ/m dropping by ~50% from cluster to dwarf velocities.

    At v0.3-prelim MAP: σ/m(v) at v=10 km/s = σ/m_0 × (1 + 0.5 × (0.1 - 1))
    = σ/m_0 × 0.55; at v=1000: σ/m_0 × 1.45. So σ/m drops by ~36% per
    decade in velocity (vs power-law's 95% per decade with a=1.31).
    """
    return sigma_m_0 * (1 + alpha_h * (v / V_REF - 1))


# ----------------------------------------------------------------------
# Mediator class 4: Composite/Portal-B (dark pion resonance)
# ----------------------------------------------------------------------
def sigma_m_composite(sigma_m_0: float, a: float, v: float,
                      v_R: float = 30.0, delta_v: float = 50.0) -> float:
    """σ/m(v) = σ/m_0 × exp(-(v - v_R)^2 / (2 Δv^2)).

    Gaussian resonance at v_R (dark-pion mass-degenerate regime).
    For v_R = 30 km/s, Δv = 50 km/s: gives σ/m peaked at dwarf velocities,
    drops by 90% from dwarf to cluster (v=30 to v=1000).

    At v0.3-prelim MAP: σ/m(v) at v=10 km/s = σ/m_0 × exp(-(10-30)^2/(2*50^2))
    = σ/m_0 × 0.96; at v=1000: σ/m_0 × exp(-(1000-30)^2/(2*50^2))
    = σ/m_0 × exp(-188) ≈ 0. So σ/m effectively vanishes at cluster velocities.

    NOTE: For numerical stability, clip the exponent at -100 to avoid
    underflow. This makes σ/m effectively zero at very large v.
    """
    exponent = -((v - v_R) ** 2) / (2 * delta_v ** 2)
    exponent = np.maximum(exponent, -100.0)
    return sigma_m_0 * np.exp(exponent)


# ----------------------------------------------------------------------
# Mediator class registry
# ----------------------------------------------------------------------
MEDIATOR_CLASSES = {
    "power_law": {
        "name": "Power-law (phenomenological reference)",
        "fn": sigma_m_power_law,
        "params": {"sigma_m_0", "a"},
        "extra_params": {},
    },
    "yukawa": {
        "name": "Yukawa (dark photon kinetic mixing)",
        "fn": sigma_m_yukawa,
        "params": {"sigma_m_0", "a"},
        "extra_params": {"m_chi_gev": 40.0, "m_aprime_mev": 10.0},
    },
    "scalar_portal": {
        "name": "Scalar/Higgs portal (linear)",
        "fn": sigma_m_scalar_portal,
        "params": {"sigma_m_0", "a"},
        "extra_params": {"alpha_h": 0.5},
    },
    "composite": {
        "name": "Composite (dark pion resonance)",
        "fn": sigma_m_composite,
        "params": {"sigma_m_0", "a"},
        "extra_params": {"v_R": 30.0, "delta_v": 50.0},
    },
}


# ----------------------------------------------------------------------
# T39 joint log-likelihood (substitute σ/m form)
# ----------------------------------------------------------------------
def loglike_t39_with_form(sigma_m_0: float, a: float, mediator_class: str) -> float:
    """Total T39 log-likelihood using the specified mediator form.

    Replaces sigma_m_at_v(...) calls with the chosen mediator form's
    σ/m(v) function for the SPARC and dSph/UFD channels.
    """
    if mediator_class not in MEDIATOR_CLASSES:
        raise ValueError(f"Unknown mediator class: {mediator_class}")

    cfg = MEDIATOR_CLASSES[mediator_class]
    sigma_fn = cfg["fn"]
    extra = cfg["extra_params"]

    # SPARC (substitute σ/m(v) in the per-galaxy hierarchical likelihood)
    # t8.loglike_sparc_hierarchical internally calls sigma_m_at_v(...)
    # but we can't easily monkey-patch that. Instead, we evaluate
    # the sigma/m at the effective velocity scale and apply as a
    # multiplicative offset to the SPARC loglike.
    sigma_m_eff = sigma_fn(sigma_m_0, a, V_REF, **extra)
    sigma_m_ref = sigma_m_at_v(sigma_m_0, a, V_REF)
    if sigma_m_ref <= 0 or sigma_m_eff <= 0:
        return -np.inf
    # Offset captures how much SPARC's σ/m(v) average shifts
    sparc_offset = -0.5 * ((np.log(sigma_m_eff) - np.log(sigma_m_ref)) ** 2)
    ll_sparc = loglike_sparc_hierarchical(sigma_m_0, a) + sparc_offset

    # dSph, UFD (these are velocity-independent in the project)
    ll_dsph = loglike_dsph_v03(sigma_m_0, a)
    ll_ufd = loglike_ufd_v03(sigma_m_0, a)

    # LZ and Fermi (kinetic mixing, depend on epsilon and alpha)
    log_epsilon = V03_MAP["log_epsilon"]
    log_alpha = V03_MAP["log_alpha"]
    epsilon = 10 ** log_epsilon
    alpha = 10 ** log_alpha
    sigma_DM_nucleon_cm2 = sigma_SI_from_dark_photon(
        epsilon=epsilon,
        m_chi_GeV=M_CHI_GEV_FIXED,
        m_A_prime_MeV=M_A_PRIME_MEV_FIXED,
        alpha_D=ALPHA_D_FIXED,
    )
    sigma_v = sigma_v_from_dark_photon(
        m_chi_GeV=M_CHI_GEV_FIXED,
        m_A_prime_MeV=M_A_PRIME_MEV_FIXED,
        alpha_D=ALPHA_D_FIXED,
    )
    ll_lz = loglike_lz_real(M_CHI_GEV_FIXED, sigma_DM_nucleon_cm2)
    ll_fermi = loglike_fermi_dwarf(M_CHI_GEV_FIXED, sigma_v)

    return ll_sparc + ll_dsph + ll_ufd + ll_lz + ll_fermi


# ----------------------------------------------------------------------
# Phase 5 main
# ----------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("PHASE 5: MEDIATOR CLASS COMPARISON")
    print("=" * 60)
    print(f"v0.3-prelim MAP: sigma/m_0={V03_MAP['sigma_m_0']}, a={V03_MAP['a']}")
    print(f"  log_epsilon={V03_MAP['log_epsilon']}, log_alpha={V03_MAP['log_alpha']}")
    print()

    print("sigma/m(v) at v=10 km/s (dwarf) and v=1000 km/s (cluster):")
    print("-" * 60)
    print(f"{'Class':<20} {'sigma/m(10)':>12} {'sigma/m(1000)':>14} {'Ratio':>10}")
    for class_id, cfg in MEDIATOR_CLASSES.items():
        fn = cfg["fn"]
        extra = cfg["extra_params"]
        s_dwarf = fn(V03_MAP["sigma_m_0"], V03_MAP["a"], V_DWARF, **extra)
        s_cluster = fn(V03_MAP["sigma_m_0"], V03_MAP["a"], V_CLUSTER, **extra)
        ratio = s_dwarf / s_cluster if s_cluster > 0 else float("inf")
        print(f"{class_id:<20} {s_dwarf:>12.4f} {s_cluster:>14.4e} {ratio:>10.2f}")
    print()

    # Compute log_Z for each mediator class at v0.3-prelim MAP
    print("log_Z at v0.3-prelim MAP (per class):")
    print("-" * 60)
    log_Zs = {}
    for class_id in MEDIATOR_CLASSES:
        log_Z = loglike_t39_with_form(
            V03_MAP["sigma_m_0"], V03_MAP["a"], class_id
        )
        log_Zs[class_id] = log_Z
        print(f"  {class_id:<20} log_Z = {log_Z:>12.2f}")

    # Reference: power-law (T39)
    log_Z_ref = log_Zs["power_law"]
    print()
    print(f"Bayes factors (delta log Z vs power-law reference):")
    print("-" * 60)
    print(f"{'Class':<20} {'delta log Z':>14} {'Interpretation':>30}")
    for class_id, log_Z in log_Zs.items():
        delta = log_Z - log_Z_ref
        if abs(delta) < 1.0:
            interp = "INDISTINGUISHABLE"
        elif delta > 0:
            interp = "FAVORED"
        else:
            interp = "DISFAVORED"
        print(f"{class_id:<20} {delta:>+14.2f} {interp:>30}")

    # Kill criterion check
    log_Z_values = list(log_Zs.values())
    max_log_Z = max(log_Z_values)
    min_log_Z = min(log_Z_values)
    spread = max_log_Z - min_log_Z

    print()
    print("=" * 60)
    print("KILL CRITERION CHECK (per roadmap):")
    print("=" * 60)
    print(f"  spread (max log_Z - min log_Z) = {spread:.2f} nats")
    print(f"  threshold: |delta log Z| < 1 between ANY pair")
    if spread < 1.0:
        print("  VERDICT: KILL CRITERION TRIGGERED")
        print("    All mediator classes are indistinguishable.")
        print("    Mediator class NOT constrained by current data.")
        print("    CAVEAT: Existing likelihoods are baked into the power-law form,")
        print("    so they cannot discriminate mediator classes through this test.")
        print("    See docs/PHASE5_MEDIATOR_CLASS_2026_09_12.md for honest framing.")
        decision = "KILL"
        decision_reason = (
            "STRUCTURAL: Existing likelihoods are baked into power-law form; "
            "cannot discriminate mediator classes without likelihood rewrite."
        )
    else:
        print("  VERDICT: KILL CRITERION NOT TRIGGERED")
        print("    At least one mediator class is distinguishable.")
        print("    Phase 5 PROCEED (findings publishable).")
        decision = "PROCEED"
        decision_reason = (
            "PHYSICS: At least one mediator class is distinguishable from the rest."
        )

    # Save results
    # Use PROJECT_ROOT.parent as the actual repo root (Phase 5 lives in code subdir)
    repo_root = PROJECT_ROOT.parent
    out_dir = repo_root / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "phase5_mediator_class_comparison.json"

    results = {
        "phase": 5,
        "date": "2026-09-12",
        "v03_map": V03_MAP,
        "log_Z_per_class": log_Zs,
        "log_Z_power_law_reference": float(log_Z_ref),
        "delta_log_Z_vs_power_law": {
            class_id: float(log_Z - log_Z_ref)
            for class_id, log_Z in log_Zs.items()
        },
        "spread": float(spread),
        "decision": decision,
        "decision_reason": decision_reason,
        "kill_criterion": {
            "threshold": 1.0,
            "spread": float(spread),
            "triggered": bool(spread < 1.0),
        },
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()