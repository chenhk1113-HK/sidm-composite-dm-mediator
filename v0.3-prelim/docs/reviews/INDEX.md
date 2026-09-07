# Reviewer Audit Index

This file indexes every reviewer audit conducted on this
project, in reverse chronological order (newest first).

## Format

Each entry follows the **V1 5-label matrix** convention used
by the established audit pattern (see `REVIEWER_AUDIT_R2`
through `REVIEWER_AUDIT_R16` for the format):

- ✅ Confirmed
- ✅ Valid-deferred (correct but not yet shipped)
- ⚠️ Imprecise (right direction, wrong specifics)
- ❌ Stale (doesn't match on-disk state)
- ✅ Already-shipped (recommendation implemented in prior round)

## Active audits (2026-09)

| Round | Source doc | File | Date | Notes |
|---|---|---|---|---|
| R17 | `Review6.docx` | [`REVIEW6_AUDIT.md`](./REVIEW6_AUDIT.md) | 2026-09-07 | Two-reviewer composite. Reviewer 1 (T90.1/T95 branch): 10/10 confirmed. Reviewer 2 (master-repo): ~8/16 confirmed, 5 stale, 3 imprecise. |
| R-AK1 | `magnet1.docx` | [`MAGNET1_REVIEW_AUDIT.md`](./MAGNET1_REVIEW_AUDIT.md) | 2026-09-07 | Reviewer-2 reviewed a non-existent "magnetic-knot/Hopfion" mechanism (zero grep hits in repo). Audit flagged the mismatch per AK-series pattern. |
| R16 | `sidmgrok1.docx` | [`../REVIEWER_AUDIT_R16.md`](../REVIEWER_AUDIT_R16.md) | 2026-08-27 | AI-disclaimed Grok review; 12 numbered recommendations, 3 stale. |
| R15 | `sidm5.docx` | [`../REVIEWER_AUDIT_R15.md`](../REVIEWER_AUDIT_R15.md) | 2026-08-26 | Referee-style review; 22 numbered claims verified; 6 stale. |

## Historical audits (2026-08 and earlier)

| Round | File | Date | Notes |
|---|---|---|---|
| R_DATASETS2 | [`../REVIEWER_AUDIT_R_DATASETS2.md`](../REVIEWER_AUDIT_R_DATASETS2.md) | 2026-08 | Data-source audit. |
| R14 | [`../REVIEWER_AUDIT_R14.md`](../REVIEWER_AUDIT_R14.md) | 2026-08 | nlive=2000 convergence, KSFR mask extension. |
| R13 | [`../REVIEWER_AUDIT_R13.md`](../REVIEWER_AUDIT_R13.md) | 2026-08 | 9 items, all shipped. |
| R12 | [`../REVIEWER_AUDIT_R12.md`](../REVIEWER_AUDIT_R12.md) | 2026-08 | Sign-flip + unit-bug audit; 11 items, all shipped. Closure at [`../R12_AUDIT_CLOSURE.md`](../R12_AUDIT_CLOSURE.md). |
| R11 | [`../REVIEWER_AUDIT_R11.md`](../REVIEWER_AUDIT_R11.md) | 2026-08 | 14 items. |
| R10 | [`../REVIEWER_AUDIT_R10.md`](../REVIEWER_AUDIT_R10.md) | 2026-08 | Earlier-round audit. |
| R9 | [`../REVIEWER_AUDIT_R9.md`](../REVIEWER_AUDIT_R9.md) | 2026-08 | Earlier-round audit. |
| R2 | [`../REVIEWER_AUDIT_R2.md`](../REVIEWER_AUDIT_R2.md) | 2026-07 | Foundational audit; established the V1 matrix pattern. |

## Companion docs

| Doc | Purpose |
|---|---|
| [`TIDY_UP_SCOPE_AUDIT.md`](./TIDY_UP_SCOPE_AUDIT.md) | Scope decision for the 2026-09-07 tidy-up round (Reviewer 2 vs GitHub best practices vs project reality). |
| [`T90_BRANCH_FINDINGS_LAYMAN.md`](./T90_BRANCH_FINDINGS_LAYMAN.md) | One-pager layman summary of T90.1/T95 branch findings. |
| [`reviews/`](./) | This directory — all reviewer-audit-related docs. |

## Counts by round (newest first)

| Round | File | Confirmed | Already-shipped | Valid-deferred | Imprecise | Stale | Total |
|---|---|---|---|---|---|---|---|
| R17 (Reviewer 1) | REVIEW6_AUDIT.md | 10 | 0 | 0 | 0 | 0 | **10** |
| R17 (Reviewer 2) | REVIEW6_AUDIT.md | ~8 | 0 | 0 | 3 | 5 | ~16 |
| R16 | REVIEWER_AUDIT_R16.md | (full breakdown in file) |
| R15 | REVIEWER_AUDIT_R15.md | 12 | 4 | 1 | 3 | 6 | 22 |

(Older rounds do not follow the V1 5-label matrix format and
are not directly comparable.)

## See also

- [`CHANGELOG.md`](../../CHANGELOG.md) — every round's
  substantive change, with commit hashes for full provenance
- [`CURRENT.md`](../../CURRENT.md) — current standing version
  + headline numbers
- [`scripts/t82_audit.py`](../../scripts/t82_audit.py) — CI-gatable
  drift-guard (44 doc-presence + 1 VERSION-drift checks)
- [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — CI
  workflow that runs pytest + t82_audit on every push/PR
