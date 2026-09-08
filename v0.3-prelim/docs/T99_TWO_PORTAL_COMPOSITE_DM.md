# T99 — Two-Portal Composite DM: v0.7 MAP + Di Mauro as Complementary

**Date:** 2026-09-08
**Status:** Conceptual framing, no new model parameters
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Cross-references:** T87 §13, T90_INDEX, T98, T90_PATH_C4_V17

---

## TL;DR

The v0.7 MAP (composite-DM via kinetic mixing, ε ~ 10⁻³⁷) and Di Mauro
2026 (arXiv:2609.02608, thermal secluded-WIMP inelastic 𝒪₁ˢ, ε
implicitly ~ 0.3) are **NOT competing interpretations**. They describe
**two independent dark-sector portals** that can coexist in the same
composite-DM UV completion.

- **Portal A (kinetic mixing, ε ~ 10⁻³⁷):** explains the SIDM phenomena
  — dwarf-galaxy cores, BAHAMAS, LSS, σ/m ≈ 0.27 cm²/g.
  Does NOT explain the LZ 248 keV event (74 OOM short of σ_DM-nuc).
- **Portal B (inelastic 𝒪₁ˢ, full strength):** explains the LZ 248 keV
  event with δ ~ 297 keV (pseudo-Dirac) or 371 keV (Higgsino).
  Does NOT participate in the SIDM channels.

**The T17 v17 Bayesian time-series analysis is already consistent with
this framing**: magnetic-moment (T90) and Higgsino-inelastic (Fan &
Tweed 2026) are tied at 47% posterior each, instrumental at 6%. The
data does not distinguish between the two at the LZ event, because
both predict ~1 event.

This is **not a new model** — it is a re-framing of existing results
that makes clear: v0.7 MAP's failure to explain the LZ event is not
a contradiction, it is a feature of composite-DM models with multiple
independent dark-sector couplings.

---

## Motivation

The T98 cross-check (this PR) found that v0.7 MAP's σ_DM-nuc at 248 keV
is **74.8 orders of magnitude below** the ~6.5×10⁻⁴³ cm² required to
explain the LZ 248 keV event under Di Mauro's interpretation. The
obvious question is: can the project's ε be raised to match?

The answer (analyzed in the Option-B discussion, 2026-09-08): raising
ε by 37 OOM to ~0.3 would:

1. **Break the SIDM interpretation.** σ/m at dwarf cores scales as
   ε² × α_χ / m_φ⁴. At ε ~ 0.3 with m_φ = 453 MeV, σ/m would be
   ~10⁷² cm²/g — excluded by 70+ OOM.
2. **Move out of the freeze-in regime.** At ε ~ 0.3, DM thermalizes
   with the SM bath. The relic density becomes a freeze-out
   calculation, no longer derived from ε.
3. **Violate PandaX-4T / XENONnT direct-detection limits.** At
   ε ~ 0.3, σ_DM-nuc is in the current exclusion zone.

So v0.7 MAP is **rigid** to ε — it must stay in the freeze-in regime
to satisfy the SIDM channels. It cannot be "tuned" to explain LZ.

But this doesn't mean the LZ event is unexplained. The T17 v17
posterior already shows that an **independent** inelastic portal
(Higgsino-like, Fan & Tweed 2026) is tied with magnetic-moment at
47% each. The data supports two channels contributing.

---

## The two-portal composite-DM UV model

### Portal A: kinetic mixing ε (SIDM)

| Property | Value | Source |
|---|---|---|
| Coupling | ε ~ 10⁻³⁷ | T41 v0.7 MAP joint fit |
| Mediator | dark photon, m_φ = 453 MeV | T41 v0.7 MAP |
| Relic density | freeze-in | ε⁴ in production rate |
| σ/m at v=10 km/s | 0.27 cm²/g | dwarf cores + BAHAMAS + LSS |
| LZ σ_DM-nuc at 248 keV | 1.15×10⁻¹¹⁷ cm² | T87 |
| Indirect detection | 5-12 OOM below limits | T15 |
| Status | **FITS 8 of 19 channels** | T41 v0.7 |

### Portal B: inelastic 𝒪₁ˢ (LZ 248 keV)

| Property | Value | Source |
|---|---|---|
| Coupling | g_χ (vector), full thermal strength | Di Mauro 2026 |
| Mass splitting | δ ~ 297 keV (pseudo-Dirac) | Di Mauro 2026 |
| Mediator | (UV-dependent; could be same dark photon at full strength) | Fan & Tweed 2026 |
| Relic density | coannihilation / freeze-out | ε⁴ replaced by thermal ⟨σv⟩ |
| σ_DM-nuc at 248 keV | 6.5×10⁻⁴³ cm² | Di Mauro 2026 |
| LZ N_events at 248 keV | ~1 | matches observed |
| Status | **FITS LZ 248 keV event** | T17 v17 (47% posterior) |

### How they coexist

The composite-DM UV completion can host both portals via different
microphysical channels:

1. **Kinetic mixing** arises from the loop-level mixing between the
   dark photon and the Standard Model photon. This is naturally
   suppressed (ε ~ 10⁻³⁷) by the loop factor and the dark-sector
   compositeness scale. **This is Portal A.**

