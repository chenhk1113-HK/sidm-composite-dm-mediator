# T109 — Review_7.docx audit closure (2026-09-08)

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Reviewer document:** `Review_7.docx` (received 2026-09-08)
**Audited branch state:** `39e647c` (pre-T109)
**Closure commit:** T109 (this work)

---

## TL;DR

Review_7.docx is a **pre-PR WIP assessment** of the magnetic-moment
branch that is broadly accurate in physics framing but systematically
underestimates the current state of the branch. Out of 28 verified
claims:

- **13 ✅ Confirmed** (branch purpose, modular design, two-portal physics, etc.)
- **4 ✅ Already-shipped** (959 tests pass, outputs/ gitignored, CI workflow exists, summary docs exist)
- **7 ⚠️ Valid-deferred** (low-energy precision constraints, form-factor scan, 7D dynesty, etc.)
- **3 ⚠️ Stale** (reviewer described WIP status that was resolved 1-2 weeks ago)
- **1 ❌ N/A** (reviewer assumes a `dev` branch; project uses master + WIP)

**2 genuine follow-up items** were identified and shipped in this commit:

1. **MODEL_ASSUMPTIONS_AND_LIMITATIONS.md** — added a "Magnetic-moment Ls₁₀ channel (T90 work)" sub-section under §0 with current status, physics ingredients, relation to T87 verdict, and 8D posterior numbers.
2. **scripts/t82_audit.py** — added 6 new drift-guard needles for the T90 magnetic-moment section so the audit script catches accidental removal of the section or stale numbers.

---

## What the reviewer got right

| # | Claim | Verdict | Why |
|---|---|---|---|
| 1 | "Composite dark-pion can acquire magnetic dipole moment" | ✅ Confirmed | Core T90 physics; documented in `T90_MAGNETIC_MOMENT_PLAN.md` |
| 2 | "Modular addition, doesn't break SIDM pipeline" | ✅ Confirmed | Branch is off master; v0.7 MAP unchanged |
| 3 | "Two independent scattering channels (kinetic-mixing + magnetic-moment)" | ✅ Confirmed | T99 two-portal framing |
| 4 | "Physics idea well-motivated" | ✅ Confirmed | NREFT operators + composite DM is a meaningful extension |
| 5 | "Documentation is honest about incompleteness" | ✅ Confirmed | T90_INDEX and T90 merge rule explicitly document gaps |

---

## What the reviewer got wrong (stale claims)

| # | Claim | Reality |
|---|---|---|
| 1 | "Missing full pytest coverage" | **959 tests pass** (was 8 at the time the reviewer was looking) |
| 2 | "Intermediate JSON committed to git" | `outputs/` is gitignored; no JSON in `git log --stat` |
| 3 | "No CI checks" | Project has CI workflow (commit `6609bb1`); pytest is the de facto gate |
| 4 | "Draft posterior scans" | T108 is a full 8D dynesty with log Z = -162.78 ± 0.20 |
| 5 | "Should not be merged into dev/main" | Still correct (T90 merge rule 2/5) but for different reason than reviewer cited |

---

## What the reviewer missed (NEW work since their snapshot)

| Work | Description | Status |
|---|---|---|
| T98 (2026-09-04) | Di Mauro 2026 cross-check (arXiv:2609.02608) | Shipped |
| T99 (2026-09-04) | Two-portal composite-DM framing | Shipped |
| T101 (2026-09-05) | LZ 248 keV data extraction | Shipped |
| T102 (2026-09-05) | 2D Bayesian scan (m_χ, δ) | Shipped |
| T103 (2026-09-05) | 4D LZ-only joint fit | Shipped |
| T105 (2026-09-08) | UV consistency check (Alves-Wacker 2010) | Shipped |
| T106 (2026-09-08) | Multi-experiment joint fit (DIAMX) | Shipped |
| T107 (2026-09-08) | 8D emcee joint fit (B1-lite) | Shipped |
| T108 (2026-09-08) | 8D dynesty nested sampling | Shipped |

These 9 items (T98-T108) are the **most recent and most impactful** work on the branch. They:
- Quantify the inelastic-DM vs magnetic-moment cross-section gap (74.8 OOM)
- Add the LZ 248 keV event as a new data channel
- Find a major revision to the project's v0.7 best-fit (m_χ 498 → 138 GeV)
- Provide the first 8D posterior for the two-portal model

---

## Genuine follow-up items shipped in T109

