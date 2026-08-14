# sidm-composite-dm-mediator

**Composite dark matter with a secluded mediator** — Bayesian constraint pipeline for self-interacting dark matter (SIDM) cross-sections, with a feasibility survey of mediator detection.

Renamed from `dm-sidm-pipeline` on 2026-08-14 to reflect the two workstreams that define this project: composite-DM microphysics (dark glueballs, dark rho, dark baryons) and mediator-detection feasibility (T40–T76).

This codebase was originally forked from the WIMpy Bayesian methodology (dynesty nested sampling + BIC + BMA), adapted from dark-energy macro-evolution to dark-matter microphysics. See `PLAN_v0.1.md` for the original motivation.

SIDM (self-interacting dark matter) cross-section constraint pipeline.

## Status

**v0.3-prelim-D10 shipped — Tier-3 publication work (T3.1 + T3.2 + T3.3 complete)** — T30 (LZ real posterior ingested, 26 mass points from HEPData 155182), T31 (halo-mass marginalization: dwarf fails due to KiSS-SIDM N=1e4 limitation), T32 (Fermi dwarf channel from 4FGL-DR4 14-year data, strongly constrains σ/m under WIMP coupling). 261/263 tests pass.

**Three Tier-3 items complete:**
- **T3.1 (T30)**: Real LZ WS2024 ingested from HEPData 155182 (26 mass points). Placeholder was lossy; real LZ strongly constrains σ/m at m_chi=40 GeV.
- **T3.2 (T31)**: Halo-mass marginalization attempted but dwarf KiSS-SIDM run fails (N=1e4 too small for 10⁸ M_sun halo at σ_m=5 cm²/g). Canonical penalty should be used as upper bound.
- **T3.3 (T32)**: Fermi dwarf galaxy channel from 4FGL-DR4 (21 sources, Hooper & Linden 2024 limits) added. **KEY PHYSICS RESULT:** combined LZ + Fermi + T8 channels strongly constrain σ/m at m_chi=40-50 GeV under standard WIMP coupling. **Either the SIDM mediator must decouple from thermal-WIMP expectations, or SIDM is excluded at standard coupling.**

**Tier 3 completed (D8):**
- **T3.4 (T29):** β_seg fitted — data prefers β_seg = 0.899 (NOT 0.25 hardcoded). 2-comp-vs-1-comp BF unchanged, but absolute σ1, σ2 differ.
- **T3.5 (MATHEMATICS.md):** 250+ line math appendix with all derivations.
- **T3.6 (TUTORIAL.md):** 300+ line end-to-end guide for new developers.

**Open Tier-3 items (deferred to v0.4):**
- T3.1: Replace Gaussian placeholders with raw posterior chains (~1-2 weeks/channel)
- T3.2: Halo-mass marginalization
- T3.3: Fermi + N-body channels

