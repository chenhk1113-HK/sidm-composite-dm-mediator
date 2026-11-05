# Stage 3 — IllustrisTNG merger-history sample, as actually built (2026-11-04)

Companion to `docs/STAGE3_TNG_FEASIBILITY_2026-11-04.md` (which records the *feasibility*
measurements before any sample existed). This file records **what is on disk now**, how it was
selected, what it has already been used to measure, and what it does **not** support.

Everything below is a measurement from this host on 2026-11-04, with the query or file that
produced it. Nothing here is quoted from memory or from the portal's documentation.

---

## 1. Two tiers, both built with the same script

`v0.3-prelim/code/tng_stage3_build.py` (band parameters env-overridable, so tier 2 is the same
code and not a fork). Per-subhalo API reads only — the ~500 GB supplementary MergerHistory
download was never attempted.

| | tier 1 `stage3_sample` | tier 2 `stage3_anchor` |
|---|---|---|
| purpose | low-mass RELHIC-velocity band, resolution control | bracket the Cloud-9 anchor mass |
| runs | TNG50-1 (60) + TNG100-1 (30) | TNG50-1 (25) |
| V_max window (km/s) | 15 – 45 | 25 – 30 |
| M window (M☉) | 3.16e7 – 1e9 | 4e9 – 6e9 |
| other cuts | starless (`len_stars<1`), primary, gas ≥ 1.476e5 M☉, 100 ≤ len_dm ≤ 4000 | same, len_dm ≤ 20000 |
| accepted / requested | 90 / 90, **0 refused, 0 tree failures** | 25 / 25, **0 refused, 0 tree failures** |
| main-lineage nodes (min/med/max) | 56 / 88 / 98 | 91 / 97 / 99 |
| merger events in tree (min/med/max) | 0 / 6 / 15 | **15 / 29 / 46** |
| disk | 90 trees, 0.13 MB + 12.8 KB csv | 25 trees, 0.05 MB + 3.7 KB csv |

Tier-1 detail (per run):

| run | M (M☉) | V_max (km/s) | len_dm | gas (M☉) |
|---|---|---|---|---|
| TNG50-1 | 6.85e8 / 9.01e8 / 9.99e8 | 15.05 / 16.55 / 18.81 | 1510 / 1986 / 2200 | 1.6e5 / 2.2e5 / 5.0e5 |
| TNG100-1 | 7.77e8 / 9.26e8 / 9.86e8 | 15.00 / 16.49 / 19.17 | 104 / 124 / 132 | 6.9e5 / 8.3e5 / 2.1e6 |

Tier-2 detail: M 4.12e9 / 4.83e9 / 5.80e9 M☉, V_max 25.01 / 26.32 / 28.34 km/s,
len_dm 9019 / 10526 / 12781, gas 2.2e6 / 5.2e7 / 7.9e7 M☉.

**Two things the tables settle.** (a) The requested tier-1 mass window was not reachable at its
low end: `vmax__gt=15` alone gives **count = 0** for `mass__lt=6.77e-3` (M < 1e8 M☉) in TNG50-1 —
at z = 0 no subhalo below ~1e8 M☉ has V_max ≥ 15 km/s, so the band's mass floor is inert and the
sample is what the V_max floor allows. (b) Merger activity is strongly mass-dependent in this
population: RELHIC-mass halos (tier 2) carry **15–46** merger events in their main trees against
**0–15** for the tier-1 low-mass halos. That is the number `phase_g2_merger_history.py`'s
quiescent/active modulator (× 0.7 / × 8.0) has been asserting from literature labels; the sample
now makes it measurable instead of asserted.

Manifests: `v0.3-prelim/data/results/tng_stage3_sample_manifest.json`,
`tng_stage3_anchor_manifest.json`. Candidate tables:
`v0.3-prelim/data/external/tng/stage3_{sample,anchor}/candidates.csv` (gitignored data dir;
manifests are tracked so the selection is auditable).

---

## 2. What the sample already found: the Cloud-9 anchor sits above the simulated ceiling

The canonical anchor is **M₂₀₀ = 5e9 M☉ with V_max = 31.12 km/s** (Cloud-9 = M94 RELHIC), used by
`predict_sidm_halo(5e9, 31.12, 1.4, σ)`. Counting the TNG50-1 z = 0 population in the same cell
(primary, starless, gas ≥ 1.476e5 M☉, len_dm ≥ 100, M 4–6e9 M☉), via
`scripts/tng_vmax_envelope.py`:

