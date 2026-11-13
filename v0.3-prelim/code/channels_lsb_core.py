"""LSB core check — low-surface-brightness core-formation / core-collapse test.

Purpose
-------
Independent check of the v19.2-F mediator cross-section model against
LOW-SURFACE-BRIGHTNESS (LSB) galaxy dark-matter cores.  LSBs are the cleanest
test bed because their baryons barely affect the halo, so a measured core is
almost purely a dark-matter statement.

Two published LSB tests are implemented, both gravothermal:

  (A) CORE-COLLAPSIBILITY (usable constraint, UPPER bound on sigma/m)
      Sanchez-Salcedo, Melnick & Vega 2005, astro-ph/0506345 (ApJ 626, 173),
      NGC 5963.  Read end-to-end from the primary PDF on 2026-11-13; PDF is
      in docs/papers/verified/.  The paper uses the SAME velocity convention
      as this repo: sigma_dm = sigma_0 * (v0 / v_rel)^a with v0 = 100 km/s
      (= scripts/constants.V_REF_KMS).
        * core-collapse time      t_rc = 0.8 Gyr * (sigma_0 / 1 cm^2 g^-1)^-1
        * requires t_rc > 1 Hubble time  ->  sigma_0 <~ 0.08 cm^2 g^-1
        * independent core-size / central-density fit -> sigma_0 <~ 0.2 cm^2 g^-1
          at 95% CL, tightest ~0.1 cm^2 g^-1 for Upsilon* = 1.2; the authors
          note the limit "may be overestimated by as much as a factor 2".
      Implemented as loglike_lsb_ngc5963_core().

  (B) CORE-FORMATION TIMESCALE (DIAGNOSTIC ONLY — see warning)
      Kitazawa 2026, arXiv:2605.05588, five field LSBGs from the Di Paolo,
      Salucci & Erkurt 2019 URC-LSBG IV sample (H I: de Blok, McGaugh &
      van der Hulst 1996).
        t_r,0 = 1 / (a * rho_s * nu_s * sigma),  a = sqrt(16/pi)
        nu_s  = sqrt(4 pi G rho_s r_s^2)
        core forms at t = 30 t_r,0  (paper's t_core);  collapse at ~450 t_r,0
      WARNING (found by reproduce_kitazawa_table(), 2026-11-13): recomputing
      the paper's own equations from its own Table 1 parameters gives
      t_core values ~1.0e3 x LARGER than the paper's printed Tables 2-7
      (ratio 999-1062 on 5/5 objects at both sigma = 1 and 0.1 cm^2 g^-1).
      ADJUDICATED 2026-11-13 without contacting the author (see
      kitazawa_unit_adjudication()): the printed column reproduces eq. (11)-(12)
      halo-by-halo once multiplied by 1e3 (4-6% residual), i.e. the author's
      arithmetic matches his stated equations and only the TIME COLUMN is 1e3
      low.  A kpc^3 <-> pc^3 slip is ruled out (that would be 1e9, and the NFW
      mass integral confirms rho_s is per kpc^3 in all 15 rows).  Cross-checked
      against Yang+ 2024 eq. 2.2 (gravothermal_yang2024.collapse_time_SI_gyr),
      whose halo scaling is identical (ratio 8.46 on all five halos) and whose
      own BM2 calibration halo it reproduces at 28.70 Gyr vs the published 28.7.
      This repo's Balberg+ 2002 convention (gravothermal.py,
      t_core = 12.7 / sigma_m * (rho_s / 1e7 M_sun kpc^-3)^-1 * t_dyn) gives
      7.0 Gyr for the same five halos.  The four published conventions span
      0.3 -> 13,800 Gyr for the same halos, which is why no LSB core-formation
      timescale can pin sigma/m at these densities.
      Consequence: these LSBs do NOT support the paper's headline claim
      ("sigma/m ~ 0.1 favoured, 1 excluded"); correctly evaluated they require
      sigma/m >> 1 to form cores within a Hubble time.  Because a broken
      number is worse than no number, this half is exposed as a diagnostic
      only and is NOT wired into any likelihood.

Both halves use the repo's own velocity mapping from mediator_registry, so the
composite mediator / form-factor / thermal classes are treated correctly rather
than being folded into a single power law.

Conventions
-----------
* sigma_m_0, a          : the repo's 2-parameter fit; sigma/m quoted at
                          V_REF = 100 km/s.
* sigma_m_at_v(...)     : mediator_registry velocity mapping, mediator-class
                          aware.
* One-sided likelihoods: CDM (sigma -> 0) receives ZERO penalty, because CDM
                          produces no SIDM core collapse.  A test that punished
                          sigma -> 0 would be a one-way SIDM cheerleader.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# sys.path bootstrap (matches tests/test_long_term_5_and_3.py)
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_PRELIM = _HERE.parent.parent          # repo root
for _p in (_HERE, _HERE.parent, _PRELIM,
           _PRELIM / "v0.1-prelim" / "code"):   # halo_profiles.py lives here
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from mediator_registry import sigma_m_at_v  # noqa: E402

# ---------------------------------------------------------------------------
# Units / physical constants (CGS unless stated)
# ---------------------------------------------------------------------------
G_CGS = 6.674e-8          # cm^3 g^-1 s^-2
MSUN_G = 1.989e33         # g
KPC_CM = 3.086e21         # cm
YR_S = 3.156e7            # s
GYR_S = 1e9 * YR_S
HUBBLE_TIME_GYR = 13.8    # Planck 2018, used for the collapse-lifetime test

A_HARD = math.sqrt(16.0 / math.pi)   # Kitazawa eq (5); hard-sphere factor ~2.257
KPC3_TO_CM3 = KPC_CM ** 3

# Kitazawa's "core has formed" criterion (paper defines t_core = 30 t_r,0)
KITAZAWA_CORE_RELAXATIONS = 30.0
# Kitazawa's adopted lookback to the LSB proto-cluster epoch
KITAZAWA_AGE_GYR = 11.0

# ---------------------------------------------------------------------------
# (A) NGC 5963 — Sanchez-Salcedo, Melnick & Vega 2005 (VERIFIED, primary PDF)
# ---------------------------------------------------------------------------
NGC5963_V_KMS = 150.0        # characteristic collision velocity quoted in S05
NGC5963_TRC_GYR_PER_CM2G = 0.8   # t_rc = 0.8 Gyr / (sigma_0 / 1 cm^2 g^-1)
NGC5963_SIGMA_LIMIT_CM2G = 0.2   # 95% CL upper limit (conservative; S05 sec 4.1)
NGC5963_SIGMA_LIMIT_TIGHT = 0.1  # Upsilon* = 1.2 core-size fit
NGC5963_SIGMA_CC_LIMIT = 0.08    # core-collapse / halo-lifetime limit, Upsilon*=1.2
NGC5963_LOG_WIDTH = 0.4          # soft window in ln(sigma): ~+/-50% tolerance
# Observed decompressed halo parameters (S05 Table 1, Upsilon* = 1.2 row)
NGC5963_C_NFW = 15.6
NGC5963_V200_KMS = 109.0
NGC5963_R_CORE_KPC = 0.42        # isothermal-sphere fit core radius
NGC5963_RHO0_MSUN_PC3 = 1.75     # isothermal-sphere fit central density

# ---------------------------------------------------------------------------
# (B) Kitazawa+ 2026 five field LSBGs (arXiv:2605.05588 Table 1)
#     rho_s / r_s are the NFW scale parameters for the fiducial proto-cluster
#     scenario; printed t_core values kept for the reproduction audit.
# ---------------------------------------------------------------------------
KITAZAWA_LSB_TABLE = (
    # name,      log10 M_dyn, R_c kpc, r_s kpc, rho_s Msun/kpc^3, t_core paper (sig=1, 0.1)
    ("F561-1",   9.66, 25.0,  6.2, 1.8e6, 0.54, 5.40),
    ("F563-V1",  9.00, 14.0,  3.9, 1.8e6, 0.87, 8.70),
    ("F571-V1", 10.13, 21.0, 11.0, 1.8e6, 0.30, 3.00),
    ("F574-1", 10.43, 34.0, 13.0, 1.8e6, 0.27, 2.70),
    ("F574-2",  9.50, 33.0,  4.9, 1.8e6, 0.69, 6.90),
)

# Kitazawa's printed conclusion, kept as metadata so the audit is legible.
KITAZAWA_PRINTED_CLAIM = "sigma/m = 1 cm^2 g^-1 excluded; sigma/m ~ 0.1 favoured"


# ---------------------------------------------------------------------------
# Core physics helpers
# ---------------------------------------------------------------------------
def rho_s_cgs(rho_s_msun_kpc3: float) -> float:
    """NFW scale density, M_sun kpc^-3 -> g cm^-3."""
    return rho_s_msun_kpc3 * MSUN_G / KPC3_TO_CM3


def nu_s_kms(rho_s_msun_kpc3: float, r_s_kpc: float) -> float:
    """Kitazawa eq (12): nu_s = sqrt(4 pi G rho_s r_s^2), returned in km/s."""
    rho = rho_s_cgs(rho_s_msun_kpc3)
    r_cm = r_s_kpc * KPC_CM
    return math.sqrt(4.0 * math.pi * G_CGS * rho) * r_cm / 1.0e5


def t_r0_gyr(sigma_m_cm2_g: float, rho_s_msun_kpc3: float, r_s_kpc: float) -> float:
    """Kitazawa eq (11): relaxation time t_r,0 = 1 / (a rho_s nu_s sigma), in Gyr.

    sigma_m_cm2_g is the cross-section PER UNIT MASS (cm^2 g^-1) evaluated at
    the halo's own velocity; a = sqrt(16/pi) (hard spheres).
    """
    if sigma_m_cm2_g <= 0.0:
        return float("inf")
    rho = rho_s_cgs(rho_s_msun_kpc3)
    nu = nu_s_kms(rho_s_msun_kpc3, r_s_kpc) * 1.0e5      # cm/s
    return 1.0 / (A_HARD * rho * nu * sigma_m_cm2_g) / GYR_S


def t_core_form_gyr(sigma_m_cm2_g: float, rho_s_msun_kpc3: float, r_s_kpc: float) -> float:
    """Kitazawa eq (7): core-formation time t_core = 30 t_r,0, in Gyr."""
    return KITAZAWA_CORE_RELAXATIONS * t_r0_gyr(sigma_m_cm2_g, rho_s_msun_kpc3, r_s_kpc)


def sigma_min_for_core_formation(
    rho_s_msun_kpc3: float,
    r_s_kpc: float,
    age_gyr: float = KITAZAWA_AGE_GYR,
    n_relaxations: float = KITAZAWA_CORE_RELAXATIONS,
) -> float:
    """Invert t_core = n * t_r,0 <= age: minimum sigma/m (cm^2 g^-1) that forms a
    core inside `age_gyr` for this halo.  Returns +inf for age <= 0."""
    if age_gyr <= 0.0:
        return float("inf")
    rho = rho_s_cgs(rho_s_msun_kpc3)
    nu = nu_s_kms(rho_s_msun_kpc3, r_s_kpc) * 1.0e5
    return 1.0 / (A_HARD * rho * nu * (age_gyr / n_relaxations) * GYR_S)


def nfw_mass_within_msun(rho_s_msun_kpc3: float, r_s_kpc: float, r_kpc: float) -> float:
    """NFW enclosed mass M(<r) = 4 pi rho_s r_s^3 [ln(1+x) - x/(1+x)], x = r/r_s.

    Used only as an independent self-consistency check of the catalogue
    parameters against the papers' quoted dynamical masses.
    """
    x = r_kpc / r_s_kpc
    return 4.0 * math.pi * rho_s_msun_kpc3 * r_s_kpc ** 3 * (math.log1p(x) - x / (1.0 + x))


def ngc5963_trc_gyr(sigma_at_v_cm2_g: float) -> float:
    """S05 eq (7): core-collapse time for the NGC 5963 decompressed NFW halo."""
    if sigma_at_v_cm2_g <= 0.0:
        return float("inf")
    return NGC5963_TRC_GYR_PER_CM2G / sigma_at_v_cm2_g


# ---------------------------------------------------------------------------
# (A) Usable likelihood: NGC 5963 core-collapsibility
# ---------------------------------------------------------------------------
def loglike_lsb_ngc5963_core(
    sigma_m_0: float,
    a: float,
    mediator_class: str = "power_law",
    sigma_limit_cm2_g: float = NGC5963_SIGMA_LIMIT_CM2G,
    log_width: float = NGC5963_LOG_WIDTH,
) -> dict:
    """One-sided upper-limit likelihood from NGC 5963 (Sanchez-Salcedo+ 2005).

    NGC 5963's core is small (r_c ~ 0.42 kpc) and dense (rho_0 ~ 1.75
    M_sun pc^-3), so S05 conclude sigma/m at the halo's own collision velocity
    (v ~ 150 km/s) must stay below ~0.2 cm^2 g^-1 or the halo would have
    gravothermally collapsed within a Hubble time.

    Returns loglike = 0 for sigma_eff <= limit (no penalty, CDM included),
    and -0.5 * (ln(sigma_eff / limit) / log_width)^2 above it.  Soft and
    continuous, scale-free in log space, and never rewards larger sigma/m.
    """
    sigma_eff = float(sigma_m_at_v(sigma_m_0, a, NGC5963_V_KMS,
                                   mediator_class=mediator_class))
    if sigma_eff <= 0.0:
        return {
            "loglike": 0.0,
            "metadata": {
                "channel": "lsb_ngc5963_core",
                "sigma_eff_cm2_g": 0.0,
                "v_kms": NGC5963_V_KMS,
                "limit_cm2_g": sigma_limit_cm2_g,
                "trc_gyr": float("inf"),
                "penalised": False,
            },
        }
    if sigma_eff <= sigma_limit_cm2_g:
        return {
            "loglike": 0.0,
            "metadata": {
                "channel": "lsb_ngc5963_core",
                "sigma_eff_cm2_g": sigma_eff,
                "v_kms": NGC5963_V_KMS,
                "limit_cm2_g": sigma_limit_cm2_g,
                "trc_gyr": ngc5963_trc_gyr(sigma_eff),
                "penalised": False,
            },
        }
    dln = math.log(sigma_eff / sigma_limit_cm2_g)
    return {
        "loglike": -0.5 * (dln / log_width) ** 2,
        "metadata": {
            "channel": "lsb_ngc5963_core",
            "sigma_eff_cm2_g": sigma_eff,
            "v_kms": NGC5963_V_KMS,
            "limit_cm2_g": sigma_limit_cm2_g,
            "trc_gyr": ngc5963_trc_gyr(sigma_eff),
            "penalised": True,
            "sigma_m0_implied_limit": _invert_sigma_m0(
                sigma_limit_cm2_g, a, mediator_class, NGC5963_V_KMS),
        },
    }


def _invert_sigma_m0(sigma_target: float, a: float, mediator_class: str, v_kms: float) -> float:
    """Largest sigma_m_0 whose sigma/m_eff at v_kms still equals sigma_target."""
    lo, hi = 0.0, max(10.0, sigma_target)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if float(sigma_m_at_v(mid, a, v_kms, mediator_class=mediator_class)) < sigma_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# (B) Diagnostic only: Kitazawa LSB core-formation timescales
# ---------------------------------------------------------------------------
def kitazawa_lsb_rows(
    sigma_m_0: float,
    a: float,
    mediator_class: str = "power_law",
    age_gyr: float = KITAZAWA_AGE_GYR,
) -> list[dict]:
    """Per-LSB core-formation check at the model's own sigma/m for each halo.

    Each row carries: halo velocity nu_s, sigma/m_eff evaluated at nu_s, the
    recomputed t_core, the sigma/m required to form a core within age_gyr, the
    repo-internal gravothermal.py timescale for the same halo, and a verdict.
    """
    from gravothermal import gravothermal_r_core  # noqa: PLC0415

    rows = []
    for name, log_m, r_c, r_s, rho_s, _t1, _t01 in KITAZAWA_LSB_TABLE:
        nu = nu_s_kms(rho_s, r_s)
        sigma_eff = float(sigma_m_at_v(sigma_m_0, a, nu, mediator_class=mediator_class))
        t_core = t_core_form_gyr(sigma_eff if sigma_eff > 0 else 1e-30, rho_s, r_s)
        t_core_sig1 = t_core_form_gyr(1.0, rho_s, r_s)
        t_core_sig01 = t_core_form_gyr(0.1, rho_s, r_s)
        sigma_req = sigma_min_for_core_formation(rho_s, r_s, age_gyr)
        mass_check = nfw_mass_within_msun(rho_s, r_s, r_c)
        # Repo-internal cross-check: gravothermal.py is Balberg+2002-calibrated
        # and is the codebase's own timescale, so run the same halo through it.
        r_core_repo = float(gravothermal_r_core(
            sigma_eff if sigma_eff > 0 else 1e-30, rho_s, r_s,
            v_max=nu, t_Gyr=age_gyr))
        rows.append({
            "name": name,
            "log10_mdyn": log_m,
            "r_c_kpc": r_c,
            "r_s_kpc": r_s,
            "rho_s_msun_kpc3": rho_s,
            "nu_s_kms": nu,
            "sigma_eff_cm2_g": sigma_eff,
            "t_core_gyr": t_core,
            "t_core_gyr_at_sigma_1": t_core_sig1,
            "t_core_gyr_at_sigma_0p1": t_core_sig01,
            "sigma_required_cm2_g": sigma_req,
            "forms_core_in_age": bool(t_core <= age_gyr),
            "m_dyn_from_params_msun": mass_check,
            "m_dyn_from_paper_msun": 10.0 ** log_m,
            "repo_r_core_pred_kpc": r_core_repo,
            "repo_phase": "collapsed" if r_core_repo <= 0.06 else "expanded",
        })
    return rows


def reproduce_kitazawa_table() -> list[dict]:
    """Audit the paper's printed t_core values against its own equations.

    Recomputes t_core = 30 t_r,0 from the paper's own Table 1 parameters at
    sigma/m = 1 and 0.1 cm^2 g^-1 and reports the ratio to the printed value.
    A ratio of 1 would confirm the published table.
    """
    rows = []
    for name, _log_m, _r_c, r_s, rho_s, t1_printed, t01_printed in KITAZAWA_LSB_TABLE:
        t1_calc = t_core_form_gyr(1.0, rho_s, r_s)
        t01_calc = t_core_form_gyr(0.1, rho_s, r_s)
        rows.append({
            "name": name,
            "nu_s_kms": nu_s_kms(rho_s, r_s),
            "sigma_1": {"printed_Gyr": t1_printed, "recomputed_Gyr": t1_calc,
                        "ratio_calc_over_printed": t1_calc / t1_printed},
            "sigma_0p1": {"printed_Gyr": t01_printed, "recomputed_Gyr": t01_calc,
                          "ratio_calc_over_printed": t01_calc / t01_printed},
        })
    return rows


# ---------------------------------------------------------------------------
# (B2) Kitazawa+2026's other two proto-cluster scenarios (paper Tables 4-7)
#      The paper runs THREE initial conditions, labelled by its 'A' column
#      (A = 100 / 10 / 5), each with a sigma = 1 and a sigma = 0.1 table.
#      Carrying all six makes the ~1e3 discrepancy test independent of which
#      table you look at.
#      rows: (name, r_s kpc, rho_s Msun/kpc^3, printed t_core sig=1, sig=0.1)
# ---------------------------------------------------------------------------
KITAZAWA_SCENARIOS = (
    {"label": "z=2.45 (A=100)", "A": 100.0, "age_gyr": KITAZAWA_AGE_GYR,
     "rows": tuple((n, r_s, rho_s, t1, t01)
                   for (n, _lm, _rc, r_s, rho_s, t1, t01) in KITAZAWA_LSB_TABLE)},
    {"label": "z=7.66 (A=10)", "A": 10.0, "age_gyr": 13.0, "rows": (
        ("F561-1", 7.3, 1.3e6, 0.76, 7.6),
        ("F563-V1", 4.5, 1.3e6, 1.20, 12.0),
        ("F571-V1", 13.0, 1.3e6, 0.41, 4.1),
        ("F574-1", 15.0, 1.3e6, 0.37, 3.7),
        ("F574-2", 5.6, 1.3e6, 0.99, 9.9),
    )},
    {"label": "z=7.88 (A=5)", "A": 5.0, "age_gyr": 13.0, "rows": (
        ("F561-1", 4.7, 3.6e6, 0.27, 2.7),
        ("F563-V1", 2.9, 3.6e6, 0.44, 4.4),
        ("F571-V1", 8.2, 3.6e6, 0.15, 1.5),
        ("F574-1", 9.3, 3.6e6, 0.14, 1.4),
        ("F574-2", 3.7, 3.6e6, 0.34, 3.4),
    )},
)

# The paper's own thresholds (Sec. 2): the core-like profile is stable up to
# ~8 t_core, and collapse sets in at ~450 t_r,0 = 15 t_core.
KITAZAWA_COLLAPSE_IN_T_CORE = 450.0 / KITAZAWA_CORE_RELAXATIONS   # = 15.0


def reproduce_all_kitazawa_tables() -> list[dict]:
    """Audit all six printed tables (3 scenarios x 2 cross sections x 5 LSBs).

    A ratio of 1 would confirm the published table; ~1e3 refutes it.
    """
    out = []
    for sc in KITAZAWA_SCENARIOS:
        ratios = []
        for (_n, r_s, rho_s, t1_printed, t01_printed) in sc["rows"]:
            ratios.append(t_core_form_gyr(1.0, rho_s, r_s) / t1_printed)
            ratios.append(t_core_form_gyr(0.1, rho_s, r_s) / t01_printed)
        out.append({"label": sc["label"], "A": sc["A"], "age_gyr": sc["age_gyr"],
                    "n_ratios": len(ratios), "ratio_min": min(ratios),
                    "ratio_max": max(ratios), "ratios": ratios})
    return out


def kitazawa_interpretation_audit() -> list[dict]:
    """Test the paper's conclusion against the threshold ITS OWN definitions imply.

    The paper rejects sigma/m = 1 because its printed t_core is 'much shorter
    than 11 Gyr ... the system would undergo gravothermal collapse ... into
    black holes', and accepts sigma/m = 0.1 because t_core is 'comparable to
    11 Gyr'.  But t_core = 30 t_r,0 is its CORE-FORMATION time; its collapse
    threshold is ~450 t_r,0 = 15 t_core.  't_core < age' and '15 t_core < age'
    are different tests and give different counts.
    """
    out = []
    for sc in KITAZAWA_SCENARIOS:
        for sigma_m, idx in ((1.0, 3), (0.1, 4)):
            printed = [r[idx] for r in sc["rows"]]
            out.append({
                "label": sc["label"], "sigma_m": sigma_m, "age_gyr": sc["age_gyr"],
                "n": len(sc["rows"]),
                "n_t_core_lt_age": sum(1 for t in printed if t < sc["age_gyr"]),
                "n_collapse_lt_age": sum(
                    1 for t in printed
                    if KITAZAWA_COLLAPSE_IN_T_CORE * t < sc["age_gyr"]),
            })
    return out


# ---------------------------------------------------------------------------
# (B4) Unit adjudication of the ~1e3 offset, resolved internally 2026-11-13
#      (owner decision: no author enquiry).  Four published timescales for the
#      SAME halos at sigma/m = 1 cm^2 g^-1:
#        printed (Table 2)            0.27 - 0.87  Gyr
#        repo Balberg+ 2002 convention            7.0  Gyr
#        paper eq. (11) + (7) here              270 - 899  Gyr
#        Yang+ 2024 eq. 2.2 (150 C)           2281 - 7605  Gyr
#      printed x 1e3 reproduces our evaluation to 4-6% on every halo, and
#      Yang/ours is a CONSTANT (8.46) across all five -> identical halo scaling,
#      so the discrepancy is one global time-unit factor, not arithmetic.
# ---------------------------------------------------------------------------
KITAZAWA_BALBERG_PREFACTOR = 12.7            # gravothermal.py / Balberg+ 2002
KITAZAWA_BALBERG_RHO_REF_MSUN_KPC3 = 1.0e7   # the convention's calibration density


def kitazawa_balberg_t_core_gyr(sigma_m_cm2_g: float, rho_s_msun_kpc3: float) -> float:
    """Repo Balberg+ 2002 convention: 12.7/sigma x (rho_s/1e7)^-1 x t_dyn, in Gyr."""
    from gravothermal_yang2024 import G_KPC3_PER_MSUN_GYR2
    if sigma_m_cm2_g <= 0.0:
        return float("inf")
    t_dyn_gyr = 1.0 / math.sqrt(4.0 * math.pi * G_KPC3_PER_MSUN_GYR2 * rho_s_msun_kpc3)
    scaling = (rho_s_msun_kpc3 / KITAZAWA_BALBERG_RHO_REF_MSUN_KPC3) ** -1
    return (KITAZAWA_BALBERG_PREFACTOR / sigma_m_cm2_g) * scaling * t_dyn_gyr


def kitazawa_unit_adjudication() -> list[dict]:
    """Resolve the ~1e3 offset by comparing four published timescales.

    No author contact was used (owner's decision, 2026-11-13).  The verdict this
    pins: the printed column reproduces eq. (11)-(12) halo-by-halo after a factor
    1e3, so the paper's arithmetic is right and its time unit is 1e3 low; and our
    own evaluation is anchored by Yang+ 2024's BM2 halo, which its calibrated
    function reproduces at the published 28.7 Gyr.
    """
    import gravothermal_yang2024 as yang
    out = []
    for name, _lm, _rc, r_s, rho_s, t1_printed, _t01_printed in KITAZAWA_LSB_TABLE:
        ours = t_core_form_gyr(1.0, rho_s, r_s)
        yang_pub = yang.collapse_time_SI_gyr(1.0, rho_s, r_s)
        out.append({
            "name": name,
            "rho_s_msun_kpc3": rho_s,
            "r_s_kpc": r_s,
            "printed_gyr": t1_printed,
            "eq11_recomputed_gyr": ours,
            "balberg2002_repo_gyr": kitazawa_balberg_t_core_gyr(1.0, rho_s),
            "yang2024_published_prefactor_gyr": yang_pub,
            "yang2024_bm2_calibrated_gyr": yang.collapse_time_calibrated_gyr(1.0, rho_s, r_s),
            "printed_x1000_over_recomputed": (t1_printed * 1.0e3) / ours,
            "yang_over_eq11": yang_pub / ours,
        })
    return out


# ---------------------------------------------------------------------------
# Whole-check report
# ---------------------------------------------------------------------------
def lsb_core_check(
    sigma_m_0: float,
    a: float,
    mediator_class: str = "power_law",
) -> dict:
    """Run the full LSB core check and return a report dict."""
    ngc = loglike_lsb_ngc5963_core(sigma_m_0, a, mediator_class=mediator_class)
    rows = kitazawa_lsb_rows(sigma_m_0, a, mediator_class=mediator_class)
    n_form = sum(1 for r in rows if r["forms_core_in_age"])
    n_repo_collapsed = sum(1 for r in rows if r["repo_phase"] == "collapsed")
    sigma_req_max = max(r["sigma_required_cm2_g"] for r in rows)
    return {
        "sigma_m_0": sigma_m_0,
        "a": a,
        "mediator_class": mediator_class,
        "ngc5963": ngc,
        "kitazawa_rows": rows,
        "kitazawa_verdict": {
            "n_lsb_forming_core_within_age": n_form,
            "n_lsb_collapsed_by_repo_timescale": n_repo_collapsed,
            "n_lsb_total": len(rows),
            "max_sigma_required_cm2_g": sigma_req_max,
            "note": "diagnostic only — see module docstring / KB entry "
                    "arXiv:2605.05588 (printed t_core values ~1e3 off)",
        },
    }


def _fmt(x: float, width: int = 10, prec: int = 3) -> str:
    if x == float("inf"):
        return "inf".rjust(width)
    if x >= 1e6:
        return f"{x:.2e}".rjust(width)
    return f"{x:.{prec}f}".rjust(width)


def main() -> None:  # pragma: no cover - CLI
    print("=" * 78)
    print("LSB CORE CHECK — reproduce Kitazawa+2026 printed t_core from its own equations")
    print("=" * 78)
    print(f"{'LSB':>9} {'nu_s km/s':>10} | {'sig=1 printed':>13} {'recomputed':>11} {'ratio':>9} | "
          f"{'sig=0.1 printed':>15} {'recomputed':>11} {'ratio':>9}")
    for r in reproduce_kitazawa_table():
        print(f"{r['name']:>9} {r['nu_s_kms']:>10.1f} | "
              f"{r['sigma_1']['printed_Gyr']:>13.2f} {_fmt(r['sigma_1']['recomputed_Gyr'], 11, 1)} "
              f"{r['sigma_1']['ratio_calc_over_printed']:>9.1f} | "
              f"{r['sigma_0p1']['printed_Gyr']:>15.2f} {_fmt(r['sigma_0p1']['recomputed_Gyr'], 11, 1)} "
              f"{r['sigma_0p1']['ratio_calc_over_printed']:>9.1f}")
    print(f"\npaper's printed conclusion: {KITAZAWA_PRINTED_CLAIM}")

    print("\n" + "=" * 78)
    print("KITAZAWA+2026 — all six printed tables (3 proto-cluster scenarios)")
    print("=" * 78)
    for sc in reproduce_all_kitazawa_tables():
        print(f"  {sc['label']:>16}  A={sc['A']:>5.0f}  age={sc['age_gyr']:.0f} Gyr "
              f" n={sc['n_ratios']:>2}  recomputed/printed = "
              f"{sc['ratio_min']:.1f} - {sc['ratio_max']:.1f}")
    print("  -> the ~1e3 factor is uniform across scenarios, densities and "
          "cross sections,\n     which is what a fixed unit slip looks like.")

    print("\n" + "=" * 78)
    print("KITAZAWA+2026 — claim vs the threshold its own definitions imply")
    print("=" * 78)
    print(f"  collapse threshold used here: {KITAZAWA_COLLAPSE_IN_T_CORE:.0f} x t_core "
          f"(paper: ~450 t_r,0, t_core = {KITAZAWA_CORE_RELAXATIONS:.0f} t_r,0)")
    for r in kitazawa_interpretation_audit():
        print(f"  {r['label']:>16} sigma/m={r['sigma_m']:>4}: "
              f"t_core < age for {r['n_t_core_lt_age']}/{r['n']}  vs  "
              f"{KITAZAWA_COLLAPSE_IN_T_CORE:.0f} t_core < age for "
              f"{r['n_collapse_lt_age']}/{r['n']}")

    print("\n" + "=" * 78)
    print("LSB CORE CHECK — model evaluated at three reference points")
    print("=" * 78)
    cases = [
        ("12-channel MAP", 0.684, 1.481, "power_law"),
        ("canonical pair amp", 0.008150396851725193, 1.93, "power_law"),
        ("CDM limit", 1e-12, 1.481, "power_law"),
    ]
    for label, s0, a_val, mc in cases:
        rep = lsb_core_check(s0, a_val, mc)
        ngc = rep["ngc5963"]
        print(f"\n[{label}] sigma_m0={s0:.6g}  a={a_val:.3f}  class={mc}")
        print(f"  NGC 5963 : sigma_eff(v=150) = {ngc['metadata']['sigma_eff_cm2_g']:.4f} cm2/g "
              f"vs limit {ngc['metadata']['limit_cm2_g']:.2f} | t_rc = "
              f"{_fmt(ngc['metadata']['trc_gyr'], 9, 1)} Gyr | loglike = {ngc['loglike']:.3f}")
        print(f"  Kitazawa : {rep['kitazawa_verdict']['n_lsb_forming_core_within_age']}"
              f"/{rep['kitazawa_verdict']['n_lsb_total']} LSBs form a core within "
              f"{KITAZAWA_AGE_GYR} Gyr; hardest halo needs sigma/m >= "
              f"{rep['kitazawa_verdict']['max_sigma_required_cm2_g']:.3g} cm2/g")
        for r in rep["kitazawa_rows"]:
            print(f"    {r['name']:>9} nu_s={r['nu_s_kms']:6.1f} km/s "
                  f"sigma_eff={r['sigma_eff_cm2_g']:8.4f} "
                  f"t_core={_fmt(r['t_core_gyr'], 9, 1)} Gyr "
                  f"needs>={r['sigma_required_cm2_g']:8.3g} "
                  f"repo_phase={r['repo_phase']:>9} "
                  f"M(<R_c)={r['m_dyn_from_params_msun']:.2e} vs {r['m_dyn_from_paper_msun']:.2e}")


if __name__ == "__main__":  # pragma: no cover
    main()
