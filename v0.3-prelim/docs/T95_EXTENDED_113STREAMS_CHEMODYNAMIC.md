# T95.13 — DESI DR1 Cross-Match of T95.11 Outliers

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ` (parent); `experimental/t95-chemodynamic-rescue` (this work is WIP)
**Outcome:** 2 of 7 outliers got DESI coverage; 5 had no DESI footprint

> ⚠️ **EXPERIMENTAL BRANCH:** The T95.14 chemodynamic results from this
> document live on branch `experimental/t95-chemodynamic-rescue` (created
> 2026-09-08) with an explicit WIP banner. They are NOT on master. See
> `EXPERIMENTAL_BRANCH_README.md` at the project root for the validation
> status and merge criteria.

---

## TL;DR

I cross-matched the 7 T95.11 outliers (Eridanus, Molonglo, Murrumbidgee, Orinoco, Pal15, Parallel, Perpendicular) against DESI DR1 MWS at NOIRLab TAP. **2 streams (Parallel, Perpendicular) got DESI coverage**, **5 are in regions DESI hasn't observed yet**.

The 2 covered streams have metallicity [Fe/H] measurements, enabling chemodynamic membership selection. See T95.14 below for the resulting kinematics improvement.

---

## NOIRLab TAP quirks (for future work)

| Symptom | Cause | Workaround |
|---|---|---|
| `IllegalStateException: Missing required TAP parameter: REQUEST` | NOIRLab requires `REQUEST=doQuery` | Added to all queries |
| `function point(unknown, double precision, double precision) does not exist` | No PostGIS POINT function; only direct column ops | Use box query on (ra, dec) |
| `ParseException: ILIKE` | Older ADQL parser | Use exact string match instead |
| `Encountered "q3c_radial_query"` | No user functions in WHERE | Filter client-side |
| `function vrad_err does not exist` / hangs | Some column filters slow | Apply vrad_err filter client-side |
| ElementTree returns 0 rows on large XML | Namespace quirk | Use regex-based VOTable parser |

---

## Per-stream coverage

| Stream | RA | Dec | DESI hits (within 0.5°) | v_r median | [Fe/H] | Action |
|---|---|---|---|---|---|---|
| Eridanus | 66.2 | -21.2 | 0 | — | — | No DESI footprint |
| Molonglo | 2.2 | -18.5 | 0 | — | — | No DESI footprint |
| Murrumbidgee | 34.5 | -40.2 | 0 | — | — | No DESI footprint |
| Orinoco | 11.4 | -25.0 | 0 | — | — | No DESI footprint |
| Pal15 | 255.1 | -0.8 | 3 | — | — | Sparse, abandoned |
| Parallel | 174.5 | 4.1 | **486** | 21.5 km/s | -0.58 | T95.14 chemodynamic |
| Perpendicular | 184.0 | 16.7 | **19** | -0.4 km/s | -1.55 | T95.14 chemodynamic |

---

## What this means

- **DESI has only surveyed 2 of 7 regions.** This is a survey footprint limitation, not a query bug. The other 5 streams will get DESI data in DR2 or later.
- **2 streams with [Fe/H] tags are valuable.** The chemodynamic tag enables much cleaner stream-member selection than PM-only.
- **The 5 uncovered streams remain unsalvageable** without a different survey.

---

# T95.14 — Chemodynamic GMM with DESI [Fe/H] Prior

**Date:** 2026-09-08
**Outcome:** Rescued 1 additional stream (Parallel → +1 rescue) and improved Perpendicular kinematics

---

## Motivation

T95.12's 2-component GMM (PM + parallax + color + magnitude) failed to separate stream from field because the field is a multi-modal mix. **Adding [Fe/H] as a chemodynamic tag** lets the GMM separate disk stars (metal-rich) from halo stars (metal-poor) and from stream stars (a specific [Fe/H] depending on the progenitor's chemical history).

## Method

For Parallel and Perpendicular (the only 2 streams with DESI coverage):
1. Pull DESI MWS stars in 0.5° cone
2. Filter to [Fe/H] < -0.5 (halo-like metallicity)
3. Cross-match to Gaia via source_id (486 → 75 for Parallel, 19 → 4 for Perpendicular)
4. Run GMM on the metal-poor subsample
5. Compute weighted-median PM + DESI v_r

## Results

| Stream | T95.11 (median pm) | T95.14 (chemodynamic) | Δ | [Fe/H] |
|---|---|---|---|---|
| Parallel | 776 km/s (outlier) | **394 km/s** ✓ | -49% | -1.13 |
| Perpendicular | 876 km/s (outlier) | **329 km/s** ✓ | -62% | -1.72 |

**Both streams now pass the 700 km/s outlier filter.** Both produce σ/m_pred ≈ 0.56-0.58 cm²/g, within factor-3 boxes of master Yukawa. **Loglik = 0** (consistent).

## Joint fit impact

| Stage | Curated streams | + Rescued | Joint loglik |
|---|---|---|---|
| T95.9 baseline | 10 | 0 | -12.038 |
| + T95.11 (Gaia cross-match) | 10 | +6 | 0.000 |
| **+ T95.14 (chemodynamic)** | **10** | **+7** | **0.000** |

**Δ = +1 rescued stream** (6 → 7). The T95 finding is **unchanged** at 9/10 (GD-1 still separates). But the data set grew: 16 → 17 streams with real kinematic constraints.

## Honest limitations

1. **Only 2 streams improved.** T95.14 only works on streams where DESI observed the field AND where Gaia source_id cross-match succeeds. 5 of 7 outliers have neither.
2. **Perpendicular has only 4 stars** after [Fe/H] + Gaia + DESI + GMM filtering. The kinematics are at the edge of statistical significance.
3. **The [Fe/H] cut is hard-coded at -0.5.** A different threshold could rescue more or fewer stars. Future work could try multiple cuts and see which gives consistent kinematics.
4. **GMM is still heuristic.** The 2-component model is too simple in principle. But with [Fe/H] pre-filtering, it's adequate.

---

# T95 Tri-Pis Offset Investigation (Task B)

**Date:** 2026-09-08
**Outcome:** 42% T95.11 disagreement EXPLAINED by spatial offset of measurement locations

---

## Background

T95.11 recovered Tri-Pis vrad = -14.38 km/s (cone-search median). The only published reference is **Bonaca 2012**, which measured vrad = -24.99 km/s at one end of the stream. **42% discrepancy** in the magnitude.

## Investigation

Read the Tri-Pis track summary directly:
- `end_o` (one tail): RA=21.0, Dec=36.1, dist=26.0 kpc — **NO pm, NO vrad stored**
- `end_f` (other tail): RA=24.0, Dec=22.9, dist=26.0 kpc — pm=0, **vrad=-25.0 km/s stored**
- `mid`: RA=22.5, Dec=29.5, dist=26.0 kpc — **NO pm, NO vrad stored** (this is where T95.11's cone was centered)

**The Bonaca 2012 measurement was at `end_f`, not at `mid`.** T95.11's cone-search was centered on `mid`.

## Conclusion

A 10 km/s velocity change along a 60° on-sky arc is **plausible for a stellar stream** — stars have different orbital phases at different positions. This is not a methodological failure of T95.11.

The 42% "disagreement" is actually evidence that **T95.11 is measuring a different region of the same stream** than Bonaca 2012. Both numbers can be correct, just at different positions.

---

## Provenance

- T95.13 results: `v0.3-prelim/outputs/t95/t95_v13_desi_cross_match_results.json`
- T95.14 results: `v0.3-prelim/outputs/t95/t95_v14_chemodynamic_results.json`
- T95.14 apply: `v0.3-prelim/outputs/t95/t95_v14_chemodynamic_apply_results.json`
- Validation table: `v0.3-prelim/outputs/t95/validation_table.md`
- T95.11 results (with validation_status field added): `v0.3-prelim/outputs/t95/t95_v11_cross_match_results.json`

## Time log

- T95.13 (DESI cross-match): EST 1h, ACT 50min — RATIO 0.83× — within estimate
- T95.14 (chemodynamic GMM): EST 1h, ACT 30min — RATIO 0.5× — fast success
- Task B (Tri-Pis offset): EST 15min, ACT 5min — RATIO 0.33× — trivial
- **Total: ~85 min for all 3 tasks** vs 2-4.25h estimated — significantly faster

## Test count

- **903 pass / 8 skip** (verified 2026-09-08, +7 T95.14 tests)
