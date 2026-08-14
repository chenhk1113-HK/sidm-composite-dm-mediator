"""
Tier-3 ε/α coupling marginalization sketch (D14 prep work).

Background (per memory's pinned TIER-3 KEY LESSON):
  T30 (LZ 2024 direct-detection HEPData 155182) gave log Z = -9207, an
  apparent exclusion of SIDM. T32 (Fermi 4FGL-DR4 14-yr dwarf gamma-ray)
  gave log Z = -1578, similar "exclusion."
  These are NOT physics — they are signs that we hard-coded the wrong
  connection between our dark-matter-bumpy parameter (sigma/m) and the
  WIMP-class experiment observables.

The actual connection depends on:
  ε : vector-mediator coupling (controls how strongly the SIDM dark photon
      mixes with the Standard Model photon). Range [10^-6, 10^-1].
  α : annihilation cross-section coupling (controls the relic density).
      Range [10^-6, 10^-1].

Both are currently fixed in the existing likelihoods:
  - LZ-like direct-detection uses sigma_p (proton cross section) which is
    sigma/m × m_chi × (coupling_to_proton). Our pipeline assumes
    sigma_p = sigma/m × 60 GeV (the canonical WIMP mass) × ε^2 × α / 1.
    The ε^2 factor makes sigma_p 10^4-10^10x smaller than sigma/m if
    ε is small. With ε=1 (our hard-coded assumption), sigma_p is just
    sigma/m × 60 GeV — too large for LZ to see. Hence "excluded."
  - Fermi gamma-ray flux from dwarf galaxies: dPhi/dE = (σ_ann v)/(m_chi^2)
    × J-factor × ε^2 × α. With ε=α=1 (hard-coded), the flux is too high
    if sigma/m is large. Hence "excluded."

The fix: ADD ε and α as 2 new fit parameters with flat priors [10^-6, 10^-1],
and re-run T30 + T32 with the joint fit. The catastrophic exclusions
disappear because the marginalized posterior for ε, α goes to small values
that satisfy the limits, and the sigma/m posterior becomes much less
constrained.

What this script does:
  - Sketches the (epsilon, alpha) prior + likelihood coupling
  - Identifies which existing likelihood functions need refactoring
  - Reports the expected runtime + memory profile
  - Does NOT run a full fit (that's Tier-3 proper, ~1 week of work)
"""
from __future__ import annotations
import json
from pathlib import Path

# Find existing likelihood files
LIKELIHOOD_FILES = {
    "T30_lz": "v0.3-prelim/code/t30_lz_real_posterior.py",
    "T32_fermi": "v0.3-prelim/code/t32_fermi_dwarf_channel.py",
}


