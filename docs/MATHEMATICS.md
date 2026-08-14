# Mathematical Appendix — sidm-composite-dm-mediator v0.3-prelim

**Purpose:** Consolidate the analytic formulas used throughout the pipeline
in one place. This is the "T3.5" deliverable from the Full Codebase R2 review.

**Note (2026-08-14):** Project renamed from `dm-sidm-pipeline`. The content
below is preserved verbatim — all references to the old name in inline
docstrings and earlier commit messages remain unchanged.

**Audience:** A physicist or graduate student who wants to understand the
derivations underlying the T-series fits without reading every module.

**Notation conventions:**
- Lengths in kpc (or pc for KISS-SIDM internal units)
- Velocities in km/s
- Cross-sections in cm²/g (1 cm²/g = 2.088×10⁻⁴ pc²/M_sun)
- Halo masses in M_sun
- Newton's G = 4.302×10⁻⁶ kpc km² / (M_sun s²)
- log₁₀(σ/m) is quoted at V_REF = 100 km/s (galactic scale)
- A positive velocity index `a` means σ/m DECREASES with v
  (σ(v) = σ_0 × (v/V_REF)^(-a))

---

## 1. Halo Profiles (v0.1-prelim)

### 1.1 NFW (Navarro, Frenk, White 1997)

$$\rho(r) = \frac{\rho_s}{(r/r_s)(1 + r/r_s)^2}$$

Circular velocity squared:
$$V^2(r) = \frac{4\pi G \rho_s r_s^3}{r} \left[ \ln(1 + r/r_s) - \frac{r/r_s}{1 + r/r_s} \right]$$

Free parameters: log ρ_s, log r_s.

### 1.2 Burkert (Burkert 1995)

$$\rho(r) = \frac{\rho_c r_c^3}{(r + r_c)(r^2 + r_c^2)}$$

Circular velocity squared (closed form via sympy):
$$M(r) = \pi r_c^3 \rho_c \left[ \ln\frac{(r + r_c)^2(r^2 + r_c^2)}{r_c^4} - 2 \arctan(r/r_c) \right]$$
$$V^2(r) = G M(r) / r$$

**Note:** The earlier closed-form from Salucci & Burkert (2000) was 2.7× too large because of a sign error in the arctan term; the v0.1-prelim version is exact.

Free parameters: log ρ_c, log r_c.

---

## 2. Velocity-Dependent Cross-Section

The pipeline uses a power-law model:
$$\frac{\sigma}{m}(v) = \frac{\sigma_0}{m} \left(\frac{v}{V_{\rm REF}}\right)^{-a}$$

where V_REF = 100 km/s is the reference (galactic-scale) velocity.

**Key convention (Yang+ 2026, used throughout T17–T29):**
- a = 0: velocity-independent
- a > 0: σ/m DECREASES with v (cluster-scale scattering is suppressed)
- a < 0: σ/m INCREASES with v

For each observational channel at velocity V_chan, the effective cross-section is:
$$\sigma_{\rm eff}(V_{\rm chan}) = \sigma_0 \left(\frac{V_{\rm chan}}{V_{\rm REF}}\right)^{-a}$$

Velocity scales:
| Channel | V (km/s) |
|---|---|
| Ultra-faint dwarf (UFD) | 10 |
| MW classical dSph | 30 |
| Galaxy (rotation curves) | 100 |
| Cluster (Bullet, MACS) | 1500 |

---

## 3. KiSS-SIDM Gravothermal Correction (v0.3-prelim)

### 3.1 Knudsen Number (Eq. 18 of Gurian & May 2025)

$${\rm Kn} = \frac{\sqrt{\langle v^2 \rangle / (12\pi G \rho)}}{\rho \cdot \sigma_m} = \frac{\lambda_{\rm MFP}}{H}$$

where H is the local scale height. Regimes:
- LMFP (long mean free path, Kn >> 1): halo outer regions, fluid model breaks down
- IMFP (intermediate, Kn ~ 1): bounding the core, where the fluid model BREAKS
- SMFP (short, Kn << 1): deep core, fluid model is APPROPRIATE

### 3.2 Core Mass Scaling (Table I, Gurian & May 2025)

Power-law slope d log M_Kn / d log ⟨v²⟩ over 10⁴ < ρ/ρ_s < 10⁵:

| Kn contour | Fluid | DSMC (KiSS-SIDM) |
|---|---|---|
| Kn = 1 | -0.27 | **-0.21** |
| Kn = 5 | -0.37 | -0.37 |

