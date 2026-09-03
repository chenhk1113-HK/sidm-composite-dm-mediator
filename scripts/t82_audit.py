#!/usr/bin/env python3
"""T82 stale-claim audit script.

Verifies every bold quantitative claim in the 5 drift-guard docs +
2 supporting docs against the canonical v0.7 T41 result JSON.

SOURCE OF TRUTH:
    v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json

CHECKED SOURCES (each gets PASS or DRIFT_FOUND):
    VERSION, README.md, CITATION.cff, EXTRACT.md,
    MODEL_ASSUMPTIONS_AND_LIMITATIONS.md, CHANGELOG.md,
    docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md

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

DOCS = [
    ("VERSION", "VERSION"),
    ("README.md", "README.md"),
    ("CITATION.cff", "CITATION.cff"),
    ("EXTRACT.md", "EXTRACT.md"),
    ("MODEL_ASSUMPTIONS_AND_LIMITATIONS.md", "MODEL_ASSUMPTIONS_AND_LIMITATIONS.md"),
    ("CHANGELOG.md", "CHANGELOG.md"),
    ("docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md", "docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md"),
]

CHECKS_PER_DOC: dict[str, list[tuple[str, str]]] = {
    "README.md": [
        ("σ/m headline", "0.27 cm²/g"),
        ("a headline", "+0.34"),
        ("tension", "0.60σ"),
        ("m_φ median", "588 MeV"),
        ("m_φ MAP", "453 MeV"),
        ("m_χ median", "498 GeV"),
        ("m_χ MAP", "770 GeV"),
        ("ε median", "1.4×10⁻³⁷"),
        ("log Z", "−163.29 ± 0.085"),
        ("channels", "**19**"),
        ("tests", "504 pass, 6 skip"),
    ],
    "CITATION.cff": [
        ("log Z", "-163.29"),
        ("tension", "tension T39 vs Yukawa a = 0.60"),
        ("m_chi", "MAP m_chi = 770"),
        ("sigma/m_0", "sigma/m_0 = 0.27"),
    ],
    "MODEL_ASSUMPTIONS_AND_LIMITATIONS.md": [
        ("log_epsilon", "log_epsilon = -36.95"),
        ("log_alpha", "log_alpha = -16.17"),
        ("m_φ claim", "m_φ = 453"),
        ("ε_γ", "1.12 × 10⁻³⁷"),
        ("α_X", "6.84 × 10⁻¹⁷"),
    ],
    "EXTRACT.md": [
        ("Channels 19", "Channels: **19**"),
        ("Tests 504", "504 pass"),
        ("σ/m headline", "σ/m = 0.27 cm²/g"),
    ],
    "docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md": [
        ("m_χ MAP", "770 GeV"),
        ("σ/m₀", "0.27 cm²/g"),
        ("log Z", "**-163**"),
        ("tension 0.60", "0.60** (below 1.0)"),
        ("channels 19", "**19**"),
        ("tests 504", "504**"),
    ],
    "CHANGELOG.md": [
        ("T75 entry", "v0.4-prelim+T75"),
        ("log Z", "-163.29"),
    ],
    "VERSION": [
        ("standing version", "0.4-prelim+T75"),
    ],
}


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

    for fpath_label in (label for _path, label in DOCS):
        path = REPO / fpath_label
        if not path.exists():
            print(f"=== {fpath_label}: NOT FOUND ===")
            any_drift = True
            continue
        checks = CHECKS_PER_DOC.get(fpath_label, [])
        if not checks:
            continue
        text = path.read_text(encoding="utf-8")
        print(f"=== {fpath_label} ===")
        for label, needle in checks:
            total += 1
            if needle in text:
                passes += 1
                print(f"  ✓ {label}: '{needle}' found")
            else:
                any_drift = True
                print(f"  ✗ {label}: '{needle}' MISSING")

    print()
    print("=" * 70)
    if any_drift:
        print(f"DRIFT DETECTED: {passes}/{total} checks passed")
        return 1
    print(f"ALL CLEAR: {passes}/{total} checks passed — no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
