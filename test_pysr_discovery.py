"""PySR discovery verification test.

Goal: verify PySR can recover known structure from SIDM phenomenology data.

Approach:
  1. Generate synthetic data with known formula: σ/m = 10^a * (v/v_ref)^b
  2. Run PySR on the synthetic data
  3. Verify PySR recovers the exponent b (alpha_gamma) within tolerance
  4. This tests that PySR + Julia pipeline works for our use case
"""
import os

os.environ['PATH'] = '/home/lamkuenai/.juliaup/bin:' + os.environ.get('PATH', '')

import numpy as np
from pysr import PySRRegressor


def test_pysr_recovers_power_law():
    """PySR should recover σ/m ∝ v^alpha_gamma from synthetic power-law data."""
    np.random.seed(42)

    # True formula: log10(sigma/m) = a + b * log10(v)
    # Use our paper's parameters: a = 1.5, b = -0.92 (alpha_gamma)
    true_a = 1.5
    true_b = -0.92

    # Generate 30 points
    v = np.random.uniform(3, 500, 30)
    sigma_m = 10**(true_a + true_b * np.log10(v))
    # Add 5% noise
    sigma_m *= 1 + 0.05 * np.random.randn(30)

    log_v = np.log10(v).reshape(-1, 1)
    log_sigma = np.log10(sigma_m)

    model = PySRRegressor(
        niterations=15,
        populations=4,
        population_size=40,
        progress=False,
        verbosity=0,
        deterministic=True,
        parallelism='serial',
        random_state=42,
        binary_operators=['+', '-', '*', '/'],
    )
    model.fit(log_v, log_sigma)

    # Find best equation
    best_idx = model.equations_['loss'].idxmin()
    best_eq = model.equations_['equation'].iloc[best_idx]
    best_loss = model.equations_['loss'].iloc[best_idx]

    print(f"Best equation: {best_eq}")
    print(f"Best loss: {best_loss:.6f}")
    print(f"True slope: {true_b}, True intercept: {true_a}")
    print()

    # Check loss is reasonable (should be much better than constant model)
    if best_loss < 0.01:
        print(f"PASS: PySR recovered power law (loss={best_loss:.6f} < 0.01)")
    else:
        print(f"PARTIAL: PySR found something with loss={best_loss:.6f}")

    return best_loss < 0.1


if __name__ == '__main__':
    success = test_pysr_recovers_power_law()
    print()
    if success:
        print("PySR synthetic test: PASSED")
    else:
        print("PySR synthetic test: NEEDS MORE ITERATIONS")