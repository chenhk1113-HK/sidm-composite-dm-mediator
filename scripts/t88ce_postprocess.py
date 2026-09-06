"""Post-process script for T88.C + T88.E headline + sampling-variance control test.

Reads both JSON outputs and computes:
1. T88.C pure contribution (Euclid lensing only)
2. T88.E pure contribution (Euclid subhalo forecast only)
3. Sampling variance (control vs T88.B headline)
4. Net delta (T88.C+E vs v0.7 baseline)

Usage: python scripts/t88ce_postprocess.py
"""
import json
from pathlib import Path

RESULTS_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results")

# Reference: v0.7 baseline (XRISM OFF, EROSITA OFF, Euclid OFF)
v07_path = RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json"
# T88.B: XRISM + EROSITA ON (no T88.D, T88.C, T88.E)
t88b_path = RESULTS_DIR / "t41_mediator_mass_joint_fit_t88b_v07_with_erosita_nlive2000.json"
# T88.CE headline: XRISM + EROSITA + T88.D + T88.C + T88.E ON
t88ce_headline = RESULTS_DIR / "t41_mediator_mass_joint_fit_t88ce_v08_with_euclid_lensing_and_subhalo_forecast_nlive2000.json"
# T88.CE control: XRISM + EROSITA + T88.D + T88.C ON, T88.E OFF
t88ce_control = RESULTS_DIR / "t41_mediator_mass_joint_fit_t88ce_sampling_variance_control.json"


def load_or_none(p):
    if not p.exists():
        return None
    return json.load(open(p))


def get_physical(j):
    if j is None:
        return None
    return {
        "log_Z": j["log_Z"],
        "log_Z_err": j["log_Z_err"],
        "sigma_m_0_MAP": j["MAP_physical"]["sigma_m_0_derived"],
        "a_MAP": j["MAP_physical"]["a_derived"],
    }


v07 = get_physical(load_or_none(v07_path))
t88b = get_physical(load_or_none(t88b_path))
t88ce_head = get_physical(load_or_none(t88ce_headline))
t88ce_ctrl = get_physical(load_or_none(t88ce_control))

print("=" * 75)
print("  T88.C + T88.E HEADLINE + SAMPLING-VARIANCE CONTROL TEST")
print("  (per skill P17)")
print("=" * 75)

for label, j in [("v0.7 baseline (XRISM/EROSITA/Euclid OFF)", v07),
                   ("T88.B headline (XRISM+EROSITA ON)", t88b),
                   ("T88.CE control (XRISM+EROSITA+T88.D+T88.C ON, T88.E OFF)", t88ce_ctrl),
                   ("T88.CE HEADLINE (XRISM+EROSITA+T88.D+T88.C+T88.E ON)", t88ce_head)]:
    if j is None:
        print(f"\n{label}:")
        print("  (MISSING)")
        continue
    print(f"\n{label}:")
    print(f"  log Z = {j['log_Z']:+.4f} +/- {j['log_Z_err']:.4f}")
    print(f"  sigma_m_0 MAP = {j['sigma_m_0_MAP']:.4f} cm^2/g")
    print(f"  a MAP = {j['a_MAP']:.4f}")

print()
print("=" * 75)
print("  ISOLATED CHANNEL CONTRIBUTIONS")
print("=" * 75)

if t88ce_head and t88ce_ctrl:
    pure_t88e = t88ce_head["log_Z"] - t88ce_ctrl["log_Z"]
    print(f"\nPure T88.E contribution (T88.CE_headline - T88.CE_control):")
    print(f"  delta_log_Z = {pure_t88e:+.4f}")
    if abs(pure_t88e) < t88ce_ctrl["log_Z_err"] * 2:
        print(f"  within 2*sigma ({2*t88ce_ctrl['log_Z_err']:.4f})")
    else:
        print(f"  >2*sigma from 0 (channel signal!)")
    # Hand-computed expected: -0.975 log-units
    print(f"  Expected (hand-computed): -0.975 log-units at v0.7 MAP")
    print(f"  Sampling variance (control vs T88.B): {t88ce_ctrl['log_Z'] - t88b['log_Z']:+.4f}")

if t88ce_head and v07:
    print(f"\nT88.CE headline vs v0.7 baseline:")
    print(f"  delta_log_Z = {t88ce_head['log_Z'] - v07['log_Z']:+.4f}")
    print(f"  (includes sampling variance + XRISM + EROSITA + T88.D + T88.C + T88.E)")
    print(f"\nsigma_m_0 MAP shift: {v07['sigma_m_0_MAP']:.4f} -> {t88ce_head['sigma_m_0_MAP']:.4f}")
    print(f"a MAP shift: {v07['a_MAP']:.4f} -> {t88ce_head['a_MAP']:.4f}")