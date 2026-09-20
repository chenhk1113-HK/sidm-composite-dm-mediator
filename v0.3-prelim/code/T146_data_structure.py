"""
T146: Targeted parameter search near T143 result.

After T145 showed that the apparent slope -1 was misleading (came from
v=15→v=28 discontinuity, not power-law), let me search parameters more
carefully. We need to match 4-peak structure, not just slope.

Strategy: Look at the data structure itself to figure out what physics
the 4 peaks correspond to.
"""
import numpy as np
import sidmkit
import warnings
warnings.filterwarnings('ignore')
import json

with open(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\sigma_m_phase44.json") as f:
    data = json.load(f)

v_data = {}
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]
        v_val = float(v_str[1:])
        v_data[v_val] = v

# Look at our data structure more carefully
v_arr = np.array(sorted(v_data.keys()))
s_arr = np.array([v_data[v] for v in v_arr])

print("Our data structure:")
print(f"{'v (km/s)':>10} {'σ/m':>12} {'log10 σ/m':>12} {'Δ(log σ/m)':>12}")
log_s = np.log10(s_arr)
for i, (v, s, ls) in enumerate(zip(v_arr, s_arr, log_s)):
    if i == 0:
        delta = ""
    else:
        delta = f"{ls - log_s[i-1]:+.3f}"
    print(f"{v:>10.1f} {s:>12.4e} {ls:>+12.4f} {delta:>12}")

# Log slope between consecutive points
print()
print("Local log-slope between consecutive points:")
for i in range(1, len(v_arr)):
    delta_log_v = np.log10(v_arr[i] / v_arr[i-1])
    delta_log_s = log_s[i] - log_s[i-1]
    local_slope = delta_log_s / delta_log_v
    print(f"  v={v_arr[i-1]:>5.1f} to v={v_arr[i]:>5.1f}: local slope = {local_slope:+.3f}")