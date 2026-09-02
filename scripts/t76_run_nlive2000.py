"""Run T41 v0.7 at nlive=2000 for final convergence check.

Background launch — runs in foreground for the wrapper but with a
generous timeout. Saves to v0.7 nlive2000 result file.
"""
import sys
sys.path.insert(0, 'v0.3-prelim/code')
sys.path.insert(0, 'v0.1-prelim/code')
import os

os.environ['T41_NLIVE'] = '2000'

# Note: T41 main() writes to a fixed path 't41_mediator_mass_joint_fit.json'.
# We'll rename after the run completes.

import t41_mediator_mass_joint_fit as t41
print('=== T41 v0.7 at nlive=2000 ===')
print('Expected wall: ~700-1000s (~12-17 min)')
print()
t41.main()