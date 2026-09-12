# LIGO + CERN/LHC probes for SIDM and iDM — background reference (2026-09-12)

**Status:** BACKGROUND REFERENCE ONLY. None of the 6 mechanisms listed are actionable channel additions for the current project's parameter space (elastic, point-like, GeV–TeV WIMP-mass SIDM). Saved for future model-extension work.

**Source:** `ligo.docx` (uploaded by user 2026-09-11 17:06 CST, author V2545A)
**Length:** 9 substantive paragraphs

---

## Why this is background-only (per AGENTS.md rule 11 — honest framing)

The current project's parameter space:
- **Mass:** m_χ ~ GeV–TeV (WIMP-like, point-like)
- **Velocity:** v ~ 10–1000 km/s (galactic/cluster scales)
- **Model:** elastic SIDM, σ/m_0 ∈ [0.001, 1000] cm²/g, velocity dependence a ∈ [0, 3]
- **Couplings:** ε (kinetic mixing), α (dark coupling), both in particle-physics prior

**Mapping each of the 6 mechanisms to project applicability:**

| # | Mechanism | Project regime | Applicable? |
|---|---|---|---|
| 1 | BBH Inspiral Dephasing (GW190728) | σ/m at v~c, relativistic | **NO** — wrong velocity regime |
| 2 | Superradiant Cloud Bounds (Cygnus X-1) | m_χ ~ 10⁻¹⁴–10⁻¹¹ eV (ultralight boson) | **NO** — wrong mass scale + wrong model class |
| 3 | Direct Interferometer Noise (H1/L1/Virgo) | m_{A'} ~ 10⁻¹³ eV, ε² ≲ 10⁻⁴⁷ | **MARGINAL** — LIGO bounds weaker than astro/cosmo bounds at this mass |
| 4 | Displaced Vertices + Soft Leptons (ATLAS/CMS/LHCb/FASER/MATHUSLA) | iDM, χ₂ → χ₁ decay | **NO** — wrong model class (inelastic, not elastic) |
| 5 | Monojet + E_T (Run 2/3) | ε, g_D for compressed iDM | **MARGINAL** — LHC ε bounds not constraining at project m_A' range |
| 6 | Emergent Jets & Dark Showers (dark QCD) | Λ_dark ~ GeV, composite SIDM | **NO** — wrong model class (composite, not point-like) |

**3/6 mechanisms probe wrong model class** (ultralight, inelastic, composite).
**2/6 probe wrong regime** (relativistic BBH, ultralight dark photon).
**1/6 (LHC monojet)** is potentially relevant but not constraining.

---

## The 6 mechanisms (verbatim from source)

### LIGO/KAGRA (3)

1. **BBH Inspiral Dephasing** (SIDM Core Saturation & Bosenova Instabilities):
   Strain data from binary black hole mergers (e.g., GW190728) tests dark matter spikes. Repulsive self-interactions (λφ⁴ > 0) saturate local DM density around compact binaries; attractive self-interactions (λ < 0) trigger bosenova-like cloud implosions during inspiral. Both alter environmental dynamical friction and produce measurable phase shifts relative to vacuum waveforms.

2. **Superradiant Cloud Bounds** (Ultralight SIDM Self-Coupling):
   Searches for continuous monochromatic gravitational waves and stellar-mass black hole spin-down data (e.g., Cygnus X-1 using LVK O3 strain) constrain ultralight scalar/vector bosons (m_χ ~ 10⁻¹⁴–10⁻¹¹ eV). Non-zero self-interactions bound cloud growth via non-linear scattering, placing constraints on the self-coupling constant and preventing premature spin exhaustion.

3. **Direct Interferometer Noise** (Gauge Mediators for SIDM/iDM):
   Cross-correlation of background strain noise across LIGO Hanford, Livingston, and Virgo sets direct upper limits on vector dark photons A'—a primary candidate mediator for velocity-dependent SIDM and iDM mass splittings. For U(1)_B or U(1)_{B-L} couplings, direct mirror acceleration limits gauge coupling to ε² ≲ 10⁻⁴⁷ around m_{A'} ≈ 10⁻¹³ eV.

