# T95.10 Literature Search Scaffolding

**Date:** 2026-09-08  
**Streams to search:** 95 (T95.10 OK subset)  
**Queries per stream:** 4 (by short name × subhalo/gap/DM/perturbations)  
**Total queries:** 380  

## Purpose

Replace the velocity-only synthesized constraints in the T95.10 joint
fit with published literature constraints as found. The T95.9 curated
set has 10 streams with published sigma/m bounds. The T95.10 residual
has 95 streams with track+velocity data, but most lack individual gap-count
papers (they were discovered recently by Gaia).

## Known references (from T95.9 + literature pointers)

See `KNOWN_REFERENCES` dict in `t95_v26_lit_search.py` for the current
starting set. Includes Sagittarius (the gold standard), Cetus, Elqui,
Tucana III, Ophiuchus, Monoceros, etc. The 95 OK streams mostly consist
of Gaia-discovered (Gaia-N) and Ibata-2024 catalog (New-N, C-N) streams
without dedicated gap-count papers.

## Workflow

1. Open `outputs/t95/t95_v26_lit_search_queries.txt` — it has all 380 queries.
2. For each stream, run the 4 queries against arXiv (`arxiv.org/search`)
   or NASA/ADS (`ui.adsabs.harvard.edu`).
3. Record findings in `outputs/t95/t95_v26_lit_search_results.json`:
   - `papers_found`: comma-separated author+year list
   - `n_gaps_published`: count or '0 (no gaps confirmed)'
   - `sigma_m_lower_published` / `sigma_m_upper_published`: from gap-count analysis
   - `v_perturber_published`: characteristic perturber velocity
   - `constraint_status`: needs_search → searched_no_constraint → constraint_added
4. After search complete, re-run the T95.10 pipeline with the populated
   constraints — joint loglik will become meaningful.

## Honest scoping note

A full literature search of 95 streams × 4 queries is 1-2 hours of
focused work. Most streams will fall into `searched_no_constraint`
(recently discovered, no dedicated gap-count paper). Expected yield:
- 5-10 streams with NEW constraints (Sagittarius, Cetus, Elqui, etc.)
- 30-50 streams with `searched_no_constraint`
- 30-40 streams that remain `needs_search` (low priority, very recent)

## Status (2026-09-08)

- [x] Scaffold shipped (this file + queries file + empty results JSON)
- [ ] Stream-by-stream arXiv search (1-2 hrs of focused work)
- [ ] Populate results JSON
- [ ] Re-run T95.10 with literature constraints
- [ ] Update joint fit + T95 finding if loglik moves materially
