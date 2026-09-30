# Changelog — v19.2-B §2.7 cycle (R26 → R36, 2026-09-30)

## Summary

Eleven review rounds (R26 → R35) on §2.7 (Ohana+ 2026 c-M consistency), each catching an error the previous introduced. The cycle ended with §2.7 **PARTIALLY CLOSED**: the 0.16 dex consistency check is verified (chain is valid: Ohana+ → DJ19 §2.1 → DK14/DK15); the 0.07/0.085 dex values are reframed as sensitivity results, not literature predictions.

R36 added single-source-of-truth numbers file + drift check. **§2.7 is frozen. No more iteration. Next phase: paper thesis.**

## Timeline

### Initial (8f3a70a)
- Fabricated 0.06σ match
- Status: closed (typo + tautology)

### v19.2-B.2 (3a2f4fd) — R26
- **r26.docx units bug fix**: v19.2-B v2 multiplied denominator by log(10), treating 0.085 dex as natural-log scatter
- DK14 0.16 dex NOT yet identified; v19.2-B.1-v19.2-B.6 used 0.085 dex (source UNVERIFIED)
- Tension: 6.18σ at 0.085 dex
- Status: closed

### v19.2-B.3 (a877283) — R27
- Dropped "0.06σ match" overclaim from R26 trajectory tables
- Sharpened framing: "Clean negative at 0.085 dex" (no fabricated match)
- MCP UTF-8 fix
- Status: closed

### v19.2-B.4 (62c2bb0) — R28
- Docstring arithmetic-reproducible
- MCP UTF-8 encoding fix
- Paper §2.7 added
- Status: closed

### v19.2-B.5 (7ca4bf5) — R29
- §2.7 reconciliation with r29 reviewer feedback
- Mechanism: 3 candidate sources for 6.18σ vs Ohana+ 3.2σ gap identified
- Trajectory table added to §2.7
- Status: closed

### v19.2-B.6 (a79b207) — R30
- Paper-JSON reconciliation
- Trajectory labels aligned
- Ohana+ scatter inspected (PDF)
- **Initial scatter diagnosis (R30):** "Diemer+ 2019 cosmic" was the most plausible attribution
- Status: closed

### v19.2-B.7 (8677c71) — R31 (REVERSAL)
- **KEY FINDING:** r31 PDF inspection reveals Ohana+ uses **0.16 dex**, NOT 0.085 dex
- R31 initial framing: "REPRODUCES" Ohana+ 3.2σ
- Tension: **3.29σ** (MCMC) / 3.16σ (fiducial) at DK14 0.16 dex
- Status: closed (but introduced "reproduction" overclaim that R31-VERIFICATION would later walk back)

### v19.2-B.8 (da610fe) — R31-VERIFICATION
- r31 itself flagged that "REPRODUCTION" was too strong (synthetic-data tautology)
- **REPRODUCTION → CONSISTENCY CHECK** at the fiducial reframe
- Synthetic-data caveat added to §2.7
- Status: closed

### v19.2-B.9 (53efaec) — R32 polish
- R32 Issue 5 wording: "is consistent with Ohana+ 3.2σ at the fiducial under the 0.16 dex convention"
- R32 Issue 4: 3.16σ fiducial number added to JSON + trajectory
- **R32 Issue 3 introduced a new error:** "Both 0.085 dex and 0.16 dex are prescriptions from DJ19" — WRONG. DJ19 does not give 0.085 dex.
- Status: closed (but introduced scatter-attribution error that R33 would catch)

### v19.2-B.10 (ba6e54c) — R33 polish
- **R33 Issue 2 verification:** fetched DK14 PDF directly, verified 0.16 dex = DK14 Table 1
- Corrected R32: "DJ19 endorses DK14" framing was wrong — DJ19 §2.1 says "0.16 dex (DK15)" which is the same paper
- **DJ19 = c-M median paper, NOT scatter source. DK14 = scatter source.**
- 0.13σ attribution corrected (c_best-fit drives the spread, not c_med change)
- Lead with 3.16σ (fiducial) over 3.29σ (MCMC)
- 0.085 dex attribution downgraded to "UNVERIFIED"
- **R33 introduced a meta-error:** claimed "Ohana+ miscited DJ19" — but Ohana+ citation was correct (DJ19 §2.1 endorses DK14 via "DK15" citation; the chain is valid)
- Status: closed (but introduced meta-correction error that R34 would catch)

