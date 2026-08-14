"""Inspect UGC02953 error model."""
import sys
sys.path.insert(0, '/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/code')
from sparc_loader import load_one_sparc
g = load_one_sparc('/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.1-prelim/data', 'UGC02953')
print('errV stats:', g.errV.min(), g.errV.mean(), g.errV.max(), g.errV.std())
print('Vobs stats:', g.Vobs.min(), g.Vobs.mean(), g.Vobs.max(), g.Vobs.std())
print('First 5 errV:', g.errV[:5])
print('First 5 Vobs:', g.Vobs[:5])
print()
import numpy as np
print('errV/Vobs ratio:', g.errV / np.maximum(g.Vobs, 1.0))
print()
# Look for very-small errV values that would inflate chi^2
print('errV < 1.0:', np.sum(g.errV < 1.0), 'points')
print('errV < 2.0:', np.sum(g.errV < 2.0), 'points')
print('errV < 5.0:', np.sum(g.errV < 5.0), 'points')