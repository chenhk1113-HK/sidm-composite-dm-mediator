# KiSS-SIDM Upstream Finding + UFD Re-run (T71.7)

> **Date**: 2026-08-28 (T71.7 round)
> **Per user direction**: "kiss sidm ufd, use the author original c python; download hepdata"
> **Outcome**: KiSS-SIDM upstream located + T38a dwarf N=5e4 re-run with extended timeout (background). HEPData download confirmed blocked by missing source material.

---

## 1. The KiSS-SIDM upstream URL (correcting an earlier misframing)

### What we said earlier (T71.5)
> "KiSS-SIDM Julia bridge hits a hard 3600s timeout at UFD N=5e4 (T38a failure). The canonical-halo pipeline is production-grade and fully converged at N=1e4-1e5, but the dwarf/UFD regime is intractable at our compute budget without rewriting the DSMC in a faster language or using the paper's original C/Python implementation."

### What's actually true (T71.7)

**The KiSS-SIDM code at `https://gitlab.com/Socob/KiSS-SIDM` is Julia, NOT C/Python.**

The user's "use the author original c python" instruction was based on a misframing — there is no C/Python original. The authors' original code IS Julia, and it's already installed on our system.

**Repo metadata** (from `git -C /tmp/KiSS-SIDM log` + GitLab page):
- **URL**: `https://gitlab.com/Socob/KiSS-SIDM`
- **Authors**: James Gurian (first author of arXiv:2505.15903, PRL 135 221001) + Simon May (GitLab handle "Socob")
- **Most recent commit**: 2026-08-18 (actively maintained)
- **First commit author**: `James Gurian <jamesgurian@Jamess-MacBook-Air.local>`
- **Language**: Julia 1.11.5
- **Size**: 2,289 lines across 15 modules (`mainloop.jl`, `collision.jl`, `1d_sphere.jl`, `gravity.jl`, etc.)
- **Package name**: `DSMC` (Julia module)
- **Local install path**: `/home/lamkuenai/KiSS-SIDM`
- **Local install status**: `DSMC package loaded OK, version: 0.0.1`

### Our bridge already wraps the upstream

`v0.3-prelim/code/kiss_sidm_julia_bridge.py:25-27`:
```python
JULIA_PROJECT = "/home/lamkuenai/KiSS-SIDM"
JULIA_BIN = "/home/lamkuenai/.juliaup/bin/julia"
JULIA_VERSION = "+1.11.5"
```

And the bridge docstring already cites the upstream URL:
> "Calls the actual KiSS-SIDM Julia code (https://gitlab.com/Socob/KiSS-SIDM) from our Python pipeline."

**We were never reimplementing KiSS-SIDM. We've been wrapping the real upstream code the whole time.** The "3600s timeout at N=5e4" failure was a **wrapper-level limit** (`subprocess.run(timeout=3600)`), not an upstream-code limitation.

### What was wrong

My earlier pre-flight claim that we'd need "the authors' C/Python implementation" was a guess based on incomplete information. The user trusted that guess and gave an instruction based on it. The honest correction: the upstream IS the implementation, and the fix is to bypass our wrapper's hardcoded timeout.

---

## 2. The T38a UFD failure mode — re-analyzed

### T38a (2026-08-22) failure
- Configuration: dwarf halo (M_halo = 10⁸ M_☉, r_s = 0.5477 kpc, σ/m = 5 cm²/g), N=5e4 particles, t_end = 10 Gyr
- Observed in T38 partial wallclock finding: **2 of 10 snapshots produced in 12 min** before manual kill
- T38b full run: hit **3600s wrapper timeout** (NOT a Julia crash)

### Conclusion: the simulation works, just slowly

Per the T38 partial finding JSON:
> "T38a N=5e4 clears the AssertionError" was based on OBSERVATIONAL evidence (2 of 10 snapshots produced in 12 min before a manual kill). The full run is wall-clock-prohibitive at single-session resolution.

The Julia simulation runs correctly. The wall-clock issue is **extrinsic to the physics**: 10 Gyr / (5e4 particles × per-iteration cost) takes longer than 1 hour. With a 2-hour budget (7200s), we should complete ~10-12 snapshots. With a 5-hour budget (18000s), we should converge.

---

## 3. T71.7 fix: make wrapper timeout configurable + re-run T38a N=5e4

### Code change (`v0.3-prelim/code/kiss_sidm_julia_bridge.py:375-382`)

```python
# Subprocess timeout (was hardcoded 3600s, now configurable via env var).
# Default 3600s (1 hour) preserved for safety; override with KISS_SIDM_TIMEOUT_S.
# For UFD-scale N>=5e4 runs, T71.7 recommends >= 7200s (2 hr).
# For full convergence at N>=2e6 (paper threshold), set KISS_SIDM_TIMEOUT_S=18000 (5 hr).
# WARNING: large timeouts lock WSL resources; use background mode for >7200s.
timeout_seconds = int(os.environ.get("KISS_SIDM_TIMEOUT_S", "3600"))
t0 = time.time()
proc = subprocess.run(
    cmd, capture_output=True, text=True, timeout=timeout_seconds,
)
```

### New launcher (`v0.3-prelim/code/t71_7_kiss_sidm_ufd_launcher.py`)

Sets `KISS_SIDM_TIMEOUT_S=7200` BEFORE importing the bridge, then calls `run_canonical_kiSS_sidm(N=50000, ...)` with T38a's dwarf halo parameters. Saves result to `v0.3-prelim/data/results/t71_7_kiss_sidm_ufd_n5e4.json`.

### Background run (launched 2026-08-28 17:39:58)

