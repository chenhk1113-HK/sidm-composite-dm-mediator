# AstroLLM (github.com/astrollm/astrollm)

**Status:** WATCHING (not adopted)
**Repo:** [github.com/astrollm/astrollm](https://github.com/astrollm/astrollm)
**Site:** [astrollm.org](https://astrollm.org)
**License:** Apache 2.0
**Maintainer:** Nandan (single)
**Verified:** 2026-10-17

## What it is

Domain-specialized LLM for astronomy & astrophysics:
- Phase 1 deliverable: Qwen3.5-4B/9B QLoRA + Gemma 4 E4B
- Retrieval-grounded + tool-integrated (NASA ADS, SIMBAD, VizieR, NED)
- Differentiates from AstroSage (de Haan+ 2024) by retrieval + tool use (not just fine-tune)
- Differentiates from AstroLLaMA (Nguyen+ 2023) by database integration

## Current state (as of 2026-10-17)

**NOT YET USABLE.** README says:
> "Status: Phase 1 (v1) — Retrieval-Grounded Copilot, in progress. The retrieval foundation is built and ablated end-to-end (pilot + widening + pool sweep); the RAG-SFT pilot is pre-registered and its gold-seed authoring harness is built — Phase A hand-authoring is the active work. Not yet usable."

- No model weights released (HuggingFace org exists but empty)
- No GitHub releases
- Q3 2026 release target slipped to Q4 2026
- Single maintainer (bus factor = 1)

## v19.2-F relevance assessment

**Verdict: NOT useful for current scope.** Parked in KB for 3-6 month re-evaluation.

**Why not now:**
1. v19.2-F is paper-submission ready (v40.x Phase 3 CLOSED). The project is in "polish" mode, not "new tool adoption" mode.
2. Existing toolchain (M3 + OpenAI4S + Nemotron + KB + drift-guard) already covers AstroLLM's would-be use cases:
   - Paper search → arXiv API + `docs/papers/`
   - Citation verification → controller + KB
   - Numerical review → Python re-runs
3. AstroLLM's focus is astronomy Q&A + tool use, NOT paper claim verification + numerical sanity-checking (which is what v19.2-F needs)

**When to revisit:**
- When AstroLLM v1 ships with model weights
- Benchmark against M3 on a v19.2-F task:
  - "Find papers citing Yang+ 2024 with σ/m < 0.5 cm²/g at v > 100 km/s"
  - "Verify Segue 1 σ_v = 3.7 km/s is consistent with the latest (post-2024) Simon+ reanalysis"
  - "Generate a JSON of all UFD kinematics from the past 3 years, with citations"

**If/when adopted, would need:**
1. Re-evaluate v40.13 reference registry task on AstroLLM (catch any v40.14-style citation errors)
2. Cross-check that AstroLLM's retrieval doesn't fabricate citations (it WILL — like all LLMs)
3. Re-validate AstroLLM's numerical claims against controller's Python re-runs

## TO VERIFY (re-evaluation checklist)
- [ ] v1 weights released on HuggingFace
- [ ] astrollm.org public beta live
- [ ] Independent benchmark vs M3 on astronomy paper search
- [ ] Independent benchmark vs controller on citation verification
- [ ] Single-maintainer risk: is Nandan still active?
- [ ] License remains Apache 2.0 (no relicensing)