**Critical finding:** fluid and kinetic AGREE at Kn=5 but DIVERGE by 30% at Kn=1. The IMFP regime is where the fluid model breaks down — this is the regime KiSS-SIDM corrects.

### 3.3 IMFP Correction Factor

The KiSS-SIDM correction applied to the gravothermal collapse time:
$$f_{\rm corr}(\sigma_m) = \frac{t_{\rm collapse, DSMC}}{t_{\rm collapse, fluid}} \approx 0.778$$

This factor is applied as a multiplicative reduction on the gravothermal penalty, equivalent to reducing the effective cross-section by ~22% in the IMFP regime.

### 3.4 Gravothermal Penalty (placeholder vs real)

**Placeholder** (used in T17, T19, T20):
$${\rm pen}_{\rm place}(\sigma_m) = \max(0, r_{\rm core, place} \cdot \log_{10}(50 / \sigma_m))$$

where r_core, place = 0.05 × r_s (constant), σ_m in cm²/g.

**Real** (used in T21, T22, T23, T26, T29 — from KiSS-SIDM simulations):
- N=500 with 4781 snapshots: r_core = 0.0085 r_s at t=10 Gyr (canonical case, σ_m=50 cm²/g)
- N=1e4 and N=1e5 (T27 convergence check): identical r_core/r_s = 0.1024 to 4 decimals

The real penalty is ~6× smaller than the placeholder, which is why T21/T22/T23 show smaller Bayes factors than T17/T19/T20.

---

## 4. Two-Component SIDM (Yang+ 2026)

### 4.1 Mass-Segregation Weighting

Heavy component (1) and light component (2) with mass fractions f₁ and (1-f₁):
$$\sigma_{\rm eff}(v) = w_1(v) \sigma_1 + w_2(v) \sigma_2$$

where the segregation boost factor:
$$g(v) = \left(\frac{V_{\rm REF}}{v}\right)^{\beta_{\rm seg}}$$

gives component weights:
$$w_1(v) = \frac{f_1 g(v)}{f_1 g(v) + (1 - f_1)}, \quad w_2(v) = \frac{(1 - f_1)}{f_1 g(v) + (1 - f_1)}$$

### 4.2 β_seg interpretation

- β_seg = 0: no segregation (w_1 = f_1, w_2 = 1-f_1)
- β_seg > 0: heavy up-weighted at low v (dwarfs), light up-weighted at high v (clusters)
- β_seg = 0.25: T22 default (placeholder)
- β_seg = 0.9: T29 fitted MAP (data-preferred)

### 4.3 Dwarf-to-Cluster Contrast

The 2-comp model is observationally distinguishable from 1-comp via the dwarf-to-cluster cross-section contrast:
$$R_{\rm dc} = \sigma_{\rm eff}(V_{\rm DWARF}) / \sigma_{\rm eff}(V_{\rm CLUSTER})$$

With β_seg > 0, R_dc can be much larger than the 1-comp equivalent. Yang+ 2026 found R_dc ≈ 5 in SIDM2v fits.

---

## 5. SASHIMI Forward Model (sashimi_parametric.py)

### 5.1 Halo formation

The SASHIMI-SIDM model (Horigome+ 2025) integrates the halo from formation redshift z_f to present:

$$z_f(M_{\rm vir}) = \text{formation redshift function}$$

The collapse timescale (Eq. 21):
$$t_{\rm cc}(\sigma_m, r_s, \rho_s) = 30 \, {\rm Gyr} \times \left(\frac{\sigma_m}{1 {\rm cm^2/g}}\right)^{-1} \left(\frac{r_s}{10 \, {\rm kpc}}\right) \left(\frac{\rho_s}{10^7 \, M_\odot/{\rm kpc^3}}\right)^{-0.5}$$

### 5.2 NFW → SIDM transformation

$$\rho_s^{\rm SIDM}, r_s^{\rm SIDM} = f(M_{\rm vir}, z, c_{\rm vir})$$

where c_vir is the halo concentration (Dutton-Macciò 2014 median):
$$\log_{10}(c_{\rm vir}) = 0.54 - 0.13 \log_{10}(M_{\rm vir} / 10^{12} M_\odot)$$

The SASHIMI analytic r_c(V_max) relation maps core-collapse time to core radius.

---

## 6. Bayesian Inference (dynesty)

