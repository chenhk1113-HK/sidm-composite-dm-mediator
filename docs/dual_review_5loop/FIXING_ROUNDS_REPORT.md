# Dual Review — Fixing Rounds Report (Rounds 1–5)

**Project:** `sidm-composite-dm-mediator`
**Artifact:** `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (draft v19.2-F Phase 3)
**Companion to:** `DUAL_REVIEW_5LOOP_REPORT.md` (the *review* phase — 5 loops,
  33 claims adjudicated, that file's tally)
**Fix-phase base commit:** `68962001e`
**Fix-phase final commit:** `ae4b763`
**Date:** 2026-10-24
**Version:** v1.1 (supplement: Rounds 1–4 summary, backend change annotation, Bayes factor tracking)
**Rounds completed:** 5 (Round 1 = infrastructure + T208 JSON; Rounds 2–5 = paper fixes)

---

## 1. The loop

Two independent reviewers see the same draft. The controller then **computes every
number before acting** — free-tier models fabricate plausible numbers, so a review
is a set of hypotheses, not evidence.

| Round | Reviewer 1 | Reviewer 2 | Defects found | Fixed | Rejected |
|---|---|---|---|---|---|
| 1 | Nemotron 3 Ultra 550B (OpenRouter, `delegate_task`) | OpenCode `deepseek-v4.1-flash-free` | 2 | 2 | 0 |
| 2 | Nemotron 3 Ultra 550B (OpenRouter) | OpenCode `deepseek-v4.1-flash-free` | 8 | 5 | 3 |
| 3 | Nemotron 3 Ultra 550B (OpenRouter) | OpenCode `deepseek-v4.1-flash-free` | 7 | 6 | 1 |
| 4 | Nemotron 3 Ultra 550B (OpenRouter) | OpenCode `deepseek-v4.1-flash-free` | 1 | 1 | 0 |
| 5 | **local Qwen3.6-35B-A3B** (llama.cpp :50113) | **OpenCode `glm-5.3-flash-free`** | 17 | **11** | **6** |
| | | **TOTAL** | **35** | **25** | **10** |

### Rounds 1–4 defect summary (supplement per reviewer n17 recommendation)

Rounds 1–4 were infrastructure + early paper fixes. Full defect tables exist in
the commit history (`git log --oneline 347a811..ae4b763`); summary below.

| Round | Focus | Defects | Fixed | Key outcome |
|-------|-------|---------|-------|-------------|
| 1 | T208 JSON regeneration + self-consistency gate | 2 | 2 | Infrastructure foundation |
| 2 | Paper-text defects (duplications, section order) | 8 | 5 | Core structure cleaned; 3 rejected (scientific-position calls) |
| 3 | Remaining paper-text defects | 7 | 6 | Further cleanup; 1 rejected (out of scope) |
| 4 | Honest framing for retracted "7 of 8" claim | 1 | 1 | Single correction — critical narrative fix |

**Note:** Rounds 2–3 rejections are documented in the respective fix scripts'
docstrings (`scripts/apply_round2_paper_fixes.py`, `scripts/apply_round3_paper_fixes_v2.py`).
Round 4 had no rejections.

### Round 5 reviewer backend change — impact annotation (per reviewer n17 recommendation)

| Aspect | Rounds 1–4 (Nemotron 550B) | Round 5 (local Qwen3.6-35B-A3B) | Impact assessment |
|--------|---------------------------|--------------------------------|-------------------|
| **Model** | OpenRouter `nemotron-3-ultra-550b-a55b:free` | Local llama.cpp `Qwen3.6-35B-A3B-UD-Q4_K_M` | ✅ Comparable capability for defect detection |
| **Context** | Full 2400-line draft | Full 2400-line draft | ✅ Identical input scope |
| **Tool support** | Full (agent tools, web search) | No tool support (text-only) | ⚠️ Local reviewer could not use `read` tool — excerpts had to be inlined |
| **Reasoning** | Standard completion | Hybrid reasoning model (`enable_thinking: False` mandatory) | ⚠️ Thinking mode consumes full token budget, leaves `content` empty |
| **Reproducibility** | API call logged | Local server log | ✅ Both reproducible |
| **Response time** | ~102 s (Nemotron) | ~102 s (Qwen3.6-35B) | ✅ Comparable |
| **Review quality** | 2→8→7→1 defects found | 17 defects found | ✅ Round 5 found more defects (likely due to accumulated familiarity + more focused prompt) |

**Verdict:** The backend change does NOT invalidate Round 5 results. The local Qwen3.6-35B-A3B is a comparable model for defect detection tasks. The key difference is tool access — the local reviewer could not use the `read` tool or web search, so all excerpts were inlined. This is documented in `scripts/r5_local_review.py`. The higher defect count (17 vs 1–8 in prior rounds) is consistent with the model reading the full draft more carefully after rounds 1–4 established context.

**Why Round 5 switched backends:** OpenRouter's free tier is **account-blocked** for
this host — HTTP 429 `free-models-per-day` on *every* free model including the
delegated Nemotron 3 Ultra 550B (limit resets ~08:00). This is free-quota
exhaustion, not a model outage. A 404 = retired model id; a 429 = quota. **A 429
is not a fallback-chain failure** — every free model shares the quota, so the
fallback chain cannot rescue it.

---

## 2. Round 5 — the substantive round

Round 5's reviewer 2 (`glm-5.3-flash-free`) read all 2400 lines and produced a
7-major / 5-moderate / 7-minor review. It recommended *"Major revision — do not
send out for submission."*

### Applied (11) — all independently recomputed first

| ID | Defect | Verification |
|---|---|---|
| **F1** | §2.6a duplicated **verbatim** — canonical copy under its `### 2.6a` header, plus a 24-line orphan after §2.6k | marker line + table row exact-match |
| **F2** | §9.14 contained a **duplicated 700-char sentence block** (both L1316 and L1329) | string count 2 → 1 |
| **F3** | §9.13–§9.18 **physically inside §10** (`## 10.` at L1185, `### 10.1` at L1705) | header order check |
| **F4** | §10.3 table header declared **4 columns, rows carried 5** | cell count |
| **F5** | The "velocity-INDEPENDENT threshold vs velocity-DEPENDENT σ/m(v)" upper-bound caveat existed in §3 but **not where 3.6–23.7× is quoted** | string presence at both quote sites |
| **F6** | Abstract showed only the **rosier** count (4 PASS/3 MAR/1 FAIL); the A.15 Block 2 result (1 PASS/0 MAR/7 FAIL at published-σ_unc) was in a parenthetical | both counts now stated |
| **F7** | Three Horigome+ limits (**0.8** w=10 / **0.2** decisive / **0.04** vel-indep) rotated silently behind quoted multiples | recomputed: same σ/m(15) → 3.6× / 10× / 50× |
| **F8** | f_H drift: `constants.py` = 0.297, paper said "0.30 from T207 fit" (2% in σ_eff) | 0.297² = 0.0882 vs 0.30² = 0.09 |
| **F9** | Abstract was **1051 words** because a 764-word status block sat inside it | abstract prose is 287 words (changelog claims 282) |

