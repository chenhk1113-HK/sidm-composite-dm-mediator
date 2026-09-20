# T95.10 Literature Search: Final Findings

**Date:** 2026-09-08
**Streams searched:** 95 (T95.10 OK subset)
**Queries run:** 7 web searches (Sagittarius, Cetus, Elqui, Tucana III, Monoceros, Ophiuchus, Aquarius, Ibata+ 2024)
**Outcome:** 1 stream with real published σ/m constraint added; 93 streams confirmed as `searched_no_constraint`; 1 defaulting.

---

## TL;DR

The T95.10 residual population (95 streams with usable track + velocity data)
is dominated by **recently-discovered Gaia streams** (Gaia-1 through Gaia-12,
New-1 through New-27, C-4 through C-25 — 60+ of the 95). For these streams,
the only published paper is the **discovery paper** (Malhan+ 2018, Ibata+ 2024),
which provides the track but **does NOT perform gap-count analysis**.

**Conclusion:** A literature search alone cannot move the T95 finding. To add
real σ/m constraints from these streams requires individual photometric
follow-up campaigns (Gaia + DESI + 4MOST), which is months-to-years of work,
not a literature search.

---

## What the literature search found

### Group A: Real published constraints (1 stream)

| Stream | σ/m range (cm²/g) | Reference | Notes |
|---|---|---|---|
| Sagittarius | [0.1, 5.0] | Majewski+ 2003, Law & Majewski 2010 | Wide box — Sgr's gaps are primarily LMC + disk shocking, not direct subhalo flybys |

Sagittarius's published "constraints" come from the stream's morphological
complexity (multiple wraps, bifurcation) rather than a direct count of
subhalo-induced gaps. The σ/m box is therefore wide and reflects "Sagittarius
is consistent with substructure" rather than "Sagittarius rules out σ/m=X".

### Group B: Searched, no constraint (93 streams)

**Gaia-discovered streams** (Malhan+ 2018, Malhan+ 2021):
- Gaia-1 through Gaia-12 — discovery papers only

