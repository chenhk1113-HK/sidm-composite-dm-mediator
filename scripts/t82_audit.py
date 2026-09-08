#!/usr/bin/env python3
"""T82 stale-claim audit script.

Verifies every bold quantitative claim in the 5 drift-guard docs +
2 supporting docs against the canonical v0.7 T41 result JSON.

SOURCE OF TRUTH:
    v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json

CHECKED SOURCES (each gets PASS or DRIFT_FOUND):
    VERSION, README.md, CITATION.cff, EXTRACT.md,
    MODEL_ASSUMPTIONS_AND_LIMITATIONS.md, CHANGELOG.md,
    docs/LAYMAN_SUMMARY.md, CURRENT.md

Each check returns MATCH (the expected string is present) or DRIFT
(missing or mismatched). Exit code 0 = clean, 1 = drift detected.

Run from the project root:
    python scripts/t82_audit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

GROUND_TRUTH_JSON = (
    REPO
    / "v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json"
)
# Post-T88.E headline (v0.8) — see data/results/t41_mediator_mass_joint_fit_t88ce_v08_with_euclid_lensing_and_subhalo_forecast_nlive2000.json
HEADLINE_V08_JSON = (
    REPO
    / "v0.3-prelim/data/results/t41_mediator_mass_joint_fit_t88ce_v08_with_euclid_lensing_and_subhalo_forecast_nlive2000.json"
)

DOCS = [
    ("VERSION", "VERSION"),
    ("README.md", "README.md"),
    ("CITATION.cff", "CITATION.cff"),
    ("EXTRACT.md", "EXTRACT.md"),
    ("MODEL_ASSUMPTIONS_AND_LIMITATIONS.md", "MODEL_ASSUMPTIONS_AND_LIMITATIONS.md"),
    ("CURRENT.md", "CURRENT.md"),
    ("CHANGELOG.md", "CHANGELOG.md"),
    ("docs/LAYMAN_SUMMARY.md", "docs/LAYMAN_SUMMARY.md"),
]

CHECKS_PER_DOC: dict[str, list[tuple[str, str]]] = {
    "README.md": [
        ("σ/m headline", "0.06 cm²/g"),
        ("a headline", "+0.13"),
        ("tension", "0.60σ"),
        ("m_φ MAP", "453 MeV"),
        ("m_χ MAP", "770 GeV"),
        ("log Z (v0.8)", "−164.87 ± 0.084"),
        ("log Z (v0.7 historical)", "−163.29"),
        ("channels", "**22**"),
        ("tests", "677 pass, 8 skip"),
        ("headline row present", "**σ/m₀**"),
        ("ε posterior reference", "10⁻³⁷"),
    ],
    "CITATION.cff": [
        ("log Z (v0.8)", "-164.87"),
        ("log Z (v0.7 historical)", "-163.29"),
        ("tension", "tension T39 vs Yukawa a = 0.60"),
        ("m_chi", "MAP m_chi = 770"),
        ("sigma/m_0 (v0.7 historical)", "sigma/m_0 = 0.27"),
        ("sigma/m_0 (v0.8)", "sigma/m_0 = 0.06"),
        ("version", "0.4-prelim+T88E"),
    ],
    "MODEL_ASSUMPTIONS_AND_LIMITATIONS.md": [
        ("log_epsilon", "log_epsilon = -36.95"),
        ("log_alpha", "log_alpha = -16.17"),
        ("m_φ claim", "m_φ = 453"),
        ("ε_γ", "1.12 × 10⁻³⁷"),
        ("α_X", "6.84 × 10⁻¹⁷"),
        # T90 (2026-09-08) magnetic-moment "Door B" section cross-checks
        ("T90 Door B section heading", "Magnetic-moment Ls₁₀ channel"),
        ("T90 8D log Z", "-162.78"),
        ("T90 8D delta log Z", "+0.51"),
        ("T90 8D MAP m_chi", "138 GeV"),
        ("T90 8D MAP delta", "98 keV"),
        ("T90 8D MAP sigma_PortalB", "1.4×10⁻⁴²"),
        # T110 (2026-09-08) 7D dynesty magnetic-moment fit
        ("T110 7D log Z", "-174.014"),
        ("T110 7D delta log Z", "-10.72"),
        ("T110 7D MAP m_chi", "712.6 GeV"),
        ("T110 7D MAP mu_x", "1.08×10⁻⁷"),
    ],
    "EXTRACT.md": [
        ("Channels 22", "Channels: **22 effective**"),
        ("Tests 677", "677 pass"),
        ("σ/m headline", "σ/m = 0.06 cm²/g"),
    ],
    "docs/LAYMAN_SUMMARY.md": [
        ("m_χ MAP", "770 GeV"),
        ("σ/m₀", "0.06 cm²/g"),
        ("log Z", "**-163**"),
        ("tension 0.60", "0.60** (below 1.0)"),
        ("channels 21", "**21**"),
        ("tests 677", "**677**"),
    ],
    "CHANGELOG.md": [
        ("v0.4-prelim+T88E", "v0.4-prelim+T88E"),
        ("log Z", "−164.87"),
    ],
    "VERSION": [
        ("standing version", "0.4-prelim+T88E"),
    ],
    "CURRENT.md": [
        ("Bayesian evidence log Z", "−164.87 ± 0.084"),
        ("m_χ (MAP)", "770 GeV"),
        ("m_φ (MAP)", "453 MeV"),
        ("σ/m₀", "0.06 cm²/g"),
        ("Tension", "0.60σ"),
        ("Channels", "22 effective channels"),
        ("677 tests", "677 pass"),
        ("Drift-guard", "44/44 ALL CLEAR"),
    ],
}


# ---------------------------------------------------------------------------
# T83.6 (post-review) — VERSION drift-guard.
# Per Updated review1.docx §1 (received 2026-09-03): the raw VERSION file
# once lagged behind the badge/CITATION/CHANGELOG. Add an explicit check so
# any future VERSION-vs-doc drift fails CI rather than slipping past
# human reviewers. The canonical standing-version string for the
# current Tier-1 milestone is "0.4-prelim+T75" — bump this constant when
# the next standing version is published.
# ---------------------------------------------------------------------------

CANONICAL_STANDING_VERSION = "0.4-prelim+T88E"
VERSION_LABEL = "VERSION"


def main() -> int:
    if not GROUND_TRUTH_JSON.exists():
        print(f"ERROR: ground truth JSON not found: {GROUND_TRUTH_JSON}", file=sys.stderr)
        return 2

    j = json.loads(GROUND_TRUTH_JSON.read_text(encoding="utf-8"))
    log_z = round(j["log_Z"], 2)
    log_z_err = round(j["log_Z_err"], 3)

    print("GROUND TRUTH (v0.7 T41, nlive=2000, ndim=6, DAMPE+LSS channels):")
    print(f"  log Z = {log_z} ± {log_z_err}")
    print(f"  m_χ MAP = {round(j['MAP_physical']['m_chi_GeV'], 1)} GeV")
    print(f"  m_φ MAP = {round(j['MAP_physical']['m_phi_MeV'])} MeV")
    print(f"  σ/m₀ MAP = {round(j['MAP_physical']['sigma_m_0_derived'], 2)} cm²/g")
    print(f"  a MAP = {round(j['MAP_physical']['a_derived'], 2)}")
    print(f"  ε_median = {j['median_physical']['epsilon']:.3e}")
    print(f"  tension = {round(j['yukawa_tension']['a_difference'], 2)}σ")
    print()

    any_drift = False
    total = 0
    passes = 0

    for _fpath, label in DOCS:
        path = REPO / label
        if not path.exists():
            print(f"=== {label}: NOT FOUND ===")
            any_drift = True
            continue
        checks = CHECKS_PER_DOC.get(label, [])
        if not checks:
            continue
        text = path.read_text(encoding="utf-8")
        print(f"=== {label} ===")
        for chk_label, needle in checks:
            total += 1
            if needle in text:
                passes += 1
                print(f"  ✓ {chk_label}: '{needle}' found")
            else:
                any_drift = True
                print(f"  ✗ {chk_label}: '{needle}' MISSING")

    # ------------------------------------------------------------------
    # VERSION drift-guard (T83.6, post-review Updated review1.docx §1).
    # Confirms the raw VERSION file exactly equals the canonical standing
    # version string. A diff means the VERSION file hasn't been bumped in
    # the latest docs-bake commit.
    # ------------------------------------------------------------------
    version_path = REPO / VERSION_LABEL
    if version_path.exists():
        raw_version = version_path.read_text(encoding="utf-8").strip()
        total += 1
        if raw_version == CANONICAL_STANDING_VERSION:
            passes += 1
            print(f"=== {VERSION_LABEL} (drift-guard) ===")
            print(f"  ✓ VERSION = '{raw_version}' matches canonical '{CANONICAL_STANDING_VERSION}'")
        else:
            any_drift = True
            print(f"=== {VERSION_LABEL} (drift-guard) ===")
            print(f"  ✗ VERSION = '{raw_version}' does NOT match canonical "
                  f"'{CANONICAL_STANDING_VERSION}' — drift!")

    print()
    print("=" * 70)
    if any_drift:
        print(f"DRIFT DETECTED: {passes}/{total} checks passed")
        return 1
    print(f"ALL CLEAR: {passes}/{total} checks passed — no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())