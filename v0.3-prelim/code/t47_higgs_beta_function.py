"""
T47 — Mediator contribution to the SM Higgs quartic beta function.

Question: Does the dark-sector mediator (m_phi ~ 200 MeV, epsilon ~ 10^-48)
destabilize or stabilize the SM electroweak vacuum?

Background (SM Higgs vacuum stability):
  - The SM Higgs quartic lambda_H(M_Pl) is marginally negative when
    computed at NNLO with m_H = 125 GeV and m_t = 173 GeV.
  - This means the electroweak vacuum is METASTABLE at ~10^10 GeV.
  - Lifetime: longer than the age of the universe by ~10^600 (huge).
  - But the metastability is a 'delicate' situation — small perturbations
    from new physics can tip the balance.

Reference: Isidori, Ridolfi, Strumia 2001 (hep-ph/0104016)
           Bednyakov, Kniehl, Pikelner, Veretin 2015 (arXiv:1507.08833)

The mediator (dark photon A') contributes to lambda_H via:
  Method 1: Kinetic mixing portal
    The Lagrangian has -epsilon/2 * F^mu_nu * F'_mu_nu
    After diagonalization, the dark photon acquires a coupling to the
    SM Higgs via the field redefinition. This gives a contribution:
        delta_lambda_H ~ (e * epsilon)^2 * (m_A' / M_Pl)^2  (suppressed by epsilon^2)

  Method 2: Higgs portal (if mediator couples directly to |H|^2)
    delta_L = lambda_Hphi * |H|^2 * phi^2 / 2
    This gives delta_lambda_H ~ lambda_Hphi^2 / (16 pi^2) * log(M_UV / m_phi)

For our SIDM parameters (epsilon ~ 10^-48, g_chi ~ 0.5):
  Method 1: delta_lambda_H ~ (10^-48)^2 * (m_phi / M_Pl)^2 ~ 10^-114
  Method 2: If lambda_Hphi ~ g_chi^2 / 4 ~ 0.06 (Yukawa-like),
             delta_lambda_H ~ 0.06^2 / (16 pi^2) * log(M_Pl / m_phi)
                            ~ 10^-4 * 25 ~ 10^-3

Let me compute precisely.
"""
from __future__ import annotations
import json
import numpy as np
from pathlib import Path


RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# Standard Model parameters at M_Z
M_Z_GEV = 91.1876  # Z boson mass
M_H_GEV = 125.25   # Higgs mass
M_T_GEV = 172.69   # Top mass
V_H_GEV = 246.22   # Higgs VEV
ALPHA_EM = 1.0 / 127.9
ALPHA_S_MZ = 0.1179
G_GEV = 1.1663787e-5  # Fermi constant

# Couplings at M_Z
g_1 = np.sqrt(5/3) * np.sqrt(4 * np.pi * ALPHA_EM)  # U(1)_Y
g_2 = 2 * np.sqrt(G_GEV * M_Z_GEV**2 / np.sqrt(2))  # SU(2)_L
g_3 = np.sqrt(4 * np.pi * ALPHA_S_MZ)  # SU(3)_c
y_t = np.sqrt(2) * M_T_GEV / V_H_GEV  # top Yukawa

# Higgs quartic
lambda_H = M_H_GEV**2 / (2 * V_H_GEV**2)

# Planck scale
M_PLANCK_GEV = 1.2209e19  # GeV (reduced Planck)

# Loop factor (1/(16 pi^2))
LOOP = 1.0 / (16 * np.pi**2)


def beta_lambda_SM(lambda_H_val: float, y_t_val: float, g_1_val: float, g_2_val: float) -> float:
    """SM beta function for the Higgs quartic (1-loop, no mediator).

    d lambda_H / d ln mu = (1/(16 pi^2)) * [24 lambda_H^2 - 6 y_t^4
                                            + (3/8) (2 g_2^4 + (g_1^2 + g_2^2)^2)]

    Ref: Peskin & Schroeder 26.4; Machacek & Vaughn 1983.
    """
    return LOOP * (
        24 * lambda_H_val ** 2
        - 6 * y_t_val ** 4
        + (3.0 / 8.0) * (2 * g_2_val ** 4 + (g_1_val ** 2 + g_2_val ** 2) ** 2)
    )


def delta_lambda_H_kinetic_mixing(epsilon: float, m_phi_GeV: float,
                                    M_UV_GeV: float = M_PLANCK_GEV) -> float:
    """Mediator contribution to lambda_H via kinetic mixing portal.

    The dark photon A' acquires a coupling to the Higgs via field
    redefinition. The contribution to lambda_H is:
        delta_lambda_H ~ epsilon^2 * (m_phi / M_UV)^2

    This is the 'induced Higgs quartic' from the kinetic mixing in the
    mass eigenbasis. For us, M_UV = M_Pl (worst case).
    """
    return epsilon ** 2 * (m_phi_GeV / M_UV_GeV) ** 2


