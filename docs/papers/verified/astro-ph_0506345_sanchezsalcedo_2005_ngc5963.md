# astro-ph/0506345 — Sánchez-Salcedo, Melnick & Vega 2005: dark matter in NGC 5963

**Status:** VERIFIED — full text read end-to-end 2026-11-13 from the downloaded PDF
(`verified/astro-ph_0506345_sanchezsalcedo_2005_ngc5963.pdf`; 254,727 bytes, PDF 1.4,
**13 pages**, sha256 `2d248a975735fe363e5c599c22a4568c2f1473df131493bb9c8a11d34e054371`,
integrity checked: magic `%PDF-` and `file(1)` reports "PDF document,
version 1.4, 13 page(s)"). Every number quoted below was read out of that text, not
from a summary.

**arXiv:** [astro-ph/0506345](https://arxiv.org/abs/astro-ph/0506345)
**Authors:** C. M. Sánchez-Salcedo (UNAM), J. Melnick (UNAM), L. Vega (UNAM)
**ApJ 626, 173–184 (2005)** (journal reference as printed on the arXiv page).

## What the paper does

H I rotation curve of the low-surface-brightness spiral **NGC 5963** is decomposed
with the disc-to-halo scaling factor Upsilon* swept over 0.07 – 1.2, and the halo is
then tested against **self-interacting dark matter with a velocity-dependent cross
section**:

```
sigma_dm(v_rel) = sigma_0 * (v_0 / v_rel)^a ,   v_0 = 100 km/s     (paper's eq. 13)
```

**This is the same convention this project uses**: `sigma_0` is quoted at
`V_REF = 100 km/s` (`scripts/constants.py: V_REF_KMS = 100.0`), and `a` is the
velocity index. So the paper's `sigma_0` maps onto the project's `sigma_m_0`
without a rescaling — the reason this paper is directly usable as a channel.

## Numbers quoted by v19.2-F (all verified against the PDF text)

| Quantity | Value | Where in the paper |
|---|---|---|
| Characteristic collision velocity in NGC 5963 | **v ~ 150 km/s** | §4 ("collisions at v ~ 150 km/s") |
| Core-collapse time for the decompressed NFW halo | **t_rc = 0.8 Gyr x (sigma_0 / 1 cm^2 g^-1)^-1** | eq. (7), halo with c' = 15.6, V_200' = 109 km/s (Upsilon* = 1.2 row of Table 1) |
| Upper limit requiring halo lifetime > 1 Hubble time | **sigma_0 <~ 0.08 cm^2 g^-1** (Upsilon* = 1.2), **<~ 0.05** (Upsilon* = 1.0) | §4.3; "this all but removes the permitted window sigma_0 = 0.3 – 1 for Upsilon* > 0.85" |
| Core-size / central-density upper limit | **sigma_0 <~ 0.2 cm^2 g^-1 at 95% CL** | §4.1/§4.2 ("a tight constraint sigma_0 < 0.2 cm2 g-1 at 95% confidence level") |
| Tightest core-size fit | **sigma_0 <~ 0.1 cm^2 g^-1** for Upsilon* ~ 1.2 | §4.2 conclusion; the authors add the limit "may be overestimated by as much as a factor 2 because of our conservative assumptions" |
| Worked example | r_c < 1 kpc and rho_0 = 0.4 M_sun pc^-3 -> **sigma_0 <= 0.035 cm^2 g^-1** | §4.2 |
| Observed decompressed halo, Upsilon* = 1.2 | c' = **15.6**, V_200' = **109 km/s** | Table 1 |
| Observed core radius / central density | r_c = **0.42 – 0.95 kpc**, rho_0 = **0.38 – 1.75 M_sun pc^-3** (isothermal fits; NFW-before-decompression cores 0.71 – 2.60 kpc) | Table 1 |
| SIDM-simulation reference the paper compares against | cores with rho ~ **0.02 M_sun pc^-3** and radii **2.5 – 5 kpc** for sigma v_100/m = 0.3 – 1 | §4.2 (Colín, Browning & Melnick 2002) |
| Alternative the paper considers | the halo may be **core collapsing** rather than having a small cross section | §1, §4.3 |

## The core argument, in one paragraph

NGC 5963's halo is dense and its core is small (rho_0 up to 1.75 M_sun pc^-3,
r_c ~ 0.4 – 0.95 kpc). SIDM at sigma/m ~ 0.3 – 1 cm^2/g would have produced a
big low-density core (rho ~ 0.02 M_sun pc^-3, r_c ~ 2.5 – 5 kpc) in a Hubble
time, and at sigma/m >~ 0.1 the halo would gravothermally collapse in
t_rc <~ 8 Gyr. Both readings exclude the cross-section band that was then being
proposed to explain flat rotation curves. **The constraint is an UPPER bound
with no lower bound**: sigma/m -> 0 (CDM) is fully allowed by this galaxy.

## v19.2-F relevance

- **Implemented** as `loglike_lsb_ngc5963_core()` in `v0.3-prelim/code/channels_lsb_core.py`
  (one-sided, soft in log space, zero penalty at sigma/m -> 0).
- **Ablated** in `v0.3-prelim/code/t13_v2_lsb_ablation.py` against the 12-channel
  T13_v2 baseline; results in `v0.3-prelim/data/results/t13_v2_lsb_ablation_2026-11-13.json`.
- Velocity caveat the code has to handle: the paper's *limit* is quoted in its own
  `sigma_0` normalisation (v_0 = 100 km/s), while the *physics* happens at the
  halo's collision velocity v ~ 150 km/s. The channel therefore evaluates
  `sigma_m_at_v(sigma_m_0, a, 150)` through `mediator_registry` and compares to
  the 0.2 cm^2/g ceiling. At `a = 1.481` (12-channel MAP) the implied ceiling on
  `sigma_m_0` is ~0.36 cm^2/g; at `a = 1.0` it is 0.30 cm^2/g.
- Single-galaxy evidence: the authors themselves note the analysis rests on one
  halo. Treat as a bracket, not a precise bound.

## Cross-references

- [[astro-ph_0506345 ... PDF]] — the downloaded primary source
- Concepts/Gravothermal Collapse — t_rc = 1/(3 rho sigma v) family; the repo's own
  calibrated version is `v0.3-prelim/code/gravothermal.py`
  (`t_core = 12.7 / sigma_m x (rho_s/1e7 M_sun kpc^-3)^-1 x t_dyn`, Balberg+ 2002)
- [[2605.05588 Kitazawa 2026]] — the LSB core-formation half of the same check
  (failed its own numerical cross-check; see that entry)
- Registry §7 LSB core channel row
