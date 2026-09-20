# Phase 23-25 — Remaining Tension Diagnostics

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Direction:** Address remaining Phase 22 failures (Cloud-9, SPARC, Euclid subhalo)
> **Predecessor:** Phase 22 (6 → 2 failures via reviewer fixes)

---

## TL;DR — Honest results

| Channel | Phase 22 | Phase 23-25 | Status |
|---|---|---|---|
| **Cloud-9** | -13.21 (FAIL) | **-0.53 (PASS)** | ✓ RESOLVED (multi-portal wrapper bug fix) |
| **SPARC** | 0 (disabled) | **-312,939 (FAIL)** | ✗ Real structural conflict with SPARC data |
| **Euclid subhalo** | -14.09 (FAIL) | **-11.82 (FAIL)** | ✗ Structural conflict, no coupling fix helps |
| **KSFR/PCAC** | 0 (N/A) | unchanged | ✓ dark photon N/A |
| **DAMPE, Fermi, XRISM-φ→γγ** | 0 (asymmetric DM) | unchanged | ✓ nullified |

**Net result: 6/20 → 2/20 channel failures** — but the 2 remaining are **REAL structural conflicts**, not artifacts.

---

## Phase 23 — Cloud-9 (RESOLVED)

### The bug

Phase 22 evaluated Cloud-9 with `loglike_relhic_t90v29(theta_9d)`, which extracts `(m_phi, m_chi, g_chi)` from **theta[0:3]** = **Portal A only**. This gave loglike = -13.21.

But the multi-portal model has TWO portals contributing to the total σ/m. At v = 28 km/s (Cloud-9):
- Portal A (heavy): σ/m(28) ~ small
- Portal B (light, 20 MeV): σ/m(28) ~ large
- **Total**: σ/m(28) = 42.41 cm²/g ← IN Cloud-9 range [30, 500]

### The fix

Created `t90_v45_cloud9_multi_portal.py` wrapper:
1. Compute total σ/m(28) = Portal A + Portal B (additive Yukawa)
2. Map to effective single-portal (m_phi, m_chi, g_chi) that reproduces the total
3. Evaluate T90.29 v3 likelihood at the effective params

### Result

| Channel | Phase 22 (Portal A only) | Phase 23 (multi-portal) |
|---|---|---|
| Cloud-9 loglike | -13.21 | **-0.53** |

**Cloud-9 PASSES** when correctly evaluated. The "tension" was a wrapper bug, not a model issue.

### Halo marginalization (also Phase 23)

Tried marginalizing over (M200, c200) nuisance parameters:
- Log-normal prior on M200 (sigma 0.3 dex around published 4.7e9 M_sun)
- Half-Gaussian prior on c200 (sigma 0.5 around published 4.0)
- 25 × 15 grid marginalization

**Delta loglike from marginalization: +0.00** (no change). The halo parameters are well-constrained enough that marginalization doesn't relax the bound.

---

## Phase 24 — SPARC (REAL CONFLICT)

### What SPARC says