| V_max window (km/s) | 28–29 | 29–30 | 29.5–30.0 | 29.9–30.1 | 30–31 | 31–34 |
|---|---|---|---|---|---|---|
| count | 16 | 6 | 2 | **0** | **0** | **0** |

Read-back of 20 individual detail records from that cell confirms the ladder is real and not a
filter artifact — the highest V_max actually present is **29.58 km/s** (subhalo 906682,
M = 5.90e9 M☉, gas 4.59e7 M☉, len_stars = 0, len_dm = 12896), then 29.10 (878879, 5.34e9 M☉):

```
id 878879  Vmax 29.10  M 5.34e9  gas 2.70e7  len_stars 0  r_half,dm 9.33 kpc
id 906682  Vmax 29.58  M 5.90e9  gas 4.59e7  len_stars 0  r_half,dm 11.18 kpc
id 923996  Vmax 25.43  M 4.15e9  gas 9.02e6  len_stars 0  r_half,dm  9.81 kpc
```

Dropping the starless and gas cuts opens the cell: M 4–6e9 with V_max 30–35 has **2041** objects
at z = 0, but the four read back show why they fail the RELHIC cuts — 840011 (V_max 34.46,
M 5.39e9) has **gas = 0** and 123 stars; 843246 (30.42, 4.41e9) gas 0, 279 stars; 845100 (31.84,
4.03e9) gas 0, 22 stars. So at z = 0 a halo that massive is either stellar or gas-poor, not both.

The anchor does exist **at higher redshift** — same cell (M 4–6e9, starless, gas-bearing,
V_max 28–34), TNG50-1:

| snapshot | 99 | 90 | 80 | 70 | 60 | 50 |
|---|---|---|---|---|---|---|
| z | 0.000 | 0.110 | 0.261 | 0.440 | 0.676 | 0.997 |
| count | 22 | 31 | 39 | 54 | 54 | 40 |

**Honest reading.** The (M, V_max) pair the project anchors on is not realized by any starless
gas-bearing TNG50-1 halo at z = 0 — the ceiling is ~29.6 km/s — but the same cell is populated at
z ≈ 0.1–1.0. Two consequences, both decision-relevant:

1. If Stage 3 is used to justify the anchor, the comparison must be made **at the halo's
   formation redshift**, not at z = 0, and the 22-member z = 0 cell (the nearest realizable
   objects, V_max 28–30) should be the matched sample.
2. `M200 = 5e9` with `V_max = 31.12` implies a lower concentration than TNG50-1 produces for
   starless gas-bearing halos at that mass (the realized members have r_half,dm 9.3–18 kpc). This
   is a **consistency test of an observation-derived anchor against a simulated mass–velocity
   relation**, not a refutation: RELHIC M₂₀₀ and V_max come from light, and both are model-dependent.

---

## 3. Growth and merger timing measured from the stored products (2026-11-04)

`v0.3-prelim/code/tng_stage3_growth_summary.py` reads only the local products (90 + 25 merger
trees, 2,090 node rows, the API snapshot→redshift table) and writes
`v0.3-prelim/data/results/tng_stage3_growth_summary.json`. Masses use the run's own
`SubhaloMass` unit, 1e10 Msun/h with h = 0.6774, the Planck-II value the IllustrisTNG papers use.
`z` was backfilled into all 2,090 rows (0 missing). Merger redshifts come from the snapshot id the
tree reports for each merger event.

Coverage first, because it limits what the numbers mean:

| stored lineage | TNG50-1 tier 1 (60) | TNG100-1 tier 1 (30) | TNG50-1 anchor tier (25) |
|---|---|---|---|
| main-lineage nodes in the tree (median) | 96 | 77 | 97 |
| deepest snapshot the subhalo is tracked to (median) | 4 (z = 10.0) | 23 (z = 3.49) | 3 (z = 11.98) |
| nodes stored per halo (stride 4 / 3) | 25 | 20 | 33 |
| halos whose stored lineage reaches z ≥ 3 | **60 / 60** | **19 / 30** | **25 / 25** |

Tier-1 growth and merger statistics (median, with the quartile spread where it matters):

