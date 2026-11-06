## IllustrisTNG figures that arrived on their own (2026-11-06)

### 1. Selection rules actually applied

- Snapshot: z=0 (snap 99)
- Stellar particles: len_stars = 0 for every row (star-free selection)
- Gas: present in every row; gas mass range 1.6239e5 – 2.0520e6 Msun; median 3.1739e5 Msun; len_gas 1–8
- Tier-1 sample (candidates.csv): 90 accepted halos (60 TNG50-1 + 30 TNG100-1)
- Tier-2 anchor tier (Cloud-9 mass window): 25 accepted TNG50-1 halos
- Selection filter: zero stellar particles, gas particles present, fixed mass window, V_max band, len_dm band
- Node fetch: 2090 rows, 4 failed requests, stride 4, wall 5045 s, 1,160,502 bytes

### 2. Tier-1 dwarf-analogue sample

| Property | TNG50-1 (60 halos) | TNG100-1 (30 halos) |
|---|---|---|
| M_total (Msun) | 6.85326e8 – 9.98509e8 (median 9.01166e8) | 7.76941e8 – 9.86035e8 (median 9.26329e8) |
| V_max (km/s) | 15.0509 – 18.8130 (median 16.5474) | 15.0003 – 19.1689 (median 16.4868) |
| len_dm | 1510 – 2200 (median 1985.5) | 104 – 132 (median 124) |
| gas mass (Msun) | 162386 – 501919 (median 221435) | 693829 – 2.05196e6 (median 826690) |
| len_gas | 2 – 8 | 1 – 2 |
| merger trees OK | 60/60 | 30/30 |

Source: `v0.3-prelim/data/external/tng/stage3_sample/candidates.csv` (per-halo detail read-backs), recomputed
min/median/max per run. Combined across both runs (from `v0.3-prelim/data/results/tng_stage3_growth_summary.json`):
n_halos 90, V_max 15.0003 / 16.5062 / 19.1689 km/s, len_dm 104 / 1841 / 2200.
`nodes_stats.json` holds fetch counts only (rows, failed, stride, wall time, bytes), not per-halo values.

### 3. Tier-2 Cloud-9-mass anchor tier

| Property | Value |
|---|---|
| n_halos | 25 (all TNG50-1) |
| M_total (Msun) | 4.1197e9 – 5.8016e9 (median 4.8282e9) |
| V_max (km/s) | 25.0131 – 28.3375 (median 26.3222) |
| len_dm | 9019–12781 |
| assembly_frac z0.5 median | 0.7788729966216984 |
| assembly_frac z1 median | 0.5372478809768287 |
| assembly_frac z2 median | 0.28912400982195346 |
| assembly_frac z3 median | 0.1457567320656894 |
| vmax_growth median_vmax0_over_vmax_at_z1 | 1.0439025595414568 |
| mergers median_total | 29 |
| mergers quiet_fraction | 0.0 (all 25 merged after z=1) |
| mergers median_earliest_merger_z | 7.00541704554453 |
| mergers median_latest_merger_z | 0.0736613846564387 |

Verified from nodes_stats.json stage3_anchor by_run TNG50-1.

### 4. The V_max ceiling scan (within Cloud-9 mass window at z=0)

| V_max range (km/s) | Halos in TNG50-1 |
|---|---|
| 28–29 | 16 |
| 29–30 | 6 |
| 30–31 | 0 |
| 31–34 | 0 |

Single highest: subhalo 906682 at V_max 29.5767 km/s (M 5.8974e9 Msun, gas 4.5911e7 Msun, len_dm 12896, half-mass radius 11.1849 kpc).

Cloud-9's published maximum rotational velocity is ~31.1 km/s, so no z=0 halo in this window reproduces Cloud-9's mass-and-speed combination.

Verified from tng_vmax_envelope.json: ladder [28,29]=16, [29,30]=6, [30,31]=0, [31,34]=0.

### 5. Growth and merger statistics (tng_stage3_growth_summary.json)

**Growth since z=1:**
- ratio V_max(z=0)/V_max(z=1) = 1.0439 (anchor tier), 1.0403 (tier-1 TNG100-1), 1.0214 (tier-1 TNG50-1)

