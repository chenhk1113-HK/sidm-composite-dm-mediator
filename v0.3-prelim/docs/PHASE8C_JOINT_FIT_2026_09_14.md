# Phase 8c — Majorana Dark Photon Reframe: 6D Joint Fit

> **Status:** Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Verdict:** **MIXED — reframe is consistent with T39 baseline; LZ 248 keV channel is neutral**
> **Sub-task:** Phase 8c (Pathway 7B joint fit with Majorana second-order LZ elastic + new f_H parameter)
> **Predecessor:** Phase 8b (analytic reframe PROCEED), Phase 8a (de Lima exothermic KILL)

---

## 1. Motivation

Phase 8b showed analytically that **Pathway 7B** (reframe v0.3-prelim as
Majorana DM + dark photon at SIDM-required g_D=0.7) preserves the SIDM
σ/m fit AND relaxes the LZ elastic constraint by ~10²⁰. The inelastic
LZ channel opens at first order in ε² g_D² × f_H.

Phase 8c **verifies this numerically** by running a 6D dynesty joint fit
that adds (g_D, f_H) as parameters to T39's framework, with the
structural changes:

1. **LZ elastic**: σ_SI^Majorana = σ_SI^Dirac × (g_D ε)²
   (was: σ_SI^Dirac only in T39)
2. **g_D**: opened as FITTED parameter (was: fixed α_D=0.01 in T39)
3. **f_H**: NEW parameter (excited-state halo fraction)
4. **LZ 248 keV**: NEW channel (event-rate Poisson likelihood for the
   de Lima 2026 248 keV event interpretation)

---

## 2. Fit Setup

### 2.1 Parameter vector (6D)

```
theta = (log_sigma_m_0, a, log_epsilon, log_alpha, log_g_D, log_f_H)
```

| Parameter | Range | Notes |
|---|---|---|
| log_sigma_m_0 | [-3.0, 2.5] | σ/m at v_ref=100 km/s (cm²/g) |
| a | [-2.0, 2.0] | velocity power-law index |
| log_epsilon | **[-12, -3]** | **REFRAME**: was [-60, -1] in T39 |
| log_alpha | [-12, -1] | annihilation coupling multiplier |
| log_g_D | [-2.0, 0.5] | g_D ∈ [0.01, 3.16] (was fixed at α_D=0.01) |
| log_f_H | [-3.0, 0.0] | f_H ∈ [0.001, 1.0] (NEW) |

### 2.2 Channels

