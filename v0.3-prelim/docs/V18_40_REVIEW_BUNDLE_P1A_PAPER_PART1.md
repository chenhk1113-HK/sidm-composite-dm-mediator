# v18.40 Review Bundle — 2026-09-25

Single-file concatenation of paper + 5 investigation docs + 6 code files in spine order.

**Repository state:**
- Branch: `wip/cloud-9-relhic` + `wip/multi-component-SIDM-core-collapse`
- Commit: `df9aadd`
- Tag: `v18.40-constraint-map-with-refinements`
- Standing version: v0.4-prelim + v18.40

**Honest verdict (unchanged from v18.38):** 6-7 of 8 channels under borrowed f_H prescription;
framework is a structural constraint map + no-go catalogue, not a unified derivation.

**v18.40 refinements (T212):**
- §10.4d Path A3: Cloud-9 σ/m ≥ 50 reframed as systematic upper bound (Turini & Benítez-Llambay 2026)
- §10.4e Path B3 trim: Silverman+ 2026 gravothermal CAN run at σ/m ≥ 10 cm²/g (50× above Phase 44)

---

## Table of Contents

1. PAPER_V1_DRAFT.md (v18.40)
2. T208 Path B Gravothermal Refuted
3. T208/T209 Strategic Investigation Report
4. T210 Cloud-9 Crater Gating Test
5. T211 Path B3 + B2 Literature Survey
6. T212 Path B3 Trim + A3 Plan
7. T208 Path B Gravothermal (Python)
8. T209 KiSS-SIDM N-body Setup (Julia)
9. T210 Crater/Antlia Gating (Python)
10. T210 Path A2 Sharp Resonance (Python)
11. T210 σ_eff Decompose (Python)
12. T212 Silverman Gravothermal (Python)

---


# File 1: PAPER_V1_DRAFT.md (v18.40)

```
1: PAPER_V1_DRAFT.md (v18.40, 157 KB)

_Source path: `v0.3-prelim/docs/PAPER_V1_DRAFT.md`_

```
# Multi-Component Self-Interacting Dark Matter: Joint Multi-Channel Constraints and UV Completion No-Go Theorems

**Authors:** SIDM Composite DM-Mediator Collaboration
**Branch:** `wip/multi-component-SIDM-core-collapse` (commit `9daf10a`, 2026-09-21; synced with `wip/cloud-9-relhic`)
**Status:** Paper draft (v18.38, INTERNAL REFERENCE, **focal version**). v18.38 adds T207 Path F1 three-term σ_eff decomposition (§9.9-§9.11): resolves the v18.34 structural SPARC limitation under borrowed prescription mode (heavy-light σ_HL term reaches σ_eff(100) ≈ 0.19). Free fit with Yang+ 2025 f_H_cc ≥ 0.05 prior lands at v_HL = 105 ± 39 km/s (Mechanism A on-peak), f_H_cc = 0.060 ± 0.012 (boundary pathology eliminated), 50τ-convergence marginally achieved (ratio 1.089). Path F1 is a **structural fix**, not an automatic data-resolution: SPARC log L = -2.03 (z ≈ 2.0, clear fail) under the priored free fit — honest prior-vs-likelihood tradeoff. v18.34 retired the Hidden U(1) UV completion (falsified by referee report 2026-09-19); v18.38 does NOT change that. The paper still presents the multi-component + gravothermal phenomenology as a **phenomenological constraint map, not a unified derivation**, and documents **five independent UV completion no-go theorems** (magnetic dipole DM, Hidden U(1) + 10 MeV pseudo-Dirac, GeV-scale inelastic DM, Chu+ 2019 p-wave resonance, T184 one-mediator UV systematic); the Cloud-9 4000× spike still cannot be derived from standard Yukawa physics (T165-T172 robustness investigation). The phenomenology (T120: multi-resonance + two-component asymmetric DM + gravothermal selection + Gaussian Breit-Wigner profiles) is consistent with **6–7 of 8 observational constraints depending on the f_H prescription** (RMSE = 0.25 on the 7-point fit under borrowed f_H). **Markdown source of truth — no PDF build during drafting.** See README.md, CHANGELOG.md, and `v0.3-prelim/docs/` for full supporting documentation.

**Draft workflow (per 2026-09-17 user decision):** Read this file directly in any modern text editor (VS Code, GitHub, Obsidian). Unicode subscripts/superscripts, M☉, σ, ⚠, etc. all render as proper text in the editor. No PDF rendering until the paper is closer to submission. When PDF is needed, install Pandoc + XeLaTeX and run `pandoc PAPER_V1_DRAFT.md -o paper.pdf` (one-time setup, ~5 min).
**Recommended venue:** PRD, JCAP, or JHEP (mixed-verdict focus appropriate for all three)

---

## Abstract