def delta_lambda_H_higgs_portal(lambda_Hphi: float, m_phi_GeV: float,
                                  M_UV_GeV: float = M_PLANCK_GEV) -> float:
    """Mediator contribution to lambda_H via Higgs portal coupling.

    If the dark sector has a direct coupling |H|^2 phi^2, the RG running
    gives:
        delta_lambda_H ~ lambda_Hphi^2 / (16 pi^2) * log(M_UV / m_phi)

    For the SIDM model, lambda_Hphi ~ g_chi^2 / 4 (Yukawa-like).
    """
    return lambda_Hphi ** 2 * LOOP * np.log(M_UV_GeV / m_phi_GeV)


def delta_lambda_H_dark_yukawa(g_chi: float, m_phi_GeV: float,
                                  M_UV_GeV: float = M_PLANCK_GEV) -> float:
    """Mediator contribution to lambda_H via dark Yukawa coupling.

    If the dark sector has dark fermions (chi) with Yukawa coupling
    lambda_dark = g_chi, the dark fermion loop contributes:
        delta_lambda_H ~ g_chi^4 / (16 pi^2) * log(M_UV / m_phi)

    This is analogous to the top-quark contribution to lambda_H.
    """
    return g_chi ** 4 * LOOP * np.log(M_UV_GeV / m_phi_GeV)


