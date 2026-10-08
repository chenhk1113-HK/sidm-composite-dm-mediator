"""
Phase G11 v3 — Debug: check f_H saturation across constrained halos
"""
import math
import numpy as np

F_H_INITIAL = 0.297

# Use the calibrated tau values from Phase G11
constrained_tau = {
    "Fornax dSph": 91.79,
    "Sculptor dSph": 91.79,
    "Draco dSph": 91.79,
    "Boötes I UFD": 79.37,
    "Cloud-9 host": 201.81,
    "MW-mass host": 654.02,
    "Cluster": 654.02,
}

# f_H formula from v2
def f_H_sidm2c_v2(r_over_r_s, tau, cap=0.60):
    if tau <= 0:
        return F_H_INITIAL
    tau_seg = 0.3
    concentration = 1 + (cap/F_H_INITIAL - 1) * (1 - math.exp(-tau / tau_seg))
    return F_H_INITIAL * concentration

print("Test: f_H at tau values from Phase G11 calibration")
print()
print(f"{'Halo':<28} {'tau':<10} {'exp(-tau/0.3)':<14} {'concentration':<16} {'f_H'}")
print("-" * 80)

for name, tau in constrained_tau.items():
    exp_term = math.exp(-tau / 0.3)
    concentration = 1 + (0.60/0.297 - 1) * (1 - exp_term)
    f_h = F_H_INITIAL * concentration
    print(f"{name:<28} {tau:<10.2f} {exp_term:<14.2e} {concentration:<16.6f} {f_h:.6f}")

print()
print("All tau >> 0.3, so exp(-tau/0.3) ~ 0 and concentration ~ 1 + 0.60/0.297 - 1 = 1.020")
print("All f_H saturate at F_H_INITIAL * (0.60/0.297) = 0.60")
print()
print("The issue: tau_seg = 0.3 is too short relative to actual tau values (~80-650)")
print("All halos are in the saturated regime where concentration ~ constant")
print()
print("Solution: use tau_seg scaled to actual halo population")
print("Try tau_seg = 100 (typical value):")
print()

tau_seg = 100.0
print(f"{'Halo':<28} {'tau':<10} {'exp(-tau/100)':<14} {'concentration':<16} {'f_H'}")
print("-" * 80)
for name, tau in constrained_tau.items():
    exp_term = math.exp(-tau / tau_seg)
    concentration = 1 + (0.60/0.297 - 1) * (1 - exp_term)
    f_h = F_H_INITIAL * concentration
    print(f"{name:<28} {tau:<10.2f} {exp_term:<14.4f} {concentration:<16.6f} {f_h:.6f}")