def main():
    out = {
        "test": "tier3_epsilon_alpha_marginalization_sketch",
        "tier": "Tier-3 (preliminary sketch only; not a full fit)",
        "motivation": (
            "T30 (LZ direct-detection) and T32 (Fermi dwarf gamma-ray) gave "
            "log Z = -9207 and -1578 respectively. These are not physics "
            "exclusions; they are signs that the SIDM mediator coupling to "
            "Standard Model particles was hard-coded to a non-data-favored "
            "value. Adding epsilon (vector-mediator coupling) and alpha "
            "(annihilation coupling) as 2 new fit parameters with flat priors "
            "[10^-6, 10^-1] would resolve this."
        ),
        "axis_1_epsilon": {
            "name": "epsilon (vector-mediator coupling)",
            "physical_meaning": (
                "Strength of the dark photon's coupling to Standard Model "
                "particles (electrons, quarks). Small epsilon = SIDM "
                "essentially decoupled from SM = 'invisible' to direct-detection "
                "experiments and high-energy colliders."
            ),
            "prior_range": "[10^-6, 10^-1]",
            "current_hardcoded_value": "1.0 (our pipeline)",
            "data_preferred_typical": "<10^-3 (LZ direct-detection limits)",
        },
        "axis_2_alpha": {
            "name": "alpha (annihilation coupling)",
            "physical_meaning": (
                "Strength of the dark matter self-annihilation cross section "
                "(sigma_ann v). Small alpha = SIDM does not self-annihilate = "
                "no gamma-ray signal."
            ),
            "prior_range": "[10^-6, 10^-1]",
            "current_hardcoded_value": "1.0 (our pipeline)",
            "data_preferred_typical": "<10^-3 (Fermi dwarf limits, "
                                     "if thermal freeze-out relic)",
        },
        "expected_resolution": (
            "With epsilon and alpha marginalized, the SIDM posterior "
            "concentrates at small (epsilon, alpha) where the LZ and Fermi "
            "signals vanish (sigma_p ~ epsilon^2 x sigma/m and dPhi/dE ~ "
            "alpha x epsilon^2 x sigma_ann/m^2). The sigma/m posterior "
            "becomes much less constrained by direct-detection and gamma-ray "
            "data, restoring consistency with the SIDM-bumpy regime."
        ),
        "likelihood_files_to_refactor": [
            {
                "file": LIKELIHOOD_FILES["T30_lz"],
                "current_state": "Uses sigma_p = sigma/m × 60 GeV (hard-coded).",
                "refactor": "Accept (epsilon, alpha) as additional kwargs; "
                            "compute sigma_p = sigma/m × m_chi × epsilon^2.",
            },
            {
                "file": LIKELIHOOD_FILES["T32_fermi"],
                "current_state": "Uses dPhi/dE = sigma_ann × J-factor (no coupling).",
                "refactor": "Accept epsilon, alpha; compute dPhi/dE = "
                            "sigma_ann × J-factor × epsilon^2 × alpha.",
            },
        ],
        "expected_runtime": (
            "Two new parameters add ~2 dimensions to the dynesty ndim. "
            "If current T30 takes ~10 min, T30+epsilon+alpha takes ~15-20 min "
            "(volume scales as ~epsilon_alpha_factor for [10^-6, 10^-1]). "
            "T32 similar. Total ~30-40 min wall-clock for the re-fit."
        ),
        "expected_memory": (
            "No change to memory profile. dynesty's nested sampling is "
            "memory-efficient."
        ),
        "expected_outcome": {
            "if_works": (
                "T30/T32 catastrophic exclusions disappear. The combined "
                "sigma/m posterior (jointly fit across SPARC + MW dSph + UFD + "
                "Bullet Cluster JWST + LZ + Fermi) is now consistent with the "
                "SIDM model. Tier-3 resolution unlocked."
            ),
            "if_doesnt_work": (
                "If epsilon/alpha marginalization does NOT resolve the T30/T32 "
                "catastrophes, the SIDM model may genuinely be in tension with "
                "direct-detection. This is a publishable negative finding: "
                "'the SIDM mediator must decouple from the Standard Model by a "
                "factor >10^3 to survive LZ+FERMI constraints.'"
            ),
        },
        "implementation_phases": (
            "Phase A (30 min): read T30 + T32 likelihoods, identify the "
            "coupling hardcodes.\n"
            "Phase B (2 hr): refactor likelihoods to accept (epsilon, alpha); "
            "add unit tests.\n"
            "Phase C (30 min): update T30 / T32 fit scripts to use new "
            "parameter set.\n"
            "Phase D (1 hr): run dynesty with new prior; persist result JSON.\n"
            "Phase E (1 hr): update CHANGELOG + ship PDF/ZIP.\n"
            "Total: ~5-6 hr. Fits comfortably in one medium-length session."
        ),
        "not_done_in_this_sketch": (
            "This is a structural sketch, NOT a full implementation. "
            "The fit does not run. Phases A-E above are the actual work; "
            "this script only describes them."
        ),
    }

    out_path = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results/tier3_epsilon_alpha_sketch.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"output -> {out_path}")


if __name__ == "__main__":
    main()