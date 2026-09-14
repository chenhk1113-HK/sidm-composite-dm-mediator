# T90 Cloud-9 Branch — Navigation Index

> **Purpose:** Single entry point for the T90 Cloud-9 branch (`wip/cloud-9-relhic`).
> **Last updated:** 2026-09-14
> **Tag:** `t90-grand-unified-v63-2026-09-14`

---

## 📖 Start here

**For a 5-minute read:** [`T90_MASTER_REFERENCE_2026_09_14.md`](./T90_MASTER_REFERENCE_2026_09_14.md)

The master reference consolidates T90.14 → T90.63 + Phase 20-21 findings into:
- 5+1 channel matrix
- 5 alternative frameworks × channels
- Unified model parameters
- Failed-channel analysis (DAMPE/XRISM/eROSITA)
- Ablation hierarchy

---

## 🗂️ Per-version docs (audit trail)

### Foundational versions (V14–V22)

| Version | Doc | What it does |
|---|---|---|
| V14 | [`V14_CALIBRATED`](./T90_PATH_C4_V14_CALIBRATED.md) | Calibrated operators baseline |
| V17 | [`V17_LZ_TIME_SERIES`](./T90_PATH_C4_V17_LZ_TIME_SERIES.md) | LZ time-series analysis |
| V22 | [`V22_MASTER_RECALIBRATION`](./T90_PATH_C4_V22_MASTER_RECALIBRATION.md) | Master recalibration (reference σ/m point) |

### Cloud-9 / RELHIC integration (V27–V29)

| Version | Doc | What it does |
|---|---|---|
| V27 | [`V27_RELHIC_CLOUD9`](./T90_PATH_C4_V27_RELHIC_CLOUD9.md) | RELHIC Cloud-9 likelihood |
| V28 | [`V28_RELHIC_MCMC`](./T90_PATH_C4_V28_RELHIC_MCMC.md) | RELHIC MCMC sampling |
| V29 | [`V29_RELHIC_YUKAWA`](./T90_PATH_C4_V29_RELHIC_YUKAWA.md) | RELHIC Yukawa σ/m |

### Architecture steps (V40–V50)

| Version | Doc | What it does |
|---|---|---|
| V40 | [`V40_HONEST_UNIFICATION`](./T90_PATH_C4_V40_HONEST_UNIFICATION.md) | Honest unification framing |
| V44 | [`V44_MULTI_PORTAL`](./T90_PATH_C4_V44_MULTI_PORTAL.md) | Multi-portal infrastructure |
| **V45** | **[`V45_MULTI_PORTAL_RESULTS`](./T90_PATH_C4_V45_MULTI_PORTAL_RESULTS.md)** | **Multi-portal joint fit (THE architectural step)** |
| V46 | [`V46_MULTI_COMPONENT`](./T90_PATH_C4_V46_MULTI_COMPONENT.md) | Multi-component SIDM |
| V47 | [`V47_GRAVOTHERMAL_FLUID`](./T90_PATH_C4_V47_GRAVOTHERMAL_FLUID.md) | 1D gravothermal fluid |
| V48 | [`V48_PARAMETER_SCAN`](./T90_PATH_C4_V48_PARAMETER_SCAN.md) | Parameter scan (HONEST NEGATIVE) |
| V49 | [`V49_INELASTIC_SIDM`](./T90_PATH_C4_V49_INELASTIC_SIDM.md) | Inelastic SIDM (HONEST NEGATIVE) |
| V50 | [`V50_RESONANT_SIDM`](./T90_PATH_C4_V50_RESONANT_SIDM.md) | Resonant SIDM (alternative mechanism) |

### Joint fits and unified model (V51–V58)

| Version | Doc | What it does |
|---|---|---|
| V51 | [`V51_RESONANT_JOINT_FIT`](./T90_PATH_C4_V51_RESONANT_JOINT_FIT.md) | Resonant 6D joint posterior |
| V52 | [`V52_LIKECOMPARE`](./T90_PATH_C4_V52_LIKECOMPARE.md) | Apples-to-apples multi-portal vs resonant |
| V55 | [`V55_HYBRID_JOINT_FIT`](./T90_PATH_C4_V55_HYBRID_JOINT_FIT.md) | Hybrid 9D joint fit (3 ch) |
| V56 | [`V56_LZ_CHANNEL`](./T90_PATH_C4_V56_LZ_CHANNEL.md) | Hybrid + LZ (10D, 4 ch) |
| V57 | [`V57_KSFR_CHANNEL`](./T90_PATH_C4_V57_KSFR_CHANNEL.md) | Hybrid + LZ + KSFR (10D, 5 ch) |
| V58 | [`V58_ABLATION`](./T90_PATH_C4_V58_ABLATION.md) | Channel-set ablation (robustness hierarchy) |

### Synthesis and extensions (V59–V63)

| Version | Doc | What it does |
|---|---|---|
| V59 | [`V59_GRAND_UNIFIED_SUMMARY`](./T90_PATH_C4_V59_GRAND_UNIFIED_SUMMARY.md) | Grand unified synthesis (5 channels) |
| V60 | [`V60_NATURALNESS`](./T90_PATH_C4_V60_NATURALNESS.md) | Barbieri-Giudice naturalness |
| V61 | [`V61_KAHLHOEFER_AUDIT`](./T90_PATH_C4_V61_KAHLHOEFER_AUDIT.md) | σ_DM-nuc audit (REVISED — unit bug found) |
| V62 | [`V62_GAUSSIAN_TO_REAL_POSTERIORS_AUDIT`](./T90_PATH_C4_V62_GAUSSIAN_TO_REAL_POSTERIORS_AUDIT.md) | Posterior realism audit |
| V63 | [`V63_LRD_CHANNEL`](./T90_PATH_C4_V63_LRD_CHANNEL.md) | LRD channel (Jiang 2026 ApJL 996 L19) |

