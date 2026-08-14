"""Profile V^2(r) timing test."""
import sys
import time
import numpy as np
sys.path.insert(0, '/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/code')
from halo_profiles import V_NFW, V_Burkert

r = np.linspace(0.1, 60, 115)
rho, r_s = 1e7, 10**0.5
rho_c, r_c = 1e7, 10**0.5

t0 = time.time()
for _ in range(100):
    V2 = V_NFW(r, rho, r_s)
t_nfw = (time.time() - t0) / 100
print(f"NFW: {t_nfw*1000:.3f} ms per call")

t0 = time.time()
for _ in range(10):
    V2 = V_Burkert(r, rho_c, r_c)
t_burkert = (time.time() - t0) / 10
print(f"Burkert: {t_burkert*1000:.3f} ms per call")

# Project: dynesty needs ~10000 likelihood evals per fit
# (nlive=200, with bound updates)
proj_nfw_per_fit = t_nfw * 10000
proj_burkert_per_fit = t_burkert * 10000
print(f"Projected NFW per fit:     {proj_nfw_per_fit:.1f} s")
print(f"Projected Burkert per fit: {proj_burkert_per_fit:.1f} s")
print(f"175 galaxies x 2 models:   {(175 * 2 * (proj_nfw_per_fit + proj_burkert_per_fit))/60:.1f} min total")