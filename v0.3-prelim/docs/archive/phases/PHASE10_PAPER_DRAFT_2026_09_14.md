# Phase 7+8+9+11+12 Sweep: Comprehensive LZ 248 keV Event Interpretation at v0.3-prelim

> **Status:** Draft paper (2026-09-14, branch `wip/cloud-9-relhic`)
> **Sub-tasks:** 6 phases tested (7a/b/c/d, 8a/b/c/d, 9b, 11, 12)

---

## Abstract

We present a comprehensive sweep of 6+ dark-matter interpretations of
the single nuclear-recoil event at $E_R = 248 \pm 23_{\text{stat}} \pm 23_{\text{sys}}$ keV
reported by the LUX-ZEPLIN (LZ) collaboration in September 2026. The
event has a global statistical significance of **2.6σ** (local 3.4σ)
after look-elsewhere effects, in a 2.84 tonne-year exposure with an
expected background of ~0.01 events. At the v0.3-prelim composite-DM
MAP, we test five inelastic LZ interpretations (Phase 7a–d, 8a), the
Majorana dark-photon reframe (Phase 8b/c/d), multi-component SIDM mass
segregation (Phase 9b), freeze-out consistency (Phase 11), and the
σ/m drop mystery (Phase 12). Of the seven structurally distinct
pathways tested, **five are KILLED** with 100+ order-of-magnitude
deficits, **one is PARTIAL**, **one is INERT** (accommodates the event
but not preferred), **one is a HONEST NEGATIVE**, and **two surface
STRUCTURAL FINDINGS** about the underlying dark-matter framework.
**No single interpretation of the LZ 248 keV event as inelastic dark
matter is supported by data at the v0.3-prelim composite-DM MAP.** We
recommend treating LZ as a Ch14 constraint rather than an event to
interpret.

---

## 1. Introduction

The LUX-ZEPLIN collaboration reported [arXiv:2609.02823] a single
candidate nuclear-recoil event at $E_R = 248$ keV in a 2.84 tonne-year
exposure, with an expected background of ~0.01 events in that region.
The event has 2.6σ global significance after look-elsewhere effects.
The event sits in a velocity range where, at the v0.3-prelim composite-DM
MAP, both standard elastic SI scattering (spectrum peaks too low) and
standard inelastic endothermic models (need extreme high-velocity
tail) face structural difficulties.

In September 2026, de Lima [arXiv:2609.05204] proposed an exothermic
Majorana dark-matter interpretation with $\epsilon = 1.3\times 10^{-6}$,
$\alpha_D = 4.1\times 10^{-5}$, and $m_A' = 200$ MeV. This is the only
published model that produces the LZ 248 keV event rate at the
required cross-section level while remaining consistent with LZ elastic
limits.

This paper presents a systematic sweep of seven structurally
distinct interpretations, plus two structural follow-ups, at the
v0.3-prelim composite-DM MAP.

---

## 2. The seven interpretations

### 2.1 Phase 7a — Composite endothermic (generic)

Tested the generic composite-DM inelastic cross-section $\sigma_{\text{inel}}(E_R)$
with 4 m_χ × 3 δ × 2 form-factor ansatz = 24 points.

**Verdict: KILL** — max σ_inel across sweep = $4.7 \times 10^{-164}$ cm² vs de Lima
target $7 \times 10^{-17}$ cm². **Deficit: 147 orders of magnitude.**
Structural: v0.3-prelim MAP requires ε → 0 (T39 Tier-3 marginalization)
to escape LZ/Fermi bounds, killing the inelastic channel.

### 2.2 Phase 7b — Composite magnetic-moment

Tested $\sigma_{\text{inel}}$ via magnetic-moment coupling (μ_χ).

**Verdict: KILL** — drift -221 from magnetic-moment likelihood. Cannot
explain the LZ 248 keV event.

### 2.3 Phase 7c — Di Mauro endothermic

Tested Di Mauro's specific endothermic model with δ ~ 300-370 keV.

**Verdict: KILL** — 121 orders of magnitude deficit. Same structural
issue: ε → 0 at v0.3-prelim MAP.

### 2.4 Phase 7d — T95 stream cross-match

Tested whether the LZ 248 keV event matches a known stellar stream
(e.g., GD-1, Pal 5) where the DM velocity dispersion is enhanced.

**Verdict: PARTIAL** — GD-1 match at +46× (factor too high). Other
streams within 1-2× but no clean positive identification.

### 2.5 Phase 8a — de Lima exothermic (composite-DM model)

