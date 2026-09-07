# T90 / T95 Time-Log

**Purpose**: Log every time estimate I make + the actual time spent,
to build a calibration over time. Started 2026-09-07 per user directive.

**SCOPE (updated 2026-09-07)**: This is the per-project time log.
The **GLOBAL** time-log rule lives in `~/.hermes/time-log.md`
(a project-agnostic aggregator). This file is the project-specific
entry point for the sidm-composite-dm-mediator project.

Per-user directive 2026-09-07: "keep the log on for all tasks,
not just this project." Logging now applies to ALL projects,
ALL sessions, ALL tasks where I say "X minutes/hours/days/weeks".

**Format**:
```
[YYYY-MM-DD] [path/task]
  ESTIMATE:    <what I said>  <units>  <agent-compute|calendar>
  ACTUAL:      <what happened>  <units>
  RATIO:       <actual/estimate>
  NOTE:        <anything relevant — overnight pause, blocked on X, etc.>
```

---

## 2026-09-07 — T90 Path C.4 (cross-detector) and follow-ups

### Path 6 (repo cleanup: Dockerfile + .dockerignore)
- **ESTIMATE**: 2-4 hours (agent compute)
- **ACTUAL**: ~1.5 hours active
- **RATIO**: 0.5-0.75× (over-estimated)
- **NOTE**: Mechanical work, no physics; straightforward

### Path 1 (multi-operator fit v14)
- **ESTIMATE**: 2-4 hours (agent compute)
- **ACTUAL**: ~4 hours active
- **RATIO**: 1.0× (matched estimate well)
- **NOTE**: Built on v13 framework; calibration logic was the main work

### Path 7 (consolidate T90 docs into T90_INDEX.md)
- **ESTIMATE**: 4-8 hours (agent compute)
- **ACTUAL**: ~30 minutes active
- **RATIO**: 0.06-0.13× (massively over-estimated)
- **NOTE**: Pure writing; the docs already existed, just needed an index

### Path 3 (UV completion v16) — DONE 2026-09-07
- **ESTIMATE**: 5-10 hours of agent compute
- **ACTUAL**: ~3 hours of agent compute
- **RATIO**: 0.3-0.6× (over-estimated)
- **NOTE**: All 3 UV models calibrated; 11/11 tests pass; doc written. Composite (Aranda+) is most accessible experimentally; dark photon (Fabbrichesi+) is most testable; vector-like (Hisano+) is non-minimal (37 PeV).

### Path 4 (indirect signals v15) — DONE 2026-09-07
- **ESTIMATE**: 4-8 hours of agent compute
- **ACTUAL**: ~1.5 hours of agent compute
- **RATIO**: 0.2-0.4× (over-estimated)
- **NOTE**: All 3 indirect channels implemented (γγ line, solar nu, antiprotons). LZ-tuned model is 5-12 orders of magnitude below current limits — indirect detection CANNOT falsify the LZ interpretation. 10/10 tests pass.

### Path 2 (LZ time-series v17) — DONE 2026-09-07
- **ESTIMATE**: 2-4 hours (structural); 14-21 days (full reanalysis)
- **ACTUAL**: ~2 hours of agent compute (structural + public data)
- **RATIO**: matched estimate (structural branch chosen)
- **NOTE**: Per user correction, LZ data IS publicly available (PRL 135, 011802 + arXiv:2609.02823). Used those numbers. Added Higgsino interpretation (Fan & Tweed 2026). Magnetic-moment and Higgsino tied at 47% posterior each (both predict 1 event). 12/12 tests pass.

---

## Calibration attempts (data extraction from state.db)

### Attempt 1: 2026-09-07, sqlite query
- **Approach**: All sessions > 6 hours wall time = over-estimated (overnight)
- **ESTIMATE (computed)**: 39× under-estimate (median)
- **REVISED**: Filter to wall-time < 6h (real single sessions) → only 1 clean CLI session
- **REVISED ESTIMATE**: 4.67× under-estimate (1 data point)
- **VERDICT**: Insufficient data; cannot claim robust ratio

---

## Pattern so far

| Work type | Estimate pattern | Confidence |
|---|---|---|
| Mechanical (cleanup, file writes) | OVER-estimated 2-4x | high (1 data point) |
| Script+test on existing framework | MATCHED estimate | medium (1 data point) |
| Pure writing (docs, indices) | OVER-estimated 10-20x | medium (1 data point) |
| **Physics implementation (UV completion, single paper)** | **OVER-estimated 2-3x** | **medium (1 data point)** |
| **Physics implementation (indirect signals)** | **OVER-estimated 2-5x** | **medium (1 data point)** |
| **Physics implementation (LZ time-series, structural)** | **MATCHED estimate** | **medium (1 data point)** |

---

## Next estimate to log

When user asks for next task, log HERE before starting.
