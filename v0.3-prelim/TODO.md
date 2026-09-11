# TODO List — Pending Work Items

**Last updated:** 2026-09-11
**Maintained by:** Hermes Agent
**Branch context:** `wip/cloud-9-relhic` (T90 Cloud-9 branch)

---

## LRD (Little Red Dot) channel — DEFERRED PER USER DIRECTIVE 2026-09-11

**Title:** T90.63 LRD/SIDM channel — DEFERRED (not included in unified model)

**Source:** User directive 2026-09-11 (after T90.63 v1, v2, v3 smoke tests):
> "record but dont include lrd, it is too extreme and far away in time and space."

**Decision:** LRD channel work is preserved in git history as exploratory research but is **NOT included** in the unified SIDM model results.

**What was investigated (T90.63 v1, v2, v3):**
- **v1** (commit `8a6d0c3`): Gaussian per-bin likelihood for n_LRD at z=5,7,8.5
- **v2**: UV luminosity function bins (10 bins, Taylor+2025, Matthee+2024, Harikane+2023, Greene+2026) + bolometric correction L_bol/L_5100=5 (arXiv:2509.05434) + A_V=1 fixed dust attenuation
- **v3** (commit `748d911`): Cardelli+Clayton+Mathis 1989 extinction law + variable A_V sampled from lognormal distribution

**Why deferred:**

1. **User's explicit judgment: "too extreme and far away in time and space"**
   - LRDs are at z~3-8 (lookback time 11-13 Gyr)
   - Unification-relevant channels (Cloud-9, Galactic, Bullet, LZ) are local (z~0)
   - Connecting local SIDM physics to high-z LRD seed formation involves assumptions about DM halo populations, accretion physics, and dust that are not independently validated

2. **Structural tension with other channels** — confirmed across all three dust treatments:
   - v1: σ/m(Cloud-9)=1.04 (violates ≥30), σ/m(v=30)=1.03
   - v2: σ/m(Cloud-9)=0.017 (violates ≥30), σ/m(v=30)=3.64
   - v3: σ/m(Cloud-9)=0.264 (violates ≥30), σ/m(v=30)=0.64
   - **The Cloud-9/LRD tension is ROBUST** — not a dust assumption artifact

3. **Other problems uncovered during exploration:**
   - **Unit conversion bugs**: 977.8 Myr vs 977800 Myr (off by 1000×) — caught and fixed in v1, recurred in v2
   - **Age-of-universe function**: returned lookback time instead of age in early v2 (fixed in v2 patch, then properly fixed in v3)
   - **Cardelli law coefficients**: polynomial `0.574*x^1.61` gives wrong values for x>3 (UV range); need Table 3a values
   - **Bolometric correction sensitivity**: arXiv:2509.05434 L_bol/L_5100=5 is a single Sept 2025 paper — needs independent confirmation

**Affects:** None going forward. The LRD code (v1, v2, v3) is in git history but should not be wired into production T90 fits.

**Priority:** N/A — explicitly deferred per user.

**Status:** Deferred, NOT started for inclusion in unified model.

**Lessons captured (in writeup docs):**
- `v0.3-prelim/docs/T90_PATH_C4_V63_LRD_CHANNEL.md` — v1 writeup
- `v0.3-prelim/docs/T90_PATH_C4_V63_V3_CARDELLI_DUST.md` — v3 writeup with the three-version comparison

**Standing reference for future LRD work:**
If LRD constraints become relevant in the future (e.g., new Jiang+2027 mechanism, independent bolometric correction confirmation, low-z LRD analogs found), the existing v3 code + Cardelli law framework is the most defensible starting point. But per current user judgment, this is deferred indefinitely.

---

## T90.62 (item 8 from 2026-09-11 review) — NOT DONE

**Title:** Replace Gaussian placeholder channels with raw posterior chains

**Source:** Reviewer 2 (2026-09-11), recommendation #4:
> "Replace Gaussian placeholder channels with raw posterior chains
> before any publication claim."

**What needs to happen:**
- Audit all `loglike_*` functions in `v0.3-prelim/code/channels_extended.py`
  and `v0.3-prelim/code/ksfr_pcac_validity.py`
- For each channel that uses a Gaussian approximation:
  - Check if a real posterior chain exists (from paper authors or
    public MCMC dump)
  - If yes, swap the Gaussian for the real chain
  - If no, document why Gaussian is the best we can do

**Estimated time:** 1 hour to 2 days depending on:
- How many channels need this (need to audit first)
- Chain availability from data sources
- Whether the codebase has the chain-extraction infrastructure

**Affects:** Both T90 (wip/cloud-9-relhic) and v0.8 (standing) lines.
Any channel used by T90.57 or T41 v0.8 that is Gaussian-approximated.

**Priority:** Medium. Per the 2026-09-08 pause directive, this is
appropriate to defer until either:
- New MCMC chains become available
- The user gives explicit go-ahead
- The T90 line moves from exploratory to standing

**Why deferred:**
1. **Scope is unknown** — requires auditing all loglike_* functions first
2. **External dependency** — depends on what chains are publicly available
3. **High blast radius** — affects the underlying science, not just docs
4. **Per pause directive** — "wait for new evidence and datasets"

**Status as of 2026-09-11:** Recorded, NOT started.

---

## Items 6 and 7 (2026-09-11 review) — DONE