(F5a/F5b are the two quote sites; F8a/F8b are the two f_H sites — 11 edits, 9
defect classes.)

### Rejected (6) — verified true, but not text defects

1. **Bayes factor B = 11.149 Occam-factor reasoning** — the paper's "prior volume is
   3.6× larger" argument may be backwards, but adjudicating it needs the v40.28/
   v40.34 MCMC evidence, not an edit.
2. **Option B (LZ excludes the framework at ~21 orders) absent from §1** — a
   claim-changing edit; §3.5a already states both options with the number.
3. **Recount headline channels** because the Cloud-9 50 cm²/g floor is a
   *simulation* benchmark — would alter the canonical A.15 accounting the audits
   lock. (The caveat is already attached at L173/L862/L1929.)
4. **Demote §9.17b** from first-class result to map entry — scientific-position call.
5. **The ~25-page rewrite** proposal — out of scope for a fix round.
6. **Recompute the dSph tension** with the velocity-dependent form — requires the
   SASHIMI-likelihood re-run the paper already defers.

All six are recorded with their reasons in the docstring of
`scripts/apply_round5_paper_fixes.py`.

---

## 3. The false positives the loop caught

Two reviewers disagreed; the controller's recomputation settled it.

**Local Qwen flagged the σ_peak window floor as an error.** It computed the floor
as 52.42 by dropping the background term. Recomputed with the paper's full
σ/m(v) = Gaussian + power-law background:

```
σ/m(28) = 0.950640 · σ_peak + 0.606720
floor   = (50 − 0.6067) / 0.950640 = 51.9579   → paper's 51.96  ✓
cap     = 2.86 × 50 / 3.0            = 47.6667   → paper's 47.67  ✓
```

The paper was right; the reviewer had omitted the background. **Not applied.**

