"""F39 bootstrap: regenerate the gate inputs that git ignores, from tools tracked in git.

Finding F39 says the certification is working-copy-scoped: the suite reads inputs that
.gitignore keeps out of the repository (docs/papers/*.pdf, v0.3-prelim/outputs/**,
v0.3-prelim/data/external/**), so a fresh clone cannot reproduce a gate certification.
Measured on 53806dd (docs/evidence/clone_run_53806dd_20261115.txt): 10 failed / 3642 passed /
112 skipped in a clean clone, against 3709 passed / 25 skipped / 40 deselected in the working
copy. 87 of the extra skips and 9 of the 10 failures were missing inputs, not broken code.

This script is the repair: every ignored input the suite depends on is declared once, with the
tracked command that rebuilds it, and each input is classified by whether a clone CAN rebuild it.

  REPO_BUILT        a command inside this repository rebuilds it           -> clone-reproducible
  FETCH             a tracked fetcher downloads it from a public source     -> clone-reproducible
                    (needs network; --fetch enables these steps)
  HOST_PINNED       data that lives outside the repository and has no      -> NOT clone-reproducible
                    tracked producer; the manifest records where it lives
  LONG_RUN          a sampler/producer whose runtime is minutes-to-hours;  -> reproducible in
                    bootstrapped only with --long                          principle, not by default

Usage:
    python scripts/bootstrap_gate_inputs.py              # rebuild what is cheap and local
    python scripts/bootstrap_gate_inputs.py --fetch      # also download declared inputs
    python scripts/bootstrap_gate_inputs.py --list       # print the manifest, change nothing
    python scripts/bootstrap_gate_inputs.py --require    # exit non-zero if a declared short
                                                         # input cannot be accounted for

Design rule this script enforces (learned the hard way, F36/F38/F40 round): a manifest is only
worth having if it is falsified. v0.3-prelim/tests/test_bootstrap_gate_inputs.py checks that
every declared producer exists, that declared targets are actually git-ignored (otherwise the
manifest would be describing tracked files as missing inputs), and that a declared producer that
does not exist makes THIS script fail instead of silently reporting the input as unavailable.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (REPO_ROOT honours DM_SIDM_PROJECT_ROOT: works in a clone/worktree)

REPO = paths.REPO_ROOT
PY = sys.executable

KIND_REPO_BUILT = "REPO_BUILT"
KIND_FETCH = "FETCH"
KIND_HOST_PINNED = "HOST_PINNED"
KIND_LONG_RUN = "LONG_RUN"


@dataclass
class GateInput:
    """One git-ignored file (or directory) that the test suite reads."""

    name: str
    kind: str
    targets: list  # paths that must exist for the suite to exercise its tests
    build: list | None = None  # argv that materialises the targets (cwd = REPO)
    needs_network: bool = False
    long_run: bool = False
    note: str = ""
    consumed_by: list = field(default_factory=list)  # tests that read these targets


OHANA_PDF = REPO / "docs/papers/verified/2608.04362_ohana_2026_cloud9_cdm_sidm.pdf"
SPARC_TABLE = REPO / "v0.3-prelim/data/external/sparc/Table1.mrt"
GALSTREAMS_CURATED = REPO / "v0.3-prelim/outputs/t95/multi_stream_real_galstreams.json"
# The catalog location is an override, not a literal: CG-16 forbids host paths in live-scope code,
# and the point of declaring it here is that a clone on ANOTHER machine can set the variable and
# discover whether its own machine has the catalog at all.
GALSTREAMS_ROOT = Path(os.environ.get("DM_SIDM_GALSTREAMS_ROOT", str(Path.home() / "galstreams/galstreams/tracks")))

MANIFEST: list[GateInput] = [
    GateInput(
        name="ohana_paper_pdf",
        kind=KIND_FETCH,
        targets=[OHANA_PDF],
        build=["bash", "docs/papers/download_papers.sh"],
        needs_network=True,
        consumed_by=["v0.3-prelim/tests/test_v40_61_n14_docx_response.py::test_ohana_paper_saved_locally"],
        note=("The reviewer-n14 Item 5 guard requires the Ohana+ 2026 PDF on disk (arXiv 2608.04362, "
              "2,654,775 bytes). docs/papers/*.pdf is gitignored, and until 2026-11-15 "
              "download_papers.sh had no line for this id -- so the only tracked fetcher could not "
              "produce the one PDF a gate guard asserts on. That line now exists."),
    ),
    GateInput(
        name="sparc_table1",
        kind=KIND_FETCH,
        targets=[SPARC_TABLE],
        build=[PY, "scripts/fetch_sparc.py"],
        needs_network=True,
        consumed_by=["v0.3-prelim/tests/test_phase33d_real_sparc.py",
                     "v0.3-prelim/tests/test_sparc_hierarchical.py"],
        note=("v0.3-prelim/data/external/ is gitignored (line 53), and its fetch_sparc.py therefore "
              "did not exist in a fresh clone -- the clone lacked the tool the data depended on. "
              "Copied to scripts/ (tracked) on 2026-11-16; downloads Table1.mrt and MassModels.mrt "
              "from astroweb.cwru.edu."),
    ),
    GateInput(
        name="fh_pairing_registry",
        kind=KIND_REPO_BUILT,
        targets=[REPO / "v0.3-prelim/data/results/fH_pairing_registry.json"],
        build=[PY, "scripts/fH_pairing_registry.py"],
        consumed_by=["v0.3-prelim/tests/test_fH_pairing_registry.py"],
        note="The pairing registry the guards compare the source tree against. Rebuilding it is how "
             "a fresh clone gets the artifact; the guard then checks the rebuilt artifact against "
             "the source in the same breath.",
    ),
    GateInput(
        name="t90_v23_dry_run_outputs",
        kind=KIND_REPO_BUILT,
        targets=[
            REPO / "v0.3-prelim/outputs/t90/t90_v23_lz_lowE_count.json",
            REPO / "v0.3-prelim/outputs/t90/t90_v23_pandax_highE_count.json",
            REPO / "v0.3-prelim/outputs/t90/t90_v23_xenonnt_s2only_count.json",
            REPO / "v0.3-prelim/outputs/t90/t90_v23_joint_likelihood.json",
        ],
        build=[PY, "v0.3-prelim/code/t90_v23_dry_run_all.py"],
        consumed_by=["v0.3-prelim/tests/test_t90_v23_dry_run.py"],
        note="outputs/ is gitignored (line 38). Four failures in the clean-clone run were these files "
             "absent: the dry-run producers are seconds long and depend on nothing external.",
    ),
    GateInput(
        name="fermi_mcdaniel_external_data",
        kind=KIND_FETCH,
        targets=[REPO / "v0.3-prelim/data/external/fermi_mcdaniel2024"],
        build=["bash", "scripts/fetch_external_data.sh"],
        needs_network=True,
        consumed_by=["v0.3-prelim/tests/test_t32_real_likelihood.py"],
        note=("The figshare fetcher existed ONLY at outputs/fetch_external_data.sh -- inside a "
              "gitignored directory -- so a fresh clone lacked the very tool the test told it to run. "
              "Copied to scripts/ (tracked) on 2026-11-16 and the test's skip message re-pointed; "
              "md5-verified against the figshare-computed hashes, 220 TS profiles."),
    ),
    GateInput(
        name="t95_curated_galstreams",
        kind=KIND_REPO_BUILT,
        targets=[GALSTREAMS_CURATED],
        build=[PY, "v0.3-prelim/code/t95_v25_multi_stream_real_galstreams.py"],
        consumed_by=["v0.3-prelim/tests (phase7d stream-map script run)"],
        note=("Only regenerable if the galstreams catalog is reachable -- see galstreams_tracks. "
              "Without it the producer writes nothing and the dependent test fails for a missing "
              "input rather than for a code fault."),
    ),
    GateInput(
        name="galstreams_tracks",
        kind=KIND_HOST_PINNED,
        targets=[GALSTREAMS_ROOT],
        build=None,
        note=("t95_v25 reads track.st.*.ecsv from a hard-coded host path outside the repository "
              "(C:/Users/<user>/galstreams/galstreams/tracks, inventoried as FROZEN under CG-16). "
              "The catalog is not vendored, pip install galstreams is not in the project venv, and "
              "no tracked script downloads it. This is the part of F39 a bootstrap cannot close: "
              "a fresh clone of this repository cannot run the stream-map chain at all until the "
              "catalog is either vendored into v0.3-prelim/data/external/ or a fetcher is added."),
    ),
    GateInput(
        name="producer_posteriors",
        kind=KIND_LONG_RUN,
        targets=[REPO / "v0.3-prelim/outputs"],
        build=None,
        long_run=True,
        consumed_by=["test_t10*", "test_t95_v1*", "test_t98*", "test_t106-t108", "test_t90_v11_v12_v13"],
        note=("107 tests in the clean-clone run skipped with 'No T1xx results; run <producer>.py'. "
              "Those producers are dynesty/N-body runs (minutes to hours) and the skips are a "
              "deliberate design: a test that cannot see its posterior skips rather than failing. "
              "They are listed here so the skip count is explained rather than mysterious, not so "
              "the gate can re-run them."),
    ),
]


def _present(target: Path) -> bool:
    try:
        return target.exists()
    except OSError:
        return False


def _git_ignored(target: Path) -> bool:
    try:
        r = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q", str(target)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.returncode == 0
    except OSError:
        return False


def run(do_fetch: bool, do_long: bool) -> int:
    built: list[str] = []
    already: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []

    for gi in MANIFEST:
        if all(_present(t) for t in gi.targets):
            already.append(gi.name)
            continue
        if gi.kind == KIND_HOST_PINNED or gi.build is None:
            skipped.append(f"{gi.name} ({gi.kind}: no tracked producer)")
            continue
        if gi.long_run and not do_long:
            skipped.append(f"{gi.name} (LONG_RUN: pass --long to rebuild)")
            continue
        if gi.needs_network and not do_fetch:
            skipped.append(f"{gi.name} ({gi.kind}: pass --fetch to download)")
            continue
        print(f"  building {gi.name}: {' '.join(gi.build)}")
        try:
            r = subprocess.run(gi.build, cwd=str(REPO), capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
        except OSError as exc:
            failed.append(f"{gi.name}: could not run producer: {exc}")
            continue
        if r.returncode != 0:
            tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-3:]
            failed.append(f"{gi.name}: producer exit {r.returncode}: {' | '.join(tail)}")
            continue
        missing = [str(t) for t in gi.targets if not _present(t)]
        if missing:
            failed.append(f"{gi.name}: producer succeeded but wrote none of {missing}")
            continue
        built.append(gi.name)

    print(json.dumps({"present": len(already), "built": built, "skipped": skipped,
                      "failed": failed, "manifest_size": len(MANIFEST)}, indent=1))
    return 1 if failed else 0


def require() -> int:
    """Manifest integrity: a declared short input must have a producer that exists on disk."""
    problems = []
    for gi in MANIFEST:
        if gi.kind == KIND_HOST_PINNED:
            continue
        if gi.build is None:
            if not gi.long_run:
                problems.append(f"{gi.name}: kind {gi.kind} declares no producer")
            continue
        producer = gi.build[-1]
        if producer.endswith(".py") or producer.endswith(".sh"):
            if not (REPO / producer).exists():
                problems.append(f"{gi.name}: declared producer {producer} does not exist")
        for t in gi.targets:
            if not _git_ignored(t) and not _present(t):
                problems.append(f"{gi.name}: target {t} is neither git-ignored nor present")
    print(json.dumps({"manifest_size": len(MANIFEST), "problems": problems}, indent=1))
    return 1 if problems else 0


def listing() -> int:
    for gi in MANIFEST:
        print(f"{gi.kind:11s} {gi.name}")
        for t in gi.targets:
            print(f"            target: {t} (gitignored={_git_ignored(t)}, present={_present(t)})")
        if gi.build:
            print(f"            build : {' '.join(gi.build)}")
        print(f"            note  : {gi.note}")
    counts: dict[str, int] = {}
    for gi in MANIFEST:
        counts[gi.kind] = counts.get(gi.kind, 0) + 1
    print("counts:", counts)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="run declared downloaders (needs network)")
    ap.add_argument("--long", action="store_true", help="also rebuild minutes-to-hours producers")
    ap.add_argument("--list", action="store_true", help="print the manifest without changing anything")
    ap.add_argument("--require", action="store_true", help="manifest integrity check, no side effects")
    args = ap.parse_args()
    if args.list:
        return listing()
    if args.require:
        return require()
    print(f"# bootstrap_gate_inputs: repo={REPO} python={PY}")
    return run(do_fetch=args.fetch, do_long=args.long)


if __name__ == "__main__":
    raise SystemExit(main())
