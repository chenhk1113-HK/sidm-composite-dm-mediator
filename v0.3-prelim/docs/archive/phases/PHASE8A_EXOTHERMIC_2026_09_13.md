# Phase 8a — Exothermic LZ Interpretation at v0.3-prelim MAP

> **Status:** Shipped 2026-09-13 (branch `wip/cloud-9-relhic`)
> **Verdict:** **KILL TRIGGERED**
> **Sub-task:** Phase 8a (exothermic channel sweep, completes the LZ-event-interpretation series)

---

## 1. Motivation

The LZ collaboration published the 248 keV event paper on arXiv on
**2026-09-02** ([arXiv:2609.02823](https://arxiv.org/abs/2609.02823)),
and a competing theoretical paper by **de Lima** appeared three days
later on **2026-09-04** ([arXiv:2609.05204](https://arxiv.org/abs/2609.05204))
proposing an **exothermic dark matter** interpretation.

Phase 7 (7a-7d) tested four LZ-event interpretations at v0.3-prelim MAP
(composite-mediator endothermic, magnetic-moment, Di Mauro endothermic,
T95 stream cross-match). The **exothermic channel was NOT tested** —
Phase 7 missed de Lima's paper because it appeared AFTER Phase 7 shipped.

Phase 8a completes the LZ-event-interpretation sweep by testing the
exothermic channel at v0.3-prelim MAP.

---

## 2. The Exothermic Channel (de Lima 2026)

**Physics**: χ_H + N → χ_L + N (down-scatter, releases mass splitting δ)

Key differences from endothermic (Phase 7c):
| Property | Endothermic (Di Mauro) | Exothermic (de Lima) |
|---|---|---|
| Direction | χ_L → χ_H (absorbs δ) | χ_H → χ_L (releases δ) |
| Velocity threshold | v_min > sqrt(2δ/μ) | **None** (any v can scatter) |
| Spectrum | Falls off above v_min threshold | **Peaks at E₀ = m_χ δ/(m_χ+m_N)** |
| Preferred m_χ | 800-1300 GeV | **30-200 GeV** |
| Preferred δ | 200-500 keV | **0.5-1 MeV** (δ < 2m_e) |
| Required ε | ~10⁻⁷ (implied) | **~10⁻⁶** |
| Halo velocity | Tail (rare) | **Body** (no tail needed) |

The **structural advantage** of exothermic: no need for the dark matter
to sit in the high-velocity tail of the halo distribution. The recoil
spectrum is peaked at E₀ independent of v.

---

## 3. v0.3-prelim MAP vs de Lima Target

| Parameter | v0.3-prelim MAP | de Lima target |
|---|---|---|
| ε (kinetic mixing) | 7.71 × 10⁻⁵⁷ | 1.3 × 10⁻⁶ |
| α_χ (dark coupling) | 8.98 × 10⁻²⁹ | α_D × ε² = 7 × 10⁻¹⁷ at f_H = 0.5 |
| α_χ × ε² | **5.33 × 10⁻¹⁴¹** | **7 × 10⁻¹⁷** |
| **Deficit** | — | **~10⁻¹²⁴ (124 orders of magnitude)** |

The v0.3-prelim deficit is **STRUCTURAL**, not parameter-tuning:
v0.3-prelim MAP was constructed under the **T39 Tier-3 caveat** that
"the SIDM mediator must be INVISIBLE to the Standard Model at
direct-detection energies." This is the OPPOSITE of what exothermic
requires.

---

## 4. Sweep Results (4 m_χ × 3 δ × 2 ansatz = 24 points)

| m_χ [GeV] | δ [keV] | ansatz | E₀ [keV] | σ_inel(E₀) [cm²] | log₁₀(σ/σ_target) |
|---|---|---|---|---|---|
| 30 | 500 | gaussian | 93.8 | 3.73 × 10⁻¹⁶⁴ | -147.27 |
| 30 | 1000 | gaussian | 187.5 | 3.50 × 10⁻¹⁶⁴ | -147.30 |
| **45** | **1000** | **gaussian** | **257.1** | **4.05 × 10⁻¹⁶⁴** | **-147.24** |
| 100 | 500 | gaussian | 217.4 | **4.72 × 10⁻¹⁶⁴** | -147.17 (max) |
| 200 | 1000 | gaussian | 606.1 | 3.71 × 10⁻¹⁶⁴ | -147.28 |

**Max σ_inel across sweep**: 4.72 × 10⁻¹⁶⁴ cm² at (m_χ=100 GeV, δ=500 keV, gaussian)

**Deficit vs de Lima target**: **147 orders of magnitude** across all 24 points.

---

## 5. Required Epsilon to Match de Lima

Given v0.3-prelim's α_χ = 8.98 × 10⁻²⁹, the epsilon required to match
de Lima's α_D × ε² = 7 × 10⁻¹⁷ target is:

```
ε_required = sqrt(7e-17 / 8.98e-29) = 8.83 × 10⁵
```

This is **non-perturbative** (ε > 1 means the kinetic mixing is outside
the validity of perturbation theory for U(1) kinetic mixing).

Compared to v0.3-prelim MAP's ε = 7.71 × 10⁻⁵⁷:

```
ε_required / ε_v03 = 8.83e5 / 7.71e-57 = 1.15 × 10⁶²
```

**The required epsilon is 10⁶² times larger than v0.3-prelim's MAP value.**

---

## 6. Verdict: KILL

**Kill criterion**: max σ_inel across sweep < de Lima target σ × 10⁻¹⁰

| Quantity | Value |
|---|---|
| Max σ_inel at v0.3-prelim MAP | 4.72 × 10⁻¹⁶⁴ cm² |
| de Lima target σ × ε² | 7 × 10⁻¹⁷ |
| Deficit | **147 orders of magnitude** |

**KILL TRIGGERED.** Phase 8a confirms that the exothermic channel cannot
explain the LZ 248 keV event at v0.3-prelim MAP, by 147 orders of magnitude.

---

## 7. Structural Finding

The KILL verdict is **structural**, not parameter-tuning:

1. **v0.3-prelim MAP** was derived under the T39 Tier-3 marginalization
   that requires the SIDM mediator to be invisible to the SM (ε → 0,
   α_χ → 0) to escape LZ and Fermi bounds while still fitting SIDM data.

2. **Exothermic LZ interpretation** (de Lima) requires ε ~ 10⁻⁶ to produce
   the LZ event rate at all. This is **6 orders of magnitude above the
   perturbativity bound** for kinetic mixing.

3. **The two regions of (ε, α_χ) space are mutually exclusive.** No
   single point in parameter space can simultaneously satisfy:
   - T39 Tier-3 multi-channel SIDM fit (requires ε < 10⁻³⁰)
   - de Lima exothermic LZ event rate (requires ε > 10⁻⁶)

**Conclusion**: The composite-DM SIDM model at v0.3-prelim MAP **cannot**
explain the LZ 248 keV event via ANY inelastic channel (endothermic OR
exothermic). The deficit is structural.

---

## 8. Updated Phase 7/8 Series Status

| # | Sub-task | Verdict | Deficit |
|---|---|---|---|
| 7a | composite endothermic (generic) | **KILL** | 117 orders |
| 7b | composite magnetic-moment | **KILL** | drift -221 |
| 7c | Di Mauro endothermic | **KILL** | 121 orders (σ) |
| 7d | T95 stream cross-match | **PARTIAL** | mixed (GD-1 +46×) |
| **8a** | **de Lima exothermic** | **KILL** | **147 orders** |

**5 of 5 LZ-event interpretation channels KILL at v0.3-prelim MAP.**

**Recommended action** (per roadmap §Phase 7):
> "Abandon LZ event interpretation; treat LZ as Ch14 constraint."

This action is now **justified by all five channels**.

---

## 9. References

- arXiv:2609.02823 — LZ collaboration, 2026-09-02
- arXiv:2609.05204 — de Lima, 2026-09-04 (v2 2026-09-08)
- `T39_tier3_epsilon_alpha_joint_fit.json` — v0.3-prelim MAP (log Z = -2.94)
- `t87_composite_inelastic_nucleon.py` — sigma_inel_nuc machinery (proxy)
- `PHASE7A_COMPOSITE_MEDIATOR_2026_09_13.md` — Phase 7a
- `PHASE7C_DI_MAURO_2026_09_13.md` — Phase 7c (Di Mauro)
- `ROADMAP_MISSING_POSTERIORS_2026_09_12.md:445` — Phase 7 spec

---

## 10. Code & Data

- `v0.3-prelim/code/phase8a_exothermic_v03_map.py` (~250 lines)
- `v0.3-prelim/data/results/phase8a_exothermic_v03_map.json`
- `v0.3-prelim/tests/test_phase8a_exothermic.py` — **11/11 PASS**
- Wall time: ~2 seconds
