# T112 — High-resolution 8D dynesty (nlive=2000, tight delta prior)

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** RUNNING (background process `proc_f136bac59d7e`)
**Method:** dynesty nested sampling, 8D

---

## TL;DR

T112 implements reviewer suggestion §1(a) and §1(c) from
"Suggestions for taking Door B further":

- **§1(a) — High-resolution nested sampling**: nlive=2000 (vs T108's 500)
  to target Δlog Z uncertainty ≲ 0.1.
- **§1(c) — Tight delta prior**: δ restricted to [50, 200] keV (vs T108's
  [1, 1000] keV). The 50-200 keV window is motivated by Berlin & Ferraro
  (2025) composite-DM mass-splitting theory: δ ~ Λ_D / m_χ ≈ 100 keV.

---

## What this changes vs T108

| Parameter | T108 | T112 |
|---|---|---|
| `nlive` | 500 | **2000** (4×) |
| `dlogz` target | 0.1 | **0.05** (2× tighter) |
| `log_delta_keV` prior | [0, 3.0] (1-1000 keV) | **[1.7, 2.3] (50-200 keV)** |
| Wall time | 438s | **~1750s (29 min, 4×)** |

---

## Why this matters

**Reviewer's concern:** T108's +0.51 has ~0.20 uncertainty. T108 is only
~2.5σ above v0.7. A tighter error bar will show whether the preference
is real or noise.

**Prior tightening rationale:** The uniform prior on δ ∈ [1, 1000] keV
in T108 includes regions where composite-DM models are not theoretically
motivated (e.g., δ > 200 keV requires unusual UV completions). Restricting
to [50, 200] keV:
- Removes parameter volume where v0.7 has no predictive power.
- Concentrates Bayes factor on the theoretically motivated region.
- Allows the data to better discriminate between models.

**Expected outcome:** If Door B is "real" (data prefers δ ~ 100 keV),
Δlog Z will likely INCREASE with the tighter prior (less volume in the
null region). If Door B is "spurious" (just fitting noise), Δlog Z
will DECREASE or stay similar.

---

## Caveats

1. **TIGHTER PRIOR changes the Bayes factor.** T108's Δlog Z = +0.51 used
   uniform prior over [1, 1000] keV. T112's Δlog Z uses [50, 200] keV.
   These are NOT directly comparable.
2. **nlive=2000 increases wall time ~4×** (~29 min vs 7 min for T108).
3. **If Δlog Z(T112) > +2**, Door B becomes "legitimately competitive"
   per reviewer's own criterion. This is the test.
4. **If Δlog Z(T112) < +0.51**, the tight prior excludes the T108 MAP
   region; Door B's preference was driven by volume, not evidence.

---

## Files

- `v0.3-prelim/code/t112_highres_8d_dynesty.py` — main 8D dynesty script
- `v0.3-prelim/tests/test_t112_t113_t114.py` — tests (T112 + T113 + T114)
- `v0.3-prelim/outputs/t95/t112_highres_8d_dynesty.json` — final output
- `v0.3-prelim/docs/T112_HIGHRES_8D_DYNESTY.md` — this doc

---

## Cross-references

- **T108 (baseline 8D):** nlive=500, δ ∈ [1, 1000] keV, Δlog Z = +0.51
- **T110 (Door C closed):** 7D dynesty, Δlog Z = -10.72
- **T111 (Door D closed):** 9D emcee, Δlog Z = -5.72
- **Berlin & Ferraro (2025):** composite-DM mass-splitting theory

---

## Standing posture

- **Master:** v0.5-prelim tagged, untouched
- **T90/LZ branch:** Tier A+B+D shipped; T112 running
- **Tier D (UV completion):** Out of project scope per user

---

## Provenance

- T112 implementation: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Branch: `wip/tier3-magnetic-moment-LZ`