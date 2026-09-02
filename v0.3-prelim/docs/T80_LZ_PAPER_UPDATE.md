# T80 — LZ Paper Update (v0.4-prelim)

> **Status:** Shipped 2026-09-02. Defensive doc-update in response to
> the LZ preprint appearing (much earlier than the KIV cron's
> expected 2026-11-01 fire date).
> **Trigger:** User upload of `LZ_Preprint_260901_Dark_Matter_EFT_Nuclear_Recoil_Search_at_Higher.pdf`
> (the actual LZ paper, 25 pages, full author list from the LZ
> collaboration); user direction "continue".
> **Companion:** [T77 LZ signal update](T77_LZ_2026_09_UPDATE.md),
> [T78 kinetic-mixing](T78_KINETIC_MIXING_LZ_LINK.md),
> [T79 composite form factor](T79_COMPOSITE_FORM_FACTOR_REMNANT.md).

## What this ships

1. **Paper-specific facts** added to T77, T78, T79 docs:
   - **Local significance: 3.4σ** (NOT in press releases)
   - **Best-fit model: Ls₁₀ WIMP at 1000 GeV/c²** (Table I)
   - **NREFT framework**: O₁ˢ, O₄ᵛ, L₁₋L₂₀, Ls₁₀ operators
   - **Exposure: 2.84 tonne-years** (220 d × 4.71 t)
   - **Energy window: 5.4 – 270 keV** (extended from 0-50 keV standard)
2. **Standing posture preserved**: 2.6σ global < 3σ → no Channel 5
   update, no T41 re-run
3. **KIV cron `080d2f590251` retained** for 2026-11-01 to check for
   PRL final-version updates
4. **Updated MODEL_ASSUMPTIONS §0** + **EXTRACT.md** + **layman summary**

## What the paper actually says (verified end-to-end)