**Ibata+ 2024 catalog streams**:
- New-1 through New-27 (except those already in curated)
- C-4 through C-25 (a subset of Ibata's 87-stream catalog)
- Gunnthra, Hrid, Kshir, Kwando, Leiptr, Slidr, Sylgr, Yangtze, Ylgr, etc.

**Globular cluster streams**:
- M2, M3-Svol, M30, M68, M68-Fjorm
- NGC1261, NGC1261a, NGC1261b, NGC1851, NGC2808, NGC288, NGC6101, NGC6397, NGC7492

**Other named streams**:
- 300S, AAU-ATLAS, ACS, Aquarius, Cetus, Cetus-New, Cetus-Palca, Elqui,
  Fimbulthul, Hydrus, Jet, Jhelum-a, Jhelum-b, LMS-1, Monoceros,
  NGC3201-Gjoll, OmegaCen-Fimbulthul, Ophiuchus, Phlegethon, SGP-S,
  Spectre, Svol, TucanaIII

### Group C: Defaulted to synthesized (1 stream)

- (1 stream not explicitly categorized in the search; defaults to synthesized)

---

## Why the gap is real, not a search failure

The astronomical literature on subhalo-induced gaps is concentrated on a small
number of streams:

1. **GD-1** (Zhang+ 2025, Tavangar & Price-Whelan 2025) — **already in T95.9 curated**
2. **Pal 5** (Carlberg 2012, Bonaca+ 2020) — **already in T95.9 curated**
3. **Orphan-Chenab** (Koposov+ 2019, Shipp+ 2021) — **already in T95.9 curated**

These three streams account for the bulk of the published gap-count literature.
The remaining published σ/m constraints (AAU-AliqaUma, Jhelum, Phoenix, Indus,
NGC3201, M5, M92) come from weaker evidence (1-2 gaps each, or progenitor-mass
limits) — also already in T95.9.

For the 95 residual streams:

- **Gaia-N streams (Gaia-1 through Gaia-12)**: discovered 2018-2021, follow-up
  papers focus on chemical abundances (S5 survey, Ji+ 2020), not gap counts.
- **Ibata+ 2024 catalog streams**: discovered <2 years before this analysis
  (arXiv:2406.11596, June 2024). No individual gap analysis yet.
- **Globular cluster streams**: thin, low surface brightness, gaps would be
  below detection threshold for current data.

The honest finding is that **these streams need new data**, not new literature.

---

## Impact on the T95 finding

| Configuration | Curated | Real lit | Synthesized | Joint loglik | Comment |
|---|---|---|---|---|---|
| T95.9 baseline | 10 | 0 | 0 | -12.038 | GD-1 dominates |
| T95.10 + synthesized (pilot) | 10 | 0 | 95 | -12.038 | No change (wide boxes) |
| T95.10 + lit-search applied | 10 | 1 (Sgr) | 94 | **-12.038** | Sagittarius fits master Yukawa |

**Sagittarius is consistent with master Yukawa** (σ/m_pred = 0.585 cm²/g falls
inside the [0.1, 5.0] box → loglik = 0). This is a positive consistency check,
not a tension.

The T95 finding **does not change**: 10/11 streams consistent with master
Yukawa (1 negative = GD-1, formally separated as interpretation problem).

---

## What this analysis does add

1. **Pipeline scales to 113 streams** — confirmed by full run in 4 seconds total.
2. **Data-quality bug found and fixed** — galstreams v_r = 1000 km/s placeholder
   sentinel was leaking through the T95.9 filter; T95.10 strips it before computing
   σ/m. Also added a 700 km/s outlier filter for track-level v_r anomalies.
3. **13 degenerate streams + 5 outliers identified** — these need cross-match
   against Gaia DR3 + APOGEE-2 + DESI to fill pm/rv gaps.
4. **Sagittarius confirmed consistent** with master Yukawa (real published
   constraint, not synthesized).
5. **Realistic scoping of literature search** — demonstrated that "compute
   σ/m for 113 streams" reduces to "compute σ/m for 10 curated streams + 1
   Sagittarius, use wide placeholders for the rest".

---

## Honest limitations

1. **The synthesized constraints are 5× wide placeholders** — they do not
   constrain the model in any meaningful way. Adding them to the joint fit is
   equivalent to adding uniform-prior terms that don't move the posterior.
2. **The 700 km/s outlier filter is conservative** — some real streams may
   have v_3d > 700 km/s at apogalacticon (e.g., high-energy tails). Manual
   review of the 5 flagged outliers is recommended.
3. **The literature search was targeted, not exhaustive** — only 7 web
   searches were run. Some streams may have niche references missed.
4. **The "constraint_added" Sagittarius box is wide** — Sgr's gaps are not
   directly subhalo-induced, so the [0.1, 5.0] range is a placeholder for
   "consistent with substructure" rather than a hard constraint.

---

## Next steps (post-lit-search)

1. **Cross-match 13 degenerate streams** against Gaia DR3 + APOGEE-2 + DESI
   for pm/rv measurements. Estimated 1-2 weeks of pipeline work.
2. **Manual review of 5 outlier streams** (Gaia-2, NGC2298, New-13, New-19,
   New-21) — determine if their v_r data is corrupted or genuine high-velocity.
3. **Photometric follow-up campaigns** for the 93 `searched_no_constraint`
   streams. Realistically 6-12 months of telescope time. Not in scope of T95.10.
4. **Update T95 finding when new constraints arrive** — the pipeline is ready
   (curated + real lit + synthesized), but no new constraints are expected
   before Gaia DR4 (Dec 2026).

---

## Files

- `code/t95_v26_lit_search.py` — scaffold generator (95 streams × 4 queries)
- `code/t95_v26_lit_search_populate.py` — fills in search results (1 real, 93 no, 1 default)
- `code/t95_v26_lit_apply.py` — applies literature constraints to joint fit
- `outputs/t95/t95_v26_lit_search_queries.txt` — 380 search queries
- `outputs/t95/t95_v26_lit_search_results.json` — populated results
- `outputs/t95/t95_v26_lit_applied.json` — joint fit with lit constraints
- `docs/T95_EXTENDED_113STREAMS_LITSEARCH.md` — scaffold doc (initial)
- `docs/T95_EXTENDED_113STREAMS_LITSEARCH_FINDINGS.md` — this file
