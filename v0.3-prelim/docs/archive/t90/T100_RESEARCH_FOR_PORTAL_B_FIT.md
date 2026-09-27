# T100 — Research Findings for Two-Portal Tier-2 Fit (2026-09-08)

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Purpose:** Catalogues external literature and data needed to implement
Portal B (inelastic 𝒪₁ˢ) in the joint fit alongside Portal A (kinetic
mixing ε) per T99.

---

## TL;DR — what we have, what we need, what we can compute

We have:
- 6 published papers analyzing the LZ 248 keV event with quantitative
  cross-section predictions, mass splittings, and m_χ constraints
- The actual S1c/S2c coordinates of the LZ event
- Background rate in the 248 keV region (0.0106 counts)
- Public upper limits from LZ (two-sided 90% CL intervals as function of δ)
- A widely-used recoil-energy-resolution formula

We need to compute:
- The Portal B (inelastic 𝒪₁ˢ) σ_DM-nuc vs (m_χ, δ) for **thermal full
  strength** (not the ε²-suppressed v0.7 MAP form)
- The Portal A (kinetic mixing) σ/m vs (m_φ, ε) — already in v0.7 MAP
- A combined log-likelihood that includes LZ 248 keV event + upper limits
  + existing 19 channels of v0.7 MAP

We can compute the Tier-2 fit in 1-2 weeks. This doc is the menu of
parameters, prior ranges, and external data needed.

---

## External literature catalog

### 1. LZ collaboration paper (arXiv:2609.02823, 2 Sep 2026)

The actual experimental paper. Key data extracted:

| Quantity | Value | Source |
|---|---|---|
| Exposure | 2.84 tonne-years | LZ paper |
| Live days | 220 (Mar 2023 - Apr 2024) | LZ paper |
| Fiducial mass | 4.71 ± 0.08 tonnes | LZ paper |
| ROI (S1c, S2c) | 3 < S1c < 600 phd, S2 > 645 phd, 10^2.75 < S2c < 10^4.15 | LZ paper |
| E_R range | 5.4 - 270 keV | LZ paper |
| Event energy | 248 ± 23 (stat) ± 23 (sys) keV | LZ paper |
| Event S1c | 540.1 phd | LZ paper |
| Event S2c | 9268 phd | LZ paper |
| Event time | 21:22:39 UTC, 16 June 2023 | LZ paper |
| Event position (NR band) | 1.5σ below median NR at that S1c | LZ paper |
| Event position (ER band) | 6.7σ below median ER at that S1c | LZ paper |
| Background in 248 keV region | 0.0106 ± 0.0008 counts | LZ paper |
| Global significance | 2.6σ | LZ paper |
| Local significance | 3.4σ | LZ paper |
| Energy resolution σ | 1.46 × √(E_R/keV) keV | LZ paper (ΔE_R formula) |

**The LZ paper publishes two-sided 90% CL intervals on σ_SI^N as a
function of δ for m_χ = 1 TeV.** This is exactly the prior we need.

### 2. Di Mauro 2026 (arXiv:2609.02608, 2 Sep 2026)

Already documented in T98 and T87 §13. Key data:

| Model | m_χ | δ | σ_DM-nuc | Channel |
|---|---|---|---|---|
| Pseudo-Dirac fermion | ~1 TeV | 297 keV | 6.5×10⁻⁴³ cm² | Inelastic 𝒪₁ˢ (L10s), off-diagonal vector |
| Thermal Higgsino | ~1.1 TeV | 371 keV | (electroweak; ~1.86×10⁻³⁹ cm² per Fan-Tweed) | Inelastic 𝒪₁ˢ (L10s) |

Note: Di Mauro gives the **pseudo-Dirac** σ at 6.5×10⁻⁴³ cm² (not
secluded-WIMP full thermal). The thermal Higgsino is analyzed in
detail by Fan-Tweed.

### 3. Fan & Tweed 2026 (arXiv:2609.01583, 1 Sep 2026)

The Higgsino-specific paper. Most predictive because electroweak
interaction fixes everything except δ.

| Quantity | Value | Formula |
|---|---|---|
| σ_HN (Higgsino-nucleon) | **1.86×10⁻³⁹ cm²** | G_F² μ_N² / (8π) |
| Vector/scalar conversion | 3.2 | [A / ((A-Z) - (1-4sin²θ_W)Z)]² ≈ 3.2 for xenon |
| m_χ (thermal freeze-out) | ~1.1 TeV | Standard thermal relic |
| δ preferred | ~350 keV | Where σ_V^N approaches LZ 90% CL interval |
| δ ≲ 350 keV | "Two-sided CL interval lies below Higgsino" | Thermal Higgsino falls outside 90% CL |
| δ ≳ 350 keV | "Within the two-sided CL interval" | Thermal Higgsino can explain the event |