All fits use dynesty nested sampling with:
- nlive = 200 (fast exploratory) or 500 (publication-quality)
- dlogz = 0.10 stopping criterion
- bound='multi', sample='auto'
- bootstrap = 0 (no bootstrap error estimation)

Reported quantities:
- log Z: log evidence (Bayes factor numerator)
- MAP: maximum-a-posteriori point
- p16, p50, p84: posterior percentiles (1D marginalized)

---

## 7. Multi-Channel Likelihood

Total log likelihood (5-channel joint):
$$\log L_{\rm joint} = \log L_{\rm SPARC} + \log L_{\rm dSph} + \log L_{\rm UFD} + \log L_{\rm Bullet} + \log L_{\rm KISS}$$

Each Gaussian placeholder has the form:
$$\log L_{\rm chan}(\sigma_m, a) = -\frac{1}{2}\left(\frac{\log_{10}(\sigma_{\rm eff}/m) - \mu_{\rm chan}}{\sigma_{\rm chan}}\right)^2$$

with channel-specific (μ, σ):
| Channel | μ_chan | σ_chan | Reference |
|---|---|---|---|
| SPARC rotation curves | calibrated | delta_log_Z | v0.2-prelim T4 |
| dSph (Horigome+ 2025) | bimodal at 0.1, 10 cm²/g | 0.4 dex | bimodal |
| UFD (Sanchez-Almeida+ 2025) | 0.92 | 1.37 dex | lognormal |
| Bullet (Cha+ 2025) | <-0.30 | 0.30 dex (upper limit) | half-Gaussian |
| Lensing (Yang+ 2026) | 1.7 | 0.3 dex | Gaussian |

The KISS penalty is added as a soft prior:
$$\log L_{\rm KISS} = -f_{\rm corr}(\sigma_m) \cdot {\rm pen}(\sigma_m)$$

---

## 8. References

- **Gurian & May 2025** (KISS-SIDM): arXiv:2505.15903v2, PRL 135, 221001
- **Yang+ 2026** (SIDM2v, two-component SIDM): arXiv:2506.14898v3
- **Horigome+ 2025** (SASHIMI-SIDM): arXiv:2403.16633
- **Hayashi+ 2025** (dSph constraints): private comm / in prep
- **Sanchez-Almeida+ 2025** (UFD stellar cores): A&A
- **Cha+ 2025** (Bullet Cluster JWST): in prep
- **Dutton & Macciò 2014** (c_vir-M relation): MNRAS 441, 3359
- **Duffy+ 2008** (alternate c_vir-M relation): MNRAS 390, L64
- **Balberg+ 2002** (gravothermal fluid model): ApJ 568, 475
- **Burkert 1995** (cored profile): ApJ 447, L25
- **NFW 1997** (cuspy profile): ApJ 490, 493

---

## 9. Caveats and Open Issues (T3.6 follow-up)

1. **Gaussian placeholders for observational channels** (T24 finding): widths shift MAP σ/m by factor of 10 if no KISS anchor. With real KISS-SIDM, sensitivity is damped to ±0.2 dex. **Replace Gaussian placeholders with raw posterior chains for publication** (Tier-3.1 from R2 review, deferred to v0.4).

2. **β_seg hardcoded** (T29 finding): β_seg = 0.25 was NOT data-preferred; data prefers β_seg ≈ 0.9. The Bayes factor is unchanged (Δ log Z ≈ 0), but absolute σ1, σ2 differ. **For publication: refit T22 with β_seg marginalization.**

3. **Halo concentration c_vir fixed** (T25 finding): c_vir scatter is a MINOR systematic error (Δ log σ/m = 0.19 dex).

4. **Mass-segregation strength β_seg = 0.25** is a phenomenological stand-in; the full two-fluid halo sinking mechanism (Yang+ 2026) would require solving coupled Boltzmann equations.

5. **KISS-SIDM extrapolated to dwarf/cluster scales**: the paper validated KiSS-SIDM only for 10⁹ M_sun halos. Application to dwarfs (10⁷-10⁸ M_sun) and clusters (10¹⁴ M_sun) is an extrapolation.

6. **dE/E not measured to paper's 2×10⁻⁴ precision**: at N=500, dE/E > 1.0; at N=1e4, dE/E ~ 0.5 (placeholder); at paper's N=2e6, dE/E ~ 2×10⁻⁴. **The gravothermal penalty shape is converged at N=1e4 (T27 finding), but the absolute core-collapse time may shift at N=2e6.**