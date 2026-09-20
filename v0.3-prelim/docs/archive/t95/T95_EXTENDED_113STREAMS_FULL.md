# T95.10 Full: 113-stream residual run

**Date:** 2026-09-08  
**galstreams catalog total:** 123  
**Curated (T95.9, excluded):** 10  
**Residual population:** 113  

## Outcome breakdown

- ✓ Pipeline OK: **95**
- ⚠ Outliers (v_3d > 700 km/s, suspicious data): **5**
- ✗ Degenerate kinematics (v_t=0, v_r=0): **13**
- ✗ Other failures (no track/velocity): **0**

## Wall time

- Catalog build: 1.83s
- Residual processing: 2.09s
- Per-stream avg: 0.018s
- Per-stream max: 0.09s

## Velocity and distance coverage (OK subset)

- v_3d range: 12.2 – 600.8 km/s
- d range: 1.00 – 50.10 kpc

## Joint loglikelihood

- Curated streams (T95.9, published constraints): 10
- Synthesized streams (this work, velocity-only): 95
- Total in joint fit: **105**
- Combined loglik (master Yukawa): **-12.038**

## Per-stream constraint table

Full table is in `outputs/t95/t95_v26_full_results.json`.

| ✓/✗ | Stream | d (kpc) | v_3d (km/s) | σ/m pred (cm²/g) | E[gaps] |
|---|---|---|---|---|---|
| ✓ | NGC7492 | 1.00 | 12.2 | 0.981 | 23.88 |
| ✓ | NGC1261b | 1.00 | 12.6 | 0.975 | 21.99 |
| ✓ | SGP-S | 1.00 | 15.5 | 0.943 | 14.12 |
| ✓ | C-10 | 1.00 | 18.3 | 0.845 | 3.21 |
| ✓ | Hydrus | 1.00 | 18.7 | 0.915 | 9.41 |
| ✓ | C-13 | 1.00 | 18.7 | 0.915 | 9.39 |
| ✓ | C-11 | 1.00 | 29.0 | 0.769 | 0.89 |
| ✓ | M2 | 1.00 | 29.3 | 0.852 | 3.57 |
| ✓ | Gaia-11 | 1.00 | 30.2 | 0.645 | 0.08 |
| ✓ | New-18 | 1.00 | 30.3 | 0.847 | 3.33 |
| ✓ | New-26 | 1.00 | 30.7 | 0.845 | 3.22 |
| ✓ | C-25 | 1.00 | 33.8 | 0.830 | 2.52 |
| ✓ | ACS | 11.70 | 36.7 | 0.822 | 2.19 |
| ✓ | Monoceros | 10.60 | 37.5 | 0.819 | 2.09 |
| ✓ | New-22 | 1.00 | 38.0 | 0.809 | 1.79 |
| ✓ | NGC1261a | 1.00 | 45.7 | 0.760 | 0.77 |
| ✓ | C-24 | 1.00 | 49.5 | 0.801 | 1.56 |
| ✓ | New-24 | 1.00 | 55.6 | 0.699 | 0.25 |
| ✓ | Yangtze | 9.12 | 56.4 | 0.767 | 0.87 |
| ✓ | New-1 | 1.00 | 61.4 | 0.721 | 0.38 |
| ✓ | Kwando | 1.00 | 63.8 | 0.715 | 0.34 |
| ✓ | New-25 | 1.00 | 69.1 | 0.752 | 0.67 |
| ✓ | C-9 | 1.00 | 71.8 | 0.750 | 0.64 |
| ✓ | NGC1261 | 1.00 | 74.3 | 0.700 | 0.25 |
| ✓ | Gaia-7 | 1.00 | 76.4 | 0.730 | 0.45 |
| ✓ | NGC5466 | 1.00 | 80.7 | 0.730 | 0.44 |
| ✓ | M68-Fjorm | 1.00 | 85.8 | 0.728 | 0.43 |
| ✓ | New-4 | 1.00 | 90.8 | 0.703 | 0.27 |
| ✓ | New-27 | 1.00 | 92.6 | 0.709 | 0.30 |
| ✓ | NGC6397 | 1.00 | 92.6 | 0.715 | 0.34 |
| ✓ | New-11 | 1.00 | 93.0 | 0.724 | 0.40 |
| ✓ | NGC2808 | 1.00 | 93.4 | 0.708 | 0.29 |
| ✓ | C-7 | 1.00 | 97.2 | 0.670 | 0.14 |
| ✓ | AAU-ATLAS | 1.00 | 105.9 | 0.694 | 0.22 |
| ✓ | New-17 | 1.00 | 107.9 | 0.692 | 0.21 |
| ✓ | New-7 | 1.00 | 109.7 | 0.690 | 0.21 |
| ✓ | New-6 | 1.00 | 110.8 | 0.686 | 0.19 |
| ✓ | TucanaIII | 1.00 | 113.5 | 0.686 | 0.19 |
| ✓ | New-10 | 1.00 | 115.6 | 0.685 | 0.19 |
| ✓ | C-20 | 1.00 | 119.0 | 0.684 | 0.18 |
| ✓ | Cetus | 30.62 | 127.0 | 0.674 | 0.15 |
| ✓ | NGC288 | 1.00 | 133.3 | 0.693 | 0.22 |
| ✓ | OmegaCen-Fimbulthul | 1.00 | 136.1 | 0.639 | 0.07 |
| ✓ | LMS-1 | 1.00 | 136.2 | 0.666 | 0.13 |
| ✓ | New-9 | 1.00 | 136.6 | 0.668 | 0.13 |
| ✓ | C-22 | 1.00 | 144.2 | 0.651 | 0.09 |
| ✓ | Slidr | 1.00 | 145.2 | 0.659 | 0.11 |
| ✓ | Elqui | 50.10 | 148.7 | 0.658 | 0.11 |
| ✓ | M30 | 1.00 | 152.5 | 0.642 | 0.08 |
| ✓ | Cetus-Palca | 33.39 | 156.2 | 0.652 | 0.10 |
| ✓ | Gaia-8 | 1.00 | 163.2 | 0.647 | 0.09 |
| ✓ | Leiptr | 1.00 | 166.9 | 0.644 | 0.08 |
| ✓ | New-12 | 1.00 | 168.0 | 0.617 | 0.05 |
| ✓ | C-8 | 3.44 | 175.9 | 0.640 | 0.07 |
| ✓ | Cetus-New | 18.47 | 179.8 | 0.637 | 0.07 |
| ✓ | New-14 | 1.00 | 190.1 | 0.631 | 0.06 |
| ✓ | Svol | 1.00 | 191.0 | 0.639 | 0.07 |
| ✓ | New-15 | 1.00 | 192.5 | 0.630 | 0.06 |
| ✓ | C-19 | 1.00 | 192.7 | 0.629 | 0.06 |
| ✓ | Phlegethon | 1.00 | 195.0 | 0.601 | 0.03 |
| ✓ | Gaia-1 | 1.00 | 207.0 | 0.623 | 0.05 |
| ✓ | M3-Svol | 10.75 | 211.3 | 0.613 | 0.04 |
| ✓ | Sylgr | 1.00 | 211.5 | 0.621 | 0.05 |
| ✓ | C-23 | 1.00 | 215.9 | 0.622 | 0.05 |
| ✓ | C-5 | 4.30 | 216.6 | 0.619 | 0.05 |
| ✓ | Jet | 30.71 | 231.5 | 0.612 | 0.04 |
| ✓ | Hrid | 1.00 | 234.5 | 0.609 | 0.04 |
| ✓ | New-16 | 1.00 | 238.6 | 0.601 | 0.03 |
| ✓ | M68 | 4.11 | 252.5 | 0.587 | 0.02 |
| ✓ | NGC3201-Gjoll | 1.00 | 256.5 | 0.598 | 0.03 |
| ✓ | Gaia-6 | 1.00 | 260.2 | 0.592 | 0.03 |
| ✓ | New-2 | 1.00 | 262.4 | 0.600 | 0.03 |
| ✓ | C-12 | 1.00 | 280.4 | 0.594 | 0.03 |
| ✓ | Ophiuchus | 1.00 | 292.6 | 0.596 | 0.03 |
| ✓ | New-3 | 1.00 | 294.4 | 0.589 | 0.02 |
| ✓ | Kshir | 1.00 | 294.4 | 0.597 | 0.03 |
| ✓ | 300S | 15.93 | 296.3 | 0.588 | 0.02 |
| ✓ | Gaia-10 | 1.00 | 300.3 | 0.587 | 0.02 |
| ✓ | Sagittarius | 28.82 | 307.2 | 0.585 | 0.02 |
| ✓ | New-8 | 1.00 | 315.6 | 0.582 | 0.02 |
| ✓ | C-4 | 3.55 | 316.4 | 0.582 | 0.02 |
| ✓ | Fimbulthul | 4.12 | 320.6 | 0.580 | 0.02 |
| ✓ | Ylgr | 1.00 | 326.8 | 0.579 | 0.02 |
| ✓ | New-5 | 1.00 | 348.8 | 0.580 | 0.02 |
| ✓ | NGC1851 | 1.00 | 349.7 | 0.581 | 0.02 |
| ✓ | NGC6101 | 1.00 | 363.2 | 0.569 | 0.02 |
| ✓ | Gaia-9 | 1.00 | 379.4 | 0.566 | 0.01 |
| ✓ | New-23 | 1.00 | 425.7 | 0.556 | 0.01 |
| ✓ | Gunnthra | 3.08 | 430.7 | 0.552 | 0.01 |
| ✓ | Spectre | 12.50 | 482.6 | 0.545 | 0.01 |
| ✓ | Jhelum-a | 13.00 | 503.6 | 0.540 | 0.01 |
| ✓ | Jhelum-b | 13.00 | 503.6 | 0.540 | 0.01 |
| ✓ | New-20 | 1.00 | 530.2 | 0.536 | 0.01 |
| ✓ | Gaia-12 | 1.00 | 557.8 | 0.584 | 0.02 |
| ✓ | Aquarius | 4.09 | 600.8 | 0.526 | 0.01 |
| ✗ | Alpheus | 1.80 | 0.0 | — (degenerate) | — |
| ✗ | Eridanus | 95.00 | 0.0 | — (degenerate) | — |
| ⚠ | Gaia-2 | 7.04 | 855.6 | — (outlier) | — |
| ✗ | Hermus | 19.65 | 0.0 | — (degenerate) | — |
| ✗ | Hyllus | 20.78 | 0.0 | — (degenerate) | — |
| ✗ | Molonglo | 20.00 | 0.0 | — (degenerate) | — |
| ✗ | Murrumbidgee | 20.00 | 0.0 | — (degenerate) | — |
| ⚠ | NGC2298 | 1.00 | 982.6 | — (outlier) | — |
| ✗ | NGC6362 | 7.65 | 0.0 | — (degenerate) | — |
| ⚠ | New-13 | 1.00 | 968.5 | — (outlier) | — |
| ⚠ | New-19 | 1.00 | 986.0 | — (outlier) | — |
| ⚠ | New-21 | 1.00 | 844.3 | — (outlier) | — |
| ✗ | Orinoco | 20.60 | 0.0 | — (degenerate) | — |
| ✗ | Pal15 | 38.40 | 0.0 | — (degenerate) | — |
| ✗ | Parallel | 14.27 | 0.0 | — (degenerate) | — |
| ✗ | Pegasus | 18.00 | 0.0 | — (degenerate) | — |
| ✗ | Perpendicular | 15.29 | 0.0 | — (degenerate) | — |
| ✗ | Tri-Pis | 26.00 | 0.0 | — (degenerate) | — |

## Degenerate streams (need pm/rv cross-match)

  Alpheus, Eridanus, Hermus, Hyllus
  Molonglo, Murrumbidgee, NGC6362, Orinoco
  Pal15, Parallel, Pegasus, Perpendicular
  Tri-Pis

## Outlier streams (v_3d > 700 km/s; needs manual review)

These streams have summary-level or track-level v_r data that is
either unphysical (placeholder values not equal to 1000 km/s) or wildly
inconsistent with bound MW dynamics. The T95.10 pipeline flags them but
does NOT include them in the joint fit. Manual review recommended before
trusting any σ/m prediction from these tracks.

  Gaia-2, NGC2298, New-13, New-19
  New-21

## What this does NOT do

- Synthesized boxes are 5× wide placeholders — they do not constrain the model.
- No published gap-count data has been added; that requires literature search.
- GD-1 interpretation problem remains formally separated.
- T90 master-branch merge criterion is unchanged.

## Next steps

1. Cross-match the degenerate streams against Gaia DR3 + APOGEE-2 + DESI for pm/rv.
2. Literature search for published gap counts on the OK streams (see T95.10 lit-search).
3. Replace synthesized constraints with literature-derived ones as found.
4. Re-run joint fit; if loglik changes materially, update T95 finding.