**The Higgsino prediction is a fixed point, not a free parameter.**
This is the cleanest test of Portal B.

### 4. McCabe 2026 (arXiv:2609.04181, 4 Sep 2026)

Seasonal modulation analysis. Key result for our priors:

| δ (keV) | m_χ lower bound (GeV) | m_χ upper bound (GeV) |
|---|---|---|
| 250 | 149 | ~1000 (escape speed) |
| 300 | 234 | ~1000 |
| 350 | 396 | ~1000 |
| 400 | 817 | ~1000 |

The upper bound is the halo escape speed (~544 km/s + Earth velocity
~232 km/s = ~780 km/s max). At high δ, only the high-velocity tail
of the halo can scatter, which is where the seasonal modulation
signal lives (50-100% modulation amplitude).

**For our fit**: prior on δ should be 1 keV to 400 keV. Prior on
m_χ should be 50 GeV to 2 TeV (with δ < 400 keV allowing higher
m_χ up to the escape-speed limit).

### 5. Gu, Li, Tang, Xu 2026 (arXiv:2609.05291, 4 Sep 2026)

**Inelastic xenon excitation channel:** χ + Xe → χ + Xe* (the xenon
nucleus is excited, not just recoiled). The Xe* de-excites via
gamma emission, adding an electromagnetic component that shifts
the signal toward the ER band.

Key findings:
- The inelastic-xenon rate is **O(0.1) of the elastic rate** for
  most benchmarks — too small to observe soon
- Provides a **complementary test** of inelastic DM interpretations
  of high-recoil events
- Could be observed at next-generation detectors (XLZD, PandaX-xT)

**For our fit**: this is a second-order channel; not critical for
the Tier-2 fit but worth flagging as a future observable.

### 6. XENONnT / PandaX-4T null results

These are already in the project's v0.7 MAP as direct-detection
constraints. Key numbers:

| Experiment | σ_SI upper limit (cm²) | m_χ range (GeV) | Source |
|---|---|---|---|
| XENONnT 3.1 t-yr | ~2×10⁻⁴⁸ (at m_χ = 30 GeV) | 6-1000 | PRL 135, 221003 |
| PandaX-4T | ~3×10⁻⁴⁷ (at m_χ = 40 GeV) | 5-1000 | PRL 134, 011805 |
| LZ 60-day (first) | ~9×10⁻⁴⁸ (at m_χ = 36 GeV) | 9-2000+ | PRL 131, 041002 |

For inelastic (Portal B) constraints, the situation is more complex
because the limit depends on δ. XENONnT and PandaX have both
published inelastic limits but with limited δ reach.

---

## What the Tier-2 fit needs (concrete parameter list)

### New free parameters (Portal B)

| Parameter | Symbol | Prior range | Source for prior |
|---|---|---|---|
| Mass splitting | δ | log-uniform [1 keV, 400 keV] | McCabe 2026 + LZ scan range |
| Dark coupling | g_χ (or g_V) | log-uniform [0.1, 4π] | Standard secluded WIMP range |
| Higgsino-like mass (if applicable) | μ | [800 GeV, 1500 GeV] | Fan-Tweed 1.1 TeV ± 300 GeV |

### New likelihood terms (Portal B)

1. **LZ 248 keV event**: Poisson(N_obs=1 | N_pred(δ, m_χ, σ))
2. **LZ 90% CL upper limits**: from LZ paper, σ_SI^N(δ) curves for
   each tested m_χ (LZ tested 50, 100, 200, 500, 1000, 2000 GeV)
3. **PandaX-4T / XENONnT null results**: similar upper limits
4. **Higgsino fixed-point comparison** (if applicable): compare
   σ_predicted(δ, m_χ) to 1.86×10⁻³⁹ cm² as a χ² term

### Existing Portal A likelihoods (already in v0.7 MAP)

These are unchanged. The 19 channels of the v0.7 MAP joint fit stay.

### Joint fit structure

The new combined loglik is:

```
log L = log L_PortalA(m_φ, m_χ, g_χ, ε, α_χ) + log L_PortalB(δ, m_χ, σ_DM-nuc)
```

where:
- `log L_PortalA` is the existing 19-channel v0.7 MAP likelihood
- `log L_PortalB` is the new LZ + PandaX + XENONnT likelihood
- `m_χ` is **shared** between the two portals (same DM particle)
- All other parameters are independent

This is a 7D-8D fit (5-6 from Portal A + 1-2 from Portal B).

---

## Where the new channels would be implemented