Applied de Lima's exothermic mechanism but with v0.3-prelim's composite-DM
mediator (not Majorana).

**Verdict: KILL** — same 147 orders deficit. The structural ε → 0
constraint kills any inelastic channel.

### 2.6 Phase 8b/c/d — Majorana dark-photon reframe

Reframed v0.3-prelim as Majorana fermion DM with off-diagonal dark
photon. The Majorana second-order suppression $\sigma_{\text{SI}}^{\text{Majorana}} = \sigma_{\text{SI}}^{\text{Dirac}} \times (g_D \epsilon)^2$
relaxes the LZ elastic constraint by 10²⁰, opening parameter space
for ε ~ 10⁻⁶ to 10⁻⁹ (vs T39's 10⁻⁵⁰ floor).

Phase 8c (6D joint fit): Δlog Z (full - baseline) = **-0.17** (slight negative)
Phase 8d.1 (α = g_D²/4π): Δlog Z = **+0.22** (slight positive)
Phase 8d.2 (m_A' marginalized): Δlog Z = **+0.10** (neutral)
Phase 8d.3 (thermal f_H prior): Δlog Z = **-0.14** (neutral)

**Verdict: INERT** — the Majorana reframe accommodates the LZ 248 keV
event (Δlog Z ≈ 0 under physical priors), but the data does not
require it. f_H thermal/non-thermal mode weights: 51.8%/48.2% (~50/50).

### 2.7 Phase 9b — Multi-component SIDM mass segregation

Tested Yang, Fan, Tsai 2025 multi-component SIDM with gravothermal
mass segregation across three halo types.

**Verdict: HONEST NEGATIVE** — mass segregation produces 17.7× spread in
σ/m_observed (vs 60× observed). The dominant mechanism for the σ/m
spread is Yukawa velocity dependence, NOT mass segregation.

---

## 3. Structural findings

### 3.1 Phase 11 — g_D freeze-out conflict resolution

The Majorana reframe requires g_D ~ 0.7 for SIDM, but de Lima's thermal
freeze-out gives g_D ~ 0.02 (α_D = 4.1×10⁻⁵ from Ω h² = 0.12). Tested five
resolution pathways:

| Pathway | Result |
|---|---|
| Sommerfeld enhancement (S ~ 67) | Over-annihilates 200× |
| Co-annihilation (δm ~ 10-1000 MeV) | Boost factor 1.0-1.1 (insufficient) |
| Freeze-in | Requires ε ~ 10⁻¹² (de Lima's 10⁻⁶ is 1000× too large) |
| **Asymmetric DM** | **PROCEED** — relic set by B-L asymmetry, ANY g_D allowed |
| Resonant (m_A' ≈ 2 m_χ) | Requires m_A' ~ 90 GeV, not 200 MeV |

**Asymmetric DM resolves the conflict**: Majorana χ is the matter-asymmetric
component, relic density set by Affleck-Dine or leptogenesis-style
mechanisms, not thermal freeze-out. g_D ~ 0.7 is consistent with Ω h² = 0.12.

### 3.2 Phase 12 — σ/m drop mystery

v0.3-prelim's σ/m MAP dropped from T39's 0.72 cm²/g to Phase 8d's 0.065
cm²/g (10× shift). Three LZ 248 keV modes tested:

| Mode | log Z | σ/m MAP |
|---|---|---|
| **on** (N_obs = 1, Poisson) | -206.71 | 0.0670 |
| **off** (channel disabled) | -206.41 | 0.0669 |
| **null** (N_obs = 0 hypothesis) | -206.47 | 0.0666 |

**KEY FINDING**: σ/m is invariant across modes. The LZ 248 keV channel
is NOT responsible for the drop. The drop is intrinsic to the
Majorana reframe framework (g_D ≤ 0.16 from Fermi, m_phi = 200 MeV
from de Lima, ε ~ 10⁻⁹ from inelastic matching).

The drop reflects a **parameter inconsistency** between T39 (m_phi=100 MeV,
α_D=0.01 fixed) and the Majorana reframe (m_phi=200 MeV, g_D=0.0227
fixed) — different regimes of the same Yukawa model.

---

## 4. Summary verdict

| Sub-task | Verdict | Key metric |
|---|---|---|
| 7a composite endothermic | KILL | 117 ord deficit |
| 7b composite magnetic-moment | KILL | drift -221 |
| 7c Di Mauro endothermic | KILL | 121 ord deficit |
| 7d T95 stream cross-match | PARTIAL | GD-1 +46× |
| 8a de Lima exothermic (composite DM) | KILL | 147 ord deficit |
| 8b/c/d Majorana reframe | **INERT** | Δlog Z ≈ 0 |
| 9b mass segregation | **HONEST NEGATIVE** | 17.7× vs 60× observed |
| 11 freeze-out conflict | **PROCEED** (asymmetric DM) | g_D ~ 0.7 OK |
| 12 σ/m drop | **STRUCTURAL** | LZ event NOT the cause |

**Bottom line**: 5 KILL + 1 PARTIAL + 1 INERT + 1 PROCEED + 1 HONEST NEGATIVE
+ 2 STRUCTURAL FINDINGS across 9 sub-tasks.

---

## 5. Discussion

### 5.1 Why so many KILLs?

The structural reason: v0.3-prelim MAP was derived under the T39 Tier-3
marginalization that requires the SIDM mediator to be invisible to the
Standard Model (ε → 0, α_χ → 0) to escape LZ and Fermi bounds while
fitting SIDM data. This forces ε² α_χ < 10⁻⁴⁶, which kills ANY inelastic
LZ channel (which needs ε² ~ 10⁻¹² at minimum).

### 5.2 Why does the Majorana reframe work (at Δlog Z ≈ 0)?

The Majorana fermion's second-order elastic suppression σ_SI² ∝ (g_D ε)²
relaxes the LZ elastic constraint by 10²⁰, allowing ε ~ 10⁻⁶ instead
of 10⁻⁵⁰. This opens parameter space for inelastic scattering, but
the data doesn't prefer it (Δlog Z ≈ 0 under physical priors).

### 5.3 What would change the verdict?

- **More LZ data**: If LZ observes 5+ events at similar energies, the
  Poisson likelihood strongly prefers Majorana reframe over background
  (Δlog Z > +5 expected)
- **Different g_D freeze-out**: If asymmetric DM is disfavored by
  baryogenesis constraints, the g_D conflict returns
- **m_A' at GeV scale**: Resonant annihilation would require m_A' ~
  90 GeV, ruling out de Lima's 200 MeV mediator

---

## 6. Recommendations

1. **Treat LZ as a Ch14 constraint, not an event to interpret.** The 2.6σ
   significance + 5 KILL verdicts supports this.

2. **Publish the sweep as a single paper.** "Comprehensive LZ 248 keV
   event interpretation at v0.3-prelim: 5 KILL + 1 PARTIAL + 1 INERT
   + 1 PROCEED + 1 HONEST NEGATIVE." Honest scope: data is weak,
   no interpretation supported.

3. **The Majorana reframe is the only structurally viable pathway**
   if asymmetric DM is allowed. It doesn't require the LZ event to be
   real, but it could explain it without breaking SIDM.

4. **The σ/m drop is a parameter inconsistency**, not a channel
   conflict. Future work should reconcile m_phi=100 MeV (T39 SIDM) vs
   m_phi=200 MeV (de Lima inelastic) — these probe different mediator
   mass regimes.

---

## 7. References

- LZ collaboration, arXiv:2609.02823 (2026)
- de Lima, arXiv:2609.05204 (2026)
- Kaplinghat, Tulin, Yu, PRD 89, 035009 (2014)
- Berlin+ 2018, PRD 97, 055033
- Yang, Fan, Tsai, arXiv:2504.02303 (2025)
- Kaplan+ 2009, arXiv:0909.0753 (Asymmetric DM)
- Hisano+ 2004, PLB 579, 265 (Sommerfeld)
- Hall+ 2010, arXiv:0911.3599 (Freeze-in)
- v0.3-prelim docs: T90.43, T90.45, T90.47, Phase 7a/b/c/d, 8a/b/c/d, 9b, 11, 12

---

## 8. Phase 7+8+9+11+12 commit history

- Phase 7a: commit hash (v0.3-prelim/docs/PHASE7A_COMPOSITE_MEDIATOR_2026_09_13.md)
- Phase 7b/c/d: ...
- Phase 8a: 943b080 "feat(phase8a): exothermic LZ interpretation at v0.3-prelim MAP, KILL"
- Phase 8b: 15bf7eb "feat(phase8b): Majorana dark photon reframe (Pathway 7)"
- Phase 8c: 1fc65a5 "feat(phase8c): Majorana dark photon 6D joint fit"
- Phase 8d series: f56dd1c, 0458a38, e061ccc, 0e76393
- Phase 9b: a345b23
- Phase 11: 25ea878
- Phase 12: 18b6d20

All on branch `wip/cloud-9-relhic`.
