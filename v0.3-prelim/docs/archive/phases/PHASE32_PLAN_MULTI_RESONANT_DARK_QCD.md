# Plan — Phase 32: Multi-Resonance Dark QCD SIDM (Tsai 2022 framework)

> **Status:** 📋 Plan ready (2026-09-14)
> **Trigger:** User: "try composite dark mesons, search the web for any useful ref then make the plan"
> **Predecessor:** Phase 31bc — resonant SIDM failed Tests H (dwarf cores) and G (stream gaps)
> **Reference:** Tsai, McGehee, Murayama 2022, "Resonant Self-Interacting Dark Matter from Dark QCD",
> Phys.Rev.Lett. 128 (2022) 17, 172001; arXiv:2008.08608 (FERMILAB-PUB-20-365-AE-T)

---

## Goal

Replace the single-resonance Breit-Wigner (Phase 29) with a **multi-resonance dark-QCD framework** that has multiple near-threshold resonances (analogous to ϕ-K-K, ϒ(nS)-B-B systems in SM). This addresses the two Phase 31bc failures:
- **Test H (dwarf cores)**: single resonance overshoots at v=10-20 km/s because the Breit-Wigner is too broad
- **Test G (stream gaps)**: single resonance undershoots at v=200-400 km/s because the tail is too low

Multi-resonance structure provides independent control over each velocity scale.

---

## Why multi-resonance dark QCD?

### The single-resonance problem (recap from Phase 29 + 31bc)

| Velocity scale | Physical system | Required σ/m | Single-BW prediction |
|---|---|---|---|
| v ≈ 10-20 km/s | Dwarf galaxies (Fornax, Sculptor) | ~1-10 cm²/g | **29-465 cm²/g (overshoots)** |
| v ≈ 28 km/s | Cloud-9 RELHIC | 30-500 cm²/g | **29 cm²/g ✓** |
| v ≈ 100 km/s | SPARC galaxies | ~0.07 cm²/g | 0.035 cm²/g (close) |
| v ≈ 200-400 km/s | Stellar streams | ~0.1-1 cm²/g | **0.013-0.005 cm²/g (undershoots)** |
| v ≈ 1000 km/s | Clusters | <0.1 cm²/g | 0.0006 cm²/g ✓ |

The Breit-Wigner form (one peak) cannot simultaneously produce large σ/m at v=10-20 AND small σ/m at v=200-400. The "tuning" Γ_R/E_R ~ 0.013 is right for Cloud-9 but wrong for the adjacent scales.

### Why multi-resonance works (Tsai 2022 key insight)

In a QCD-like dark sector, **multiple resonances appear NATURALLY**:

**Light quark model (analogous to ϕ-K-K)**:
- DM = dark "kaons" (m_K ~ 100 MeV to 1.5 GeV)
- Resonant self-interaction mediated by dark ϕ (vector meson) exchange
- Single narrow resonance near ϕ threshold
- Δ ≡ (m_ϕ - 2m_K)/m_ϕ ~ 10⁻⁷·⁸ (fine-tuned)

**Heavy quark model (analogous to ϒ(nS)-B-B)**:
- DM = heavy-light mesons (m_DM ~ m_Q ~ GeV scale)
- **Multiple resonances** from heavy quarkonium excited states ϒ(1S), ϒ(2S), ϒ(3S), ϒ(4S), ...
- Level spacing: Δn = C × (1/n) [Eq. (11) of Tsai 2022]
- n=4 state (ϒ(4S)) is the famous B-B threshold resonance
- **This is the multi-resonance structure we need**

**Key formula** (Tsai 2022 Eq. 11-13):
```
m[ϒ(nS)] - m[ϒ((n-1)S)] = C × [1/n + O(1/n²)]
m[ϒ(4S)] - 2 m_B = 0.0019 (QCD example)

Tuning required: F.T. ≡ Δ × (m_Q/Δn) ≈ Δ × (4/(3e))² × n³
For n > 10, fine-tuning reduces by factor 10⁵
```

