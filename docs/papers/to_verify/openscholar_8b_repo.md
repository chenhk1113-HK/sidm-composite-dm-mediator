# OpenScholar-8B (huggingface.co/OpenSciLM/Llama-3.1_OpenScholar-8B)

**Status:** NOT ADOPTED
**Repo:** [huggingface.co/OpenSciLM/Llama-3.1_OpenScholar-8B](https://huggingface.co/OpenSciLM/Llama-3.1_OpenScholar-8B)
**Paper:** arXiv:2411.09012 (Asai et al., 2024) "OpenScholar: Synthesizing Scientific Literature with Retrieval-Augmented Language Models"
**Base:** Llama-3.1-8B
**Format:** HF Transformers (not GGUF)
**License:** Apache 2.0
**Verified:** 2026-10-17

## What it is

RAG-based 8B LLM for **scientific literature synthesis**. Unlike AstroSage (isolated Q&A), OpenScholar retrieves from a corpus, then synthesizes answers with citations. 1.7k+ stars on related open-scholar GitHub repo. Was on the user's radar as "Not attempted on Linux/Docker/HuggingFace mirror. Lower priority" (from prior session).

## v19.2-F relevance assessment

**Verdict: NOT useful for current scope. Out-of-domain training data.**

**Why not now:**
1. **Out-of-domain training**: OpenScholar is trained on Semantic Scholar Open Research Corpus (CS/ML papers), NOT astrophysics. SIDM papers are astro-ph, which is sparse in the training data.
2. 8B is much smaller than M3 → reasoning depth downgrade
3. Will still hallucinate citations (LLM failure mode proven by v40.6 fabricated quote)
4. v19.2-F is paper-submission ready (v40.x Phase 3 CLOSED)
5. Existing M3 + WebSearch + web_extract covers literature search
6. Citation verification still requires controller + actual file read (not LLM)

**When to consider (if ever):**
- If v19.2-F opens a 50+ paper automated lit review (M3 might not be best at synthesizing that volume)
- If we want to **benchmark M3 vs OpenScholar on astronomy Q&A** (out-of-domain, but useful test)
- If OpenScholar releases an astro-specific fine-tune
- If M3 goes down

**User hardware compatibility:**
- 8B on CPU: ~5-10 tok/s (similar to AstroSage)
- 96GB RAM on Minisforum X1 Pro is plenty
- BUT: integrated GPU (Radeon 890M, Strix Point) is not supported for Strix Halo workloads (per 2026-10-16 feasibility check)

**If adopted, would need:**
1. Benchmark on 5+ v19.2-F tasks (paper lookup, citation verification, parameter sanity-check)
2. Cross-check OpenScholar claims with controller's Python re-runs (it WILL hallucinate)
3. Note: out-of-domain for astro, expect ~30% accuracy drop vs in-domain

## TO VERIFY
- [ ] Independent benchmark vs M3 on SIDM-relevant tasks
- [ ] Performance on integrated GPU (Strix Point unsupported; CPU-only)
- [ ] License confirmed Apache 2.0
- [ ] Was previously listed as "lower priority" in earlier session — confirm same conclusion
