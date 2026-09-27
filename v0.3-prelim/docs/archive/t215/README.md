# Archive — T215 round-by-round responses (SUPERSEDED)

This directory contains the per-round response documents from the T215
KiSS-SIDM investigation (Rounds 1–6 of the Rv18.4 review cycle).

## Canonical references

These round-by-round docs are **SUPERSEDED** by the consolidated documents:

- **Canonical framing:** `../T215_CANONICAL_FRAMING_2026-09-26.md`
- **Tier 1+2 pilot (final):** `../T215VWXY_TIER12_PILOT_2026-09-27.md`
- **Paper §10.5b:** `../PAPER_V1_DRAFT.md` §10.5b (the final shipped section)

These documents are preserved for git history traceability. Their numbers
and claims may have been superseded by later rounds; always defer to the
canonical references above.

## Files in this archive

| File | Round | Topic |
|---|---|---|
| `T215HI_RNG_SEED_RESPONSE_2026-09-26.md` | Round 1 | RNG seed hypothesis |
| `T215K_FRESH_SESSION_TEST_2026-09-26.md` | Round 2 | Fresh-session 5× test |
| `T215M_RV18_4_ROUND4_RESPONSE_2026-09-26.md` | Round 4 | Threading refuted |
| `T215N_SAME_SESSION_TEST_2026-09-26.md` | Round 5 | Same-session 100/100 RNG test |
| `T215P_PER_RUN_DENSITY_ANALYSIS_2026-09-26.md` | Round 5 | 5/5 fresh-session qualitative signal |
| `T215E_60MYR_BREAKTHROUGH_2026-09-26.md` | early | First 60 Myr reach |

## Why archived

Per devplan1.docx Phase 1.3:
> "Current state — headers added but files still in the primary docs
> directory — is the worst of both worlds."

Headers were added in Round 7, but the files remained in `docs/`. This
move puts them under `archive/t215/` with a clear pointer to the canonical
documents. Git history is preserved.