### v19.2-B.11 (d7de62b) — R34 polish
- **R34 Issue 2 verification:** re-fetched Ohana+ §3.1 PDF, found 4 verbatim quotes all attributing to "Diemer and Joyce, 2019" — Ohana+ citation is CORRECT, not miscited
- Re-fetched DJ19 §2.1, found: "the scatter, which is much larger, about 0.16 dex (DK15)"
- **Citation chain Ohana+ → DJ19 → DK14/DK15 fully verified**
- 0.085 dex / 6.18σ downgraded to footnote-only
- 0.09σ bound corrected from 0.13σ (was the pipeline spread, not from published)
- §2.7 Closure Status block added: 0.16 dex CLOSED, 0.085 dex OPEN
- Status: closed

### v19.2-B.12 (c9f6b4c) — R35 polish (TERMINAL)
- **R34 Issue 1 reframing:** the [0.07, 0.085] dex range in v19.2-B.1 commit `f76a9cd` was framed as "Diemer+ 2019 model-dep scatter values" — a citation attempt, not verified literature. Reframed 6.18σ and 7.51σ as **sensitivity results, not literature-based predictions**
- Every 6.18σ/7.51σ appearance carries "(sensitivity, source UNVERIFIED per r34 Issue 1)" marker
- DK14/DK15 identity explicit: "DK14 = arXiv:1407.4730 (2014 preprint) published as ApJ 799, 108 (2015); 'DK15' refers to the same paper, ApJ publication year"
- "Ohana+ citation is CORRECT" softened to "Ohana+ cites DJ19, which endorses DK14/DK15 0.16 dex in §2.1; the chain is valid (common secondary-source-endorses-primary pattern)"
- Status: closed (terminal)

### R36 (709bb1e) — Single source of truth + freeze
- Created `v0.3-prelim/data/standing_numbers.json` as authoritative source for §2.5/§2.6/§2.7 numbers
- Created `scripts/load_standing_numbers.py` with drift check
- PAPER_STANDING_NUMBERS.md flagged as rendering, not source
- **§2.7 FROZEN — no more iteration**
- Status: closed

---

## §2.7 Final Status (frozen)

| Component | Status |
|---|---|
| 0.16 dex consistency check (3.16σ at fiducial) | **CLOSED** |
| Citation chain Ohana+ → DJ19 → DK14/DK15 | **CLOSED** (chain is valid) |
| DK14/DK15 identity | **CLOSED** (arXiv:1407.4730 → ApJ 799, 108, 2015) |
| 0.085 dex / 6.18σ | **OPEN** — reframed as sensitivity result, not literature prediction |
| 0.07 dex / 7.51σ | **OPEN** — reframed as sensitivity result (sibling value) |
| **v19.2-B overall** | **PARTIALLY CLOSED** |

---

## Process Lessons (per user feedback)

### 1. The 11-bundle loop is the signal

Each iteration caught an error the previous introduced:
- Initial: fabricated 0.06σ
- R26: wrong c-M formula (units bug)
- R27: dropped overclaim
- R28: docstring arithmetic fix
- R29: §2.7 added
- R30: paper-JSON reconciled
- R31: SCATTER CORRECTION (6.18σ → 3.29σ)
- R31-VER: REPRODUCTION → CONSISTENCY CHECK
- R32: wording polish (introduced scatter-attribution error)
- R33: scatter verification (corrected R32, introduced meta-correction error)
- R34: meta-correction (corrected R33, closed citation chain)
- R35: sensitivity-result reframing (terminal)

This is **not convergence**. It's a verification gap upstream: three files (paper, script, JSON) each maintained their own copy of standing numbers. The fix is a single source of truth, implemented in R36 as `v0.3-prelim/data/standing_numbers.json` + `scripts/load_standing_numbers.py` (drift check).

### 2. Over-iteration risk

Eleven adversarial review cycles on one subsection, ending in a number that is footnote-only and a citation that was wrong twice — suggests the review loop was generating work rather than resolving it. The 0.16 dex side is genuinely closed. Take the win and move.

### 3. §2.7 is a robustness check, not a result

The 3.16σ consistency at fiducial under Ohana+'s scatter convention, using synthetic data at that fiducial, is exactly what it is: a self-consistency check. It does not discriminate SIDM from CDM, does not test against real data, and does not need the abstract.

---

## Next Phase (pending user direction)

Per R35 + R36 + user directive 2026-09-30:
1. ~~Stale branch disposition~~ — archived (1)
2. **One-page thesis statement** — deferred per user instruction (sentence to be decided later)
3. ~~Consolidate 11-bundle history~~ — this changelog
4. **Decide paper thesis before any new section work** — gravothermal cascade / σ_eff / LZ direct-detection
5. **Defer v19.2-B v3** until thesis is set; v3 is expensive and only worth doing if Cloud-9 tension is central to the thesis

---

**§2.7 is frozen at R35-POLISH. Single source of truth lives at `v0.3-prelim/data/standing_numbers.json`. Drift check: `python scripts/load_standing_numbers.py`. Next move: paper thesis.**