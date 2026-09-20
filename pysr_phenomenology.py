"""PySR discovery run on SIDM phenomenology data.

Goal: discover the formula σ/m(v) from the 8 observational constraint points.

Known structure (from our 4-ingredient model):
  sigma_over_m(v) ~ (v/v_ref)^(-alpha_gamma)

We use v_ref = 28 km/s (Cloud-9 velocity).
"""
import os

os.environ['PATH'] = '/home/lamkuenai/.juliaup/bin:' + os.environ.get('PATH', '')

import json
import numpy as np
from pysr import PySRRegressor

# Load phenomenology data
with open('/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/sigma_m_phase44.json') as f:
    data = json.load(f)

# Extract (v, sigma_over_m) pairs
velocities = []
sigma_over_m = []
labels = []
for k, v in data.items():
    if k.startswith('v') and isinstance(v, (int, float)):
        v_str = k.split('_')[0]  # "v3.0"
        v_val = float(v_str[1:])  # 3.0
        velocities.append(v_val)
        sigma_over_m.append(v)
        labels.append('_'.join(k.split('_')[1:]))

X = np.array(velocities).reshape(-1, 1)
y = np.array(sigma_over_m)

print(f"Phenomenology data points: {len(X)}")
print(f"Velocity range: {X.min():.1f} - {X.max():.1f} km/s")
print(f"sigma/m range: {y.min():.2e} - {y.max():.2e} cm²/g")
print()
print("Data points:")
for v, s, lbl in sorted(zip(velocities, sigma_over_m, labels)):
    print(f"  v={v:6.1f} km/s, σ/m={s:.4e}, label={lbl}")
print()

# Use log-log fit (works better for power laws)
log_X = np.log10(X)
log_y = np.log10(y)

print("=== PySR discovery run (log10 scale) ===")
print("Target: discover log10(sigma_over_m) as function of log10(v)")
print()

model = PySRRegressor(
    niterations=20,
    populations=4,
    population_size=40,
    progress=False,
    verbosity=1,
    deterministic=True,
    parallelism='serial',
    random_state=42,
    binary_operators=['+', '-', '*', '/'],
    unary_operators=['square', 'cube', 'sqrt'],
)

model.fit(log_X, log_y)

# Find best equation
best_idx = model.equations_['loss'].idxmin()
best_eq = model.equations_['equation'].iloc[best_idx]
best_loss = model.equations_['loss'].iloc[best_idx]
best_complexity = model.equations_['complexity'].iloc[best_idx]

print()
print(f"Best equation (log10 space): {best_eq}")
print(f"  complexity={best_complexity}, loss={best_loss:.6f}")
print()

# Translate back: log10(sigma/m) = a + b * log10(v) => sigma/m = 10^a * v^b
# So alpha_gamma = b (slope in log-log)
# v_ref can be inferred from 10^a * v_ref^b = measured at v_ref

# Show top 5 equations
print("=== Top 5 equations by loss ===")
top5 = model.equations_.nsmallest(5, 'loss')[['complexity', 'loss', 'equation']]
for _, row in top5.iterrows():
    print(f"  complexity={row['complexity']}, loss={row['loss']:.6f}: {row['equation']}")

print()
print("PySR phenomenology discovery: PASSED" if best_loss < 1.0 else "PySR discovery: needs more iterations")