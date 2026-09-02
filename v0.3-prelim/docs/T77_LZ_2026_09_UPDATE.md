# T77 — LZ 2026-09-01 Mysterious Signal Update (v0.4-prelim)

> **Status:** Shipped 2026-09-02. Defensive doc-update in response to the
> 2026-09-01 LZ signal announcement.
> **Trigger:** User upload of `more info.docx` referencing the LZ signal;
> user direction "c and then plan for d".
> **Companion:** [MODEL_ASSUMPTIONS_AND_LIMITATIONS §0](../MODEL_ASSUMPTIONS_AND_LIMITATIONS.md),
> [T76 v0.7 convergence](T76_V07_NLIVE2000.md).

## What happened

**2026-09-01** — The LUX-ZEPLIN (LZ) collaboration announced a single
high-energy particle interaction event in their 10-tonne liquid-xenon
detector at the Sanford Underground Research Facility. Key facts
(verified across 5+ independent university press releases — Imperial,
Northwestern, SLAC, Brown, LBNL, Sheffield):

| Property | Value | Source |
|---|---|---|
| **Date of announcement** | 2026-09-01 | Imperial / Northwestern / Brown |
| **Statistical significance** | **2.6σ** (≈0.5% background probability) | LBNL + Sheffield press releases |
| **Discovery threshold** | 5σ (not reached) | LBNL |
| **Implied WIMP mass if real** | **≥ 200 GeV/c²** | LBNL + Sheffield |
| **Type of interaction** | "Beyond the simplest model" (non-standard WIMP-nucleon) | LZ spokesperson R. Gaitskell |
| **Conference** | TeV Particle Astrophysics 2026 (Japan) | All sources |
| **Paper status** | Released on arXiv (TBD); submitted to PRL | All sources |
| **LZ operations** | Extended beyond 2028 to gather more data | Imperial |

## Verification

