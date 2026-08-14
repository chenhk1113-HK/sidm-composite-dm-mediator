"""Quick stats on SPARC galaxies by point count."""
import sys
sys.path.insert(0, '/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/code')
from sparc_loader import load_all_sparc
gs = load_all_sparc('/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.1-prelim/data')
print(f'Total galaxies: {len(gs)}')
print()
print('Top 10 by data-point count:')
for g in sorted(gs, key=lambda g: -g.n_pts)[:10]:
    print(f'  {g.name:>12}: n={g.n_pts}, Vobs=[{g.Vobs.min():.1f}, {g.Vobs.max():.1f}]')
print()
print('Bottom 5 by data-point count:')
for g in sorted(gs, key=lambda g: g.n_pts)[:5]:
    print(f'  {g.name:>12}: n={g.n_pts}')
print()
import numpy as np
n_pts = np.array([g.n_pts for g in gs])
print(f'n_pts stats: median={np.median(n_pts)}, mean={n_pts.mean():.1f}, min={n_pts.min()}, max={n_pts.max()}')
print(f'n_pts >= 20: {np.sum(n_pts >= 20)}/{len(gs)} galaxies')
print(f'n_pts >= 30: {np.sum(n_pts >= 30)}/{len(gs)} galaxies')