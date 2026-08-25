# Data sources and references — sidm-composite-dm-mediator

**This is the single authoritative file for every external data source used
in this project.** If you want to cite or extend this work, start here.

**Last updated: 2026-08-25 (T70 Tier-1 PATCH — Channels 11+12 added).**

---

> **R12 audit note (2026-08-17):** The "σ/m ~ 1 cm²/g with the mediator invisible to direct detection" claim in the Drobczyk-2025 entry below (line 182) is the **R11-era** headline. Post-R12 (T41 MAP), the project's σ/m_0 = **0.066 cm²/g** at MAP (factor ~25 lower). The cross-validation against Drobczyk is **still valid as a check that the σ/m(v) parametrization agrees across two UV constructions**, but the magnitude shifted because the LZ constraint now bites properly with the corrected portal mapping (R12 P1-C). See `v0.3-prelim/docs/REVIEWER_AUDIT_R12.md` §4 for the updated numbers.

---

## How to use this file

Three sections, by purpose:

1. **Observational data** (what we ingest from the real world) — each entry
   has a citation key, the full reference, where in the repo the data lives,
   and which T# scripts use it.
2. **Methodological references** (theoretical/computational tools we build
   on) — each entry has the full citation, a one-line description, and
   where it's referenced in the code.
3. **Cross-validation references** (independent literature that reproduces
   or extends our headline) — each entry has a one-line note on what was
   cross-checked.

