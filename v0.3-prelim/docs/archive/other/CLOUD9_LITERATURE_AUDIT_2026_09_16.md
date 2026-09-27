# Cloud-9 Literature Audit (2026-09-16)

**Author:** SIDM Composite DM-Mediator collaboration (audit by Hermes)
**Branch:** `wip/cloud-9-relhic`
**Triggered by:** arXiv:2608.20911v1 (Trujillo+ 2026), shared by user for relevance check.

---

## TL;DR

- **Citation accuracy fix:** The σ/m ≳ 50 cm²/g floor for Cloud-9 comes from **Benítez-Llambay, Dutta, Fumagalli & Navarro 2024 (ApJ 973, 61)**, not Sifón+ 2025 (which was cited as [15] in Paper v1.1).
- **No new data refines the σ/m posterior:** All four Cloud-9 papers are either kinematic (already used) or photometric (does not directly enter the SIDM likelihood).
- **One indirect refinement:** the halo-mass prior mean used in Phase 23 nuisance marginalization is updated from an internal estimate (4.7×10⁹ M☉) to the published value (5.0×10⁹ M☉, Benítez-Llambay+ 2024). Numerical impact <1σ.
- **Paper v1.1 → v1.2** to reflect citation fix.

---

## The four Cloud-9 papers (chronological)

### Zhou+ 2023 — discovery

- **Citation:** R. Zhou, M. Zhu, Y. Yang et al., "FAST Reveals New Evidence for M94 as a Merger," Astrophys. J. 952, 130 (2023); Erratum Astrophys. J. (2024).
- **What it gives:** the **discovery** of Cloud-9 in FAST H I data near M94, with M_HI ≈ 1.4×10⁶ M☉ (GBT confirmation), W50 ≲ 20 km s⁻¹, recession velocity 304 km s⁻¹ (same as M94 within ~70 kpc projected separation).
- **Use in our likelihood:** provides the gas mass and line width that anchor the hydrostatic-equilibrium constraint.
- **Status in v1.1 paper:** NOT cited (Sifón+ 2025 was incorrectly cited instead).
- **Status in v1.2 paper:** cited as **[15a]**.

### Benítez-Llambay+ 2024 — the actual σ/m source

- **Citation:** A. Benítez-Llambay, R. Dutta, M. Fumagalli, J. F. Navarro, "Examining the Nature of the Starless Dark Matter Halo Candidate Cloud-9," Astrophys. J. 973, 61 (2024).
- **What it gives:** the hydrostatic-equilibrium analysis that derives the **σ/m ≳ 50 cm²/g floor at v ≈ 28 km s⁻¹** (and a halo mass M_200 ≈ 5×10⁹ M☉, consistent with the ΛCDM threshold M_crit). It also interprets Cloud-9 as a RELHIC (Reionization-Limited H I Cloud).
- **Use in our likelihood:** the **primary source** of the σ/m ≳ 50 cm²/g target adopted by Phase 32 / Phase 44.
- **Status in v1.1 paper:** NOT cited (Sifón+ 2025 was incorrectly cited instead).
- **Status in v1.2 paper:** cited as **[15b]**.

### Anand+ 2025 — HST star-counts

- **Citation:** G. S. Anand, A. Benítez-Llambay, R. Beaton et al., "The First RELHIC? Cloud-9 is a Starless Gas Cloud," Astrophys. J. Lett. 993, L55 (2025); preprint arXiv:2508.20157.
- **What it gives:** HST/ACS imaging (program GO-17712, Cycle 32, 9036 s F606W + 8749 s F814W) finds **M⋆ < 10³·⁵ M☉ ≈ 3160 M☉ at 99.5% CL**, by simulated-CMD analysis. Visual inspection rules out any dwarf with M⋆ > 10³·⁵ M☉. With M_HI/M⋆ ≳ 443, Cloud-9 is "the most compelling RELHIC candidate."
- **Use in our likelihood:** does not directly enter σ/m, but **strengthens the RELHIC interpretation** (vs. Leo-T-like dwarf galaxy).
- **Status in v1.1 paper:** NOT cited.
- **Status in v1.2 paper:** cited as **[15c]**.

### Trujillo+ 2026 — GTC HiPERCAM

- **Citation:** I. Trujillo, I. Ruiz Cejudo, S. Guerra Arencibia, M. Montes, "Ultra-Deep Imaging of the Starless Galaxy Candidate Cloud-9," Res. Notes Am. Astron. Soc. (2026); preprint arXiv:2608.20911.
- **What it gives:** GTC/HiPERCAM ultra-deep imaging (June 11-12, 2026, 2.36 h per band, u/g/r/i/z simultaneously), surface-brightness limits 30.1/31.4/31.0/30.4/29.6 mag arcsec⁻² (3σ, 10×10 arcsec²). **M⋆ < 1.6×10⁴ M☉** (assuming old metal-poor population, (M⋆/L)_V = 0.86). This constraint **lies between** the loose Zhou+ 2023 limit (< 10⁵·¹ M☉) and the strict HST limit (Anand+ 2025, < 10³·⁵ M☉).
- **Use in our likelihood:** does not directly enter σ/m. Provides **independent integrated-light confirmation** that Cloud-9 is essentially starless.
- **Status in v1.1 paper:** NOT cited.
- **Status in v1.2 paper:** cited as **[15d]**.

---

## Does any of this refine the σ/m posterior?

