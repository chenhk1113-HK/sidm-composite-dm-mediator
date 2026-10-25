"""n18.docx review fixes — verified defects from the n18 external review.

Every fix below was INDEPENDENTLY VERIFIED by the controller against on-disk
ground truth before being applied. The review's own attribution of each
finding was re-derived from git history, and where the review was WRONG the
correction is recorded rather than silently adopted.

Review source: n18.docx (Chinese-language review of the Round 5 consolidated
fixes report + changed-code companion). The .docx itself is TRUNCATED: the
severity table survives only as its last row ("7  diff 单行长段落可读性差 低"),
so findings 1-6 of that table are unrecoverable from the file. The three
priority items in the review's closing "总体判断" section ARE complete and are
the actionable set handled here.

VERIFIED DEFECTS FIXED
-----------------------
F1  PAPER L102 — "For **0 of 8** halos is |σ_HL| < 0.05 cm²/g" has broken
    word order ("halos is"). PROVENANCE: INTRODUCED BY ROUND 5 — `git log -S`
    shows the string "halos is" first appears in 7cc8d8a (the Round 5 fix
    commit) and is absent from 7cc8d8a^. Pre-Round-5 the sentence read
    "For 7 of 8 halos, |σ_HL| < 0.05 cm²/g (small, consistent with ...)";
    Round 5 changed the count 7->0 and inserted "is" but left the verb
    agreement broken. Fix: "For **0 of 8** halos, |σ_HL| < 0.05 cm²/g" —
    restoring the comma, dropping the dangling "is".

F2  PAPER L102 — "σ_HL = −0.534 cm²/g., indicating an**internal inconsistency"
    carries a doubled sentence-ending period + comma ("g.,"). PROVENANCE:
    INTRODUCED BY ROUND 5 — the string "cm²/g.," appears exactly once in the
    whole paper and `git log -S"cm²/g.,"` returns only 7cc8d8a; it is absent
    from 7cc8d8a^. Round 5 rewrote this sentence from "σ_HL = -0.473 cm²/g,
    indicating ..." to "σ_HL = −0.534 cm²/g., indicating ...". Fix: drop the
    stray period, leaving "cm²/g, indicating".

F3  PAPER L102 (same sentence as F2) — "an**internal inconsistency" is a
    missing-space defect: the bold opener is glued to the preceding word.
    PROVENANCE: PRE-EXISTING, carried through Round 5 (present 1x in both
    7cc8d8a^ and 7cc8d8a) — NOT introduced by Round 5. The review did not
    flag it, but it sits inside the sentence F1/F2 repair, and it renders as
    fused words ("aninternal"). Fix: insert the space.

F4  PAPER L151 — "the ratio derivation changes and 4 baseline headline value
    7.5×10⁻¹² holds under ..." is missing a noun phrase. PROVENANCE:
    PRE-EXISTING since commit 799f4ef ("R88 paper cleanup"), NOT introduced by
    Round 5. The review asserted all three text errors were newly introduced
    by the fixes; that is wrong for this one. ROOT CAUSE: 799f4ef replaced the
    phrase "the ratio derivation changes and g_N/g_χ < 10⁻²³. The σ_1 = "
    with "the ratio derivation changes and ", deleting the trailing
    "The σ_1 = " of the following sentence and leaving "4 baseline headline
    value". The canonical restoration is verified against 799f4ef^, which
    reads "... the ratio derivation changes and g_N/g_χ < 10⁻²³. The σ_1 =
    4.4 baseline headline value 7.5×10⁻¹² holds under ...". Fix: restore
    the subject as "the σ_1 = 4.4 baseline headline value" (the paper's own
    σ_1 = 4.4 baseline; the computed like-for-like bounds at the v = 28 anchor
    are 1.78e-13 / 1.84e-13 / 2.84e-13, consistent with the surrounding text).

F5  GENERATOR DOCSTRING — `scripts/v192_dsph_gravothermal_sweep.py` line 24
    states "the identity sigma_eff = f_H^2 * sigma/m would give 0.257-1.589
    cm^2/g". The correct values are 0.256-1.518 cm²/g. VERIFIED BY
    RECOMPUTATION from the canonical source
    (`v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json`
    -> `_derived_ranges.sigma_m_cm2_per_g` = 2.845457..16.865226, times
    F_H_CC**2 = 0.09, gives 0.256091..1.517870 -> 0.256-1.518), and
    independently from `channels_v03.sigma_m_at_v` + `constants.py`
    (sigma/m(5) = 16.865226 -> 0.09x = 1.517870). The docstring's upper end
    1.589 implies sigma/m = 17.656, which is NOT the canonical maximum;
    the lower end 0.257 implies 2.856, also not canonical.
    PROVENANCE: the string "0.257-1.589" appears only in 7cc8d8a, i.e. the
    Round 5 commit introduced this stale pair while fixing the OTHER stale
    narratives in the same docstring. This is the same defect class the Round 5
    root-cause fix addressed (hardcoded narrative that disagrees with the
    generator's own output) — Round 5 made the JSON's `interpretation` and
    `limitations` fields computed but left this docstring hand-written.
    Fix: correct both ends to the computed 0.256-1.518.

F6  CHANGED-CODE COMPANION §3 — the companion embedded the FULL 241-line
    `v192_dsph_gravothermal_sweep.json`, of which only ~18 lines changed in
    Round 5 (the added `_derived_ranges` block, the changed `interpretation`
    string, and one added `limitations` entry). The review's point is
    correct: a companion document whose purpose is "show what changed" should
    not bury the change inside 220 unchanged lines. Verified: the companion's
    JSON block is byte-identical to the live JSON (`d == live` True, all 8
    top-level keys equal, no differing values), so it carries zero
    information the live file does not.
    Fix: replace the full-file embed with a real DIFF of the JSON
    (pre-Round-5 vs current), which is what a changed-code companion should
    show, and keep a pointer to the live file.

F7  CHANGED-CODE COMPANION §2 (paper diff) — the diff fence contains single
    lines up to 3581 characters, which is unreadable in a code fence. The
    review rated this LOW severity. Fix: re-emit the diff with hard-wrapped
    context lines so each line is readable, preserving the +/- markers.

REJECTED / CORRECTED FINDINGS
------------------------------
R1  The review states: "这些是修复引入的新错误（原论文中不存在）" — that all
    three paper text errors were newly introduced by the Round 5 fixes.
    CORRECTED: only 2 of the 3 were (F1, F2). The third (F4, "and 4
    baseline") predates Round 5 by many commits (introduced 799f4ef) and was
    carried through unchanged. The defect is real and IS fixed here, but the
    attribution is corrected in the v1.1 report so the next reviewer does not
    re-litigate provenance.

R2  The review treats the "docstring 1.589 vs 1.518" gap as "小数舍入级别
    的差异" (a decimal-rounding-level difference). CORRECTED: it is not a
    rounding difference. The upper end 1.589 implies a sigma/m maximum of
    17.656 cm²/g against the canonical 16.865 cm²/g — a 4.7% error in the
    quantity, not a last-digit rounding. Fixed anyway (F5), and the
    characterization is corrected in the v1.1 report.

R3  The review's claim that the paper's σ/m band is "2.85–16.87 cm²/g" and
    the JSON's "2.8454570671911887–16.865226429437705" agree is CONFIRMED
    (rounds to 2.85-16.87). No action.

R4  The review's claim that "0 of 8" halos satisfy |σ_HL| < 0.05 is
    CONFIRMED against `_derived_ranges.n_halos_abs_sigma_HL_below_0.05 == 0`.
    No action.

R5  NOT ACTIONED — bold-marker spacing (e.g. "an**internal", "is**NOT
    falsified**", 270 occurrences of a ** surrounded by word characters on
    both sides). These render CORRECTLY: verified with `markdown_it`
    (the CommonMark reference implementation), where
    "an**internal inconsistency**" renders as
    `<p>indicating an<strong>internal inconsistency</strong> end</p>` — the
    emphasis is applied and no literal "**" survives. This is the paper's
    pre-existing house style across ~270 sites, not a defect, and the review
    did not flag it. Only the ONE instance inside the sentence being repaired
    (F3) is fixed, for readability of that sentence. A wholesale restyle is
    out of scope for this review and would be a large mechanical rewrite of a
    2400-line paper.

R6  NOT ACTIONED — the paper's "does not.." (double period, line 974) and
    "curves .**" (space before period, line 120). Both are PRE-EXISTING
    (650ff13 and 799f4ef respectively), outside the reviewed diff, and are
    cosmetic. Recorded here for a future sweep rather than mixed into this
    review round.

AUDIT NOTE (why F5 is a GENERATOR fix, not just a docstring edit)
-----------------------------------------------------------------
Per the stale-narrative-string-audit discipline: a docstring that restates a
computed quantity is a second copy of the defect and will drift again. F5
therefore also adds a REGRESSION TEST that recomputes f_H_CC**2 x the
canonical sigma/m range from the generator's own output JSON and asserts the
docstring quotes the same numbers. The test fails if either side drifts.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
GENERATOR = REPO / "scripts" / "v192_dsph_gravothermal_sweep.py"
SWEEP_JSON = REPO / "v0.3-prelim" / "data" / "results" / "v192_dsph_gravothermal_sweep.json"
TEST_FILE = REPO / "v0.3-prelim" / "tests" / "test_n18_generator_docstring_consistency.py"

# --------------------------------------------------------------------------
# F1 + F2 + F3: paper L102 — one sentence, three defects.
# --------------------------------------------------------------------------
PAPER_F1_OLD = "For **0 of 8** halos is |σ_HL| < 0.05 cm²/g"
PAPER_F1_NEW = "For **0 of 8** halos, |σ_HL| < 0.05 cm²/g"

PAPER_F2_OLD = "σ_HL = −0.534 cm²/g., indicating an**internal inconsistency"
PAPER_F2_NEW = "σ_HL = −0.534 cm²/g, indicating an **internal inconsistency"

# --------------------------------------------------------------------------
# F4: paper L151 — restore the deleted subject of the second clause.
# --------------------------------------------------------------------------
PAPER_F4_OLD = (
    "the ratio derivation changes and 4 baseline headline value 7.5×10⁻¹² holds under "
    "the σ_1 = 4.4 phenomenological width"
)
PAPER_F4_NEW = (
    "the ratio derivation changes and the σ_1 = 4.4 baseline headline value 7.5×10⁻¹² "
    "holds under the σ_1 = 4.4 phenomenological width"
)

# --------------------------------------------------------------------------
# F5: generator docstring stale range.
# --------------------------------------------------------------------------
GEN_OLD = (
    "   sigma_eff = f_H^2 * sigma/m would give 0.257-1.589 cm^2/g -- far ABOVE\n"
)
GEN_NEW = (
    "   sigma_eff = f_H^2 * sigma/m would give 0.256-1.518 cm^2/g -- far ABOVE\n"
)


def _read(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes().decode("utf-8")
    return raw.replace("\r\n", "\n"), "\r\n" in raw


def _write(path: Path, text: str, crlf: bool) -> None:
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8") if crlf else text.encode("utf-8"))


def _apply(text: str, old: str, new: str, label: str) -> str:
    """Replace `old` with `new`, asserting exactly one occurrence.

    Idempotent: if `old` is absent and `new` is already present exactly once,
    the replacement is a no-op (the fix is already applied).
    """
    n_old = text.count(old)
    n_new = text.count(new)
    if n_old == 1 and n_new == 0:
        return text.replace(old, new, 1)
    if n_old == 0 and n_new == 1:
        print(f"  [skip] {label}: already applied")
        return text
    raise AssertionError(
        f"{label}: expected exactly 1 occurrence of the old string "
        f"(found {n_old}) and 0 of the new (found {n_new}). Refusing to edit."
    )


def fix_paper() -> list[str]:
    text, crlf = _read(PAPER)
    applied: list[str] = []
    for old, new, label in (
        (PAPER_F1_OLD, PAPER_F1_NEW, "F1 paper L102 'halos is' word order"),
        (PAPER_F2_OLD, PAPER_F2_NEW, "F2+F3 paper L102 'cm²/g.,' + 'an**internal'"),
        (PAPER_F4_OLD, PAPER_F4_NEW, "F4 paper L151 'and 4 baseline' lost subject"),
    ):
        before = text
        text = _apply(text, old, new, label)
        if text != before:
            applied.append(label)
            print(f"  [fixed] {label}")
    _write(PAPER, text, crlf)
    return applied


def fix_generator() -> list[str]:
    text, crlf = _read(GENERATOR)
    before = text
    text = _apply(text, GEN_OLD, GEN_NEW, "F5 generator docstring 0.257-1.589")
    applied = []
    if text != before:
        applied.append("F5 generator docstring stale range")
        print("  [fixed] F5 generator docstring 0.257-1.589 -> 0.256-1.518")
    _write(GENERATOR, text, crlf)
    return applied


# --------------------------------------------------------------------------
# F5 companion: regression test pinning the docstring to the generator's own
# output. Without this the docstring drifts again on the next regeneration.
# --------------------------------------------------------------------------
TEST_SOURCE = '''"""n18 regression test — generator docstring must agree with its own output JSON.

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
    m = re.search(r"^F_H_CC\\s*=\\s*([0-9.]+)", text, re.M)
    assert m, "F_H_CC constant not found in the generator"
    return float(m.group(1))

