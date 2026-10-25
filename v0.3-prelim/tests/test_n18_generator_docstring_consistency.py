"""n18 regression test — generator docstring must agree with its own output JSON.

F5 (n18.docx review): the module docstring of
`scripts/v192_dsph_gravothermal_sweep.py` quoted the f_H^2 x sigma/m range as
"0.257-1.589 cm^2/g" while the generator's own emitted JSON gives
0.256-1.518 cm^2/g. A docstring that restates a computed quantity is a second
copy of the defect (see the stale-narrative-string-audit discipline), so this
test pins the two against each other.

The test recomputes the range from `_derived_ranges` in the generator's
output JSON and asserts the docstring quotes the same numbers. It fails if
EITHER side moves.

Round 5 already made the JSON's `interpretation` and `limitations` fields
computed; this test closes the remaining hole (the hand-written docstring).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATOR = REPO / "scripts" / "v192_dsph_gravothermal_sweep.py"
SWEEP_JSON = REPO / "v0.3-prelim" / "data" / "results" / "v192_dsph_gravothermal_sweep.json"


def _generator_f_h_cc() -> float:
    """The canonical f_H_cc, read from the generator's own constant.

    `dsph_halos` entries do not carry f_H_cc, so the generator's F_H_CC
    constant is the single source of truth. Reading it (rather than
    hard-coding 0.30) means the test tracks the generator if f_H ever changes.
    """
    text = GENERATOR.read_text(encoding="utf-8")
    m = re.search(r"^F_H_CC\s*=\s*([0-9.]+)", text, re.M)
    assert m, "F_H_CC constant not found in the generator"
    return float(m.group(1))

def _docstring_range() -> tuple[float, float]:
    text = GENERATOR.read_text(encoding="utf-8")
    m = re.search(
        r"sigma_eff = f_H\^2 \* sigma/m would give ([0-9.]+)-([0-9.]+) cm\^2/g",
        text,
    )
    assert m, "docstring no longer states the f_H^2 x sigma/m range"
    return float(m.group(1)), float(m.group(2))


def test_docstring_range_matches_output_json():
    """The docstring's quoted range must equal f_H^2 x the canonical sigma/m range."""
    data = json.loads(SWEEP_JSON.read_text(encoding="utf-8"))
    rng = data["_derived_ranges"]["sigma_m_cm2_per_g"]
    f_h = _generator_f_h_cc()
    expected_lo = round(f_h**2 * rng["min"], 3)
    expected_hi = round(f_h**2 * rng["max"], 3)

    doc_lo, doc_hi = _docstring_range()
    assert (doc_lo, doc_hi) == (expected_lo, expected_hi), (
        f"docstring quotes {doc_lo}-{doc_hi} cm^2/g but the generator's own output "
        f"gives {expected_lo}-{expected_hi} cm^2/g (f_H^2 x sigma/m range "
        f"{rng['min']:.6f}..{rng['max']:.6f}). Regenerate and update both together."
    )


def test_docstring_range_is_not_the_retracted_value():
    """Guard the specific stale pair the n18 review caught (0.257-1.589)."""
    doc_lo, doc_hi = _docstring_range()
    assert (doc_lo, doc_hi) != (0.257, 1.589), (
        "docstring quotes the retracted 0.257-1.589 range; the canonical "
        "f_H^2 x sigma/m range is 0.256-1.518 cm^2/g"
    )


def test_published_sigma_eff_band_in_docstring_matches_json():
    """The docstring's published sigma_eff band must match _derived_ranges too."""
    data = json.loads(SWEEP_JSON.read_text(encoding="utf-8"))
    rng = data["_derived_ranges"]["sigma_eff_published_cm2_per_g"]
    text = GENERATOR.read_text(encoding="utf-8")
    m = re.search(r"published\s+sigma_eff band is ([0-9.]+)-([0-9.]+) cm\^2/g", text)
    assert m, "docstring no longer states the published sigma_eff band"
    assert (float(m.group(1)), float(m.group(2))) == (
        round(rng["min"], 3),
        round(rng["max"], 3),
    ), "docstring published sigma_eff band disagrees with _derived_ranges"


def test_halo_count_in_docstring_matches_json():
    """'0 of 8 halos' must match _derived_ranges.n_halos."""
    data = json.loads(SWEEP_JSON.read_text(encoding="utf-8"))
    rng = data["_derived_ranges"]
    text = GENERATOR.read_text(encoding="utf-8")
    m = re.search(r"and (\d+) of (\d+) halos satisfy \|sigma_HL\| < 0\.05 cm\^2/g", text)
    assert m, "docstring no longer states the halo count"
    assert int(m.group(1)) == rng["n_halos_abs_sigma_HL_below_0.05"]
    assert int(m.group(2)) == rng["n_halos"]
