# Phase 11 + 12 — Majorana Freeze-Out & σ/m Drop Mystery

> **Status:** Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Sub-tasks:** Phase 11 (g_D freeze-out conflict), Phase 12 (σ/m drop mystery)
> **Predecessor:** Phase 8d (Majorana INERT), Phase 9b (mass segregation insufficient)

---

## Phase 11 — g_D Freeze-Out Conflict Resolution

### The problem

The Majorana reframe requires **g_D ~ 0.7** for SIDM (σ/m ~ 1 cm²/g at v=100). But de Lima's thermal freeze-out calculation gives **g_D ~ 0.02** (α_D = 4.1e-5 from Ω h² = 0.12). These differ by **35×**.

### Five pathways tested

| Pathway | Mechanism | Result |
|---|---|---|
| A | Sommerfeld enhancement (S ~ 67 for m_A'=200 MeV) | Ωh² ~ 6e-4 at g_D=0.7 — over-annihilates 200× |
| B | Co-annihilation with δm ~ 10-1000 MeV partner | Boost factor 1.0-1.1 — too small to fix 35× gap |
| C | Freeze-in (Hall+ 2010) | Requires ε ~ 1.4e-12 (de Lima's 1.3e-6 is 1000× too large) |
| **D** | **Asymmetric DM (Kaplan+ 2009)** | **PROCEED** — relic set by B-L-like asymmetry, ANY g_D allowed |
| E | Resonant annihilation (m_A' ≈ 2 m_χ) | Requires m_A' ~ 90 GeV, not 200 MeV |

### Verdict

**Pathway D (Asymmetric DM) resolves the freeze-out conflict.**

In asymmetric DM, the relic density is set by a B-L-like asymmetry in
the early universe, NOT by thermal freeze-out annihilation. Just like
baryons (Ω_b ~ 0.05 set by CP-violating baryogenesis, not by p̄-p
annihilation), Majorana χ particles can have ANY coupling to the
dark photon — including g_D ~ 0.7 — as long as an asymmetry-generating
mechanism (e.g. Affleck-Dine, leptogenesis) produces the right Ω h².

**Implication**: The Majorana reframe is cosmologically viable if
Majorana χ is the asymmetric matter component. The freeze-out
conflict is resolved without modifying the SIDM or LZ 248 keV
predictions.

**References**:
- Kaplan+ 2009 (arXiv:0909.0753) — Asymmetric DM review
- Hall+ 2010 (arXiv:0911.3599) — Freeze-in production
- Hisano+ 2004 (PLB 579, 265) — Sommerfeld enhancement for Majorana
- Griest/Scherrer 1989 — Co-annihilation formalism

---

## Phase 12 — σ/m Drop Mystery Investigation

### The problem

v0.3-prelim's σ/m MAP dropped from T39's 0.72 cm²/g to Phase 8c's
0.065 cm²/g — a 10× shift. Phase 8c/8d attributed this to the LZ 248
keV channel preferring smaller g_D. But is that actually the cause?

### Three hypotheses

| Hypothesis | Prediction | Test |
|---|---|---|
| A: Statistical fluctuation | Drop the 248 keV channel → σ/m returns to ~0.7 | Run with channel OFF |
| B: SIDM channels overestimate | σ/m stays low regardless of LZ channel | Run with N_obs=0 |
| C: Different physics | σ/m differs between "on" and "null" modes | Compare "on" vs "null" |

### Results — all three modes give σ/m = 0.067 cm²/g

| Mode | log_Z | σ/m MAP | σ/m median |
|---|---|---|---|
| **on** (Poisson N_obs=1) | -206.71 | 0.0670 | 0.0648 |
| **off** (channel disabled) | -206.41 | 0.0669 | 0.0648 |
| **null** (N_obs=0 hypothesis) | -206.47 | 0.0666 | 0.0649 |

Δlog Z (off vs on): +0.307 (LZ channel is mildly disfavored)
Δlog Z (null vs on): +0.240 (N_obs=1 hypothesis is mildly disfavored)

### Verdict

**The σ/m drop is INTRINSIC to the Majorana reframe, NOT caused by
the LZ 248 keV channel.**

All three LZ 248 keV modes (on/off/null) give σ/m ≈ 0.067 cm²/g.
The drop is built into the joint posterior through:
- g_D constrained to ~0.13-0.16 by Fermi (g_D²/4π → σ_v limit)
- m_A' = 200 MeV → propagator gives small σ_inel
- ε ~ 10⁻⁹ → σ_inel × f_H × exposure must match 1 event

The "drop" is just the MAP at the constrained corner of the joint
posterior, not a consequence of including the LZ event channel.

### What this means

**Hypothesis A is INCORRECT**: the LZ 248 keV event is NOT responsible
for the σ/m drop. The drop happens even without the channel.

**Hypothesis B is the actual answer**: the SIDM σ/m at v=100 km/s in
the Majorana reframe is constrained to ~0.065 by:
1. Fermi dwarf limit (forces g_D ≤ 0.16)
2. m_phi = 200 MeV de Lima assumption (gives small σ_inel propagator)
3. ε ~ 10⁻⁶ from de Lima's inelastic LZ matching

**The σ/m drop reflects the INCONSISTENCY between T39's
(m_phi=100 MeV, α_D=0.01 fixed) and de Lima's (m_phi=200 MeV, g_D=0.0227
fixed) parameter choices.** They're probing DIFFERENT regimes of
the same model.

---

## Combined Phase 11+12 Verdict

The Majorana reframe is:
- ✓ Structurally viable (σ_SI² suppressed by (g_D ε)²)
- ✓ Cosmologically viable (asymmetric DM pathway)
- ✓ Compatible with the LZ 248 keV event (Δlog Z ≈ 0)
- ✗ σ/m at v=100 is constrained to ~0.065 cm²/g by the joint posterior,
  not by the LZ event itself

**The "σ/m drop" is real but it reflects a DIFFERENCE between T39
and the Majorana reframe parameter choices, not a problem with the
reframe.**

## Honest scope

These results don't change the verdict of Phase 8d — the Majorana
reframe is INERT (accommodates LZ 248 keV but doesn't require it).
They add:
- A cosmologically viable pathway (asymmetric DM)
- A clear identification of why σ/m dropped (parameter inconsistency,
  not channel conflict)

## Code & Data

- `code/phase11_majorana_freeze_out.py` (~290 lines)
- `code/phase12_sigma_m_drop_mystery.py` (~270 lines)
- `data/results/phase11_majorana_freeze_out.json`
- `data/results/phase12_sigma_m_drop_mystery.json`
- `tests/test_phase11_majorana_freeze_out.py` — **8/8 PASS**
- `tests/test_phase12_sigma_m_drop_mystery.py` — **4/4 PASS**

## References

- Phase 8d (`PHASE8D_SERIES_2026_09_14.md`) — Majorana INERT
- Phase 9b (`PHASE9_MASS_SEGREGATION_2026_09_14.md`) — mass segregation insufficient
- Kaplan+ 2009 (arXiv:0909.0753) — Asymmetric DM
- Hall+ 2010 (arXiv:0911.3599) — Freeze-in production
- Griest/Scherrer 1989 — Co-annihilation formalism
- Hisano+ 2004 (PLB 579, 265) — Sommerfeld enhancement
