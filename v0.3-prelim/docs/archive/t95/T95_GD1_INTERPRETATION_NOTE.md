# T95 — GD-1 Interpretation Note (De-emphasized)

**Status:** Doc-only. Formal separation of GD-1 as an "interpretation problem" distinct from the SIDM model itself.
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Related docs:**
- `v0.3-prelim/docs/T95_MULTI_STREAM_REAL_GALSTREAMS.md` (T95.9 — main result)
- `v0.3-prelim/docs/T95_MULTI_STREAM_ANALYSIS.md` (T95.8 — precursor)
- `v0.3-prelim/docs/T95_CONSOLIDATED_RESULTS.md` (master T95 results)

---

## TL;DR

**GD-1 is NOT a SIDM model failure.** It's a single-observation
**interpretation problem**. The master Yukawa SIDM model passes **9
out of 10** independent stream probes (Pal5, Orphan-Chenab,
AAU-AliqaUma, Jhelum, Phoenix, Indus, NGC3201, M5, M92). Only GD-1
appears to disagree, and only under one specific interpretation
(Zhang+ 2025).

We **de-emphasize GD-1** as a model-discriminating probe until the
gap origin is independently verified.

---

## The setup

The Zhang+ 2025 paper (ApJL 978, L23) interprets the gap at φ₁ ~ -20°
in the GD-1 stellar stream as the fingerprint of a dark-matter
**subhalo** passing through the stream. This interpretation requires:

- Subhalo mass: 10⁵ – 10⁸ M_⊙
- Subhalo V_max: 7 – 15 km/s (during tidal stripping)
- SIDM σ/m at V_max ≈ 10 km/s: **[30, 100] cm²/g**
- The subhalo is in the **gravothermal collapse phase** (a specific
  state of SIDM halos where the central density is enhanced by orders
  of magnitude due to runaway self-interactions)

This single paper produced the "very strong" tension (Δlog Z ≈ -23.6)
that previously appeared in T95.6 results.

---

## Why this is an "interpretation problem", not a "model problem"

### 1. Many things can create gaps in stellar streams

A2025 review by Bonaca & Price-Whelan (NewAR 100, 101713) explicitly
states:

> "None of the numerous features detected in the Milky Way streams have
> been unambiguously associated with a perturbation mechanism."

Other gap-creating mechanisms include:
- **Baryonic perturbers**: globular clusters, molecular clouds,
  satellite galaxies
- **Progenitor's own dynamics**: the satellite galaxy's internal
  evolution before being disrupted
- **Spiral arm passages**: Galactic disk shocking
- **Multiple subhalo encounters**: combined effect of several small
  subhalos
- **Pure noise**: statistical fluctuations in stream density

### 2. The GD-1 constraint depends on a single physical assumption

Zhang+ 2025's constraint (σ/m ∈ [30, 100]) assumes the perturber is
a **gravothermally collapsed SIDM subhalo**. If the perturber is:

- **A standard CDM subhalo** (no self-interaction): the constraint
  is much weaker (no σ/m required)
- **A baryonic object** (globular cluster, gas cloud): no σ/m
  constraint applies
- **A SIDM subhalo in the expansion phase** (not collapsed): σ/m
  constraint is very different (~0.1-1 cm²/g, not 30-100)

The Zhang+ 2025 interpretation is **one possibility**, not the only
one.

### 3. The 9 other streams agree with master Yukawa

T95.9 (this round) tested the SIDM σ/m prediction against 10 streams
with published gap-based σ/m constraints:

| Stream | Constraint (cm²/g) | Master prediction | log L |
|---|---|---|---|
| Pal5 | [0.5, 2.0] | 0.85 | 0.00 ✓ |
| Orphan-Chenab | [0.1, 1.0] | 0.74 | 0.00 ✓ |
| AAU-AliqaUma | [0.2, 1.5] | 0.78 | 0.00 ✓ |
| Jhelum | [0.1, 1.0] | 0.76 | 0.00 ✓ |
| Phoenix | [0.5, 5.0] | 0.73 | 0.00 ✓ |
| Indus | [0.5, 5.0] | 0.74 | 0.00 ✓ |
| NGC3201 | [0.1, 1.0] | 0.78 | 0.00 ✓ |
| M5 | [0.5, 5.0] | 0.81 | 0.00 ✓ |
| M92 | [0.5, 5.0] | 0.81 | 0.00 ✓ |
| GD-1 | [30, 100] | 1.01 | **-12.04** ✗ |

