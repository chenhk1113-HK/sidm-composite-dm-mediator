"""Guard against the F41 class: executable code sitting inside a gitignored directory.

F41 was not a missing data file. `outputs/` and `v0.3-prelim/data/external/` are ignored as
WHOLE directories, so a script placed inside one is invisible to git: it does not travel to a
clone, cannot be reviewed, and -- when a test's skip message tells the reader to run it -- asks
a fresh clone to execute a file that clone has never seen. Twenty such scripts were archived to
archive/outputs_scripts_2026-11/ on 2026-11-16 and the two that tests actually name were moved to
scripts/.

This test keeps the hole from quietly refilling: any .py/.sh inside a declared gitignored scope
must either be a producer declared by scripts/bootstrap_gate_inputs.py or appear in ALLOWLIST
below with a reason. The falsification test creates a real undeclared file and requires the
detection to fire -- a guard that never fails is not a guard.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import bootstrap_gate_inputs as boot  # noqa: E402

# Directories .gitignore ignores wholesale, where a stray script would be invisible to git.
GITIGNORED_SCOPES = ("outputs/", "v0.3-prelim/outputs/", "v0.3-prelim/data/external/")
SCRIPT_SUFFIXES = (".py", ".sh")

ALLOWLIST: dict[str, str] = {
    "v0.3-prelim/data/external/sparc/fetch_sparc.py": (
        "the original copy that lived beside the data it downloads; superseded by the tracked "
        "scripts/fetch_sparc.py (F41). Kept on disk because it is inside an ignored data "
        "directory that bootstrap rebuilds, and no code imports it."
    ),
}


def _declared_producers() -> set[str]:
    out = set()
    for gi in boot.MANIFEST:
        script = boot.producer_script(gi)
        if script:
            out.add(script.replace("\\", "/"))
    return out


def _untracked_scripts() -> list[str]:
    """Scripts present on disk but not tracked by git (git-ignored included)."""
    r = subprocess.run(["git", "-C", str(REPO), "ls-files", "--others"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    paths = [p.replace("\\", "/") for p in (r.stdout or "").splitlines() if p.strip()]
    return [p for p in paths
            if p.endswith(SCRIPT_SUFFIXES)
            and p.startswith(GITIGNORED_SCOPES)]


def _undeclared() -> list[str]:
    declared = _declared_producers()
    return [p for p in _untracked_scripts()
            if p not in declared and p not in ALLOWLIST]


# ------------------------------------------------------------------ the invariant
def test_gitignored_scopes_are_actually_gitignored():
    """The scope list must describe real ignore rules, or the guard checks nothing."""
    for scope in GITIGNORED_SCOPES:
        probe = REPO / scope / "cg16_probe.py"
        r = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q", str(probe)],
                           capture_output=True)
        assert r.returncode == 0, f"{scope} is not git-ignored, so it belongs in tracked scope"


def test_no_undeclared_script_lives_in_a_gitignored_scope():
    problems = _undeclared()
    assert not problems, (
        f"{len(problems)} executable script(s) live in a gitignored scope without being declared "
        f"as a bootstrap producer or allowlisted with a reason: {problems}. This is F41: a clone "
        "cannot see them, and any test that names them asks the clone to run an unseen file."
    )


def test_outputs_directory_holds_no_code_after_the_migration():
    """The 2026-11-16 migration moved every script out of outputs/; it must stay code-free."""
    leftovers = sorted(p.name for p in (REPO / "outputs").glob("*")
                       if p.suffix in SCRIPT_SUFFIXES)
    assert not leftovers, f"outputs/ contains code again: {leftovers}"


def test_archived_scripts_are_tracked_and_documented():
    archive = REPO / "archive/outputs_scripts_2026-11"
    files = sorted(p for p in archive.iterdir() if p.suffix in SCRIPT_SUFFIXES)
    assert files, "the archive is empty; the migration is not where the finding says it is"
    r = subprocess.run(["git", "-C", str(REPO), "ls-files", "--", "archive/outputs_scripts_2026-11"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    tracked = {p.replace("\\", "/") for p in (r.stdout or "").splitlines()}
    untracked = [p.name for p in files if f"archive/outputs_scripts_2026-11/{p.name}" not in tracked]
    assert not untracked, f"archived scripts are not tracked in git: {untracked}"
    assert (archive / "README.md").exists(), "the archive needs a reason for existing"
    readme = (archive / "README.md").read_text(encoding="utf-8", errors="replace")
    assert "F41" in readme, "the archive README must name the finding it closes"


def test_allowlist_entries_are_explained_and_not_stale():
    for path, reason in ALLOWLIST.items():
        assert len(reason) > 40, f"{path} is allowlisted without an explanation"
        declared = path in _declared_producers()
        exists = (REPO / path).exists()
        assert exists or declared, (
            f"{path} is allowlisted but is neither on disk nor declared: retire the entry"
        )


# ------------------------------------------------------------------ falsification
def test_an_undeclared_script_in_outputs_is_detected():
    fixture = REPO / "outputs" / "hermes_falsification_orphan.py"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text("# fixture for the F41 guard\n", encoding="utf-8")
    try:
        rel = "outputs/hermes_falsification_orphan.py"
        assert rel in _untracked_scripts(), "the scan did not see a script in a gitignored scope"
        assert rel in _undeclared(), "an undeclared gitignored script passed the guard"
    finally:
        fixture.unlink(missing_ok=True)


def test_a_declared_producer_is_not_flagged():
    """The guard must not cry wolf about the tools the manifest itself declares."""
    declared = sorted(_declared_producers())
    assert declared, "no producer is declared, so this test would prove nothing"
    on_disk = [p for p in _untracked_scripts() if p in declared]
    for path in on_disk:
        assert path not in _undeclared(), f"{path} is declared yet flagged"


def test_migration_repointed_every_tracked_reference():
    """A moved script whose references still name the old path is a half-finished migration."""
    # The pattern is assembled at runtime on purpose: a literal copy of the old path in this file
    # would be the single hit this guard reports, i.e. the guard would flag itself forever.
    r = subprocess.run(["git", "-C", str(REPO), "grep", "-n", "-I",
                        "outputs/" "downsample_for_reference.py", "--", ":!outputs",
                        ":!archive", ":!CHANGELOG.md", ":!docs/INTEGRITY_FINDINGS_2026-11-04.md"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    stale = [line for line in (r.stdout or "").splitlines() if line.strip()]
    assert not stale, f"tracked files still point at the pre-migration path:\n" + "\n".join(stale)


# -------------------------------------------------------------------------------------------
# F45: the other thing a gitignored tool carries that a data audit never looks for.
#
# Moving outputs/ scripts into tracked scope (the F41 fix) also moved a hardcoded GitHub token
# into git. It was caught by GitHub's push protection when the round was pushed -- outside the
# repo's own checks -- and it had never been scanned before precisely because the file lived in a
# directory git never looked at. The token was NOT published (the push was refused); it was
# redacted from the working tree on 2026-11-16 and the owner was told to rotate it.
#
# Scope, stated honestly: this guard scans the CURRENT tracked tree. It cannot see a credential
# that already sits in historical commits; at the time of writing the redacted token still exists
# in the blobs of commits 6d705a4..HEAD~ (unpushed at redaction time). Removing it from history
# means rewriting commit shas, which would invalidate every gate-log header and census citation
# that names them -- a larger integrity cost than the residue, so the residue is disclosed rather
# than silently rewritten.
# -------------------------------------------------------------------------------------------

CREDENTIAL_PATTERNS = {
    "GitHub classic PAT": rb"ghp_[A-Za-z0-9]{36,40}",
    "GitHub fine-grained PAT": rb"github_pat_[A-Za-z0-9_]{30,}",
    "GitHub OAuth token": rb"gho_[A-Za-z0-9]{36,}",
    "GitHub server-to-server token": rb"ghs_[A-Za-z0-9]{36,}",
    "AWS access key id": rb"AKIA[0-9A-Z]{16}",
    "Private key block": rb"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Slack token": rb"xox[abpr]-[A-Za-z0-9-]{10,}",
}
SCANNABLE_SUFFIXES = (".py", ".sh", ".md", ".json", ".yaml", ".yml", ".txt", ".cff",
                      ".ipynb", ".ps1", ".cmd", ".bat", ".ini", ".cfg", ".toml")
MAX_SCAN_BYTES = 4_000_000


def _tracked_scannable_files():
    r = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    paths = [p for p in (r.stdout or "").split("\0") if p]
    return [REPO / p for p in paths if Path(p).suffix.lower() in SCANNABLE_SUFFIXES]


def _scan_for_credentials(files):
    """Return (path, label, byte offset) for every credential-shaped literal in `files`."""
    hits = []
    for f in files:
        try:
            data = f.read_bytes()
        except OSError:
            continue
        if len(data) > MAX_SCAN_BYTES:
            continue
        for label, pat in CREDENTIAL_PATTERNS.items():
            m = re.search(pat, data)
            if m:
                try:
                    shown = str(f.relative_to(REPO))
                except ValueError:  # a falsification file outside the repo
                    shown = str(f)
                hits.append((shown, label, m.start()))
    return hits


def test_no_tracked_file_carries_a_credential_shaped_literal():
    files = _tracked_scannable_files()
    assert len(files) > 200, f"the scan covered only {len(files)} files; the file list is wrong"
    hits = _scan_for_credentials(files)
    assert not hits, (
        "a credential-shaped literal is in tracked scope (F45 class). Offenders are named by "
        "path, pattern label and byte offset -- the literal itself is never printed:\n"
        + "\n".join(f"  {p}: {label} at byte {off}" for p, label, off in hits)
    )


def test_a_hardcoded_token_in_a_script_is_detected(tmp_path):
    """Falsification: fabricate the defect in a throwaway file and require the scan to fire."""
    fake = tmp_path / "verify_remote.py"
    fake.write_bytes(b'headers={"Authorization": "token ' + b"ghp_" + b"X" * 36 + b'"}\n')
    hits = _scan_for_credentials([fake])
    assert len(hits) == 1, f"the fabricated token was not detected: {hits}"
    assert hits[0][1] == "GitHub classic PAT", hits

    # ...and the redacted placeholder must not be reported, or the guard would flag its own fix.
    clean = tmp_path / "clean.py"
    clean.write_text('headers={"Authorization": "token REDACTED-2026-11-16"}\n', encoding="utf-8")
    assert not _scan_for_credentials([clean]), "the guard flags its own redaction placeholder"