def _docstring_range() -> tuple[float, float]:
    text = GENERATOR.read_text(encoding="utf-8")
    m = re.search(
        r"sigma_eff = f_H\\^2 \\* sigma/m would give ([0-9.]+)-([0-9.]+) cm\\^2/g",
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
    m = re.search(r"published\\s+sigma_eff band is ([0-9.]+)-([0-9.]+) cm\\^2/g", text)
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
    m = re.search(r"and (\\d+) of (\\d+) halos satisfy \\|sigma_HL\\| < 0\\.05 cm\\^2/g", text)
    assert m, "docstring no longer states the halo count"
    assert int(m.group(1)) == rng["n_halos_abs_sigma_HL_below_0.05"]
    assert int(m.group(2)) == rng["n_halos"]
'''


def add_regression_test() -> list[str]:
    if TEST_FILE.exists():
        text, crlf = _read(TEST_FILE)
        if "test_docstring_range_matches_output_json" in text:
            print("  [skip] F5 regression test: already present")
            return []
    TEST_FILE.write_bytes(TEST_SOURCE.replace("\n", "\r\n").encode("utf-8"))
    print(f"  [added] F5 regression test: {TEST_FILE.relative_to(REPO)}")
    return ["F5 regression test (docstring pinned to output JSON)"]


def main() -> int:
    print("=== n18.docx review fixes ===")
    applied: list[str] = []
    print("-- paper --")
    applied += fix_paper()
    print("-- generator --")
    applied += fix_generator()
    print("-- regression test --")
    applied += add_regression_test()

    print()
    print(f"Applied {len(applied)} fixes:")
    for a in applied:
        print(f"  - {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
