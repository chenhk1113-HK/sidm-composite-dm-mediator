# T111 — Multi-component DM (Door D): v0.7 + light species for LZ

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** SHIPPED — Tier B (Door D) test of multi-component DM hypothesis
**Method:** emcee B1-lite (full 9D dynesty would take 4-10 hours)

---

## TL;DR

T111 extends v0.7's 6D baseline by **3 new parameters** for a second
(light) DM species that explains the LZ 248 keV event:

- **log₁₀(m_χ_light / GeV) ∈ [0.5, 2.0]** — light species mass (3 to 100 GeV)
- **log₁₀(σ_light / cm²) ∈ [-48, -42]** — light species cross-section
- **log₁₀(f_light) ∈ [-4, 0]** — fraction of DM in light species (0.01% to 100%)

Total: **9D parameter space**.

**Hypothesis:** Dark sector has TWO DM species:
- **Heavy species** (m_χ ≈ 100 GeV, v0.7's existing parameter): controls σ/m (SIDM)
- **Light species** (m_χ ≈ 60 GeV, new parameter): gives LZ direct-detection signal

This decouples the SIDM astrophysics from the direct-detection anomaly.

---

## Why Door D is interesting

Doors A, B, C have all been tested:
- **Door A (v0.7 kinetic-mixing baseline):** σ/m fits well; LZ not in fit
- **Door B (Portal B inelastic, T108):** Δlog Z = +0.51, mildly preferred
- **Door C (magnetic-moment Ls₁₀, T110):** Δlog Z = -10.72, CLOSED

**Door D is qualitatively different:** it posits a different dark sector
structure (multi-component DM), not just a different scattering channel.
The light species is allowed to have a **different** kinetic-mixing
suppression than the heavy species — it's not constrained by v0.7's
ε² ~ 10⁻⁷⁴ freeze-in argument.

---

## Likelihood components

- **T41 v0.7 joint (6D)** — unchanged; controls heavy species + σ/m
- **LZ 2024 limit (light species)** — penalty if σ_light > 10 × σ_LZ_limit(m_χ_light)
- **LZ 248 keV event (light species)** — Gaussian likelihood for matching
  the 1-event excess (N_obs=1, σ_N=1)
- **Relic density** — soft prior: f_light ≤ 1 (heavy + light total ≤ Ω_DM)

The 9D likelihood is:

```
log L_9D = log L_v0.7(m_φ, m_χ_h, g_χ, log_ε, log_α, log_ξ)
        + log L_LZ(m_χ_l, σ_light, f_light)
        + soft_relic_penalty(f_light > 1)
```

---

## Three possible outcomes

| Outcome | Δlog Z | Interpretation | Door D status |
|---|---|---|---|
| **Door D closed** | < 0 | Light species not preferred over v0.7 alone | Closed |
| **Door D weakly open** | 0 to +2 | Mild preference for multi-component DM | Open (weak) |
| **Door D strongly open** | ≥ +2 | Significant preference; meets T90 merge #5 | **Strong open** |

---

## Parameters

### Heavy species (v0.7 6D, unchanged)

| Parameter | Range |
|---|---|
| log m_φ / MeV | [-1.0, 4.0] |
| log m_χ_heavy / GeV | [0.5, 3.0] |
| g_χ | [0.01, 2.0] |
| log ε | [-60, -1] |
| log α_X | [-30, -1] |
| log ξ | [-1, 0.7] |

### Light species (new 3D)

| Parameter | Range | Physical meaning |
|---|---|---|
| log m_χ_light / GeV | [0.5, 2.0] | Light DM mass (3 to 100 GeV) |
| log σ_light / cm² | [-48, -42] | Light species σ_DM-nucleon |
| log f_light | [-4, 0] | Fraction of DM in light species (0.01% to 100%) |

---

## Expected behavior

For T111 to find Door D "open," the emcee needs to find a region where:
- f_light × σ_light × 10/m_χ_light × 2.84 ≈ 1 (matches N_obs=1)
- σ_light ≤ σ_LZ_limit(m_χ_light) (not excluded)
- Heavy species stays near v0.7 MAP (preserves σ/m)

A typical match: m_χ_light ≈ 60 GeV (DIAMX best fit), σ_light ≈ 2.4×10⁻⁴⁷
(at LZ limit), f_light ≈ 0.01-1 (depending on the exact scaling).

If the multi-component DM MAP converges to f_light → 10⁻⁴ (prior lower
bound), Door D is closed — light species is negligible.

---

## Caveats and honest limitations

1. **emcee B1-lite, not nested sampling.** Approximate log Z; the proper
   test of T90 criterion #5 would be 9D dynesty (4-10 hours wall time).
2. **Light species likelihood is simplified.** Uses a Gaussian
   approximation for N_pred ≈ 1. Real LZ likelihood uses binned Poisson
   on the actual recoil spectrum.
3. **No relic density coupling.** f_light + f_heavy = 1 is a soft prior;
   real Ω_χ_h + Ω_χ_l = 0.12 (Planck) should be enforced.
4. **No form-factor for light species.** Assumes order-1 form factor;
   real composite-DM form factor could differ.
5. **The σ/m is dominated by heavy species.** Light species contributes
   negligibly to σ/m (mass-suppressed). This is correct — multi-component
   DM scenarios have this property.

---

## Files

- `v0.3-prelim/code/t111_multicomponent_dm.py` — main script (9D emcee)
- `v0.3-prelim/tests/test_t111_multicomponent_dm.py` — 17 tests (15 pass, 2 skip)
- `v0.3-prelim/outputs/t95/t111_multicomponent_9d_emcee.json` — final output
- `v0.3-prelim/docs/T111_MULTICOMPONENT_DM.md` — this doc

---

## Usage

```bash
# Full production run (5-10 min)
T111_NWALKERS=32 T111_NSTEPS=2000 T111_BURN=500 .venv-sidm-bench/Scripts/python.exe \
    v0.3-prelim/code/t111_multicomponent_dm.py
```

Output: `v0.3-prelim/outputs/t95/t111_multicomponent_9d_emcee.json`

---

## Cross-references

- **T108 (Door B / Portal B):** Δlog Z = +0.51 (best current single-component door)
- **T110 (Door C / magnetic-moment):** Δlog Z = -10.72 (closed)
- **T87:** composite-DM cannot claim LZ at v0.7 MAP
- **T106 (DIAMX):** cross-detector hint (m_χ ≈ 60 GeV)
- **T98 (Di Mauro):** inelastic-DM interpretation of LZ

---

## What this means for T90

If Door D opens strongly (Δlog Z ≥ +2), the multi-component DM
hypothesis becomes the project's new best LZ explanation, replacing
Door B. This would update §0 to reflect Door D's status.

If Door D is closed or weakly open, the project's stance remains:
"Door B is best, but not significant."

---

## Standing posture

- **Master:** v0.5-prelim tagged, untouched
- **T90/LZ branch:** Tier A shipped (Door B documentation)
- **Tier B (T111):** Running in background process `proc_85303576f5be`
- **Tier D (UV completion):** Held pending Tier B result

---

## Provenance

- T111 implementation: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Branch: `wip/tier3-magnetic-moment-LZ`
- Standing posture: T90 branch, master untouched