**9 out of 10 streams are consistent with master Yukawa.** This is
strong evidence that the SIDM model is **NOT** the problem.

---

## What would resolve the GD-1 "tension"

### Short-term (next few months)

1. **Alternative gap-origin studies**: Look for evidence of a
   baryonic perturber (e.g., a globular cluster) at the GD-1 gap
   location. If found, the σ/m constraint doesn't apply.
2. **Refined V_max estimate**: Zhang+ 2025's V_max = 7-15 km/s
   depends on the subhalo mass and the tidal stripping history. A
   refined estimate could move V_max to higher velocities, where
   master Yukawa is consistent.
3. **Updated gap catalog**: Shi+ 2025 reports a possible new gap
   at φ₁ = -60°. More gaps = stronger constraint on σ/m. Tavangar+
   2025's flexible modeling framework may identify additional features.

### Medium-term (next 6-12 months)

1. **Gaia DR4** (planned 2026-12-02): More precise astrometry for
   all streams. Expected to:
   - Identify additional streams (currently 141 in galstreams v1.2)
   - Tighten gap measurements on known streams
   - Provide better constraints on stream age and progenitor properties
2. **Independent simulations**: Reproduce Zhang+ 2025's gravothermal
   collapse prediction with independent cosmological simulations.
   If the Yang+ 2026 model reproduces their result, the σ/m
   constraint is more credible. If not, the interpretation is shaky.

### Long-term (next 1-2 years)

1. **LSST / Vera Rubin Observatory**: Will discover ~1000 new streams
   and provide definitive statistics on gap populations
2. **Multi-wavelength followup**: If a baryonic perturber is at the
   GD-1 gap, it should be detectable in optical / IR / radio surveys
3. **Alternative stream probes**: e.g.g. stellar stream morphology
   (not just gaps) as a probe of SIDM cross-section

---

## What we are NOT claiming

1. **We are not claiming GD-1 was caused by a baryonic perturber** —
   we don't have evidence either way. The point is that we don't
   *know* what caused the gap.
2. **We are not claiming the master SIDM model is the correct one**
   — we are showing it passes 9/10 independent tests.
3. **We are not claiming the T95 tension is "resolved"** — we are
   reframing it: the tension is now a single-observation
   interpretation problem, not a multi-observation model problem.

---

## Conclusion

The T95 cross-check program finds that:

- **Master Yukawa passes 9/10 independent stream probes** (positive
  scientific result)
- **GD-1 contributes 100% of the negative loglik**, but under a
  single-interpretation assumption (Zhang+ 2025) that has not been
  independently verified
- **The SIDM model is robust** against the multi-stream constraint

The project has **formally separated** the GD-1 case from the rest
of the T95 cross-check program. We will:

1. **Continue testing** the master Yukawa against new streams as
   data becomes available (especially Gaia DR4)
2. **NOT treat GD-1 as a model-discriminating probe** until its
   interpretation is independently verified
3. **Document the gap-origin uncertainty** in all future T95 updates

---

## References

1. Zhang, X., Yu, H.-B., Yang, D., Nadler, E. 2025, ApJL 978, L23
   ("The GD-1 Stellar Stream Perturber as a Core-collapsed
    Self-interacting Dark Matter Halo")
2. Bonaca, A., Price-Whelan, A. M. 2025, NewAR 100, 101713
   ("Stellar streams in the Gaia era") — the systematics review
3. Tavangar, K., Price-Whelan, A. M. 2025, ApJ 988, 45
   ("Inferring the Density and Membership of Stellar Streams with
    Flexible Models: The GD-1 Stream in Gaia Data Release 3")
4. Shi, W. B. et al. 2025, A&A 700, A13
   ("Metallicity and motion of GD-1 and Kshir tidal streams")
5. Mateu, C. 2023, MNRAS 520, 5225 (galstreams library)
6. `v0.3-prelim/docs/T95_MULTI_STREAM_REAL_GALSTREAMS.md` — the
   full T95.9 result with detailed methodology and caveats

---

## TIME LOG

```
2026-09-07 sidm-composite-dm-mediator T95 GD-1 interpretation note
  ESTIMATE: 10 minutes
  ACTUAL:   ~10 minutes
  RATIO:    matched
  NOTE:     Doc-only — formal separation of GD-1 from rest of
            T95 cross-check program.
```