| quantity | TNG50-1 | TNG100-1 |
|---|---|---|
| M(z=0) [Msun] | 6.85e8 – 9.99e8 (median 9.01e8) | 7.77e8 – 9.86e8 (median 9.26e8) |
| V_max(z=0) [km/s] | 15.05 – 18.81 (median 16.55) | 15.00 – 19.17 (median 16.49) |
| DM particles at z=0 | 1510 – 2200 (median 1986) | 104 – 132 (median 124) |
| M(z)/M(0) at z = 0.5 | 0.834 (q25 0.775 / q75 0.865) | 0.771 (0.686 / 0.879) |
| M(z)/M(0) at z = 1 | 0.696 (0.653 / 0.737) | 0.648 (0.568 / 0.747) |
| M(z)/M(0) at z = 2 | 0.446 (0.381 / 0.520) | 0.445 (0.329 / 0.502) |
| M(z)/M(0) at z = 3 | 0.308 (0.223 / 0.366) — all 60 halos | 0.392 (0.297 / 0.422) — **only the 19 halos that reach z ≥ 3** |
| redshift where the lineage held 50% of its z=0 mass | 1.36 (1.28 / 1.45) | 0.77 (0.54 / 0.96) |
| V_max(z=0) / V_max(z≈1) | 1.021 | 1.040 |
| main-progenitor mergers (total) | median 7.5 (6 / 9), max 15 | median 0 (**max 1**) |
| mergers at z < 1 | median 2, max 8 | median 0, max 1 |
| halos with no merger after z = 1 | 16 / 60 → quiet fraction **0.267** | 25 / 30 → **0.833** |
| most recent merger redshift (median) | 0.535 | 0.500 (the only merger some of them have) |

Anchor tier (the Cloud-9 mass scale), same script, `stage3_nodes_anchor` (824 rows, 2 request
failures out of 826, 470 KB):

| quantity | TNG50-1 anchor tier (25 halos, 4–6e9 Msun) |
|---|---|
| M(z=0) [Msun] | 4.12e9 – 5.80e9 (median 4.83e9) |
| V_max(z=0) [km/s] | 25.01 – 28.34 (median 26.32) |
| DM particles at z=0 | 9,019 – 12,781 (median 10,526) — well resolved, no resolution wall here |
| M(z)/M(0) at z = 0.5 / 1 / 2 / 3 | 0.779 / 0.537 / 0.289 / **0.146** |
| redshift where the lineage held 50% of its z=0 mass | **0.175** (q25 0.132 / q75 0.277) |
| V_max(z=0) / V_max(z≈1) | 1.044 |
| main-progenitor mergers | median 29 (26 / 32), max 46 |
| mergers at z < 1 | median 12, max 22 |
| halos with no merger after z = 1 | **0 / 25** → quiet fraction **0.000** |
| most recent merger redshift (median) | **0.074** |

Two consequences, both measured rather than assumed:

1. **Redshift evolution cannot close the Cloud-9 velocity gap.** These halos grow V_max by only
   4.4% between z ≈ 1 and z = 0. The ceiling found in section 2 was 29.58 km/s against Cloud-9's
   31.12 km/s, a +5.2% requirement, and the anchor-cell population was already counted at higher
   redshift. So "match the anchor at formation redshift instead of z = 0" (option D8) does not
   rescue the velocity by itself: the simulated halos in that cell are simply a few percent below
   the observed value at every redshift, and the tension is a mass–velocity offset, not a timing
   artifact.
2. **The mass-matched simulated analogue of Cloud-9 is not quiescent.** All 25 anchor halos merged
   after z = 1, and the median one merged at z = 0.074 (~0.9 Gyr ago). They also assemble very
   late — half their z = 0 mass arrived after z ≈ 0.18. That is a property of what TNG50-1 puts in
   the 4–6e9 Msun, gas-rich, starless, primary-flagged cell, and it is the population this sample
   selected. It does **not** contradict Cloud-9 being quiescent (Cloud-9 is a ~1e9 Msun dwarf in
   the M94 group, an order of magnitude less massive, and its isolation is an observational
   statement), but it does mean these 25 halos are **not** drop-in Cloud-9 analogues for the
   `phase_g2_merger_history.py` labels: if they were used as "quiescent", the sample's own merger
   lists would say otherwise. The quiescent analogue in this sample is the tier-1 population
   (26.7% quiet at z < 1) at ~1e9 Msun, which is also the mass scale Cloud-9's host actually has.

**The finding that matters most is a limitation, not a result: TNG100-1 cannot supply merger
histories in this mass band.** Its 1e9 Msun subhalos are only tracked back to snapshot ~23
(z ≈ 3.5) and their merger lists contain **0 events for 30 of 30 halos' medians (max 1)**. Their
apparent 83% "quiet" rate is therefore a subhalo-tracking artifact — the ancestors were never
found — and reading it as "these halos experienced no mergers" would be a false claim. TNG50-1,
which tracks the same masses back to z ≈ 10, gives 7.5 mergers per halo and a 26.7% quiet rate.
Any merger-history statistic in the RELHIC band must come from TNG50-1; TNG100-1 stays a mass /
V_max resolution control only (its 104–132 DM particles already said so).

