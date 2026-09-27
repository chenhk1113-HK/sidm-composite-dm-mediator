"""
T148: Quick & dirty sidmkit parameter exploration.

Avoid the slow parameter sweep of T145. Test individual parameter
combinations with simple progress tracking.
"""
import sys
import sidmkit
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Test ONE parameter set, see how long it takes
print("Testing single parameter set...")
import time

t0 = time.time()
model = sidmkit.YukawaModel(m_chi_gev=10.0, m_med_gev=0.01, alpha=0.1,
                              potential=sidmkit.PotentialType.ATTRACTIVE)
v_test = np.array([3, 5, 7, 10, 15, 28, 100, 500])
sigma = sidmkit.sigma_over_m(v_test, model, method='partial_wave')
t1 = time.time()
print(f"  Time: {t1-t0:.2f}s")

# Now try a parameter set near threshold
# When parameters are near bound state threshold, sidmkit may hang
# Use a moderate set
t0 = time.time()
model = sidmkit.YukawaModel(m_chi_gev=10.0, m_med_gev=0.001, alpha=0.5,
                              potential=sidmkit.PotentialType.ATTRACTIVE)
sigma = sidmkit.sigma_over_m(v_test, model, method='partial_wave')
t1 = time.time()
print(f"  Time (alpha=0.5, mA=1 MeV): {t1-t0:.2f}s")

# Try much weaker coupling
t0 = time.time()
model = sidmkit.YukawaModel(m_chi_gev=10.0, m_med_gev=0.01, alpha=0.01,
                              potential=sidmkit.PotentialType.ATTRACTIVE)
sigma = sidmkit.sigma_over_m(v_test, model, method='partial_wave')
t1 = time.time()
print(f"  Time (alpha=0.01): {t1-t0:.2f}s")
print(f"  Sigma values: {sigma}")