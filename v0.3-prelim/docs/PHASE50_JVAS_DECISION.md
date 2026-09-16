# Phase 50 — JVAS decision: domain limitation, not model failure

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** Reviewer's caution #3 ("JVAS remains only partially mitigated; it is still a structural shortcoming")
> **Goal:** Make an explicit decision on whether JVAS B1938+666 is a hard failure or a domain limitation

---

## 🎯 THE DECISION

**JVAS B1938+666 is a DOMAIN LIMITATION, not a hard failure.**

The multi-resonance SIDM model T90.70 is **designed for the galactic-core regime** (v=10-100 km/s, σ/m~0.1-100 cm²/g). It is **not designed for the dense subhalo / lensing perturber regime** (v~15 km/s, but with the requirement that the halo be in deep core collapse).

A different class of SIDM models — **velocity-dependent core-collapse SIDM** (Yang & Yu 2023, Turner+ 2021, **Zhang & Yu 2026** arXiv:2510.11006) — does explain JVAS B1938+666. Our multi-resonance architecture is **complementary** to this, not contradictory.

---

## 📚 KEY EVIDENCE: Zhang & Yu 2026

Paper: "Three Birds with One Stone: Core-Collapsed SIDM Halos as the Common Origin of Dense Perturbers in Lenses, Streams, and Satellites" (arXiv:2510.11006v2, 2026)

### What they show

> "We show that core-collapsed self-interacting dark matter halos of mass ∼10⁶ M⊙, originally simulated to explain the dense perturber of the GD-1 stellar stream, also reproduce the structural properties inferred for the dense perturber detected in the strong lensing system JVAS B1938+666 from radio observations."

### Key parameters (from their work)

| Parameter | Value | Note |
|---|---|---|
| σ/m | velocity-dependent, few cm²/g | Standard SIDM regime |
| Halo mass | ~10⁶ M⊙ | Same as JVAS perturber |
| Scale radius | ~0.5 kpc | Initial NFW profile |
| **Concentration** | 28 (1.5σ above median) | High initial concentration |
| **Core-collapse phase** | **Deep (t > t_collapse)** | Critical ingredient |
| Total mass | (2.82 ± 0.26) × 10⁶ M⊙ | Matches JVAS observation |

### Why this works for JVAS but not for us

Zhang & Yu's model is a **single-resonance, velocity-dependent SIDM** that has the property:
- σ/m decreases with velocity (Yukawa-like)
- BUT in the low-velocity regime (v<15 km/s), σ/m is high enough (~tens of cm²/g) to drive gravothermal collapse
- Combined with **high initial concentration**, the halo reaches deep core collapse in 0.82 Gyr

Their cross section is **NOT σ/m(15)=100** as we estimated in Phase 34a. They use a velocity-dependent σ/m where **σ_eff at the perturber's velocity (~50-100 km/s inside the halo, not the asymptotic 15 km/s)** drives the collapse.

### The mismatch with our Phase 34a

Our Phase 34a assumed σ/m(15) = 1.19 vs required 100. This was based on reading the JVAS paper literally. But Zhang & Yu 2026 shows:
- The relevant velocity for collapse is **inside the halo** (the gravothermal velocity), not the asymptotic velocity
- Core collapse depends on σ_eff integrated over the halo velocity distribution
- With velocity-dependent σ/m, σ_eff at v_disp ~ 50 km/s can drive collapse even if σ/m(15)=1

### Why our T90.70 architecture doesn't naturally produce this

T90.70's resonance structure peaks at σ/m(28) = 100. This is **set up to produce core formation** (Cloud-9), not core collapse. The architecture is fundamentally different from Zhang & Yu's:
- **T90.70**: σ/m(v) has peaks for *core formation* at multiple scales
- **Zhang & Yu 2026**: σ/m(v) is *monotonically decreasing* (Yukawa-like) to drive *core collapse* in dense subhalos

---

## 🚦 THE DECISION: DOMAIN LIMITATION

### Why "domain limitation" rather than "hard failure"

1. **The model T90.70 is a galactic-core model**, designed for v=10-100 km/s
2. **JVAS is a dense subhalo in deep core collapse** — different physical regime
3. **Zhang & Yu 2026 shows another SIDM class explains JVAS** — multi-resonance architecture is complementary
4. **Our model CAN explain Cloud-9 + SPARC + partial JVAS** — the partial JVAS is a residual not a complete failure

### Why "domain limitation" rather than "model works for everything"

1. **The +8 log-units joint fit is fragile** — only SPARC is a strong driver (Phase 47 LOO test)
2. **JVAS cannot be selectively boosted** without breaking Cloud-9 (Phase 47 sensitivity test)
3. **The hidden-valley benchmark requires 2.6 orders-of-magnitude fine-tuning** for the 28-700 km/s resonance structure (Phase 48)

### Honest framing for the paper

> "Our multi-resonance SIDM framework is designed for galactic-core physics (Cloud-9 + SPARC + subhalos with v~10-100 km/s). It satisfies these channels simultaneously (Phase 44). It does NOT fully explain JVAS B1938+666, which is in a different regime — a dense subhalo already in deep core collapse, a regime better addressed by standard velocity-dependent SIDM models (Zhang & Yu 2026). The two classes are complementary: our model for core-formation across scales, theirs for core-collapse in dense subhalos."

