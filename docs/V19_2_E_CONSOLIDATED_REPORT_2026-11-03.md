# v19.2-E Consolidated Report — 2026-11-03 (stages 1-2 complete, stage 3 pending)

**Scope:** the four-stage chain ordered by the user on 2026-11-03: (1) housekeeping save → (2) new-data search (Euclid/Roman/DESI) → (3) real galaxy merger data → (4) consolidate and report. This document is the running stage-4 consolidation; stage 3 is gated on IllustrisTNG registration approval (application submitted; FIRE-2/EAGLE-IC are no-login fallbacks).

**Record status:** the audited physics record remains **v1.17** (tag `v19.2-F-RecordSave-v1.17`). Nothing in this chain changes any posterior or the anchor **σ/m = 174 cm²/g @ 29.4 km/s (Cloud-9 = M94 RELHIC) — ARCHIVED pair** (the live canonical raw peak is 27.272481773080454 cm²/g and the halo-level σ_eff = 15.348366 cm²/g is unchanged). The chain adds evidence adjudication, two corrected code bugs, and closed literature intake.

---

**Pairing declaration (findings F26/F33):** this document quotes amplitudes in two pairings. The LIVE canonical pair is f_H = 0.7501856343179664 with σ_0 = 0.008150396851725193 cm²/g and σ_peak = 27.272481773080454 cm²/g. The ARCHIVED pair is f_H = 0.297 with σ_0 = 0.052 cm²/g and σ_peak = 174.0 cm²/g. Unless a sentence says otherwise, an amplitude quoted below is an ARCHIVED-pair raw amplitude. Both pairs give the same halo-level σ_eff = f_H² × (σ/m) = 15.348366 cm²/g at the 29.4 km/s resonance, so no effective prediction changes. Sources: scripts/constants.py, v0.3-prelim/data/results/canonical_numbers.json, v0.3-prelim/data/results/fH_pairing_registry.json.

## 1. Stage 1 — housekeeping save (COMPLETE)

- `CHANGELOG.md`/`VERSION` backfilled (n25/n26); `CURRENT.md` stale "Tag pending" corrected.
- Commit `ef427e6` + annotated tag **`v19.2-F-RecordSave-v1.17`** → save point capturing report v1.17, the n22-n26 audit chain, and the 15/15 gate.

## 2. Stage 2 — new-data sweep (COMPLETE, 15/15 gate `344595e`)

Canonical record: `docs/NEW_DATA_SWEEP_2026-11-03.md`.
- Live-verified 32 cited arXiv IDs against the arXiv API; one sweep citation error corrected (`2609.28890` is solar physics → true SIDM calibration paper is `2610.28890`).
- Citation watch (Sameie+ 2020, Lei+ 2026, Wang+ 2026, window 2025-06→2026-11): **no revisions found; the v=150 dissolution criterion did not fire.**
- Cloud-9 identity confirmed repo-wide: **M94 RELHIC, not the GD-1 spur.**
- Roman remains forecast-only (mission launch pending).

## 3. KB intake — CLOSED 21/21 (per AGENTS.md KB rule: local PDF + verified summary)

All 21 accepted candidates read end-to-end and adjudicated against local PDF text (delegated extractions treated as leads; headline numbers grep-verified; **three delegated misclassifications corrected**: Silva = DESI-Lyα sterile neutrinos; Crumrine = mixed-DM satellite limits; Besnard = FDM globular clusters). PDFs + summaries in `docs/papers/verified/` (68 PDFs total). Commits `2d7e0b7` (Tier-1, gate 15/15) + `4a715ce` (Tier-2).

### Verdict headlines

