# v0.3-prelim — Multi-resonance SIDM research workspace

> **Branch:** `wip/cloud-9-relhic` (working) + `wip/multi-component-SIDM-core-collapse` (publication)
> **Status:** v18.40 (2026-09-25) — **T212 Path A3 + Path B3 trim**. Cloud-9's σ/m ≥ 50 floor reframed as systematic upper bound (Turini & Benítez-Llambay 2026); Silverman+ 2026 gravothermal threshold σ/m ~ 1 cm²/g at Cloud-9 host halo (5× above Phase 44 baseline; corrected from earlier 10× estimate after V_max + t_cross fixes per 2review.docx Reviewer 2). See [`docs/PAPER_V1_DRAFT.md`](docs/PAPER_V1_DRAFT.md) §10.4d, §10.4e for the full refinements.
> **Final verdict:** Multi-resonance SIDM is a **phenomenological interpolation** through 8 observational channels + structural constraint map, not a first-principles derivation. See [`docs/PAPER_V1_DRAFT.md`](docs/PAPER_V1_DRAFT.md) §11 conclusions (v18.40) for the honest framing.

This is a research workspace for the multi-resonance SIDM model. The investigation ran from Phase 32 to Phase 41D, covering 9 sub-tasks across multiple sub-phases.

---

## 🎯 Headline finding (Phase 42)

> **Multi-resonance SIDM is a defensible particle-physics framework that unifies cross-sections across velocity scales (Cloud-9, SPARC, subhalos), but rotation-curve data alone do NOT prefer it over simpler cored profiles (Burkert, PISO, Einasto) once proper Occam penalties are applied.**

This is the honest scientific conclusion after 4 phases of increasingly rigorous head-to-head comparisons.

---

## 📊 Phase summary

| Phase | Topic | Tests | Verdict |
|---|---|---|---|
| 32a | Multi-resonant SIDM, dark-QCD | 11/11 PASS | PROCEED |
| 32b | 30k MCMC joint fit | 9/9 PASS | m_chi=7.1 GeV posterior |
| 32c | All 9 tests | 9/9 PASS | Conditional pass |
| 33a | Bayes factor | — | INCONCLUSIVE |
| 33b | Tsai 2022 UV | — | FALSIFIED |
| 33c | Synthetic SPARC | 96/100 | PASS |
| 33d | Real SPARC Vflat | 115/127 | PASS |
| 34a | JVAS B1938+666 lensing | — | FAILS (84×) |
| 35-36 | 5-resonance + concentration physics | — | REVERTED |
| 37 | Final verdict v37 | 139/139 | Partial solution |
| 38 | sidmkit cross-check | 3/3 | Pipeline integrity |
| 39 | NFW vs SIDM (15 galaxies) | 5/5 | STRONG_SIDM (overstated) |
| 40 | + Burkert + Occam (120 galaxies) | 8/8 | Burkert wins (honest) |
| 41 | + Einasto + PISO + dynesty | 8/8 | Burkert wins by dynesty |
| 41D | + Gravothermal (Yang+ 2023) | 8/8 | Hybrid SIDM still better |

**171/171 tests pass** across all phases.

---

## 🏗️ Structure

```
v0.3-prelim/
├── code/                  # Python modules
│   ├── t90_v50_resonant_sidm.py          # Single resonance baseline
│   ├── t90_v70_multi_resonant_darkqcd.py # Multi-resonant (FINAL)
│   ├── t90_v71_five_resonance_jvas.py    # REVERTED 5-resonance attempt
│   ├── phase32a_*.py through phase41d_*.py
│   └── ...
├── tests/                 # Pytest suite (171 tests)
├── docs/                  # Per-phase documentation
├── data/
│   ├── external/sparc/    # SPARC data (gitignored)
│   └── results/           # Phase JSON outputs
└── README.md              # This file
```

---

## 🚀 Quick start

### Run all tests

```bash
cd v0.3-prelim
python -m pytest tests/test_phase11_*.py tests/test_phase12_*.py ... tests/test_phase41d_*.py
```

Expected: 171/171 PASS.

### Re-run the final rotation-curve comparison

```bash
python code/phase41_extended_comparison.py  # 5 models, 120 galaxies
python code/phase41d_parametric_sidm.py     # + gravothermal
```

