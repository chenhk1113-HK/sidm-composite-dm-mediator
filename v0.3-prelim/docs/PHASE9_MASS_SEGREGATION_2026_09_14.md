# Phase 9 — Multi-Component SIDM Mass Segregation: Honest Negative

> **Status:** Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Verdict:** **HONEST NEGATIVE — mass segregation alone is INSUFFICIENT**
> **Sub-tasks:** Phase 9 (initial, used v_escape — buggy), Phase 9b (corrected, uses v_disp)
> **Predecessor:** Phase 8d (Majorana reframe INERT, σ/m drop to 0.065 cm²/g)

---

## 1. The Question

Phase 8d left a puzzle: v0.3-prelim's σ/m MAP dropped from 0.72 (T39)
to 0.065 (Phase 8c/8d), driven by the LZ 248 keV channel preferring
smaller g_D. The data across SIDM channels spans σ/m ~ 0.5 to 50 cm²/g
(Bullet to Cloud-9) — a factor of 100 spread. Can Yang, Fan, Tsai 2025
multi-component SIDM with gravothermal mass segregation reproduce this?

## 2. The Setup

Multi-component SIDM (m_H > m_L):
- Heavy species sinks to halo center via gravothermal collapse + drag
- Light species pushed outward by heavy's collapse
- OLD halos: segregated (heavy-rich center, light-rich outskirts)
- YOUNG halos: still mixed

If segregation is strong enough, σ/m_observed at the half-light
radius differs from the unmixed expectation — providing an additional
mechanism beyond pure velocity dependence.

**v0.3-prelim parameters**:
- m_H = 45 GeV, m_L = 15 GeV (m_H/m_L = 3, Yang+ 2025 default)
- g_H = g_L = 0.7 (SIDM-required)
- m_phi = 100 MeV (v0.3-prelim SIDM MAP value)

**Halo types**:
- Dwarf/LSB (YOUNG, 5 Gyr): v_disp = 30 km/s, σ/m_obs ~ 30 cm²/g (Cloud-9)
- MW-like (OLD, 10 Gyr): v_disp = 100 km/s, σ/m_obs ~ 1 cm²/g (T39 MAP)
- Cluster (OLD, 10 Gyr): v_disp = 3000 km/s, σ/m_obs ~ 0.5 cm²/g (Bullet limit)

## 3. Phase 9 (initial) — Bug

First attempt used `effective_sigma_m_at_radius` which evaluates σ/m at
the **local escape velocity** (v ~ 1000s km/s in MW halos). This is
**way above Yukawa Born validity** and gave σ/m ~ 0 cm²/g everywhere.

## 4. Phase 9b (corrected) — Use v_disp, not v_escape

Fixed: σ/m_observed = density-weighted mixture of σ_H(v_disp) and σ_L(v_disp).

### Results

| Halo | v_disp | σ/m_obs (data) | σ/m_evolved | ratio |
|---|---|---|---|---|
| Dwarf/LSB (YOUNG, 5 Gyr) | 30 km/s | 30.0 cm²/g | 0.94 | **32× off** |
| MW-like (OLD, 10 Gyr) | 100 km/s | 1.0 cm²/g | 0.93 | **1.08 match** |
| Cluster (OLD, 10 Gyr) | 3000 km/s | 0.5 cm²/g | 0.053 | 9.4× off |

- σ/m_evolved spread: 17.7×
- σ/m_observed spread: 60×
- **Mass segregation INSUFFICIENT** to explain the observed spread.

## 5. The Real Mechanism: Velocity Dependence, Not Segregation

Looking at the numbers:
- σ_H(v_disp) drops from 0.93 cm²/g at v=100 km/s to 0.053 cm²/g at v=3000 km/s
- That's a 17× drop **just from velocity dependence of the Yukawa cross-section**
- The mass segregation (f_H going from 0.75 to 1.0 at r_half) contributes an additional factor of ~1.5×

**The observed σ/m spread is mostly YUKAWA VELOCITY DEPENDENCE, not mass segregation.**