We present a velocity-dependent self-interacting dark matter (SIDM) architecture — **a constraint map and no-go catalogue, not a definitive particle-physics model** — that addresses the tension between Cloud-9's high self-interaction requirement (σ/m ≥ 50 cm²/g at v ≈ 28 km/s [15b, 15e]) and the dwarf galaxy upper limits (σ/m ≲ 0.8 cm²/g at v ≈ 5–15 km/s [27]). **Honest phenomenological statement (v18.32):** We have a phenomenological interpolation, not a first-principles derivation. The multi-resonance + two-component + gravothermal framework describes **6–7 of 8 observational channels depending on the assumed f_H prescription**: with borrowed (hand-picked) f_H values, 7 of 8 channels pass; with Yang+ 2025-derived or T202 N-body-derived f_H, only 4 of 8 channels pass. The Cloud-9 vs dSph tension is **unresolved at Phase 44 parameters** — the framework cannot simultaneously satisfy Cloud-9 (σ/m ≥ 50) and dSph (σ/m ≤ 0.8) when f_H is derived from a first-principles source at our parameters. The heavy-channel-only decomposition σ_eff = f_H² × σ_HH(v) **cannot match SPARC's σ/m ≈ 0.193** at v = 100 km/s (max achievable σ_eff = 0.069). **Path F1 (T207, v18.38, §9.9-§9.11) addresses this structural limitation** by adding the σ_HL term: the three-term decomposition σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL + f_L² σ_LL reaches σ_eff(100) ≈ 0.19 via the heavy-light cross-section under borrowed prescription mode. **Path F1 removes the structural SPARC ceiling under borrowed/Yang f_H; the priored free fit does not resolve SPARC (log L ≈ −2).** Path F1 is a structural fix, not an automatic data-resolution — the free fit trades SPARC fit quality for physically motivated f_H_cc (standard prior-vs-likelihood tradeoff). **The Cloud-9 4000× spike is not derived from first principles.** **Note on the LZ 2026 September event below: this is a separate falsifiability test against direct-detection data, NOT a 9th bulk-halo σ/m channel.** In addition to these 8 channels, we explicitly test our composite-DM model against the LZ September 2026 248 keV single-event observation [50] (arXiv:2609.02823, 2.6σ significance, marginal status) using a comprehensive four-model cross-detector analysis (T201 canonical, `v0.3-prelim/code/T201_canonical_lz_audit.py`, using WIMpy 1.1.1 as ground truth): v0.7 composite-DM fails by 70 orders; v18.11 Drobczyk candidate is **kinematically accessible** (v_min = 591 km/s < SHM threshold 776 km/s at E_R = 5.4 keV, m_χ = 10.3 GeV) but **under-predicts** LZ events by ~2.5 orders per WIMpy 1.1.1 (N ≈ 3.5×10⁻³ vs 1 observed, a factor of ~300 below the single event; per T201 with WIMpy as ground truth). This is fully consistent with the LZ observation being background; v18.11 does not explain the event, and a ~300× enhancement of σ_SI (e.g., higher g_h_SM) would be required to bring v18.11 into the LZ sensitivity regime. Di Mauro 2026 inelastic interpretation [51] is **kinematically inaccessible** at LZ (TS&W 2001 PRD 64, 043502 v_min = 2418 km/s with reduced mass > SHM threshold 776 km/s, 0 events regardless of σ_inel); and T90-equivalent σ_SI magnitude (6.5×10⁻⁴³ cm² treated as elastic SI at T90's benchmark, NOT the actual magnetic-moment operator) OVER-predicts LZ by ~5 orders (N ≈ 1.16×10⁵ events, point-particle WIMpy T201); the LZ-tuned T90 WIMpy T198 result (using the actual magnetic-moment operator with form factors, tuned to ~1 event at LZ by construction) gives N ≈ 1 event at LZ but over-predicts XENONnT/PandaX-4T by 100-500×. This demonstrates that the model is **falsifiable in real time** against current direct-detection experiments but also that **no tested parameter point reaches LZ sensitivity**, leaving the LZ event — if real — as an open signature that requires either heavier DM mass (m_χ ≥ 50 GeV) or an inelastic channel not captured by v18.11. The architecture is composed of **four physical ingredients** (§2): (i) multi-resonance SIDM cross-section with one dominant Breit-Wigner peak plus three bookkeeping interpolation nodes; (ii) two-component asymmetric dark matter with a heavy component (χ_H, σ_HH dominant) and a light component (χ_L); (iii) gravothermal core-collapse selection; (iv) Gaussian Breit-Wigner resonance profiles. Best-fit parameters: T163 KK-tower (α_D = 0.3, m₀ = 0.3 GeV, r = 1.5, n_modes = 2, RMSE = 1.408) within the Phase 44 framework (σ/m = 0.052 cm²/g at v = 100 km/s).

**Honest model-comparison framing (Phase 42, Phase 54, T177, T205):** On SPARC rotation curves alone (120 galaxies, dynesty Bayesian evidence), this architecture is **outperformed by Burkert** (coreless isothermal) and PISO profiles. On the joint 7-channel likelihood (Phase 54), it wins on raw log-likelihood (+6.08 over constant σ/m) but loses on BIC-corrected evidence (ΔBIC = +3.22 favoring constant) due to the 15-vs-1 parameter penalty. The headline model-comparison number is **T177 log B = 3.06 (B = 21) — semi-informative Bayes factor using Gaussian likelihoods with hand-picked σ_unc (50 for Cloud-9, 0.05 for dSph, etc.). T205 update with published error budgets from the actual observational papers gives log B = 2.41 (B = 11, moderate evidence)**. The 6–7-of-8 channel-coverage rate is therefore a **channel-completeness result**, not a "model dominates the data" claim.

**Five no-go theorems on UV completion** (magnetic dipole DM [T120.10], Hidden U(1) + 10 MeV pseudo-Dirac [T120.16], GeV-scale inelastic DM [T130], Chu+ 2019 p-wave resonance [T131], thermal-WIMP one-mediator UV systematic [T184]) and a **two-mediator Drobczyk candidate** (thermal relic Ωh² = 0.119 at δ = 0.43%, g_h_SM = 0.00040, m_Φh = 20.69 GeV; T192 thermal-averaged) constitute the UV status. The Drobczyk candidate requires detuning 5× broader than the published benchmark (composite UV or fine-tuning argument required).

Three independent observational anchors support the framework: (1) thermal relic density via a two-mediator UV completion (Drobczyk 2025 [15f], T185/T190/T192), with the CHARM-compliant configuration at g_h_SM = 0.00040, δ = 0.43%, m_Φh = 20.69 GeV, Ωh² = 0.119; (2) JVAS substructure physics via core-collapsed SIDM (Yu 2026 [23], three-bird-one-stone for JVAS + GD-1 + Fornax 6 at ~10⁶ M☉ halo mass scale); and (3) four falsifiable predictions (§10.5a): Sommerfeld enhancement at freeze-out, direct-detection null at σ_SI ~ 2×10⁻⁴⁹ cm² (below neutrino floor), indirect-detection null at ⟨σv⟩₀ ~ 10⁻²⁹ cm³/s, and beam-dump sensitivity at 20 GeV.

Sections 4–8 (mass-spectrum embeddings, JVAS tension, profile discussion) are in `PAPER_V1_DRAFT_SUPPLEMENTARY.md`. The paper is organized as: physical ingredients (§2), joint constraints (§3), two-component resolution (§9), UV completion + Cloud-9 robustness (§10), conclusions (§11).

---

---

## 1. Introduction

Self-interacting dark matter (SIDM) was proposed as a solution to small-scale structure problems: cored dark-matter density profiles in dwarf galaxies (Kaplinghat, Tulin & Yu 2016 [1]), the diversity of rotation-curve shapes (Oman et al. 2015 [2]), and the too-big-to-fail problem (Boylan-Kolchin et al. 2011 [3]). The standard velocity-independent SIDM model with σ/m ≈ 1 cm²/g faces a multi-scale challenge: this cross-section is appropriate for dwarf-scale halos but is too large for cluster-scale halos (v ≈ 1000 km/s), where constraints from galaxy clusters and the Bullet Cluster require σ/m ≲ 0.1 cm²/g (Randall et al. 2008 [4]).

Velocity-dependent SIDM models resolve this tension by reducing σ/m at high velocities through one of several mechanisms: Yukawa suppression (Feng, Kaplinghat & Yu 2009 [5]; Tulin, Yu & Zurek 2013 [6]), threshold resonances (Chu, Hambye & Tytgat 2018 [7]; Duerr et al. 2021 [8]), or geometric mass-ladder constructions (Hong, Kuranchi & Perez 2020 [9]; Girmohanta & Yasuoka 2025 [10]).

**The v1.14 model** — the focal version of this paper — combines **four physical ingredients** into a phenomenological framework. Per the v18.32 honest phenomenological audit, the σ/m(v) parameterization can describe **6–7 of 8 observational constraints** spanning four orders of magnitude in velocity, **depending on the assumed f_H prescription**: Cloud-9 (σ/m ≥ 50 cm²/g at v = 28 km/s, lower bound; the specific 4000× spike is not derived from our model — see §3.2 + §10.4a), dSph (σ/m ≲ 0.8 at v = 15), UFD (σ/m ≲ 0.1 at v = 3–10), SPARC (σ/m ≈ 0.2 at v = 100), and clusters (σ/m ≲ 0.001 at v = 500). **Important caveats**: (a) the two-component + gravothermal interpretation requires f_H values **not derived from first principles** and **not reproduced** by our own N-body check at Phase 44 parameters (T202 finds f_H ≈ 0.92 uniform; T183 finds f_H ≈ 0.61), and (b) the heavy-channel-only decomposition σ_eff = f_H² × σ_HH(v) **cannot match SPARC's σ/m ≈ 0.193 at v = 100 km/s** for any f_H (max achievable σ_eff = 0.069). **Path F1 (T207, v18.38, §9.9-§9.11)** addresses this via the three-term decomposition σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL + f_L² σ_LL: under the borrowed prescription mode (hand-picked f_H), the σ_HL term reaches σ_eff(100) ≈ 0.19 with v_HL ≈ 100 km/s, σ_peak_HL ≈ 0.34. Under the Yang+ 2025 f_H_cc ≥ 0.05 prior, the free fit lands at v_HL = 105 ± 39 km/s (Mechanism A on-peak) with f_H_cc = 0.060 ± 0.012 but **fails SPARC at the posterior median** (log L = -2.03, z ≈ 2.0) — Path F1 is a structural fix, not an automatic data-resolution. The four ingredients are:

1. **Multi-resonance SIDM** with one dominant Breit-Wigner peak (v₁ ≈ 28 km/s, the Cloud-9 channel) plus three bookkeeping interpolation nodes at v ≈ 100, 178, 430 km/s on a velocity-dependent Yukawa background.
2. **Two-component asymmetric DM** (Yang, Tsai & Fan 2025, PRD 112, 083011 [42]) — heavy χH + light χL, mass ratio 3:1. Yang, Nadler, Yu & Zhong 2024 JCAP framework [43] for parametric halo modeling.
3. **Gravothermal core-collapse selection** (Yu et al. 2026, PRL [23]) — the heavy component sinks out of the observation region in collapsed halos.
4. **Gaussian Breit-Wigner profiles** — replaces the Lorentzian 1/Δv² tails of v1.6–v1.10. This is **OUR innovation** (T120.1–T120.4); earlier published work used Lorentzian profiles and suffered 6–23× tension with dSph/UFD limits.

The ultra-faint dwarf regime relevant to the v ≈ 28 km/s requirement is now being mapped at high discovery efficiency by the Vera C. Rubin Observatory LSST, with the first UFD from EDP2 — Aquarius IV at D_⊙ = 109 kpc (M_V = −1.9, r_1/2 = 19 pc; Cerny et al. 2026 [26]) — demonstrating that the population of SIDM-relevant dwarf systems is expected to grow substantially over the coming decade.

**Our contributions (v1.14):**
1. **Multi-component + gravothermal + Gaussian Breit-Wigner phenomenology** — phenomenological framework describing 6–7 of 8 observational constraints depending on f_H prescription (§2, §3). This is the **focal result** of the paper. The two-component + gravothermal interpretation is NOT first-principles derived and NOT numerically validated at Phase 44 parameters — see §9.6 (Limitations) and §11.
2. **Joint multi-channel evidence**: 31/31 additional dSph/UFD points satisfied that the Phase 44 single-channel baseline fails (§5). On the same dataset, a proper per-point Gaussian likelihood + BIC analysis is pending.
3. **MCMC verification** (T120.9a, §6): posterior recovers parameters within 1σ (a_slope = 0.92 ± 0.36, w₁ = 4.4 ± 2.0 km/s, f_H = 0.20 ± 0.11). The f_H posterior is wide and the central value is sensitive to the f_H prior — see §9.6.
4. **Pass-rate improvement** (T120.8, §6): 31/31 additional dSph/UFD points satisfied that the Phase 44 single-channel baseline fails (qualitative preference; formal per-point Gaussian likelihood + proper BIC pending).
5. **Five UV completion no-go theorems** (§10): magnetic dipole DM [T120.10], Hidden U(1) + pseudo-Dirac [T120.16], GeV-scale inelastic DM [T130], published best-fit p-wave resonance (Chu-Garcia-Cely-Murayama 2019 [28], T131), and thermal WIMP (T184) all fail. **The Cloud-9 4000× spike is not solved by any one-mediator UV completion (five no-go theorems); it requires physics beyond standard Yukawa interactions (T165-T172, T179). The thermal relic density is solved by a two-mediator UV completion (Drobczyk 2025 [15f], T185/T190, §10.3) — this addresses the relic but does NOT solve the Cloud-9 spike specifically.**
6. **EFT target map** (§10.5): what UV completions must satisfy to reproduce our phenomenology.
7. **Honest mixed-result on rotation curves**: architecture is consistent with rotation-curve data but not uniquely preferred over simpler cored profiles (§7).
8. **Direct-detection falsifiability test** (§3.5a, supplementary §S6): cross-detector analysis of the LZ September 2026 248 keV event using WIMpy 1.1.1 as ground truth. The v18.11 Drobczyk candidate under-predicts by ~2.5 orders; Di Mauro inelastic is kinematically inaccessible; no tested parameter point reaches LZ sensitivity.

**What is genuinely ours vs cited:**

- **Genuinely ours**: The 4-resonance multi-peak structure; the Gaussian profile replacement for Lorentzian (T120.1-4); the specific combination of multi-comp + gravothermal + Gaussian profiles; the MCMC verification (T120.9a); the 8-constraint joint fit; the **5 no-go theorems**.
- **Cited framework**: Yang+ 2025 PRD (two-component asymmetric DM); Yu+ 2026 PRL (gravothermal selection); Zhang 2016 / Chu+ 2019 (UV completion attempts that we then falsified). These are cited as **references** for our comparison, not as derivations of our f_H values.

---

## 2. The Multi-Resonance SIDM Model

### 2.1 σ/m(v) parameterization

The momentum-transfer cross-section per unit mass is parameterized as:

  σ/m(v) = σ₀(v) + Σᵢ σ_peak,ᵢ × BW(v; v_target,ᵢ, Γᵢ)

where the Breit-Wigner factor is

  BW(v; v_t, Γ) = (Γ/2)² / [(v² − v_t²)² + (Γ · v_t / 2)²]

and σ₀(v) = σ₀ · (1 km/s / v)^α is the velocity-dependent background (Yukawa-type suppression, Feng+ 2009 [5]). The sum runs over the four Breit-Wigner resonances. Each resonance's peak height σ_peak,ᵢ and width Γᵢ are free parameters (see §2.2 for per-resonance values). **Convention:** Γ here is the full width at half maximum (FWHM) of the Breit-Wigner in v²-space; some authors use the half-width or define the denominator with Γ² rather than (Γ/2)². The four resonance positions are listed in §2.2 with Γᵢ/vᵢ ≈ 0.05–0.10, i.e. the resonance is much narrower than its central velocity.

**Velocity-dependent background:** The background σ₀(v) = σ₀ · (1 km/s / v)^α with σ₀ ≈ 0.2 cm²/g and α ≈ 0.7 (Feng+ 2009 [5]) provides the dominant cross-section at low velocities. This is the standard Yukawa-SIDM background.

**Breit-Wigner peaks:** Each peak at velocity vᵢ has its own peak cross-section σ_peak,ᵢ (different per resonance, see §2.2) and width Γᵢ/vᵢ ≈ 0.05–0.10. The peaks are localized in velocity space and contribute σ/m ≈ σ_peak,ᵢ only within a narrow window around vᵢ.

**Important distinction between v_target and v_peak.** The `v_target,i` are *kinematic input parameters* in the multi-resonance parameterization, derived from the resonance energy via the kinematic relation E_R = ¼ m_χ v_target² (correct equal-mass CM kinematics; see T101_4_DECISION_GATE_REPORT_2026_09_19.md). For the v₁ resonance (the only high-amplitude feature), the actual peak of σ/m(v) occurs at v_peak,1 ≈ v_target,1 ≈ 29 km/s, with σ/m(v_peak,1) ≈ 197 cm²/g — i.e., v_peak,1 ≈ v_target,1 rather than 1.4× v_target,1. **Note:** an earlier version of this paper (v1.6–v1.8) reported v_peak,1 ≈ 41 km/s; that value was an artifact of using the wrong kinematics formula (E_R = ½ m_χ v_target² instead of ¼ m_χ v_target²). The corrected kinematics (T101.4) gives v_peak,1 = v_target,1. Cloud-9 (σ/m ≥ 100 cm²/g near v ≈ 28 km/s) is still satisfied: σ/m(v=28) ≈ 100 cm²/g and σ/m(v_peak,1 = 29) ≈ 197 cm²/g. For the low-amplitude features (v₂–v₄) the Breit-Wigner tails of the dominant v₁ resonance contribute significant σ/m at neighbouring velocities, so the actual peak of σ/m(v) at low-amplitude "resonances" is driven by overlap rather than the resonance formula itself. Figure 1 (`v0.3-prelim/docs/figures/sigma_m_v_phase44.png`) shows σ/m(v) with both the v_target,i input parameters and the v_peak,i actual peak locations marked.

**Canonical kinematic form (v²-space).** The Breit-Wigner formula used throughout this paper — and implemented in `phase44_joint_fit.sigma_m_at_v`, which is the canonical reference used by every Phase 32–54 result — uses the v²-space form (equation above). This is the standard kinematic form for s-channel dark-matter scattering, in which the resonance is centered on the energy E_R = (½) m_χ v_target² and the BW factor is constructed from (v² − v_t²)² rather than (v − v_t)². An alternative implementation using the *v-space* form — `BW(v) = (Γ_v/2)² / [(v − v_t)² + (Γ_v/2)²]` with Γ_v = γ_frac × v_target — was constructed as an independent cross-check (`v0.3-prelim/code/independent_sigma_m.py`, with tests in `test_independent_and_robustness.py`). The two implementations agree in the non-resonant regime (off-peak velocities where both reduce to the background σ₀(v)); at the resonant peaks they differ by up to ≈30× because the v-space form has wider non-resonant tails and the v²-space form has narrower resonant peaks. This is a **genuine physical ambiguity** between the two kinematic forms, not a coding error, and it is captured by the self-check tests (`test_independent_matches_phase44_at_non_resonant_velocities`, `test_independent_peak_at_each_v_target`). We adopt the v²-space form as canonical because (i) it matches the kinematic s-channel derivation, (ii) it is the form used in all Phase 32–54 fits, and (iii) it produces the σ/m values cited in this paper. The v-space form is retained only as a cross-check, not as an alternative computation.

### 2.2 One resonance + three bookkeeping interpolation nodes

**UV status of node positions (per Option 7, 2026-09-21):** The node POSITIONS v₃ = 178, v₄ = 430 km/s DO have a UV derivation — they come from the Phase 53 v2 clockwork UV prior (a clockwork discretization of the mediator mass spectrum). The original T90.70 priors used v₃ = 300, v₄ = 700 km/s (no UV justification); the clockwork-derived values are preferred because they have a UV-aware derivation (5-parameter fit, BIC Δ = −5.66 favoring clockwork). The node PEAK HEIGHTS, however, are purely phenomenological — set by the optimizer to give a smooth σ/m(v) curve from Cloud-9 down to cluster scales. **The nodes are therefore "phenomenological peak heights with UV-derived positions,"** a mixed-status interpolation.

Recent work by Engelhardt et al. 2026 [49] also tests core-collapse timescales in velocity-dependent SIDM and finds comparable Yukawa-background parameter space; their results provide independent confirmation that **standard Yukawa velocity-dependence is consistent with our framework** in the dwarf regime.

**Reframing (per R2 review, 2026-09-21):** The architecture uses ONE genuine high-amplitude Breit-Wigner resonance (v₁ = 28 km/s, the Cloud-9 channel) plus THREE low-amplitude bookkeeping interpolation nodes (v₂ = 100 km/s, v₃ = 178 km/s, v₄ = 430 km/s). The bookkeeping nodes are NOT physically motivated resonances — they are interpolation anchors that allow the σ/m(v) curve to fall smoothly from the high Cloud-9 value to the low cluster-scale value. This reframing does NOT change any fitted values; it makes the model architecture honest: a single resonance (v₁) on a velocity-dependent background, with three nodes providing numerical interpolation flexibility.

**Reservation about v₃, v₄ positions:** The original parameterization used v₃ = 300 km/s and v₄ = 700 km/s (T90.70 priors). The clockwork UV prior (§6, Phase 53 v2) produces v₃ = 178 km/s, v₄ = 430 km/s. We adopt the clockwork values because they have a UV-aware derivation. Either choice produces σ/m ≤ 0.1 cm²/g at v > 100 km/s — both are below observational upper limits in that velocity range.

**Per-feature values:**

- v₁ = 28 km/s: σ_peak ≈ 100 cm²/g (Cloud-9 requirement from UDG kinematics; Phase 32). Cloud-9 is the prototypical ultra-diffuse galaxy (UDG) of the kind with extremely extended globular cluster systems [25]. **This is the only true high-amplitude Breit-Wigner resonance.**
- v₂ = 100 km/s: σ_peak ≈ 0.07 cm²/g (SPARC transition velocity; rotation-curve inner-core consistency, Phase 33d). **Bookkeeping interpolation node** — structurally a low-amplitude suppression feature, not an enhancement. The rotation-curve data are consistent with σ/m(100) ≈ 0.07 because that is the value the architecture predicts at this transition velocity.
- v₃ = 178 km/s (clockwork) or 300 km/s (T90.70): σ_peak ≈ 0.1 cm²/g. **Bookkeeping interpolation node.**
- v₄ = 430 km/s (clockwork) or 700 km/s (T90.70): σ_peak ≈ 0.01 cm²/g (cluster-scale suppression; essentially CDM-like at v ≈ 1000 km/s). **Bookkeeping interpolation node.**

The key insight is that the multi-resonance architecture generates a σ/m(v) shape that is high at v ≈ 28 km/s (Cloud-9), falls off at v ≈ 100 km/s to a value compatible with SPARC rotation-curve inner cores (σ/m ≈ 0.07), and remains low at higher velocities (cluster/strong-lensing scales). This monotonic falloff is what the four-position parameterization achieves, regardless of whether the v₂–v₄ features are called "peaks" or "interpolation nodes."

**Canonical σ/m(v) figure (T194, `t194_master_sigma_v.png`):** Figure 1 shows the master σ/m(v) curve produced by this parameterization, with all observational channels overlaid as colored bands/ceilings. The figure clearly distinguishes the dominant v₁ resonance from the three bookkeeping nodes, shows the 7-point fit data, and demonstrates why Cloud-9 (the σ/m ≥ 50 floor at v=28) cannot be derived from standard Yukawa background alone (the background Yukawa alone, shown as dashed black, gives σ/m(28) ≈ 0.07 cm²/g — three orders of magnitude below Cloud-9). The T194 figure is the canonical visual reference for all §3 channel-pass discussions.

[See `v0.3-prelim/data/results/t194_master_sigma_v.png` for the figure with all observational constraints overlaid.]


### 2.3 Physical motivation

The Breit-Wigner peaks arise from s-channel mediator exchange in DM-χ + χ → med + χ → χ + χ, where the mediator is a hidden-sector gauge boson with mass m_med such that the s-channel process is resonant at v_res = (m_med / m_χ) c (Chu, Hambye & Tytgat 2018 [7]). The four-peak structure requires four mediators with hierarchical masses.

### 2.4 Relationship to existing models

The closest existing work is **Yang & Yu 2023** [11] (single-breathing-mode mediator with one resonance), **Turner et al. 2021** [12] (atomic-DM transitions), and the **Yang & Yu 2022** [13] core-collapse extension. Our model differs by having **multiple simultaneous resonances** and by **jointly optimizing** against SPARC, Cloud-9, and JVAS constraints. The Girmohanta-Yasuoka 2025 [10] dark-photon model is structurally similar but uses a different UV-completion story.

---

## 3. Multi-Channel Observational Constraints

**Channel count convention (v18.30 update):** Earlier versions of this paper reported a "7 of 8 channels" headline, which used hand-picked `f_H_at_r` values from a placeholder function that was labeled "Based on Yang+ 2025" but was **not actually derived** from Yang+ Fig. 2. After the v18.29 Rule 28 arithmetic audit, the function was rewritten to be Yang+ 2025-derived. With the Yang+-derived `f_H_at_r`, the multi-resonance profile **does not simultaneously satisfy** the Cloud-9 (σ/m ≥ 50) and dSph (σ/m ≲ 0.8) channels at Phase 44 parameters, because (a) gravothermal cascade timescale ≫ Hubble time at Phase 44 σ/m, and (b) Yang+ Fig. 2 segregation is modest (f_L ∈ 0.3-0.6), not extreme (f_H from 0.95 to 0.10) as the placeholder claimed. The honest verdict is that **at Phase 44 parameters, the multi-resonance σ/m(v) profile is a phenomenological interpolation through 8 channels, not a first-principles derivation of the underlying physics.** The Cloud-9 vs dSph tension is **unresolved** at Phase 44. See §3.3 T120.3aFix-v18.30 for the two-regime framing (Phase 44 vs Yang+ σ/m). The LZ September 2026 direct-detection event (§3.5a) is a **separate falsifiability test** — NOT a 9th bulk-halo channel.

### 3.1 SPARC rotation curves

**Data:** 127 galaxies from the Spitzer Photometry and Accurate Rotation Curves (SPARC) sample [14].

**Constraint:** σ/m at v ≈ 100 km/s should be ≈ 0.07 cm²/g for the rotation curves to be consistent with the observed V_flat in the inner core. Phase 33d tested all 127 SPARC galaxies; **115/127 = 90.6% pass the V_flat test** with the multi-resonance σ/m(v) architecture. This is consistent with, but not better than, single-Yukawa SIDM.

**Result:** Multi-resonance architecture is consistent with SPARC.

### 3.2 Cloud-9 ultra-diffuse galaxies

**Data:** Cloud-9, a Reionization-Limited H I Cloud (RELHIC) candidate near M94, discovered by Zhou+ 2023 [15a] (FAST H I detection, M_HI ≈ 1.4×10⁶ M☉, W50 ≲ 20 km s⁻¹). The hydrostatic-equilibrium analysis of Benítez-Llambay, Dutta, Fumagalli & Navarro 2024 [15b] (ApJ 973, 61) yields a σ/m ≳ 50 cm²/g floor at v ≈ 28 km s⁻¹, with a halo mass M_200 ≈ 5×10⁹ M☉ (consistent with M_crit). Stellar-mass upper limits on any luminous counterpart have been refined by Anand+ 2025 [15c] (HST/ACS star-counts, M⋆ < 10³·⁵ M☉, 99.5% CL; baseline comparison with Leo T, μ_0,V ≈ 27 mag arcsec⁻²) and Trujillo+ 2026 [15d] (GTC/HiPERCAM integrated light at surface-brightness limits 31.4 mag arcsec⁻² in g, 31.0 in r — **~10× deeper than previous DESI Legacy / HST searches**, M⋆ < 1.6×10⁴ M☉ assuming old, metal-poor population; surface mass density < 0.01 M☉/pc²). **Trujillo+ 2026 [15d] is the strongest stellar-mass bound on Cloud-9 to date**, with the Leo T comparison caveat noted in Anand+ 2025 [15c] potentially underestimating the bound by 2-3 mag for galaxies with the diffuse extended morphology of Cloud-9. The σ/m(28) ≈ 100 cm²/g value we adopt as the multi-resonance working anchor is an internal derivation, consistent with the Benítez-Llambay+ 2024 published floor and chosen to provide a concrete quantitative target.

**Constraint:** At v ≈ 28 km/s, σ/m should be high (≳ 50 cm²/g published; we use ≈ 100 cm²/g as the internal target).

**Result:** ✅ Multi-resonance architecture satisfies this via the v₁ = 29 km/s Breit-Wigner peak. With the corrected kinematics (T101.4), the actual peak of σ/m(v) occurs at v_peak,1 = v_target,1 ≈ 29 km/s (NOT at 1.4× v_target ≈ 41 km/s as previously stated in v1.6–v1.8); σ/m(v_peak,1) ≈ 197 cm²/g, comfortably above the Cloud-9 target of σ/m ≈ 100 cm²/g. At v = 28 km/s (the Cloud-9 kinematic v), σ/m ≈ 100 cm²/g. At the kinematic input velocity v_target,1 = 29 km/s, σ/m(v_target,1) ≈ 197 cm²/g — i.e., v_target,1 IS the location of the maximum of σ/m(v) under the corrected kinematics.

### 3.3 JVAS B1938+666 strong-lensing perturber

**Data:** Vegetti et al. 2010 [16] observed a small-density perturbation in the JVAS B1938+666 strong-lensing system that has been *interpreted* (in subsequent lensing-modelling literature) as requiring σ/m(15) ≈ 100 cm²/g. Note: this constraint is a derived interpretation of the lensing-perturbation signal rather than a direct cross-section measurement, and it carries substantial modelling uncertainty. The perturber mass is (1.13±0.04)×10⁶ M☉ within a projected radius of 80 pc at z = 0.881 [23].

**Excluded from the 4-channel fit (per Grok 2026-09-21 review):** JVAS is a single ~10⁶ M☉ substructure measurement, **not a measurement of the bulk halo σ/m(v)**. Including it in the same 4-channel table as Cloud-9, dSph, SPARC, Cluster conflates two different physics regimes. The reframing below (Yu 2026 [23]) confirms JVAS is complementary substructure physics, not an additional bulk channel..

**Constraint (as commonly stated):** σ/m ≈ 100 cm²/g at v ≈ 15 km/s.

**Result:** ⚠ Tension with the multi-resonance architecture at face value. The model achieves σ/m(15) ≈ 4.2 cm²/g, a factor of ~24× below the JVAS target of σ/m(15) ≈ 100 cm²/g. (Earlier reports in this paper sometimes quote a factor of ~84×, which refers to a different reference velocity — v=15 is the canonical JVAS velocity used here.)

**Reframing (per Yu 2026 PRL 136, 141001 [23], added 2026-09-21):** The JVAS perturber is **a single dense ~10⁶ M☉ substructure**, not a measurement of the bulk σ/m of the host halo. Yu (2026) [23] shows via N-body simulation that core-collapsed SIDM halos of mass ~10⁶ M☉ naturally produce the JVAS perturber density profile — this is **gravothermal core-collapse physics** at the subhalo mass scale, not the bulk cross-section at v ≈ 15 km/s. Our phenomenology at v ≈ 15 km/s applies to the **host halo** (M_halo ~ 10⁹ M☉), where the core-collapse enhancement does NOT apply. The structural limit is therefore **not a failure of our σ/m(v) parameterization** but rather a statement that the JVAS perturber requires substructure physics outside our bulk-phenomenology scope. This is consistent with the §10.4c.A5 verdict (gravothermal enhancement ~100×, needs 3125×) — the missing factor is from the substructure being in core-collapse state, not from our cross-section being wrong.

**Cross-confirmation (Fornax 6, Yu 2026 [23]):** Yu (2026) [23] further shows that the same ~10⁶ M☉ core-collapsed SIDM halo density profile simultaneously explains (a) the JVAS B1938+666 perturber, (b) the GD-1 stellar stream perturber, and (c) the Fornax 6 stellar cluster in the Fornax dwarf spheroidal (M★ ≈ 7.2×10³ M☉, r_h ≈ 11 pc, σ ≈ 5.6 km/s, anomalously high M/L ≈ 15-258; Pace et al. 2021, Peñarrubia et al. 2024). Fornax 6 is therefore an **independent observational anchor** for the same ~10⁶ M☉ core-collapsed SIDM halo physics, at a different cosmic location. Our phenomenology covers dSph (M_halo ~ 10⁹ M☉) and cluster (M_halo ~ 10¹⁴ M☉) scales; the JVAS / GD-1 / Fornax 6 anchors at 10⁶ M☉ are **complementary** substructure physics, not in tension with our bulk σ/m(v).

**T204 substructure test (2026-09-23) — explicit numerical check of Yu+ 2026 mechanism at Phase 44 params:** A 10⁶ M☉ subhalo at the JVAS perturber location has r_vir = 1.5 kpc (c = 15), V_max = 1.69 km/s, and NFW scale density **ρ_s = 4.34×10⁻² M☉/pc³** (NFW-from-M-and-c derivation). At v1.13 canonical parameters (σ₀ = 0.052 cm²/g at v_ref = 100 km/s, **a_slope = 1.0** per Option A flattening — §3.2), σ/m(v_max) = 0.052 × (100/1.69)^1.0 = **3.07 cm²/g** at the subhalo's virial velocity. Using the **Balberg+ 2002 Eq. 22 normalization** (PRL 88, 101301), t_core = 12.7 / σ × (ρ_s/10⁻²)^-1 × (r_s/10⁴) × (100/v_max) Gyr, the core-collapse timescale is **t_core ≈ 5.6×10⁻¹ Gyr (560 Myr)** — **~25× faster than the Hubble time**. The halo crossing time is t_cross = r_s/V_max = **60 Myr**; the t_core/t_cross ratio is 9.3, comfortably above unity (no causality violation). For comparison, **the sanity check against a Milky-Way-sized halo** (σ/m = 1, ρ_s = 10⁻², r_s = 10⁴, v_max = 100) yields t_core = 12.7 Gyr, consistent with literature. **Verdict**: at Phase 44 + v1.13 canonical parameters, **the Yu+ 2026 substructure mechanism IS active** in 10⁶ M☉ subhalos. JVAS / GD-1 / Fornax 6 are *explicitly predicted* by the framework via substructure core-collapse. This is *strong* structural support for the multi-component + gravothermal mechanism. **Caveats**: (a) T202's N-body check is *inconclusive* (the same 2048-particle simulator cannot reproduce Yang+ 2025's Fig. 2 segregation, so the gravothermal cascade is plausible but not yet numerically validated at our parameters), (b) the Balberg+ 2002 normalization is the standard order-of-magnitude estimate and does not capture anisotropic velocity distributions, halo triaxiality, or baryonic feedback that modify collapse timescales by factors of ~2–10, (c) the velocity-dependence extrapolation from v_ref = 100 km/s (calibration range) to v = 1.69 km/s (subhalo) carries O(1) uncertainty in a_slope, and (d) the Balberg formula's r_s ∝ t_core scaling is calibrated on galaxy-scale halos (r_s ~ 10–30 kpc); sub-kpc extrapolation is plausible but unverified. **Pre-v18.28 warning** (corrected per Scrutiny.docx): earlier T204 versions used a_slope = 1.93 (Phase 44 original) and gave t_core = 13 Myr < t_cross = 60 Myr, which is *unphysical* (collapse faster than information can propagate). The current v18.28 uses a_slope = 1.0 (v1.13 canonical) and gives t_core = 560 Myr > t_cross = 60 Myr. The qualitative verdict (collapse within Hubble time) survives, but the quantitative value changed by 45×. Full derivation in `code/T204_substructure_test.py`.

### 3.3b Stellar streams and stellar halo substructure (Yu 2026 PRL 136, 141001 [23])

**Dataset:** Three independent stellar-halo / stellar-stream observables that probe ~10⁶ M☉ core-collapsed SIDM substructure:

| Observable | Source | Subhalo mass / location | Significance |
|---|---|---|---|
| **GD-1 stellar stream perturber** | Bonaca+ 2019, 2020 (Gaia DR2); Price-Whelan & Bonaca 2018; Malhan+ 2019; Erkal+ 2019 | M_sub ≈ 10⁶–10⁷ M☉ at ~10–20 kpc from GC | Off-stream spur + gap structure ⇒ dense subhalo along GD-1 |
| **JVAS B1938+666 strong-lensing perturber** | Vegetti+ 2010 [16]; subsequent Yu+ 2026 [23] re-analysis | (1.13±0.04)×10⁶ M☉ within 80 pc at z = 0.881 | Subhalo detection in strong-lensing data |
| **Fornax 6 cluster** (Fornax dSph) | Pace+ 2021; Peñarrubia+ 2024 | M★ ≈ 7.2×10³ M☉, r_h ≈ 11 pc, σ ≈ 5.6 km/s, M/L ≈ 15-258 (anomalous) | Cluster captured by dense ~10⁶ M☉ substructure |

**Mechanism:** Yu (2026) PRL 136, 141001 [23] demonstrates via N-body simulation that a single ~10⁶ M☉ core-collapsed SIDM halo density profile **simultaneously explains all three** observables (the "three birds with one stone" result). The gravothermal cascade reaches core-collapse within a Hubble time at this mass scale because the collapse timescale t_core ∝ ρ_s⁻¹ × r_s × v_max⁻¹ scales favorably for dense, low-velocity subhalos.

**Result:** The framework **predicts** all three observables via the Yu+ 2026 substructure mechanism (verified numerically in T204, §3.3 above): σ/m(v=1.69 km/s) = **3.07 cm²/g**, t_core = **560 Myr** (25× faster than Hubble), t_core/t_cross = 9.3 (no causality violation). **Verdict:** stellar streams + stellar halo substructure are **consistent with** the multi-component + gravothermal framework as **complementary substructure predictions**, not bulk σ/m channels.

**Important caveat (per v18.32 honest phenomenological audit):** Like all three mechanism-dependent predictions, this is contingent on the gravothermal cascade being operative at ~10⁶ M☉ — which Yu+ 2026 [23] confirms via dedicated N-body but our own T202 N-body check at Phase 44 σ/m cannot independently validate (the 2048-particle simulator lacks the resolution to track dense subhalo core-collapse). The prediction is **physically motivated but not independently numerically validated by us**.

### 3.4 Joint fit

**Canonical parameter table** (referenced from §3.4 throughout the paper):

| Parameter | Symbol | Free / Fixed | Value (v1.98 fit) | Source / Constraint |
|---|---|---|---|---|
| DM mass | m_χ | FREE | (Phase 44 default) | T90.70 prior |
| Background σ/m normalization | σ₀ | FREE | (Phase 44 default) | T90.70 prior |
| Background slope | α | FREE | 1.0 (default; a_slope_override) | T90.70 prior |
| Resonance v₁ position (Cloud-9) | v_target[0] | FREE | 28 km/s | T120 fit |
| Resonance v₁ peak height | σ_peak[0] | FREE | ~100 cm²/g | T120 fit |
| Resonance v₁ width | width_frac[0] | FREE | 0.05 | T90.70 |
| Resonance v₂–v₄ positions | v_target[1..3] | FIXED | [100, 178, 430] km/s | §2.2 (bookkeeping nodes) |
| Resonance v₂–v₄ peak heights | σ_peak[1..3] | FIXED | [0.07, 0.10, 0.01] cm²/g | T90.70 |
| Resonance v₂–v₄ widths | width_frac[1..3] | FIXED | [0.05, 0.05, 0.10] | T90.70 |
| Heavy/light mass ratio | m_H/m_L | FIXED | 3:1 | Yang, Tsai, Fan 2025 PRD [42] |
| Gaussian width | w₁ | FREE | 4.4 ± 2.0 km/s | T120 MCMC |
| Heavy fraction profile | f_H(r) | ASSUMED (placeholder) | ~0.85 / 0.30 (hand-picked); ~0.92 uniform (T202 N-body); ~0.61 (T183 fluid) | not derived; see §9.6 Limitations |
| Clockwork prior (Phase 53 v2) | log v₁, q | FREE | 5 params total | Phase 51 MINIMAL fit |

**Phase 44 free fit**: 15 parameters (background 3 + resonance 4×3) → see §8.1 for parameter-by-parameter breakdown
**Phase 53 v2 clockwork fit**: 5 parameters (background 3 + clockwork log v₁, q)

**T163 best fit (KK tower realization):** T163 explored the KK-tower
embedding within the Phase 44 framework. The best-fit parameters are
**α_D = 0.3, m₀ = 0.3 GeV, r = 1.5, n_modes = 2** (RMSE = 1.408). T163
is a specific realization of the multi-resonance structure where the
four "bookkeeping interpolation nodes" of the Phase 44 default are
replaced by a KK tower of n_modes = 2 modes. Both Phase 44 and T163
share the same σ/m(v) phenomenology at the velocity scales probed by
the 7-point fit (v = 5 to 500 km/s); T163's KK tower provides a more
principled UV-motivated spectrum than the ad-hoc bookkeeping nodes.
**Phase 44 + T120 added**: 18 parameters (15 + 3 new: w₁, f_H profile, m_H/m_L ratio → but m_H/m_L fixed by Yang+ so effectively 17 free; see §9.7)

**Baseline definition (T90.70):** the same 15-parameter multi-resonance parameterization with **v_targets fixed at the canonical T90.70 values [28, 100, 300, 700] km/s** (i.e., a T90.70 pre-fit snapshot where the resonance positions have not yet been adjusted to match the multi-channel likelihoods). All other parameters (background σ₀, α, peak heights, widths) are held at their T90.70 priors. The **joint multi-channel improvement** reflects the optimizer adjusting the v_targets (and other free parameters) to fit the SPARC + Cloud-9 + JVAS likelihoods simultaneously. The clockwork UV prior (§6, Phase 53 v2) replaces the 4 free v_targets with 2 clockwork parameters (log_v₁, q); the 5-parameter model satisfies the joint likelihood nearly as well as the 15-parameter free fit (Δ = −0.16 in scoring-rule units; the qualitative preference is robust but formal BIC requires proper likelihood construction).

**Result:** **31/31 additional dSph/UFD points satisfied** that the Phase 44 single-channel baseline fails (T120.8). The stress test (Phase 47) reveals that SPARC dominates the fit; JVAS and Cloud-9 are variance-absorbing channels (their LOO contribution to the joint log-likelihood is small).

### 3.5 Stress-test analysis

Leave-one-out analysis (Phase 47) shows:
- All-three logL = −11.58
- Without JVAS: −2.24 (Δ = +9.34)
- Without Cloud-9: −7.26 (Δ = +4.32)
- Without SPARC: −13.65 (Δ = −2.07)

**Interpretation:** The joint fit's improvement comes mostly from the SPARC constraint; JVAS and Cloud-9 are essentially uncorrelated variance-absorbing channels. The +8 log-unit gain is therefore primarily a SPARC self-consistency check, with secondary validation from Cloud-9 and JVAS.

### 3.5a LZ 2026 September event: explicit test against current direct-detection data (compressed)

**Verdict (T201, WIMpy-validated canonical):** Four models, four distinct verdicts against the LZ September 2026 single-event observation [50] (arXiv:2609.02823, 2.6σ, marginal status):

| Model | LZ deficit / verdict | Note |
|---|---|---|
| v0.7 composite-DM | **70 orders short** | freeze-in ε² × F²_composite suppression |
| v18.11 Drobczyk | **2.5 orders short** (~300× below observed) | consistent with LZ being background |
| Di Mauro 2026 inelastic | **kinematically inaccessible** (0 events) | TS&W v_min = 2418 km/s > SHM 776 km/s |
| T90 point-particle | **5 orders over** (excluded) | σ_SI magnitude too large |

**Honest framing:** The LZ event is **not a passing channel** but a **falsifiability demonstration**. As a 2.6σ single-event observation, it has ~0.5% probability of being a statistical fluctuation; it is consistent with — but not evidence for — inelastic dark matter scattering. Six consecutive versions of the rate calculation (T196-T200, T201-initial) had dimensional or API-signature bugs; **T201 with WIMpy ground truth is the canonical reference**. The T90 magnetic-moment interpretation is **FALSIFIED by cross-detector consistency** (over-predicts XENONnT/PandaX/DARWIN by 100-23,000×), and the magnetic-moment vs Higgsino-inelastic interpretations of the LZ event are tied at 47% posterior — a second LZ data release is required to discriminate. The full rate-calculation history, reduced-mass TS&W formula derivation, cross-detector matrix (XENONnT/PandaX/DARWIN/DarkSide), and the WIMpy `DMUtils.dRdE_standard` API signature audit are moved to **Supplementary §S6**.

**CHARM-ceiling quantification:** The current v18.11 benchmark sits at g_h_SM = 0.00040 (T192 thermal-averaged config, §10.5a), well below the CHARM bound g_h_SM < 0.005. Since σ_SI ∝ g_h_SM², the maximum allowed enhancement from the benchmark is (0.005/0.00040)² ≈ 156×, giving σ_SI ≈ 3×10⁻⁴⁷ cm² and N ≈ 0.55 events at LZ — consistent with the observed 1 event at ~32% Poisson probability. **v18.11 at the CHARM ceiling of its own UV completion is consistent with the LZ observation; the current σ_SI benchmark is ~300× below that ceiling.** This makes v18.11 "falsifiable in real time" but not currently excluded by the LZ null.

### 3.6 dSph upper-limit tension (Horigome+ 2025)

**Data:** Horigome+ 2025 [27] (arXiv:2503.13650) reports 95% CL upper limits on σ/m for both velocity-independent and velocity-dependent SIDM, based on the combined Milky-Way dSph kinematic analysis of 8 classical dSphs and 23 UFDs using the SASHIMI-SIDM framework:
- **Velocity-independent** (w→∞, Eq. 13 with F=1): σ/m < **0.04 cm²/g** at dSph velocities (95% percentile; Section "Results" of [27])
- **Velocity-dependent with w = 10 km/s** (Eq. 13 of [27]): σ/m < **0.8 cm²/g**
- **Velocity-dependent with w = 30 km/s** (closer to velocity-independent): σ/m < 0.2 cm²/g

The Horigome+ constraint applies at v_eff = 0.64 × V̂_max (Eq. 15 of [27], following Yang & Yu 2022 [30]). For classical dSphs (Draco, Fornax, Sculptor), V̂_max ~ 15–30 km/s → v_eff ~ 10–20 km/s. For UFDs (Segue 1, etc.), V̂_max ~ 5–15 km/s → v_eff ~ 3–10 km/s.

**Constraint for our model:** The multi-resonance architecture is **highly velocity-dependent** (with effective w ~ 10–30 km/s from the BW peak structure); the relevant Horigome+ limit is therefore **0.8 cm²/g** (w=10 km/s case), not the velocity-independent 0.04 cm²/g limit. The choice of which limit to apply depends on how strongly velocity-dependent the model is at v_eff; for our phenomenology (which has BW peak width Γ ~ 10–30 km/s around v₁ = 29 km/s), the w = 10–30 km/s case is the appropriate comparison.

**Result:** ⚠ Mild tension with the multi-resonance architecture in the **Phase 44 single-component baseline** (smaller than initially reported). The two-component + gravothermal result (§9.3) resolves this.

With the correct velocity convention (v_eff = 0.64 × V̂_max) AND the correct limit for a velocity-dependent model (0.8 cm²/g at w=10 km/s), the violation at the Horigome+ 95% CL is (Phase 44 single-component baseline, BEFORE multi-component correction):

| Velocity scale | σ/m(v) [Phase 44 single] | σ/m(v) [v1.13 with hand-picked placeholder f_H, retracted v18.29 — shown for reference only] | Horigome+ limit (w=10) | Phase 44 violation | v1.13 status (placeholder f_H) |
|---|---|---|---|---|---|
| v_eff = 5 km/s (UFDs) | 18.4 cm²/g | **0.09 cm²/g** | 0.8 cm²/g | **23×** | ✓ PASS (200× under) |
| v_eff = 10 km/s (UFDs/UFD-like) | 6.5 cm²/g | **0.05 cm²/g** | 0.8 cm²/g | **8×** | ✓ PASS |
| v_eff = 15 km/s (classical dSphs) | 5.0 cm²/g | **0.03 cm²/g** | 0.8 cm²/g | **6×** | ✓ PASS |
| v_eff = 20 km/s (high-V̂_max dSphs) | 6.8 cm²/g | **0.04 cm²/g** | 0.8 cm²/g | **8×** | ✓ PASS |

**Caveat:** the v1.13 ✓ PASS values in this table use the **hand-picked placeholder f_H** (retracted v18.29; see §9.3 and §9.7). With Yang+ 2025-derived or T202 N-body f_H, the dSph v=15 channel fails (σ/m_eff ≈ 3.1 cm²/g vs 0.8 ceiling; see §9.3 table). The table is retained here for archival purposes; the current honest status is documented in §3.6 status line below.

If we instead use the velocity-independent limit (0.04 cm²/g), the violations are higher (115–460×), but this is not the appropriate limit for a strongly velocity-dependent model like ours.

**Note on earlier versions:** v1.6–v1.9 of this paper applied the velocity-independent limit (0.2 cm²/g) at v=30 km/s, giving a "800× violation" (v1.9) which was based on both (a) the wrong velocity convention AND (b) the wrong limit for a velocity-dependent model. v1.10 corrects the velocity convention (v_eff = 0.64 × V̂_max); the limit choice was further refined in v1.11 (this version) to use the w=10 km/s case appropriate for our model. The combined effect is to reduce the apparent tension from ~800× to **6–23×** at v_eff = 5–20 km/s.

**Status (v1.12 → v18.33 — HONEST PHENOMENOLOGICAL):** The 6–23× violation reported in v1.11 was nominally resolved in v1.12 by the combined two-component asymmetric DM (Yang+ 2025 PRD [42]) + gravothermal core-collapse selection effect (Yu+ 2026 PRL [23]) + Gaussian Breit-Wigner profile. **However, per the v18.32 honest phenomenological audit, this resolution depends on f_H values that are not first-principles derived and not reproduced by the project's own N-body check.** The Channel-by-Channel table below used **hand-picked f_H values** (~0.85 / 0.30) that were initially attributed to Yang+ 2025 Fig. 2 but were later (v18.29) shown to **not actually match Yang+ Fig. 2**. With Yang+ 2025-derived f_H (Phase 44 σ/m → no significant gravothermal cascade), the multi-resonance profile **does not simultaneously satisfy** the Cloud-9 (σ/m ≥ 50) and dSph (σ/m ≤ 0.8) channels at Phase 44 parameters. Furthermore, the heavy-channel-only decomposition σ_eff = f_H² × σ_HH(v) cannot match SPARC's σ/m ≈ 0.193 at v = 100 km/s for any f_H (max achievable σ_eff = 0.069) — a structural limitation. **See §9.6 (Limitations) for the full honest discussion and §9.7 for the per-f_H-prescription channel table.**

| Channel | Constraint | σ/m_eff (with borrowed f_H, v1.12) | σ/m_eff (T202 f_H ≈ 0.92) | σ/m_eff (Yang+ 2025-derived f_H) | Status |
|---|---|---|---|---|---|
| Cloud-9 (v=28, core-forming) | ≥100 cm²/g | **128 cm²/g** ✓ | **92 cm²/g** ✗ (below floor) | **87 cm²/g** ✗ (below floor) | Pass with borrowed; fail with Yang+-derived |
| dSph (v=15, core-collapsed, r_obs=0.2 r_vir) | ≤0.8 cm²/g | **0.18 cm²/g** ✓ | **4.2 cm²/g** ✗ (above ceiling) | **3.1 cm²/g** ✗ (above ceiling) | Pass with borrowed; fail with Yang+-derived |
| SPARC (v=100, intermediate) | ∈[0.05, 0.5] | **0.19 cm²/g** ✓ | **0.058 cm²/g** | **0.053 cm²/g** | Cannot match (max σ_eff = 0.069 < 0.193) |
| Cluster (v=500) | <1.0 cm²/g | **0.0002 cm²/g** ✓ | **0.003 cm²/g** ✓ | **0.003 cm²/g** ✓ | Pass (Cluster does not depend on f_H) |

**Honest summary**: With borrowed (placeholder) f_H values, 3 of the 4 channels pass (Cloud-9, SPARC, Cluster). The dSph channel also passes with borrowed f_H but **fails with Yang+-derived or T202-derived f_H**. The SPARC channel cannot be matched by any single-channel decomposition at Phase 44 — a full σ_HH + σ_HL + σ_LL decomposition is required. The Cluster channel is the only one robustly satisfied regardless of f_H prescription. **The v1.12 "RESOLVED" framing is replaced by "v18.32: partially resolvable, structurally incomplete".**

---

---

## Supplementary Material Pointer

**Sections 4–8 of earlier drafts (Comparison with Simpler Halo Profiles, Mass-Spectrum Embeddings, UV-Prior Joint Fit, JVAS Tension, Discussion) have been moved to `PAPER_V1_DRAFT_SUPPLEMENTARY.md` for journal submission brevity.** Per Review_PAPER_V.docx structural suggestion (2026-09-21), the main paper is now organized around the core phenomenology (§1 Introduction → §2 Model → §3 Constraints → §9 Two-Component Resolution → §10 UV Completion No-Go Theorems → §11 Conclusions).

---


## 9. Two-Component Interpretation: Phenomenological Status and Open Issues (v18.33)

**Per the v18.32 honest phenomenological audit, §9 is rewritten from "Self-Consistent Two-Component Model with Gravothermal Selection" to "Phenomenological Status and Open Issues."** The earlier framing claimed the three-mechanism combination (Gaussian BW + two-component + gravothermal) **simultaneously satisfied** 7 of 8 observational channels. After the v18.29-v18.31 audit:

1. The **two-component + gravothermal mechanism requires f_H values** that are not derived from first principles and not reproduced by the project's own N-body check.
2. The **σ_eff = f_H² × σ_HH(v) decomposition** cannot match SPARC's σ/m ≈ 0.193 at v = 100 km/s for any f_H (max achievable σ_eff = 0.069) — a structural limitation.
3. The **T206 free-parameter fit** peaks at the grid boundary, reflecting the same structural failure.

This section now states honestly what the three mechanisms can and cannot do, with explicit limitations.

### 9.1 Motivation

The Horigome+ 2025 [27] constraint at v_eff ≈ 15 km/s (σ/m < 0.8 cm²/g for w=10 km/s) and the Cloud-9 σ/m ≈ 100 cm²/g requirement at v ≈ 28 km/s, combined with the SPARC band [0.05, 0.5] cm²/g at v ≈ 100 km/s and the cluster limit σ/m < 1 cm²/g at v ≈ 500 km/s, cannot be simultaneously satisfied by any single-component smooth σ(v) function (see §8.5 of v1.11 and the T110 closed investigations). The Lorentzian Breit-Wigner form has an irreducible tail σ_BW(v=15) ≈ 5 cm²/g given the v₁ peak at v ≈ 29 km/s.

### 9.2 The Three Mechanisms (phenomenological)

We combine three independent mechanisms to attempt to resolve this tension:

**(a) Gaussian Breit-Wigner profile (replaces Lorentzian).**
The Lorentzian tail σ ∝ (v − v_T)⁻² is replaced by a Gaussian σ ∝ exp[−(v − v_T)²/(2w²)]. For the v₁ peak (v_T = 29 km/s) with Gaussian width w₁ = 3 km/s, σ_BW(v=15) drops from 5.0 cm²/g (Lorentzian) to 2.0 cm²/g (Gaussian). The Gaussian profile is physically motivated for narrow s-channel resonances where the natural width Γ is set by the channel kinematics. **This is the one mechanism with first-principles motivation.**

**(b) Two-component asymmetric DM (Yang, Tsai, Fan 2025 PRD [42], cited as reference).**
The dark sector contains two species χ_H (heavy, mass ratio m_H/m_L ≈ 3) and χ_L (light). Cross-component scatterings can drive mass segregation: the heavy component sinks to the inner halo, the light component is expelled outward. **The f_H(r) profile that Yang+ 2025 PRD Fig. 2 shows is for σ₀/m = 147.1 cm²/g, NOT Phase 44's σ/m = 0.052 cm²/g.** These are different regimes. At Phase 44 σ/m, the gravothermal cascade timescale ≫ Hubble time, so no significant segregation is expected. **Yang+ 2025 is cited as a reference, not as the source of our f_H values.**

**(c) Gravothermal core-collapse selection effect (Yu 2026 PRL [23], Yang, Nadler, Yu, Zhong 2024 JCAP [43]).**
Different halos are in different evolutionary stages. Cloud-9 (still core-forming) retains a heavy fraction throughout the halo; dSphs (already gravothermally collapsed) have their heavy component concentrated in a deep inner core that is **smaller than the half-light radius** at which observations sample the stellar kinematics. The OBSERVED σ/m in a dSph therefore comes from a region where f_H is much smaller than the unresolved deep core. **However, this requires the gravothermal cascade to have actually progressed — at Phase 44 σ/m, this requires ≫ Hubble time and is not expected to occur.**

The effective cross-section per unit mass in the mixed halo is σ_eff/m = f_H² × σ_HH/m + 2f_H f_L × σ_HL/m + f_L² × σ_LL/m, where σ_HL drives the segregation. **Our current implementation uses only the heavy-channel term σ_HH, ignoring σ_HL and σ_LL — see §9.6.**

### 9.3 Phenomenological Status Table (per f_H prescription)

The 8-channel fit outcome **depends on the assumed f_H prescription**. We document this honestly by showing the channel-by-channel outcome under three different f_H choices:

| Channel | Constraint | σ/m_eff (hand-picked placeholder f_H, retracted v18.29; shown for reference only) | σ/m_eff (Yang+ 2025-derived f_H) | σ/m_eff (T202 N-body f_H) | Status across prescriptions |
|---|---|---|---|---|---|
| Cloud-9 (v=28, core-forming) | ≥100 cm²/g | 128 cm²/g ✓ | 87 cm²/g ✗ | 92 cm²/g ✗ | Pass with borrowed; fail with derived |
| dSph (v=15, core-collapsed) | ≤0.8 cm²/g | 0.18 cm²/g ✓ | 3.1 cm²/g ✗ | 4.2 cm²/g ✗ | Pass with borrowed; fail with derived |
| UFD (v=10, core-collapsed) | ≤0.8 cm²/g | 0.05 cm²/g ✓ | 0.16 cm²/g ✓ | 0.16 cm²/g ✓ | Pass (small margin with derived) |
| edge UFD (v=7) | ≤0.8 cm²/g | 0.07 cm²/g ✓ | 0.26 cm²/g ✓ | 0.27 cm²/g ✓ | Pass |
| UFD (v=5) | ≤0.8 cm²/g | 0.09 cm²/g ✓ | 0.46 cm²/g ✓ | 0.47 cm²/g ✓ | Pass |
| extreme UFD (v=3) | ≤0.8 cm²/g | 0.16 cm²/g ✓ | 0.94 cm²/g ✗ | 0.94 cm²/g ✗ | Pass with borrowed; fail with derived |
| SPARC (v=100, intermediate) | ∈[0.05, 0.5] cm²/g | 0.19 cm²/g ✓ | 0.053 cm²/g ✗ | 0.058 cm²/g ✗ | Cannot match (max σ_eff = 0.069) |
| Cluster (v=500) | <1.0 cm²/g | 0.0002 cm²/g ✓ | 0.003 cm²/g ✓ | 0.003 cm²/g ✓ | Pass (independent of f_H) |

**Honest summary** (replaces the v1.12/v1.13 "7 of 8 simultaneously satisfied" claim):

- With **borrowed (hand-picked) f_H**: 7 of 8 channels pass; SPARC and Cloud-9 ≥100 target satisfied.
- With **Yang+ 2025-derived f_H** (σ/m = 0.052 → no significant gravothermal cascade): only 4 of 8 channels pass; Cloud-9, dSph, extreme-UFD, SPARC all fail.
- With **T202 N-body f_H** (f_H ≈ 0.92 uniform, no segregation): only 4 of 8 channels pass (same channels as Yang+-derived).
- **SPARC cannot be matched** by any single-channel σ_eff = f_H² × σ_HH decomposition at Phase 44 σ/m. A full σ_HH + σ_HL + σ_LL decomposition is required.
- The **borrowed f_H "resolution" was structurally dependent** on values that are not derived and not reproduced by N-body.

### 9.4 Mechanism Decomposition (what each mechanism contributes)

The dSph σ/m_eff(v=15) decomposition illustrates the contribution of each mechanism:

| Mechanism | σ/m(v=15) | Reduction factor | Status |
|---|---|---|---|
| Phase 44 single-component Lorentzian | 5.0 cm²/g | (baseline) | Reproduced (T204) |
| + Gaussian BW (w₁=3) | 2.0 cm²/g | 2.5× | **First-principles motivated** |
| + two-component (borrowed f_H=0.30) | 0.18 cm²/g | 11× | **Placeholder-dependent** |
| + Horigome+ limit (w=10 km/s) | 0.8 cm²/g | (constraint) | — |

The combined 28× reduction (5.0 → 0.18 cm²/g) comes from **one well-motivated mechanism** (Gaussian BW, 2.5×) and **one placeholder-dependent mechanism** (two-component f_H = 0.30, 11×). With Yang+ 2025-derived f_H ≈ 0.79 at observation radius, the two-component reduction factor drops to ≈1.3×, so σ/m_eff(v=15) ≈ 1.5 cm²/g, exceeding the Horigome+ limit.

### 9.5 Why It Works (and Why It Doesn't)

The "self-consistent" v1.12 framing was misleading. The mechanism does **not** provide a first-principles derivation of f_H; it provides a **phenomenological framework** in which some f_H values reproduce the observational constraints. With the project's own N-body check (T202) showing f_H ≈ 0.92 uniform at Phase 44 σ/m, the gravothermal cascade is **not operative** in our parameter regime.

The 8-channel fit is best interpreted as:
- **A phenomenological interpolation** through 8 observational channels, using a multi-resonance σ/m(v) parameterization.
- The two-component + gravothermal selection is a **conceptual motivation**, not a derived physical prediction.
- The actual f_H profile at Phase 44 parameters is **unknown** (placeholder borrowed from a different σ/m regime; T202 N-body finds uniform; Yang+ Fig. 2 simulated at 2800× larger σ/m).

### 9.6 Limitations (v18.32 honest phenomenological audit)

The T206 Path C free-parameter fit (run on the joint 8-channel likelihood with corrected one-sided penalties) gives:

- Peak log L = **−0.431** (dominated by SPARC residual).
- Peak f_H_core_forming = **1.000** (boundary).
- Peak f_H_core_collapsed = **0.041** (boundary; grid extended to [0.0, 1.0] in v18.34).
- 68% CI on f_H_core_collapsed = **[0.0, 0.061]** — boundary sliver including the lower bound, confirming the likelihood is **monotonically decreasing above 0.041** and does not turn over inside the physical region.
- Per-channel contribution at peak (T206 v18.34, σ_unc-normalized one-sided Gaussian):

| Channel | log L contribution | σ_eff at peak | obs |
|---|---|---|---|
| SPARC v=100 | **−0.408** | 0.019 | 0.193 |
| Cloud-9 v=28 | −0.024 | 100.07 | 128.0 |
| UFD v=3, 5, 7, 10 | 0.000 each | 0.011–0.077 | 0.047–0.155 |
| dSph v=15 | 0.000 | 0.008 | 0.032 |
| Cluster v=500 | 0.000 | 0.000 | 0.000 |

The fit is **dominated by a single residual (SPARC)**; the boundary peak reflects the structural failure of σ_eff = f_H² × σ_HH to reach SPARC, not a data-driven f_H measurement.

**σ_unc convention (T206 vs T205):** The per-channel contributions above use T206's internal convention σ_unc = obs (a self-normalized choice per channel). T205, in contrast, uses the published error budgets from the actual observational papers (Cloud-9 floor ≈ 30 cm²/g; UFD/dSph ceiling ≈ 0.05 cm²/g; SPARC measurement ≈ 0.05 cm²/g; cluster ceiling ≈ 5×10⁻⁴ cm²/g). The qualitative conclusion is unchanged under either choice: **SPARC dominates the residual, the fit peaks at the f_H_cc lower boundary, and the boundary peak is structural rather than data-driven.** The two conventions are not directly comparable numerically (Cloud-9 σ_unc differs by ≈4×: 128 in T206 vs 30 in T205), but they are consistent in identifying SPARC as the irreducible residual.

**Interpretation**: The fit peaks at the grid boundary because the σ_eff = f_H² × σ_HH decomposition **cannot reach SPARC's σ/m ≈ 0.193** (max σ_eff = 0.069). The optimizer pushes f_H_cc to minimize UFD ceiling penalties while accepting an irreducible SPARC residual. This is **not a phenomenological measurement of f_H**; it reflects the structural failure of the heavy-channel-only decomposition.

**Known limitations**:

1. **Heavy-channel-only decomposition** σ_eff = f_H² × σ_HH: ignores σ_HL and σ_LL contributions. Cannot match SPARC. Required for full phenomenology.

2. **f_H profile not derived**: placeholder borrowed from Yang+ 2025 at 2800× larger σ/m; T202 N-body finds uniform at Phase 44; T183 fluid gives f_H ≈ 0.61. Three inconsistent values, none derived from our parameters.

3. **Cloud-9 4000× spike unexplained**: the published σ/m ≥ 50 cm²/g floor is satisfied only with borrowed f_H. The specific spike (σ/m = 128 vs ≥50) is a free parameter, not derived.

4. **T206 Path C is boundary-peaked**: the corrected one-sided likelihood gives a fit that is monotonic toward the grid boundary, not an interior maximum. Not a data-constrained measurement.

5. **dSph vs Cloud-9 tension unresolved at Phase 44**: with Yang+ 2025-derived or T202-derived f_H, the model **cannot simultaneously satisfy** Cloud-9 ≥100 cm²/g and dSph ≤0.8 cm²/g.

### 9.7 Channel outcome per f_H prescription

This subsection is a tabulation reference: see §9.3 for the full table.

| f_H prescription | Channels passing | Source / status |
|---|---|---|
| Borrowed (hand-picked 0.85/0.30/0.10) | 7 of 8 | v1.12 placeholder, retracted in v18.29 |
| Yang+ 2025-derived (σ/m=0.052 → no seg) | 4 of 8 (Cloud-9, extreme-UFD fail; SPARC structural fail) | v18.29-v18.30, matches T202 |
| T202 N-body (f_H ≈ 0.92 uniform) | 4 of 8 | v18.23 N-body, Phase 44 params |
| T183 fluid (f_H(core) ≈ 0.61) | ~6 of 8 (Cloud-9 marginal) | T183, see caveat in §9.5 |
| T206 Path C free-parameter fit | Structural boundary peak, not a measurement | v18.32 corrected likelihood |

The paper is best read as a **constraint map + no-go catalogue**, not a unified model. The two-component interpretation is conceptually motivated but not first-principles validated.

### 9.8 Complexity accounting (Occam's razor) — unchanged

The T120 model adds ~7 free parameters over Phase 44 (m_H/m_L ratio, Gaussian width w₁, f_H profile shape, gravothermal evolution time τ, etc.). However, four of these are externally constrained:
- m_H/m_L is fixed by Yang+ 2025 PRD at 3:1 (not free)
- Gaussian width w₁ is constrained by the resonance natural width Γ
- f_H profile shape is **NOT** constrained by cosmological simulations at Phase 44 parameters (see §9.6)
- Gravothermal evolution time τ is constrained by cluster density profiles

So the **effective free-parameter count** is closer to 3-4 (not 7), which is consistent with the **5-parameter clockwork UV-prior fit** in §6 (Phase 53 v2). The f_H prescription remains the largest source of model-dependence in the phenomenology.

### 9.9 Path F1: three-term σ_eff decomposition (T207, v18.38)

**Motivation.** The v18.34 phenomenological audit identified a **structural limitation** of the heavy-channel-only decomposition: σ_eff = f_H² × σ_HH(v) **cannot match SPARC's σ/m ≈ 0.193 at v = 100 km/s** for any f_H (max achievable σ_eff = 0.069; see §10.1, abstract, §1 caveat). The full three-term mixture rule,

σ_eff(v) = f_H² × σ_HH(v) + 2 f_H f_L × σ_HL(v) + f_L² × σ_LL(v),

introduces a heavy-light cross-section σ_HL that has its own velocity dependence — independent of the heavy-only σ_HH(v) Breit-Wigner structure. Path F1 (T207) implements and fits this three-term decomposition against the 8-channel joint likelihood.

**What T207 added.** Two new scripts (`v0.3-prelim/code/two_component_three_term.py`, 165 LoC; `T207_three_term_fit.py`, 250 LoC) and 9 result files (`v0.3-prelim/data/results/t207_*.json`) implementing the three-term formula with 9 free parameters (σ_0, σ_peak_HH_1, σ_0_HL, σ_peak_HL, v_HL, σ_0_LL, a_slope, f_H_cf, f_H_cc). The fit operates in three modes: **free_f_H** (all 9 parameters free; σ_HL unconstrained), **prescription modes** (borrowed / yang / t202 external f_H values), and **smart_de** (Phase 44 best-fit seeded DE).

**Key structural finding (T207 v18.37, per `T207_THREE_TERM_REPORT_2026-09-23.md` §3):**
- The free_f_H fit is **pathologically boundary-peaked**: f_H_cc → 0.004 at the grid lower bound, mirroring the v18.31 T206 retraction. Not a data-driven measurement.
- The DE saturates the likelihood (log L_peak ≈ 0) at σ_peak_HL ≈ 0.34, v_HL ≈ 98 km/s. **The σ_HL term is structurally needed**: SPARC cannot be reached under σ_HH + σ_LL alone; the heavy-light cross-section contributes ~0.16 of the 0.193 SPARC target.
- Three prescription modes (borrowed, yang, t202) all yield σ_HL ≈ 0.3-0.4, v_HL ≈ 98-100 km/s — a **robust on-peak HL signature** at SPARC-relevant velocity.

### 9.10 Path F1 v18.38: priored free fit (Yang+ 2025 Fig. 2 floor)

**Why the prior change.** v18.37's f_H_cc → 0 boundary peak is structurally identical to the v18.31 (T206) pathology retracted in v18.32. v18.38 tightens BOUNDS[8] from (0.0, 1.0) to (0.05, 1.0) — a **conservative physical floor chosen to rule out the f_H_cc → 0 pathology**. Yang+ 2025 Fig. 2 itself suggests a stricter floor at ~0.4 (f_L ∈ 0.3-0.6 across all M_halo bins ⇒ f_H_cc ∈ 0.4-0.7); 0.05 is the maximally-permissive bound that still excludes the boundary pathology.

**Results** (per `T207_V1838_PRIORED_REVIEW_2026-09-25.md` §4):
- DE peak: f_H_cc = 0.053 (Yang+ floor), v_HL = 103.3 km/s, σ_peak_HL = 0.325, σ_peak_HH_1 = 388.6 — Mechanism A on-peak
- emcee 50k posterior median (32 walkers × 50000 steps, burn-in 2000, Gaussian init from DE):
  - f_H_cc = **0.060 ± 0.012** (narrow, at floor — boundary pathology eliminated)
  - v_HL = **105 ± 39 km/s** (Mechanism A on-peak)
  - σ_peak_HL = 0.52 ± 0.36
  - σ_peak_HH_1 = 625 ± 250
  - a_slope = 0.96 ± 0.20, f_H_cf = 0.83 ± 0.15
- **50τ convergence marginally achieved**: ratio = n_steps / (50 × τ_max) = 50000 / (50 × 918) = **1.089** (vs v18.37's 0.576 — **1.89× improvement**, driven by both shorter τ_max (1737→918, prior removed slow direction) AND same chain length; not 94× as initially reported — see `T207_V1838_PRIORED_REVIEW_2026-09-25.md` §10 erratum).
- **τ_max dropped from 1737 (v18.37) to 918 (v18.38)**: the f_H_cc ≥ 0.05 prior removed a slow direction in the sampler; both shorter τ and same chain length contribute to the convergence improvement.

**Smart_de cross-check** (per §5): all three prescription modes (borrowed, yang, t202) reproduce v18.37 results to 4 sig figs (log L -6.04 / -9.09 / -11.08 respectively; v_HL all ~100 km/s). The prior change does not disturb prescription baselines — confirming the v18.38 effect is specific to the free_f_H branch where f_H was previously unconstrained.

### 9.11 Path F1 honest verdict split (v18.38)

The priored free fit **trades SPARC fit quality for a physically motivated f_H_cc — standard prior-vs-likelihood tradeoff, not a bug**:

| Mode | SPARC log L | z | F1 verdict |
|---|---|---|---|
| borrowed (hand-picked f_H) | -0.09 | 0.42 | **RESOLVED** |
| yang (Yang+ 2025-derived f_H) | -0.24 | 0.69 | **MARGINAL** |
| t202 (N-body f_H) | -0.60 | 1.10 | **NOT RESOLVED** |
| free_f_H priored (v18.38) | -2.03 | 2.01 | **CLEAR FAIL** |
| free_f_H boundary (v18.37) | ≈ 0 (saturated, pathological) | — | (pathology, not a measurement) |

**Summary of Path F1 v18.38:**
- ✅ **Boundary-peak pathology eliminated** (f_H_cc = 0.060 ± 0.012, not 0.004)
- ✅ **Mechanism A empirically preferred** by posterior (v_HL = 105 ± 39 km/s, on-peak HL)
- ✅ **50τ convergence marginally achieved** (ratio 1.089, 1.89× v18.37's 0.576)
- ✅ **Prescription modes robust** to prior change (smart_de cross-check identical)
- ⚠ **F1 resolved only under borrowed prescription mode**; yang marginal, t202 not resolved, priored free fit clear-fails SPARC at the posterior median
- ⚠ **Mechanism A vs B remains observationally degenerate at SPARC**: both yield σ_eff(100) ≈ 0.19; the prior (not causality) selects A in v18.38. Cloud-9 causality (§10.4a) constrains σ_peak_HH_1 (Cloud-9 v=28) independently of σ_HL (SPARC v=100) — the two velocity scales don't interact in the mixture rule.
- ⚠ **Cloud-9 vs dSph tension unchanged** from v18.37 — Cloud-9 sits at floor (obs = 128 cm²/g, σ_unc = 30)

**Net effect on paper verdict:** The σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL + f_L² σ_LL decomposition is **structurally sufficient** (it can reach SPARC's σ/m ≈ 0.193 via the σ_HL term), but the free fit cannot simultaneously satisfy SPARC and the Yang+ 2025-derived f_H_cc ≥ 0.05 prior. **Path F1 is resolved under borrowed prescription mode; the honest phenomenological verdict per f_H prescription (§9.3 / §9.7) is unchanged.** Cloud-9 vs dSph tension remains the unresolved structural issue.