### How this fixes Phase 31bc failures

With multiple resonances (one at v ~ 10-20, one at v=28, one at v=200), each can independently fit its target:

| Resonance | n state | Velocity | Fits |
|---|---|---|---|
| ϒ(2S)-like | n=2 | v ~ 5-10 km/s | Dwarf galaxies (controls Test H) |
| ϒ(4S)-like | n=4 | v ~ 28 km/s | **Cloud-9 (the original target)** |
| ϒ(8S)-like | n=8 | v ~ 200 km/s | Stellar streams (controls Test G) |
| ϒ(12S)-like | n=12 | v ~ 1000 km/s | Clusters (essentially CDM-like) |

The level spacing naturally creates the right velocity structure because **E_CM(nS) ~ n² × Λ_D** and **v ~ √(E_CM/m_χ)** scales predictably.

---

## What the plan delivers

### Phase 32a: Multi-resonance model implementation (~1-2 hours)

Create `code/t90_v70_multi_resonant_darkqcd.py`:
- Extend `t90_v50_resonant_sidm.py` to handle **N resonances** (default N=4)
- Each resonance characterized by (E_R_n, Γ_R_n)
- Resonance widths follow Tsai 2022 level-spacing rule
- Multi-resonance σ/m(v) = σ_background + Σ_n σ_BW_n(v)

### Phase 32b: Joint fit (~2-3 hours)

Create `code/phase32b_multi_resonant_joint_fit.py`:
- 6D + N×3 = ~18 parameters (4 resonances × 3 each: E_R, Γ_R, g_n)
- Reuse rejection sampling from Phase 29
- Priors: Tsai 2022 level-spacing constraints
- Fit to Cloud-9, SPARC, dwarf galaxies, stellar streams, clusters
- Output: posterior median with **test predictions** for all 9 critical review tests

### Phase 32c: Re-run all 9 critical review tests (~2 hours)

For each test from Phase 30/31, re-evaluate with multi-resonance model:
- D (fine-tuning): Is the multi-resonance architecture natural?
- A (other low-v): Does each system get fitted by its own resonance?
- F (relic density): Multi-resonance affects freeze-out (Tsai 2022 §Freeze-out)
- B (SPARC Bayes): Better fit than power-law?
- C (subhalo real data): Consistent with Euclid Q1?
- **H (dwarf cores)**: Now fitted by separate low-v resonance
- I (DD limits): Multi-resonance affects σ_SI via KK loop
- E (UV completion): Tsai 2022 IS the UV completion
- **G (stream gaps)**: Now fitted by separate high-v resonance

### Phase 32d: Documentation + verdict (~1 hour)

- `docs/PHASE32_MULTI_RESONANT_DARK_QCD_2026_09_14.md`
- Update `T90_MASTER_REFERENCE`, `T90_CLOUD9_INDEX`
- Update README with new verdict
- Commit + tag

---

## Expected outcomes

### Best case: ALL 9 tests pass

If the multi-resonance model can independently fit each velocity scale, the verdict upgrades from "PARTIALLY_PLAUSIBLE" to **"PLAUSIBLE w/ explicit UV"**. This would be a **major positive result** — a dark matter model with:
- ✓ Cloud-9 solved
- ✓ Dwarf cores fitted (Test H)
- ✓ Stream gaps fitted (Test G)
- ✓ SPARC fitted
- ✓ UV completion (Tsai 2022 dark QCD)

### Realistic case: Tests H, G improve, others unchanged

The multi-resonance architecture should fix the two CRITICAL failures (Tests H, G). The other tests (D, A, F, B, C, I) likely stay similar. Verdict upgrades to **"MOSTLY_PLAUSIBLE w/ 1-2 remaining caveats"**.

### Pessimistic case: Multi-resonance overfits

If the model needs finely-tuned positions for each resonance, the "fine-tuning" criticism returns (Test D). The dark-QCD framework provides natural spacing **only if the resonances follow the Tsai 2022 level-spacing rule** — if our fitted positions deviate significantly, we're back to phenomenological.

