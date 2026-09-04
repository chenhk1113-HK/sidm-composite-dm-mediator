# T88.C — Euclid Q1 Strong-Lensing Cluster Catalog (Channel 23)

**Round:** T88.C (fifth round of the T88 dataset-acquisition series)
**Source:** R15B reassessment P2 entry (line 191); reframed after external check.

## Status: BLOCKED — awaiting user go-ahead

**Blocker:** R15B proposal P2 was framed as "Euclid Q1 BCG offsets" with
"14 grade-A clusters" cited. External verification (ESA Cosmos Q1
papers list, 41 papers published 30 June 2026) reveals:

1. **No dedicated BCG-offset paper exists in Euclid Q1.** The Q1
   special issue contains 41 papers; none is a BCG-offset analysis.
2. **The "14 grade-A clusters" claim IS verifiable**, but it refers to
   the strong-lensing cluster catalog (XXXIII, Bergamini+ 2026,
   A&A 711 A33, arXiv:2503.15330), where "14" is the number of clusters
   with P_lens = 1 (secure lensing features), not BCG-offset clusters.
3. **R15B's framing was approximate.** The data exists (14 high-quality
   strong-lensing clusters at v ~ 1000 km/s from Euclid Q1), but the
   *observable* shifts from "BCG-X offset (D_BCG-X)" to "lensing-derived
   mass profile / Einstein radius / shear ratio."

This is a textbook **stale-claim audit failure** (AGENTS.md rule 21
warns against citing unverified IDs). The mitigation is to reframe
T88.C to use the actual published data (XXXIII lensing mass profiles)
while documenting the framing shift in the doc.

## Three options (proposed 2026-09-04)

### Option 1 (Recommended): T88.C reframed to XXXIII lensing density profiles

**What ships:**
- Channel 23 likelihood: compare predicted SIDM core formation at
  v ~ 1000 km/s to lensing-derived Einstein radii / mass profiles of
  the 14 grade-A Euclid Q1 strong-lensing clusters.
- Forward model: σ/m at v=1000 km/s = σ/m_0 × (100/1000)^a = σ/m_0 × 10^(-a).
- Soft one-sided UPPER LIMIT (matching Channel 8 / 10 pattern) since
  the lensing data provides radial mass profiles, not a sharp detection.
- At v0.7 MAP (σ/m_0=0.28, a=0.16): σ/m(v=1000) = 0.28 × 0.692 = 0.194 cm²/g.
  Below 0.5 threshold → channel silent at v0.7.
- 15-20 tests (hand-verified math, no-network constants, T41 wire-in).
- Doc + CHANGELOG + drift-guard (22 effective channels, 626 → 645 tests).

**Time:** ~3 hours.

### Option 2: T88.C as Bhargava+ 2026 (XXXIV) cluster workflow first detections

Cross-validation of XXXIII. Uses the same σ/m at v=1000 framework but
with the XXXIV catalog. Same channel count increment; ~3 hours.

### Option 3: Skip T88.C entirely; ship T88.E (Euclid subhalo dN/dM forecast)

Per R15B Tier-2 forecast priority: use LensPop pipeline, label honestly
as forecast not measurement. Adds a *different* velocity regime
(100-200 km/s) — complementary to T88.A/B/D which are at 500-1000 km/s.
~10-15 hours.

### Option 4: T88-series wrap-up doc (T88_WRAP.md)

Ship a summary noting XRISM+T88.A done, eROSITA T88.B done, T88.D null
done, T88.C+ deferred pending proper data source identification.
Avoids commitment to a reframe. ~30 minutes.

## What needs user input

The R15B audit ("14 grade-A clusters" → BCG-offset → at v ~ 1000 km/s)
turned out to be **approximately correct** (the 14 number IS real, but
the observable is lensing-derived mass profile not BCG offset).

The three meaningful next moves are:
- **Option 1**: ship the reframed T88.C (best science, ~3h)
- **Option 3**: pivot to T88.E forecast (different velocity regime, ~12h)
- **Option 4**: wrap T88 series (close out without committing, ~30 min)

Per AGENTS.md rule 5 ("get explicit approval before ANY state-changing
action with side effects"), I am pausing here for user decision.

## Standing posture preserved (regardless of choice)

- VERSION: `v0.4-prelim+T75` (no bump)
- log Z: -164.23 ± 0.085 (last headline: T88.B)
- σ/m: 0.28 cm²/g
- 21 effective channels
- 626 pass / 8 skip
- Drift-guard: 40/40 ALL CLEAR

## Cited literature

- Euclid Collaboration: Bergamini et al. 2026 (Euclid Q1 - XXXIII
  strong-lensing cluster catalog), A&A 711 A33, arXiv:2503.15330,
  DOI 10.1051/0004-6361/202554577.
- ESA Cosmos Euclid Q1 papers list:
  https://www.cosmos.esa.int/web/euclid/q1-papers (41 papers, retrieved
  2026-09-04).
- v0.3-prelim/docs/consider5_review/R15B_DATASET_AVAILABILITY_REASSESSMENT.md
  (the source of the "14 grade-A clusters" framing, lines 191 / 167-174).

## Awaiting user decision

Reply with one of:
- "go option 1" → ship T88.C with Euclid Q1 XXXIII lensing mass profiles
- "go option 3" → ship T88.E Euclid subhalo dN/dM forecast
- "go option 4" → ship T88_WRAP.md and close out the T88 series
- "stop" → do nothing further