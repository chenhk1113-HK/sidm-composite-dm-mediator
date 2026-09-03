# R15-B — Cosider5.docx Re-assessment: Dataset Availability

**Source:** `consider5_source.docx` (R15, audited 2026-09-03 in
`README.md` of this directory).

**Trigger:** User redirected after R15 recommended "P3 (Euclid Q1 subhalo)
→ fresh data; needs analysis pipeline" as Tier-3 priority. Re-assessment
asks: which datasets are **actually available right now**, vs the R15 audit's
listing of 6 proposals.

**Scope of this document:** Per-dataset ground-truth check (downloadable
catalog, statistical power at project's velocity range, integration cost
into T41 joint fit). Standing posture preserved: `v0.4-prelim+T75`, log Z =
−163.29 ± 0.085, σ/m = 0.27 cm²/g.

**Methodology (per AGENTS.md rules 21, 22, 23, 26):**

1. Every concrete claim in `consider5_source.docx` was verified against
   primary sources (arXiv, ESA archive, HEASARC, journal DOIs). Search
   hits were filtered to first-3 abstracts per query; abstract-level
   facts only, not body-text inferences.
2. Each proposal is evaluated on 4 axes: (a) **publicly downloadable
   catalog today**, (b) **statistical power at the project's velocity
   range** (10–1000 km/s), (c) **integration cost** (per joint-fit
   onboarding skill's 7-phase pattern), (d) **constraint orthogonality**
   to existing 19 channels.
3. The R15 audit ("`README.md`") is preserved unchanged; this document
   SUPERSEDES the recommended acquisition order from R15.
4. No new dependencies were installed (AGENTS.md rule 17, standing rule
   in `yang2026_likelihood.py` docstring). All fact-checks use existing
   `web_search` + `web_extract` tools.

---

## Per-proposal availability audit

### P1 — JWST Deep Cluster Strong Lensing (AS1063, Abell 2744, SMACS 0723)

**R15 audit verdict:** Marginal — Channel 8 (cluster upper limit) covers.

**Re-assessment:**

| Axis | Finding |
|---|---|
| Data | ✅ Published. Diego+ 2026 (arXiv:2602.15940, 9 pages) and Williams+ (arXiv:2602.12332) are public. AS1063 has 1 confirmed core radius measurement. Abell 2744 + SMACS 0723 have older JWST/HST data from 2022-2023. |
| Velocity | v ≈ 1000 km/s — covered by existing Channel 8 (Bullet Cluster 95% CL). |
| Statistical power | ⚠️ Single-cluster core-radius measurements are weak priors. The Diego+ 2026 paper itself flags fuzzy-DM as alternative; not a clean SIDM-only signal. R15 audit already noted this. |
| Cost | ⚠️ High: per-cluster lens modeling (free-form inversion, GRALE/WSLAP), 5-10h per cluster for code + tests. Would need ≥3 clusters for a real prior. |
| Orthogonality | ❌ Low. Channel 8 already constrains σ/m at v≈1000 km/s from the opposite direction (upper limit, not detection). Adding 1-3 cluster cores is incrementally informative, not transformative. |

**Verdict:** **DEFER.** Channel 8 covers; the marginal cost-benefit does not
justify the per-cluster lens modeling investment when the same observation
is consistent with fuzzy-DM.

---

### P2 — Euclid Q1 Cluster Catalogs (BCG offsets, ρ(r))

**R15 audit verdict:** Marginal — Channels 3+8 cover.

**Re-assessment:**

| Axis | Finding |
|---|---|
| Data | ✅ Published. Euclid Q1 (released 2025-03-19, 63.1 deg²). Bergamini+ 2025 (arXiv:2503.15330, A&A 711 A33, 2026) presents **83 cluster lenses with 𝒫lens > 0.5, of which 14 have 𝒫lens = 1**. Cluster density profiles are public. |
| Velocity | v ≈ 1000 km/s — same as P1, same Channel 8 coverage. |
| Statistical power | ⚠️ Medium. 14 grade-A clusters is a real sample. BCG offsets would constrain σ/m via core sloshing. |
| Cost | ⚠️ Medium: BCG offset extraction is straightforward (FITS + centroid), ~5h for code + tests. |
| Orthogonality | ⚠️ Medium. Different from Channel 8 (which is upper limit from kinematics) — BCG offset gives a *detection* of core physics, not a limit. |

**Verdict:** **CONSIDER as Tier-2 candidate** if the velocity gap problem
is the priority. Better than P1 because the data is pre-processed (no
per-cluster modeling) and the observable (BCG offset) is mechanistically
distinct from Channel 8's kinematic limit.

---

### P3 — Euclid Q1 Strong Lensing Substructure Sample (dN/dM)

**R15 audit verdict:** Genuinely useful — quantitative upgrade over Channel 6.

**Re-assessment (this is the option that triggered the user redirect):**

| Axis | Finding |
|---|---|
| Data | ⚠️ **Partially available.** Walmsley+ 2025 (arXiv:2503.15324) catalogs **497 galaxy-galaxy strong lenses** in Q1 (not 170,000 — the doc's claim is the full-survey forecast for end-of-decade, not Q1). The substructure dN/dM is **NOT in the public catalog** — it requires per-lens modeling (LEMON, Busillo+ 2025; Lines+ 2025) then meta-analysis. |
| Velocity | v ≈ 100-200 km/s — partial overlap with Channel 6 (Yang+ 2026 single-paper σ ~ 0.3 dex width). |
| Statistical power | ⚠️ **Lower than R15 estimated.** With 497 lenses and per-lens modeling complexity, the expected dN/dM measurement has comparable statistical power to Yang+ 2026, not "quantitative upgrade". A real upgrade requires the full-survey 100k lenses (end-of-decade). |
| Cost | ⚠️ **Higher than R15 estimated.** Two viable paths: (a) Forecast channel — use LensPop to predict dN/dM from the 497 host-mass distribution. ~10-15h, but it's a forecast, not a measurement. (b) Real-measurement channel — only feasible after Q1 substructure modeling papers (LEMON-line) publish, or after DR1 (end of 2026). |
| Orthogonality | ✅ High. Orthogonal to Channel 8 (cluster upper limit) and Channel 2 (UFD upper limit). dN/dM is the *detection* direction. |

**Verdict:** **DEFER the measurement; CONSIDER as forecast channel (Tier-2
candidate).** The R15 audit's "quantitative upgrade over Channel 6"
framing was based on the doc's incorrect 170k-lens claim. Real Q1 has
497, and the dN/dM catalog itself requires community modeling work that
isn't done. As a *forecast* channel using LensPop, it's still useful but
honestly labeled as such.

**R15 error attribution (per AGENTS.md rule 12, self-disclosure):** The
R15 audit repeated the doc's "Euclid ~170,000 lenses" claim without
checking against arXiv:2503.15324. The doc itself conflated forecast
with current data. Corrected here.

---

### P4 — JWST Resolved Stellar Kinematics of Local Group UFDs

**R15 audit verdict:** Genuinely useful — adds density profiles vs upper limits.

**Re-assessment:**

| Axis | Finding |
|---|---|
| Data | ⚠️ **Sparse.** Eridanus II + Tucana II have JWST NIRCam photometry (programs GO-2582, GO-4471). Proper motions are still in proposal/early-pipeline stage (Cycle 3+). Direct σ(r) measurements for Eridanus II have HST-based values (Simon+ 2021, Koposov+ 2015) but JWST proper motions are required for the precision claim in the doc. |
| Velocity | v ≈ 10-30 km/s — Channel 2 (Horigome+ 2025, σ/m < 0.2 cm²/g) gives an upper limit at this scale. The doc's "unitary limit σ/m ~10-100 cm²/g or gravothermal core collapse" is a real observable but the data isn't ready. |
| Statistical power | ⚠️ Low-medium. With only 2-3 UFDs having both NIRCam photometry + PMs, the constraint is bounded by stellar sample size (~100 stars per UFD), not measurement precision. |
| Cost | ⚠️ High: per-star PM extraction + Jeans modeling, ~15-20h per UFD. |
| Orthogonality | ✅ High. Direct density profile vs Channel 2's upper limit. |

**Verdict:** **DEFER (data not ready).** The doc overstates data readiness —
JWST proper motions for Eridanus II / Tucana II are not yet public.
Recheck in 6-12 months when JWST Cycle 3-4 PM programs complete.

---

### P5 — eROSITA eRASS1 Cluster Catalogs

**R15 audit verdict:** Genuinely useful — fills velocity gap.

**Re-assessment:**

| Axis | Finding |
|---|---|
| Data | ✅ **Publicly downloadable today.** eRASS1 Western Galactic hemisphere released 2024-01-31 via HEASARC. Main catalog (Merloni+ 2024, arXiv:2402.08452, A&A 2024) contains all extended X-ray sources; group/cluster subsample is well-characterized. Eastern Galactic hemisphere is German-held; German eROSITA contribution halted Feb 2024 (Ukraine sanctions). |
| Velocity | v ≈ 300-800 km/s — **fills the velocity gap** between Channel 2 (UFD, 10-30) and Channel 8 (cluster, 1000+). This is the project's biggest blind spot. |
| Statistical power | ✅ High. ~10,000+ groups and small clusters with mass measurements. σ/m constraint at v ~ 500 km/s is well-determined from cluster density profiles + X-ray mass proxies. |
| Cost | ✅ Low. Catalog is public; no per-source analysis needed for the v → M conversion (use published kT-M scaling). Hardcode the sample statistics per skill P9 (no-network contract). ~5-10h for code + tests. |
| Orthogonality | ✅ High. Direct detection at v ~ 500 km/s — no other channel covers this velocity range. |

**Verdict:** **ADOPT (Tier-1 priority).** This is the best cost/impact
proposal of the six. The R15 audit's "fills velocity gap" claim is
correct and the data is the most ready of all 6. The German eROSITA
halt is a concern for eRASS2+ but eRASS1 data is permanent.

---

### P6a — XRISM Resolve (Perseus ICM kinematics)

**R15 audit verdict:** Partially useful — (a) baryonic vs SIDM useful.

**Re-assessment:**

| Axis | Finding |
|---|---|
| Data | ✅ Published. A&A 2026 (DOI:10.1051/0004-6361/202557660) presents extended gas kinematic maps of Perseus from XRISM/Resolve, 745 ks exposure, multiple pointings. Velocity dispersion ~300 km/s in eastern region. |
| Velocity | All scales — Perseus is a single cluster at v ~ 1000+ km/s. Sample size N=1 (just Perseus). |
| Statistical power | ⚠️ Low for SIDM constraint (N=1 cluster). High for baryonic feedback (the actual paper's scope). |
| Cost | ✅ Low. Single observation; published numbers can be hardcoded. ~3-5h for code + tests. |
| Orthogonality | ⚠️ Medium. ICM velocity dispersion is a baryonic-feedback diagnostic, not a clean SIDM constraint. Useful for cross-checking Channel 8 (does the observed dispersion match SIDM prediction + baryonic feedback?). |

**Verdict:** **ADOPT as supplementary channel (Tier-2 priority).** Cheap
and adds baryonic-feedback cross-check. P6b (mediator decay line) is
asymptotically null at v0.7 ε (τ_φ ~ 5×10⁴⁴ yr per R15 audit's
numerical check) — skip.

---

### P6b — XRISM mediator decay line (φ → γγ / e⁺e⁻)

**R15 audit verdict:** Partially useful — asymptotically null at v0.7 ε.

**Re-assessment (carried forward from R15):** Confirmed null. τ_φ =
1/(α ε² m_φ) ≈ 1.6×10⁵² s ≈ 5×10⁴⁴ yr ≈ 3.6×10³⁴ × Hubble time at
v0.7 ε. XRISM cannot detect this. **Verdict: SKIP.**

---

## Tier-ranked re-assessment

### Tier-1 (ADOPT, ship next round)

| # | Proposal | Velocity | Cost | Headline value |
|---|---|---|---|---|
| **5** | **eROSITA eRASS1** | 300-800 km/s | ~5-10h | Fills the velocity gap. ~10,000 groups/clusters. Public catalog. **Highest cost/impact.** |

### Tier-2 (CONSIDER, ship Tier-1 round or queue for Tier-2)

| # | Proposal | Velocity | Cost | Headline value |
|---|---|---|---|---|
| **6a** | XRISM Perseus ICM | 1000+ km/s | ~3-5h | Baryonic-feedback cross-check for Channel 8. N=1 but cheap. |
| **2** | Euclid Q1 BCG offsets | 1000 km/s | ~5h | Adds a *detection* to Channel 8's *upper limit*. 14 grade-A clusters. |
| **3** | Euclid Q1 subhalo dN/dM (forecast) | 100-200 km/s | ~10-15h | Forecast channel via LensPop; honest label as forecast, not measurement. |

### Tier-3 (DEFER)

| # | Proposal | Reason |
|---|---|---|
| **1** | JWST cluster lensing | Diego+ 2026 flags fuzzy-DM alternative; marginal vs Channel 8. |
| **3 (real)** | Euclid Q1 subhalo dN/dM (measurement) | Catalog requires community modeling work; feasible after DR1 (end of 2026). |
| **4** | JWST UFD kinematics | JWST proper motions not public; recheck in 6-12 months. |
| **6b** | XRISM mediator decay | τ_φ ~ 5×10⁴⁴ yr at v0.7 ε; asymptotically null. |

---

## What's wrong with the original R15 audit

Per AGENTS.md rule 12 (self-disclosure of mistakes), the R15 audit
(`README.md` of this directory) had two errors that this re-assessment
corrects:

1. **P3 framing.** R15 said "P3 (Euclid subhalo dN/dM) — fresh data;
   needs analysis pipeline" with priority above P5. The doc's
   "Euclid ~170,000 strong galaxy-galaxy lenses" claim was incorrect
   (it is the *full-survey forecast*, not Q1 actual). With Q1 actual
   = 497 lenses and the dN/dM requiring community modeling, P3 as a
   *measurement* channel is Tier-3. As a *forecast* channel it is
   Tier-2 but should be labeled honestly.

2. **Acquisition priority.** R15 recommended "P5 → P6a → P3 → P4 →
   P1+P2 deferred". The re-assessment confirms P5 → P6a → P3
   (forecast) but demotes the measurement version of P3 to Tier-3
   (data not ready) and adds P2 (Euclid Q1 BCG offsets) to Tier-2.

---

## Recommended next-step decision matrix

Per the joint-fit onboarding skill (7-phase pattern, P12 sequential-only
constraint), the **fastest path** is a single Tier-1 ship:

- **Round T88.A (next session, ~5-10h):** Add eROSITA eRASS1 as
  Channel 20. Forward model: σ/m at v ~ 500 km/s from cluster
  density profiles. Wire into T41, 4-config ablation, re-run at
  nlive=500. Doc + drift-guard + ship.

Then queue Tier-2 candidates as separate rounds per cost:
- T88.B: XRISM Perseus ICM (~3-5h)
- T88.C: Euclid Q1 BCG offsets (~5h)
- T88.D: Euclid Q1 subhalo dN/dM (forecast, ~10-15h)

This is a 4-round T88 series (~25-35h total wall) but each round is
independently shippable and sequentially testable.

The Option-E "T88 full dataset-acquisition round" (single round
shipping all 4) was estimated at 25-40h in the R15 audit. Sequential
rounds with user checkpoint are safer because each ship exposes real
data and lets the user abort if the constraint signal is weaker than
expected (per Y1 4-state taxonomy: "already-shipped / partially-built /
genuinely-deferred / blocker-changed").

---

## Audit provenance

- R15 source: `consider5_source.docx` (preserved unchanged)
- External fact-checks performed (2026-09-04):
  - arXiv:2503.15324 (Walmsley+ 2025, Euclid Q1 strong lensing)
  - arXiv:2503.15330 / A&A 711 A33 (Bergamini+ 2025, Euclid Q1 cluster catalog)
  - arXiv:2402.08452 / A&A (Merloni+ 2024, eROSITA eRASS1)
  - DOI:10.1051/0004-6361/202557660 (XRISM Perseus 2026)
  - arXiv:2602.15940 (Diego+ 2026, AS1063 cores)
  - arXiv:2602.12332 (Williams+, AS1063 globular clusters)
  - arXiv:2403.16633 (SASHIMI-SIDM, subhalo dN/dM framework)
  - PR D 111, 063001 (subhalo evaporation in lens systems)
- Cross-checked against existing Channel 6 implementation
  (`v0.3-prelim/code/yang2026_likelihood.py`) and Channel 18
  (`zhang_lss_channel.py`).
- Standing posture preserved: no code shipped, no channels added.
- Re-assessment performed: 2026-09-04 (per AGENTS.md rule 21).