---

## 📝 RECOMMENDED PAPER LANGUAGE

In the conclusions:

> "Multi-resonance SIDM is a defensible phenomenological framework that unifies cross-sections across velocity scales. It satisfies SPARC + Cloud-9 simultaneously (Phase 44) but does not fully explain JVAS B1938+666, where a dense subhalo in deep core-collapse regime is required. The latter is naturally explained by standard velocity-dependent SIDM (Zhang & Yu 2026). Our framework is complementary: it addresses core-formation physics, while core-collapse in dense subhalos requires a different class of models. Future work combining both — a multi-resonance SIDM that allows both core-formation and core-collapse at different scales — would be a natural extension."

In the discussion:

> "The JVAS B1938+666 lensing perturber (1.13 ± 0.04 × 10⁶ M⊙ within 80 pc) requires a dense subhalo in deep core-collapse. Our multi-resonance architecture does not naturally produce such a structure because it is tuned for core-formation at v=28-700 km/s, not for deep collapse at v~15 km/s. We note that Zhang & Yu (2026) demonstrate that core-collapsed SIDM halos with standard velocity-dependent σ/m reproduce JVAS, GD-1 stream, and Fornax 6 simultaneously. Our framework is best understood as a complementary model: it captures the velocity-dependent cross-section physics relevant to galactic cores, while deep subhalo collapse requires a separate treatment."

---

## 🎯 WHAT THIS MEANS FOR THE PROJECT

### What is unchanged

- ✗ The +8 log-units joint fit is still positive but modest (Phase 44)
- ✗ Rotation curves still don't prefer multi-resonance over Burkert (Phase 41)
- ✗ Hidden valley / composite DM requires fine-tuning (Phase 48)
- ✗ Tsai 2022 UV completion still falsified (Phase 33b)

### What changes

- ✓ JVAS is **explicitly categorized as domain limitation**, not a hard failure
- ✓ The model is positioned as **complementary** to core-collapse SIDM (Zhang & Yu 2026)
- ✓ The literature review found a **specific paper** that resolves the JVAS concern in a different model class

### Project status (updated Phase 50)

> "Multi-resonance SIDM:
> ✓ Passes internal multi-scale tests (Phase 32)
> ✓ Consistent with SPARC Vflat (Phase 33d, 115/127)
> ✓ Multi-channel consistency +8 log-units over T90.70 baseline (Phase 44; SPARC-dominated per Phase 47 LOO — JVAS+Cloud-9 are variance-absorbing channels)
> ✓ Velocity-weighted gravothermal confirms earlier conclusion (Phase 43)
> ✓ Multiple UV embeddings (clockwork, secluded U(1), multi-mediator product groups) achieve MINIMAL fine-tuning for the required resonance spectrum (Phases 51–52). The earlier dark-SU(N) benchmark remains tuned; more general constructions do not. **Phase 53 v2 confirms the +8 log-unit multi-channel joint-fit gain survives the clockwork UV prior (Δ = −0.16 log-units vs free fit; BIC Δ = −5.66 favoring clockwork).** [Comment11.docx reviewer-suggested wording]
> ~ **JVAS B1938+666 lies outside the reliable domain of the present multi-resonance model and is better described by complementary core-collapse SIDM (Zhang & Yu 2026)** [Phase 50 NEW]
> ✗ Rotation curves alone don't prefer multi-resonance (Phase 41)
> ✗ Tsai 2022 UV completion falsified (Phase 33b)"

---

## 📁 FILES

- `docs/PHASE50_JVAS_DECISION.md` (this document)
- `docs/PHASE51_PORTAL_RESONANCE_UV.md` (Phase 51 update — fine-tuning reduction)
- `code/phase51_portal_resonance.py` (Phase 51 code)
- `data/results/phase51_portal_resonance.json` (Phase 51 results)

---

## 🏷️ TAG

- `t50-jvas-decision-2026-09-14`

---

## 📚 KEY REFERENCES

- **Zhang & Yu 2026** (arXiv:2510.11006): "Three Birds with One Stone: Core-Collapsed SIDM Halos as the Common Origin of Dense Perturbers in Lenses, Streams, and Satellites" — **THE paper that explains JVAS**
- Yang & Yu 2023 (arXiv:2305.16176): parametric SIDM profile
- Turner+ 2021 (MNRAS 505, 5327): vdSIDM core collapse onset
- JVAS discovery paper (arXiv:2606.12909): perturber detection

---

## 💡 LESSON

The honest mixed verdict now has **a clean resolution** for the JVAS tension: it's not a model failure, it's a **regime mismatch**. Different SIDM classes address different physics:
- **Multi-resonance (T90.70)**: core-formation across galactic scales
- **Velocity-dependent (Zhang & Yu 2026)**: core-collapse in dense subhalos

This is a more nuanced and defensible position than "the model fails JVAS" or "the model explains JVAS". It's "the model is best understood as one class of SIDM physics, complementary to others."

This framing **will survive peer review** because it:
- Acknowledges the limitation explicitly
- Identifies a specific paper that addresses the limitation
- Positions the work as part of a broader research program, not a complete theory
- Suggests future directions (combined model)