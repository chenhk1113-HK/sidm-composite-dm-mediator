# `docs/dual_review_5loop/` — what this folder is and which file is current

**Purpose:** the working directory of the Round-5 dual-review audit chain (project rounds n18 → n26,
2026-10-24 → 2026-11-02). It holds the review-response report at every version, the reviewer inputs,
the raw reviewer logs, and the gate-evidence folders each round produced.

**One file is the record; everything else is working material.**

---

## Canonical (read these)

| File | Role |
|---|---|
| `SIDM_ROUND5_CONSOLIDATED_FIXES_v1.17_2026-11-02.md` | **The report of record.** Every finding adjudicated, the coverage-gap register with IDs and status, and the gate contract. Captured by the annotated tag `v19.2-F-RecordSave-v1.17`. |
| `SIDM_N24_CLOSEOUT_REPORT_WITH_CODE_v1.1_2026-11-01.md` | Close-out companion to the report (the n24 round, with the code that implements the new gate layers). |
| `../V19_2_E_CONSOLIDATED_REPORT_2026-11-03.md` | What happened **after** this chain (v19.2-E stages 1-2, KB intake, gravothermal timing fixes). The audit chain is closed; the project moved on here. |
| `../V19_2_F_REFERENCE_DATA_REGISTRY.md` | Canonical numerical values for every citation and number used anywhere in the project. |

## Superseded report versions — `superseded/` (audit trail, not for reading)

22 files were moved into [`superseded/`](superseded/) on 2026-11-03 with `git mv`, so every one of them
is still in the history at both its original and its current path:

- `superseded/SIDM_ROUND5_CONSOLIDATED_FIXES_v1.3 … v1.16` — 14 earlier versions of the report. Each
  newer version supersedes the previous one; v1.17 is current and stays in this folder's top level.
- `superseded/SIDM_ROUND5_CHANGED_CODE_v1.1 … v1.8` — the earlier code-change appendices, same
  supersession rule.

**Why `SIDM_ROUND5_CHANGED_CODE_v1.9` stays at the top level even though v1.17 supersedes it:** gate
layers 8 and 9 (`audit_doc_anchors.py`, `audit_model_provenance.py`) resolve the companion deliverable
with a non-recursive glob of this folder's top level. With no appendix there, the companion resolves to
`None` and layer 8 fails outright — verified, not guessed. The audit layers define what must stay put.

They are retained because the review chain's own rule is that a retraction or correction must stay
traceable to the version that contained it. Moving them changed nothing about that rule.

Do **not** quote numbers from a superseded version: several were corrected in later rounds. If a document
cites one, check the same finding in v1.17 before repeating it.

## Reviewer inputs and raw logs (evidence, not conclusions)

- `NEMOTRON_LOOP1…5_review.md` — automated reviewer outputs (Nemotron), one per loop.
- `OPENCODE_LOOP1…5_review_prompt_*.md` — the prompt each loop was given, with the defect it targeted.
- `loop1…5_opencode.log`, `nemotron_context_loop1…5.txt` — raw transcripts and context dumps.
- `SIDM_DUAL_REVIEW_FINDINGS_v1.0_2026-10-24.md`, `DUAL_REVIEW_5LOOP_REPORT.md`,
  `FIXING_ROUNDS_REPORT.md` — the first-round findings and the loop-structure report.
- `SIDM_REFERENCE_INTEGRITY_v1.0_2026-10-27.md`, `SIDM_REFERENCE_RESOLUTION_v1.0_2026-10-27.md` —
  citation-integrity audits run inside the chain.
- `GROUND_TRUTH.json`, `ADJUDICATION.json`, `ADJUDICATION_EXTRA.json` — machine-readable adjudication
  records the report's claims are checked against.

## Gate evidence folders

Each is the saved output of a 15-layer `scripts/verify_release_gate.py` run on a named tree:

| Folder | Tree it certifies |
|---|---|
| `evidence_n23`, `evidence_n24`, `evidence_n25`, `evidence_n26` | the four audit rounds |
| `evidence_sweep20261103` | `8f262ba` (new-data sweep) |
| `evidence_kb_tier1_20261103`, `evidence_kb_tier2_20261103` | `2d7e0b7`, `4a715ce` (literature intake 21/21) |
| `evidence_lookback_fix_20261103` | `c1ee215` (gravothermal timing fix) |

Every evidence folder carries the same two standing disclosures: internal pytest skips are named, not
folded into the pass count, and a green gate asserts only its enumerated layers — it is not a
whole-document verdict.
