# Phase 34a — JVAS B1938+666 Lensing Test

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** User uploaded halo1.docx with TWO arxiv papers
> **Papers**:
>   1. **arXiv:2603.19362** (Klemmer+ 2026) — SIDM subhalo evolution
>   2. **arXiv:2606.12909** — JVAS B1938+666 lensing perturber (SIDM core collapse)
> **Verdict:** **🎯 JVAS_FAIL — model is 84× TOO LOW for JVAS-like core collapse**

---

## 🎯 THE BIG RESULT

Paper 2 (arXiv:2606.12909) interprets a recent lensing observation (10⁶ M⊙ perturber at JVAS B1938+666) as a **deeply core-collapsed SIDM halo**. They require:

- σ/m ~ **100 cm²/g** at v ~ 15 km/s
- Progenitor: M_200 = 1.5×10⁸ M_sun, c_200 = 50
- The collapsed halo develops a secondary dense core (3×10⁵ M_sun within 10 pc) inside an extended envelope

**Our model gives σ/m(15) = 1.19 cm²/g** — a **factor of 84 too low**.

**Estimated core-collapse timescale**: 68 Gyr (5× the age of the universe). JVAS-like perturbers **CANNOT** form via deep core collapse in our model.

---

## Method

1. Load Phase 32b posterior median (m_chi=6.58 GeV, σ_0_dwarf=0.195, a_slope=0.869, v_targets=[27.9, 54.8, 272, 978])
2. Evaluate σ/m(v) at 8 test velocities (10, 12, 15, 20, 28, 50, 100, 200 km/s)
3. Compare to Paper 2's requirement σ/m(15) ~ 100 cm²/g
4. Estimate core-collapse timescale using Balberg+ 2002 / Paper 2 Eq. 3

---

## Results

### σ/m(v) profile

| v (km/s) | σ/m (cm²/g) | Regime |
|---|---|---|
| 10 | 1.56 | Dwarfs |
| 12 | 1.37 | Dwarfs |
| **15** | **1.19** | **<-- JVAS regime** |
| 20 | 1.17 | Dwarfs |
| 28 | **93.3** | **(Cloud-9)** |
| 50 | 0.38 | SPARC regime |
| 100 | 0.20 | SPARC regime |
| 200 | 0.11 | Stream regime |

### Key test

| Quantity | Value |
|---|---|
| Paper 2 required σ/m(15) | 100 cm²/g |
| Our model σ/m(15) | 1.19 cm²/g |
| Ratio | 0.0119 |
| **Deficit** | **83.9× TOO LOW** |

### Core-collapse timescale

- t_c ≈ 68 Gyr
- Hubble time: 13.8 Gyr
- **t_c / t_Hubble ≈ 5**: Core collapse would take 5× the age of the universe
- **JVAS B1938+666 perturbers cannot form via this mechanism in our model**

---

## Verdict

**JVAS_FAIL** — Model is 84× too low for JVAS-like core collapse.

---

## Implications

### What this means

If JVAS B1938+666's interpretation is correct:
- SIDM at v=15 km/s MUST have σ/m ~ 100 cm²/g
- Our model gives 1.19 cm²/g there
- **Our model CANNOT explain JVAS-like perturbers**

If JVAS B1938+666 is NOT representative:
- Most SIDM lenses may have higher concentration progenitors (c > 80)
- σ/m ~ 1-10 cm²/g could suffice for core collapse with extreme concentration
- Model could still be viable for OTHER lensing tests (different mass scale, different redshift)

### What's the path forward?

To make the model consistent with Paper 2:

| Option | Effect |
|---|---|
| Widen R1 resonance (Cloud-9) | Would over-shoot dwarfs (σ/m(10) would also be 100) |
| Add R0 resonance at v=10-15 | Would shift Cloud-9 resonance, breaking the original target |
| Increase σ_0_dwarf to ~80 cm²/g | Would break dwarf core tests (currently 1-2 cm²/g needed) |
| **Accept that model cannot explain JVAS** | Honest — model explains Cloud-9+SPARC but NOT JVAS |

The cleanest path is **honest**: state that the model explains a specific subset of observations (Cloud-9, SPARC) but not others (lensing anomalies).

---

## Comparison with previous phases

| Phase | σ/m(15) | Pass? |
|---|---|---|
| Phase 31a-c (single-BW) | 200-900 cm²/g | FAIL (overshoot dwarfs) |
| **Phase 32bc (multi-BW + bg)** | **1.19 cm²/g** | **PASS internal tests, but FAIL JVAS** |
| Required for JVAS (Paper 2) | 100 cm²/g | — |

The multi-resonance architecture SOLVED the dwarf-overshoot problem but at the cost of **also losing the core-collapse regime** at v=15.

---

## Files shipped

- `code/phase34a_jvas_lensing_test.py` (~230 lines)
- `data/results/phase34a_jvas_lensing_test.json`
- `tests/test_phase34a_jvas_lensing.py` — 5/5 PASS

**135/135 tests pass** across 24 phases, 35 sub-tasks.

---

## Bottom line

The JVAS B1938+666 lensing test is a **specific, falsifiable, discriminating test** that our model fails by 84×. Unlike the SPARC probe (which tests a wide band), this test targets a specific velocity (v=15) requiring a specific σ/m value (~100).

This is the most decisive **external falsification** of the model since the project began. The verdict:
- ✓ Cloud-9 (v=28, σ/m=100): works
- ✓ SPARC (v=80-150, σ/m=0.05-0.2): works
- ✗ JVAS B1938+666 (v=15, σ/m=100): **FAILS**

The model is **viable for SOME observational probes** but **not a complete dark matter solution**.

---

## Recommended next steps

1. **Add JVAS B1938+666 as a permanent test** in the test suite
2. **Update README** with the JVAS_FAIL verdict
3. **Decide**: retune model (would break other tests) or accept partial solution
4. **Document** this as a "scope limitation": model fits Cloud-9/SPARC/subhalos but not lensing anomalies

Want me to update the README + master doc to reflect this new finding?