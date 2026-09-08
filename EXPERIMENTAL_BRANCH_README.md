# ⚠️ EXPERIMENTAL BRANCH — UNVALIDATED RESULTS ⚠️

**Branch:** `experimental/t95-chemodynamic-rescue`
**Based on:** `wip/tier3-magnetic-moment-LZ` @ `4dc2bcc`
**Created:** 2026-09-08
**Status:** EXPERIMENTAL — DO NOT USE FOR PUBLICATION

---

## Cross-references

This branch's relationship to the rest of the project:

- **Master (canonical):** `master` @ `v0.4-prelim+T88E` — DO NOT touch with this work
  - Cross-reference: see `CURRENT.md` (project root) "Standing: v0.4-prelim+T88E" section
  - Cross-reference: see `README.md` "EXPERIMENTAL BRANCH NOTICE" banner
- **Source WIP branch:** `wip/tier3-magnetic-moment-LZ` @ `4dc2bcc` (T95.10 → T95.14 work)
- **This branch:** `experimental/t95-chemodynamic-rescue` (adds the EXPERIMENTAL banner + cross-references)
- **Full T95.13/T95.14 report:** `v0.3-prelim/docs/T95_EXTENDED_113STREAMS_CHEMODYNAMIC.md` (in source WIP branch)
- **Validation table:** `v0.3-prelim/outputs/t95/validation_table.md` (in source WIP branch)
- **T95.11 results JSON:** `v0.3-prelim/outputs/t95/t95_v11_cross_match_results.json` (now has `validation_status` field)

---

## What this branch is

This is a side branch that carries the **T95.13 + T95.14 chemodynamic stream-kinematics rescue** as an experimental result. It is **NOT on master** because:

1. **Validation gap:** 5 of 7 T95.11-rescued streams have no published kinematics to validate against. The 1 comparison that exists (Tri-Pis vs Bonaca 2012) was 42% off — explained by spatial offset between measurement locations but still indicative of systematic uncertainty.

2. **Chemodynamic approach is new:** T95.14's [Fe/H]-filtered GMM worked on 2 streams (Parallel, Perpendicular) but has not been independently replicated.

3. **The T95 finding (9/10 streams consistent with master Yukawa) is unchanged from T95.9.** The +7 rescued streams confirm what the curated 10 already showed; they don't constitute a new discovery.

4. **The T90 merge rule (locked 2026-09-06) prohibits master promotion of unvalidated branches.** This branch is the explicit alternative — the work is preserved and accessible without violating the rule.

---

## What this branch contains

### T95.13 (DESI DR1 cross-match)
- 2 of 7 T95.11 outliers had DESI DR1 coverage
- 5 were in regions DESI hasn't surveyed (footprint limitation)
- Worked around 6 distinct NOIRLab TAP quirks

### T95.14 (Chemodynamic GMM)
- Added DESI [Fe/H] as chemodynamic prior to GMM
- Rescued 1 additional outlier (Parallel → 394 km/s; Perpendicular → 329 km/s)
- Both now pass the 700 km/s outlier filter
- Both produce σ/m ≈ 0.56-0.58 cm²/g, factor-3 boxes consistent with master Yukawa

### Joint fit impact
| Stage | Curated | + Rescued | Joint loglik |
|---|---|---|---|
| T95.9 baseline | 10 | 0 | -12.038 |
| + T95.11 | 10 | 6 | 0.000 |
| + T95.14 | 10 | 7 | 0.000 |

### T95.11 validation table
5 of 6 T95.11-rescued streams have no published reference. The 1 that does (Tri-Pis) was 42% off, explained by velocity gradient along the stream.

---

## When this branch would be merge-worthy

This branch should be considered for promotion to master **only** when:

- [ ] External validation exists for at least 3-5 of the chemodynamic-rescued streams (DESI DR2, Gaia DR4, 4MOST, or published literature)
- [ ] A peer-reviewed or community-reviewed publication has accepted the methodology
- [ ] The T95.14 chemodynamic approach has been replicated by an independent team
- [ ] All 5 unvalidated streams have either been validated or explicitly flagged as "untestable with current data"

Realistic timeline: **Gaia DR4 (Dec 2026)** or **DESI DR2 (mid-2027)**.

---

## How to use this branch

If you want to cite the chemodynamic rescue in a paper or talk:

```bash
git checkout experimental/t95-chemodynamic-rescue
# this is the work-in-progress branch with full provenance
```

For canonical/citable results, use master (`v0.4-prelim+T88E`) until the validation criteria above are met.

---

## Time log for branch creation

- ESTIMATE: 20-30 min
- ACTUAL: ~10 min so far
- STATUS: in progress

