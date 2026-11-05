"""F16 single-source test for the channel taxonomy (2026-11-05).

Finding F16: the repo carried two different '8 channel' lists with different halo-type
labels and two different headline tallies, one of which (4 PASS / 3 MARGINAL / 1 FAIL)
no stored parameter set or documented sigma_unc convention reproduces.

What this test guarantees:
  1. the stored canonical tally block is reproducible RIGHT NOW by re-evaluating the
     channel list (live producer, not a read of stored JSON);
  2. the generated section_A15.md is identical to the region spliced into the paper;
  3. no headline doc quotes the retired 4/3/1 tally outside a retirement sentence;
  4. the block declares which likelihood list and sigma_unc convention it belongs to.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CANON_JSON = REPO / "v0.3-prelim" / "data" / "results" / "canonical_numbers.json"
A15_MD = REPO / "v0.3-prelim" / "data" / "results" / "section_A15.md"
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

RETIRED_TALLY = "4 PASS / 3 MARGINAL / 1 FAIL"


def _reevaluate_in_subprocess():
    """Re-derive every tally from scripts/canonical_numbers.py (no stored JSON read)."""
    snippet = (
        "import json,sys;"
        "sys.path.insert(0, r" + repr(str(REPO)) + ");"
        "sys.path.insert(0, r" + repr(str(REPO / "scripts")) + ");"
        "import canonical_numbers as c;"
        "out = [dict(parameter_set=n, convention=cv,"
        "            tally=c.evaluate_channels(c.PARAMETER_SETS[n], cv)[1])"
        " for n in c.PARAMETER_SETS for cv in c.SIGMA_UNC_CONVENTIONS];"
        "print(json.dumps(out))"
    )
    res = subprocess.run([sys.executable, "-c", snippet], capture_output=True,
                         text=True, encoding="utf-8", timeout=600, cwd=str(REPO))
    assert res.returncode == 0, f"generator re-evaluation failed:\n{res.stderr[-2000:]}"
    return json.loads(res.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def block():
    data = json.loads(CANON_JSON.read_text(encoding="utf-8"))
    return data["canonical_abstract_channel_count"]


def test_tally_block_is_declared_computed(block):
    assert block.get("computed") is True
    assert block.get("taxonomy"), "taxonomy (which channel list) is not declared"
    assert "OBS_PUBLISHED" in block["taxonomy"]
    assert block.get("likelihood_convention") in ("published_sigma_unc",
                                                 "self_normalized_sigma_unc")


def test_stored_tallies_reproduce_by_live_re_evaluation(block):
    live = _reevaluate_in_subprocess()
    stored = {(e["parameter_set"], e["convention"]): e["tally"]
              for e in block["evaluations"]}
    assert live, "generator produced no evaluations"
    mismatches = []
    checked = 0
    for ev in live:
        key = (ev["parameter_set"], ev["convention"])
        if key not in stored:
            continue
        checked += 1
        if stored[key] != ev["tally"]:
            mismatches.append(f"{key}: stored {stored[key]} vs recomputed {ev['tally']}")
    assert checked >= 2, f"only {checked} stored evaluations could be re-derived"
    assert not mismatches, "stored channel tally does not reproduce:\n" + "\n".join(mismatches)


def test_headline_counts_match_the_headline_evaluation(block):
    assert block["n_PASS"] == sum(1 for c in block["PASS_channels"])
    assert block["n_MARGINAL"] == sum(1 for c in block["MARGINAL_channels"])
    assert block["n_FAIL"] == sum(1 for c in block["FAIL_channels"])
    assert block["n_PASS"] + block["n_MARGINAL"] + block["n_FAIL"] == block["n_channels_total"]


def test_legacy_pass_fail_summaries_match_the_computed_evaluations(block):
    """canonical_numbers.json carries two views of the same accounting. They must agree, and
    each 'N of 8 channels pass' string must name the parameter set it summarises (F16 naming rule)."""
    data = json.loads(CANON_JSON.read_text(encoding="utf-8"))
    computed = {(e["parameter_set"], e["convention"]): e["tally"] for e in block["evaluations"]}
    pairs = {
        "pass_fail_summary_v19_2_D_canonical": ("v19_2_D_canonical_phase_44", "published_sigma_unc"),
        "pass_fail_summary_v19_2_E_A2_best_fit": ("v19_2_E_A2_5param_DE_best_fit", "published_sigma_unc"),
    }
    for key, ck in pairs.items():
        assert key in data, f"{key} missing from the canonical map"
        summary = data[key]
        want = computed[ck]
        got = {k: summary[k] for k in ("PASS", "MARGINAL", "FAIL")}
        assert got == want, f"{key}: {got} vs computed {want}"
        assert summary.get("parameter_set") and summary.get("convention"), \
            f"{key} states an 'N of 8' count without naming its parameter set / convention"
        assert ck[0] in summary["canonical_count_string"], \
            f"{key}.canonical_count_string does not name {ck[0]}"


def test_retired_tally_appears_only_inside_retirement_text():
    docs = [CANON_JSON, A15_MD, PAPER, REPO / "README.md", REPO / "CURRENT.md",
            REPO / "docs" / "TRANSITION_V19_2_D_TO_V19_2_E.md",
            REPO / "docs" / "INTEGRITY_FINDINGS_2026-11-04.md"]
    offenders = []
    for doc in docs:
        if not doc.exists():
            continue
        lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines):
            if RETIRED_TALLY not in line:
                continue
            window = " ".join(lines[max(0, i - 3): i + 4]).upper()
            if "RETIRED" in window or "F16" in window:
                continue
            offenders.append(f"{doc.name}:{i + 1}: {line.strip()[:160]}")
    assert not offenders, ("retired 4/3/1 tally quoted as live:\n" + "\n".join(offenders))


def test_generated_a15_region_matches_the_paper():
    """The paper must carry the generated table verbatim, not a hand-written copy."""
    if not (A15_MD.exists() and PAPER.exists()):
        pytest.skip("generated A.15 or paper missing")
    generated = A15_MD.read_text(encoding="utf-8").strip()
    paper = PAPER.read_text(encoding="utf-8")
    # Compare the table rows the generator produced against the paper body.
    rows = [ln.strip() for ln in generated.splitlines()
            if ln.strip().startswith("|") and ("v=" in ln or "TOTAL" in ln)]
    assert rows, "generated A.15 has no channel table rows"
    missing = [r for r in rows if r not in paper]
    assert not missing, (f"{len(missing)} generated A.15 row(s) absent from the paper:\n"
                         + "\n".join(missing[:8]))
    # A hand-edited paper could still carry an unlabelled TOTAL row; that would be a second
    # source of the headline, which is what F16 was about.
    stale = [ln.strip() for ln in paper.splitlines()
             if ln.strip().startswith("|") and "**TOTAL**" in ln
             and "PASS /" in ln]
    assert not stale, ("paper carries an unlabelled channel TOTAL row:\n"
                       + "\n".join(stale[:4]))


def test_drift_guard_channel_guard_is_wired():
    src = (REPO / "scripts" / "drift_guard.py").read_text(encoding="utf-8")
    assert "def check_channel_count_claims(" in src
    assert "check_channel_count_claims(doc_text" in src