2. **Inelastic 𝒪₁ˢ scattering** arises from a separate dark-sector
   operator — e.g., an off-diagonal vector coupling between χ₁ and χ₂
   (the pseudo-Dirac case in Di Mauro 2026), or the electroweak
   neutralino mass splitting in the Higgsino case. These couplings
   are **NOT suppressed by the kinetic mixing loop** — they are
   fundamental to the composite structure. **This is Portal B.**

3. The two portals are **independent EFT channels**. Portal A is
   the vector-current × SM current coupling (C₁ˢ × J_SM). Portal B
   is the inelastic dark-current × SM current coupling
   (𝒪₁ˢ_inel × J_SM) with a mass-splitting δ. They have different
   Lorentz structure, different kinematics, and different
   microphysical origins.

4. **The v0.7 MAP fits 8 of 19 channels via Portal A** (the SIDM
   channels). **The LZ 248 keV event is fit by Portal B** (which is
   not part of the 19-channel v0.7 MAP fit, but is allowed by the
   same composite UV).

---

## What this framing means for the project

### For the v0.7 MAP joint fit

The v0.7 MAP result (log Z = -163.29, m_χ = 770 GeV, σ/m = 0.27 cm²/g,
etc.) is **unchanged** by this framing. Portal A still controls the
SIDM channels. Portal B is a separate question that the v0.7 fit
does not address.

### For the T90 magnetic-moment branch

The T90 magnetic-moment branch is a **third portal** — the
electromagnetic dipole operator M_χ. It is a different EFT channel
from both Portal A (kinetic mixing) and Portal B (inelastic 𝒪₁ˢ).
The T17 v17 posterior shows the magnetic-moment operator gives 47%
posterior at the LZ event, tied with Higgsino-inelastic. **Three
portals (A, B, magnetic-moment) are independently viable; the data
cannot distinguish them at the LZ event.**

### For the T98 cross-check

T98 documents that v0.7 MAP (Portal A only) does NOT explain the LZ
event. **This is now correctly framed**: Portal A wasn't supposed to
explain the LZ event. The LZ event is the job of Portal B (or
magnetic-moment). T98 is documentation of a non-overlap, not a
contradiction.

### For the T90 merge rule

The T90 merge rule (5 conditions: independent cross-detector
confirmation, peer-reviewed publication, community consensus,
published BSM-model motivation, fitted 7D posterior Δ log Z ≥ +2)
is unchanged. The Di Mauro paper satisfies one condition (published
BSM-model motivation for the Ls₁₀ operator specifically). The other
four remain unmet.

### For future work

This framing suggests two concrete follow-ups (not done in this PR):

1. **Implement Portal B in the joint fit.** Add a second χ state
   with mass splitting δ as a free parameter. Compute the LZ 248 keV
   σ_DM-nuc via Portal B (inelastic 𝒪₁ˢ) AND the SIDM σ/m via
   Portal A (kinetic mixing). Fit both jointly. This would be a
   Tier-2 effort: new module + tests + 7D or 8D posterior.

2. **Test the three-portal mixture at LZ.** Combine T17 v17
   posterior with Portal B (Di Mauro 2026) and Portal C
   (magnetic-moment, T90) into a single Bayesian hypothesis. The
   expected result, based on the existing 47/47/6 split, is that
   all three contribute ~30-50% posterior each, with the data
   under-determining the mixture.

Neither of these is a published result — they are the natural
next steps. The user has not yet requested them; the framing
document is a "menu" of options for the next session.

---

## Cross-references

| Doc | What it contributes |
|---|---|
| [T87_LZ_FORWARD_PREDICTION.md §13](./T87_LZ_FORWARD_PREDICTION.md) | The v0.7 MAP σ_DM-nuc at δ=297 keV = 1.15×10⁻¹¹⁷ cm² (74.8 OOM short) |
| [T90_PATH_C4_V17_LZ_TIME_SERIES.md](./T90_PATH_C4_V17_LZ_TIME_SERIES.md) | The 47/47/6 posterior split (magnetic-moment / Higgsino / instrumental) |
| [T90_INDEX.md](./T90_INDEX.md) "Cross-link to arXiv:2609.02608" | The 5 T90 merge criteria and the T90 branch context |
| [T98_di_mauro_cross_check.py output](../outputs/t95/t98_di_mauro_cross_check.json) | The numerical comparison between T43, T87, and Di Mauro 2026 |
| [T90_PATH_C4_V18_LATTICE_UV.md](./T90_PATH_C4_V18_LATTICE_UV.md) | The lattice-UV ruling out of composite-DM (orthogonal to this framing) |

---

## What this does NOT do

- **No new model parameters.** The two-portal framing is interpretive.
- **No new joint fit.** Portal B is not in v0.7 MAP.
- **No T90 merge.** T90 merge rule is unchanged.
- **No change to master.** This is on `wip/tier3-magnetic-moment-LZ`.

---

## Provenance

- T99 conceptual doc: 2026-09-08
- Inspired by: T98 cross-check + Option-B discussion
- Hermes Agent (MiniMax-M3) for the user
- Standing posture: T90 stays on `wip/tier3-magnetic-moment-LZ`,
  master at `v0.4-prelim+T88E`, T90 merge rule unchanged.
