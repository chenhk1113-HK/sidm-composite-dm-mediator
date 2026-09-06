# Disclaimer

> **Every line of code, every comment, every value in every test, and every
> word in every doc in this repo was generated, reviewed, and iterated by
> AI systems, not by a human domain expert.**

This project is a personal research artifact developed end-to-end with
AI assistance. The contributions are:

- **Lead developer + project owner:** K. Lam (provides the research
  question, the review chain, and the standing-posture decisions).
- **Coder (primary):** Hermes (MiniMax M3 model).
- **Reviewer pool:** Doubao, Qwen 3.8 Max, and other AI reviewers
  (cross-validation and adversarial-style audits).

## What this means for users

1. **No human domain-expert review.** The physics, statistics, and
   code have been vetted by AI systems, not by a particle physicist or
   astrophysicist. Treat the work as **preliminary research, not
   publication-ready science**.
2. **Cross-validation by independent groups required.** Before using any
   number in this repo for downstream work, **reproduce the T41
   nested-sampling run and the key unit/sign tests**. Per reviewer 2:
   "Treat pre-R12 numbers as historical. Reproduce if you plan to
   build on it."
3. **Not a substitute for independent verification.** This disclaimer
   also appears as the first line of `README.md`. The project is
   offered as a starting point for further investigation, not as a
   definitive answer.

## Reproducibility caveats

- Hardware / software dependencies are listed in `requirements.txt` and
  `v0.3-prelim/INSTALL.md`.
- Julia + KiSS-SIDM calibration is required to fully reproduce the
  gravothermal core-collapse channel (Channel 8).
- All joint-fit posteriors are stored as JSON in
  `v0.3-prelim/data/results/`.

## Change history

| Date | Change | Source |
|---|---|---|
| 2026-09-06 | Initial creation per `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` cross-reference (the file was referenced but never created — created in T89.2 doc-fix round). | T89.2 doc-fix, this commit |
