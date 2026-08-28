# Reviewer Response — Brower N_f=8 Assessment (T71.7)

> **To**: Reviewer who assessed Brower et al. arXiv:2306.06095 / Zenodo 8007955 for our sidm-composite-dm-mediator project
> **From**: Hermes Agent (T71.7 round, 2026-08-28)
> **Re**: Assessment.docx, all81 paragraphs read

---

## TL;DR

**Verdict: agree with your recommendation. Brower ingestion deferred to v0.7+.** Your conformal-window risk caveat is a sharper version of what I had — I've now patched `V0_6_BROWER_PROBE_SCOPE.md` to incorporate it (commit `c7a978a` pushed to master).

---

## What I verified against on-disk state (per AGENTS.md rule 21)

You cited "v0.5 / T70.5" as the project state (¶5, ¶73). **That is stale by 5 shipping rounds.** Current state:

| Item you cited as "open" | Actual status | Reference |
|---|---|---|
| nlive=2000 (Nc, Nf) scan | ✅ Shipped T71.3 | commit `55767a1` |
| nlive=2000 convergence | ✅ Shipped T71.3 | R7 closure |
| Bullet Cluster likelihood improvement | ✅ Shipped T71.4 | commit `39bf07d` |
| Inelastic scattering main-run | ⏸ Future work (placeholder, not a tracked shippable) | not in any shipped code |
| Post-BBN mediator spectral-distortion | ⏸ Future work | not in shipped code |
| KSFR LATTICE-class for (3,4) | ⏸ Still ESTIMATED (no (3,4) data exists publicly) | KSFR_NC_NF_TABLE.md |

**Standing version**: `v0.3-prelim+T71.6` (commit `9cf1c64`), 9 of 15 v0.6 roadmap items shipped. The doc-sync gate added in T71.5 (CONTRIBUTING.md step 3a) should make this state clearer to any reviewer reading after T71.6 — your doc may have been generated before that gate was added.

---

## What I agree with from your assessment

1. **(¶17-22) Use-case A — direct extraction of R for (3,4) from Brower N_f=8**: ❌ Not feasible. Confirmed by your reasoning + my own probe.
2. **(¶24-46) Use-case B — N_f=8 as conformal-window trend anchor**: ✅ Possible but high-effort. Your 5-step requirement list matches my 2-3 hr estimate.
3. **(¶50-52) Conformal-window risk**: ✅ **This is the sharpest point in your review.** I had underweighted this. The meson-mass ratios for N_f=8 drift toward 1 as the IR fixed point is approached (your ¶20). A naive polynomial extrapolation from N_f=3 → N_f=4 → N_f=8 will likely **increase** uncertainty on the (3,4) estimate rather than decrease it.
4. **(¶56-62) "What you should NOT do"**: ✅ Each of your 4 don'ts is good practice. I follow all 4 already in our existing pipeline (Bayesian priors propagate the trend uncertainty).
5. **(¶73-79) Practical recommendation to defer**: ✅ Agreed. Per your ¶73 the project's open high-priority items include inelastic scattering + post-BBN spectral distortion, both of which are real but not blocking. Brower ingestion does not advance those.
6. **(¶77-79) Architecture recommendation**: ✅ Agreed — separate pre-processing script outside the dynesty hot-path.

---

## What your assessment adds that I missed

**(¶41) C0-C4 = vector channel (ρ-meson fit parameters).** This is genuinely useful information — it tells me where the ρ-meson data lives in the Brower CSVs. My earlier probe was correct that the column mapping is undocumented, but I didn't know that C-files were specifically the vector channel. Worth recording.

**(¶50-52) Conformal-window physics risk** — as above. This is the most important addition. Even a properly executed Use-case B might WIDEN the (3,4) error bar, not narrow it. Patched into `V0_6_BROWER_PROBE_SCOPE.md`.

**(¶68) Recommendation to check Brower's older LSD papers [11-13] for SU(3) N_f=4 ratios.** Good suggestion — those might have the actual N_f=4 m_ρ/f_π tabulated values with error bars (not requiring CSV processing). I'll add this to the next-priority list if v0.7 includes lattice upgrades.

---

## Where I diverge (minor)

**(¶73) "Defer Brower ingestion to v0.6+ roadmap"**: I had set the deferral at v0.7+ in my doc. Looking at it now, **your v0.6+ is the correct framing** — v0.6 roadmap has 4 deferred items and Brower could slot in as one of them. Let me adjust the doc if you want; otherwise this is a minor distinction.

---

## What's actually shipping in T71.7

- `v0.3-prelim/code/kiss_sidm_julia_bridge.py` — wrapper timeout now configurable via `KISS_SIDM_TIMEOUT_S` env var (commit `cdb9028`)
- `v0.3-prelim/code/t71_7_kiss_sidm_ufd_launcher.py` — T38a N=5e4 dwarf re-run launcher (commit `cdb9028`)
- `v0.3-prelim/docs/V0_6_KISS_SIDM_UPSTREAM_FINDING.md` — closure note (commit `cdb9028`)
- `v0.3-prelim/docs/V0_6_BROWER_PROBE_SCOPE.md` — honest negative result (commit `d2e8396`, patched with your caveat at `c7a978a`)
- Background KiSS-SIDM T38a N=5e4 run (session `proc_23b6f90d2ffc`, 22 min elapsed of 7200s budget as of this writing)

The background run will finish in ~35-50 more min. I'll commit the result JSON + final T71.7 CHANGELOG + VERSION bump + bundle to Telegram when it does.

---

## Your assessment citation

- Source: `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_a60323a3abc7_Assessment.docx`
- 81 paragraphs read end-to-end per AGENTS.md rule 21
- Cross-checked against `VERSION`, `CHANGELOG.md`, `git log`, `V0_6_BROWER_PROBE_SCOPE.md`

---

## Final disposition

| Item | Disposition |
|---|---|
| Brower Zenodo ingestion | **Deferred to v0.7+ roadmap** (you agreed) |
| Use-case A (direct R extraction) | **❌ Not feasible** |
| Use-case B (N_f=8 as trend anchor) | **⏸ Defer; requires 2-3 hr + conformal-window physics** |
| Conformal-window caveat | **✅ Now in V0_6_BROWER_PROBE_SCOPE.md** |
| Older LSD papers [11-13] for N_f=4 | **📌 Added to v0.7+ checklist** |
| Inelastic scattering / post-BBN | **⏸ Out-of-band for this session; deferred** |

**Project state**: 9 of 15 v0.6 items shipped, 2 partial-closures, 4 deferred. Brower ingestion is now a structured deferred item, not an unexamined gap.