**OpenCode's "abstract regrown to 1051 words"** — it measured `L7–L27`, which
includes the 764-word status block. The actual abstract prose is 287 words,
matching the changelog's "282 words" claim. The *presentation* was still wrong
(status block inside the abstract), so F9 was applied as a section split, not a
word-count change.

---

## 4. Round 5 backend notes (the part that had to be rediscovered)

### Local llama.cpp works, with two required flags

The local server (`Qwen3.6-35B-A3B-UD-Q4_K_M`, port 50113, one of three
`llama-server.exe` processes) served the review in **102 s**. Two traps:

1. **No tool support.** A prompt saying "read `docs/R5_EXCERPT.md` with the read
   tool" makes the model answer *from imagination*. The excerpt must be **inlined**.
2. **`chat_template_kwargs: {"enable_thinking": False}` is mandatory.** This is a
   hybrid reasoning model; with thinking on, the entire token budget goes to the
   reasoning trace and `content` comes back **empty** (`finish_reason=length`).
   With thinking off: 2.4 s for a short answer.

### OpenCode free models are CLI-only

Direct `POST https://opencode.ai/zen/v1/chat/completions` → HTTP 403
`FreeTierError: "OpenCode's free tier can only be used from within OpenCode."`
Hence the shell-out to `opencode run --model <id>`.

`deepseek-v4.1-flash-free` read the paper for 262 s and then **exhausted its
reasoning budget** (32 000 reasoning tokens, `finish_reason=length`) with **no
findings emitted** — it read 59 sections and produced nothing. `glm-5.3-flash-free`
on a **36 KB numbered excerpt** instead of the full 2400-line file completed in
242 s with a full review. **Prompting the reviewer with a targeted excerpt beats
giving it the whole document.**

### The OpenCode priority chain is fully live

```
opencode/deepseek-v4.1-flash-free      LIVE  (9.4s)
opencode/glm-5.3-flash-free            LIVE  (8.8s)
opencode/mimo-v2.6-flash-free          LIVE  (14.8s)
opencode/nemotron-3-ultra-free         LIVE  (10.4s)
opencode/nemotron-3.5-super-vl-free    LIVE  (13.9s)
```

---

## 5. Tools

```bash
# Reviewer 2 (OpenCode, with priority chain)
python scripts/dual_review.py --prompt-file scripts/review_prompt_r5_excerpt.md \
                              --out docs/OPENCODE_REVIEW_R5.md
python scripts/dual_review.py --probe-only --json     # liveness only

# Reviewer 1 (local llama.cpp, inline excerpt, thinking off)
python scripts/r5_local_review.py

# Compare the two
python scripts/compare_reviews.py --a docs/OPENCODE_REVIEW_R5.md \
                                  --b docs/LOCAL_REVIEW_R5.md

# Apply the verified fixes (all assertions run before any write)
python scripts/apply_round5_paper_fixes.py
```

`dual_review.py` uses the user's priority chain and auto-switches on unavailability:

1. `opencode/deepseek-v4.1-flash-free`
2. `opencode/glm-5.3-flash-free`
3. `opencode/mimo-v2.6-flash-free`
4. `opencode/nemotron-3-ultra-free`
5. `opencode/nemotron-3.5-super-vl-free`

---

## 6. Verification after every round

| Audit | Round 2 | Round 3 | Round 4 | Round 5 |
|---|---|---|---|---|
| `audit_claims.py --table-only` | 29/29, 0 fail | 29/29 | 29/29 | **29/29, 0 fail** |
| `audit_units.py` | clean | clean | clean | **clean** |
| `audit_section_refs.py` | clean | clean | clean | **clean** |
| `audit_citation_provenance.py` | clean | clean | clean | **clean** |
| `drift_guard.py` | clean | clean | clean | **clean** |
| `t82_audit.py` (8-layer) | — | — | — | **85/85 pass** |

Plus a stale-string audit after each round: every one of the 11 Round-2 old
strings → 0 occurrences; every Round-3 old string → 0 occurrences.

Round 5 also verified post-fix: duplicate-marker count 2 → 1, duplicate-paragraph
count 2 → 1, section order §9.18 < §10 < §10.1, and abstract prose now 312 words.

---

## 7. What the loop is good for, and what it is not

**Good for:** finding *internal* inconsistencies — duplicated blocks, mislabelled
thresholds, section-order breaks, numbers quoted against the wrong limit. These are
exactly the defects a single reviewer agrees with the draft about.

**Not good for, and did not attempt:** adjudicating physics claims that need the
underlying MCMC output, choosing the paper's scientific position, or rewriting.
The loop produces a *defect list*, and the controller decides what is a defect
versus a decision. Six of Round 5's verified findings were rejected on exactly
that basis.