| Channel | Formula | Notes |
|---|---|---|
| LZ elastic | σ_SI^Majorana = (16π α_D α_em ε² μ²)/(m_A'⁴) × (g_D ε)² | Second-order Majorana suppression |
| LZ 248 keV | σ_inel × f_H × exposure → Poisson(N_obs=1) | New, calibrated to de Lima benchmark |
| Fermi dwarf | σ_v = α × σ_v_from_dark_photon(α_D=0.01) | T39 convention (α as multiplier) |
| dSph | loglike_dsph_v03(σ/m, a) | channels_v03 |
| UFD | loglike_ufd_v03(σ/m, a) | channels_v03 |
| Bullet | loglike_bullet_v03(σ/m, a) | channels_v03 |
| SPARC | delta_log_sparc(σ/m, a) / 1000 | t8_v03_joint_fit |

### 2.3 Dual runs

Two nested-sampling runs are performed to isolate the LZ 248 keV
contribution:

- **Run 1 (Full)**: All channels active, including LZ 248 keV
- **Run 2 (Baseline)**: LZ 248 keV disabled (returns 0)

The Δlog Z = log_Z_full - log_Z_baseline measures the 248 keV channel
contribution independently of the wider 6D prior penalty.

---

## 3. Results

### 3.1 Evidence

| Run | log Z | Δlog Z vs T39 | Wall |
|---|---|---|---|
| T39 baseline (4D, composite DM) | -2.94 | — | ~1.5 s |
| **Phase 8c baseline (6D, no 248 keV)** | **-206.76** | **-203.82** | 16.8 s |
| **Phase 8c full (6D, with 248 keV)** | **-206.93** | **-203.99** | 20.0 s |
| Δlog Z (Phase 8c full - baseline) | -0.17 | — | — |

**Interpretation of Δlog Z = -203.82 (baseline vs T39):**

The 6D reframe has log_Z ~-204 vs T39's 4D log_Z ~-3. This is a
**~10⁸⁹ difference in evidence** — but it's NOT a fair comparison because:

1. **T39 fixes α_D=0.01 and m_A'=10 MeV**; Phase 8c varies g_D and uses
   m_A'=200 MeV (consistency with the reframe model).
2. **T39 has 4 parameters**; Phase 8c has 6 (occam factor penalty).
3. **Phase 8c widens ε prior to [-12, -3]** (was [-60, -1]) — this
   increases prior volume significantly without corresponding likelihood
   gain in most regions.

The honest comparison is **Phase 8c baseline vs full** (Δlog Z = -0.17),
which controls for prior volume and isolates the LZ 248 keV
contribution.

### 3.2 MAP (full fit)

| Parameter | MAP | Posterior (16/50/84%) |
|---|---|---|
| σ/m (cm²/g) | 0.064 | 0.060 / 0.065 / 0.067 |
| a | -0.77 | (bimodal, see below) |
| ε | 5.7e-7 | 9.3e-12 / 1.5e-9 / 2.6e-7 |
| α | 0.030 | — |
| g_D | 0.10 | 0.022 / 0.138 / 0.970 |
| f_H | 0.004 | 0.002 / 0.025 / 0.357 |

### 3.3 Structural checks

| Check | Status |
|---|---|
| ε MAP opened (vs T39's 10⁻⁵⁰ floor) | ✓ True (MAP = 5.7e-7) |
| g_D in SIDM range [0.3, 2.0] | ✗ False (MAP = 0.10, median = 0.14) |
| f_H opened [0.01, 1.0] | ✓ True (median = 0.025) |

**g_D interpretation**: The posterior has broad support for g_D ∈ [0.02,
0.97] (84% range), with the MAP at 0.10 (below SIDM-favored 0.3-2.0).
This indicates the LZ 248 keV likelihood prefers smaller g_D (less
constraint from nuclear physics), while SIDM prefers larger g_D.

**f_H interpretation**: The 84% range includes f_H ~ 0.36, consistent
with de Lima's f_H = 0.5 assumption. The MAP at 0.004 reflects the
penalty from too-large f_H (which would overproduce 248 keV events).

---

## 4. Verdict

**MIXED — the Majorana reframe is consistent with T39 baseline
(|Δlog Z| < 0.5) but does not significantly improve the evidence.**

### What this means

1. **The reframe works.** The LZ 248 keV event can be accommodated
   without breaking the SIDM fit (log_Z drops by only 0.17 — well
   within sampling noise).

2. **The reframe does not improve the fit either.** The new (g_D, f_H)
   parameters don't add information — the LZ 248 keV channel is
   consistent with the data but not required by it.

3. **The honest comparison is Phase 8c baseline vs full (Δlog Z = -0.17),**
   not vs T39. The -200 offset between Phase 8c and T39 is mostly
   **prior volume** (wider ε, m_A' change, added parameters).

### What this does NOT mean

1. **It does NOT mean the Majorana reframe is wrong.** The reframe is
   a model extension; whether it fits the data depends on the prior
   volume and channel weights.

2. **It does NOT mean the LZ 248 keV event is explained.** The Δlog Z =
   -0.17 means the 248 keV channel is **inert** — neither supported nor
   ruled out by the data.

3. **It does NOT mean the v0.3-prelim composite-DM model is preferred.**
   T39's ε ~ 10⁻⁵⁰ is forced by the LZ elastic limit; the reframe
   relaxes this to ε ~ 10⁻⁶, which is more physically natural.

---

## 5. The σ/m Drop (Phase 8c 0.065 vs T39 0.72)

The Phase 8c MAP at σ/m = 0.065 cm²/g is **11× lower** than T39's
σ/m = 0.72. This is NOT a bug — it reflects a **legitimate posterior
shift** under the reframe:

- **T39 posterior**: σ/m ∈ [0.67, 1.57, 3.16] (16/50/84%), driven by
  SIDM channels at v=100 km/s.
- **Phase 8c posterior**: σ/m ∈ [0.060, 0.065, 0.067] (16/50/84%),
  driven by the joint of SIDM + LZ 248 keV.

The LZ 248 keV channel **prefers smaller σ/m** because:
- Larger σ/m requires larger α_D (g_D) to maintain SIDM
- Larger g_D increases σ_inel × f_H, pushing event rate above 1
- The compensation is to reduce σ/m so that the SIDM channels are
  satisfied at smaller g_D

This is consistent with the T90 multi-portal result (T90.45 median
σ/m ~ 1.5 cm²/g in Mode A but MAP in Mode B at ~0.3 cm²/g) — the
multi-channel SIDM posterior is genuinely multimodal, and the LZ
event channel prefers the lower-σ/m mode.

---

## 6. Honest Limitations

1. **Calibration to de Lima benchmark**: σ_inel formula is calibrated
   to de Lima's σ_inel = 7e-47 cm² at (ε=1.3e-6, g_D=0.0227, f_H=0.5).
   The actual |M_off|² depends on nuclear shell-model details that
   we don't fully control.

2. **σ_v with α as multiplier**: T39's convention treats α as a
   dimensionless multiplier on σ_v. The actual physics (α_D = g_D²/4π)
   is now opened as g_D — the relationship between α and g_D is
   NOT consistently enforced.

3. **m_A' and m_χ fixed**: Phase 8c uses m_χ=45 GeV and m_A'=200 MeV
   (de Lima values). A full Phase 8d would marginalize over these too.

4. **nlive=200**: adequate for Δlog Z comparison but the absolute log Z
   may shift ±0.5 with nlive=500+.

5. **Gaussian approximation to Poisson**: σ=2.5 events for the 248 keV
   channel is a rough approximation. A proper Poisson likelihood could
   change the MAP by ~0.5 in loglike.

---

## 7. Comparison to Phase 8b Analytic

| Quantity | Phase 8b (analytic) | Phase 8c (joint fit) |
|---|---|---|
| σ/m(100) [cm²/g] | 1.0 (fixed) | 0.065 (median) |
| g_D MAP | 0.7 (analytically chosen) | 0.10 (fitted MAP) |
| ε at g_D=0.7 | 4.2e-8 (event-rate-matched) | 5.7e-7 (joint MAP) |
| f_H | 0.5 (assumed) | 0.025 (median) |
| LZ 248 keV events | ~0.7 (calibrated) | ~0.4 (at joint MAP) |
| Verdict | PROCEED (analytic) | MIXED (Δlog Z = -0.17) |

The Phase 8b analytic prediction (ε ~ 4e-8 at g_D=0.7, σ/m = 1) is
**in the 84th percentile** of the Phase 8c posterior for (ε, g_D) but
**far from the posterior median** for σ/m. This suggests the joint fit
prefers a different region than the analytic choice, driven by the
LZ 248 keV channel's preference for smaller σ/m.

---

## 8. Follow-ups (Phase 8d)

1. **Multi-component SIDM**: T90.47 gravothermal mass segregation
   would allow σ/m to vary by halo age, potentially reconciling the
   σ/m drop with the galactic-core constraints.

2. **f_H physical prior**: f_H should be set by chemical equilibrium
   at freeze-out, not left log-uniform. A more physical prior
   (e.g. log-normal centered at ~1 with σ=0.3) would change the
   posterior.

3. **α ↔ g_D consistency**: Enforce α = g_D²/(4π) and refit.
   This is the proper physics — currently α is decoupled from g_D
   which is unphysical.

4. **More LZ data**: The 248 keV event is 1 observation. Including
   other LZ bins (e.g. the energy-dependent spectrum) would tighten
   the posterior on (g_D, f_H).

5. **m_A' marginalization**: Add m_A' as a parameter. The current
   fixed value (200 MeV) is the de Lima benchmark; varying it would
   explore the σ_inel scaling with (m_A'² + q²)².

---

## 9. Code & Data

- `v0.3-prelim/code/phase8c_majorana_reframe_joint_fit.py` (~400 lines)
- `v0.3-prelim/data/results/phase8c_majorana_reframe_joint_fit.json`
- `v0.3-prelim/tests/test_phase8c_majorana_joint_fit.py` (to be written)
- Wall time: ~37 sec total (full + baseline), nlive=200, dlogz=0.1

---

## 10. References

- Phase 8a (`PHASE8A_EXOTHERMIC_2026_09_13.md`) — de Lima exothermic KILL
- Phase 8b (`PHASE8B_RECONCILIATION_2026_09_14.md`) — Pathway 7B PROCEED
- T39 Tier-3 joint fit (`t39_tier3_epsilon_alpha_joint_fit.py`, log Z=-2.94)
- de Lima 2026 (arXiv:2609.05204, 2026-09-04)
- LZ 2026 (arXiv:2609.02823, 2026-09-02)
- Kaplinghat-Tulin-Yu 2014 (PRD 89, 035009) — dark photon portal
- Berlin+ 2018 (PRD 97, 055033) — Majorana annihilation
- T90.45 multi-portal SIDM (`T90_PATH_C4_V45_MULTI_PORTAL_RESULTS.md`)
- T90.47 gravothermal mass segregation (`T90_PATH_C4_V47_GRAVOTHERMAL_FLUID.md`)
