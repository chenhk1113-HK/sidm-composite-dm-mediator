import numpy as np, os, csv
ROOT = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/external/fermi_mcdaniel2024"

# 1. Inspect a single TS profile
arr = np.load(f"{ROOT}/dSphs/TS_profiles/Segue_1_noprior_bb.npy")
print(f"TS profile shape: {arr.shape}, dtype: {arr.dtype}")
print(f"TS range: min={arr.min():.3f}, max={arr.max():.3f}, sample TS[20,30]={arr[20, 30]:.3f}")

# 2. Mass and sigma_v grids
masses = np.logspace(np.log10(1.0), np.log10(1000.0), 40)
sigvs = np.logspace(-28, -22, 60)
print(f"Mass grid: 40 log-spaced over [1 GeV, 1 TeV] = [{masses[0]:.2f}, {masses[-1]:.2f}]")
print(f"Sigma_v grid: 60 log-spaced over [1e-28, 1e-22] = [{sigvs[0]:.2e}, {sigvs[-1]:.2e}]")

# 3. File structure
files = os.listdir(f"{ROOT}/dSphs/TS_profiles/")
print(f"Total .npy files: {len(files)}")
dsphs = set()
for f in files:
    for suf in ["_noprior_bb", "_Jprior_bb", "_noprior_tau", "_Jprior_tau"]:
        if f.endswith(suf + ".npy"):
            dsphs.add(f[:-len(suf + ".npy")])
dsphs = sorted(dsphs)
print(f"Distinct dSphs: {len(dsphs)}")
print(f"Sample dSphs: {dsphs[:8]}")

# 4. dSphs.csv (Table 1)
with open(f"{ROOT}/dSphs.csv") as fh:
    rows = list(csv.DictReader(fh))
print(f"\ndSphs.csv rows: {len(rows)}")
print(f"CSV columns: {list(rows[0].keys())}")
print(f"First row: {rows[0]}")
print(f"Last row: {rows[-1]}")

# 5. TS statistics across all profiles
ts_all_min = +np.inf
ts_all_max = -np.inf
for f in files:
    a = np.load(f"{ROOT}/dSphs/TS_profiles/{f}")
    ts_all_min = min(ts_all_min, a.min())
    ts_all_max = max(ts_all_max, a.max())
print(f"\nGlobal TS range across all {len(files)} profiles: [{ts_all_min:.3f}, {ts_all_max:.3f}]")

# 6. Per-dSph sample: Segue_1 (most-constraining) full TS map
seg = np.load(f"{ROOT}/dSphs/TS_profiles/Segue_1_noprior_bb.npy")
print(f"\nSegue_1 TS map (b-bbar, no J prior):")
print(f"  shape {seg.shape}, max TS = {seg.max():.3f} at mass_idx={np.unravel_index(seg.argmax(), seg.shape)[0]}, sigv_idx={np.unravel_index(seg.argmax(), seg.shape)[1]}")
# Convert to physical units at the maximum
imax, jmax = np.unravel_index(seg.argmax(), seg.shape)
print(f"  at m_chi = {masses[imax]:.1f} GeV, sigma_v = {sigvs[jmax]:.2e} cm^3/s")

# 7. Combined TS (sum over dSphs) for b-bbar, no J prior
combined = np.zeros((40, 60))
for dsph in dsphs:
    f = f"{ROOT}/dSphs/TS_profiles/{dsph}_noprior_bb.npy"
    if os.path.exists(f):
        combined += np.load(f)
print(f"\nCombined TS (sum over {len(dsphs)} dSphs, b-bbar, no J prior):")
print(f"  max TS = {combined.max():.3f}")
print(f"  at m_chi = {masses[np.unravel_index(combined.argmax(), combined.shape)[0]]:.2f} GeV")
# 95% CL threshold for 1 DOF is TS = 2.71 (Wald), but for upper limits we use TS < 0
print(f"  pixels with TS < 0 (= 95% CL excluded): {np.sum(combined < 0)} / {combined.size}")
# Sigma_v at which TS first crosses 0 (upper limit at the mass where TS is most constraining)
imax2 = np.unravel_index(combined.argmax(), combined.shape)[0]
sigv_95 = sigvs[np.searchsorted(-combined[imax2, :], 0.0)]
print(f"  approximate 95% CL sigma_v upper limit at m_chi = {masses[imax2]:.1f} GeV: {sigv_95:.2e} cm^3/s")