### Item 1: MODEL_ASSUMPTIONS_AND_LIMITATIONS.md sub-section

Added a 60-line sub-section to §0 documenting the T90 magnetic-moment work:

```markdown
### Magnetic-moment Ls₁₀ channel (T90 work, 2026-09-08) — the "second door"

[physics ingredients, status, T87 relation, 8D posterior numbers, standing posture]
```

Plus a change-history entry at the end of the doc.

### Item 2: scripts/t82_audit.py drift-guard

Added 6 new needles in the `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` check list:

- `Magnetic-moment Ls₁₀ channel` (section heading)
- `-162.78` (8D log Z)
- `+0.51` (Δlog Z)
- `138 GeV` (8D MAP m_χ)
- `98 keV` (8D MAP δ)
- `1.4×10⁻⁴²` (8D MAP σ_PortalB)

Plus a regression test `test_t90_door_b_section_in_model_assumptions` that runs the audit and asserts all 6 needles are present.

**Drift-guard status: 50/50 ALL CLEAR** (was 44/44; +6 needles).

### Item 3: Update t82_audit test count threshold

Updated `test_total_check_count_at_least_40` to `test_total_check_count_at_least_50` to reflect the new needle count.

---

## What was NOT shipped (and why)

### Not shipped: 7D dynesty (6 v0.7 + μ_χ)

The reviewer flagged this as a real gap. It's the missing piece for
T90 merge rule criterion #5 (Δlog Z ≥ +2). However:

- It would take 4-10 hours of dynesty runtime
- It requires careful consideration of priors (μ_χ has a wide range)
- The T108 8D fit (which already includes the magnetic-moment
  channel via Portal B) shows Δlog Z = +0.51, not +2

**Decision:** Defer to a dedicated Tier-2 round, not in this closure
cycle. The T90 work is still WIP per the merge rule; a 7D dynesty
should be a planned Tier-2 item, not a quick fix.

### Not shipped: form-factor uncertainty scan

Reviewer flagged this. Also deferrable. The T90 v14 calibrated
operators have one form-factor choice; systematic scan is Tier-2 work.

### Not shipped: low-energy precision constraints

Reviewer flagged this as missing from likelihood. **This is correct**
but would require a new channel implementation (atomic parity
violation, etc.). Out of branch scope; document as future work.

---

## Honest limitations of T109

1. **The 6 needles pin a snapshot, not the live state.** If T90 numbers
   change (e.g., from a future 7D dynesty), the needles will need to
   be updated. This is **intentional** — the drift-guard catches
   drift, but the canonical values must be maintained manually.

2. **No automated verifier for the doc text quality.** The audit
   checks for string presence, not for correct grammar or physics.
   A human reviewer is still needed to ensure the section is
   well-written.

3. **The audit doesn't catch downstream drift.** If README.md or
   CHANGELOG.md is updated to remove a T90 number, the audit won't
   catch it (only MODEL_ASSUMPTIONS is checked). This is the
   current scope of the script.

---

## Files

- `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` — added §0+ sub-section + change-history entry
- `scripts/t82_audit.py` — added 6 T90 needles
- `v0.3-prelim/tests/test_t82_audit_version_drift.py` — added 2 new tests
- `v0.3-prelim/docs/T109_REVIEW7_AUDIT_CLOSURE.md` — this doc

## Test count

- **960 pass / 8 skip** (was 959, +1 new T90 door B test)
- `t82_audit.py`: 50/50 ALL CLEAR (was 44/44)

## Time log

- ESTIMATE: 30 min
- ACTUAL: ~25 min
- RATIO: 0.83× — matched estimate

## Standing posture

- **T90 branch** now has drift-guard for the magnetic-moment section
- **MODEL_ASSUMPTIONS** is the canonical doc for the magnetic-moment work
- **Master** still v0.5-prelim, untouched
- **T90 merge rule** still 2/5 criteria

## Cross-references

- `Review_7.docx` — the review (input)
- `T90_INDEX.md` — T90 cross-link index
- `T90_MAGNETIC_MOMENT_PLAN.md` — magnetic-moment plan
- `T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` — magnetic-moment forward prediction
- T98-T108 — recent T90 work that the reviewer missed
- **T109 (this work)** — Review_7.docx audit closure

## Provenance

- T109 implementation: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Reviewer document: `Review_7.docx` (uploaded 2026-09-08)
- Branch: `wip/tier3-magnetic-moment-LZ`
- Standing posture: T90 branch, master untouched
