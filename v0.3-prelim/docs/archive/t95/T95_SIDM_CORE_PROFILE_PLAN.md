# T95 — SIDM Core Profile + Gas Morphology Branch Plan

**Status:** PLANNED (Phase 0 in progress)
**Date:** 2026-09-07
**Trigger:** `bok halo.docx` upload — research-workflow proposal for SIDM astrophysical studies
**Author:** T90.1 follow-up

---

## TL;DR

Run a SIDM hydro simulation of a Milky-Way-like dwarf galaxy using
the master's Yukawa σ/m(v) prescription, produce mock ALMA
observations, and compare against real ALMA data for Draco /
Fornax / Sculptor. Add the result as **Channel 27** in the master
joint fit.

**Headline answer to "is bok doc useful for the project":**
**Yes, after reframing.** The doc is a research program, not a
checklist. Two of its suggestions are real wins (SWIFT cross-check,
Gaia stream gaps); one requires new infrastructure (MARTINI mock-obs);
the rest are out of scope (Bok globule shape-shift, dissipative
SIDM, sub-halo population modeling).

**MARTINI's proper home is here, not in T90.** T90 is LZ
direct-detection. T95 is astrophysical gas morphology. They are
different physics, different observables, different scales.

---

## What bok doc actually offers

The `bok halo.docx` upload (2026-09-07) is a research-workflow
proposal in two languages (English + Chinese). Three layers:

1. **Mechanism proposals**: sub-halo tidal deformation, Jeans
   instability modification, CDM drag/sequestration.
2. **Data sources**: SWIFT, FIRE-2, Gaia DR3/4, ALMA archives.
3. **Tools**: swiftsimio, GIZMO-Analysis, MARTINI, powderday,
   spectral-cube, galpy/Gala.

After re-reading, the project's master already uses:
- `sidmkit` + `sidm-vdsigmas` (point-wise σ/m benchmarks, T89)
- Analytic Yukawa σ/m(v) (Born approx)
- SPARC rotation-curve hierarchical fits (galaxy-scale gravity)
- Euclid Q1 lensing forward model (cluster-scale gravity)

**The gap**: master has the σ/m prescription but never tests
whether it predicts what galaxies actually look like in gas or
stars. T95 is the test.

---

## Plan: T95 — SIDM Core Profile + Gas Morphology

### Scope (one sentence)

Run a SIDM hydro sim of a Milky-Way-like dwarf using the
master's Yukawa σ/m(v), produce mock ALMA cubes via MARTINI,
compare against real ALMA data for Draco / Fornax / Sculptor,
and add a galaxy-morphology channel to the master joint fit.

### Phased structure

**Phase 0 (~1 week) — SWIFT halo cross-check, NO new deps**
- Pull publicly available SWIFT SIDM halo snapshots at σ/m ≈
  0.1 cm²/g from DiRAC (per bok doc refs [4,6,7])
- Use `h5py` (already in project) to extract ρ(r) profiles
- Compute master's predicted core radius from Yukawa at same
  σ/m
- **Deliverable**: 1-page memo on agreement / disagreement
- **Gating**: if Yukawa disagrees with SWIFT by >3×, master
  needs σ/m fix before any new branch

**Phase 1 (1-2 weeks) — GIZMO install + zoom-in ICs**
- Install GIZMO (public, well-maintained)
- **User approval required** (AGENTS.md rule 17/24)
- Acquire zoom-in ICs from FIRE-2 public Latte suite
- Run CDM-only control simulation as smoke test
- **Deliverable**: working GIZMO pipeline reproducing a
  known CDM dwarf density profile

**Phase 2 (~1 week + 1-7 day compute) — SIDM re-simulation**
- Substitute master's Yukawa σ/m(v) for CDM in GIZMO
- Re-run same zoom-in
- Extract: density profiles, gas morphology, σ_gas(r), core
  size, central density slope
- **Deliverable**: SIDM-rerun snapshot + ρ(r) and σ_gas(r)

**Phase 3 (~1 week) — MARTINI mock ALMA + real ALMA compare**
- Install MARTINI
- **User approval required** (AGENTS.md rule 17/24)
- Pull real ALMA data for Draco from ALMA Science Archive
- Compare: moment-0 maps (gas column density), moment-1
  maps (velocity field), line-width profiles
- **Deliverable**: quantitative comparison report —
  χ² or KS test on morphology, half-light radius, central
  density

**Phase 4 (~1 week) — Channel 27 in master joint fit**
- Add `loglike_dwarf_gas_morphology()` likelihood to
  `channels_extended.py` (or new module)
- Wire into `t41_mediator_mass_joint_fit.py` behind env
  var `T95_GAS_MORPHOLOGY_CHANNEL=1` (matches T90 gating
  pattern)
- Re-run 6D and 7D fits
- **Deliverable**: updated fit results + doc on channel-27
  contribution

---

## Total cost and dependencies

| Item | Effort | New dep? | Approval needed? |
|---|---|---|---|
| Phase 0 SWIFT cross-check | 1 week | None | No |
| Phase 1 GIZMO install + IC | 1-2 weeks | **GIZMO** | **Yes (rule 17/24)** |
| Phase 2 SIDM re-sim | 1 week + 1-7d compute | None (uses GIZMO) | Compute resources |
| Phase 3 MARTINI + ALMA | 1 week | **MARTINI**, `spectral-cube` | **Yes (rule 17/24)** |
| Phase 4 Channel 27 + fit | 1 week | None | No |
| **Total** | **6-8 weeks + compute** | **3 new packages** | **2 approval gates** |

