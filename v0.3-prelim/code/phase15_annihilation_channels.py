"""
Phase 15 — Probe: Can g_D exceed 0.16 with alternate annihilation channels?

The Fermi dwarf limit (σv < 5×10⁻²⁶ cm³/s for bb̄) forces g_D ≤ 0.16
in our pipeline. Question: if Majorana χ annihilates through a different
final state (ττ, μμ, e+e-, light quarks) does the limit relax enough
to allow g_D ~ 0.5-0.7 (the SIDM-required value)?

Method:
  Compute σv for χχ → XX at v_rel ~ 10⁻³ c (freeze-out) for each
  final state. Compare to Fermi upper limit for that channel.
  Return the maximum g_D that satisfies the limit per channel.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

M_CHI_GEV = 45.0
M_A_PRIME_MEV = 200.0
N_A = 6.022e23  # Avogadro

# Fermi dwarf upper limits (Approx, 95% C.L., integrated over solid angle)
# These are conservative channel-by-channel limits for dwarf galaxies
# from Ackermann+ 2015 / Albert+ 2017
FERMI_LIMITS = {
    "e+e-":  3e-26,    # very constraining
    "μ+μ-":  5e-26,
    "τ+τ-":  5e-26,    # same as muons
    "uu":    1e-25,
    "dd":    1e-25,
    "ss":    1e-25,
    "cc":    1e-25,
    "bb":    5e-26,    # used in our pipeline
    "tt":    1e-23,    # not relevant for m_chi = 45 GeV
    "gg":    1e-25,    # loop-induced
    "WW":    1e-25,    # kinematic threshold m_chi > m_W
    "ZZ":    1e-25,
    "hh":    1e-25,    # Higgs
    "νν":    1e-25,    # weakly constrained
}


def sigma_v_xx_cm3_per_s(g_D: float, channel: str) -> float:
    """
    σv for χχ → XX via dark photon (s-channel) at v_rel ~ 10⁻³ c.

    σv = (g_D⁴ / 32π m_χ²) × β_f × S_sommerfeld × BR(XX)

    For Majorana χ, σv scales as g_D⁴ (with helicity suppression factors).
    """
    m_chi_GeV = M_CHI_GEV
    g_chi = g_D  # dark coupling
    alpha_D = g_chi**2 / (4 * np.pi)

    # Threshold factor: 0 if channel mass > m_chi
    channel_masses = {
        "e+e-": 0.000511, "μ+μ-": 0.1057, "τ+τ-": 1.777,
        "uu": 0.0023, "dd": 0.0048, "ss": 0.095, "cc": 1.27, "bb": 4.18,
        "tt": 173.0, "gg": 0.0, "WW": 80.4, "ZZ": 91.2, "hh": 125.0, "νν": 0.0,
    }
    if channel_masses.get(channel, 1e10) > m_chi_GeV:
        return 0.0

    # Phase space: β_f = sqrt(1 - m_X²/m_χ²)
    m_X = channel_masses[channel]
    if m_X == 0:
        beta_f = 1.0
    else:
        beta_f = np.sqrt(1 - (m_X / m_chi_GeV)**2)

    # Cross-section prefactor (Born, s-channel dark photon)
    # σv ∝ g_D⁴ × β_f × 1/m_χ²
    prefactor = g_chi**4 / (32 * np.pi * m_chi_GeV**2)
    # Convert from natural units (GeV^-2) to cm³/s using 1 GeV^-2 = 0.3894e-27 cm²
    # and c = 3e10 cm/s
    GeV2_to_cm3_per_s = 0.3894e-27 * 3e10  # ≈ 1.17e-17
    sigma_v = prefactor * beta_f * GeV2_to_cm3_per_s

    # Sommerfeld boost (rough estimate for m_A' = 200 MeV, v_rel ~ 10⁻³ c)
    # eps_v = m_A' / (m_chi * v) = 0.2 / (45 * 0.001) = 4.4 (BORN regime, S~1)
    eps_v = M_A_PRIME_MEV / (M_CHI_GEV * 1e3 * 0.001)
    if eps_v < 1:
        S_sommerfeld = 1.0 / eps_v  # Coulomb regime
    else:
        S_sommerfeld = 1.0  # Born regime (no enhancement)

    sigma_v *= S_sommerfeld
    return float(sigma_v)


def find_max_gD(channel: str, sigma_v_limit: float) -> float:
    """Find g_D such that σv(g_D) = sigma_v_limit."""
    g_low, g_high = 1e-4, 5.0
    for _ in range(60):
        g_mid = 0.5 * (g_low + g_high)
        if sigma_v_xx_cm3_per_s(g_mid, channel) > sigma_v_limit:
            g_high = g_mid
        else:
            g_low = g_mid
    return 0.5 * (g_low + g_high)


def main():
    print("=" * 80)
    print("Phase 15 — Probe: g_D limit per annihilation channel")
    print("=" * 80)
    print(f"Majorana χ with m_chi = {M_CHI_GEV} GeV, m_A' = {M_A_PRIME_MEV} MeV")
    print(f"SIDM requires g_D ~ 0.7; current pipeline uses bb̄ with g_D ≤ 0.16")
    print()

    out = {"test": "Phase15_annihilation_channels",
           "direction": "Find max g_D per annihilation channel"}

    results = {}
    for ch, sigma_v_limit in FERMI_LIMITS.items():
        g_max = find_max_gD(ch, sigma_v_limit)
        sv_at_target = sigma_v_xx_cm3_per_s(0.7, ch)
        sv_at_pipeline = sigma_v_xx_cm3_per_s(0.16, ch)
        verdict = ("OK" if g_max >= 0.7 else
                   "RELAXED" if g_max >= 0.3 else
                   "CONSTRAINED")
        results[ch] = {
            "fermi_limit": sigma_v_limit,
            "g_D_max": g_max,
            "sigma_v_at_gD_0.7": sv_at_target,
            "sigma_v_at_gD_0.16": sv_at_pipeline,
            "verdict": verdict,
        }
        print(f"  {ch:<8} Fermi limit = {sigma_v_limit:.1e} cm³/s, g_D_max = {g_max:.3f} ({verdict})")

    # Identify the most relaxed channel
    best_ch = max(results.keys(), key=lambda c: results[c]["g_D_max"])
    print()
    print(f"Most relaxed channel: {best_ch}, g_D_max = {results[best_ch]['g_D_max']:.3f}")
    print(f"Required for SIDM: g_D ~ 0.7")
    if results[best_ch]["g_D_max"] >= 0.7:
        print("→ Switching to {best_ch} WOULD allow SIDM-required g_D ~ 0.7")
    else:
        print("→ Even most relaxed channel does NOT allow g_D ~ 0.7")
        print("  This is a STRUCTURAL Fermi limit on the model")

    out["results"] = results
    out["best_channel"] = best_ch
    out["best_g_D_max"] = results[best_ch]["g_D_max"]
    out["verdict"] = ("SWITCH_CHANNEL_OK" if results[best_ch]["g_D_max"] >= 0.7
                      else "FERMI_LIMIT_STRUCTURAL")

    out_path = RESULTS_DIR / "phase15_annihilation_channels.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