| File | What it would do |
|---|---|
| `v0.3-prelim/code/t100_portal_b_inelastic_likelihood.py` | Compute Portal B loglik for given (δ, m_χ, σ) |
| `v0.3-prelim/code/t100_two_portal_joint_fit.py` | Combined fit driver |
| `v0.3-prelim/data/results/lz_90cl_inelastic_<mchi>.json` | LZ 90% CL upper limit tables (per m_χ) |
| `v0.3-prelim/data/results/xenonnt_inelastic_limits.json` | XENONnT inelastic limits |
| `v0.3-prelim/data/results/pandax_inelastic_limits.json` | PandaX inelastic limits |
| `v0.3-prelim/tests/test_t100_portal_b.py` | Unit tests |
| `v0.3-prelim/docs/T100_TWO_PORTAL_FIT.md` | Final results doc |

---

## What we can compute TODAY vs. what requires data extraction

Today (no new data extraction needed):
- Recoil spectrum as function of (m_χ, δ) — straightforward kinematics
- v_min(m_χ, δ, E_R) — formula given in McCabe 2026
- σ_inel_nuc(δ, m_χ) for the **secluded-WIMP** regime (the Fan-Tweed
  Higgsino case is a fixed point, not a parameter)
- Compare to LZ 90% CL upper limits from the published paper

Requires data extraction (1-2 hours):
- LZ 90% CL upper limit curves as function of δ for each m_χ tested
  (50, 100, 200, 500, 1000, 2000 GeV) — need to OCR or read off figures
- PandaX-4T and XENONnT inelastic limits as function of δ

Requires more work:
- Full LZ S1c-S2c likelihood (not public; would need to fit the
  published {540.1 phd, 9268 phd} event using NEST-like response
  model — Gu et al. 2026 did this and could be replicated)
- S1+S2 systematic uncertainties (correlated between channels)

---

## Prior recommendation

| Parameter | Prior | Justification |
|---|---|---|
| log_δ_MeV | Uniform [-3, -0.4] (1 keV to 400 keV) | McCabe 2026 mass-splitting range |
| log_m_χ_GeV | Uniform [1.7, 3.3] (50 GeV to 2 TeV) | LZ-tested mass range; Higgsino at 1.1 TeV is in this range |
| log_σ_DM_nuc | Uniform [-46, -39] (10⁻⁴⁶ to 10⁻³⁹ cm²) | Spans secluded-WIMP (10⁻⁴³) to Higgsino (10⁻³⁹) |

If using the Higgsino fixed-point model:
| Parameter | Prior | Justification |
|---|---|---|
| δ (Higgsino) | Uniform [1 keV, 400 keV] | Same as above |
| μ (Higgsino mass) | Gaussian(1.1 TeV, 0.3 TeV) | Fan-Tweed prediction |
| σ_HN | **FIXED at 1.86×10⁻³⁹ cm²** | Not a free parameter |

---

## Effort estimate for Tier-2 fit

| Step | Effort | Description |
|---|---|---|
| 1. Data extraction | 1-2 hours | Read LZ paper for 90% CL upper limit tables |
| 2. Portal B likelihood module | 4-6 hours | Compute σ_inel_nuc vs (δ, m_χ), compare to upper limits |
| 3. Two-portal joint fit driver | 4-6 hours | Combine with existing 19-channel v0.7 MAP fit |
| 4. Run fit (8D) | 2-8 hours wall-clock | dynesty nested sampling on 8D posterior |
| 5. Tests + docs | 2-3 hours | Unit tests, fit result JSON, writeup |
| 6. Cross-validation against T17 v17 | 1-2 hours | Check 47/47/6 split is recovered |
| **Total** | **~15-25 hours wall-clock** (3-5 days part-time) | Tier-2 effort |

---

## Cross-references

| Doc | Relevance |
|---|---|
| T87 §13 (existing) | v0.7 MAP σ_DM-nuc at δ=297 keV = 1.15×10⁻¹¹⁷ cm² |
| T90_INDEX "Cross-link to arXiv:2609.02608" (existing) | 5 T90 merge criteria, 1 newly met |
| T98 (existing) | T43 vs Di Mauro numerical comparison |
| T99 (existing) | Two-portal framing |
| T90_PATH_C4_V17 (existing) | 47/47/6 posterior (magnetic-moment / Higgsino / instrumental) |
| **T100 (this doc)** | Research findings for Tier-2 fit |

---

## Standing reminders

- T90 merge rule is unchanged (Di Mauro satisfies 1 of 5 criteria)
- Master untouched at v0.4-prelim+T88E
- T90 branch is `wip/tier3-magnetic-moment-LZ`
- Tier-2 fit would also live on this branch

---

## Provenance

- T100 research compilation: 2026-09-08
- 6 external papers analyzed
- 1 user request (proceed B after T99 framing)
- Hermes Agent (MiniMax-M3)