**Tier 1 (T26):** T21 width sensitivity with KISS-SIDM penalty — **dampens by 5×** (Δ log σ/m = +0.198 vs T24's -1.006). Headline σ/m is moderately robust to width choice because KISS is doing real physics work.

**Tier 2 (T27):** Multi-resolution KISS-SIDM (N=500, 1e4, 1e5) — r_core/r_s **identical** at N=1e4 and N=1e5. Gravothermal penalty converged at N=1e4.

**Tier 3 (T28):** Published-style non-Gaussian dSph channel — MAP log σ/m **unchanged** (Δ < 0.01 dex) while log Z improves by +0.7. Headline is robust to posterior shape choice.

**Implication for D5 headline:** the D6 finding that "headline could shift by factor of 10 if widths are off" was the WORST case (no gravothermal anchor). With the real KISS-SIDM penalty as anchor, the headline σ/m = 1-3 cm²/g is **moderately robust** to width uncertainty. Publication work (replacing Gaussian placeholders with raw posterior chains) will refine log Z values but is NOT expected to relocate the MAP.

**Tier 1 quick wins (shipped):**
- requirements.txt (pinned numpy 2.4.6, scipy 1.18.0, dynesty 3.0.0)
- kiss_sidm_julia_bridge.py /tmp cleanup (try/finally wrapper)
- Split-brain fix: config.py copied to Windows side; 7 regression tests

**Tier 2 systematics (shipped):**
- T24 (likelihood-width sensitivity): **MAJOR** shift — Δ log σ/m = -1.006 dex (factor of 10) when widths change by 2x
- T25 (c_vir marginalization): MINOR shift — Δ log σ/m = -0.193 dex
- T9 prior variation (lifted into FINDINGS): MAP log σ/m varies 0.77 dex across 4 prior choices
- T2.1 unit conversion tests (16 tests): Newton's G, cm²/g conversion, Knudsen number, sigma-v law, mass segregation

**Implication for the D5 headline:** σ/m = 1.4-1.7 cm²/g (T21 with real KISS-SIDM) is correct **only if** the likelihood widths are correctly calibrated. T24 shows the headline could shift by a factor of 10 if the widths are off by ±0.3 dex. **For publication: replace Gaussian proxies with raw posterior chains (T3.1 from R2 review).**

**Honest scope:** the 0.5x narrower case gives log Z = -64.62, so the data strongly prefers widths around the default — but the absolute σ/m depends on the width by ~1 dex.

**Key finding 1 (T22):** the placeholder was right about 2-comp NOT being
preferred. Δ(log Z, 2-comp vs 1-comp) = +0.48 (T22) vs +0.57 (T19 placeholder).

**Key finding 2 (T23):** with REAL KISS-SIDM, the IMFP correction no longer
matters (Δ = -0.04 vs placeholder -1.46). The placeholder T20 conclusion that
IMFP correction disfavors 2-comp was an artifact of the over-strong
gravothermal penalty.

**Key finding:** the placeholder gravothermal model was over-penalizing
the fit by 0.7 log Z units. With the REAL KISS-SIDM, the headline
σ/m shifts from ~1.0 (placeholder) to **~1.4-1.7 cm²/g (T21)**.

- Direction A: SASHIMI-SIDM in-house port (shipped 2026-08-10, msg 38460).
- Direction B: two-component (mass-segregated) SIDM (T18 placeholder, T19 real, T20 KISS-SIDM-corrected).
- Direction C: KISS-SIDM fit correction (shipped 2026-08-11 in v0.3-prelim-D).
- Direction 1: KISS-SIDM corrected 5-channel fit (T17 placeholder, T21 real KISS-SIDM).
- Direction 2: pure-Python KISS-SIDM DSMC simulator (v0.3-prelim-D2) + real KISS-SIDM Julia integration (v0.3-prelim-D4).
- Direction 3: combined T19 (Yang+ 2026 real curve) + T20 (KISS-SIDM × 2-comp).
- Julia install: ✅ DONE in v0.3-prelim-D4 (Julia 1.11.5 + 348 packages at `/home/lamkuenai/.juliaup/bin/`).

## Project layout

```
C:\Users\lamkuenai\projects\dm-sidm-pipeline\
├── README.md          ← this file
└── PLAN_v0.1.md       ← 13.5 KB feasibility plan
```

(Folders `code/`, `data/`, `docs/`, `plots/`, `logs/`, `notes/` will
be created at v0.1-prelim time, once Phase 1 begins.)

## Background

The motivation for this project came from a dark-glueball.info doc
uploaded 2026-08-10 (saved at
`C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_40787cdd0b55_dark glueball.docx`).
The doc proposed dark glueballs as a dark-matter candidate that
naturally produces SIDM-like self-interactions (3-to-2 cannibalism
in the early universe). The feasibility analysis concluded:

- Dark glueballs are a **dark-matter** question, not a **dark-energy**
  question → fits a NEW pipeline, not WIMpy extension.
- The WIMpy methodology (dynesty nested sampling + BIC + BMA +
  Welch t-test + mock-data validation) transfers 1:1 to dark-matter
  model comparison.
- 4 channels of evidence (rotation curves, dwarf cores, CMB,
  lensing) — the first 2 are scope-feasible, CMB is blocked on
  full Planck clik, lensing is a 6-month effort on its own.

## Relationship to other projects

| Project | Path | Relationship |
|---|---|---|
| WIMpy (cosmology) | `C:\Users\lamkuenai\projects\wimpy\` | Sister project — shares methodology |
| FUSE MAST-U | `C:\Users\lamkuenai\projects\fuse-mast-u-patch-loop\` | Unrelated (fusion, not cosmology) |
| FUSE sandbox | `C:\Users\lamkuenai\projects\fuse-sandbox-nt\` | Unrelated (fusion active repo) |
| SmolVLA | `C:\Users\lamkuenai\smolvla-libero-v7-full\` | Unrelated (robotics, not cosmology) |

## Methodology reuse from WIMpy

- **Python venv**: `/home/lamkuenai/wimpy/bin/python` (WSL) — already
  has dynesty + numpy + scipy. **Do NOT create new venv** unless
  hitting a missing-package wall.
- **Aggregator pattern**: copy `wimpy_results/scripts/test33_model_averaging.py`
  and adapt JSON schema.
- **PDF + ZIP ship pattern**: copy `wimpy_results/scripts/build_*.py`
  pattern, adapt cover for SIDM numbers.
- **Project-doc structure**: same `code/data/docs/plots/logs/notes/`
  convention (per project-doc structure rule).

## Next steps

Pending user authorization to start Phase 1 (T1-T3, SPARC single-galaxy
+ joint fits). Estimated 2-4 weeks.

## Update history

- 2026-08-10 — Project folder created. PLAN_v0.1.md authored from
  dark-glueball.docx feasibility analysis.