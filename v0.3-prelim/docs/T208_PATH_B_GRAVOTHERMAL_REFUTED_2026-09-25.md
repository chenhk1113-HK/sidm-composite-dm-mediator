# T208 Path B — Gravothermal at Cloud-9 Host-Halo Mass Scale

**Date:** 2026-09-25
**Purpose:** Test whether gravothermal core-collapse at the Cloud-9 host-halo mass scale (M_200 = 5×10⁹ M_☉) can produce a σ/m(v=28 km/s) enhancement that satisfies the Cloud-9 floor (≥50 cm²/g) without violating the dSph ceiling (≤0.8 cm²/g at v=15 km/s).

**Method:** Balberg+ 2002 Eq. 22 (PRL 88, 101301) gravothermal t_core normalization, same as T204. Computes t_core(t_halo, c, σ/m, v_max) at Cloud-9 host-halo parameters and checks if t_core ≤ t_Hubble.

**Code:** `v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py` (110 lines, pure analytical).
**Result:** `v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json`.

## Results

### Cloud-9 host-halo parameters (cosmological NFW)
- M_halo = 5×10⁹ M_☉
- concentration c = 12
- r_vir ≈ 35.1 kpc (cosmological, 200 ρ_crit)
- r_s ≈ 2.92 kpc
- V_max ≈ 24.75 km/s
- ρ_s ≈ 9.69×10⁻³ M_☉/pc³

### σ/m at the Cloud-9 host-halo scale (Phase 44 baseline, a_slope = 1.0)
- σ/m(v=28, Cloud-9) = 0.186 cm²/g — **270× below the 50 cm²/g floor**
- σ/m(v=15, dSph) = 0.347 cm²/g — at the dSph ceiling

### Gravothermal at Cloud-9 host-halo (Phase 44 σ/m)
- **t_core = 73.7 Gyr** (using virial σ/m = 0.21 cm²/g)
- **t_Hubble = 13.8 Gyr**
- **t_core / t_Hubble = 5.3** — gravothermal phase DOES NOT run
- Causality OK: t_core / t_cross = 638 (well above 3.0 cap)

### σ/m required for gravothermal to run at Cloud-9 host halo
- σ/m ≥ **1.12 cm²/g** (virial) for t_core = Hubble
- Phase 44 needs **21.6× enhancement** to even start gravothermal

### Even if gravothermal ran: enhancement insufficient
- A 100× core-enhancement (typical for deep core-collapse) gives σ_eff(v=28) = 18.6 cm²/g
- Cloud-9 needs ≥ 50 cm²/g — **2.7× short even with deep core enhancement**

### σ/m violation of dSph at Yang+ 2025 high-σ regime
- At σ/m = 147 cm²/g (Yang+ 2025 high-σ): t_core = 105 Myr (runs fast)
- σ_eff(v=28) = 525 cm²/g (Cloud-9 PASSES — 10× above floor)
- σ_eff(v=15) = 980 cm²/g (dSph **VIOLATED by 1225×**)
- Cloud-9 vs dSph tension is STRUCTURAL, not gravothermal

## Verdict

**Path 2 (gravothermal unification) is REFUTED at Phase 44 σ/m.** The gravothermal phase does not run at the Cloud-9 host-halo mass scale (t_core = 73.7 Gyr ≫ t_Hubble = 13.8 Gyr). Furthermore, **no σ/m value resolves Cloud-9 vs dSph via gravothermal at this mass scale** — the tension is structural, not a missing gravothermal phase.

This **closes Path 2** as a route to unified-model status. The Cloud-9 spike (σ/m ≥ 50 cm²/g at v=28 km/s) and the dSph ceiling (≤ 0.8 cm²/g at v=15 km/s) cannot be reconciled by gravothermal enhancement at the host-halo mass scale.

## Implications for the paper

The Cloud-9 vs dSph tension remains **unresolved**. Per the Confirmed_v18 reviewer's note: this is the load-bearing structural issue. The paper's honest framing is preserved:
- Path F1 (T207, v18.38) fixes the SPARC structural limitation (heavy-channel-only σ_eff)
- Path 2 (T208, this report) refutes gravothermal as a Cloud-9 vs dSph resolution
- The Cloud-9 4000× spike is NOT derived from first principles
- The model remains a constraint map, not a unified derivation

## What does NOT change

- Standing paper verdict (6-7 of 8 channels, five no-go theorems) preserved
- Path F1 verdict split (borrowed RESOLVED, yang MARGINAL, t202 NOT RESOLVED, priored free fit CLEAR FAIL) preserved
- T204 substructure result at 10⁶ M☉ scale (Yu+ 2026 mechanism confirmed for SUBHALOS) preserved — gravothermal DOES run at subhalo scale, just not at host-halo scale
- §3.3b Yu+ 2026 PRL 136, 141001 stellar streams and stellar halo substructure preserved

## Next steps

Path 4 (first-principles f_H from KiSS-SIDM DSMC N-body) is still in progress per user directive "strategic budget, whatever it takes." Even though Path 2 is refuted, Path 4 produces a standalone first-principles anchor for f_H that removes the Yang+ 2025 Fig. 2 dependency. The result will be reported in v18.39 regardless of whether it unifies the model.

## Honest framing

This is a **negative result** — Path 2 (gravothermal unification) is refuted. Negative results are still publishable findings: the paper can state explicitly that gravothermal enhancement at the Cloud-9 host-halo mass scale is **insufficient to resolve the Cloud-9 vs dSph tension**, regardless of σ/m. This is stronger science than claiming a positive result that doesn't hold.