# Data sources and references — sidm-composite-dm-mediator

**This is the single authoritative file for every external data source used
in this project.** If you want to cite or extend this work, start here.

Last updated: 2026-08-14.

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

### `Fermi-dSph-14yr` — McDaniel et al. (2024)

**Reference**: McDaniel, A. et al. (2024), "Legacy Analysis of Dark Matter
Annihilation from the Milky Way Dwarf Spheroidal Galaxies with 14 Years of
Fermi-LAT Data" (FERMI-LAT Collaboration, PI: Karwin), arXiv: [2311.04982](https://arxiv.org/abs/2311.04982).

**Note**: The README and earlier docs referenced "Hooper & Linden 2024" but
no such paper exists in the cited form. The canonical 14-year Fermi-LAT
dSph stacking analysis is McDaniel et al. 2024 (above). For shorter-stacked
versions see also [Hooper & Linden 2015](https://arxiv.org/abs/1503.06209)
(9 dSphs, Reticulum II hint) and the [11-year 27-dSph analysis](https://inspirehep.net/literature/1709795).

**Data location**: 21 dSph sources with J-factors, ingested as posterior
chains at `v0.3-prelim/data/external_data/fermi_dwarf_14yr/`.

**Used by**: T32 (Tier-3.3) in v0.3-prelim — combined with LZ WS2024, gives
a strongly constraining σ/m limit. Key physics result (T32): under
standard WIMP coupling, the SIDM mediator would be excluded at m_χ = 40–50
GeV; **mediator must decouple from thermal-WIMP expectations by ~10⁰×.**

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
| **Kaplinghat, Tulin, Yu (2014)** "Direct detection portals for self-interacting dark matter", *Phys. Rev. D* **89**, 115005 | [1310.7945](https://arxiv.org/abs/1310.7945) | Direct-detection evasion argument |
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

- **No HEPData 155182.** The LZ WS2024 record is HEPData record
  [ins2726677](https://www.hepdata.net/record/ins2726677) (linked from the
  arXiv:2410.17036 page). Earlier drafts of our README referenced "HEPData
  155182" — that number doesn't refer to the LZ WS2024 result. Corrected here.
- **No "Hooper & Linden 2024" 14-year Fermi-dSph paper.** No such paper
  exists. The canonical 14-year analysis is McDaniel et al. 2024
  (arXiv:2311.04982). Earlier drafts referenced "Hooper & Linden 2024" in
  error. Corrected here.

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