def run_lambda_H_to_planck(lambda_H_MZ: float, n_steps: int = 1000) -> dict:
    """Run lambda_H from M_Z to M_Pl using the SM-only beta function.

    Returns the value at M_Pl and a few intermediate values.
    """
    mu = np.log(M_Z_GEV)
    mu_final = np.log(M_PLANCK_GEV)
    d_mu = (mu_final - mu) / n_steps

    # RG running (1-loop, SM-only)
    mu_arr = [mu]
    lambda_arr = [lambda_H_MZ]
    y_t_arr = [y_t]
    g_1_arr = [g_1]
    g_2_arr = [g_2]

    # Also run g_1, g_2, y_t approximately
    # 1-loop beta functions:
    # beta_g_1 = (1/(16 pi^2)) * (41/10) g_1^3
    # beta_g_2 = (1/(16 pi^2)) * (-19/6) g_2^3
    # beta_y_t = (1/(16 pi^2)) * y_t (9/2 y_t^2 - 8 g_3^2 - 9/4 g_2^2 - 17/20 g_1^2)
    # For simplicity, assume g_1, g_2, y_t change slowly (rough approx)

    for i in range(n_steps):
        l = lambda_arr[-1]
        yt = y_t_arr[-1]
        g1 = g_1_arr[-1]
        g2 = g_2_arr[-1]

        # Update lambda_H
        dl = beta_lambda_SM(l, yt, g1, g2) * d_mu
        lambda_arr.append(l + dl)

        # Update g_1, g_2, y_t (1-loop)
        dg1 = LOOP * (41.0/10) * g1 ** 3 * d_mu
        dg2 = LOOP * (-19.0/6) * g2 ** 3 * d_mu
        # y_t - assume 8 g_3^2 dominates (g_3 ~ 1.2 at M_Z, but ~0.5 at M_Pl)
        # for simplicity, use the dominant running
        g3 = 1.2 * np.exp(-LOOP * 7 * (mu_arr[-1] - mu))  # g_3 evolves
        dyt = LOOP * yt * (9.0/2 * yt**2 - 8 * g3**2 - 9.0/4 * g2**2 - 17.0/20 * g1**2) * d_mu
        g_1_arr.append(g1 + dg1)
        g_2_arr.append(g2 + dg2)
        y_t_arr.append(yt + dyt)
        mu_arr.append(mu_arr[-1] + d_mu)

    final_lambda_Pl = lambda_arr[-1]
    return {
        "lambda_H_at_MZ": lambda_H_MZ,
        "lambda_H_at_M_Pl": final_lambda_Pl,
        "n_steps": n_steps,
        "mu_arr": np.exp(mu_arr[::n_steps//10]).tolist(),
        "lambda_arr": lambda_arr[::n_steps//10],
    }


def compute_full_rg() -> dict:
    """Compute the full RGE including mediator contributions."""
    result = {}
    result["m_H_GeV"] = M_H_GEV
    result["lambda_H_at_MZ"] = lambda_H
    result["g_1_MZ"] = g_1
    result["g_2_MZ"] = g_2
    result["y_t_MZ"] = y_t
    result["alpha_EM_inv"] = 1.0 / ALPHA_EM
    result["M_Pl_GeV"] = M_PLANCK_GEV

    # Run SM-only first
    sm_run = run_lambda_H_to_planck(lambda_H)
    result["sm_only_at_M_Pl"] = sm_run["lambda_H_at_M_Pl"]

    # Mediator scenarios (T46 best fit parameters)
    m_phi_MeV = 1795.0  # from T46 MAP
    m_phi_GeV = m_phi_MeV / 1000.0
    g_chi = 0.46
    epsilon = 1e-48  # T46 predicted

    # Method 1: kinetic mixing
    delta_lam_1 = delta_lambda_H_kinetic_mixing(epsilon, m_phi_GeV)
    result["delta_lambda_H_kinetic_mixing"] = delta_lam_1

    # Method 2: Higgs portal (if exists)
    lambda_Hphi = g_chi ** 2 / 4.0  # Yukawa-like
    delta_lam_2 = delta_lambda_H_higgs_portal(lambda_Hphi, m_phi_GeV)
    result["delta_lambda_H_higgs_portal"] = delta_lam_2

    # Method 3: dark Yukawa
    delta_lam_3 = delta_lambda_H_dark_yukawa(g_chi, m_phi_GeV)
    result["delta_lambda_H_dark_yukawa"] = delta_lam_3

    # Total delta_lambda_H (sum of contributions)
    delta_lam_total = delta_lam_1 + delta_lam_2 + delta_lam_3
    result["delta_lambda_H_total"] = delta_lam_total

    # Comparison: SM lambda_H at M_Pl is ~ -0.01 (metastable)
    # The mediator's contribution is much smaller than the SM correction terms
    sm_lambda_Pl = sm_run["lambda_H_at_M_Pl"]
    relative_correction = abs(delta_lam_total / sm_lambda_Pl) if sm_lambda_Pl != 0 else 0
    result["sm_lambda_H_at_M_Pl"] = sm_lambda_Pl
    result["relative_correction"] = relative_correction

    # Verdict
    if relative_correction < 1e-6:
        verdict = "NEGLIGIBLE: mediator does NOT affect SM vacuum stability"
    elif relative_correction < 1e-3:
        verdict = "MARGINAL: small correction, would need precision to detect"
    else:
        verdict = "SIGNIFICANT: mediator could affect SM vacuum stability"
    result["verdict"] = verdict

    return result


if __name__ == "__main__":
    print("=" * 80)
    print("T47 — Mediator contribution to SM Higgs quartic beta function")
    print("=" * 80)

    result = compute_full_rg()

    print(f"\nSM parameters at M_Z:")
    print(f"  m_H = {result['m_H_GeV']:.2f} GeV")
    print(f"  lambda_H(M_Z) = {result['lambda_H_at_MZ']:.4f}")
    print(f"  g_1 = {result['g_1_MZ']:.4f}")
    print(f"  g_2 = {result['g_2_MZ']:.4f}")
    print(f"  y_t = {result['y_t_MZ']:.4f}")
    print(f"  1/alpha_EM = {result['alpha_EM_inv']:.1f}")

    print(f"\nRG running (SM-only):")
    print(f"  lambda_H(M_Pl) = {result['sm_lambda_H_at_M_Pl']:.6f}")
    print(f"  (For reference: SM value at M_Pl is ~ -0.01 in the literature)")

    print(f"\nMediator contributions (T46 MAP: m_phi = 1795 MeV, g_chi = 0.46, eps = 1e-48):")
    print(f"  Method 1 (kinetic mixing): delta_lambda_H = {result['delta_lambda_H_kinetic_mixing']:.3e}")
    print(f"  Method 2 (Higgs portal):   delta_lambda_H = {result['delta_lambda_H_higgs_portal']:.3e}")
    print(f"  Method 3 (dark Yukawa):    delta_lambda_H = {result['delta_lambda_H_dark_yukawa']:.3e}")
    print(f"  TOTAL: delta_lambda_H = {result['delta_lambda_H_total']:.3e}")

    print(f"\nRelative correction to SM lambda_H at M_Pl:")
    print(f"  |delta_lambda / lambda_H_SM| = {result['relative_correction']:.3e}")
    print(f"\nVERDICT: {result['verdict']}")

    # Write result
    out_path = RESULTS_DIR / "t47_higgs_beta_function.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t47_higgs_beta_function.json")
    win_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")
