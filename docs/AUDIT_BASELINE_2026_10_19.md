# v19.2-F Self-Verification Audit — Baseline (2026-10-19)

## Purpose
Document the state of all 5 audit layers + Round 13 self-check BEFORE the new
verification infrastructure is added (per user plan 2026-10-19).

## Results

| Script | Status | Detail |
|---|---|---|
| `scripts/drift_guard.py` | ✓ PASS | "No drift detected" |
| `scripts/t82_audit.py` | ✓ PASS | 85/85 checks |
| `scripts/audit_claims.py` | ⚠ MIXED | Standing-numbers table 24/24 ✓, but "REGEX RESULT: FAIL" at end |
| `scripts/audit_units.py` | ✓ PASS | 1156 unicode superscripts noted, no unit issues |
| `scripts/run_round13_self_check.py` | ✗ 5/8 FAIL | See below |

## Round 13 Self-Check — 5/8 FAIL

| Check | Status | Detail |
|---|---|---|
| 1. Standing-numbers table audit | ✓ PASS | 24/24 numbers verified |
| 2. Paper-claims regex audit | ✗ FAIL | "REGEX RESULT: FAIL — at least one mapped claim has drifted or is untracked" |
| 3. Cross-validation | ✗ FAIL | 1 forbidden phrase found: "Cloud-9 tension resolved (positive)" |
| 4. Table-walker | ✗ FAIL | 8 rows with "both pass+fail markers in same row" |
| 5. §-symbol cross-references | ✗ FAIL | 5 references to non-existent sections (§7, §11) |
| 6. Citation provenance | ✗ FAIL | "Could not find References section" |
| 7. Unit consistency | ✓ PASS | — |
| 8. pytest test_paper_claims.py | ✓ PASS | 12/12 |

## What this means

The 5 failures are **real issues in PAPER_V1_DRAFT.md** that have not been
addressed since v40.36 push (per memory: "Local 5-layer verifiers not re-run
since v40.36").

Categories:
- **A. Stale claim** (Check 2): some "mapped claim has drifted or is untracked"
- **B. Forbidden phrase** (Check 3): "Cloud-9 tension resolved (positive)" is
  a no-no per current review rules (Cloud-9 vs dSph tension is actually UNCHANGED)
- **C. Table ambiguity** (Check 4): 8 rows have contradictory pass+fail markers
- **D. Broken cross-references** (Check 5): §7, §11 referenced but don't exist
- **E. Missing References** (Check 6): no References section in paper

These need to be FIXED in the paper, not just acknowledged. Per user directive
"no time budget, make model more error-proof", proceed to fix.