**Anchor assembly fractions of present-day mass:**
- median 0.779 assembled by z=0.5, 0.537 by z=1, 0.289 by z=2, 0.146 by z=3

**Anchor z_form(mass/2) median:** 0.1753 (anchor halos reach half their present mass only at z ≈ 0.18);
tier-1 combined 0.9352 (TNG50-1 1.3629, TNG100-1 0.7693).

**Merger counts:**
- Anchor: median 29 mergers total (max 46), of which median 17 happened at z >= 1 and median 12 since z=1
- Tier-1 combined: median 6 mergers total (max 15), median 4 at z >= 1 and median 1 since z=1
  (medians are taken per quantity, so they need not add exactly)
- Tier-1 by run: TNG50-1 median 7.5 total (25 of 60 have merged nothing since z=1); TNG100-1 median 0 total

**Quiescent-since-z=1 fraction:**
- Anchor: 0.000
- Tier-1 TNG50-1: 0.2667
- Tier-1 TNG100-1: 0.8333
- Tier-1 combined: 0.4556

**Merger z range:**
- Earliest merger median: z=7.005 (anchor) / 5.929 (tier-1 combined)
- Latest merger median: z=0.0737 (anchor) / 0.535 (tier-1 combined), i.e. anchor halos are still merging today

115 merger trees retrieved.

### 6. What these figures can and cannot support

- These are IllustrisTNG simulation sample measurements, obtained from the public TNG API per-subhalo detail read-backs.
- They are NOT measurements of the real Cloud-9 and NOT a constraint on this project's cross section.
- Source artifacts: `v0.3-prelim/data/external/tng/stage3_sample/candidates.csv` (90 rows),
  `stage3_anchor/candidates.csv` (25 rows), `stage3_sample/trees/` (90 files), `stage3_anchor/trees/` (25 files),
  `stage3_nodes/nodes.jsonl` (2090 rows), `stage3_nodes_anchor/nodes.jsonl` (824 rows),
  `stage3_nodes*/nodes_stats.json` (fetch counts), `v0.3-prelim/data/results/tng_stage3_growth_summary.json`,
  `C:/Users/lamkuenai/AppData/Local/hermes/cache/scratch/tng_vmax_envelope.json` (ceiling scan),
  `.../tng_probe9.json` (catalog particle-mass floors). Every number above is recomputable from those files.
- The dwarf-analogue tier (star-free, gas-bearing, ~15–19 km/s) is usable as a test bed.
- The Cloud-9-mass anchor tier is NOT quiescent (0 of 25 quiet since z=1) and its accepted halos top out at
  28.3375 km/s; widening the scan to the whole Cloud-9 mass cell (100 candidates, 4.154e9–5.995e9 Msun) finds a
  ceiling of 29.577 km/s and zero halos at or above 30 km/s. So the relaxed-anchor assumption behind the project's
  Cloud-9 model is unsupported by this sample.
- Growth since z=1 is only ~4.4%, which is why growing the halo in time cannot close the 29.58 → 31.1 km/s gap.
### 7. Parent re-verification (2026-11-06)

This doc was drafted by a delegated read-only study. Every table value was then recomputed independently
from the CSVs and the growth summary by the parent session. Five values were wrong in the draft (tier-1
mass and V_max medians mixed up between runs; anchor merger total median quoted as 17 instead of 29;
tier-1 combined merger median 5 instead of 6; tier-1 combined z_form 0.959 instead of 0.9352; and the
29.58 km/s ceiling attributed to the accepted anchor tier instead of the wider mass-cell scan). They are
corrected above. The fetch counts (2090 rows / 4 failures; 824 rows / 2 failures; 115/115 trees) and the
gas statistics were correct as drafted.
### 8. Role of this sample (decided 2026-11-06)

The owner decided on 2026-11-06 that IllustrisTNG serves as a framework check, not as a test
that a Cloud-9 analogue has to exist in the simulation (decision D8, recorded in
docs/FINDINGS_FOR_FUTURE_DELIBERATION.md section 27.8). Sections 4-5 of this file therefore read
as sample characterisation: the ceiling and the merger activity describe the simulated volume,
and the missing Cloud-9 look-alike is something to report, not to repair. Halos of Cloud-9's
mass do exist in TNG50-1 (25 accepted, 100 scanned); what they lack is the anchor's combination
of speed and quietness.
