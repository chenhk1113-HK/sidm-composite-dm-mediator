"""Guards for the F39 bootstrap manifest and for the scan scope that F39 exposed.

Two classes of defect are pinned here.

(1) A manifest is only useful if it is falsified. F36/F38/F40 were all guards that asserted how
    things are WRITTEN instead of what they DO; each passed while its invariant was broken, or
    broke on its own bookkeeping. So this file does not merely restate the manifest -- it feeds the
    integrity checker a fabricated entry and requires it to fail. A checker that never fails has
    no evidential value.

(2) scripts/fH_pairing_registry.py filtered SKIP_DIRS against ABSOLUTE path parts. Any checkout
    that itself lives under a directory named scratch/archive/deprecated -- a CI runner, a clone
    parked in a scratch area -- produced an EMPTY registry, and the drift guards then reported the
    artifact as stale. The 53806dd fresh-clone run is the proof (docs/evidence/
    clone_run_53806dd_20261115.txt). These tests reproduce the failure mode without needing a clone.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent.parent  # v0.3-prelim/tests -> repository root
sys.path.insert(0, str(REPO / "scripts"))

import bootstrap_gate_inputs as boot  # noqa: E402
import fH_pairing_registry as producer  # noqa: E402


# ---------------------------------------------------------------- manifest integrity
def test_manifest_declares_inputs_and_producers():
    assert boot.MANIFEST, "the manifest is empty, so it certifies nothing"
    names = [gi.name for gi in boot.MANIFEST]
    assert len(names) == len(set(names)), "duplicate manifest entries"
    for gi in boot.MANIFEST:
        assert gi.targets, f"{gi.name} declares no target path"
        assert gi.note, f"{gi.name} has no explanation of why the input is missing from git"
        assert gi.kind in {boot.KIND_REPO_BUILT, boot.KIND_FETCH,
                           boot.KIND_HOST_PINNED, boot.KIND_LONG_RUN}, gi.kind


def test_declared_producers_exist_and_targets_are_ignored():
    """The same invariant scripts/bootstrap_gate_inputs.py --require enforces, seen from pytest."""
    problems = []
    for gi in boot.MANIFEST:
        if gi.kind == boot.KIND_HOST_PINNED:
            continue
        assert gi.build is not None or gi.long_run, f"{gi.name} has no producer and is not long-running"
        if gi.build:
            producer_path = REPO / gi.build[-1]
            if not producer_path.exists():
                problems.append(f"{gi.name}: producer {gi.build[-1]} does not exist")
    assert not problems, problems


def test_integrity_checker_rejects_a_fabricated_entry():
    """Falsification: a producer that does not exist must make --require fail, not be forgiven."""
    bogus = boot.GateInput(
        name="falsification_entry",
        kind=boot.KIND_REPO_BUILT,
        targets=[REPO / "v0.3-prelim/outputs/definitely_not_produced.json"],
        build=[sys.executable, "scripts/no_such_producer_anywhere.py"],
        note="injected by test to prove the checker is not vacuous",
    )
    original = boot.MANIFEST
    try:
        boot.MANIFEST = list(original) + [bogus]
        assert boot.require() == 1, "integrity checker accepted a manifest entry with no producer"
    finally:
        boot.MANIFEST = original


def test_fabricated_target_outside_git_ignore_is_caught():
    """A target that is neither gitignored nor present is a lie about where the input lives."""
    bogus = boot.GateInput(
        name="falsification_tracked_target",
        kind=boot.KIND_REPO_BUILT,
        targets=[REPO / "README.md"],          # tracked, therefore not a git-ignored input
        build=[sys.executable, "scripts/no_such_producer_anywhere.py"],
        note="injected by test",
    )
    original = boot.MANIFEST
    try:
        boot.MANIFEST = [bogus]
        assert boot.require() == 1
    finally:
        boot.MANIFEST = original


def test_host_pinned_inputs_admit_they_are_not_reproducible():
    """The honest half of F39: some inputs no bootstrap can rebuild. The manifest must say so."""
    pinned = [gi for gi in boot.MANIFEST if gi.kind == boot.KIND_HOST_PINNED]
    assert pinned, "the manifest claims every input is rebuildable -- the clone run disproved that"
    for gi in pinned:
        assert gi.build is None, f"{gi.name} claims a producer for data outside the repository"
        assert "not" in gi.note.lower(), f"{gi.name} does not state that it is not reproducible"


def test_guard_required_paper_has_a_tracked_fetcher():
    """The specific gap the 53806dd clone run hit: a guard asserts on a PDF no fetcher could build."""
    sh = (REPO / "docs/papers/download_papers.sh").read_text(encoding="utf-8", errors="replace")
    ohana_pdf = next(t for gi in boot.MANIFEST if gi.name == "ohana_paper_pdf" for t in gi.targets)
    assert ohana_pdf.name.split("_")[0] in sh, "arXiv id absent from download_papers.sh"
    assert ohana_pdf.name in sh, "the guard-required PDF filename is absent from download_papers.sh"
    assert "verified" in sh.split(ohana_pdf.name)[0][-200:], "the fetch line does not target verified/"


def test_bootstrap_runs_and_reports_without_side_effects_on_a_ready_tree():
    """Idempotence: on the authoring working copy every short input already exists, so a run
    must rebuild nothing and must not report a failure."""
    r = subprocess.run([sys.executable, str(REPO / "scripts/bootstrap_gate_inputs.py")],
                       cwd=str(REPO), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 0, ((r.stdout or "") + (r.stderr or ""))[-1500:]
    text = (r.stdout or "")
    assert '"built": []' in text, f"a ready tree should need no rebuilds: {text[-800:]}"
    assert '"failed": []' in text, text[-800:]


# ---------------------------------------------------------------- scan scope (F39 mechanism)
def test_scan_scope_filter_is_relative_not_absolute():
    """Reproduce the clone failure without a clone: a repo parked under a directory literally
    named 'scratch' must not make the scan skip every module."""
    skip = producer.SKIP_DIRS
    # The clone of 2026-11-15 sat here; its .parts contained 'scratch' as an ANCESTOR.
    clone_style = Path("C:/Users/x/AppData/Local/hermes/cache/scratch/sidm_clone_f39/"
                       "v0.3-prelim/code/phase20_full_space_conditions.py")
    fake_root = clone_style.parents[2]
    absolute_parts_skips = any(part in skip for part in clone_style.parts)
    relative_parts_skips = any(part in skip for part in clone_style.relative_to(fake_root).parts)
    assert absolute_parts_skips, "fixture no longer reproduces the ancestor-name collision"
    assert not relative_parts_skips, "the relative-parts filter is itself broken"


def test_scan_classifies_the_tracked_code_dir():
    """The empty-registry failure showed up as ZERO modules, so assert presence of specific
    tracked modules and a bucket floor, not a total copied from a badge. (An earlier version of
    this test asserted ">= 50 classified of 516 tracked" and failed in a fresh clone at 38: the
    scan walks the whole tree, including gitignored scratch scripts that a clone does not have,
    so a total over the whole tree is not an invariant of the tracked code directory.)"""
    rebuilt = producer.scan()
    classified = set(rebuilt["canonical_pair_modules"]) | set(rebuilt["archived_pair_modules"]) \
        | set(rebuilt["mixed_pair_modules"])
    assert len(rebuilt["canonical_pair_modules"]) >= 10, rebuilt
    assert len(rebuilt["archived_pair_modules"]) >= 5, rebuilt

    tracked = subprocess.run(["git", "-C", str(REPO), "ls-files", "v0.3-prelim/code/*.py"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert tracked.returncode == 0
    code_modules = [ln.strip().replace("\\", "/") for ln in tracked.stdout.splitlines() if ln.strip()]
    assert len(code_modules) > 300, f"git sees only {len(code_modules)} code modules"

    # The registry buckets themselves must be reported by the scan in any checkout.
    stored = REPO / "v0.3-prelim/data/results/fH_pairing_registry.json"
    if stored.exists():
        import json
        data = json.loads(stored.read_text(encoding="utf-8"))
        for key in ("canonical_pair_modules", "archived_pair_modules"):
            for mod in data.get(key, []):
                assert mod in classified, f"{key} entry {mod} not classified by the scan"

    # The registry is deliberately selective: of 516 tracked code modules it classifies 20, because
    # only those bind a pairing name. A coverage ratio over the whole code directory is therefore
    # NOT an invariant (an earlier draft of this test asserted one and failed with 'the scan sees
    # only 20 of 516'). What IS an invariant, and what the absolute-parts bug violated, is that the
    # scan is non-empty and reproduces every entry the published artifact carries -- asserted above.
    assert classified, "the scan classified nothing: the empty-registry failure mode"
    bound = sum(len(producer.scan()[k]) for k in
                ("canonical_pair_modules", "archived_pair_modules", "mixed_pair_modules"))
    assert bound >= 15, f"scan bound only {bound} pairing commitments across the whole tree"


def test_gate_evidence_cited_by_the_scan_comment_exists():
    """The fix cites a clone-run log; a citation to a file that does not exist is the F35 pattern."""
    src = (REPO / "scripts/fH_pairing_registry.py").read_text(encoding="utf-8", errors="replace")
    cited = ["clone_run_53806dd_20261115.txt", "gate_run_repair_final_20261115.txt"]
    for name in cited:
        if name in src:
            assert (REPO / "docs/evidence" / name).exists(), f"{name} cited but not filed"