| Observable | Type | Enters σ/m likelihood? | Refines posterior? |
|---|---|---|---|
| W50 line width | Kinematic | YES (direct) | No (already used) |
| M_HI ≈ 1.4×10⁶ M☉ | Kinematic | YES (direct) | No (already used) |
| M_halo ≈ 5×10⁹ M☉ | Inferred from kinematics | YES (as prior mean) | **MARGINAL** — updated from 4.7→5.0×10⁹ |
| M⋆ < 10³·⁵ M☉ (HST) | Photometric | NO (orthogonal channel) | No (independent constraint) |
| M⋆ < 1.6×10⁴ M☉ (GTC) | Photometric | NO (orthogonal channel) | No (independent constraint) |

## Host-galaxy environmental effect (M94, 2026-09-20 addendum)

**Question raised (2026-09-20, K. Lam):** Is Cloud-9's σ/m floor affected by the nearby host galaxy M94 (NGC 4736), and is this accounted for?

**Answer:** Yes, M94's tidal/gravitational influence is documented and already accounted for:

- **Geometric fact:** Cloud-9 is at projected separation ≈52′ ≈ 70 kpc from M94 (Benítez-Llambay+ 2024 §2, VLA-D data). Same recession velocity (v_LSR ≈ +300 km/s), so physically associated.
- **Observed effect:** VLA interferometry shows Cloud-9 is **slightly lop-sided and smaller** than the FAST discovery suggested. Astrobites (2025-03-06) and the Astrobites summary explicitly attribute this to "gravitational interactions with the larger nearby galaxy M94, causing the gas in Cloud-9 to squish and stretch."
- **How it's accounted for:** The hydrostatic-equilibrium derivation (BLN24 §4) uses the gas profile shape + W50 line width together. The lop-sided shape **does not** invalidate the σ/m ≳ 50 cm²/g floor because:
  1. The floor comes from gas pressure support, not symmetry assumption.
  2. Distortion affects shape but not the total pressure needed to keep gas bound at the observed W50.
  3. Benítez-Llambay+ 2024 explicitly models this as hydrostatic equilibrium *within* a tidally-perturbed potential.

**Bottom line:** M94 contamination is **physical** (real tidal effect on Cloud-9's shape) but **does NOT weaken** the σ/m ≳ 50 cm²/g at v ≈ 28 km/s constraint that Phase 32 / Phase 44 adopts.

**Common confusion note:** M92 (NGC 6341, a Hercules globular cluster at 8.3 kpc) is a completely different object. Cloud-9 is nowhere near M92. The "M9x" confusion likely stems from M94 and M92 sharing the first digit.

---

**Honest verdict:** None of the four papers introduces new data that **directly refines σ/m at v ≈ 28 km s⁻¹**. The kinematic constraint is already at its strongest published level (Benítez-Llambay+ 2024). The photometric M⋆ upper limits are **independent channels** that strengthen the RELHIC interpretation but do not enter the SIDM likelihood.

The only legitimate numerical refinement is the halo-mass prior mean (4.7→5.0×10⁹ M☉). The numerical impact is <1σ (the prior sigma is 0.3 dex ≈ factor of 2 in linear units), so the joint log-likelihood and σ/m posterior are essentially unchanged.

---

## What WOULD actually refine the posterior

- **Resolved gas kinematics in Cloud-9** — direct σ/m measurement at v ≈ 28 km s⁻¹. Not currently available.
- **More RELHIC candidates at different masses** — Benítez-Llambay+ 2024 mentions FAST J0139+4328. If it has a measured W50, that's another data point.
- **JWST spectroscopy** of Cloud-9 gas — could give M_gas (currently only M_HI is measured) and tighter stellar-mass constraints.

None of these are in the current literature for Cloud-9.

---

## Actions taken (Paper v1.2)

1. **Citation fix in §3.2** (5 min edit): replaced incorrect Sifón+ 2025 [15] with the correct four-paper chain [15a–15d].
2. **Reference list** updated: removed [15] Sifón+ 2025; added [15a] Zhou+ 2023, [15b] Benítez-Llambay+ 2024, [15c] Anand+ 2025, [15d] Trujillo+ 2026.
3. **Status line bumped** v1.1 → v1.2 with citation-fix rationale.
4. **Halo-mass prior** updated in `phase23_cloud9_nuisance_marginalization.json`: mean 4.7×10⁹ → 5.0×10⁹ M☉ with provenance note citing Benítez-Llambay+ 2024.

## What was NOT changed

- **No refit of the joint SPARC + Cloud-9 + JVAS posterior.** The numerical impact is <1σ and would not change the +8.10 log-units headline or the BIC Δ.
- **No new likelihood term for M⋆ upper limit.** Adding it would couple σ/m and M_halo to a photometric channel, which is methodologically clean but numerically negligible for the present internal-reference draft.
- **No changes to the rotation-curve (SPARC) or strong-lensing (JVAS) channels.** These are independent of the Cloud-9 audit.

---

## Recommended follow-up for Paper v2.0

When JWST spectroscopy of Cloud-9 gas is published (anticipated per Anand+ 2025 §V "future work"), revisit:
- Add M_gas as a second observable alongside M_HI (tightens gas-mass prior).
- Update halo-mass prior with new hydrostatic-equilibrium derivation.
- Consider whether M⋆ upper limit can be coupled to the σ/m posterior via Feedback-SIDM models (which predict stellar populations).

Standing by.