| Finding | Source | Effect |
|---|---|---|
| Collapse-time calibration is not arbitrary: LMFP/SMFP (Knudsen Kn=1) boundary; Yang 150C family valid only in LMFP; SMFP t_c ∝ σ² | Bosch & Tokayer 2610.28890 + Gurian 2610.28745 | **Two-source standing caveat** on every collapse-time claim, incl. ours |
| Lensing quasar populations favor core collapse (Bayes 8:1-24:1 vs CDM), σ ~10²-10⁴ cm²/g @ ~10 km/s, MeV mediator | Gilman+ 2610.40766 / 2609.35974 | External corroboration; **no collision with 174 @ 29.4** (different σ(v) family); one lens sample, not two |
| Independent adoption of Model III (σ0=147.1, w=120); Model I cannot form the J0946 perturber at cluster scale | Tekverk+ 2610.31881 | Model III strengthened at cluster scales; Model I retained for dwarf/Cloud-9 scales |
| GD-1 single-encounter evidence weakened: 75% of 15,000 Gaia velocity jumps complex; mergers/bar make spurs at 50%/25% vs 28% for subhalos | Arora 2605.16200 + Guillaume 2610.41842 | Streams channel DOWNgraded as single-feature evidence; population-level (Nibauer) stands |
| DESI DR2 BAO prefers interacting DM at background level (lnB 5.57/8.72), σ/m<0.01 @ v~1000 km/s | Zhu 2610.26877 | **Watch item:** Model III tail (σ(1000)≈0.03) mildly pressured; Model I (5×10⁻⁵) safe |
| J0946+1006 MAIN halo is NFW (α=1.04±0.10); steepness lives in subhalos (α≈2.1-2.2; 10^8.2-10^8.6 M_sun detections) | Li 2602.20889, Kollmann 2510.17956, Nierenberg 2604.05237 | Citation discipline: subhalo steepness only |
| Euclid is now measured data: stream-host halo shapes q_proj=0.95±0.05; Fornax-7 candidate satellite; FDM m22<1.1-1.5 from GC timing | 2606.21774, 2609.14535, 2609.11328 | New channels opening; **no σ measurement yet** |
| Competing explanation for Lei/Wang-type deficits at cluster velocities (inelastic Δ=18.1 keV) | Yang & Fan 2609.29114 | Specificity dilution — logged as interpretation watch |

## 4. Gravothermal timing corrections (COMPLETE, 15/15 gate `81103b9` evidence)

Two real repository bugs found while testing `2610.28890`'s applicability to Cloud-9:
1. `lookback_time_gyr` mis-transcribed Yang+ eq. 3.2 (sign-flipped exponents; sum rendered as product) → corrected to the asinh form; verified against the paper's own z=1.55 → 9.48 Gyr example and numerical integration (9.4717).
2. `evolution_time_gyr` returned 13.647 − t_L instead of t_L(z_f) → corrected. Combined effect: τ inflated ~4.3× in affected callers (Cloud-9 τ 17.4 → 4.2; BM2 validation still passes).
- `tests/test_gravothermal_lookback_fix.py` 6/6; recheck script `scripts/recheck_cloud9_highsigma_20261103.py`; analysis `docs/CLOUD9_HIGHSIGMA_TIMING_RECHECK_2026-11-03.md`.
- Physical result: at σ≈174 cm²/g the Cloud-9 core becomes **optically thick (τ*≈1.4) at ~3-3.5 Gyr** after formation — the eq-2.2 self-similar family runs too fast beyond that point (literal 1.2-1.4 Gyr vs calibrated 2.2-2.5 Gyr), exactly the regime flagged by Bosch-Tokayer/Gurian. Dwarf anchors (σ≈7) stay optically thin and are unaffected.

## 5. What did NOT change

- 174 cm²/g @ 29.4 km/s anchor (ARCHIVED pair; live canonical raw peak 27.272481773080454 cm²/g; halo-level σ_eff = 15.348366 cm²/g unchanged); joint galaxy-scale 0.06-0.68 cm²/g range; mediator baryon-coupling ceiling <3×10⁻¹¹ (now with external support from Crumrine mixed-DM limits).
- The honest headline: **the project has not proven dark matter self-interacts and has not derived a working particle model from first principles** (v19.2-F Phase 3 FAIL stands).

## 6. Stage 3 status and next actions

- IllustrisTNG: registration application submitted; **awaiting their reply.** Kill criterion unchanged: <10 RELHIC-like halos in TNG-300 ends Path 3.
- No-login fallbacks if approval stalls: FIRE-2 (via existing LESG contacts/public) and EAGLE-IC.
- Merger-tree work must absorb Gurian's finding that mergers delay core collapse by up to 18 t_r, and replace the hand-classified quiescent/active/mixed labels in `GRAVOTHERMAL_ROADMAP.md`.
- Optional physics watch items (low cost, no blocker): Model III vs Zhu cluster-tail check; SMFP slowdown quantification using Gurian Eq. 17 constants (B=3.91, n_L=179, A=0.917, W=2.23, X̂=0.052).

## 7. Gate evidence index (this chain)

| Tree | Evidence | Result |
|---|---|---|
| `8f262ba` sweep | `evidence_sweep20261103/` | 15/15 PASS |
| `2d7e0b7` Tier-1 KB | `evidence_kb_tier1_20261103/` | 15/15 PASS |
| `c1ee215` timing fix | `evidence_lookback_fix_20261103/` | 15/15 PASS |
| `4a715ce`+ Tier-2 KB | `evidence_kb_tier2_20261103/` | 15/15 PASS (commit `014c9e0`) |

Standing disclosures: 22 pytest skips + 36 deselections per run (CG-10 / n25 III.4); the gate asserts only its enumerated layers, not a whole-document verdict (CG-5).
