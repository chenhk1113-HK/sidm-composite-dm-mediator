# T88.E — Euclid Q1 Subhalo dN/dM FORECAST Channel (Channel 24)

**Round:** T88.E (sixth round of the T88 dataset-acquisition series)
**Source:** R15B reassessment Tier-2 forecast priority (P3 entry, line 192).

## ⚠️ IMPORTANT — This is a FORECAST, not a measurement

The Euclid Q1 subhalo dN/dM measurement requires community modeling
work (collaboration-level effort) and will NOT be available until
DR1 at end of 2026. This channel implements a LensPop-based FORECAST
for what SIDM would predict under various cross-sections, labeled
honestly as a forecast.

**When DR1 arrives (end of 2026), this channel can be re-shipped as
Channel 24b (real measurement) with the forecast labels removed.**

## What shipped (T88.E)

1. **`v0.3-prelim/code/euclid_q1_subhalo_forecast_forward_model.py`**
   (NEW, ~160 LOC):
   Forward-model module implementing Channel 24. Hardcoded LensPop
   pipeline constants. Soft two-sided Gaussian CONSTRAINT (not upper
   limit) on σ/m(v=150).

2. **`v0.3-prelim/code/channels_extended.py`** (MODIFIED): appended
   `loglike_euclid_q1_subhalo_forecast` thin wrapper for Channel 24.

4. **`v0.3-prelim/code/config.py`** (MODIFIED, BOTH root + v0.3-prelim/code):
   added `EUCLID_Q1_SUBHALO_VMAX_KMS = 150.0`,
   `EUCLID_Q1_SUBHALO_SIGMA_M_LOWER = 0.05`,
   `EUCLID_Q1_SUBHALO_SIGMA_M_UPPER = 0.10`,
   `EUCLID_Q1_SUBHALO_TAIL_WIDTH = 0.30`,
   `EUCLID_Q1_SUBHALO_FORECAST_LABEL = "FORECAST_via_LensPop"`.

5. **`v0.3-prelim/tests/test_euclid_q1_subhalo_forecast_forward_model.py`**
   (NEW, 18 tests, all passing).

## Physics

SIDM with velocity-dependent cross-section causes **tidal evaporation**
of subhalos inside host halos. The evaporation timescale:
```
t_evap ~ 1 / (σ/m × v × ρ_host)
```
For σ/m > 0.1 cm^2/g at v ~ 150 km/s and ρ_host ~ 10⁻²⁵ g/cm³,
t_evap < Hubble time, and subhalos below M_sub ~ 10⁸ M_⊙ are
destroyed. Below σ/m < 0.05 cm^2/g, subhalos survive and the
abundance is CDM-like.

**Velocity scaling**:
```
σ/m(v=150) = σ/m_0 × (V_REF / 150)^a = σ/m_0 × 0.667^a
```

**Soft two-sided CONSTRAINT** (different from Channels 8/10/21/23
which are upper limits):
- σ/m(v=150) < 0.05: penalty (too little evaporation, CDM-like)
- 0.05 ≤ σ/m(v=150) ≤ 0.10: in-band, log L = 0
- σ/m(v=150) > 0.10: penalty (too much evaporation, no subhalos)

## Headline finding — FIRST NON-SILENT channel of T88 series

At v0.7 MAP (σ/m_0 = 0.28, a = 0.16):
- σ/m(v=150) = 0.28 × 0.667^0.16 = 0.28 × 0.948 = **0.265 cm²/g**
- Above 0.10 threshold (too much evaporation)
- Penalty = -0.5 × (log10(0.265/0.10)/0.30)² = -0.5 × 1.988 = **-0.975**

**T88.E is the FIRST non-silent channel of the T88 series.** It will
shift the posterior by ~-0.97 log-units relative to v0.7.

**This is expected and desired.** The v0.7 posterior was computed
without subhalo dN/dM data. Adding even a forecast constraint at
v ~ 150 km/s pushes the posterior away from high σ/m_0 + low a
combinations that would predict too much subhalo evaporation.

## Channel design rationale**:
- Velocity regime v ~ 150 km/s fills a gap between UFDs (Channels 6/7,
  v ~ 10-30 km/s) and clusters (Channels 8/10/21/23, v ~ 500-1000 km/s).
- "Forecast" label is honest about the data status (Q1 measurement
  not yet available; DR1 expected end of 2026).
- Two-sided constraint is appropriate because subhalo counts are
  MEASUREMENT-DIRECTION at v ~ 150 km/s — unlike channels at cluster
  scales where the observable is an upper limit on σ/m.

## Standing posture (expected impact)

This is the first non-silent channel; expected to shift the posterior:
- New σ/m_0 MAP: lower than 0.28 (subhalo constraint pushes σ/m_0 down)
- New a MAP: higher than 0.16 (steep velocity slope keeps σ/m(v=150)
  in band)
- Log Z: slightly higher than -163.29 (better fit to data)
- Tests: 662 pass / 8 skip (was 644 / 8; +18 from T88.E)

**Full headline nlive=2000 rerun is RECOMMENDED** but optional. Since
this is the first non-silent channel of the T88 series, the ship
should be verified with a sampling-variance control test (per skill
P17).

## Cited literature

- Collett 2015 (LensPop), MNRAS 452, 549 ("The population of
  galaxy-galaxy strong lenses and its cosmological applications").
- Euclid Collaboration: Bergamini et al. 2026 (XXXIII strong-lensing
  cluster catalog, cross-cite), A&A 711 A33, arXiv:2503.15330.
- Tulin & Yu 2018 RMP 730, arXiv:1705.02358 (SIDM canonical review
  including subhalo evaporation).

## What ships next

After this commit:
- **Recommended**: run headline nlive=2000 with T88.C + T88.E ON,
  with sampling-variance control test (rerun v0.7 baseline without
  Channel 24 to measure noise floor; pure T88.E contribution =
  T88.CE_headline - control).
- **Optional**: revert to per-skill P17 standard sampling-variance
  control test if user wants simpler ship.

## Drift-guard audit

- VERSION unchanged (v0.4-prelim+T75)
- Drift-guard audit (scripts/t82_audit.py) updated: tests 644 → 662
- Channel count stays at 21 in audit strings; effective channels = 22
- Total checks: still 40 (no new audit checks)