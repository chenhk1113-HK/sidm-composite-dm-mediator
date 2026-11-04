# Stage 3 — IllustrisTNG feasibility measurement (2026-11-04)

**Status: measured. Path 3 (merger-history work on RELHIC-like halos) is viable on TNG100-1 and
TNG50-1 and dead on TNG300-1. The cost is about two orders of magnitude below the ~500 GB estimate
that blocked Stage 3.**

All numbers below were read from the public IllustrisTNG API with the owner's key. Probe scripts and
raw logs live outside the repo (`AppData/Local/hermes/cache/scratch/tng_stage3_probe*.py`,
`tng_probe{7,8,9,10,11}.log/json`); the key is stored at `C:/Users/lamkuenai/.tng_api_key` (mode 600),
never in the repo.

## 1. Candidate window

RELHIC-like band used throughout: `vmax` 15-45 km/s, `primary_flag = 1`, `len_stars < 1`
(starless), halo mass `10^7.5 - 10^9 Msun`, and "gas-rich" adding `mass_gas > 1e-6` (native units).

**API filter contract (measured, do not relearn this the hard way):**
- `mass_log_msun__gt/lt` is **silently ignored**. The filterable field is `mass`, in native
  `SubhaloMass` units of `1e10 Msun/h`; with `h = 0.6774`, `1 unit = 1.4763e10 Msun`, so the band is
  `mass__gt = 2.14e-3`, `mass__lt = 6.77e-2`.
- Always verify a server-side cut by reading records back; a count that does not change when a filter
  is added means the filter name was wrong.
- **Measured size of that trap** (an early probe that used `mass_log_msun__gt/lt` on the same
  vmax/starless/primary cuts, so the mass window was silently absent): it reported band counts
  9,253,224 (TNG300-1), 1,073,192 (TNG100-1), 69,544 (TNG50-1) against the read-back-verified true
  band counts **119 / 425,891 / 39,404**. The inflation is run-dependent (77,000× on TNG300-1,
  2.5× on TNG100-1, 1.8× on TNG50-1), so a wrong filter name is not always obviously wrong. That
  probe's "len_dm >= 1000: 1" for TNG300-1 was an unfiltered statistic and must not be read as a
  band candidate; the band-restricted, read-back number is 0.
- Merger-tree bodies are gzip-compressed even when `content-type: application/json`; `urllib` does
  not decompress them (`gzip.decompress(raw)` is required).
- The list endpoint does not return `len_dm`; fetch the detail record for it.
- The API throttles with an HTML body (not JSON) and intermittently answers `403 Forbidden` / `504`
  on tree endpoints; a retry-with-backoff loop is required, and 403s are inconsistent per subhalo.

## 2. Resolution wall — measured, and it is what kills TNG300-1

Two independent measures agree: the simulation metadata `mass_dm` (DM particle mass) and the catalog
itself (`mass / len_dm` on real records).

| run | `mass_dm` (Msun) | implied from records (Msun) | mass of a 100-particle halo | mass of a 1000-particle halo |
|---|---|---|---|---|
| TNG300-1 | 5.880e7 | 6.948e7 | 6.95e9 | 6.95e10 |
| TNG100-1 | 7.463e6 | 8.792e6 | 8.79e8 | 8.79e9 |
| TNG50-1 | 4.537e5 | 5.308e5 | 5.31e7 | 5.31e8 |

TNG300-1 cannot resolve anything in the band at 100 particles: its minimum 100-particle halo mass
(6.95e9 Msun) is already 7x above the band ceiling (1e9 Msun). TNG50-1 resolves the whole band with
~1900-19,000 particles per halo; TNG100-1 resolves the upper half of the band.

## 3. Counts (snapshot 99, `count` endpoint, filters verified by read-back)

| run | in band | in band AND >= 100 DM particles | in band AND gas-rich AND >= 100 particles |
|---|---|---|---|
| TNG300-1 | 119 | **0** | **0** |
| TNG100-1 | 425,891 | 164,182 | 1,473 |
| TNG50-1 | 39,404 | 39,404 | 1,321 |

**Kill criterion (< 10 RELHIC-like candidates): TNG300-1 fails it (0). TNG100-1 and TNG50-1 pass it
by two orders of magnitude.**

## 4. Merger-tree access and payload size (measured, size-only requests)

Per-subhalo trees are reachable through the API; the payload is small.

| run | subhalo | `len_dm` | `sublink/simple.json` | `sublink/full.hdf5` | `sublink/mdb.hdf5` | `lhalotree/full.hdf5` |
|---|---|---|---|---|---|---|
| TNG100-1 | 1532355 | 126 | 200, 0.6 KB | 403 | 200, 64 KB | 200, 64 KB |
| TNG50-1 | 1080899 | 2104 | 200, 0.7 KB | 403 | 403 | 200, 192 KB |
| TNG50-1 | 1084928 | 1990 | 403 | 200, 320 KB | 403 | 200, 192 KB |

A parsed JSON tree for one candidate: 2,736 bytes, 97 main-progenitor nodes, 5 recorded mergers
(TNG50-1 subhalo 873037). Availability is per-subhalo inconsistent (`sublink_gal/*` mostly 403/404),
so a real pipeline must try the formats in order and retry.

**Cost of a Stage-3 sample:** 100 candidates = ~70 KB of JSON trees or ~20-30 MB of HDF5 — not
500 GB. The ~500 GB figure is the bulk MergerHistory supplementary download, which per-subhalo API
reads do not require. The real cost is request time with pacing (the API throttles at roughly the
10-15 s/request level) plus whatever analysis follows.

## 5. Recommended sample (owner decision needed)

- **Primary: TNG50-1** — 1,321 gas-rich resolved candidates, 100-particle halos are 5.31e7 Msun so
  the whole 3.2e7-1e9 Msun band is resolved, and its trees are readable. Downside: small box
  (35 Mpc/h), so few massive groups and no Milky-Mass host guarantee.
- **Secondary: TNG100-1** — 1,473 gas-rich resolved candidates, better host-halo statistics, coarser
  resolution (100 particles = 8.79e8 Msun, i.e. only the top of the band is marginally resolved).
- **Drop TNG300-1** for this purpose (0 resolved candidates in the band).
- Suggested first cut: 40-60 candidates from TNG50-1 (band-central, 100-1000 particles), plus 20-40
  from TNG100-1 as a resolution control at matched `len_dm`. Total transfer well under 50 MB.

## 6. What this does **not** establish

- It does not show that any TNG halo is a Cloud-9 analogue; `vmax` and mass windows are coarse
  proxies, and TNG has no Globular-Cluster tracers.
- It does not license a merger-history claim yet: tree *availability* is measured, tree *content
  quality* for starless low-mass subhalos is not.
- `mass_dm` and `mass/len_dm` differ by ~18% (catalog `mass` is the subhalo's own bound mass); the
  resolution conclusion is unaffected because the gap is nowhere near a factor of 7.
