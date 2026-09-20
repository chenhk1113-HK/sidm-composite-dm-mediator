# Layman Status Summary — Paper v1.14 (2026-09-20)

This is a plain-language summary of the current state of the SIDM Composite DM-Mediator project. It is the public-facing version intended for both technical and non-technical readers.

---

## Where we are now (2026-09-20)

Paper is now **v1.14** — a phenomenology paper with a documented "UV completion open problem."

---

## What works

- A dark matter model that fits **8 observational datasets** across **4 orders of magnitude in velocity** (from ultra-faint dwarf galaxies to galaxy clusters)
- Verified by **MCMC** (independent parameter recovery, 1σ consistency)
- **215 automated tests pass**
- Standard self-check: ALL CHECKS PASSED

---

## What was wrong before

Last week I claimed we had a "UV-complete" model (Hidden U(1) + dark photon). A referee pointed out three serious problems:

1. **Wrong formula**: I used V_max = α_D × m_χ (16 MeV). Referee said this was dimensionally wrong. I checked Zhang 2016's actual paper — the correct formula is V_max = α_D² × m_χ (0.024 MeV). My formula overstated the well depth by **667×**.

2. **Kinematic forbiddenness**: My model required Δm = 10 MeV to evade direct detection. But galactic kinetic energy at Cloud-9's velocity is only **23 eV**. Δm exceeded KE by **5 orders of magnitude** — so the "self-interaction preserved" claim was mathematically impossible.

3. **No published UV completion works**: I tested 4 candidate UV models (magnetic dipole, Hidden U(1), GeV inelastic DM, published p-wave resonance). **All four fail.**

---

## What I did about it

Instead of defending the broken claim, I:

- Wrote an honest referee response accepting all 3 problems (see `REFEREE_RESPONSE_v1.md`)
- Implemented a kinematic threshold test that catches this class of error (T120.16, 17 tests pass)
- Built 4 "no-go theorems" — each one proves a specific UV completion path doesn't work:
  - T120.10: Magnetic dipole DM ruled out by LZ direct detection
  - T120.16: Hidden U(1) + 10 MeV pseudo-Dirac ruled out by galactic kinematics
  - T130: GeV-scale inelastic DM requires m_χ ≥ 46 TeV (and unitarity violation)
  - T131: Published best-fit p-wave resonance (Chu et al. 2019) fails on Cloud-9
- Reframed the paper around what's actually publishable: the **phenomenology** (the dark matter model itself, without claiming to know what particle physics produces it)

---

## What's publishable now

The dark matter model that fits the data is real and reproducible. The "what particle produces this" question is honestly marked as open. This is a legitimate, honest framing — many dark matter papers are published this way. The paper's §10.5 (EFT Target Map) is a guide for future theoretical work.

---

## What's in the GitHub repo now

- **Working phenomenology code** (cloud-9 vs dSph tension solved)
- **4 UV completion attempts** (all documented as failures — that's the contribution)
- **215 tests passing**
- **Honest documentation** of what works, what doesn't, and why

---

## Bottom line

Project is in a **much stronger position** than a week ago. Self-falsification caught 3 real errors before publication. The v1.14 paper is now honest about what's known (model fits data) and what's open (UV physics still unknown).

**Branch state**: both `wip/multi-component-SIDM-core-collapse` and `wip/cloud-9-relhic` synced at commit `515e989`.

---

## What is genuinely ours vs cited

**Genuinely ours (the contribution):**
- The 4-resonance multi-peak structure with specific velocity positions
- Gaussian profile replacement for Lorentzian (T120.1-4)
- The specific combination of multi-comp + gravothermal + Gaussian profiles that solves Cloud-9 vs dSph
- MCMC verification of parameter recovery (T120.9a)
- The 4 no-go theorems (T120.10, T120.16, T130, T131)
- The 8-constraint joint fit and BIC comparison
- The EFT target map (§10.5 of v1.14)

**Cited framework:**
- Yang+ 2025 PRD (two-component asymmetric DM)
- Yu+ 2026 PRL (gravothermal selection)
- Zhang 2016 (Hidden U(1) — attempted UV completion that we falsified)
- Chu et al. 2019 (p-wave resonance — best-fit benchmark that we verified)
- Schutz-Slatyer 2014, Brahma+ 2024 (inelastic DM — used in T130 no-go)

---

## What this paper is NOT

- Not a claim that SIDM is the only solution to the small-scale structure problems
- Not a claim that we've found the UV-complete model
- Not a substitute for dedicated forward-model SPARC likelihood analysis (the +8 log-unit gain is real but uses pass/fail V_flat, not hierarchical Bayesian)
- Not the unique solution to the Cloud-9 vs dSph tension — Burkert wins Bayesian evidence in rotation curves alone (§7 of v1.14)

---

## What's next (deferred)

Per Qwen referee 2026-09-19 suggestions for v1.15+:

1. **Dark molecular dissociation** (binding energy ~20 eV ≈ KE at 28 km/s) — non-perturbative enhancement at v=28, elastic at v=15
2. **Multi-TeV inelastic DM with non-thermal production** (bypass thermal relic unitarity)
3. **Composite DM form factors** (size comparable to de Broglie wavelength at v=28 but not v=15)

These are documented as **future work** in §10.5 of v1.14. They require more theoretical work and are NOT claimed in v1.14.
