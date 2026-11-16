"""Debug the Boltzmann solver."""
import numpy as np
import sys
sys.path.insert(0, "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code")
import t55_boltzmann_relic as t55

# Trace the rate coefficient at a typical freeze-out point
m_chi = 40.0  # GeV
x_test = 20.0  # x = m/T, freeze-out for typical WIMP
T_test = m_chi / x_test  # ~ 2 GeV
g_ss = t55.g_star_s_SM(T_test)
sigma_v_GeV2 = 3e-26 * t55.CM3_TO_GEV_INV3  # ~ 3e-26 * 1.3e41 = 3.9e15 GeV^-2
H_GeV = 1.66 * np.sqrt(g_ss) * T_test ** 2 / t55.M_PLANCK_GEV
s_GeV3 = (2 * np.pi ** 2 / 45) * g_ss * T_test ** 3
rate = s_GeV3 * sigma_v_GeV2 / H_GeV
print(f"T = {T_test:.3f} GeV, g_*s = {g_ss}")
print(f"H = {H_GeV:.3e} GeV")
print(f"s = {s_GeV3:.3e} GeV^3")
print(f"sigma_v (GeV^-2) = {sigma_v_GeV2:.3e}")
print(f"rate = s <sigma*v> / H = {rate:.3e}")
print(f"rate / x^2 = {rate / x_test ** 2:.3e}")

# So if rate ~ 1e-3, then dY/dx ~ Y_eq ~ 1e-30 * (something)
# At x = 20, Y_eq ~ (1/86) * 0.145 * 20^1.5 * e^-20 = 1.69e-6 * 5.06e-9 = 8.6e-15
print(f"\nY_eq(x=20) = {t55.Y_eq_approx(20):.3e}")
print(f"Y_eq(x=5) = {t55.Y_eq_approx(5):.3e}")  # should be ~ 0.05 (still relativistic)
print(f"Y_eq(x=10) = {t55.Y_eq_approx(10):.3e}")  # should be ~ 0.001
print(f"Y_eq(x=20) = {t55.Y_eq_approx(20):.3e}")  # should be ~ 1e-8
print(f"Y_eq(x=30) = {t55.Y_eq_approx(30):.3e}")  # should be ~ 1e-13

# Try integrating the ODE with more debug
def dY_dx(Y_arr, x_val):
    Y = Y_arr[0]
    Y_eq = t55.Y_eq_approx(x_val)
    g_ss = t55.g_star_s_SM(m_chi / x_val)
    H_GeV = 1.66 * np.sqrt(g_ss) * (m_chi / x_val) ** 2 / t55.M_PLANCK_GEV
    s_GeV3 = (2 * np.pi ** 2 / 45) * g_ss * (m_chi / x_val) ** 3
    rate = s_GeV3 * sigma_v_GeV2 / H_GeV
    d = -rate / x_val ** 2 * (Y ** 2 - Y_eq ** 2)
    if x_val in [5, 10, 20, 30, 50]:
        print(f"  x={x_val:.0f}, Y={Y:.3e}, Y_eq={Y_eq:.3e}, rate/x^2={rate/x_val**2:.3e}, dY/dx={d:.3e}")
    return [d]

from scipy.integrate import odeint
x = np.linspace(1.0, 100.0, 200)
print("\nODE trace:")
Y0_init = t55.Y_eq_approx(x[0])
sol = odeint(dY_dx, [Y0_init], x)
print(f"\nFinal Y = {sol[-1, 0]:.3e}")