**What this does to the Phase G2 multipliers.** `phase_g2_merger_history.py` currently assigns
history labels per halo by hand from observation (Cloud-9 quiescent, Fornax/Sculptor/Draco active)
and applies ×0.7 / ×8.0 / ×1.0 from Silverman+ 2026 §3, with an assumed `f_active ~ 0.5`. The
measured analogue for **field** ~1e9 Msun halos in TNG50-1 is f_active(z < 1) = **0.73** (73% have
at least one merger after z = 1), and half of them merged within the last ~7.5 Gyr (median last
merger z = 0.535). Two honest conclusions: (i) the sim does not contradict the observation-based
labels — Cloud-9's isolation is exactly the minority population the sim puts at ~27%; (ii) the sim
does **not** support `f_active ~ 0.5` as a generic property of this mass range, so that number must
stay a stated literature assumption for the labelled halos and must not be quoted as simulation-
derived. The ×0.7 / ×8.0 magnitudes themselves are **not** measured by this work — only which
halos are quiet and when they last merged is.

Measured anchor-side growth is in the table above; it argues against the "match at formation
redshift" reading of D8 and for treating the anchor gap as a mass–velocity offset.

## 4. API contract, as measured (additions to the feasibility doc)

- Header is `api-key`; `X-API-Key` → HTTP 403.
- Detail endpoint `/{run}/snapshots/{snap}/subhalos/{id}/` returns ~75 fields (mass, vmax,
  veldisp, len_dm, mass_gas, halfmassrad_dm, parent, prog_sfid/snap, desc_sfid/snap, …).
- **Silently ignored filters** (each verified by the returned `count` not changing):
  `subhalo_id=<id>` as a list filter (returns the unfiltered 4,371,211-row set), `fields=…`
  on list queries, `order=…&sorting=…` (a `order=vmax&sorting=desc` request returned
  unsorted pages: 25.98, 29.10, 23.59, 26.55, …), and `count=3` (returned a full page).
  `id=<id>` **does** work (count = 1). `mass_log_msun__gt/lt` was already known to be ignored.
- Rule this keeps enforcing: **every server-side filter must be verified by read-back** before a
  count from it is quoted. Two of the three "empty cell" results here would have been reported as
  physics bugs if the detail read-backs had not confirmed them.
- Bodies may be gzip; HTML bodies and HTTP 503 mean throttle → retry with backoff. Sustained
  request rates above ~1/s start returning 503 on this host.

Resource ledger for the whole Stage-3 build today: ~2,400 API requests, 115 merger trees
(0.18 MB), ~1,290 node rows (< 0.5 MB), ~75 min of wall-clock spread over paced background runs.
Nothing was downloaded in bulk; the PC's disk, RAM and GPU were not stressed.

---

## 5. What Stage 3 does **not** establish yet

- It does not yet produce a **fit**: no likelihood has been evaluated on these halos. Section 3
  measures growth and merger timing; connecting those to the SIDM model
  (`phase_g2_merger_history.py`, `phase_g4_pipeline.py`) is still to be done.
- It does not measure the **×0.7 / ×8.0 collapse-time multipliers**. Those magnitudes come from
  Silverman+ 2026 §3 and remain an assumption; what is measured here is quiet/active membership
  and merger timing only.
- It does not measure a **mass–velocity relation** for the anchor in the statistical sense yet —
  the ceiling above is a count ladder plus 24 read-back records, not a fitted distribution.
- It says nothing about TNG300-1 (dropped: zero RELHIC-band halos with ≥ 100 DM particles) or
  about TNG100-1 at anchor masses (its RELHIC-band halos only have 104–132 DM particles, so the
  anchor-mass tier is TNG50-1-only by resolution).
- The anchor-cell result is a **tension flag**, not a verdict on Cloud-9.

## 6. Next concrete steps (in dependency order)

1. ~~Backfill `z` and run the growth-curve summary~~ — **done 2026-11-04** (section 3). What it
   replaced is the *quiet/active fraction*, not the ×0.7 / ×8.0 magnitudes, which stay a literature
   assumption until a simulation-based estimate of collapse-time shift exists.
2. Match the anchor tier to the z = 0 cell (V_max 28–30, 22 objects) and report the anchor as
   formation-redshift-dependent, or re-anchor explicitly.
3. Only then decide whether Stage 3 enters the canonical fit or stays a plausibility check.
