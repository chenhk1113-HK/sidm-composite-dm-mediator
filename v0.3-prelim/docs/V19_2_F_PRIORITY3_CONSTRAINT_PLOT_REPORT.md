# Priority 3 Constraint Plot Report

**v19.2-F — quantitative exclusion curves in the (alpha_D, m_A') plane.**


Plot file: `v0.3-prelim/docs/V19_2_F_PRIORITY3_CONSTRAINT_PLOT.pdf` (and `.png`)


## Setup

- DM mass: m_chi = 1.0 GeV
- Coupling convention: alpha_D = g^2 / (4 pi) [LOCKED, per constants.py]
- kappa_c (s-wave bound-state threshold): 1.6798
- Born formula (Tulin-Yu-Zurek 2013, Eq. 3):
    sigma_T = (g^4 m_chi^2) / (8 pi m_A^4) * L(s)^2
    s = (m_chi v / (sqrt(2) m_A))^2,  L(s) = ln(1+1/s) - 1/(1+s)

## Constraints plotted

| Constraint | Source | Visible-decay region | Invisible-decay note |
|------------|--------|----------------------|----------------------|
| BBN | Planck 2018 / Olive 2019 | m_A' < 1 MeV excluded | Survives |
| CMB | Slatyer 2016 / Poulin 2018 | 1 MeV < m_A' < 100 MeV excluded | Survives |
| SN1987A | Caputo 2021 | 1 MeV < m_A' < 100 MeV excluded | Survives |
| Lyman-alpha | Vogelsberger 2012 / Zavala 2013 | sigma/m(30 km/s) > 100 cm^2/g | **Always applies** |
| XENONnT / LZ | Aprile 2022 / Aalbers 2022 | 1 MeV < m_A' < 100 MeV excluded | Survives |

**Important**: BBN, CMB, SN1987A, XENONnT constraints all apply only if the dark
photon is VISIBLE (kinetic mixing epsilon > 1e-10, decays to SM). For an INVISIBLE
dark photon (no kinetic mixing, decays only to dark sector), all those constraints
vanish. **Lyman-alpha is the ONLY constraint that applies unconditionally** because
it depends on sigma/m (DM self-scattering), not on the decay channel.

## Candidate points and verdicts

| Candidate | alpha_D | m_A' | kappa | Lyman-alpha sigma/m | Verdict (visible) | Verdict (invisible) |
|-----------|---------|------|-------|---------------------|---------------------|----------------------|
| Framework doc | 6.80e-07 | 200 eV | 3.40e+00 | 4.04e-10 cm^2/g | **EXCLUDED** | **ALLOWED** |
| Phase-3 best fit (EXTENDED) | 5.55e-06 | 1.26e+05 eV | 4.40e-02 | 74.8 cm^2/g | **EXCLUDED** | **MARGINAL** |
| Lattice ridge #1 (m_A'=3.5 eV, kappa~1e5) | 2.97e-10 | 3.5 eV | 8.49e-02 | 1.9e-21 cm^2/g | **EXCLUDED** | **ALLOWED** |
| Lattice ridge #2 (m_A'=12.3 eV, kappa~1e6) | 4.12e-09 | 12.3 eV | 3.35e-01 | 2.41e-19 cm^2/g | **EXCLUDED** | **ALLOWED** |
| Lattice ridge #3 (m_A'=43.3 eV, kappa~1e7) | 5.99e-08 | 43.3 eV | 1.38e+00 | 6.89e-15 cm^2/g | **EXCLUDED** | **ALLOWED** |

### Per-candidate detail

**Framework doc**  (alpha_D=6.80e-07, m_A'=200 eV, kappa=3.40e+00, kappa/kappa_c=2.02e+00)

  - Lyman-alpha sigma/m(v=30 km/s, Born) = 4.04e-10 cm^2/g
    -> Lyman-alpha: ALLOWED by Born (sigma/m < 50 cm^2/g)
  - BBN (visible): EXCLUDED
  - BBN (invisible): ALLOWED
  - CMB (visible): ALLOWED
  - CMB (invisible): ALLOWED
  - SN1987A (visible): ALLOWED
  - SN1987A (invisible): ALLOWED
  - XENONnT/LZ (visible): ALLOWED
  - XENONnT/LZ (invisible): ALLOWED

  **CAVEAT**: kappa = 3.40e+00 > kappa_c = 1.6798, so the Born formula is NOT reliable here. The deep-Sommerfeld enhancement can boost sigma/m by factors of 10-100, so the Lyman-alpha verdict may be MORE EXCLUDED than shown.

**Phase-3 best fit (EXTENDED)**  (alpha_D=5.55e-06, m_A'=1.26e+05 eV, kappa=4.40e-02, kappa/kappa_c=2.62e-02)

  - Lyman-alpha sigma/m(v=30 km/s, Born) = 74.8 cm^2/g
    -> Lyman-alpha: MARGINAL (Born value 50-100 cm^2/g)
  - BBN (visible): EXCLUDED
  - BBN (invisible): ALLOWED
  - CMB (visible): ALLOWED
  - CMB (invisible): ALLOWED
  - SN1987A (visible): ALLOWED
  - SN1987A (invisible): ALLOWED
  - XENONnT/LZ (visible): ALLOWED
  - XENONnT/LZ (invisible): ALLOWED

**Lattice ridge #1 (m_A'=3.5 eV, kappa~1e5)**  (alpha_D=2.97e-10, m_A'=3.5 eV, kappa=8.49e-02, kappa/kappa_c=5.05e-02)

  - Lyman-alpha sigma/m(v=30 km/s, Born) = 1.9e-21 cm^2/g
    -> Lyman-alpha: ALLOWED by Born (sigma/m < 50 cm^2/g)
  - BBN (visible): EXCLUDED
  - BBN (invisible): ALLOWED
  - CMB (visible): ALLOWED
  - CMB (invisible): ALLOWED
  - SN1987A (visible): ALLOWED
  - SN1987A (invisible): ALLOWED
  - XENONnT/LZ (visible): ALLOWED
  - XENONnT/LZ (invisible): ALLOWED

**Lattice ridge #2 (m_A'=12.3 eV, kappa~1e6)**  (alpha_D=4.12e-09, m_A'=12.3 eV, kappa=3.35e-01, kappa/kappa_c=1.99e-01)

  - Lyman-alpha sigma/m(v=30 km/s, Born) = 2.41e-19 cm^2/g
    -> Lyman-alpha: ALLOWED by Born (sigma/m < 50 cm^2/g)
  - BBN (visible): EXCLUDED
  - BBN (invisible): ALLOWED
  - CMB (visible): ALLOWED
  - CMB (invisible): ALLOWED
  - SN1987A (visible): ALLOWED
  - SN1987A (invisible): ALLOWED
  - XENONnT/LZ (visible): ALLOWED
  - XENONnT/LZ (invisible): ALLOWED

**Lattice ridge #3 (m_A'=43.3 eV, kappa~1e7)**  (alpha_D=5.99e-08, m_A'=43.3 eV, kappa=1.38e+00, kappa/kappa_c=8.24e-01)

  - Lyman-alpha sigma/m(v=30 km/s, Born) = 6.89e-15 cm^2/g
    -> Lyman-alpha: ALLOWED by Born (sigma/m < 50 cm^2/g)
  - BBN (visible): EXCLUDED
  - BBN (invisible): ALLOWED
  - CMB (visible): ALLOWED
  - CMB (invisible): ALLOWED
  - SN1987A (visible): ALLOWED
  - SN1987A (invisible): ALLOWED
  - XENONnT/LZ (visible): ALLOWED
  - XENONnT/LZ (invisible): ALLOWED

## Key finding

The plot illustrates the following structure in the (alpha_D, m_A') plane:

1. **All 'visible-decay' constraints (BBN/CMB/SN1987A/XENONnT) carve out
   a vertical band at m_A' in [1 eV, 100 MeV]** -- but they vanish for an
   invisible dark photon. These are constraints on the dark photon's
   COUPLING TO SM, not on the dark sector self-interaction strength alpha_D.

2. **Lyman-alpha is the only constraint that is unavoidable**: it depends
   directly on alpha_D (via sigma/m), regardless of whether the dark
   photon is visible. The exclusion boundary sigma/m(30 km/s) = 100 cm^2/g
   is the upper envelope of the allowed region.

3. **In the deep-Sommerfeld regime (kappa > kappa_c)** -- which is where
   the framework point (200 eV) and the Phase-3 best fit (126 keV) sit --
   the Born formula UNDERESTIMATES sigma/m. The true Lyman-alpha
   exclusion boundary is HIGHER (more permissive) than the Born curve
   shown. A validated deep-Sommerfeld solver (Hulthen/lattice) is
   needed to draw the true boundary in this regime.

4. **The kappa = kappa_c reference line** (green dash-dot) marks the
   s-wave bound-state threshold. To the right of this line, the Born
   formula breaks down and a deep-Sommerfeld solver is required.

## Caveats and follow-ups

- Lyman-alpha curve is Born-only; in deep-Sommerfeld regime the curve
  is a LOWER bound on alpha_D, the true exclusion region is HIGHER.
- Visible-decay constraints assume epsilon > 1e-10. For a fully
  decoupled (invisible) dark photon, those constraints vanish.
- BBN/CMB/SN1987A/XENONnT are quoted as 'vertical bands' because they
  constrain the kinetic mixing epsilon, not alpha_D directly. If the
  visible-decay scenario is realized, the bands represent regions where
  the dark photon must have epsilon < 1e-10 (invisible at those scales).
- Thermal relic constraint (<sigma v> ~ 3e-26 cm^3/s) is NOT shown
  because the framework candidate is non-thermal (per the constraint
  JSON: 'framework point NOT a thermal relic; no annihilation constraint').
