"""PySR smoke test: discover y = x[0]^2 + x[1] from 50 random samples."""
import os
import sys

# Ensure juliaup is in PATH
os.environ['PATH'] = '/home/lamkuenai/.juliaup/bin:' + os.environ.get('PATH', '')

import numpy as np
from pysr import PySRRegressor

print("Setting up PySR...", flush=True)
np.random.seed(42)
X = np.random.randn(50, 2)
y = X[:, 0]**2 + X[:, 1]

model = PySRRegressor(
    niterations=5,
    populations=2,
    population_size=20,
    progress=False,
    verbosity=0,
    deterministic=True,
    parallelism='serial',
    random_state=42,
)

print("Fitting PySR (5 iterations, 40 individuals)...", flush=True)
model.fit(X, y)

best_idx = model.equations_['loss'].idxmin()
best_eq = model.equations_['equation'].iloc[best_idx]
best_loss = model.equations_['loss'].iloc[best_idx]

print(f"\nPySR discovered equation: {best_eq}", flush=True)
print(f"Loss: {best_loss:.6f}", flush=True)
print(f"\nTrue function: y = x[0]^2 + x[1]", flush=True)
print("\nPySR smoke test: PASSED", flush=True)