### CERN/LHC (3)

4. **Displaced Vertices & Soft Lepton Signature** (iDM Lifetime Frontier):
   Dedicated LLP searches in ATLAS, CMS, LHCb, and forward detectors (FASER, MATHUSLA) target inelastic DM with mass splittings Δm = m_χ₂ - m_χ₁. While direct detection is suppressed at v ~ 10⁻³c, LHC collisions produce boosted χ₂ that decays into χ₁ + e⁺e⁻/μ⁺μ⁻/π⁺π⁻, yielding displaced low-p_T tracks with missing transverse energy (E_T).

5. **Monojet + E_T Channels** (Compressed iDM & Heavy Mediators):
   Prompt high-p_T jet recoil against missing energy (p_T^jet + E_T) in ATLAS/CMS Run 2/3 constrains iDM parameter space where Δm ≲ MeV or decay products of χ₂ are too soft to reconstruct, bounding dark photon kinetic mixing ε and dark sector coupling g_D.

6. **Emergent Jets & Dark Showers** (Composite SIDM & Confinement Scales):
   Jet substructure analyses for semi-visible and emergent jets constrain composite DM models (e.g., dark QCD). High-energy production of dark quarks leads to dark hadronization, where dark pion self-interactions govern the ratio of visible decay products to invisible dark stable hadrons, probing dark confinement scales at Λ_dark ~ GeV.

---

## What would be needed to make any of these actionable

If the project ever extends, here's what each would require:

| Mechanism | Required extension | Difficulty |
|---|---|---|
| 1 (BBH dephasing) | Extend σ/m(v) model to v~c regime | Medium (months) — new physics regime |
| 2 (Superradiance) | Add ultralight boson sector (m_χ ~ 10⁻¹⁴ eV) | High (year+) — fundamentally different mass scale |
| 3 (LIGO dark photon) | Add ultralight vector A' sector | High (year+) — same as #2 |
| 4 (Displaced vertices) | Extend to inelastic DM (χ₁ + χ₂ with Δm) | Medium (months) — 2-state model |
| 5 (Monojet) | Same as #4 + LHC pipeline | Medium (months) |
| 6 (Emergent jets) | Replace point-like with composite SIDM | High (year+) — dark QCD framework |

**None of these are channel additions** — they are all model-class extensions requiring new physics, new data pipelines, and likely new priors.

---

## Why LIGO dark photon (#3) bounds are weak at m_{A'} ~ 10⁻¹³ eV

The document claims ε² ≲ 10⁻⁴⁷ at m_{A'} ~ 10⁻¹³ eV from LIGO mirror acceleration. For comparison:
- **Stellar cooling bounds** (HB stars, SN1987A): ε² ≲ 10⁻⁵² at this mass scale (much stronger)
- **Cosmic microwave background** (Planck): ε² ≲ 10⁻⁵² at this mass scale
- **LIGO bounds** are competitive **only** at m_{A'} ≲ 10⁻¹⁴ eV where stellar/CMB bounds turn off

So mechanism #3 is **3-5 orders of magnitude weaker** than existing bounds at the same parameter space. Not constraining.

---

## What this doc is good for

1. **Roadmap reference** for future project extensions
2. **Cross-check** that the project's parameter space is well-defined (none of these 6 accidentally overlap)
3. **Educational** — list of state-of-the-art SIDM/iDM probes for collaborators
4. **Placeholder** if someone wants to add ultralight / inelastic / composite sectors later

---

## Tracking

- **Uploaded:** 2026-09-11 17:06 CST (V2545A)
- **Read:** 2026-09-12 (end-to-end, 9 paragraphs)
- **Verdict:** Background reference only — NOT actionable for current project
- **Saved to repo:** 2026-09-12 (this file)
- **Code changes:** none
- **Channel additions:** none

Reference: `ligo.docx` (parent upload)
Honest framing per AGENTS.md rule 11: saving the doc because it's useful background, not because it produces immediate value. Per AGENTS.md rule 22 (no auto-install): no new dependencies, no channel additions, no code changes implied.