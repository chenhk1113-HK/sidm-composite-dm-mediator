# Phase C (v19.2-C): KiSS-SIDM N-body at Cloud-9 — Status Report

**Date:** 2026-09-30
**Status:** BLOCKED on external dependencies
**Outcome:** Honest documentation + ScalaPoN recommendation

## Status: BLOCKED on TWO fronts

### Blocker 1 — SIDM Concerto (Nadler+ 2025, arXiv:2503.10748) does NOT cover Cloud-9-mass isolated halos

SIDM Concerto hosts:
- MW-mass: MW_Halo416 (M ~ 10^12 Msun)
- Group-mass: Group_Halo352, Halo820, Halo962 (M ~ 10^13-14 Msun)
- Cluster-mass: LCluster_Halo000 (M ~ 10^15 Msun)
- LMC-mass: LMC_Halo104 (M ~ 10^11 Msun)

Cloud-9 (M_200 = 5e9 Msun, dwarf-galaxy scale) is **2 orders of magnitude below**
the smallest Concerto host. Concerto's deepest subhalos reach M ~ 10^6 Msun
(1e-5 x host), which means they DO have subhalos in the Cloud-9 mass range —
but as substructures of MW-mass hosts, with environmental effects (tidal
stripping, harassment) that Cloud-9 (RELHIC near M94) may not have.

The data release is at https://zenodo.org/records/14933624
(DOI: 10.5281/zenodo.14933624, 171.6 GB total).

### Blocker 2 — KiSS-SIDM (Gurian & May 2025, arXiv:2505.15903) requires Julia + FIRE-2 ICs

KiSS-SIDM is publicly available at https://gitlab.com/Socob/KiSS-SIDM.
It is Julia code using DSMC (Direct Simulation Monte Carlo).

Requirements to run Cloud-9 N-body:
- Install Julia (1.11+) -- ~200 MB download + package resolution (Manifest.toml has 78k entries)
- Acquire FIRE-2 initial conditions in HDF5/gizmo format -- collaborator access needed
- Cluster compute for the run itself (multi-day per the paper text)

Neither Julia nor FIRE-2 ICs are in our v0.3-prelim environment.

## Honest framing (per no-shortcut protocol + Rule 28)

The existing paper text already acknowledges v19.2 limitations:
> "What was NOT done (deferred to v19.2): Actual GIZMO N-body reproduction
> of Silverman+ 2026's 6-halo suite at Cloud-9 parameters requires FIRE-2
> ICs and multi-day cluster runs; merger-history parameterization for
> the 3-of-6 collapse prediction."

This was honest at v19.1 and remains honest at v19.2.

## Options (for user to choose when ready)

### Option A: Concerto subhalo analysis (no new deps, ~2 hours)
- Download MW_Halo416_MilkyWaySIDM parametric.tar (11.8 MB)
- Extract subhalos in mass range 1e8-1e9 Msun (Cloud-9-like)
- Compare our framework's sigma/m_peak predictions to Concerto's actual SIDM
  subhalo profiles
- Caveat: subhalos experience tidal effects Cloud-9 doesn't, so any match
  is suggestive not definitive

### Option B: Document N-body blocker, close v19.2-C
- Update PAPER_STANDING_NUMBERS.md §5 with current status
- Update §11 conclusions to flag N-body as future work requiring
  collaborator access to FIRE-2 ICs
- Move v19.2-C to "out of scope for this paper" and note it in the
  "future directions" comment for the next open research question

### Option C: Install Julia + KiSS-SIDM for proper Cloud-9 N-body
- pip/conda install Julia (large install)
- git clone KiSS-SIDM (done: external/KiSS-SIDM/)
- Acquire FIRE-2 ICs (NOT available without collaborator)
- This option is BLOCKED on FIRE-2 ICs regardless of Julia availability

**Status: STOPPED HERE** per no-shortcut protocol (no Option B without
explicit user approval). Awaiting user direction.

## What was done in this session

- Cloned KiSS-SIDM at external/KiSS-SIDM/ for future reference (no compilation attempted)
- Verified Concerto data release is on Zenodo (https://zenodo.org/records/14933624)
- Verified Nadler+ 2025 (arXiv:2503.10748) paper covers hosts down to LMC-scale, no isolated Cloud-9-mass
- Created this status report at v0.3-prelim/docs/PHASE_C_STATUS_2026_09_30.md

## Recommendation

**Recommend Option A** (Concerto subhalo analysis) as the highest-leverage path
that doesn't require new dependencies. Can ship within one session. Matches the
"simple first" pattern of v19.2-B v2.