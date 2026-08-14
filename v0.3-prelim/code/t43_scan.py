"""T43 scan — find delta window where a > 0."""
import sys
sys.path.insert(0, '.')
import t43_inelastic_dm as idm
import numpy as np

# Scan finer delta and check a in different v windows
print("Finer delta scan, a in different v windows:")
print(f"{'delta [MeV]':>12} {'v_thr [km/s]':>14} {'a (10-100)':>14} "
      f"{'a (100-300)':>14} {'a (300-1000)':>14}")
for delta in [0.001, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]:
    v_thr = idm.v_threshold_km_s(delta, 40.0)
    a_lo = idm.derived_a_inelastic(100.0, 40.0, 0.5, delta, v_lo_kms=10.0, v_hi_kms=100.0)
    a_mid = idm.derived_a_inelastic(100.0, 40.0, 0.5, delta, v_lo_kms=100.0, v_hi_kms=300.0)
    a_hi = idm.derived_a_inelastic(100.0, 40.0, 0.5, delta, v_lo_kms=300.0, v_hi_kms=1000.0)
    print(f"{delta:>12.4f} {v_thr:>14.1f} {a_lo:>14.3f} {a_mid:>14.3f} {a_hi:>14.3f}")
