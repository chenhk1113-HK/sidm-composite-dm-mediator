# SciBERT (github.com/allenai/scibert)

**Status:** NOT ADOPTED
**Repo:** [github.com/allenai/scibert](https://github.com/allenai/scibert)
**Paper:** arXiv:1903.10676 (Beltagy, Lo, Cohan 2019) "SciBERT: Pretrained Language Model for Scientific Text"
**Type:** **Encoder-only** BERT (NOT a generative LLM)
**License:** Apache 2.0
**Stars:** 1.7k, 232 forks
**Verified:** 2026-10-17

## What it is

A BERT model pretrained on scientific text:
- Training corpus: 1.14M papers from Semantic Scholar (full text)
- Custom SCIVOCAB (30% overlap with BERT vocab; optimized for scientific text)
- SOTA on NER, relation extraction, citation intent classification, dependency parsing, sentence classification (multiple benchmarks)
- 7 years old, battle-tested, widely cited

## v19.2-F relevance assessment

**Verdict: NOT useful. Wrong tool for the job.**

**Why not now:**
1. **Encoder-only** — completely different architecture from M3/OpenScholar/AstroSage. NOT a chat/LLM. Cannot generate text.
2. BERT-era (2019) — no instruction following, no tool use
3. **v19.2-F doesn't need NER, RE, classification, or dependency parsing** — the actual project work is:
   - Parameter sanity-checking (Python re-runs)
   - Citation verification (read_file + KB lookup)
   - Paper reading (controller + read_file)
   - These don't need a BERT encoder
4. Would require **significant new infrastructure** (BERT serving, embeddings pipeline) for marginal benefit
5. Existing `read_file` + `grep` is sufficient for the limited NLP v19.2-F does

**When SciBERT would be useful (for a different kind of project):**
- If v19.2-F needs **automatic metadata extraction** (paper section classification, abstract vs intro detection)
- If v19.2-F needs **citation intent classification** (cites for methodology vs cites for result)
- If v19.2-F needs **NER on paper text** (find σ/m values, σ_v values, M_halo values mentioned in papers)
- For **embedding-based similarity search** of paper sections (k-NN retrieval)

**None of these are current bottlenecks.**

**Comparison to other tools considered this session:**

| Tool | Type | Useful for v19.2-F? | Reason |
|---|---|---|---|
| AstroSage-8B | LLM (isolated Q&A) | Marginal | Same hallucination problem as M3 |
| AstroLLM | LLM (RAG) | Not yet | "Not yet usable" |
| OpenScholar-8B | LLM (RAG) | No | Out-of-domain (CS, not astro) |
| **SciBERT** | **Encoder BERT** | **No** | **Wrong tool type; no NLP bottleneck in v19.2-F** |

**User hardware compatibility:**
- BERT-base: ~110M params, 440MB; fits easily on any hardware
- CPU inference: ~50ms per embedding
- But again: **no current use case** for embeddings in v19.2-F

**If adopted, would need:**
1. A specific NLP task to solve (none identified)
2. BERT serving infrastructure (e.g., sentence-transformers, transformers, ONNX)
3. Re-evaluate against existing `grep` + `read_file` approach

## TO VERIFY
- [ ] None — SciBERT is clearly not useful for v19.2-F's current scope
- [ ] Keep entry for reference; re-evaluate IF v19.2-F needs metadata extraction
