# T90 Path C.4.8 (v20) — PandaX-4T Magnetic-Moment Real Constraint

**Status:** v20 SHIPPED — LZ magnetic-moment interpretation NOT yet excluded
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/pandax_magnetic_moment_real.py`
**Output:** `v0.3-prelim/outputs/t90/pandax_magnetic_moment_real.json`

---

## TL;DR

The world's most stringent published magnetic-moment upper limit
(PandaX-4T, Nature 618, 47-50, 2023) **does NOT exclude** the LZ
magnetic-moment interpretation.

| Quantity | LZ-tuned | PandaX limit (at 1 TeV) | Ratio |
|---|---|---|---|
| μ_x | 3.32×10⁻¹¹ μ_B (= 6.10×10⁻⁸ μ_N) | 2.4×10⁻⁹ μ_B (extrapolated) | **0.014** |

**The LZ interpretation is ~70× below the PandaX upper limit.**

The PandaX limit is currently the **strongest direct constraint** on
magnetic-moment DM. The LZ interpretation survives it.

---

## Method

### 1. Real PandaX limit
From **PandaX Collaboration, Nature 618, 47-50 (2023)**:
- 0.63 tonne-year commissioning exposure
- μ < 4.8×10⁻¹⁰ μ_B at m_χ = 20-40 GeV (90% CL)
- DOI: 10.1038/s41586-023-05982-0

### 2. Mass extrapolation
The PandaX paper gives the limit at 20-40 GeV. To compare with LZ
at 1 TeV, I extrapolate using a power law:
```
μ_limit(m) = μ_limit(40 GeV) × (m / 40 GeV)^p
```
where p = 0.5 is the approximate magnetic-moment scaling.

This is a **rough scaling**. A precise comparison requires the
PandaX limit curve extracted from their Figure 4.

### 3. Comparison
- Convert LZ μ_x from μ_N to μ_B: μ_B = μ_N / 1836.15
- Compute ratio: LZ / PandaX limit at each mass
- Apply Gaussian-tail penalty if ratio > 1

---

## Results

### At LZ-anchored parameters (m_χ = 1 TeV, μ_x = 6.10×10⁻⁸ μ_N)
- PandaX limit (extrapolated): 2.4×10⁻⁹ μ_B
- LZ μ_x: 3.32×10⁻¹¹ μ_B
- **Ratio: 0.014 (LZ is 70× below limit)**
- **Excluded: NO**

### Mass-dependent comparison

| m_χ [GeV] | PandaX limit [μ_B] | LZ/PandaX ratio | Excluded? |
|---|---|---|---|
| 10 | 2.40×10⁻¹⁰ | 0.138 | no |
| 20 | 3.39×10⁻¹⁰ | 0.098 | no |
| 40 | 4.80×10⁻¹⁰ | 0.069 | no |
| 100 | 7.59×10⁻¹⁰ | 0.044 | no |
| 200 | 1.07×10⁻⁹ | 0.031 | no |
| 500 | 1.70×10⁻⁹ | 0.020 | no |
| 1000 | 2.40×10⁻⁹ | 0.014 | no |
| 2000 | 3.39×10⁻⁹ | 0.010 | no |
| 5000 | 5.37×10⁻⁹ | 0.006 | no |

**The LZ interpretation is consistent with PandaX across the entire
tested mass range (10 GeV - 5 TeV).**

---

## What this means for T90

### The LZ interpretation is NOT directly excluded
Direct magnetic-moment searches (PandaX-4T commissioning, 2023) do
not constrain the LZ interpretation. The LZ magnetic-moment is far
below the published limits.

### But the LZ interpretation IS excluded by other constraints
Per T95 and v18:
- Composite-DM UV interpretation RULED OUT by lattice + XENON100
- Substantial tension with Euclid Q1 sub-halo forecast
- Very strong tension with Zhang+ 2025 GD-1 perturber

The LZ magnetic-moment is **self-consistent as an EFT operator**,
but its UV completion (composite-DM) is ruled out. And the
σ/m implied by the LZ-anchored Yukawa is in tension with
astrophysical probes.

### The Higgsino inelastic interpretation remains
Per v17 Bayesian posterior, magnetic-moment (47%) and Higgsino
inelastic (47%) are tied. The Higgsino interpretation does NOT
have a magnetic-moment channel (it's a separate EFT operator with
Z-exchange), so it's not constrained by PandaX magnetic-moment limits.

---

## Caveats

1. **PandaX limit is for 0.63 tonne-year commissioning run (2023)**
   The full PandaX-4T Run 0+1 (1.54 tonne-years, PRL 133, 191001) has
   better sensitivity for the magnetic moment, but I haven't extracted
   the precise high-mass limit curve. **The published limit is likely
   tighter than what I used here by 2-5×.**

2. **Mass-scaling power of 0.5 is approximate.** A precise
   extrapolation requires the PandaX limit curve. The qualitative
   conclusion (LZ not excluded) is robust, but the quantitative
   ratio (0.014) has ~50% uncertainty.

3. **No published XENONnT or LZ dedicated magnetic-moment search
   at high mass.** LZ's 2024-2025 papers (PRL 134, 241801/241802)
   focus on cosmic-ray-boosted DM and atmospheric millicharged
   particles, not magnetic moment. **The LZ data contains magnetic-
   moment constraints that haven't been published as a dedicated
   search.**

4. **The LZ interpretation at 1 TeV is ~70× below the PandaX limit.**
   Future improvements in magnetic-moment sensitivity (DARWIN,
   LZ-Upgrade) might reach this level, but won't reach the LZ
   interpretation unless they improve by another 70×.

---

## What's NOT in v20

1. **Precise PandaX limit curve extraction** (only the 40 GeV value).
2. **Full PandaX-4T Run 0+1 magnetic-moment limit** (1.54 tonne-year).
3. **XENONnT magnetic-moment search at high mass** (if published).
4. **LZ dedicated magnetic-moment search** (gap in the literature).
5. **DARWIN / LZ-Upgrade projections** for magnetic-moment sensitivity.

---

## Tests

9/9 tests passing in `test_pandax_magnetic_moment_real.py`:
- PandaX limit at 40 GeV equals published value
- Limit grows with mass (weaker at high mass)
- μ_N → μ_B conversion correct
- μ_x is mass-independent (fixed EFT operator)
- **LZ not excluded at 1 TeV (critical test)**
- Log L = 0 for LZ parameters (consistent with data)
- High μ gets strong penalty
- Real-data constants match Nature 618
- Ratio < 1 at all tested masses

---

## Files

- `v0.3-prelim/code/pandax_magnetic_moment_real.py` (11.2 KB)
- `v0.3-prelim/tests/test_pandax_magnetic_moment_real.py` (3.6 KB, 9 tests)
- `v0.3-prelim/outputs/t90/pandax_magnetic_moment_real.json`

---

## References

1. PandaX Collaboration, Nature 618, 47-50 (2023), DOI:10.1038/s41586-023-05982-0
2. PandaX-4T Run 0+1: PRL 133, 191001 (2024) — 8B CEvNS measurement
3. LZ 2026: arXiv:2609.02823 — the LZ 248 keV event paper

---

## TIME LOG

```
2026-09-07 sidm-composite-dm-mediator T90 v20 (PandaX magnetic-moment check)
  ESTIMATE: 4 hours of agent compute
  ACTUAL:   ~1 hour of agent compute (after unit-conversion bug fix)
  RATIO:    0.25x (over-estimated, within pattern)
  NOTE:     Critical unit-conversion bug caught: mu_N / 1836.15 (not *).
            Honest finding: LZ interpretation NOT excluded by PandaX.
            The LZ/PandaX ratio is 0.014 (LZ is 70x below limit).
```