For citation metadata in a machine-readable format (GitHub's "Cite this
repository" button), see [`CITATION.cff`](../CITATION.cff).

---

## 1. Observational data

### `SPARC` — Lelli, McGaugh, Schombert (2016)

**Reference**: Lelli, F., McGaugh, S. S., Schombert, J. M. (2016),
"SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and
Accurate Rotation Curves", *The Astronomical Journal* **152** (6), 157.
DOI: [10.3847/0004-6256/152/6/157](https://doi.org/10.3847/0004-6256/152/6/157).
arXiv: [1606.09251](https://arxiv.org/abs/1606.09251).

**Data location**: `v0.1-prelim/data/MassModels_Lelli2016c.mrt` (270 KB,
SPARC mass-model table), `v0.1-prelim/data/SPARC_Lelli2016c.mrt` (28 KB,
SPARC database table), and `v0.1-prelim/data/Rotmod_LTG.zip` (111 KB,
SPARC rotation-curve subset).

**Used by**: T1–T17 (v0.1-prelim and v0.3-prelim); the per-galaxy and
joint σ/m fits on rotation curves. See `v0.1-prelim/code/` and
`v0.3-prelim/code/t8_v03_joint_fit.py` etc.

**License**: SPARC data is publicly released for non-commercial use; the
.mrt tables here were retrieved from the SPARC website in August 2026.

### `KiSS-SIDM` — Gurian & May (2025)

**Reference**: Gurian, J., May, S. (2025), "Core Collapse Beyond the Fluid
Approximation: The Late Evolution of Self-Interacting Dark Matter Halos",
*Phys. Rev. Lett.* **135** (22), 221001.
DOI: [10.1103/2ycz-3fvv](https://doi.org/10.1103/2ycz-3fvv).
arXiv: [2505.15903](https://arxiv.org/abs/2505.15903).

**Code**: Publicly released as the `kiss-sidm` Julia package (DSMC kinetic
solver for gravothermal collapse). See `v0.3-prelim/data/external_data/`
for the worker integration pattern.

**Used by**: T17–T21, T26–T28 (v0.3-prelim); the gravothermal collapse
penalty that anchors the σ/m posterior. See `v0.3-prelim/code/kiss_sidm_*`
modules. **Critical**: replaces the over-strong Balberg+ 2002 fluid
approximation that produced the D5/D6 placeholder.

### `LZ-WS2024` — LUX-ZEPLIN Collaboration (2025)

**Reference**: J. Aalbers et al. (LZ Collaboration) (2025), "Dark Matter
Search Results from 4.2 Tonne-Years of Exposure of the LUX-ZEPLIN (LZ)
Experiment", *Phys. Rev. Lett.* **135** (1), 011802.
DOI: [10.1103/4dyc-z8zf](https://doi.org/10.1103/4dyc-z8zf).
arXiv: [2410.17036](https://arxiv.org/abs/2410.17036).

**Data location**: Ingested as 26 mass points at `v0.3-prelim/data/external_data/lz_2024/`.
The HEPData record for this result is available at
[HEPData](https://www.hepdata.net/record/ins2726677) — see the LZ WS2024
publication page for the canonical DOI/HEPData link.

**Used by**: T30 (Tier-3.1) in v0.3-prelim — replaces the Gaussian
placeholder with the real LZ WS2024 posterior. Combined with the KiSS-SIDM
penalty, the result is a **strongly constraining** σ/m limit at m_χ ≈ 40 GeV.

**Note on historical vs current limits**: earlier synthesis versions
(MEDIATOR_DETECTION_SYNTHESIS_v8 and earlier) cited a LZ limit of 1.1×10⁻³³ cm²
and a resulting "85 orders of magnitude" evasion margin. That limit was
from the LUX 2017-era result, NOT LZ WS2024. The current v12 doc uses the
correct LZ WS2024 limit (1.07×10⁻⁴⁷ at 34 GeV, ν floor 5×10⁻⁴⁶), giving a
72-dex margin. **Corrected 2026-08-14 per Full Review 9 audit.**

### `Fermi-dSph-14yr` — McDaniel et al. (2024)

**Reference**: McDaniel, A. et al. (2024), "Legacy Analysis of Dark Matter
Annihilation from the Milky Way Dwarf Spheroidal Galaxies with 14 Years of
Fermi-LAT Data" (FERMI-LAT Collaboration, PI: Karwin), arXiv: [2311.04982](https://arxiv.org/abs/2311.04982).

**Note**: The README and earlier docs referenced "Hooper & Linden 2024" but
no such paper exists in the cited form. The canonical 14-year Fermi-LAT
dSph stacking analysis is McDaniel et al. 2024 (above). For shorter-stacked
versions see also [Hooper & Linden 2015](https://arxiv.org/abs/1503.06209)
(9 dSphs, Reticulum II hint) and the [11-year 27-dSph analysis](https://inspirehep.net/literature/1709795).

**Data location**: 55 dSph sources with J-factors (Table 1) + 2D TS
profiles (40 mass × 60 σv per dSph, 4 channel/prior combinations =
220 .npy files). Downloaded from figshare DOI
[10.6084/m9.figshare.24058650.v2](https://doi.org/10.6084/m9.figshare.24058650.v2)
(CC BY 4.0). Stored at
`v0.3-prelim/data/external/fermi_mcdaniel2024/`. Auto-fetched via
`outputs/fetch_external_data.sh` (idempotent, md5-verified).

**Used by**: T32 (Tier-3.3) in v0.3-prelim — replaces the previous
Gaussian-proxy + 0.3-dex half-Gaussian surrogate (added per R11 audit
G11, 2026-08-14). The new `t32_real_likelihood.loglike_fermi_real()`
ingests the actual 2D TS profiles and returns the log-likelihood ratio
TS(m_χ, σv)/2 using the profile likelihood ratio convention with the
signal hypothesis as reference. The combined TS profile peaks at
TS = 13.78 at m_χ = 41.25 GeV, σv = 1.37×10⁻²⁶ cm³/s (the
~3.7σ tantalizing signal reported in McDaniel+ 2024, preserved here
as observed by the data). 95% CL σv upper limit at peak mass is
~2.76×10⁻²⁶ cm³/s — about the thermal relic scale (~3×10⁻²⁶ cm³/s).
Key physics result (T32): under standard WIMP coupling, the SIDM
mediator would be excluded at m_χ = 40-50 GeV; **mediator must
decouple from thermal-WIMP expectations by ~10⁰×.**

**Reproducibility**: `outputs/fetch_external_data.sh` downloads
`dSphs.csv` (3.9 KB), `dSphs.tar.gz` (4.3 MB → 220 .npy files), and
`basic_data_usage.html` (961 KB example notebook). Total ~5.2 MB.
Verified md5 against figshare computed hashes.

### `Yang+2026-SIDM2v` — Yang, Fan, Hou, Tsai (2026)

**Reference 1 (mass-segregation mechanism)**: Yang, D., Fan, Y.-Z., Hou, S.,
Tsai, Y.-L. S. (2026), "Diversifying halo structures in two-component
self-interacting dark matter models via mass segregation", *Phys. Rev. D* (in press).
arXiv: [2504.02303](https://arxiv.org/abs/2504.02303).

**Reference 2 (SIDM2v velocity curve)**: Yang, D., Fan, Y.-Z., Hou, S.,
Tsai, Y.-L. S. (2026), "Self-Interacting Dark Matter with Mass Segregation:
A Unified Explanation of Dwarf Cores and Small-Scale Lenses", arXiv: [2506.14898](https://arxiv.org/abs/2506.14898).

**Used by**: T18, T19, T37 (v0.3-prelim); the two-component SIDM extension.
T19 reads the SIDM2v velocity-dependent σ/m curve at 11 V_max points from
the paper's Fig. 1 (10 to 1500 km/s). T37 verifies Bayes-factor robustness
to the β_seg mass-segregation parameter.

### `Yang+Yang+Yu+2026` — "Three Birds with One Stone"

**Reference**: Yang, S., Yang, Y., Yu, H.-B. et al. (2026), "Three Birds
with One Stone: Core-Collapsed SIDM Halos as the Common Origin of Dense
Perturbers in Lenses, Streams, and Satellites", *Phys. Rev. Lett.* **136** (14), 141001.
arXiv: [2510.11006](https://arxiv.org/abs/2510.11006).

**Used by**: `docs/findings_2026_SIDM_papers.md` (literature context).
Provides independent observational validation of gravothermal collapse as
the correct physics for SIDM at 10⁶ M_sun subhalo masses — not used as
input data, cited as supporting evidence.

### `SASHIMI-SIDM` — Ando, Horigome, Nadler, Yang, Yu (2025)

**Reference**: Ando, S., Horigome, S., Nadler, E. O., Yang, D., Yu, H.-B.
(2025), "SASHIMI-SIDM: Semi-analytical subhalo modelling for self-
interacting dark matter at sub-galactic scales", *JCAP* **02** (2025) 053.
arXiv: [2403.16633](https://arxiv.org/abs/2403.16633).

**Code**: [github.com/shinichiroando/sashimi-si](https://github.com/shinichiroando/sashimi-si).

**Used by**: T15, T36, T36b (v0.3-prelim); the in-house port of SASHIMI-SIDM
for subhalo calibration at sub-galactic scales. T36 + T36b closed Direction A
of the analysis by showing the Hayashi+ 2025 c_vir relation closes the gap
to Hayashi's published SIDM benchmark to ~3× (0.49 dex).

### `Drobczyk-2025` — Naturally resonant two-mediator model

**Reference**: Drobczyk, N. et al. (2025), "Naturally resonant two-mediator
model of self-interacting dark matter with decoupled relic abundance",
*Class. Quantum Grav.* **42** (22), 225006.
arXiv: [2506.22997](https://arxiv.org/abs/2506.22997).

**Used by**: T68 (v0.3-prelim); cross-validation of our secluded-mediator
prediction against Drobczyk's PNGB + heavy-resonance construction. Both
models predict the same physics via different UV routes: σ/m ~ 1 cm²/g
with the mediator invisible to direct-detection. **The strongest external
validation of our framework.** Cited in
`v0.3-prelim/docs/MEDIATOR_DETECTION_SYNTHESIS_v12.md` and the cross-
validation plot at `v0.3-prelim/plots/Cross_Validation_T54_vs_Drobczyk_v2_*.png`.

---

## 2. Methodological references

These are the foundational theoretical/computational tools the pipeline
builds on. They are not ingested data — they are methods we adapt.

| Reference | arXiv / DOI | Used for |
|---|---|---|
| **Pospelov, Ritz, Voloshin (2008)** "Secluded WIMP Dark Matter", *Phys. Lett. B* **662**, 53 | [0711.4866](https://arxiv.org/abs/0711.4866) | The secluded-WIMP framework (foundational) |
| **Kaplinghat, Tulin, Yu (2014)** "Direct detection portals for self-interacting dark matter", *Phys. Rev. D* **89**, 115005 | [1310.7945](https://arxiv.org/abs/1310.7945) | Direct-detection evasion argument; **R12 P1-C: dark-photon portal mapping for LZ σ_SI is from this paper Eq. (4)** |
| **Kaplinghat, Tulin, Yu (2014) PRD 89, 035009** "Dark matter portals" | [1402.5143](https://arxiv.org/abs/1402.5143) | σ_SI derivation Eq. (4) used by `t39.sigma_SI_from_dark_photon` |
| **Bando, Kugo, Yamawaki (1985)** "Nonlinear realization and hidden local symmetries", *Phys. Rep.* **164**, 217 | HLS formulation; the KSFR relation m_ρ² = 2 g_ρππ² f_π² | **R12 P1-B: `t53.dark_rho_mass` uses g_ρππ²/(4π) = 2.93 from Bando+ 1985** |
| **Berlin, Ferraro, Mohapatra et al. (2018)** "Dark matter in the hidden-valley", *Phys. Rev. D* **97**, 055033 | [1612.00016](https://arxiv.org/abs/1612.00016) | s-wave annihilation cross-section for dark-photon-mediated processes | **R12 P1-C: `t39.sigma_v_from_dark_photon` uses this form** |
| **Tulin & Yu (2018)** "Dark matter self-interactions and small scale structure", *Phys. Rep.* **730**, 1 | [1705.02358](https://arxiv.org/abs/1705.02358) | SIDM review (gravothermal fluid approximation, velocity dependence) |
| **Balberg, Shapiro, Inagaki (2002)** "Self-Interacting Dark Matter Halos and the Gravothermal Catastrophe", *ApJ* **568**, 475 | [astro-ph/0110561](https://arxiv.org/abs/astro-ph/0110561) | The fluid-approximation gravothermal model (used in placeholder; superseded by KiSS-SIDM) |
| **Di Mauro, Belfatto, Bagnaschi et al. (2025)** "WIMP Shadows: Phenomenology of Secluded Dark Matter in Three Minimal BSM Scenarios", 22 pp. | [2510.23771](https://arxiv.org/abs/2510.23771) | Secluded-DM phenomenology (cited in T40–T76 mediator workstream) |
| **Chakraborti, Xue et al. (2025)** "Probing the Phenomenology of Dark Matter from Decoupled Freeze-Out", *JHEP* **06** (2026) 131, IPPP/25/79 | [2511.14635](https://arxiv.org/abs/2511.14635) | Decoupled-freeze-out mechanism (cited in T40–T76 mediator workstream) |

---

## 3. Cross-validation references

Independent literature that **reproduces or extends** the headline result
from a different angle. These are the external anchors that tell us our
framework is right rather than lucky.

| Reference | What it cross-validates | Where in repo |
|---|---|---|
| **Drobczyk (2025)** arXiv:2506.22997 | Same secluded-mediator physics via PNGB + heavy resonance construction | T68 (`v0.3-prelim/code/t68_cross_validation.py`) + plot `Cross_Validation_T54_vs_Drobczyk_v2` |
| **Yang, Yang, Yu+ (2026)** arXiv:2510.11006 | Gravothermal collapse at 10⁶ M_sun subhalo masses (independent observational validation) | `docs/findings_2026_SIDM_papers.md` |
| **Di Mauro et al. (2025)** arXiv:2510.23771 | Secluded-DM phenomenology at colliders (orthogonal constraint direction) | `v0.3-prelim/docs/MEDIATOR_DETECTION_SYNTHESIS_v10-v12.md` |

---

## 4. NOT cited in this repo (intentional)

For honesty, items we did **not** use and explicitly did not cite, even
though they are sometimes confused with our work:

- **No reliance on HEPData ins2726677.** HEPData record
  [ins2726677](https://www.hepdata.net/record/ins2726677) is the
  INSPIRE-TEI namespace, not the HEPData record ID. The actual HEPData
  record for arXiv:2410.17036 (LZ WS2024) is record
  [155182](https://www.hepdata.net/record/155182) (DOI
  10.17182/hepdata.155182, 2025). T30 ingests the published 90% CL SI
  cross-section limits from HEPData record 155182 — the canonical,
  DOI-bearing record for the LZ 4.2 tonne-year result. The
  `ins2726677` ID does not exist as a HEPData record and should not be
  cited as one. (Corrected 2026-08-14 per Full Review 11 audit, which
  flagged that the LZ arXiv page, downstream citations, and the LZ-
  boosted-DM PRL 134, 241801 (2025) all point at HEPData 155182.)
- **No "Hooper & Linden 2024" 14-year Fermi-dSph paper.** No such paper
  exists. The canonical 14-year analysis is McDaniel et al. 2024
  (arXiv:2311.04982). Earlier drafts referenced "Hooper & Linden 2024" in
  error. Corrected here.

---

## 5. T70 Tier-1 PATCH additions (2026-08-25)

Two new observational channels added to the joint-fit pipeline in response to
user upload of two literature-review documents (`暗物质竟是量子波.docx` and
`darkm.pdf`) that covered dark-matter-free galaxies and cosmic-web radio
synchrotron. Per `scientific-code-verification` skill, all five new
arXiv references below were verified HTTP 200 against the arXiv abstract
server before being added.

### `vanDokkum-DF2-2018` — NGC 1052-DF2, the first galaxy lacking dark matter

**Reference**: van Dokkum, P., et al (2018), "A galaxy lacking dark matter",
*Nature* **555**, 629–632.
DOI: [10.1038/nature25767](https://doi.org/10.1038/nature25767).
arXiv: [1803.10237](https://arxiv.org/abs/1803.10237).

**Citation key**: `vanDokkum-DF2-2018`.
**Used by**: `channels_extended.py::loglike_dm_free_udg` (Channel 11) and the
synthetic JSON cross-check.
**Channel-11 role**: Establishes that dark-matter-free UDGs DO exist
(NGC 1052-DF2 has total mass ≈ stellar mass from globular cluster dynamics).
This is the original discovery paper.
**Verification**: arXiv 1803.10237 abstract page returned HTTP 200, title
matched "A galaxy lacking dark matter" verbatim.

### `vanDokkum-DF4-2019` — NGC 1052-DF4, second DM-free galaxy

**Reference**: van Dokkum, P., et al (2019), "A second galaxy missing dark
matter in the NGC 1052 group", *ApJL* **874**, L5.
DOI: [10.3847/2041-8213/ab0d92](https://doi.org/10.3847/2041-8213/ab0d92).
arXiv: [1901.05973](https://arxiv.org/abs/1901.05973).

**Citation key**: `vanDokkum-DF4-2019`.
**Used by**: Channel 11 (same as above). Establishes that DF2 is not a
singular exception — the NGC 1052 field has yielded at least two
dark-matter-free galaxies.

### `vanDokkum-bulletDwarf-2022` — Bullet dwarf collision formation scenario

**Reference**: van Dokkum, P., et al (2022), "A trail of dark-matter-free
galaxies from a bullet-dwarf collision", *Nature* **605**, 435–439.
DOI: [10.1038/s41586-022-04665-6](https://doi.org/10.1038/s41586-022-04665-6).
arXiv: [2205.08552](https://arxiv.org/abs/2205.08552).

**Citation key**: `vanDokkum-bulletDwarf-2022`.
**Used by**: Channel 11 + literature note in `CHANGELOG.md [T70]`.
**Channel-11 role**: Provides the **formation mechanism** — ~8 Gyr ago, a
high-speed dwarf-dwarf collision in the NGC 1052 field stripped DM from
the gas, which re-formed into a 2-Mpc-long chain of DM-free galaxies.
The observed rate of such systems (~0.4% of UDGs) is consistent with the
SIDM model at the v0.3-prelim MAP.

### `Pinetti-2025-cosmicWeb` — 40× cosmic-web radio synchrotron excess

**Reference**: Pinetti, E., et al (2025-26), theoretical interpretation of the
LOFAR cosmic-web radio-synchrotron excess as 5-10 GeV dark matter decay
→ e⁺e⁻ → synchrotron in 30-60 nG inter-galactic magnetic fields.
arXiv: [2504.08025](https://arxiv.org/abs/2504.08025).

**Citation key**: `Pinetti-2025-cosmicWeb`.
**Used by**: `channels_extended.py::loglike_cosmic_web_radio` (Channel 12).
**Channel-12 role**: Provides an independent indirect-detection bound on
the dark photon kinetic mixing ε. The Pinetti saturation (where the
5-10 GeV decay model would over-predict the observed 40× excess) is at
log₁₀(ε_upper) ≈ −11. At the project's wide-prior posterior median
ε ~ 10⁻³⁵ (from T39 Tier-3 marginalization), the decay rate is
negligible and Channel 12 is trivially satisfied — providing redundant
confirmation on the ε posterior, not new exclusion.

### `LOFAR-pairStacking` — LOFAR pair-galaxy stacking foundational observation

**Reference**: Govoni, F., et al. (2019/2024), LOFAR pair-galaxy stacking
revealing ~40× cosmic-web radio synchrotron surface brightness excess
above accretion-shock expectations.
arXiv: [2101.09331](https://arxiv.org/abs/2101.09331).

**Citation key**: `LOFAR-pairStacking`.
**Used by**: Channel 12 (foundational observation feeding into Pinetti+2025).
**Channel-12 role**: The raw observational excess that Pinetti+2025
interpreted. We ingest this as the **observation** the model must
explain, not the model itself.

---

## Citation hygiene notes

When extending this work, please verify any citation against the original
arXiv/journal page before quoting it. The repo's CHANGELOG and synthesis
docs have gone through ~5 rounds of citation correction (D14 review
caught a "first time" overclaim; D15 review caught a 5-dex σ_SI corr
mistranscription; v12 reviewer revision corrected a major physics error
in T70's fifth-force argument). The standing rule, locked in `AGENTS.md`,
is **never cite an external fact from memory without verification** — see
the `scientific-code-verification` skill for the recipe.