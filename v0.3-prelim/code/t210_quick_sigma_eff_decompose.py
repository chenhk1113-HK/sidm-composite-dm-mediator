"""
T210 quick diagnostic — what is sigma_eff(28) made of?
"""
import sys
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
from T207_three_term_fit import sigma_eff_three_term

v = 28.0
f_H = 0.5
sigma_0 = 0.005
sigma_peak_HH_1 = 84.4
sigma_0_HL = 0.0001
sigma_peak_HL = 0.318
v_HL = 28.0
width_HL = 50.0
sigma_0_LL = 0.0006
a_slope = 1.0

print(f"sigma_eff(v=28, f_H=0.5, v_HL=28, sigma_peak_HL=0.318) = {sigma_eff_three_term(v, f_H=f_H, sigma_0=sigma_0, a_slope=a_slope, sigma_peak_HH_1=sigma_peak_HH_1, sigma_0_HL=sigma_0_HL, sigma_peak_HL=sigma_peak_HL, v_HL=v_HL, width_HL=width_HL, sigma_0_LL=sigma_0_LL):.4f} cm^2/g")
print()

# Vary sigma_peak_HL
print("Vary sigma_peak_HL (at v_HL=28, f_H=0.5):")
for spl in [0.318, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0]:
    se = sigma_eff_three_term(v, f_H=f_H, sigma_0=sigma_0, a_slope=a_slope, sigma_peak_HH_1=sigma_peak_HH_1, sigma_0_HL=sigma_0_HL, sigma_peak_HL=spl, v_HL=v_HL, width_HL=width_HL, sigma_0_LL=sigma_0_LL)
    print(f"  sigma_peak_HL = {spl:7.3f}: sigma_eff(28) = {se:8.3f} cm^2/g  (target >= 128)")

# Check: even with f_H=0.85 (core_forming for Cloud-9), is sigma_eff(28) different?
print()
print(f"At v_HL=28, f_H=0.85 (Cloud-9 core_forming class):")
for spl in [0.318, 5.0, 50.0]:
    se = sigma_eff_three_term(v, f_H=0.85, sigma_0=sigma_0, a_slope=a_slope, sigma_peak_HH_1=sigma_peak_HH_1, sigma_0_HL=sigma_0_HL, sigma_peak_HL=spl, v_HL=v_HL, width_HL=width_HL, sigma_0_LL=sigma_0_LL)
    print(f"  sigma_peak_HL = {spl:7.3f}: sigma_eff(28) = {se:8.3f} cm^2/g")

# What's the f_H^2 sigma_HH contribution at v=28?
print()
print(f"f_H^2 sigma_HH(28) decomposition (at v_HL=28, f_H=0.5, sigma_peak_HH_1=84.4):")
import math
# Lorentzian at v_HL=28, v=28: peak value
lorentz_at_28 = 1.0 / (1.0 + ((28.0 - 28.0) / width_HL)**2)
print(f"  Lorentzian(v=28, v_HL=28) = {lorentz_at_28:.4f}")
print(f"  sigma_HH_1(v=28) = sigma_0 + sigma_peak_HH_1 * lorentzian = {sigma_0 + sigma_peak_HH_1 * lorentz_at_28:.3f}")
print(f"  f_H^2 * sigma_HH_1(28) = {f_H**2 * (sigma_0 + sigma_peak_HH_1 * lorentz_at_28):.3f}")