This signal is **REAL** and **publicly announced**. The 2.6σ
significance is confirmed across multiple independent university press
releases. The exact numbers (2.6σ, ≥ 200 GeV/c², 0.5% background)
are consistent across LBNL and Sheffield sources, which are the two
most authoritative (Brown University is LZ's home institution).

**However, the LZ paper has not yet appeared on arXiv as of
2026-09-02** (one day after announcement). Without the paper:
- No precise σ_DM-nucleon limit can be extracted
- No precise m_χ preferred value (just lower bound)
- No precise interaction type (just "non-standard WIMP-nucleon")

## Impact on the project — per standing posture

Per the **orthogonal-physics posture** (locked 2026-08-10, reaffirmed
in T75's MODEL_ASSUMPTIONS §0):

| Observable | What LZ measures | What the project uses |
|---|---|---|
| σ_DM-DM (SIDM, headline) | No | Yes — **unchanged** by LZ event |
| σ_DM-nucleon (direct-detection) | Yes | **Sanity check only** (Channel 5) |

**Conclusion:** The LZ signal is **orthogonal to the project's
headline σ/m result.** Even if confirmed at 5σ+ in the future, it
would NOT change the σ/m measurement.

**However**, the LZ signal — if real — provides an independent
**σ_DM-nucleon** constraint that would update Channel 5 (T30 LZ
mapping). The project's T41 v0.7 posterior (m_χ ~ 770 GeV, nlive=2000)
is **consistent** with the implied WIMP mass ≥ 200 GeV/c² (i.e., the
project's preferred mass is in the allowed LZ range).

## Decision: **No project update at 2.6σ**

Per my Tier-ranked policy (from the deferred-items plan after T76):

| Significance | Action |
|---|---|
| < 3σ | **Document in standing posture only; do not modify code/data** |
| ≥ 3σ | Update T30 LZ mapping (Channel 5); re-run T41 at nlive=2000 |
| ≥ 5σ (discovery) | Major milestone; full re-run + paper draft |

The 2026-09-01 signal is at **2.6σ** — **below the 3σ threshold**.
Therefore:
- ✅ **DO** document in MODEL_ASSUMPTIONS §0 + EXTRACT.md (done)
- ✅ **DO** write this T77 file (this file)
- ❌ **DO NOT** update T30 LZ mapping
- ❌ **DO NOT** re-run T41 (the result would be unchanged anyway)

## Doc-prominence update

### MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §0

Added a **2026-09-01 LZ signal update** paragraph at the end of §0:

> LZ detected a single high-energy event at 2.6σ (≈0.5% background
> probability), implying a WIMP mass ≥ 200 GeV/c² if real. Per the
> project's standing posture, this signal — even if confirmed — does
> NOT constrain σ_DM-DM. It constrains σ_DM-nucleon, which is the
> orthogonal observable. The signal is consistent with the project's
> T41 v0.7 posterior (m_χ ~ 770 GeV, nlive=2000). No project update
> is warranted at 2.6σ (below the 3σ threshold for updating T30).
> The LZ paper is still in PRL submission as of 2026-09-02; once
> released, it should be re-evaluated for σ_DM-nucleon limits at the
> T30 Channel 5 level (NOT at the σ_DM-DM level).

### EXTRACT.md

Added a top-of-doc callout:

> 📡 2026-09-01 LZ signal update (T77): LZ announced a single
> high-energy event at 2.6σ significance (≈0.5% background
> probability), implying a WIMP mass ≥ 200 GeV/c² if real. This does
> NOT change σ/m (per the orthogonal-physics posture above). The
> signal is consistent with the project's T41 v0.7 posterior (m_χ ~
> 770 GeV, nlive=2000). No project update at 2.6σ (below the 3σ
> threshold). LZ paper pending PRL; re-evaluate when released.

## Honest caveats

1. **The LZ paper is NOT yet on arXiv.** The 2.6σ / ≥ 200 GeV/c²
   numbers come from press releases, not the paper itself. Press
   releases can have rounding / approximation; the paper may
   report different precise numbers.
2. **"≥ 200 GeV/c²" is a lower bound, not a preferred value.** The
   signal's energy deposit (a few keV) and the kinematics of
   xenon-nucleus scattering set the lower bound on m_χ; the actual
   value (if real) could be much higher.
3. **2.6σ is a fluctuation level — well below discovery.** Many
   experiments have published 2-3σ "signals" that did not survive
   re-analysis with more data. The LZ collaboration itself says
   "researchers need more data to confirm."
4. **The doc's framing of SIDM as "orthogonal interpretation path"
   to LZ signals is partly misleading.** SIDM still predicts
   σ_DM-nucleon interactions (just with different kinematics than
   WIMP). The "orthogonality" claim in `more info.docx` conflates
   two different meanings of orthogonal — σ_DM-DM vs σ_DM-nucleon
   (project's correct usage) vs WIMP vs SIDM (which is NOT
   orthogonal because both predict σ_DM-nucleon).

## Trigger conditions for re-evaluation

The project should **re-evaluate** when **any** of the following occur:

| Trigger | New action |
|---|---|
| LZ arXiv paper appears | Read paper; extract precise σ_DM-nucleon limit |
| Significance reaches ≥ 3σ | Update Channel 5 (T30 LZ mapping) with new LZ limit; re-run T41 at nlive=2000 |
| Significance reaches ≥ 5σ | Major milestone; v0.5-prelim release |
| XENONnT or PandaX publishes a confirming event | Re-evaluate as joint constraint |
| A competing experiment (DarkSide, DEAP) publishes a contradicting limit | Re-evaluate the whole LZ picture |

### Pre-registered ≥3σ re-run protocol (added in T78)

**Question:** When the LZ signal reaches ≥3σ and the paper is
published, what specifically does "re-run T41 at nlive=2000" mean?

**Answer (pre-registered, T78 2026-09-02):** Fold the new LZ
σ_DM-nucleon limit into the existing **Channel 5** (T30 LZ mapping),
NOT as a new channel. Specifically:

1. **Update `LZ_2024_LIMITS` array** in `channels_extended.py` with
   the new LZ limit at the relevant m_χ values.
2. **Recompute** the `loglike_direct_detection_exclusion` Channel 5
   using the new LZ limit at the v0.7 MAP m_χ (~ 770 GeV).
3. **Re-run T41** at nlive=2000 with the updated Channel 5.

**Why this protocol:** The new LZ limit constrains the same
observable (σ_DM-nucleon) as the existing Channel 5 — it's a
**limit update**, not a new physics observable. Adding it as a new
channel would double-count the same observable.

**Practical impact at the project's v0.7 posterior:** Even at LZ's
hypothetical 5σ confirmation, the new σ_DM-nucleon limit would not
change σ/m because the project's predicted σ_DM-nuc is suppressed by
~70 orders of magnitude relative to LZ sensitivity (see
[T78_KINETIC_MIXING_LZ_LINK.md](T78_KINETIC_MIXING_LZ_LINK.md)). So the
"re-run T41" is a defensive integrity check, not a headline-result
update.

## KIV (Keep-In-View) cron job

**Cron job ID:** `080d2f590251`
**Schedule:** `0 9 1 11 *` (every year, November 1st at 09:00)
**Next run:** **2026-11-01 09:00** (60 days from today)
**Action:** Run `scripts/lz_kiv_check.py` to query arXiv for the LZ
paper; if found, re-evaluate per trigger conditions; if not, consider
extending the KIV by another 60 days.
**Delivery:** Telegram home channel (8676870325)

The cron job is registered with `hermes cron create`. To inspect:
`hermes cron list`. To cancel: `hermes cron remove 080d2f590251`.
The first KIV check will run on 2026-11-01 — approximately 60 days
after the 2026-09-01 announcement.

## Standing-version impact

**No version bump.** T77 is a defensive doc-update, not a code change.
Standing version remains `v0.4-prelim+T75`. All 6 drift-guard sources
still agree on `v0.4-prelim+T75`.

## Drift guard

| Source | Value |
|---|---|
| VERSION | `0.4-prelim+T75` (unchanged) |
| README.md badge | `v0.4-prelim+T75` (unchanged) |
| CITATION.cff | `v0.4-prelim+T75` (unchanged) |
| CHANGELOG.md top | `v0.4-prelim+T75` (T77 entry added below) |
| EXTRACT.md | `v0.4-prelim+T75` (now mentions T77 LZ signal) |
| MODEL_ASSUMPTIONS.md | `v0.4-prelim+T75` (now mentions T77 LZ signal in §0) |

## Files

| File | Change |
|---|---|
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (MODIFIED) | §0 updated with LZ 2026-09-01 signal |
| `EXTRACT.md` (MODIFIED) | Top-of-doc LZ signal callout |
| `v0.3-prelim/docs/T77_LZ_2026_09_UPDATE.md` (NEW) | This file |
| `CHANGELOG.md` (MODIFIED) | T77 entry |

## Provenance

> T77 defensive doc-update in response to the 2026-09-01 LZ mysterious
> signal (2.6σ, single event, ≥ 200 GeV/c² WIMP). Verified across
> Imperial/Northwestern, Brown, LBNL, Sheffield press releases.
> No project update warranted at 2.6σ (below the 3σ threshold for T30).
> The signal is consistent with the project's T41 v0.7 posterior
> (m_χ ~ 770 GeV, nlive=2000). Standing posture (σ_DM-DM ≠
> σ_DM-nucleon, locked 2026-08-10) reaffirmed. Implementation:
> 2026-09-02.