consider if any datsets are useful for our project:
For a Bayesian joint-fit pipeline targeting Self-Interacting Dark Matter (SIDM) with a composite dark matter / secluded mediator framework (chenhk1113-HK/sidm-composite-dm-mediator), the primary empirical challenge is constraining the velocity-dependent cross-section \sigma/m(v) across three orders of magnitude in relative velocity (v \sim 10 \text{ km/s} to 1000 \text{ km/s}), alongside bounds on secluded mediator decays.
Several recent datasets from current-generation space telescopes provide critical observational constraints:
1. High-Velocity Scale (v \sim 1000 \text{ km/s}): Galaxy Cluster Cores & Lensing
Composite mediator models often predict a sharp suppression or saturation of \sigma/m at cluster velocities to satisfy Bullet Cluster-type bounds (\sigma/m \lesssim 0.1 \text{ cm}^2/\text{g}).
 * JWST Deep Cluster Strong Lensing (e.g., AS1063, Abell 2744 / Pandora, SMACS 0723):
   * Data Available: Ultra-deep JWST NIRCAM strong-lensing maps resolve cluster dark matter core sizes (R_{\text{core}}) and central mass profiles down to r < 10 \text{ kpc}.
   * Utility for Joint Fit: For example, recent JWST lensing analyses of AS1063 show large, flat dark matter cores co-spatial with globular cluster distributions. Comparing these observed core radii against SIDM gravothermal core-expansion predictions provides a clean prior on \sigma/m at v \approx 1000 \text{ km/s}.
 * Euclid Space Telescope – Early Data Releases (EDR & DR1 Cluster Catalogs):
   * Data Available: Wide-field weak and strong lensing maps covering thousands of massive clusters (z \sim 0.2 - 1.5).
   * Utility for Joint Fit: Euclid provides statistical samples of cluster density profiles (\rho(r)) and central Brightest Cluster Galaxy (BCG) offsets (sloshing amplitude within the core), establishing tight upper limits on high-velocity momentum-transfer cross-sections.
2. Intermediate to Low-Velocity Scale (v \sim 10 - 300 \text{ km/s}): Subhalos & Dwarf Satellites
Composite DM models (e.g., dark bound states or resonant scattering via light mediators) often feature strong velocity dependence (\sigma/m \propto v^{-4} or resonant peaks at low v).
 * Euclid Strong Lensing Substructure Sample:
   * Data Available: Euclid's high-resolution VIS instrument is cataloging \sim 170,000 strong galaxy-galaxy lenses. Sensitivity maps allow detection of dark matter subhaloes down to M_{\text{sub}} \sim 10^8 - 10^9 M_\odot.
   * Utility for Joint Fit: SIDM causes subhalo tidal evaporation and core collapse inside host halos. The observed subhalo mass function (dN/dM) from Euclid lens samples constrains subhalo survival rates against v-dependent SIDM interactions at v \approx 100 - 200 \text{ km/s}.
 * JWST Resolved Stellar Kinematics of Local Group Ultra-Faint Dwarfs (UFDs):
   * Data Available: NIRCam resolved stellar photometry and proper motions of ultra-faint dwarf satellites (e.g., Eridanus II, Tucana II).
   * Utility for Joint Fit: Probes the lowest velocity regime (v \sim 10 - 30 \text{ km/s}). Constrains whether low-velocity cross-sections hit the unitary limit (\sigma/m \sim 10 - 100 \text{ cm}^2/\text{g}) or undergo gravothermal core collapse.
3. Intermediate Mass Gap (v \sim 300 - 800 \text{ km/s}) & Mediator Decays
 * eROSITA All-Sky Survey (eRASS Group/Cluster Catalogs):
   * Data Available: X-ray catalogs covering tens of thousands of galaxy groups and small clusters.
   * Utility for Joint Fit: Fills the crucial "velocity gap" between dwarf galaxies and massive clusters, where mediator resonance effects or composite up-scattering thresholds typically manifest in the theoretical phase space.
 * XRISM (X-ray Imaging and Spectroscopy Mission) – Resolve Microcalorimeter:
   * Data Available: High-resolution X-ray spectroscopy (<5 \text{ eV} resolution) of intracluster medium (ICM) gas in cluster cores (e.g., Perseus Cluster).
   * Utility for Joint Fit:
     * Baryonic vs. SIDM Disambiguation: Measures precise ICM velocity dispersions and gas turbulence, helping isolate baryonic feedback from genuine SIDM core formation.
     * Secluded Mediator Constraints: If the secluded mediator \phi has a small portal coupling to Standard Model states (e.g., \phi \to \gamma\gamma or e^+e^-), XRISM’s spectral line resolution sets stringent limits on dark matter decay/annihilation line features in cluster cores.
Summary of Observational Inputs for the Likelihood Function
| Telescope / Dataset | Scale / Velocity Regime | Target Observable | Likelihood Term in Pipeline |
|---|---|---|---|
| JWST Lensing (AS1063/Pandora) | v \sim 1000 \text{ km/s} | Cluster core radius R_{\text{core}} & central profile | \mathcal{L}_{\text{cluster\_core}}(\sigma/m \vert_{v\sim 1000}) |
| Euclid VIS Lensing | v \sim 100 - 200 \text{ km/s} | Subhalo mass function cutoff (M_{\text{sub}}) | \mathcal{L}_{\text{subhalo}}(\text{evaporation}) |
| JWST UFD Kinematics | v \sim 10 - 30 \text{ km/s} | Central density \rho_0 / core-cusp profile | \mathcal{L}_{\text{dwarf\_core}}(\sigma/m \vert_{v\sim 20}) |
| XRISM Resolve Spectroscopy | All Scales / Energy | Cluster gas velocity & X-ray line flux limits | \mathcal{L}_{\text{mediator\_decay}}(m_\phi, \epsilon) |