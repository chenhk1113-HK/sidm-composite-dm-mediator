# REVIEWER_CONSIDER_DATA — Path-Proposal Audit of `Consider.docx` (T71.9 input)

> **Audit type:** Path-proposal (Series P from `reviewer-audit` skill)
> **Date:** 2026-09-02
> **Trigger:** User uploaded `Consider.docx` with framing "Consider the following for improving the project."
> **Status:** Critique-only; no code changes. Scope decision: **Defer with 2 v0.4-prelim experiments**.
> **Companion:** [v0.3-prelim/docs/V0_6_ROADMAP.md](V0_6_ROADMAP.md) (the standing deferred-items list).

---

## 1. Audit framing — what kind of doc is this?

`Consider.docx` (43 paragraphs, ~12 KB) is a **path-proposal** review, not a bug-finding audit. It proposes **6 new datasets / modules** that could strengthen the project's scientific plausibility, plus 5 priority-order recommendations.

Per `reviewer-audit` Series P:
- Bug-finding audits produce **fix lists** with P0/P1 severity tags.
- Path-proposal reviews produce **scope decisions** (Adopt / Defer / Reject) + tier-ranked recommendations.

This doc proposes additions, not bug fixes. The audit shape is the latter.

---

## 2. Verification matrix (5-label, per `reviewer-audit` Series W3 / V1)

I verified each of the 6 docx proposals against on-disk state per AGENTS.md rule 21 (verify reviewer claims against ground truth). Labels follow the V1 + W3 + Z1 5/6-label matrix.

| # | Docx proposal | Status | Evidence |
|---|---|---|---|
| 1 | "Add XENONnT (+ PandaX-4T) as parallel direct-detection channels" | ❌ **Stale — already-investigated-and-rejected** | `v0.3-prelim/docs/FINDINGS.md` Channel 5 row + `v0.3-prelim/code/channels_extended.py` module docstring (lines 9–30): "Direct detection experiments (LZ, XENONnT, PandaX) measure σ_DM-nucleon — the cross-section between dark matter particles and ordinary atomic nuclei. They do NOT measure σ_DM-DM, which is what SIDM σ/m quantifies. These are two completely different physical cross-sections." Project uses LZ as a **sanity check**, not a σ/m constraint. Decision was made at the 2026-08-10 peer review. |
| 2 | "Fold in Migdal-effect likelihoods for the low-mass tail" | ❌ **Stale — orthogonal-physics rejection applies** | Same reasoning as #1. Migdal targets sub-GeV DM via σ_DM-nucleon (neutron-calibration via XENON1T/XENONnT). The project's mass scale is ~800 GeV (T41 posterior median m_χ = 805 GeV), so the sub-GeV sensitivity window is irrelevant. Even with a light composite-DM extension, Migdal constrains σ_DM-nucleon, not σ_DM-DM. |
| 3 | "Incorporate the diffuse-dwarf clustering / assembly-bias result (Zhang et al. 2025 / arXiv:2504.03305)" | ✅ **Paper ID verified + genuinely-missing LSS channel** | arXiv:2504.03305 verified via web search 2026-09-02: "Unexpected clustering pattern in dwarf galaxies challenges formation models" (Nature 2025, accepted; 45 pp / 12 figs / 2 tables). Confirms SIDM core-size ↔ assembly-bias anti-correlation. Project's T18/T19/T20 already implements dwarf/cluster contrast (2777×) as 2-component diagnostic, but **no LSS / assembly-bias channel** exists. Item #3 is genuinely-missing and scientifically-motivated. |
| 4 | "Use SIDM Concerto / COZMIC suites to fix UFD KiSS-SIDM" | ⚠️ **Partially valid** + ⚠️ **wrong scope** | The project already uses **SASHIMI-SIDM** (per `channels_extended.py` + `d13_final_state_capture.py`) — a different high-resolution SIDM suite. The v0.6 roadmap item #17 (T71.7) flagged UFD KiSS-SIDM as **compute-prohibitive at single-session budget** (N=5e4 dwarf re-run TIMED OUT at 7200s with only 2/10 snapshots). Adding SIDM Concerto / COZMIC as a complementary suite is valid, but the **UFD timeout problem is architectural** (smaller N or fewer snapshots), not solved by switching simulators. |
| 5 | "Optionally add DAMPE spectra as extra indirect channel" | ✅ **Genuinely missing** (valid Tier 2 suggestion) | No DAMPE ingestion exists in `v0.3-prelim/code/`. The project has Fermi dwarfs (T31) but no cosmic-ray electron / γ spectra from DAMPE. Plausibly informative for the composite-sector annihilation/decay products. |
| 6 | "Skip doubly-charmed baryons, JUNO, Super-K" | ✅ **Already-correctly-rejected** | Docx correctly notes these are out-of-scope. Project has no SM heavy-flavor baryon, reactor-neutrino, or pure-neutrino channels. Agreement with the docx's own triage. |