### Branch context (informational)

| Doc | What it covers |
|---|---|
| [`V59_BRANCH_CONTEXT`](./T90_PATH_C4_V59_BRANCH_CONTEXT.md) | Cross-reference of README/CURRENT.md/MATHEMATICS.md/T90 doc drift (different evolution lines, not a T82 audit failure) |

---

## 🧪 Phase 11-22 series (Majorana reframe + failed-channel analysis + reviewer fixes)

### LZ 248 keV sweep + Majorana reframe

| Phase | Doc | Verdict |
|---|---|---|
| 11 | [`PHASE11_12_FREEZE_OUT_AND_SIGMA_DROP_2026_09_14`](./PHASE11_12_FREEZE_OUT_AND_SIGMA_DROP_2026_09_14.md) | Asymmetric DM PROCEED |
| 12 | (same doc) | σ/m drop STRUCTURAL (data preference, not LZ) |
| 13 | [`PHASE13_14_MEDIATOR_AND_SIGMA_DROP_2026_09_14`](./PHASE13_14_MEDIATOR_AND_SIGMA_DROP_2026_09_14.md) | Mediator bimodality STRUCTURAL |
| 14 | (same doc) | σ/m vs m_phi STRUCTURAL |
| 15–17 | [`PHASE15_16_17_PROBES_2026_09_14`](./PHASE15_16_17_PROBES_2026_09_14.md) | Annihilation STRUCTURAL; η/η_B natural at 5 GeV; g_D split needed |
| 18 | [`PHASE18_MCHI_COMPARISON_2026_09_14`](./PHASE18_MCHI_COMPARISON_2026_09_14.md) | σ/m INVARIANT across m_chi |
| 19 | [`PHASE19_FULL_REFIT_MCHI_5GEV_2026_09_14`](./PHASE19_FULL_REFIT_MCHI_5GEV_2026_09_14.md) | Full v0.3-prelim refit at m_chi=5 GeV |

### Full space-conditions test (20 channels)

| Phase | Doc | Verdict |
|---|---|---|
| **Phase 21** | **[`PHASE21_T90_45_MULTI_PORTAL_2026_09_14`](./PHASE21_T90_45_MULTI_PORTAL_2026_09_14.md)** | **T90.45 Cloud-9 mode σ/m(28)=42; KSFR/DAMPE/XRISM still FAIL** |
| **Phase 22** | **[`PHASE22_REVIEWER_DRIVEN_REFIT_2026_09_14`](./PHASE22_REVIEWER_DRIVEN_REFIT_2026_09_14.md)** | **Reviewer fixes: KSFR N/A + asymmetric DM + median mode → 6→2 failures** |
| **Phase 23-25** | **[`PHASE23_24_25_TENSION_DIAGNOSTICS_2026_09_14`](./PHASE23_24_25_TENSION_DIAGNOSTICS_2026_09_14.md)** | **Cloud-9 RESOLVED (wrapper fix); SPARC + Euclid subhalo are real structural conflicts** |

---

## 📊 Data files

All results are in `v0.3-prelim/data/results/`:

- T90 joint posteriors: `t90_v45_*.json`, `t90_v51_*.json`, `t90_v52_*.json`, `t90_v55-57_*.json`, `t90_v63_*.json`
- T90.58 ablation: `t90_v58_ablation_*.json` (6 subsets)
- Phase 20-21: `phase20_full_space_conditions.json`, `phase21_t90_45_multi_portal.json`

---

## 🏃 Quick reproduction

```bash
# Clone
git clone https://github.com/chenhk1113-HK/sidm-composite-dm-mediator.git
cd sidm-composite-dm-mediator
git checkout t90-grand-unified-v63-2026-09-14

# Run all T90 + Phase 11-21 tests
cd v0.3-prelim
python -m pytest tests/test_phase11_majorana_freeze_out.py \
  tests/test_phase12_sigma_m_drop_mystery.py \
  tests/test_phase13_mediator_mass_survey.py \
  tests/test_phase14_mphi_comparison.py \
  tests/test_phase15_16_17_probes.py \
  tests/test_phase18_mchi_comparison.py \
  tests/test_phase19_full_fit_mchi_5GeV.py \
  tests/test_phase20_full_space_conditions.py \
  tests/test_phase21_t90_45_multi_portal.py -v

# Expected: 49 passed
```

---

## 📋 Honest scope statement

This branch is **NOT** a complete dark matter solution. It is:

1. ✓ A unified SIDM model that satisfies 5 σ/m + LZ + KSFR channels simultaneously (Cloud-9, Galactic, Bullet, LZ magnetic moment, KSFR box)
2. ✗ Fails 6/20 channels in full space-conditions test (KSFR/PCAC, DAMPE, XRISM, eROSITA, Euclid subhalo, SPARC saturated proxy)
3. ✗ Indirect detection failures are model-independent (any dark photon at this mass would fail)
4. ✗ KSFR/PCAC is a hard theoretical constraint violation
5. ✓ Substantial progress over single-portal v0.3-prelim (which fails Cloud-9)
6. ✗ Not a unique determination — resonant (V50) and multi-portal (V45) also satisfy the 5 channels

For complete reproduction details, see [`T90_PATH_C4_ALL_FINDINGS_REFERENCE.md`](./T90_PATH_C4_ALL_FINDINGS_REFERENCE.md).