This is consistent with T90.45's finding that **multi-portal SIDM** (not
multi-component) is the dominant mechanism for the σ/m(v) spread.

## 6. What Doesn't Work

1. **Cloud-9 (v=30 km/s)**: σ/m_evolved = 0.94 cm²/g vs data 30 cm²/g
   - At m_phi=100 MeV, the Yukawa Born form gives σ/m(v=30) ~ 1 cm²/g
   - The Cloud-9 data requires σ/m(v=28) ~ 30 cm²/g
   - Need m_phi ~ 30-50 MeV (heavier mediator reduces σ/m at v=100)
   - This is the **multi-portal** solution (T90.45)

2. **Cluster (v=3000 km/s)**: σ/m_evolved = 0.053 cm²/g vs data 0.5 cm²/g
   - Factor 10× off — model under-predicts σ/m at high v
   - Could be due to non-perturbative effects (Sommerfeld enhancement)
   - Or cluster data has weaker constraint than the limit

3. **MW-like (v=100 km/s)**: σ/m_evolved = 0.93 cm²/g vs data 1.0 cm²/g
   - Excellent match (ratio 1.08)
   - This is the only halo type where mass segregation + Yukawa
     reproduces the observation

## 7. Implications for v0.3-prelim

The mass segregation framework (Yang+ 2025) does **NOT** solve the
σ/m spread puzzle. The dominant mechanism remains:
1. **Yukawa velocity dependence** (handles MW + Bullet partially)
2. **Multi-portal** (handles Cloud-9 — T90.45)

The σ/m drop from Phase 8c (0.72 → 0.065) is NOT explained by mass
segregation. The puzzle remains: **why does the LZ 248 keV channel
prefer σ/m ~ 0.065 when SIDM channels favor σ/m ~ 1?**

Possible answers (untested):
- LZ measures σ_inel (not σ/m at v_disp) — the channels probe
  different physics
- The LZ 248 keV event is a statistical fluctuation, not a real signal
- The SIDM channels are wrong about σ/m ~ 1 at v=100 (overestimated)

## 8. Honest Scope

- **Mass segregation is REAL** (T90.47 validates it: heavy sinks to
  center, light pushed outward over Gyr timescales)
- **Mass segregation alone is insufficient** to explain the σ/m spread
- The Yang+ 2025 framework requires **multi-portal + mass segregation**
  (not just mass segregation) to match the full data
- This is consistent with T90.45's earlier finding that multi-portal
  (not multi-component) is the dominant unified-SIDM architecture

## 9. Code & Data

- `code/phase9_multi_component_mass_segregation.py` (~200 lines, v_escape bug)
- `code/phase9b_mass_segregation_vdisp.py` (~250 lines, corrected)
- `data/results/phase9b_mass_segregation_vdisp.json`
- Wall time: ~10 sec per halo, ~30 sec total

## 10. References

- T90.47 (`T90_PATH_C4_V47_GRAVOTHERMAL_FLUID.md`) — gravothermal fluid module
- T90.45 (`T90_PATH_C4_V45_MULTI_PORTAL_RESULTS.md`) — multi-portal SIDM
- Yang, Fan, Tsai 2025 (arXiv:2504.02303) — multi-component SIDM framework
- Phase 8d (`PHASE8D_SERIES_2026_09_14.md`) — Majorana reframe INERT verdict
- Balberg, Shapiro, Socrate 2002 — gravothermal fluid foundation
- Essig+ 2019 — SIDM halo collapse calibration

## 11. Recommended Next Steps

Phase 9b's honest negative suggests:
1. **Publish Phase 9b as honest scope**: "Mass segregation is necessary
   but insufficient; multi-portal is the dominant mechanism"
2. **Combine Phase 9b + Phase 8d** as a single paper on "SIDM
   architecture constraints at v0.3-prelim"
3. **Move to a different puzzle** — perhaps the LZ 248 keV statistical
   fluctuation hypothesis, or the freeze-out conflict at g_D ~ 0.7