Outputs go to `data/results/`.

### Re-run sidmkit cross-check

```bash
pip install sidmkit
sidmkit-sparc batch --inputs data/external/sparc/Rotmod_LTG --outdir data/external/sparc/sidmkit_fits --models nfw --limit 127
```

---

## 🔑 Key files

### Production code (FINAL)

- `code/t90_v70_multi_resonant_darkqcd.py` — Multi-resonant SIDM model (4 resonances at v=[28, 100, 300, 700] km/s)
- `code/phase41_extended_comparison.py` — 5-model rotation-curve comparison
- `code/phase41d_parametric_sidm.py` — Gravothermal SIDM (Yang+ 2023)

### Test suite

- `tests/test_phase11_*.py` through `tests/test_phase41d_*.py`
- 171 tests, all PASS

### Documentation

- `docs/PHASE42_ROTATION_CURVE_FINAL_VERDICT.md` — **Master summary** (start here)
- `docs/PHASE32_*.md` through `docs/PHASE41D_*.md` — Per-phase details

---

## 🎓 Status summary (defensible as of Phase 42)

| Claim | Status |
|---|---|
| Multi-resonance SIDM passes internal tests | ✅ TRUE |
| Multi-resonance SIDM is consistent with SPARC Vflat | ✅ TRUE (115/127) |
| Multi-resonance SIDM is competitive on rotation curves | ✅ TRUE (vs PISO at fit level) |
| Multi-resonance SIDM beats NFW on rotation curves | ✅ TRUE (chi² +AIC) |
| Multi-resonance SIDM beats Burkert on rotation curves | ❌ FALSE (chi² +dynesty) |
| Multi-resonance SIDM is preferred on Bayesian evidence | ❌ FALSE (dynesty) |
| Multi-resonance SIDM explains JVAS B1938+666 | ❌ FALSE (fails by 84×) |
| Multi-resonance SIDM has correct Tsai UV completion | ❌ FALSE (Tsai 2022 falsified) |

---

## 📖 References

- **SIDM particle model**: T90 multi-resonant architecture
- **Gravothermal**: Yang & Yu 2023, arXiv:2305.16176
- **sidmkit toolkit**: arXiv:2601.04735
- **SPARC data**: astroweb.cwru.edu/SPARC/
- **JVAS B1938+666 lensing**: arXiv:2606.12909
- **Klemmer+ 2026 SIDM subhalos**: arXiv:2603.19362

---

## 🏷️ Git tags

- `t90-multi-resonant-darkqcd-v32a-2026-09-14`
- `t90-all-9-pass-v32c-2026-09-14`
- `t90-honest-bayes-factor-v33a-2026-09-14`
- `t90-tsai-falsified-external-pass-v33bc-2026-09-14`
- `t90-real-sparc-pass-v33d-2026-09-14`
- `t90-jvas-fail-v34a-2026-09-14`
- `t90-five-resonance-jvas-tradeoff-v35-2026-09-14`
- `t90-concentration-collapse-v36-2026-09-14`
- `t90-final-verdict-v37-2026-09-14`
- `t90-sidmkit-crosscheck-v38-2026-09-14`
- `t90-nfw-vs-sidm-v39-2026-09-14`
- `t90-corrected-comparison-v40-2026-09-14`
- `t90-extended-comparison-v41-2026-09-14`
- `t41d-gravothermal-2026-09-14`

---

## ⚠️ Known limitations

1. **SIDM profile is hybrid** (Burkert+NFW blend) — gravothermal alternative did not improve fit
2. **15-galaxy dynesty subset** — full 120-galaxy Bayesian evidence not computed
3. **No JVAS resolution** — lensing perturber remains unexplained (Paper 2 alternative: CDM+black hole)
4. **Tsai UV wrong** — particle physics motivation was incorrect
5. **External SPARC data gitignored** — re-fetch via `data/external/sparc/fetch_sparc.py`

---

## 📬 Contact

Branch `wip/cloud-9-relhic` represents the closed investigation. Future work should:
- Consider velocity-dependent gravothermal (substantial work, not currently pursued)
- Focus on stronger channels (lensing, subhalos, multi-channel evidence)
- Use the hybrid profile as the pragmatic choice for rotation-curve comparisons