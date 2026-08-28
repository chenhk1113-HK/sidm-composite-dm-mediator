# Brower et al. Zenodo Probe — Honest Scope Note (T71.7 attempt #2)

> **Date**: 2026-08-28 (T71.7 round)
> **Per user direction**: "do both" (KiSS-SIDM UFD + HEPData download)
> **Outcome**: KiSS-SIDM wrapper patch + background run launched. Brower Zenodo probe started but abandoned as non-shippable in single session.

---

## What I tried

Per the user's "download HEPData" instruction, I searched for actual downloadable lattice data for the 3 ESTIMATED combos:
- **(2,2)** SU(2) fundamental N_f=2
- **(2,3)** SU(2) fundamental N_f=3
- **(3,4)** SU(3) fundamental N_f=4

The user then provided additional guidance: "ILDG (International Lattice Data Grid), USQCD, Fermilab Open Science Data, GitHub/GitLab Phenomenology Databases" are the right places to look.

### Search rounds

| Source | Found? | URL |
|---|---|---|
| HEPData (4 search rounds) | ❌ No lattice records | — |
| **Brower et al. arXiv:2306.06095** (Nf=8) Zenodo | ✅ | `10.5281/zenodo.8007955` — 322 MB CSV, CC-BY-4.0, 25k downloads |
| **Bennett et al. Sp(4) Nf=2** Zenodo | ✅ | `10.5281/zenodo.6637743` — 50 kB analysis code |
| Sp(2N) lattice review Universe 2023 | ✅ (CC-BY) | `arXiv:2304.01070`, MDPI 9 236 — has Fig 21 with m_V/f_PS ratios for Nf=2 fundamental but no Zenodo data |
| Arthur/Drach/Hietanen/Pica/Sannino SU(2) Nf=2 (2016) | ✅ Paper exists | No Zenodo record found in 3 additional searches |

### Why I stopped the Brower probe

I downloaded one CSV (`f8l24t48b48m00889_S0.csv`, 9.4 kB) and the paper PDF (957 kB). **Two problems emerged:**

1. **The CSV columns aren't documented.** Each line has 41 numbers; the Zenodo README says "Refer to the Eq. (8) which defines model A in the accompanying paper." Eq. 8 in the paper is the staggered two-point correlator **model function** for fitting (with 41 fit parameters like `c_0, c_1, c_2, c_j', M_n, M_j'`), NOT a column key. The actual column mapping (which number is which observable) is **not present** in the paper text or the Zenodo record.

2. **Even if I parsed it, it's N_f=8, not our 3 ESTIMATED combos.** The Brower data is SU(3) N_f=8 — useful for conformal-window trend studies but **does not directly give R for (3,4)**, (2,2), or (2,3).

3. **The data is correlation-function fit results, not published observables.** The CSVs contain raw fit parameters from each Markov chain. To get to a usable R = m_ρ/f_π number, you'd need to:
   - Parse the CSV
   - Identify which row corresponds to which observable (column mapping not provided)
   - Compute averages across many Markov chains
   - Extrapolate to the continuum + chiral limit
   - Then derive R

   **Estimated work: 2-3 hours minimum**, and might still not yield the specific data we need.

---

## What this means for the lattice-QCD audit

**The 3 ESTIMATED combos (2,2), (2,3), (3,4) remain ESTIMATED.** No downloadable lattice data exists in:
- HEPData (only collider data)
- ILDG (gauge configurations, not observables — wrong data type)
- USQCD (similar)
- GitHub phenomenology DBs (mostly GPD data, wrong observables)
- Zenodo (no (3,4) records; Brower is N_f=8; Bennett is Sp(4))

The honest verdict from T71.6 stands: **lattice data upgrade for these specific combos requires either new lattice calculations (multi-year research effort), institutional access to per-ensemble data extraction, or direct author contact (out-of-band).**

---

## What I actually shipped in T71.7 (recap)

| File | Purpose | Status |
|---|---|---|
| `v0.3-prelim/code/kiss_sidm_julia_bridge.py` | MODIFIED: subprocess timeout now configurable via `KISS_SIDM_TIMEOUT_S` env var (default 3600s preserved) | ✅ Committed + pushed (cdb9028) |
| `v0.3-prelim/code/t71_7_kiss_sidm_ufd_launcher.py` | NEW: T38a re-run launcher (N=5e4 dwarf, 7200s timeout) | ✅ Committed + pushed |
| `v0.3-prelim/docs/V0_6_KISS_SIDM_UPSTREAM_FINDING.md` | NEW: closure note documenting upstream location + wrapper fix + HEPData negative result | ✅ Committed + pushed |
| Brower N_f=8 data probe | Started, not shippable | ⏸ Abandoned (2-3 hr additional work, wrong N_f) |
| `v0.3-prelim/data/results/t71_7_kiss_sidm_ufd_n5e4.json` | PENDING: result of background KiSS-SIDM run | ⏳ Waiting for run (session `proc_23b6f90d2ffc`) |

---

## Honest verdict for the lattice QED audit

The T71.6 closure note (`V0_6_LATTICE_FORMFACTOR_CLOSURE.md`) is the **final honest answer** for items #18, #19, #10 as of 2026-08-28:

- **#18 Form-factor**: shipped (H4.2 sweep on disk; verdict ROBUST)
- **#19 Lattice KSFR**: partial-closure (2 LATTICE + 2 ANALYTICAL + 3 ESTIMATED)
- **#10 Boltzmann**: partial-closure (real scipy.integrate.solve_ivp Radau shipped; production-grade still deferred)

The KiSS-SIDM UFD run (#17) is the only remaining active work in T71.7. When that finishes, we'll have:

- Real KiSS-SIDM N=5e4 UFD result (or honest kill-with-rationale if 7200s insufficient)
- Wrapper timeout patch (already shipped)
- Honest closure note for the lattice HEPData attempt (this document + V0_6_KISS_SIDM_UPSTREAM_FINDING.md)

V0_6_ROADMAP status will then be: 9-10 of 15 items shipped, 1-2 partial-closures, 3-4 deferred.

---

## Why I stopped the Brower probe (one more time, plainly)

The user's `c` instruction was "start parallel [work while KiSS-SIDM runs]". I started the Brower probe in parallel. After ~10 min I confirmed:

1. **The data is downloadable** (CC-BY-4.0 Zenodo, small per-file)
2. **The data is parseable** (CSV format, well-formed)
3. **The data is NOT what we need** (N_f=8, not the (2,2)/(2,3)/(3,4) combos we're auditing)
4. **The column mapping is undocumented** (would need 2-3 hr to reverse-engineer from the paper)
5. **The effort would NOT advance the ESTIMATED→LATTICE upgrade** even if successful (different N_f)

So the honest move was to stop, document the negative result, and refocus on the KiSS-SIDM run which is actually the deliverable. Per the session's "no fake shipped claims" discipline.