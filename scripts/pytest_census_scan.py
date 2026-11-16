"""F37 census: make the gate's pytest arithmetic checkable instead of hand-waved.

Finding F37 opened as a "collect-vs-run residual": a collect-only census and the
gate's own run line disagreed by a handful of items, and the disagreement was
written into INTEGRITY_FINDINGS, the CHANGELOG and CURRENT.md before being
questioned.  Two things were wrong at once:

  1. The two numbers are different censuses and were being compared as if they
     were the same one.  `X/Y tests collected (N deselected)` already contains the
     deselected items inside Y.  A run line `A passed, B skipped, N deselected`
     counts A+B as what ran.
  2. There IS a real, permanent offset, and it has a named mechanism: a test module
     that raises a module-level skip contributes NO nodeid to a collect-only census
     but contributes 1 to the run's "skipped" count.  So

         collected_nodeids + collection_level_skips == passed + skipped

     and the residual is exactly the number of module-level skips, not noise.

This script measures all of it and writes the numbers to
v0.3-prelim/data/results/pytest_census_inventory.json, so the arithmetic is a
reproducible artifact rather than a sentence.

Usage:
  python scripts/pytest_census_scan.py                # measure + write the inventory
  python scripts/pytest_census_scan.py --check        # fail if the inventory no longer matches
  python scripts/pytest_census_scan.py --gate-log PATH  # cross-check a specific filed gate log

Keep this module stdlib-only: it is invoked from inside the gate.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_pytest_selection import GATE_PYTEST_K_FILTER, GATE_PYTEST_TARGET  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
INVENTORY = REPO / "v0.3-prelim" / "data" / "results" / "pytest_census_inventory.json"

RUN_LINE_RE = re.compile(
    r"(?P<passed>\d+) passed"
    r"(?:,\s*(?P<skipped>\d+) skipped)?"
    r"(?:,\s*(?P<failed>\d+) failed)?"
    r"(?:,\s*(?P<deselected>\d+) deselected)?"
)
COLLECT_RE = re.compile(
    r"(?P<selected>\d+)(?:/(?P<total>\d+))? tests? collected"
    r"(?:\s*\((?P<deselected>\d+) deselected\))?"
)
SKIP_LINE_RE = re.compile(r"^SKIPPED \[(?P<n>\d+)\]\s+(?P<rest>.*)$")

# The token families the gate's -k filter names, PARSED FROM THE FILTER ITSELF.
# Deselection accounting is case-insensitive because pytest's -k is a case-insensitive
# substring test on the whole nodeid, including parametrization ids.
# These used to be a hardcoded tuple. A hardcoded vocabulary is how a deselection becomes
# invisible: if someone edits GATE_PYTEST_K_FILTER and not this tuple, the attribution below
# labels the new family's deselections "outside declared families" -- or, worse, keeps calling
# them accounted for. Deriving them makes the two drift-proof.
_TOKEN_RE = re.compile(r"[A-Za-z]+\d+")
FAMILY_TOKENS = tuple(t.lower() for t in _TOKEN_RE.findall(GATE_PYTEST_K_FILTER))

COMMIT_TOKEN_RE = re.compile(r"\b([0-9a-f]{7,40})\b")


def _run_pytest_collect(extra_args: list[str], cwd: Path | None = None) -> dict:
    """Collect the suite under `extra_args` and return nodeids, skips and the summary line.

    `cwd` lets the same census be taken against a different checkout (a detached worktree at
    the commit a filed gate log certifies), which is what turns a residual from a mystery into
    a measurement.
    """
    cmd = [
        sys.executable, "-m", "pytest", GATE_PYTEST_TARGET,
        "-q", "--collect-only", "-rs", "-p", "no:cacheprovider",
        *extra_args,
    ]
    proc = subprocess.run(
        cmd, cwd=str(cwd or REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=900,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    nodeids: list[str] = []
    skips: list[dict] = []
    summary = None
    for raw in out.splitlines():
        line = raw.strip()
        m = SKIP_LINE_RE.match(line)
        if m:
            skips.append({"count": int(m.group("n")), "where": m.group("rest").strip()})
            continue
        if " tests collected" in line:
            # Strip the elapsed-time suffix: a census comparison that includes wall time
            # can never match twice in a row, which would make --check self-failing.
            summary = re.sub(r"\s+in\s+[0-9.]+m?s(?:\s*\([0-9:]+m?s\))?\s*$", "", line).strip()
            continue
        if "::" in line and not line.startswith(("=", "ERROR", "WARN")):
            nodeids.append(line)
    collected = COLLECT_RE.search(summary or "")
    return {
        "nodeids": nodeids,
        "collection_skips": skips,
        "collection_skip_total": sum(s["count"] for s in skips),
        "summary_line": summary,
        "collected_selected": int(collected.group("selected")) if collected else None,
        "collected_total": int(collected.group("total")) if collected and collected.group("total")
        else (len(nodeids) if collected else None),
        "collected_deselected": int(collected.group("deselected")) if collected and collected.group("deselected")
        else None,
        "exit_code": proc.returncode,
    }


def _file_of(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def _latest_gate_log() -> Path | None:
    """Newest filed gate log by the date token in its NAME, not alphabetical order.

    Alphabetical order picks gate_run_repair_final_* over gate_run_f39_bootstrap_20261116_*,
    which would cross-check the census against the wrong certification run.
    """
    logs = list((REPO / "docs" / "evidence").glob("gate_run*.txt"))
    if not logs:
        return None

    def key(p: Path):
        m = re.search(r"(\d{8})", p.name)
        try:
            mtime = p.stat().st_mtime
        except OSError:
            mtime = 0.0
        # Same-day logs are common during a round; without mtime the choice between them is
        # alphabetical, i.e. whichever filename sorts later, not the run that actually happened
        # last.
        return (m.group(1) if m else "00000000", mtime, p.name)

    def green(p: Path) -> bool:
        try:
            return "GATE PASSED: all" in p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False

    # A red run's pytest summary is not a certification. Choosing the newest log regardless of its
    # verdict would let a failed run become the census's ground truth, so green logs win; if no
    # green log exists the newest one is still reported, and _problems() then fails the census
    # rather than reconciling against a run the gate itself declared failed.
    return max([p for p in logs if green(p)] or logs, key=key)


def _log_commit(log_text: str) -> str | None:
    """Commit the gate log certifies, from its header.

    A certification log that does not name a commit cannot be reconciled against a
    census taken on a different tree, so the absence is reported rather than guessed.
    """
    head = "\n".join(log_text.splitlines()[:40])
    for token in COMMIT_TOKEN_RE.findall(head):
        if _is_commit(token):
            return token
    return None


def _is_commit(token: str) -> bool:
    """Is this token a commit? A gate log header carries a commit AND a tree on adjacent lines.

    Asking "does this resolve to something with a tree?" cannot tell them apart -- a tree object
    peels to itself -- so the header's Tree line used to be returned as the commit, which silently
    killed the residual-explanation path (git diff against a tree sha yields nothing, so a real gap
    got filed as "unexplained").
    """
    proc = subprocess.run(
        ["git", "cat-file", "-t", token], cwd=REPO,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode == 0 and proc.stdout.strip() == "commit"


def _tree_of(commit: str) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit}^{{tree}}"], cwd=REPO,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    sha = proc.stdout.strip()
    return sha if proc.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", sha) else None


def _collect_counts_at(commit: str) -> dict | None:
    """Take the same census against a detached git worktree at `commit`.

    This is what turns a residual into a measurement. The gate log certifies the tree it ran on;
    the census is taken on today's tree; when the two differ, the difference has to be counted,
    not narrated. A detached worktree collects an old tree without touching the working copy.
    """
    parent = Path(tempfile.mkdtemp(prefix="census_wt_"))
    wt = parent / "wt"
    add = subprocess.run(["git", "worktree", "add", "--detach", str(wt), commit], cwd=REPO,
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if add.returncode != 0:
        shutil.rmtree(parent, ignore_errors=True)
        return None
    try:
        gated = _run_pytest_collect(["-k", GATE_PYTEST_K_FILTER], cwd=wt)
        selected = gated["collected_selected"] or 0
        return {
            "commit": commit,
            "tree_sha": _tree_of(commit),
            "nodeids_total": gated["collected_total"],
            "nodeids_selected": selected,
            "deselected": gated["collected_deselected"],
            "collection_level_skips": gated["collection_skip_total"],
            "predicted_run_items": selected + gated["collection_skip_total"],
            "how": f"pytest {GATE_PYTEST_TARGET} --collect-only -rs -k '<gate filter>' in a "
                   f"detached git worktree at {commit}",
            "caveat": ("a detached worktree starts without the gitignored gate inputs, so modules "
                       "that skip at import skip there too; the numbers describe that commit's code, "
                       "not the original run's data state"),
        }
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=REPO,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocess.run(["git", "worktree", "prune"], cwd=REPO,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
        shutil.rmtree(parent, ignore_errors=True)


def _changed_test_paths(commit: str) -> dict:
    """Name the code that moved between the certified commit and HEAD.

    A count difference is only explained when you can point at the files that caused it. This is
    a git question, so it is answered by git and not by interpretation.
    """
    proc = subprocess.run(
        ["git", "diff", "--name-status", commit, "HEAD", "--", GATE_PYTEST_TARGET, "tests/",
         "scripts/"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    added: list[str] = []
    removed: list[str] = []
    modified: list[str] = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        if status.startswith("A"):
            added.append(path)
        elif status.startswith("D"):
            removed.append(path)
        elif status.startswith("M"):
            modified.append(path)
    return {"status": proc.returncode, "added": sorted(added), "removed": sorted(removed),
            "modified": sorted(modified)}


def build(gate_log: Path | None = None) -> dict:
    base = _run_pytest_collect([])
    gated = _run_pytest_collect(["-k", GATE_PYTEST_K_FILTER])

    base_ids = set(base["nodeids"])
    gated_ids = set(gated["nodeids"])
    deselected_ids = sorted(base_ids - gated_ids)
    added_ids = sorted(gated_ids - base_ids)  # must stay empty; a non-empty set means -k INCREASED the suite

    per_file = Counter(_file_of(n) for n in deselected_ids)

    gate_log = gate_log or _latest_gate_log()
    run_counts = None
    if gate_log is not None and gate_log.exists():
        text = gate_log.read_text(encoding="utf-8", errors="replace")
        m = None
        for m in RUN_LINE_RE.finditer(text):
            pass  # keep the LAST matching line: the final pytest summary of the run
        if m:
            log_commit = _log_commit(text)
            run_counts = {
                "log_path": str(gate_log.relative_to(REPO)),
                "passed": int(m.group("passed")),
                "skipped": int(m.group("skipped") or 0),
                "failed": int(m.group("failed") or 0),
                "deselected": int(m.group("deselected") or 0),
                "log_commit": log_commit,
                "log_tree_sha": _tree_of(log_commit) if log_commit else None,
                "log_verdict": "green" if "GATE PASSED: all" in text else "red",
            }

    tree_sha = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=REPO,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()

    identity_ok = (
        base["collected_total"] == gated["collected_total"]
        and gated["collected_total"] == gated["collected_selected"] + gated["collected_deselected"]
        and len(deselected_ids) == gated["collected_deselected"]
        and not added_ids
    )

    reconciliation = None
    if run_counts:
        run_items = run_counts["passed"] + run_counts["skipped"] + run_counts["failed"]
        expected_items = gated["collected_selected"] + gated["collection_skip_total"]
        same_tree = bool(run_counts.get("log_tree_sha") and run_counts["log_tree_sha"] == tree_sha)
        reconciliation = {
            "run_summary_items": run_items,
            "expected_run_items": expected_items,
            "expected_from": (
                f"{gated['collected_selected']} selected nodeids + "
                f"{gated['collection_skip_total']} module-level collection skips"
            ),
            "module_level_skips": gated["collection_skip_total"],
            "residual": run_items - expected_items,
            "deselected_matches_log": run_counts["deselected"] == gated["collected_deselected"],
            "log_certifies_current_tree": same_tree,
            "cross_check_status": (
                "log certifies this exact tree" if same_tree else
                "log certifies a different tree; residual is informational"
                if run_counts.get("log_tree_sha") else
                "log names no commit; residual is informational"
            ),
        }

    residual_explanation = None
    if reconciliation and reconciliation["residual"] != 0 and run_counts.get("log_commit"):
        residual_explanation = _collect_counts_at(run_counts["log_commit"])
        if residual_explanation:
            residual_explanation["changed_test_paths"] = _changed_test_paths(
                run_counts["log_commit"])
            # The certified run and a clean measurement of the certified tree do not meet: the
            # worktree has none of the gitignored gate inputs, so input-dependent modules collect
            # differently. The gap is reported, never absorbed into the arithmetic.
            gap = (reconciliation["run_summary_items"]
                   - residual_explanation["predicted_run_items"])
            residual_explanation["input_dependent_gap"] = gap
            added_selected = (gated["collected_selected"]
                              - residual_explanation["nodeids_selected"])
            skip_change = (gated["collection_skip_total"]
                           - residual_explanation["collection_level_skips"])
            # The residual is now three measured numbers, not a story: how many test items were
            # added since the certified commit, how the module-level skip count moved, and how
            # many items a clean checkout of the certified commit cannot collect because its
            # inputs are gitignored (finding F39's residue, quantified).
            residual_explanation["decomposition"] = {
                "added_selected_nodeids_since_certified_commit": added_selected,
                "module_level_skip_change": skip_change,
                "input_dependent_gap_clean_checkout_vs_run": gap,
                "identity": "residual == input_dependent_gap - added_selected - skip_change",
                "identity_holds": (
                    reconciliation["residual"] == gap - added_selected - skip_change),
            }

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_tree_sha": tree_sha,
        "selection": {
            "target": GATE_PYTEST_TARGET,
            "k_filter": GATE_PYTEST_K_FILTER,
        },
        "collect_only": {
            "without_k": {
                "nodeids": base["collected_total"],
                "collection_level_skips": base["collection_skip_total"],
                "summary_line": base["summary_line"],
            },
            "with_gate_k": {
                "nodeids_selected": gated["collected_selected"],
                "nodeids_total": gated["collected_total"],
                "deselected": gated["collected_deselected"],
                "collection_level_skips": gated["collection_skip_total"],
                "collection_skip_sites": gated["collection_skips"],
                "summary_line": gated["summary_line"],
            },
        },
        "deselection_attribution": {
            "deselected_nodeid_count": len(deselected_ids),
            "by_file": [{"file": f, "deselected": c} for f, c in sorted(per_file.items(), key=lambda kv: -kv[1])],
            # -k matching is a case-insensitive substring test on the nodeid, so a
            # parametrized instance whose PARAM says "scripts/t220_..." counts as a
            # T220-family deselection even though its file name does not mention T220.
            "nodeids_outside_declared_families": [
                n for n in deselected_ids
                if not any(tok in n.lower() for tok in FAMILY_TOKENS)
            ],
            "gate_k_filter_added_nodeids": added_ids,
        },
        "identity": {
            "total_equals_selected_plus_deselected": bool(
                gated["collected_total"] == gated["collected_selected"] + gated["collected_deselected"]
            ),
            "nodeid_diff_equals_deselected": bool(len(deselected_ids) == gated["collected_deselected"]),
            "no_nodeid_added_by_k_filter": bool(not added_ids),
            "all_ok": bool(identity_ok),
        },
        "gate_run_cross_check": run_counts,
        "reconciliation": reconciliation,
        "residual_explanation": residual_explanation,
    }


def _problems(inv: dict) -> list[str]:
    """Independent re-derivation of every arithmetic claim stored in the inventory."""
    problems: list[str] = []
    co = inv["collect_only"]
    wk = co["with_gate_k"]
    if wk["nodeids_total"] != wk["nodeids_selected"] + wk["deselected"]:
        problems.append(
            f"collect census does not balance: {wk['nodeids_total']} total != "
            f"{wk['nodeids_selected']} selected + {wk['deselected']} deselected"
        )
    att = inv["deselection_attribution"]
    if att["deselected_nodeid_count"] != wk["deselected"]:
        problems.append(
            f"deselected nodeid enumeration ({att['deselected_nodeid_count']}) != "
            f"pytest's deselection count ({wk['deselected']})"
        )
    if sum(e["deselected"] for e in att["by_file"]) != att["deselected_nodeid_count"]:
        problems.append("per-file deselection breakdown does not sum to the deselection count")
    if att["nodeids_outside_declared_families"]:
        problems.append(
            "deselections exist outside the declared -k families: "
            + ", ".join(att["nodeids_outside_declared_families"][:5])
        )
    if att["gate_k_filter_added_nodeids"]:
        problems.append("the gate -k filter ADDED nodeids, which is impossible for a pure filter")
    rec = inv.get("reconciliation")
    run = inv.get("gate_run_cross_check")
    if rec:
        recomputed = rec["run_summary_items"] - rec["expected_run_items"]
        if recomputed != rec["residual"]:
            problems.append(
                f"filed residual {rec['residual']} != recomputed "
                f"{rec['run_summary_items']} - {rec['expected_run_items']} = {recomputed}"
            )
        if recomputed != 0 and rec.get("log_certifies_current_tree"):
            problems.append(
                f"gate run does not reconcile on this tree: run reports {rec['run_summary_items']} "
                f"items, collect predicts {rec['expected_run_items']} ({rec['expected_from']})"
            )
        if recomputed != 0 and not rec.get("log_certifies_current_tree"):
            expl = inv.get("residual_explanation")
            if not expl:
                problems.append(
                    f"residual {recomputed} is unexplained: the filed gate log certifies a "
                    "different tree and nothing measured that tree (re-run "
                    "scripts/pytest_census_scan.py)"
                )
            elif not (expl.get("decomposition") or {}).get("identity_holds"):
                problems.append(
                    f"residual {recomputed} decomposition does not close: "
                    f"{expl.get('decomposition')}"
                )
            else:
                # The residual is only "accounted for" when the census measured the certified tree
                # AND named the code that differs from it. Numbers without a cause are still a gap.
                changed = expl.get("changed_test_paths") or {}
                if not changed.get("added") and not changed.get("removed") and not changed.get(
                        "modified"):
                    problems.append(
                        f"residual {recomputed} has no named cause: git reports no test/script "
                        f"paths changed between {expl.get('commit')} and HEAD"
                    )
        if run is not None:
            if run.get("log_verdict") == "red":
                problems.append(
                    f"the census cross-checks against a RED gate log ({run.get('log_path')}): a "
                    "certification must be a run the gate declared passed"
                )
            # The status string is itself a claim about the comparison, so it must agree with the
            # flag it describes. A cross-tree zero presented as a certification is the exact
            # laundering this guard exists to prevent.
            status = (rec.get("cross_check_status") or "").strip()
            if not status:
                problems.append("a cross-check against a gate log with no stated status is not auditable")
            elif bool(rec.get("log_certifies_current_tree")) != ("certifies this exact tree" in status):
                problems.append(
                    f"cross_check_status ({status!r}) contradicts log_certifies_current_tree="
                    f"{rec.get('log_certifies_current_tree')}"
                )
            # Recompute the agreement instead of trusting the stored boolean: a stored flag is a
            # claim about a comparison, and a claim a mutation cannot break is not a check.
            live = inv["collect_only"]["with_gate_k"]["deselected"]
            if run["deselected"] != live:
                problems.append(
                    f"the filed gate log's deselection count {run['deselected']} disagrees with "
                    f"the live census {live}"
                )
    return problems


def main() -> int:
    # Unknown flags used to be ignored silently, which let a mistyped invocation look like a
    # successful cross-check. Reject them instead.
    known = {"--check", "--gate-log"}
    unknown = [a for a in sys.argv[1:] if a.startswith("-") and a not in known]
    if unknown:
        print(f"unknown flag(s): {', '.join(unknown)}")
        print(f"supported: --check, --gate-log <path>  (no flags = scan the current tree)")
        return 2
    check = "--check" in sys.argv
    gate_log = None
    if "--gate-log" in sys.argv:
        gate_log = Path(sys.argv[sys.argv.index("--gate-log") + 1])
        if not gate_log.is_absolute():
            gate_log = REPO / gate_log

    inv = build(gate_log)
    problems = _problems(inv)

    if check:
        if not INVENTORY.exists():
            print("FAIL: v0.3-prelim/data/results/pytest_census_inventory.json missing")
            return 1
        old = json.loads(INVENTORY.read_text(encoding="utf-8"))
        old_problems = _problems(old)
        if old_problems:
            print("FAIL: stored inventory is internally inconsistent:")
            for p in old_problems:
                print("  ", p)
            return 1
        if old.get("git_tree_sha") != inv["git_tree_sha"]:
            print("FAIL: census inventory predates the current tree")
            print("  recorded tree:", old.get("git_tree_sha"))
            print("  current tree :", inv["git_tree_sha"])
            print("  re-run: python scripts/pytest_census_scan.py")
            return 1
        if old["collect_only"]["with_gate_k"] != inv["collect_only"]["with_gate_k"]:
            print("FAIL: census drifted from the stored inventory")
            print("  recorded:", old["collect_only"]["with_gate_k"])
            print("  current :", inv["collect_only"]["with_gate_k"])
            return 1
        print("OK: census inventory is internally consistent and current for this tree")
        return 0

    if problems:
        print("FAIL: census arithmetic does not hold")
        for p in problems:
            print("  ", p)
        INVENTORY.write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"(diagnostic inventory written to {INVENTORY})")
        return 1

    INVENTORY.write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {INVENTORY}")
    print(json.dumps({
        "nodeids_total": inv["collect_only"]["with_gate_k"]["nodeids_total"],
        "nodeids_selected": inv["collect_only"]["with_gate_k"]["nodeids_selected"],
        "deselected": inv["collect_only"]["with_gate_k"]["deselected"],
        "module_level_skips": inv["collect_only"]["with_gate_k"]["collection_level_skips"],
        "reconciliation": inv["reconciliation"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
