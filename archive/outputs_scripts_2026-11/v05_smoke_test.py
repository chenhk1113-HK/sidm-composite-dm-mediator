"""Smoke test for v0.5 T41 re-run.

Tests that loglike_joint correctly:
1. Returns finite ll at in-box point (m_phi = 493 MeV = inside KSFR window [418, 4180])
2. Returns -inf at out-of-box point (m_phi = 26.6 MeV = below KSFR floor)
3. A full nested-sampling run completes with KSFR mask active (nlive=20 for speed)
"""
import time
import sys
import os
sys.path.insert(0, '/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code')

# Point-level tests first
import t41_mediator_mass_joint_fit as t41

# In-box point: m_phi = 493 MeV (KSFR-valid, f_pi ~ 0.059 GeV, ratio 8.36 => Lambda ~ 59 MeV)
# Wait - 493 MeV / 1000 / 8.36 = 0.0590 GeV which is BELOW KSFR_F_PI_MIN (0.05)?
# Actually 0.059 >= 0.05, so just barely in-box. Let me check:
# f_pi = m_phi_MeV / 1000 / 8.36 = m_phi_MeV / 8360
# f_pi >= 0.05 -> m_phi_MeV >= 418 MeV (exact)
# f_pi <= 0.5 -> m_phi_MeV <= 4180 MeV

# Choose m_phi = 1000 MeV (clearly in-box: f_pi = 0.120 GeV)
in_box = [
    3.0,        # log10(1000) = 3.0  ->  m_phi = 1000 MeV (f_pi = 0.120 GeV, valid)
    1.176,      # log10(15)   ->       m_chi = 15 GeV
    0.13,       # g_chi
    -35.0,      # log_epsilon (typical LZ posterior)
    -3.0,       # log_alpha
]
# Out-of-box: m_phi = 26.6 MeV (the historical T41 MAP, below KSFR floor)
out_box = [
    1.4248,     # log10(26.6) -> m_phi = 26.6 MeV
    1.176,
    0.13,
    -35.0,
    -3.0,
]
# Far out-of-box: m_phi = 10 TeV
far_box = [4.0, 1.176, 0.13, -35.0, -3.0]

print("=== Point-level tests ===")
in_ll = t41.loglike_joint(in_box)
print(f"in-box  (m_phi=1000 MeV): loglike = {in_ll}")
out_ll = t41.loglike_joint(out_box)
print(f"out-box (m_phi=26.6 MeV): loglike = {out_ll}")
far_ll = t41.loglike_joint(far_box)
print(f"far-box (m_phi=10000 MeV): loglike = {far_ll}")

import numpy as np
assert np.isfinite(in_ll), f"FAIL: in-box point should have finite loglike, got {in_ll}"
assert not np.isfinite(out_ll), f"FAIL: out-of-box point should be -inf, got {out_ll}"
assert not np.isfinite(far_ll), f"FAIL: far-box (m_phi > 4180 MeV) should be -inf, got {far_ll}"
print("Point-level tests PASSED")

# Now a tiny dynesty run to verify the sampler works with the mask
print()
print("=== Mini dynesty run (nlive=20, dlogz=1.0, fast smoke) ===")
import dynesty
t0 = time.time()
sampler = dynesty.NestedSampler(
    loglikelihood=t41.loglike_joint,
    prior_transform=t41.prior_transform_5,
    ndim=5, nlive=20, bound='multi', sample='auto', bootstrap=0,
)
sampler.run_nested(dlogz=1.0, print_progress=False)
wall = time.time() - t0
res = sampler.results
log_Z = float(res.logz[-1])
samples = res.samples
weights = np.exp(res.logwt - res.logz[-1])
imap = int(np.argmax(weights))
MAP = samples[imap]
print(f"nlive=20, dlogz=1.0: log Z = {log_Z:.3f}, wall = {wall:.1f}s")
print(f"MAP: log_m_phi_MeV = {MAP[0]:.3f} (m_phi = {10**MAP[0]:.2f} MeV)")
print(f"     log_m_chi_GeV = {MAP[1]:.3f} (m_chi = {10**MAP[1]:.2f} GeV)")
print(f"     g_chi = {MAP[2]:.3f}")
print(f"     log_epsilon = {MAP[3]:.3f} (eps = {10**MAP[3]:.2e})")
print(f"     log_alpha = {MAP[4]:.3f} (alpha = {10**MAP[4]:.2e})")

# Verify MAP m_phi is in KSFR-valid region [418, 4180]
m_phi_MAP = 10 ** MAP[0]
assert 418 <= m_phi_MAP <= 4180, f"FAIL: MAP m_phi={m_phi_MAP:.1f} MeV not in KSFR-valid [418, 4180]"
print(f"MAP m_phi = {m_phi_MAP:.1f} MeV is in KSFR-valid region ✓")
print()
print(f"Smoke test PASSED in {wall:.1f}s")