---

## What bok doc's other suggestions get used for

| Suggestion | T95 home | Out of scope |
|---|---|---|
| SWIFT SIDM simulations | **Phase 0** cross-check | — |
| FIRE-2 dDM (dissipative) | Not in T95 (different model) | Future-work note |
| Gaia DR3 GD-1 / Pal 5 | Possible **T95.5** (stream gaps) | T95 core = gas |
| ALMA Bok globule (B335, Barnard 68) | Not T95 (needs sub-halo pop) | T96? |
| **MARTINI** | **Phase 3** mock-obs | — |
| powderday | T95.5 candidate (stellar) | T95 core = gas |
| `spectral-cube`, Astropy | **Phase 3** | — |
| `swiftsimio` | Optional Phase 0 helper | — |
| `galpy`, Gala | T95.5 stellar streams | — |

**Bok doc is mostly used.** Bok globule shape-shift and
dissipative SIDM are out of scope for T95 (different physics,
different observables).

---

## Honest scope-of-MARTINI clarification

A reviewer might ask: "Why MARTINI, not powderday?" Both do
mock-observation. The answer:

- **MARTINI**: works with AMR codes (GIZMO, AREPO), uses
  adaptive mesh for ray-tracing through gas. Best for HI/CO
  lines. **Right tool for our Draco CO(1-0) / CO(2-1) target.**
- **powderday**: works with SPH codes (GADGET), uses
  Monte-Carlo dust radiative transfer. Best for dust+SED
  predictions, not line emission.

T95's primary target is **CO line emission** from Draco gas.
MARTINI is the right tool. powderday would be the right tool
**only if** we pivoted to predicting dust/SED morphology
(T95.5+).

---

## Risk assessment

**Highest risks:**

1. **Master's Yukawa prescription might be wrong by factor
   2-4.** T89 benchmark already showed factor 2-4 between
   project Yukawa and sidmkit's Born approximation (different
   conventions, distinguishable vs identical particles). If
   Phase 0 SWIFT cross-check shows the master prediction is
   off by 3× from SWIFT, **we have to fix the σ/m
   prescription first** before any new branch.
2. **GIZMO is a large code with many compile options.** The
   SIDM-in-dark-sector modification is non-trivial. Need to
   verify the code actually uses our σ/m and not a default.
3. **Compute resources.** A zoom-in with full baryonic
   physics (cooling, star formation, feedback) is days of
   wall-clock on 32+ cores. If no cluster allocation, this
   is the showstopper.
4. **LZ 248 keV event confirmation timing.** If T95 runs to
   completion and master wants to merge, but LZ community
   hasn't confirmed, T95 should follow the same merge-gating
   rule as T90 (no merge until community confirmation OR
   7D fit shows Δlog Z ≥ +2).

**Lower risks:**

- MARTINI is well-maintained, mostly Python, easy install.
- ALMA archive is mature, query interface stable.
- Real Draco CO data is published (multiple papers), easy
  to pull.
- All other Python deps (`h5py`, `numpy`, `scipy`, `astropy`)
  are already in the project.

---

## When to start T95

**My recommendation: start Phase 0 now.** Phase 0 is
zero-dependency, bounded, and produces a critical sanity
check (does our σ/m match what a serious hydro sim says
about galaxy cores?).

**If Phase 0 says "yes"**: T95 is worth doing in full.
Proceed to Phase 1 (GIZMO install — needs user approval).

**If Phase 0 says "no, off by 3×"**: master needs σ/m fix
first. T95 is parked until master is right.

**LZ event-gating**: T95 itself does not depend on the LZ
248 keV event. But the merge of T95 (or any T9x work) to
master should follow the T90 merge rule: no merge until
LZ community confirmation OR master 7D fit shows
Δlog Z ≥ +2.

---

## What I'm doing right now (2026-09-07)

**Phase 0 in progress.** Pulling SWIFT public SIDM halo data,
computing master Yukawa prediction, comparing. Zero new
dependencies. No approval gates triggered. Will report back
with agreement / disagreement in ~1 week (or when SWIFT data
is fully analyzed).

If SWIFT data is hard to access publicly, Phase 0 may take
longer (data access requests are typical for DiRAC). Will
report honestly if blocked.

---

## Branch policy

**This T95 plan does NOT create a branch yet.** Branching
will happen at Phase 1 (GIZMO install) when the first
real code work begins. Until then, all work is on master
as a planning doc + Phase 0 analysis script.

**Branch name candidate**: `wip/tier2-sidm-core-profile`
(to match the T90 `wip/tier3-magnetic-moment-LZ` naming).

---

## References

- T89 benchmark: `v0.3-prelim/docs/T89_SIDMKIT_SIDMVDSIGMAS_BENCHMARK.md`
- T90 forward prediction: `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md`
- bok doc source: `bok halo.docx` (uploaded 2026-09-07)
- AGENTS.md rules 17, 24: dependency approval gates
- T90 merge rule: see `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_PLAN.md` §merge rule