**Summary:** The docx's **#1 recommendation** (XENONnT + PandaX as parallel DD channels) is **not just stale but actively wrong** — it would violate the project's standing orthogonal-physics rejection from 2026-08-10. The **#3 recommendation** (Zhang 2025 clustering) has a wrong paper ID and is partially duplicate of existing T18/T19 dwarf-cluster contrast work. **#4** (Concerto/COZMIC) is partially valid but the underlying UFD-KiSS-SIDM problem is architectural. Only **#5** (DAMPE) is a genuinely missing, scientifically-plausible addition.

---

## 3. Tier-ranking of docx proposals

### Tier 1 (adopt — high leverage, in scope, not duplicate)
**None.** The docx's #1 (XENONnT/PandaX) is rejected; the rest are either Tier 2 / out-of-scope / already-handled.

### Tier 2 (situational / lower-priority — adopt if compute allows)
- **DAMPE spectra as additional indirect channel** (Item #5): moderate effort (~1 week), informative for composite-DM sector e±/γ signatures. Defensible Tier 2 add.

### Tier 3 (defer / reject — already-handled or out-of-scope)
- **XENONnT / PandaX as parallel DD channels** (Item #1): rejected. Violates standing orthogonal-physics decision. **Do NOT re-open** without strong new evidence.
- **Migdal-effect likelihoods** (Item #2): rejected. Sub-GeV sensitivity window is irrelevant for m_χ ~ 800 GeV; same orthogonal-physics reasoning.
- **SIDM Concerto / COZMIC for UFD closure** (Item #4): partially valid as a *complement* to existing SASHIMI-SIDM, but the underlying UFD KiSS-SIDM TIMEOUT problem is architectural (per T71.7 verdict: N=5e4 re-run TIMED OUT at 7200s with 2/10 snapshots). Fix path is **smaller N or fewer snapshots**, not a new simulator.
- **Doubly-charmed baryons / JUNO / Super-K** (Item #6): correctly rejected by the docx itself.

### Tier 2 (adopt for v0.4-prelim — paper ID verified, genuinely missing)
- **Diffuse-dwarf clustering / Zhang 2025** (Item #3): LSS / assembly-bias channel is **not yet implemented** in the project and is scientifically motivated (arXiv:2504.03305 verified 2026-09-02). SIDM naturally explains the assembly-bias signature. ~2 weeks implementation; lower priority than DAMPE because it requires new measurement-type ingest (clustering-correlation likelihood) rather than re-using existing particle-spectrum channels.

---

## 3.1 Paper-ID verification for Item #3 — ✅ verified

The docx cites `arXiv:2504.03305`. The agent retrieved the arXiv abstract for this ID (web search 2026-09-02). The paper is **verified** and matches the docx's description exactly:

- **Title:** "Unexpected clustering pattern in dwarf galaxies challenges formation models"
- **Status:** Accepted for publication in Nature (45 pp, 12 figs, 2 tables)
- **Subject:** Cosmology and Nongalactic Astrophysics (astro-ph.CO); Astrophysics of Galaxies (astro-ph.GA)
- **Key finding:** Isolated diffuse blue dwarfs have unexpectedly strong large-scale clustering, comparable to massive galaxy groups but much stronger than expected from halo mass. The halo-bias model predicts a relative bias far below the observed value, indicating the difference cannot be explained by halo-mass differences alone.
- **SIDM connection (explicit in paper):** "if dwarf galaxies with lower [concentration] are associated with SIDM halos with larger cores (lower central densities), an anti-correlation between [concentration] and [bias] is expected." The paper concludes that **SIDM naturally explains the assembly-bias signature** in isolated diffuse dwarfs.

The paper ID is correct, the SIDM linkage is direct, and the LSS / assembly-bias channel is genuinely missing from the project. Item #3 is upgraded from ⚠️-unconfirmed to ✅-Tier-2.

---

## 4. Tier-ranking of the docx's "Recommended priority order"

The docx's recommended order is:
1. Add XENONnT (+ PandaX) as parallel DD channels, fold in Migdal.
2. Incorporate diffuse-dwarf clustering (Zhang 2025).
3. Use public high-res SIDM suites (SIDMConcerto, COZMIC).
4. Optionally DAMPE.
5. Skip doubly-charmed baryons, JUNO, Super-K.

**The agent's revised priority order** (after verification):

1. **Do nothing** on #1 (XENONnT / PandaX / Migdal). Standing decision.
2. **DAMPE ingestion** — Tier-2 v0.4-prelim experiment. Single new spectrum type; defensible scope (~1 week). Easiest first ship among the genuinely-missing items.
3. **LSS / assembly-bias channel (Zhang 2025 / arXiv:2504.03305)** — Tier-2 v0.4-prelim experiment, paper ID verified. New measurement-type ingest; ~2 weeks.
4. **SIDMConcerto / COZMIC** as a *complement* to existing SASHIMI-SIDM, not a replacement. Use for substructure / gravothermal prior tightening. ~2 weeks if started.
5. **Skip** doubly-charmed baryons, JUNO, Super-K. (Same as docx.)

---

## 5. Scope decision

**DEFER with 2 v0.4-prelim experiments.**

The docx's top recommendation (#1: XENONnT/PandaX as parallel DD channels) **violates the standing orthogonal-physics rejection** from the 2026-08-10 peer review and would constitute a backwards step in the project's scientific positioning. It must NOT be adopted.

The remaining items have been verified. Two are Tier-2 v0.4-prelim experiments (DAMPE, LSS-clustering), one is a complement-not-replacement (Concerto/COZMIC), and the rest are rejected (per the docx's own triage).

Recommended v0.4-prelim experiments:

1. **DAMPE ingestion proof-of-concept** — fetch DAMPE electron + proton spectra from public archive; check whether the secluded-mediator / composite-DM sector produces detectable hard-e± or γ-line signatures in the available energy range. (~1 week.) Easiest ship — single new spectrum type, defensible scope. If positive signal, full ingestion as a Tier-2 channel; if null, document and defer.
2. **LSS / assembly-bias channel (Zhang 2025, arXiv:2504.03305)** — new measurement-type ingest (clustering-correlation likelihood). ~2 weeks implementation. Paper ID verified 2026-09-02; SIDM linkage is direct in the paper.

Both experiments defer to **v0.4-prelim** (post-T71.8). Neither should be started in the current T71.x cycle.

---

## 6. What this critique does NOT recommend (and why)

| Docx suggestion | Why not adopted |
|---|---|
| XENONnT / PandaX as σ/m constraint channels | Already-rejected (FINDINGS.md, channels_extended.py); would violate standing orthogonal-physics decision. |
| Migdal-effect likelihoods | Sub-GeV sensitivity window is irrelevant for m_χ ~ 800 GeV; orthogonal physics. |
| SIDMConcerto / COZMIC as UFD KiSS-SIDM replacement | Underlying UFD TIMEOUT is architectural, not simulator-specific. Fix path is smaller N / fewer snapshots, not a new suite. |
| Doubly-charmed baryons / JUNO / Super-K | Out of scope; docx agrees. |

---

## 7. What this critique DOES recommend

1. ~~**Verify the Zhang 2025 paper ID** before any implementation work. Single web search.~~ ✅ Done — paper ID verified 2026-09-02 (arXiv:2504.03305, Nature 2025, accepted). Promoted to Tier-2 v0.4-prelim experiment.
2. **Add DAMPE as a v0.4-prelim Tier-2 channel** (proof-of-concept first; full ingestion if signal). ~1 week effort. Easiest ship.
3. **Add LSS / assembly-bias channel (arXiv:2504.03305) as a v0.4-prelim Tier-2 channel**. ~2 weeks effort. New measurement-type ingest.
4. **Treat the v0.6 roadmap #17 (UFD KiSS-SIDM timeout) as an architectural problem**: smaller N or fewer snapshots, not a new simulator. Already documented in V0_6_KISS_SIDM_TIMEOUT_VERDICT.md.
5. **Document the orthogonal-physics rejection** more prominently in `EXTRACT.md` and `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` so future reviewers / path-proposals don't re-propose the same idea. (Doc improvement; ~30 min.)

---

## 8. Cross-references

- **Standing orthogonal-physics decision**: `v0.3-prelim/code/channels_extended.py` lines 9–30 (Channel 5 docstring); `v0.3-prelim/docs/FINDINGS.md` Channel 5 row.
- **UFD KiSS-SIDM timeout verdict**: `v0.3-prelim/docs/V0_6_KISS_SIDM_TIMEOUT_VERDICT.md` (T71.7 closure).
- **Two-component dwarf/cluster contrast diagnostic**: `v0.3-prelim/code/t18_two_component_fit.py`, `t19_yang2026_fit.py`, `t20_two_comp_kiss_sidm_fit.py`; `v0.3-prelim/docs/FINDINGS.md` "Dwarf/cluster contrast" section.
- **V0.6 deferred-items list**: `v0.3-prelim/docs/V0_6_ROADMAP.md` (this critique adds no new items; recommends folding into existing #17 if DAMPE ingestion is approved).

---

## 9. Provenance

- **Trigger:** User-uploaded `Consider.docx` via Telegram DM, 2026-09-02.
- **Reviewer framing:** "Consider the following for improving the project" (path-proposal, per `reviewer-audit` Series P).
- **Reviewer type:** Unknown (no author tag visible in the docx). Docx is in Chinese + English (CJK titles for Migdal, XENONnT, CJPL, SURF, DAMPE, SNOLAB, Super-Kamiokande, Ξ_cc⁺, JUNO).
- **Agent's verification source:** Direct on-disk read of `v0.3-prelim/code/channels_extended.py`, `v0.3-prelim/code/t30_lz_real_posterior.py`, `v0.3-prelim/code/t18_two_component_fit.py`, `v0.3-prelim/docs/FINDINGS.md`, `v0.3-prelim/docs/V0_6_ROADMAP.md`. No external web search performed (paper-ID verification deferred).
- **Audit shape:** Series P path-proposal + Series W3 5-label matrix + Series V1 verified-state labels.

---

## 10. Status

| Item | Status |
|---|---|
| Critique doc shipped | ✅ This file |
| Standing orthogonal-physics decision | Preserved (NOT re-opened) |
| XENONnT / PandaX / Migdal | ❌ Rejected — orthogonal-physics rejection from 2026-08-10 peer review applies |
| DAMPE | ✅ Tier-2 v0.4-prelim experiment (proof-of-concept; ~1 week) |
| LSS / assembly-bias (arXiv:2504.03305) | ✅ Tier-2 v0.4-prelim experiment (paper ID verified 2026-09-02; ~2 weeks) |
| SIDMConcerto / COZMIC | Defer — complement to existing SASHIMI-SIDM; underlying UFD timeout is architectural, not simulator-specific |
| Doubly-charmed baryons / JUNO / Super-K | ✅ Docx correctly rejected; agreement |
| v0.6 roadmap impact | No new items; DAMPE / LSS-clustering fold into existing v0.4-prelim roadmap |

No code changes in this round. Critique-only shippable artifact.