- **Item 7** (naturalness measure): COMPLETED in T90.60 (commit `dff55d3`).
  See `v0.3-prelim/docs/T90_PATH_C4_V60_NATURALNESS.md`.

- **Item 6** (T86 σ_DM-nuc discrepancy resolution): COMPLETED in T90.61
  (commit `5adeff5`). See
  `v0.3-prelim/docs/T90_PATH_C4_V61_KAHLHOEFER_AUDIT.md`. Finding:
  T86 audit's "15 order" claim was wrong — actual discrepancy is
  ~62 orders. T78/T79 prefactor "1.2e-32" is off by ~6 orders from
  the standard Kahlhoefer formula.

---

## Options A and B (from 2026-09-11 user prompt)

Per user "record option a and b as to do items":

### Option A — Fix downstream v0.8 docs

**Title:** Propagate T90.61 v2 findings to standing v0.8 docs

**Source:** 2026-09-11 user prompt, after Option D + C completed.

**What needs to happen:**
- Update `T86_PLAUSIBILITY_AUDIT.md` to incorporate T90.61 v2 cross-
  reference (currently partially done — see T86 lines 167-219)
- Update `T87_FORWARD_PREDICTION.md` forward prediction verdict
  (margin is ~59 orders, not 70)
- Update `README.md` project summary (~3 orders below LZ → ~59 orders)
- Update `CURRENT.md` version-of-record
- Verify internal consistency across all four

**Estimated time:** 30-60 minutes for doc updates + verification.

**Affects:** Standing v0.8 docs (not just wip branch). The T86 audit
patch is partially done in `55761d7`; the rest is deferred.

**Priority:** Medium. The T86 audit patch (T90.61 v2 cross-reference)
is in place but T87, README, CURRENT.md still need propagation.

**Why deferred:**
1. **Touches standing v0.8 docs** — per AGENTS.md rule 5, requires
   explicit user approval before state-changing actions on standing
   docs
2. **Multiple files** — risk of one drift while fixing another
3. **Low urgency** — T90 wip branch is correct; v0.8 just has the
   same approximate answer (T86 was approximately right)

**Status as of 2026-09-11:** Recorded, NOT started (partial T86
patch in place from `55761d7`).

---

### Option B — Continue T90 series (T90.62+)

**Title:** Ship additional T90 increments

**Source:** 2026-09-11 user prompt, after Option D + C completed.

**What needs to happen:**
- T90.62 (item 8): Gaussian → real posterior chains. Estimated 1h-2d.
- T90.63: MCMC convergence improvement (nlive=200 → nlive=1000).
  Wall time 4-8 hours per production run.
- T90.64: Posterior predictive checks. Mock-data validation.
  Estimated 2-3 hours.
- T90.65: Channel sensitivity sweep. Vary each channel's error bar
  by 2×, measure fit robustness. Estimated 1-2 hours.

**Estimated time:** Variable. Each T90.x is a fresh production run.

**Affects:** T90 wip branch only (no standing-doc edits).

**Priority:** Low. Per 2026-09-08 pause directive, T90 was explicitly
exempted but each new T90.x is a fresh production run that extends
scope.

**Why deferred:**
1. **Per pause directive** — "wait for new evidence and datasets"
2. **Each T90.x is a fresh production run** — wall time on order
   of 30-90 minutes per run
3. **Low marginal value** — T90.58 ablation already established
   the robustness hierarchy; T90.59 established the synthesis
4. **Open questions remain unresolved** — what to do with the
   fine-tuning penalty findings?

**Status as of 2026-09-11:** Recorded, NOT started.

---

## Earlier deferred items (from 2026-09-08 pause directive)

These remain deferred per the standing pause. Listed for reference.

### T95 streams
- **Title:** T95 chemodynamic cross-match + Gaia DR4 + 113-stream residual
  catalog
- **Status:** PAUSED per 2026-09-08 directive
- **Note:** User explicitly lifted pause for T90 series only

### Reading σ/m measurements from M51, T90 multi-velocity
- **Title:** Build proper M51 likelihood (currently a kludge that
  double-counts the Galactic channel)
- **Status:** PAUSED — research-level work, deferred per user choice
  of "KSFR only" path in T90.57

### Path C (resonance with kinetic mixing)
- **Title:** Re-parameterize T90 resonance to have kinetic mixing,
  enabling apples-to-apples LZ comparison with T90.56 hybrid
- **Status:** PAUSED — Path B chosen for T90.56

---

## How to use this TODO

This file is the canonical record of pending work items. When you
resume work on a paused item:
1. Check this file for the latest status
2. Update the status (NOT DONE → IN PROGRESS → DONE)
3. Move completed items to a "Completed" section at the bottom
4. Update the "Last updated" date

When starting new work:
1. Add a new section at the top
2. Include the source (user directive, reviewer recommendation, etc.)
3. Include priority and estimated time
4. Include any preconditions or blockers

---

## Format conventions

Each TODO item should include:
- **Title** (one-line summary)
- **Source** (who asked for it)
- **What needs to happen** (concrete steps)
- **Estimated time** (rough budget)
- **Affects** (which lines / docs / code)
- **Priority** (high/medium/low)
- **Why deferred** (if not currently active)
- **Status** (NOT DONE / IN PROGRESS / DONE)