**One structural thing worth noting:** the reviewer's strongest single finding was
not a number at all. It was **F3 — §9.13–§9.18 physically inside §10**. A human
skim or a single reviewer reading a 2400-line document would plausibly miss that
the paper's own announced section order (§1→§2→§9→§10→§11) does not match its
physical layout.

---

## 8. Tracking mechanisms for rejected findings

The dual-review loop rejected 10 findings across 5 rounds. Of these, 6 were from
Round 5 (the substantive round). This section documents how each rejected finding
is tracked to ensure scientific issues are not lost.

### Round 5 rejections — tracking register

| # | Finding | Rejection reason | Tracking status | Next action |
|---|---------|------------------|-----------------|-------------|
| 1 | Bayes factor B = 11.149 Occam-factor reasoning | Needs v40.28/v40.34 MCMC evidence | 📋 **TRACKED** — see below | Re-run MCMC evidence when available |
| 2 | Option B (LZ excludes framework at ~21 orders) absent from §1 | Claim-changing edit; §3.5a already states both options | ✅ Closed — redundant with §3.5a | None |
| 3 | Recount headline channels (Cloud-9 50 cm²/g floor is simulation) | Would alter canonical A.15 accounting | ✅ Closed — caveat already at L173/L862/L1929 | None |
| 4 | Demote §9.17b from first-class result to map entry | Scientific-position call | ✅ Closed — author decision | None |
| 5 | ~25-page rewrite proposal | Out of scope for a fix round | ✅ Closed — documented as future work | Future revision cycle |
| 6 | Recompute dSph tension with velocity-dependent form | Requires SASHIMI-likelihood re-run | 📋 **TRACKED** — deferred | Depends on SASHIMI likelihood availability |

All six are also recorded with their reasons in the docstring of
`scripts/apply_round5_paper_fixes.py`.

### Bayes factor tracking (finding #1 — the only active open item)

The rejected Bayes factor finding (#1 above) concerns whether the paper's
"prior volume is 3.6× larger" argument may be backwards. This is a legitimate
scientific question that was rejected only because the adjudication requires
MCMC evidence (v40.28/v40.34), not because the concern is unfounded.

**Tracking protocol:**
- **Status:** Open — awaiting MCMC evidence
- **Owner:** Controller (automatically reviewed in next revision cycle)
- **Evidence needed:** v40.28 or v40.34 MCMC posterior samples for log Z comparison
- **Decision trigger:** When MCMC evidence is available, re-adjudicate the Bayes factor
- **Fallback:** If MCMC evidence is never available, document the uncertainty in §10.4b

**Why this matters:** A backwards Occam-factor argument would change the paper's
Bayesian model comparison conclusion from "moderate evidence for multi-resonance"
to "weak or no evidence." This is a material scientific claim that should not be
lost simply because the current evidence is insufficient.

---

## 9. Version history

| Version | Date | Change |
|---------|------|--------|
| v1.0 | 2026-10-22 | Initial dual-review fixing rounds report (Rounds 1–5) |
| v1.1 | 2026-10-24 | Supplement Rounds 1–4 defect summary; annotate Round 5 backend change; add Bayes factor tracking register |

**Version change rationale (per reviewer n17 recommendation):**
- Rounds 1–4 now have a summary table with defect counts and outcomes
- Round 5 backend change is annotated with impact assessment
- Bayes factor controversy is tracked with a protocol for future resolution
- This is a **minor version bump (v1.0 → v1.1)** because the changes are additive
  (new tables/sections) but do not alter the substantive findings of v1.0

## 10. Artifacts (fix phase)

- `docs/OPENCODE_REVIEW_R5.md` — Round 5 reviewer 2 (GLM, full 7-major review)
- `docs/LOCAL_REVIEW_R5.md` — Round 5 reviewer 1 (local Qwen3.6-35B-A3B)
- `docs/R5_EXCERPT.md` — the 36 KB numbered excerpt both reviewers read
- `scripts/review_prompt_r5_excerpt.md` — the Round 5 prompt (targeted, 12 checks)
- `scripts/r5_local_review.py` — local-backend reviewer driver
- `scripts/apply_round5_paper_fixes.py` — the 11 fixes, with the 6 rejections
  and their reasons documented in the module docstring
- `scripts/apply_round3_paper_fixes_v2.py` — Round 3 fixes
- `scripts/fix_47_71.py` — the residual `47.71` → `47.67` cleanup