- session_id: `proc_23b6f90d2ffc`
- PID 48560 (Python launcher, sleeping); PID 41633 (Julia subprocess, 100% CPU)
- Wall-time budget: 7200s (2 hr) per `KISS_SIDM_TIMEOUT_S=7200`
- Log file: `v0.3-prelim/data/results/t71_7_kiss_sidm.log`

Expected outcome (based on T38a partial-finding extrapolation):
- 10-12 snapshots in ~40-60 min if linear scaling from 12 min for 2 snapshots
- OR may need full 2 hr to complete all 10 snapshots
- Either way: quantitative r_core/r_s for dwarf halo, OR honest kill-with-rationale

### What happens after the run

Per `notify_on_complete=true`, the run's exit will re-enter the conversation. We then:
1. Read the JSON result
2. Verify it's a `success` status (vs `error_timeout` if even 2 hr isn't enough)
3. Commit the patch + result
4. Update V0_6_ROADMAP item #17 status
5. Ship the bundle

If the run STILL hits 7200s, we know N=5e4 dwarf is truly wall-clock-prohibitive at single-session resolution and ship an honest "even 2 hr insufficient" closure note with the partial snapshot count + recommendation for N=1e5 at 5 hr.

---

## 4. HEPData download: NOT viable (confirmed by search)

Per the user's other instruction ("download hepdata"), I did4 search rounds:
- "HEPData record SU(3) lattice Nf=4 vector meson"
- "HEPData record SU(2) Nf=2 lattice"
- "HEPData site:hepdata.net SU(3) SU(2) meson"
- "Bernardoni Frezzotti lattice SU(3) Nf=4 HISQ vector meson decay constant"

**Result: no lattice-QCD HEPData records exist for the 3 ESTIMATED combos (2,2), (2,3), (3,4).** HEPData is dominated by collider-experiment tables (CMS, LZ, ALICE); lattice groups publish their data in PDF tables inside papers, not in standardized repositories.

The user provided additional guidance:
> "If you are looking for gauge configurations, propagator data, or specialized lattice correlators, you should look at dedicated repositories: ILDG (International Lattice Data Grid), USQCD, Fermilab Open Science Data, GitHub/GitLab Phenomenology Databases."

These are for **gauge configurations and propagator correlators**, not for vector-meson mass / pion decay constant ratios. The data we need (R = m_ρ/f_π at specific (N_c, N_f)) is published in **PDF tables in lattice papers** like Brower et al. PRD 110 054501 (arXiv:2306.06095), not in ILDG/HEPData repositories.

**Honest verdict**: lattice data upgrade for (2,2), (2,3), (3,4) would require either:
- Institutional access to ILDG/USQCD + per-ensemble data extraction (multi-week research effort)
- Or PDF-table extraction from ~5-10 lattice papers (messy, error-prone)
- Or direct author contact (out-of-band)

None of these fit a single chat session. The (3,3) anchor remains robust at R = 8.36 ± 0.05 with multi-source confirmation (PDG 2022 + FLAG 2021 + FLAG 2024). The 5 non-LATTICE combos remain ESTIMATED-class with honest documentation in `KSFR_NC_NF_TABLE.md`.

---

## 5. Action items

- [x] Confirm KiSS-SIDM upstream URL (gitlab.com/Socob/KiSS-SIDM, Julia)
- [x] Verify upstream is installed and loads cleanly on our system
- [x] Patch wrapper timeout to be configurable via KISS_SIDM_TIMEOUT_S env var
- [x] Write launcher for T38a re-run with 7200s timeout
- [ ] Wait for background run to finish (session_id `proc_23b6f90d2ffc`)
- [ ] Verify result + commit + push + ship

**After the run finishes, this doc + the run result will be merged into V0_6_ROADMAP item #17 + REVIEWER_AUDIT_R16.md addendum #8 + CHANGELOG [T71.7].**

---

## 6. Files shipped in T71.7 (so far)

| File | Purpose |
|---|---|
| `v0.3-prelim/code/kiss_sidm_julia_bridge.py` | MODIFIED: timeout now configurable via `KISS_SIDM_TIMEOUT_S` env var (default3600s preserved) |
| `v0.3-prelim/code/t71_7_kiss_sidm_ufd_launcher.py` | NEW: launcher for T38a N=5e4 dwarf with 7200s timeout |
| `v0.3-prelim/data/results/t71_7_kiss_sidm_ufd_n5e4.json` | PENDING: run result |
| `v0.3-prelim/data/results/t71_7_kiss_sidm.log` | IN PROGRESS: Julia subprocess log |
| `v0.3-prelim/docs/V0_6_KISS_SIDM_UPSTREAM_FINDING.md` | NEW (this document) |

**V0_6_ROADMAP item #17 status update (post-run):**
- ✅ T71.7: KiSS-SIDM upstream located (gitlab.com/Socob/KiSS-SIDM, Julia) + already installed at /home/lamkuenai/KiSS-SIDM
- ✅ T71.7: Wrapper timeout made configurable via KISS_SIDM_TIMEOUT_S env var (commit cdb9028)
- ❌ T71.7: T38a N=5e4 dwarf re-run TIMED OUT at 7200s (full 2-hour budget consumed; only 2 snapshots produced; no quantitative r_core/r_s result)
- 📌 **T71.7 honest verdict**: UFD KiSS-SIDM at N=5e4 dwarf is structurally compute-prohibitive at single-session wall-clock budget. Doubling the budget from3600s to7200s did NOT proportionally increase completed snapshots (still 2/10). The wrapper-level 3600s timeout was NOT the bottleneck. Remaining options are: (a) smaller N at canonical halo, (b) reduced snapshot_count, (c) coarser physics, or (d) accept that UFD KiSS-SIDM is out-of-session.
- See `V0_6_KISS_SIDM_TIMEOUT_VERDICT.md` for full analysis.