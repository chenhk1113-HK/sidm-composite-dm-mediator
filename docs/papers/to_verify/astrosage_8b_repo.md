# AstroSage-Llama-3.1-8B-GGUF (AstroMLab 3)

**Status:** CANDIDATE FALLBACK (not adopted)
**Repo:** [huggingface.co/AstroMLab/AstroSage-8B-GGUF](https://huggingface.co/AstroMLab/AstroSage-8B-GGUF)
**Paper:** arXiv:2411.09012 — "AstroMLab 3: Achieving GPT-4o Level Performance in Astronomy with a Specialized 8B-Parameter Large Language Model"
**Authors:** Tijmen de Haan, Yuan-Sen Ting, Tirthankar Ghosal, Tuan Dung Nguyen, Alberto Accomazzi, Azton Wells, Nesar Ramachandra, Rui Pan, Zechang Sun
**Base:** Llama-3.1-8B
**Format:** GGUF (Q8_0, BF16)
**Verified:** 2026-10-17

## What it is

Specialized 8B-parameter LLM for astronomy, astrophysics, cosmology. Claimed GPT-4o level on AstroMLab-1 benchmark. Quantized GGUF versions for local deployment.

## v19.2-F relevance assessment

**Verdict: marginally useful, NOT urgent. Don't install now.**

**Why not now:**
1. v19.2-F is paper-submission ready (v40.x Phase 3 CLOSED) — not in tool-adoption phase
2. **AstroSage is isolated Q&A** (per AstroLLM's own assessment) — no tool integration, no retrieval, no verification
3. v40.13-v40.15 work proved **isolated Q&A is the failure mode**:
   - v40.6 fabricated quote → caught by reading actual PDF, not by LLM
   - v40.4 wrong arXiv ID → caught by arXiv listing lookup
   - v40.15 wrong Walker+ 2007 citation → caught by ApJL 667, L53 abstract check
4. Existing toolchain (M3 + OpenAI4S + Nemotron + KB) already covers AstroSage's would-be use cases
5. 8B is much smaller than M3 → downgrade in reasoning depth

**When to consider:**
- M3 unavailable (rate limit, downtime) — local fallback
- Benchmark M3 vs AstroSage-8B on astronomy Q&A (could surface gaps in M3)
- 50+ more papers to review (automated lit review)
- Local/private inference becomes critical

**User hardware compatibility (per 2026-10-16 feasibility check):**
- Minisforum AI X1 Pro, 96GB RAM
- Strix Point integrated GPU (Radeon 890M) — NOT supported for Strix Halo workloads
- Q8 8B GGUF on CPU: ~5 tok/s (batch/inference viable, not real-time)
- Q4 8B GGUF on CPU: ~10 tok/s
- Fits in 96GB RAM easily

**If adopted, would need:**
1. Benchmark on 5+ v19.2-F tasks (paper lookup, citation verification, parameter sanity-check)
2. Cross-check AstroSage-8B claims with controller's Python re-runs (it WILL hallucinate)
3. Configure via Ollama or llama.cpp wrapper
4. Keep M3 as primary; AstroSage as fallback

## TO VERIFY (re-evaluation checklist)
- [ ] M3 uptime/duty cycle — is a fallback actually needed?
- [ ] AstroMLab-1 benchmark scores — published?
- [ ] Independent benchmark vs M3 on v19.2-F tasks
- [ ] CPU vs integrated GPU performance on user's hardware
- [ ] License: appears Apache 2.0 (de Haan+ 2024) — confirm