SPARC (175 galaxy rotation curves) hierarchical loglike:
- **Prefers σ/m(100) ≈ 0.069 cm²/g** (the v0.3-prelim single-portal value)
- Heavily disfavors σ/m(100) > 1 cm²/g (cores become too large, don't match rotation curves)

### What T90.45 multi-portal says

| Velocity | σ/m | Channel |
|---|---|---|
| 28 km/s | **42.4** | Cloud-9 |
| 100 km/s | **3.91** | SPARC (galactic) |
| 150 km/s | 1.33 | Euclid subhalo |
| 3000 km/s | 0.024 | Bullet cluster |

T90.45 median σ/m(100) = 3.91 cm²/g is **57× higher** than SPARC's preference.

### The conflict

| Quantity | T90.45 median | SPARC max |
|---|---|---|
| σ/m(100) | 3.91 | 0.069 |
| SPARC hierarchical loglike | -312,939 | -203,676 |
| Δlog Z (T90.45 vs SPARC max) | -109,263 | — |

**Verdict: FAILS_SPARC.** The multi-portal model is strongly disfavored by SPARC rotation curves.

### Why this happens

The Cloud-9 requirement (σ/m(28) ≥ 30) forces Portal B to be light (~20 MeV) with significant coupling. But Portal B's Yukawa form gives high σ/m at all velocities below the kinematic threshold, including at v=100 km/s where SPARC constrains σ/m < 1.

**The Cloud-9 and SPARC requirements are in structural conflict** with the current multi-portal architecture.

---

## Phase 25 — Euclid subhalo (REAL CONFLICT)

### What Euclid wants

Euclid Q1 subhalo forecast (Channel 24):
- σ/m(v=150) < 0.10 cm²/g → in-band (subhalos survive)
- σ/m(v=150) > 0.10 → too much tidal evaporation → log Z penalty

### What T90.45 says

T90.45 median σ/m(150) = 1.33 cm²/g → **10× over Euclid's limit** → loglike = -11.82.

### Coupling scan

Scanned 13 × 19 = **247 (g_chi_A, g_chi_B) combinations** keeping mediator masses fixed (m_phi_A=366, m_phi_B=20.5 MeV):

| Constraint | Satisfied by |
|---|---|
| Cloud-9 (σ/m(28) ≥ 30) | requires high g_chi_B (~0.3+) |
| Euclid subhalo (σ/m(150) < 0.10) | requires low g_chi_A AND g_chi_B |

**0 / 247 combinations satisfy both.**

### Why this is structural

Portal B's Yukawa form gives σ/m(v) ∝ g_chi_B^4 × f(v × m_phi_B). At v=28 km/s with m_phi_B=20.5 MeV, the kinematic ratio is β = m_chi v / (sqrt(2) m_phi) ~ 990 (classical regime). σ/m(28) is large.

At v=150 km/s, β is even larger (~5300). The Yukawa form σ/m ~ g^4 / m_phi^4 × (log β / β)^2 decreases, but not fast enough. To get σ/m(150) < 0.10 with σ/m(28) ≥ 30, you need an extremely steep velocity dependence, which a simple Yukawa doesn't provide.

### Verdict

**NO_CONFIGURATION_FOUND.** The m_phi_B = 20.5 MeV Portal B cannot satisfy both Cloud-9 and Euclid subhalo simultaneously.

---

## Updated status — Phase 25

### Total channel failures: 6 → 4 (improvement on Cloud-9, but reveals 2 real conflicts)

| Phase | Channels FAILING | Cloud-9 | SPARC | Euclid subhalo |
|---|---|---|---|---|
| Phase 20 (v0.3-prelim) | 6 | -10 (FAIL) | -202,229 (FAIL) | -10 (FAIL) |
| Phase 21 (T90.45 raw) | 6 | -10 (FAIL) | -290,000 (FAIL) | -10 (FAIL) |
| Phase 22 (reviewer fixes) | 2 | -13.21 (FAIL, wrapper bug) | 0 (disabled) | -14.09 (FAIL) |
| **Phase 23-25** | **2** | **-0.53 (PASS)** | **-312,939 (FAIL, real)** | **-11.82 (FAIL, real)** |

### The two remaining failures are REAL, not artifacts

| Channel | Failure severity | What's needed |
|---|---|---|
| **SPARC** | Δlog Z = -109,263 | Different multi-portal architecture (Portal B mass > 100 MeV); or different velocity dependence |
| **Euclid subhalo** | loglike = -11.82 | Steeper velocity dependence than Yukawa; or no Portal B at galactic velocities |

Both require **architectural changes** to the multi-portal model:
1. **Make Portal B mass-dependent on velocity** (e.g., velocity-dependent mass, hard to engineer)
2. **Use a different σ/m(v) form** (not pure Yukawa)
3. **Add a third portal** that suppresses σ/m at v=100-200 km/s without affecting v=28

---

## What the reviewer got right vs what was different

The reviewer recommended:
1. ✓ Median mode as baseline (cosmetic)
2. ✓ KSFR N/A for dark photon (architectural fix)
3. ✓ Asymmetric DM switch (architectural fix)
4. ✓ SPARC saturated proxy disabled (turned out to be unnecessary; the real SPARC hierarchical is just disfavored)
5. ✓ STOP RULE on new channels
6. ✓ Practical sequence followed

The reviewer did NOT anticipate:
- The Cloud-9 wrapper bug (which made Phase 22 look worse than reality)
- The structural Cloud-9 ↔ SPARC conflict
- The structural Cloud-9 ↔ Euclid subhalo conflict

These structural conflicts are **NEW findings** that emerged from Phases 23-25. They suggest the multi-portal architecture (as currently parameterized) cannot simultaneously satisfy Cloud-9 + SPARC + Euclid subhalo.

---

## What this means for the model

The T90.45 multi-portal model:
- ✓ Satisfies 18/20 channels in the T90.42 framework
- ✗ Fails 2 channels (SPARC, Euclid subhalo) due to **structural velocity-dependence conflict**
- These conflicts would require **architectural changes** to the multi-portal model:
  - Different Portal B mass (>100 MeV)
  - Different σ/m(v) form (non-Yukawa)
  - Three-portal architecture

The model is NOT a complete solution to all space conditions. It's a partial solution that:
1. ✓ Solves Cloud-9 (σ/m(28) = 42 in [30, 500])
2. ✗ Conflicts with SPARC (rotation curves prefer low σ/m(100))
3. ✗ Conflicts with Euclid subhalo forecast (too much evaporation)

To resolve these would require deeper model changes than multi-portal architecture provides.

---

## Code & Data

- `code/phase23_cloud9_nuisance_marginalization.py` (~260 lines)
- `code/phase24_multi_portal_sparc.py` (~190 lines)
- `code/phase25_euclid_subhalo_multi_portal.py` (~160 lines)
- `code/t90_v45_cloud9_multi_portal.py` (new wrapper, ~115 lines)
- `data/results/phase23_*.json`, `phase24_*.json`, `phase25_*.json`
- `tests/test_phase23_cloud9_nuisance.py` — 6/6 PASS
- `tests/test_phase24_25_sparc_euclid.py` — 6/6 PASS

**67/67 tests pass** across the post-Phase 10 sweep (15 phases, 21 sub-tasks).

---

## Next steps (deferred per STOP RULE)

Per the reviewer's STOP RULE recommendation, no new channels. The 2 remaining failures are structural and would require:

1. **Phase 26 (deferred)**: Three-portal architecture with intermediate-mass portal to suppress σ/m at v=100-200 km/s
2. **Phase 27 (deferred)**: Non-Yukawa σ/m(v) form (e.g., Born + quantum corrections)
3. **Phase 28 (deferred)**: Velocity-dependent mediator mass

These are NOT pursued per the STOP RULE. The model is honest about its limits: 18/20 channels pass, 2 are structural conflicts.
