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

## 3. Per-node growth curves (in progress at the time of writing)

`v0.3-prelim/code/tng_stage3_nodes.py` walks each main lineage and fetches the subhalo **detail**
record for every 4th node, giving M(z), V_max(z), len_dm(z), r_half(z) growth curves. First pass
status: **1,290 node rows** stored in `v0.3-prelim/data/external/tng/stage3_nodes/nodes.jsonl`,
3 failed reads (0.2%), ~2.3 s per node with 1.5 s pacing — ~2,150 requests for the tier-1 sample,
well under a megabyte. Resumable: it appends and skips stored (run, halo, snap, id) tuples.

**Defect found and fixed in this script during its own first run:** `snapshot_z.json` is JSON, so
its keys come back as **strings**, while the tree lineages use **int** snapshot numbers —
`SNAP_Z.get(run).get(snap)` therefore returned `None` and the rows written before the fix have
`z = null`. Fixed (`int(k)` on load). The already-written rows are corrected locally by a
re-join against the cached table; no re-fetch is needed. The snapshot→z table itself was taken
from the API (`{run}/snapshots/`, 100 entries/run, e.g. TNG50-1 snap 50 → z = 0.9973, snap 0 →
z = 20.0465), not from memory.

---

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

- It does not yet produce a **fit**: no likelihood has been evaluated on these halos. The trees
  give lineage topology and the node fetch gives growth curves; connecting them to the SIDM model
  (`phase_g2_merger_history.py`, `phase_g4_pipeline.py`) is still to be done.
- It does not measure a **mass–velocity relation** for the anchor in the statistical sense yet —
  the ceiling above is a count ladder plus 24 read-back records, not a fitted distribution.
- It says nothing about TNG300-1 (dropped: zero RELHIC-band halos with ≥ 100 DM particles) or
  about TNG100-1 at anchor masses (its RELHIC-band halos only have 104–132 DM particles, so the
  anchor-mass tier is TNG50-1-only by resolution).
- The anchor-cell result is a **tension flag**, not a verdict on Cloud-9.

## 6. Next concrete steps (in dependency order)

1. Backfill `z` into `nodes.jsonl` and run the growth-curve summary (M(z), V_max(z), merger time
   distribution) → replaces the asserted × 0.7 / × 8.0 Phase G2 multipliers with measured values.
2. Match the anchor tier to the z = 0 cell (V_max 28–30, 22 objects) and report the anchor as
   formation-redshift-dependent, or re-anchor explicitly.
3. Only then decide whether Stage 3 enters the canonical fit or stays a plausibility check.