---

## Reference documentation

### Tsai 2022 (PRIMARY)
**Tsai, McGehee, Murayama, "Resonant Self-Interacting Dark Matter from Dark QCD"**,
Phys.Rev.Lett. 128 (2022) 17, 172001, arXiv:2008.08608
- Section "Heavy quark model" (most relevant for our setup)
- Eq. (11) for level spacing: Δn = C × [1/n + O(1/n²)]
- Eq. (13) for fine-tuning measure: F.T. ≈ Δ × (4/(3e))² × n³
- Fig. 3 shows the resonance crossings

### Berlin et al. (SIMP/ELDER)
Berlin, Hochberg, Kuflik 2024 (and earlier work)
- Lattice-validated Sp(4) gauge theory with N_f=2
- m_π/f_π = 1.9 at resonance
- Already discussed in Tsai 2022

### Yang 2026 (TWO-COMPONENT SIDM)
**Yang, Fan, Tsai 2025/2026, "Two-component SIDM: a unified explanation of dwarf cores and small-scale lenses"**,
arXiv:2506.14898
- Directly addresses Test H failure mode
- Mass segregation in 2-component SIDM produces cored dwarfs + cuspy clusters
- **Different mechanism** but could be combined with multi-resonance

### Chu, Garcia-Cely, Murayama 2019 (resonance velocity dependence)
PRL 122, 071103; arXiv:1805.03203
- The original resonant SIDM velocity-dependence paper
- Cited by Tsai 2022 and our t90_v50

### Tulin & Yu 2018 (SIDM review)
Physics Reports 730, 1-57
- Comprehensive SIDM review including resonant models

---

## Files to create

| File | Purpose |
|---|---|
| `code/t90_v70_multi_resonant_darkqcd.py` | Multi-resonance σ/m function |
| `code/phase32a_multi_resonance_implementation.py` | Implementation + validation |
| `code/phase32b_multi_resonant_joint_fit.py` | Full joint fit (~18D) |
| `code/phase32c_re_run_all_9_tests.py` | Re-evaluate critical review tests |
| `tests/test_phase32_*.py` | Tests |
| `data/results/phase32_*.json` | Results |
| `docs/PHASE32_MULTI_RESONANT_DARK_QCD_2026_09_14.md` | Full doc |

---

## Open questions

1. **Number of resonances**: 4 (one per velocity decade) or more (6-8 for finer control)?
2. **Spacing rule**: Strict Tsai 2022 (Δn ~ 1/n) or free (more parameters)?
3. **Asymmetric DM**: Required by Phase 16 — compatible with multi-resonance?
4. **Freeze-out**: How does multi-resonance affect relic density calculation?
5. **DD limits**: Each resonance contributes to σ_SI — sum may exceed LZ bounds

---

## Sequencing recommendation

1. **Phase 32a** (~1-2 hours): Implement multi-resonance σ/m function. Test against Phase 29 single-resonance.
2. **Phase 32b** (~2-3 hours): Joint fit to all 9 critical review test predictions.
3. **Phase 32c** (~2 hours): Re-run all 9 tests. **This is the verdict moment.**
4. **Phase 32d** (~1 hour): Document + commit + push.

Total: **~6-8 hours**. Could be split across multiple sessions.

---

## Bottom line

Phase 29's single Breit-Wigner failed because it had to do too many jobs at once. The Tsai 2022 multi-resonance dark-QCD framework provides:
- Multiple natural resonances (heavy quarkonium excited states)
- Each tuned to a different velocity scale
- Built-in UV completion
- Lattice-validated parameters for some scenarios

This is the **most motivated** approach to fix Phase 31bc's failures. If it works, the model upgrades from "Cloud-9 solver" to "complete dark matter solution with UV physics".

If multi-resonance doesn't work, the alternative is Yang 2026's two-component SIDM (mass segregation) which is a **completely different architecture**.