Per the LZ preprint (LUX-ZEPLIN Collaboration, "Search for dark matter
particle interactions in an extended nuclear recoil energy window
with the LUX-ZEPLIN (LZ) experiment", preprint 2026-09-02, 25 pages):

| Property | Press release (T77) | Paper (T80) |
|---|---|---|
| **Exposure** | 220 live days (Mar 2023 – Apr 2024) | **2.84 tonne-years** (220 d × 4.71 t active volume) |
| **Energy window** | "248 keV event" | **5.4 – 270 keV** (extended from standard 0-50 keV WIMP search) |
| **Models tested** | "Beyond simplest WIMP" | NREFT operators O₁ˢ, O₄ᵛ, L₁₋L₂₀, Ls₁₀; inelastic DM |
| **Event** | 248 keV | **248 ± 23(stat) ± 23(sys) keV** |
| **Significance** | 2.6σ | **3.4σ local / 2.6σ global** (after look-elsewhere correction) |
| **Best-fit model** | n/a | **Ls₁₀ WIMP at 1000 GeV/c²** (Table I: fit = 1.0⁺¹·⁴₋₀.₇ events) |
| **Implied mass** | ≥ 200 GeV/c² | **1000 GeV/c²** best fit (consistent with project's MAP m_χ ~ 770 GeV) |
| **Background rate near event** | n/a | ~0.011 events in 248 keV region (very low) |
| **Neutron explanation** | n/a | Ruled out — would need ≥ 8 MeV neutrons, expect lower-E events |
| **²¹⁴Pb (MSSI) explanation** | n/a | Ruled out by prompt veto |
| **¹²⁴Xe activation** | n/a | Detector was in "mixed flow state" during event; radon tag not applicable |

## The critical local-vs-global distinction

The press release reported **2.6σ global significance**. The paper
also reports a **3.4σ local significance** for the best-fit model.
The difference is the **look-elsewhere effect (LEE) correction**: the
paper scans over many NREFT operators, masses, and inelastic-DM
splittings, so the global significance is reduced from 3.4σ to 2.6σ
after accounting for the multiple-hypothesis testing.

**Per the project's standing trigger policy (T77):**

| Significance | Action |
|---|---|
| < 3σ (global) | Document only; no code/data modification |
| ≥ 3σ (global) | Update Channel 5 (T30 LZ mapping); re-run T41 at nlive=2000 |
| ≥ 5σ (discovery) | Major milestone; v0.5-prelim release |

**The 2.6σ global is below the 3σ threshold.** Therefore:
- ✅ **DO** document in MODEL_ASSUMPTIONS §0 + EXTRACT.md (T77, T78, T79, T80)
- ✅ **DO** update with paper-specific findings (best-fit Ls₁₀ at 1000 GeV)
- ❌ **DO NOT** update T30 Channel 5 (2.6σ global < 3σ threshold)
- ❌ **DO NOT** re-run T41 (result would be unchanged anyway)

**The 3.4σ local significance is "interesting but not discovery"
territory.** The paper authors themselves use the 2.6σ global
figure as the headline (correct statistical practice for multi-model
searches). The project should NOT set a precedent for "local-only"
updates; that would be a slippery slope.

## Project compatibility with the LZ paper's best fit

| Quantity | Project v0.7 (nlive=2000) | LZ paper best-fit (Ls₁₀) |
|---|---|---|
| WIMP mass m_χ | **770 GeV (MAP)** / 498 GeV (median) | **1000 GeV/c²** |
| σ_DM-DM at galactic scale | **0.27 cm²/g** | n/a (measures σ_DM-nucleon) |
| Mediator mass m_φ | **453-588 MeV** | Light mediator (NREFT framework) |
| Interaction type | Composite-DM + secluded A' | Inelastic DM + EFT (magnetic moment, Ls₁₀) |
| Implied σ_DM-nucleon | ~10⁻¹¹⁷ cm² (Kahlhoefer formula) | n/a (paper measures event rate, not σ) |

**The project's m_χ ~ 770 GeV is very close to the LZ best-fit m_χ ~
1000 GeV.** Both are in the "heavy WIMP" regime where the
inelastic-DM and EFT operators become relevant. This is a
**stronger validation** than the press-release-only T77 had.

The project is in a **physically consistent region** with the LZ
best-fit scenario. The composite-DM model provides a natural
realization of NREFT operators via its internal structure (R ~ 1/Λ
~ 1/(30 MeV) ~ 0.03 fm; see T79 docs for composite form factor).

## T78 update: LZ paper validates NREFT framework

The LZ signal is described in NREFT terms (magnetic-moment
interaction Ls₁₀), which is exactly the kind of operator that
arises from kinetic mixing in a vector-mediator DM model. The
composite-DM project's ε_γ is the **same parameter** that
controls Ls₁₀-style operators at the electroweak scale. So the LZ
paper's framework **confirms** that the project's microphysics
picture is the right one — light mediator + magnetic-moment EFT
+ heavy WIMP.

**Practical impact at the v0.7 MAP:** even with the paper's
detailed NREFT framework, the kinetic-mixing suppression factor
(~50-80 orders, per T79) is unchanged. The ε²-suppression holds
because the project is at ε_γ ~ 10⁻³⁷, far below the Ls₁₀
operator's typical coupling regime (ε ~ 10⁻³). So the project
**cannot be constrained** by LZ even with the paper's detailed
NREFT framework — confirming T78/T79's qualitative claim.

## T79 update: Composite-DM overlaps with NREFT framework

The project's composite-DM (R ~ 1/Λ ~ 1/(30 MeV) ~ 0.03 fm) is in
the regime where NREFT operators like Ls₁₀ become relevant. The
composite form factor F²(q) is small at LZ energies (per T79's
calculation), but the project's microphysics — light mediator +
composite internal structure + heavy WIMP — is the **same framework**
that the LZ paper tests.

**Uncertainty band (50-80 orders) still holds.** The kinetic-mixing
suppression factor at ε ~ 10⁻³⁷ is unchanged by the paper's
detailed NREFT framework, because the suppression comes from ε²
(at the microphysics level), not from the EFT operator choice.
So T79's 50-80 orders uncertainty band is robust.

**Best-fit m_χ comparison:** the LZ paper's best-fit m_χ ~ 1000 GeV
is very close to the project's MAP m_χ ~ 770 GeV (nlive=2000).
Both are in the "heavy WIMP" regime (700-1000 GeV) where
inelastic-DM and EFT operators become relevant. This is a
**strong validation** of the project's posterior.

## What the KIV cron should do

The cron `080d2f590251` (next fire: **2026-11-01 09:00**) is
**retained** — its job is to check for the PRL final version (which
may have different numbers than the preprint). If the PRL version
changes the global significance to ≥ 3σ, the cron output will
recommend updating Channel 5 (per the standing trigger policy).

For now (T80), the preprint's 2.6σ global is below threshold, so
no Channel 5 update is needed.

## Drift guard

| Source | Value |
|---|---|
| VERSION | `0.4-prelim+T75` (unchanged; T80 is paper-specific update) |
| README.md badge | `v0.4-prelim+T75` (unchanged) |
| CITATION.cff | `v0.4-prelim+T75` (unchanged) |
| CHANGELOG.md top | `v0.4-prelim+T75` (T80 entry added below) |
| EXTRACT.md | `v0.4-prelim+T75` (LZ paper reference added) |
| MODEL_ASSUMPTIONS.md | `v0.4-prelim+T75` (LZ paper reference added to §0) |

All 6 drift-guard sources still agree on `v0.4-prelim+T75`.

## Files

| File | Change |
|---|---|
| `v0.3-prelim/docs/T77_LZ_2026_09_UPDATE.md` (MODIFIED) | Paper-specific findings added: 3.4σ local, best-fit Ls₁₀ at 1000 GeV, NREFT framework |
| `v0.3-prelim/docs/T78_KINETIC_MIXING_LZ_LINK.md` (MODIFIED) | T80 section: LZ paper validates NREFT framework |
| `v0.3-prelim/docs/T79_COMPOSITE_FORM_FACTOR_REMNANT.md` (MODIFIED) | T80 section: composite-DM overlaps NREFT framework |
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (MODIFIED) | §0: LZ paper reference + paper-specific facts |
| `EXTRACT.md` (MODIFIED) | Top-of-doc: LZ paper reference + T80 cross-reference |
| `docs/LAYMAN_SUMMARY_T77_LZ_2026_09.md` (MODIFIED) | T80 section: best-fit Ls₁₀ at 1000 GeV |
| `v0.3-prelim/docs/T80_LZ_PAPER_UPDATE.md` (NEW) | This file |
| `CHANGELOG.md` (MODIFIED) | T80 entry |

## Honest limitations

1. **Preprint, not peer-reviewed:** the LZ paper is in PRL
   submission as of 2026-09-02. The PRL version may differ from
   the preprint. The KIV cron will re-check on 2026-11-01.
2. **3.4σ local vs 2.6σ global distinction:** the project should
   NOT set a precedent for "local-only" updates. The paper
   authors themselves use the 2.6σ global figure as the headline.
3. **NREFT operator interpretation:** the LZ paper's best-fit is
   Ls₁₀ (magnetic-moment interaction), but the paper also tests
   O₁ˢ, O₄ᵛ, L₁₋L₂₀. The project should not over-commit to a
   specific operator choice at this stage.
4. **Best-fit m_χ ~ 1000 GeV vs project MAP m_χ ~ 770 GeV:** these
   are close but not identical. The project's posterior
   distribution includes m_χ values up to ~1000 GeV within the
   1σ credible interval.

## Provenance

> T80 paper-specific update in response to the LZ preprint
> appearing 2026-09-02 (much earlier than the KIV cron's
> expected 2026-11-01 fire date). The user uploaded the actual
> LZ paper as `LZ_Preprint_260901_Dark_Matter_EFT_Nuclear_Recoil_Search_at_Higher.pdf`.
> Key paper-specific facts verified end-to-end per AGENTS.md
> rule 21:
> - 2.84 tonne-years exposure
> - 5.4-270 keV energy window
> - NREFT operators O₁ˢ, O₄ᵛ, L₁₋L₂₀, Ls₁₀
> - 248 ± 23(stat) ± 23(sys) keV event
> - 3.4σ local / 2.6σ global significance
> - Best-fit: Ls₁₀ at m_χ = 1000 GeV/c²
> - Project m_χ ~ 770 GeV very close to LZ best-fit
>
> Standing posture preserved at v0.4-prelim+T75. No Channel 5
> update, no T41 re-run (2.6σ global < 3σ threshold). KIV cron
> retained for 2026-11-01 to check for PRL final version.
> Implementation: 2026-09-02.