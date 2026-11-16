"""F37 pin: the gate's pass/skip/deselect arithmetic must reconcile, and say how.

F37 was a *reported* test count whose composition nobody could re-derive: the certified gate log
says "3724 passed / 25 skipped / 40 deselected", and a bare `pytest --collect-only` says a
different number. Both were true, and neither explained the other. Two mechanisms carry the
difference and neither is a bug:

1. `-k` is a case-insensitive substring test on the whole nodeid, including parametrization ids.
   A parametrized case inside a file with a perfectly ordinary name is deselected when its PARAM
   string contains a family token (e.g. a param naming `scripts/t220_...`), so a deselection can
   appear in a file the `-k` filter never mentions.
2. Test modules that raise `pytest.skip(..., allow_module_level=True)` at import contribute zero
   nodeids to a collection -- there is no test item to collect -- but contribute one row each to
   the run's skipped count. So `selected nodeids` alone under-counts the run by the number of
   module-level skip sites (108 on this tree).

scripts/pytest_census_scan.py measures all of it and files the numbers to
v0.3-prelim/data/results/pytest_census_inventory.json. This test re-derives every arithmetic
claim in that inventory and proves the checker can fail.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import gate_pytest_selection as gate  # noqa: E402
import pytest_census_scan as census  # noqa: E402

INVENTORY_PATH = REPO / "v0.3-prelim/data/results/pytest_census_inventory.json"


def _inventory() -> dict:
    if not INVENTORY_PATH.exists():
        pytest.skip(
            f"{INVENTORY_PATH.relative_to(REPO)} not filed yet; run "
            "python scripts/pytest_census_scan.py"
        )
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ the arithmetic
def test_collect_census_balances():
    inv = _inventory()
    wk = inv["collect_only"]["with_gate_k"]
    assert wk["nodeids_total"] == wk["nodeids_selected"] + wk["deselected"], wk
    assert inv["collect_only"]["without_k"]["nodeids"] == wk["nodeids_total"], (
        "the -k filter changed the number of collectible nodeids; a filter may only subtract"
    )


def test_run_and_collect_reconcile_or_the_gap_is_measured():
    """The whole point of F37: run items == selected nodeids + module-level collection skips.

    Zero residual on the certified tree is the ideal. When the census runs on a newer tree than
    the log certifies, a non-zero residual is acceptable ONLY if the census measured the certified
    tree as well and the two counts meet: an unmeasured gap is what made the original test count
    un-re-derivable.
    """
    inv = _inventory()
    rec = inv.get("reconciliation")
    assert rec, "no gate log was cross-checked, so the run side of the census is unmeasured"
    assert rec["residual"] == rec["run_summary_items"] - rec["expected_run_items"], rec
    assert rec["module_level_skips"] > 0, (
        "a census with zero module-level skips cannot explain the skipped count; check the scan"
    )
    if rec["log_certifies_current_tree"]:
        assert rec["residual"] == 0, rec
    else:
        if rec["residual"] == 0:
            # Cross-tree and numerically equal: there is no gap, so demanding an explanation would
            # assert a shape rather than a property (the defect that made this test fail on
            # d8f1845). What must still hold is that the zero is labelled as what it is -- a
            # comparison against a log that ran somewhere else -- and that a real run is behind it.
            assert inv.get("gate_run_cross_check"), (
                f"a zero residual with no gate log behind it is not a measurement: {rec}")
            assert "certifies this exact tree" not in rec["cross_check_status"], (
                f"a cross-tree zero is being presented as a certification: {rec['cross_check_status']}")
            return
        expl = inv.get("residual_explanation")
        assert expl, f"residual {rec['residual']} is filed with no measurement behind it: {rec}"
        assert len(expl["tree_sha"]) == 40, expl
        # The certified tree was collected, not guessed: its own numbers have to add up.
        assert expl["predicted_run_items"] == (
            expl["nodeids_selected"] + expl["collection_level_skips"]), expl
        # The clean measurement of the certified tree and the run that happened there do not meet,
        # and that is a property of the suite, not of the census: a detached checkout has none of
        # the gitignored gate inputs, so input-dependent modules collect differently. The size of
        # that gap is filed as a number so nobody has to take "it's just the data" on faith.
        gap = rec["run_summary_items"] - expl["predicted_run_items"]
        assert expl.get("input_dependent_gap") == gap, (expl, rec, gap)
        # The residual is three measured numbers and they have to add up.
        dec = expl["decomposition"]
        assert dec["identity_holds"], dec
        assert rec["residual"] == (
            dec["input_dependent_gap_clean_checkout_vs_run"]
            - dec["added_selected_nodeids_since_certified_commit"]
            - dec["module_level_skip_change"]), (rec, dec)
        # A gap with no named cause is still a gap.
        changed = expl.get("changed_test_paths") or {}
        assert changed.get("added") or changed.get("removed") or changed.get("modified"), (
            f"residual {rec['residual']} is attributed to nothing: {expl}"
        )


def test_log_header_parser_returns_the_commit_not_the_tree():
    """The gate log header names a commit and a tree on adjacent lines; the parser must not confuse them.

    Falsified on the live headers: taking the tree as the commit makes `git diff` return nothing,
    and a real census gap is then filed as having no cause.
    """
    log = _inventory().get("gate_run_cross_check") or {}
    commit = log.get("log_commit")
    assert commit, "the cross-checked gate log names no resolvable commit"
    assert census._is_commit(commit), f"log_commit {commit} is not a commit object"
    assert not census._is_commit(log["log_tree_sha"]), "a tree sha must not parse as a commit"
    # Both header tokens live in the same 40-line window; the parser has to pick the commit one.
    text = Path(log["log_path"]).read_text(encoding="utf-8", errors="replace")
    head_tokens = census.COMMIT_TOKEN_RE.findall("\n".join(text.splitlines()[:40]))
    assert commit in head_tokens
    trees = [t for t in head_tokens if not census._is_commit(t)]
    assert trees, "expected the header to also carry a tree sha"
    assert census._log_commit(text) == commit


def test_the_certifying_gate_log_names_a_resolvable_commit():
    """An evidence log attached to no tree cannot certify anything (found by this guard)."""
    inv = _inventory()
    log = inv.get("gate_run_cross_check")
    assert log and log.get("log_path"), inv
    assert log.get("log_commit"), (
        f"{log.get('log_path')} certifies no commit; add 'Commit under certification: <sha>' "
        "to the log header"
    )
    assert log.get("log_tree_sha") and len(log["log_tree_sha"]) == 40, log


def test_the_cross_checked_log_is_a_green_certification():
    """The census's ground truth has to be a run the gate declared passed.

    A red run produces a perfectly well-formed pytest summary line; reconciling against one would
    make a failed build the reference the suite is measured against.
    """
    log = _inventory().get("gate_run_cross_check") or {}
    assert log, "no gate log named by the census"
    assert log.get("log_verdict") == "green", (
        f"the census is cross-checked against a {log.get('log_verdict')} run: {log.get('log_path')}")


def test_module_level_skip_sites_are_named_not_just_counted():
    inv = _inventory()
    sites = inv["collect_only"]["with_gate_k"]["collection_skip_sites"]
    count = inv["collect_only"]["with_gate_k"]["collection_level_skips"]
    assert sites, "the skip sites must be listed; a bare count is not falsifiable"
    assert sum(s.get("count", 1) for s in sites) == count, (sum(s.get("count", 1) for s in sites), count)


def test_every_deselection_belongs_to_a_declared_k_family():
    """No deselection may be unexplained -- that was the residue F37 could not account for."""
    inv = _inventory()
    att = inv["deselection_attribution"]
    assert att["nodeids_outside_declared_families"] == [], att["nodeids_outside_declared_families"][:5]
    assert att["gate_k_filter_added_nodeids"] == [], att["gate_k_filter_added_nodeids"][:5]
    assert sum(e["deselected"] for e in att["by_file"]) == att["deselected_nodeid_count"]


def test_census_family_vocabulary_cannot_drift_from_the_gate_filter():
    """If someone edits the gate's -k filter, an unmaintained attribution vocabulary would quietly
    mislabel the deselections it no longer matches."""
    inv = _inventory()
    assert inv["selection"]["k_filter"] == gate.GATE_PYTEST_K_FILTER, (
        f"filed census used {inv['selection']['k_filter']!r} but the gate now uses "
        f"{gate.GATE_PYTEST_K_FILTER!r}; re-run scripts/pytest_census_scan.py"
    )
    # The gate filter is an exclusion filter ("not T132 and not T131 ..."), so tokens are parsed
    # as identifier-shaped runs, not by splitting on a connective.
    import re as _re
    filter_tokens = {t.lower() for t in _re.findall(r"[A-Za-z]+\d+", gate.GATE_PYTEST_K_FILTER)}
    assert filter_tokens, gate.GATE_PYTEST_K_FILTER
    assert filter_tokens == {t.lower() for t in census.FAMILY_TOKENS}, (
        f"the census attributes deselections to {sorted(census.FAMILY_TOKENS)} while the gate "
        f"filter names {sorted(filter_tokens)}"
    )


def test_census_is_tied_to_a_tree_and_says_which_one():
    inv = _inventory()
    assert len(inv["git_tree_sha"]) == 40, inv["git_tree_sha"]
    rec = inv.get("reconciliation") or {}
    log = inv.get("gate_run_cross_check") or {}
    if log.get("log_commit"):
        assert len(log["log_commit"]) >= 7, log["log_commit"]
        assert rec.get("cross_check_status"), "a cross-check with no stated status is not auditable"
        assert (log.get("log_certifies_current_tree") is None) or ("certifies" in rec["cross_check_status"])
    Path(log["log_path"]) if log.get("log_path") else pytest.skip("no gate log named")


# ------------------------------------------------------------------ falsification
@pytest.mark.parametrize("mutate,expect_substring", [
    ("unbalance_collect", "does not balance"),
    ("hide_an_unattributed_deselection", "outside the declared -k families"),
    ("residual_on_certified_tree", "does not reconcile"),
    ("log_deselection_disagrees", "disagrees with the live census"),
    ("per_file_breakdown_wrong", "does not sum"),
    ("drop_the_residual_explanation", "unexplained"),
    ("residual_with_no_named_cause", "no named cause"),
    ("break_the_residual_decomposition", "decomposition does not close"),
    ("launder_a_cross_tree_zero_as_certification", "contradicts log_certifies_current_tree"),
    ("drop_the_cross_check_status", "no stated status"),
    ("cross_check_against_a_red_log", "RED gate log"),
])
def test_census_checker_fails_when_the_arithmetic_is_wrong(mutate, expect_substring):
    """Every claim the census files must be one the checker can break."""
    inv = _inventory()
    problems_before = census._problems(copy.deepcopy(inv))
    assert problems_before == [], f"the filed census already fails: {problems_before}"

    m = copy.deepcopy(inv)
    wk = m["collect_only"]["with_gate_k"]
    if mutate == "unbalance_collect":
        wk["deselected"] += 1
    elif mutate == "hide_an_unattributed_deselection":
        att = m["deselection_attribution"]
        att["nodeids_outside_declared_families"] = ["some/test.py::test_case[unfamily_token]"]
    elif mutate == "residual_on_certified_tree":
        # Numbers that agree with each other but not with the suite: the arithmetic check cannot
        # see them, only the reconciliation rule can.
        m["reconciliation"]["run_summary_items"] = m["reconciliation"]["expected_run_items"] + 3
        m["reconciliation"]["residual"] = 3
        m["reconciliation"]["log_certifies_current_tree"] = True
    elif mutate == "log_deselection_disagrees":
        m["gate_run_cross_check"]["deselected"] += 5
    elif mutate == "per_file_breakdown_wrong":
        att = m["deselection_attribution"]
        if att["by_file"]:
            att["by_file"][0]["deselected"] += 2
    elif mutate == "cross_check_against_a_red_log":
        # Only the log's verdict is forged; the arithmetic is left intact, so this case cannot
        # hide behind the residual branch.
        m["gate_run_cross_check"]["log_verdict"] = "red"
    elif mutate == "_no_such_mutation_sentinel":  # unreachable: keeps the chain shape explicit
        raise AssertionError("sentinel")
    elif mutate in ("drop_the_residual_explanation", "residual_with_no_named_cause",
                    "break_the_residual_decomposition",
                    "launder_a_cross_tree_zero_as_certification", "drop_the_cross_check_status"):
        # Force a cross-tree residual, then remove the thing that makes it accountable.
        m["reconciliation"]["run_summary_items"] += 7
        m["reconciliation"]["residual"] = (
            m["reconciliation"]["run_summary_items"] - m["reconciliation"]["expected_run_items"])
        m["reconciliation"]["log_certifies_current_tree"] = False
        # expl is a copy that always exists, because a filed census with a zero
        # residual legitimately has no explanation at all and the mutation must still be able to
        # invent one.
        expl = dict(m.get("residual_explanation") or {})
        expl.setdefault("commit", "c" * 40)
        expl.setdefault("tree_sha", "d" * 40)
        expl.setdefault("nodeids_selected", m["collect_only"]["with_gate_k"]["nodeids_selected"])
        expl.setdefault("collection_level_skips",
                        m["collect_only"]["with_gate_k"]["collection_level_skips"])
        expl.setdefault("predicted_run_items",
                        expl["nodeids_selected"] + expl["collection_level_skips"])
        if mutate == "drop_the_residual_explanation":
            m["residual_explanation"] = None
        else:
            if mutate == "residual_with_no_named_cause":
                expl["changed_test_paths"] = {"status": 0, "added": [], "removed": [],
                                              "modified": []}
                # Supply a decomposition that closes. Without it the checker reports the
                # decomposition problem and stops, so this case would test a different branch
                # than the one it claims to test -- a falsification that falsifies nothing.
                gap = m["reconciliation"]["residual"]
                expl["decomposition"] = {
                    "input_dependent_gap_clean_checkout_vs_run": gap,
                    "added_selected_nodeids_since_certified_commit": 0,
                    "module_level_skip_change": 0,
                    "identity_holds": True,
                }
            elif mutate == "break_the_residual_decomposition":
                dec = dict(expl.get("decomposition") or {})
                dec["identity_holds"] = False
                dec["module_level_skip_change"] = int(dec.get("module_level_skip_change", 0)) + 9
                expl["decomposition"] = dec
            elif mutate == "launder_a_cross_tree_zero_as_certification":
                # The arithmetic is untouched; only the LABEL on the comparison is forged: a log
                # that ran on another tree is described as certifying this one.
                rec = m["reconciliation"]
                rec["log_certifies_current_tree"] = False
                rec["cross_check_status"] = "log certifies this exact tree"
            elif mutate == "drop_the_cross_check_status":
                m["reconciliation"]["cross_check_status"] = ""
            else:
                raise AssertionError(
                    f"mutation {mutate!r} is in the parametrize table but has no body: it would "
                    "fabricate nothing and the falsification would test nothing")
            m["residual_explanation"] = expl

    else:
        raise AssertionError(
            f"mutation {mutate!r} appears in the parametrize table but has no body: it fabricates "
            "nothing, so the falsification would prove nothing (last round's defect, reproduced "
            "here rather than rediscovered)")

    problems = census._problems(m)
    assert problems, f"the checker accepted a fabricated census ({mutate})"
    assert any(expect_substring in p for p in problems), (mutate, problems)
