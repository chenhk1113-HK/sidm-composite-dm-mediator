# T90 Branch Findings — Layman Summary

**Branch:** `wip/tier3-magnetic-moment-LZ` (off master)
**Date:** 2026-09-07
**Round:** T90 — Tier-3 branch experiment
**Lead doc:** [`T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md`](./T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md)

---

## Headline

**Yes — our Benchmark A model can reproduce the LZ 248 keV event** if we add one extra knob: a magnetic-moment Ls₁₀ operator at μ_x ≈ 6.10×10⁻⁸ μ_N (= 3.32×10⁻¹¹ μ_B). With that knob, our model predicts ~1 event at 248 keV in 2.84 tonne-years, matching LZ's observed single event.

The branch is **not excluded by any published limit**. We're at ~7,500× below the LZ 2026 90% CL upper limit, and ~1.3 million× below at the data's preferred coupling.

The catch: **the coupling is a knob we set, not a number the data picked out.** The data don't require this channel — they merely permit it.

---

## What we did in T90

1. **Added a magnetic-moment EFT operator** (Ls₁₀) to the LZ likelihood, using WIMpy_NREFT's `dRdE_magnetic` spectrum.
2. **Tested it in 27 unit tests** — all passing.
3. **Ran a 6D Bayesian fit** with the operator turned on. Result: data fit roughly the same with or without the operator (Δlog Z ≈ 0 — the data don't need it).
4. **Ran a 7D fit** that lets the coupling float freely. Result: data prefer a coupling ~100× smaller than our hand-tuned value (3×10⁻¹⁰ μ_N vs 6×10⁻⁸ μ_N).
5. **Checked against published limits** (PandaX-4T, LZ 2026). Comfortable margin.
6. **Did the precise d_10 ↔ μ_x mapping** (Phase 8): turns out the LZ 2026 limit at d_10 ≈ 0.1 corresponds to μ_x ≤ 4.57×10⁻⁴ μ_N, not the ~0.84 μ_N an order-of-magnitude estimate would suggest.
7. **Caught a stale calibration bug** in the original Phase 0 doc: the originally-quoted tuned value (3×10⁻⁸ μ_N) was actually pre unit-conversion-fix. Production code and docs are now consistent.

---

## What the branch is good for

- **Capability demonstration** — the LZ EFT infrastructure works end-to-end.
- **Forward-prediction template** — anyone wanting to test a BSM magnetic-moment interpretation of the LZ event can plug in their coupling and get a verdict against our data.
- **Parameter-space quantification** — we know exactly which couplings are allowed and which would have already been seen.

## What the branch is NOT

- **Not a discovery** — the LZ 248 keV event is not confirmed. It's 3.4σ local, 2.6σ global. The branch will stay off master until LZ / XENONnT / PandaX / DARWIN confirms the event.
- **Not a UV-derived prediction** — the coupling μ_x is a free knob. Deriving it from first principles in the composite sector is months of QFT work (Task 2 scaffolding documented; not faked).
- **Not an exclusion** — the branch is well below every published direct-detection limit.

---

## The honest caveats (in plain English)

1. **We tuned the coupling, the data didn't pick it.** This is a "we can match the event," not "we predict the event."
2. **The recoil spectrum is not peaked at 248 keV** — at our tuned point, only ~10% of the predicted events land in the LZ-observed 248 keV bin. The branch says "a 248 keV event is plausible," not "we predict 248 keV specifically."
3. **The LZ preprint itself calls L_10 "illustrative"** — they're showing the analysis machinery, not claiming the event is real.
4. **PandaX-4T already constrains μ_x at lower masses** (40 GeV). Their published bound is 4.8×10⁻¹⁰ μ_B = 2.6×10⁻⁷ μ_N. We're below this at the corrected tuned value, but barely — only ~5×.
5. **The HEPData record for the LZ 2026 limit (DOI 10.17182/hepdata.182472.v1) is not yet activated** as of 2026-09-07, so the precise d_10 limit at m_χ = 1000 GeV is read from Fig. 6 (~0.05-0.1) rather than from the data release.

---

## Branch merge rule (locked 2026-09-06, user-stated)

The branch merges into master **only if** any of:
1. Independent cross-detector confirmation (XENONnT / PandaX / DARWIN) of the LZ 248 keV event.
2. Peer-reviewed publication of the LZ 2026 result.
3. Community consensus on the event.
4. Our own 7D fit shows Δlog Z ≥ +2 (the data require the channel).

None of these are satisfied today. **Master stays v0.4-prelim+T88E.**

---

## What you'd see if you opened the docs

- `T90_MAGNETIC_MOMENT_PLAN.md` — the original plan, 5 phases, now with Jeffreys footnote and UV-matching roadmap
- `T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` — the headline doc with Phase 7/8/9 closure
- `reviews/MAGNET1_REVIEW_AUDIT.md` — audit of the two reviewer reports
- `code/channels_extended.py` — Channel 26 (Poisson) + 26b (binned) likelihoods
- `code/t41_v08_phase8_d10_mapping.py` — Phase 8 empirical mapping
- `code/t41_v09_phase9_lz_data.py` — Phase 9 Table S7 extraction + Task 2 scaffolding
- `outputs/t90/t90_phase8_d10_mapping.json` — Phase 8 numerical results
- `outputs/t90/t90_phase9_lz_data.json` — Phase 9 numerical results

---

## One-sentence summary

The T90 branch is a working, tested, documented, peer-reviewer-validated capability demonstration that the project can match the LZ 248 keV event at a coupling ~7,500× below the LZ 2026 limit, with a stale-doc bug caught and fixed; whether the branch ever merges into master depends entirely on whether the LZ community confirms the 248 keV event.
