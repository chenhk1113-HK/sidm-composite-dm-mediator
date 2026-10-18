# v40.26: Data-Driven Parameter Scan (2D Background)

**Date:** 2026-10-17
**Commit:** (pending)
**Status:** 2D scan complete; 3D scan planned for v40.27
**Goal:** Find parameter configuration that maximizes channels satisfied

## Method

Scanned (A_SLOPE, σ_0) in 2D, with single Cloud-9 resonance fixed at v=29.4 km/s (σ_peak=174, σ_1=4.4). 16 observational channels checked per configuration.

## Channel set (16 channels from v19.2-F PAPER V1 DRAFT + Horigome+ 2025)

| Channel | v (km/s) | σ/m range | Source |
|---|---|---|---|
| Cloud-9 (resonance peak) | 29.4 | 87-348 | v40.24 canonical |
| Cloud-9 (kinematic) | 28.0 | 87-348 | v40.24 canonical |
| Horigome+ 2025 dSph (v=10) | 10.0 | <0.8 | arXiv:2503.13650 (w=10) |
| Horigome+ 2025 dSph (v=15) | 15.0 | <0.8 | arXiv:2503.13650 (w=10) |
| Horigome+ 2025 dSph (v=20) | 20.0 | <0.8 | arXiv:2503.13650 (w=10) |
| Andrade+ 2022 (cluster) | 1458 | <0.13 | MNRAS 510, 54 |
| O'Donnell+ 2025 | 2090 | <0.613 | arXiv:2508.20179 |
| Jee, Park, Lee 2026 | 1500 | <0.22 | arXiv:2605.00093 |
| Gilman+ 2023 | 1000 | <0.5 | arXiv:2207.13111 |
| SPARC | 100 | 0.03-0.5 | Elbert+ 2015 |
| Stellar streams | 300 | 0.05-1.0 | Stream constraints |
| Bullet Cluster | 3000 | <0.1 | Bullet shock |
| UFD cores (observational) | 15 | <0.5 | Sánchez Almeida+ 2025 |
| Extreme UFD | 5 | <5 | Loose bound |
| Lyman-α forest | 50 | 0.005-0.5 | Rough bound |
| v=500 (intermediate) | 500 | 0.001-0.1 | Intermediate scale |

## Results

### Baseline (v40.24: A_SLOPE=1.93, σ_0=0.052)
**Pass: 10/16**
- **6 failures:** Horigome v=10, 15, 20; UFD cores v=15; Lyman-α (low); Stellar streams (low); Extreme UFD (above)

### Top 2D configuration: A_SLOPE=0.500, σ_0=0.090
**Pass: 13/16**
- **3 failures:** Horigome v=15 (1.05 vs 0.8), Horigome v=20 (17.96 vs 0.8), UFD cores v=15 (1.05 vs 0.5)
- **Improvement:** +3 channels (resolves Horigome v=10, Extreme UFD, Lyman-α)
- **New issue:** Stellar streams just at boundary (0.052 vs 0.05 min)

### Top 10 configurations
All top 10 have A_SLOPE=0.500 (lowest in scan range), σ_0 in [0.09, 0.15]. All pass 13/16 channels with same 3 failures.

The v=15 and v=20 failures are due to the **resonance tail** (174 × exp(-2.4) = 15.3 at v=20), not the background. The 2D scan cannot fix this without changing σ_1 (resonance width).

## Conclusion

The 2D scan reveals:
- The dSph tension at v=10 is **resolvable** by lowering A_SLOPE
- The dSph tension at v=15, v=20 is **NOT resolvable** with 2D (background only)
- The resonance tail at v=20 requires a **3D scan** including σ_1

**v40.27 plan:** 3D scan over (A_SLOPE, σ_0, σ_1) to test if narrower resonance can resolve v=20 tension.

## What "data-driven" reveals

The data is telling us:
- The dSph Horigome constraint requires a very flat background (A_SLOPE ≈ 0.5)
- This is at odds with the Born-Yukawa UV prediction (A_SLOPE ~ -2 to -4) and the Phase 44 fit (A_SLOPE = 1.93)
- The v40.24 best-fit (Phase 44) is a **local optimum** that misses the global picture

**Honest interpretation:** The v19.2-F velocity-dependent background (A_SLOPE = 1.93) is a **fit to observational channels OTHER than dSph**, but it doesn't satisfy the dSph Horigome constraint. A data-driven approach reveals this tension.

## Action items

1. Run 3D scan (A_SLOPE, σ_0, σ_1) — v40.27
2. If 3D scan finds a winning configuration, document the parameters
3. If not, explore multi-resonance (Tsai 2022 framework) as a third option
4. Update PAPER V1 DRAFT with the data-driven findings
5. Document the **fundamental trade-off** between Cloud-9 anchor and dSph Horigome
