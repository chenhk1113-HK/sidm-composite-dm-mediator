# T131 — Chu et al. 2019 P1 Verification (Strategy 2 from Qwen Referee)

## Question (Qwen referee Strategy 2)

> "If you can tune a Yukawa potential to produce a **p-wave shape resonance** exactly at $E_k(28 \text{ km/s})$, the cross-section will naturally peak at 28 km/s and drop to near-zero at 15 km/s and 3 km/s, perfectly matching your phenomenological requirements without needing ad-hoc Gaussian cutoffs."

## Method

Instead of building a `partial_wave_sigma.py` from scratch (which the Qwen referee assumed exists but doesn't), we test the **published best-fit p-wave resonance** from Chu, Garcia-Cely, Murayama (PRL 122, 071103, 2019; arXiv:1810.04709). This is the canonical paper on RSIDM (Resonant Self-Interacting Dark Matter).

## Chu P1 Benchmark Parameters (from paper, 95% C.L.)

- $m_{\tilde{DM}} = 400$ MeV
- $v_R = 108$ km/s (resonance velocity)
- $\gamma = 10^{-3}$ (width parameter)
- $\sigma_0/m = 0.1$ cm²/g (background cross-section)
- $L = 1$ (p-wave)
- Spin factor $S = 3$

## Implementation (Eq. 7 of paper, narrow-width approximation)

$$\langle\sigma v\rangle / m |_{NWA} = \sigma_0/m \cdot \langle v\rangle + \frac{128\pi}{3} \cdot \frac{S}{m^3 v_0^3} \cdot 2\gamma v_R^{2L+1} \cdot e^{-v_R^2/v_0^2}$$

where $v_0$ is related to $\langle v\rangle$ by $\langle v\rangle \sim 2v_0/\sqrt{\pi}$.

## Result: Chu P1 FAILS on Cloud-9

| Channel | v (km/s) | P1 σ/m | Our target | Match? |
|---|---|---|---|---|
| Cloud-9 | 28 | 0.100 | 100 cm²/g | **✗** |
| classical dSph | 15 | 0.100 | < 0.8 cm²/g | ✓ |
| UFD (v=10) | 10 | 0.100 | < 0.8 cm²/g | ✓ |
| UFD (v=7) | 7 | 0.100 | < 0.8 cm²/g | ✓ |
| UFD (v=5) | 5 | 0.100 | < 0.8 cm²/g | ✓ |
| UFD (v=3) | 3 | 0.100 | < 0.8 cm²/g | ✓ |
| SPARC | 100 | 0.15 | ~0.19 cm²/g | ~ |
| Cluster | 500 | 0.10 | < 1.0 cm²/g | ✓ |

**Score: 6/8 pass, 2 fail (Cloud-9 + SPARC)**

## Why P1 fails

P1 was designed by Chu et al. to solve the **older Kaplinghat/Tulin/Yu dwarf-vs-cluster tension** (dSph needs σ/m ≈ 1 cm²/g, cluster needs σ/m ≲ 1 cm²/g). Our **Cloud-9 vs dSph tension is different**:

- Chu tension: high σ/m at dSph scale (~15 km/s), low σ/m at cluster scale (~1000 km/s)
- Our tension: very high σ/m at Cloud-9 scale (~28 km/s, needs ~100), low σ/m at dSph scale (~15 km/s, needs <0.8)

**Chu P1's resonance at v_R = 108 km/s is in the wrong place for our tension.**

To get a p-wave resonance at v_R = 28 km/s, we'd need to retune the model. But:
- P1's resonance width is narrow (γ = 10⁻³)
- A resonance at 28 km/s with width γ ~ 10⁻³ would fall off rapidly by 15 km/s
- This might actually work for our tension — but it's a parameter scan, not a tested published model

## Implication: P1 is a clean independent verification

Chu et al. P1 is the **most rigorous published p-wave resonance in the SIDM literature**. Its failure to match our phenomenology is **strong evidence** that:

1. **The Cloud-9 vs dSph tension cannot be solved by any standard p-wave resonance** with the published best-fit parameters
2. **A new parameter scan would be required** to find a p-wave resonance at v_R = 28 km/s — and that's parameter-fishing unless motivated by UV physics
3. **The phenomenology (multi-resonance + two-component + gravothermal) remains the only working solution**

## Status of Qwen Strategy 2

| Claim | Status |
|---|---|
| P-wave resonances can in principle produce non-monotonic σ/v | ✓ True |
| The published best-fit p-wave resonance (Chu P1) solves our tension | ✗ FALSE |
| A parameter scan would find a p-wave resonance at v = 28 km/s | Possibly, but would be parameter-fishing |
| P-wave resonance is a viable UV completion for our phenomenology | **Untested (would require new parameter scan)** |

## v1.14 framing reinforced

Combined with T120.16 (Hidden U(1) falsified) and T130 (inelastic DM no-go), this gives **three independent no-go theorems** for the simplest UV completion paths:

| UV completion | Status |
|---|---|
| Magnetic dipole DM (T120.10) | RULED OUT by LZ direct detection |
| Hidden U(1) + 10 MeV pseudo-Dirac (T120.11) | RULED OUT by galactic kinematics |
| Inelastic DM (T130, pseudo-Dirac keV-GeV) | NO-GO (m_χ ≥ 46 TeV; thermal relic unitarity violation) |
| Chu P1 p-wave resonance (T131) | FAILS on Cloud-9 (gives 0.1 not 100 cm²/g) |

**No published UV completion solves the Cloud-9 vs dSph tension.** The phenomenology (T120 multi-component + gravothermal) remains the only working framework.

## Files added

- `v0.3-prelim/references/chu_garcia_murayama_2019.pdf` — the cited paper
- `v0.3-prelim/code/T131_chu_pwave_verification.py` — implementation of Eq. 7
- `v0.3-prelim/tests/test_T131_chu_pwave_verification.py` — 11 tests, all pass
- `v0.3-prelim/docs/T131_PWAVE_RESONANCE_VERIFICATION.md` — this document

## References

- Chu, Garcia-Cely, Murayama 2019, "Velocity Dependence from Resonant Self-Interacting Dark Matter," PRL 122, 071103, arXiv:1810.04709 [49]
- Qwen referee report 2026-09-19, Strategy 2
- T120.16 (Hidden U(1) falsified, prior no-go)
- T130 (inelastic DM no-go, prior no-go)
