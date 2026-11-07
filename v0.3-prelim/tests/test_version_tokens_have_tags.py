"""Guard: every numbered version the repository CLAIMS must exist as a real tag.

Why this exists (finding F32, 2026-11-07).
`docs/SIDM_V40_51_FULL_REVIEW_REPORT_2026_10_19.md` line 8 states
"Final tag: v40.63-N16ReviewResponse", and `VERSION` has carried the token
`v40.63-N16ReviewResponse` since 0d64890. Neither had ever been backed by a git
tag: the tag existed only inside a document. A version label that is not a tag
is a claim with no address - no one can check out "v40.63", and no one can tell
which tree the report was describing.

Two rules are asserted:

1. NUMBERED CLAIMS MUST BE TAGGED. Every `v40.NN` token in VERSION must be
   satisfied by a tag that (a) starts with that numeric base, or (b) is the
   documented rename of it, and (c) points at a commit whose own VERSION file
   contains that token. (c) is the part that matters: a tag named correctly but
   anchored on the wrong tree satisfies the name and lies about the state.

2. THE CURRENT VERSION LINE MUST HAVE A SAVE POINT. At least one tag in the
   milestone/RecordSave family must point at a commit whose VERSION tail equals
   HEAD's VERSION tail. Ordinary commits do not trip this; advancing VERSION
   without recording a tag does.

The negative test proves the checker actually fires rather than merely passing.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = PROJECT_ROOT / "VERSION"

NUMBERED_PREFIX_RE = re.compile(r"^(v40\.\d+)")

# v40.58 was tagged under the phase-name convention instead of the numeric one.
DOCUMENTED_RENAMES = {
    "v40.58": ("v19.2-F-Phase3-CLOSED-r40.58",),
}

# Only this family is allowed to satisfy the save-point rule, so that an
# unrelated old tag cannot accidentally certify the current state.
SAVE_POINT_FAMILY_RE = re.compile(r"^(v40\.\d+|v19\.2-F-RecordSave)")


def _git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(PROJECT_ROOT),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def version_tokens(version_text: str) -> list[str]:
    """VERSION tokens that make a numbered version claim."""
    return [tok for tok in version_text.strip().split("+")
            if NUMBERED_PREFIX_RE.match(tok)]


def real_version_at(commit: str) -> str:
    return _git("show", f"{commit}:VERSION").strip()


def tag_names() -> list[str]:
    out = _git("tag", "-l")
    return [t for t in out.splitlines() if t.strip()]


def tag_target(tag: str) -> str:
    return _git("rev-list", "-n1", tag)


def check_numbered_tokens(version_text: str, tags: list[str],
                          version_at: Callable[[str], str] = real_version_at) -> list[str]:
    """Return a list of human-readable violations for the numbered-token rule.
    `version_at` is injectable so the checker can be tested against a tree that
    does not match the tag's name."""
    violations = []
    for token in version_tokens(version_text):
        base = NUMBERED_PREFIX_RE.match(token).group(1)
        candidates = [t for t in tags
                      if t.startswith(base) or t in DOCUMENTED_RENAMES.get(base, ())]
        if not candidates:
            violations.append(
                f"{token}: VERSION claims this version but no tag starts with "
                f"{base!r} (renames allowed: {DOCUMENTED_RENAMES.get(base, ())})")
            continue
        anchored = []
        for tag in candidates:
            try:
                if token in version_at(tag_target(tag)).split("+"):
                    anchored.append(tag)
            except RuntimeError:
                continue
        if not anchored:
            violations.append(
                f"{token}: tags {candidates} exist but none points at a commit "
                "whose VERSION file contains the token - the tag is anchored on "
                "a tree that does not declare this version")
    return violations


def check_save_point(head_version_text: str, tags: list[str],
                     version_at: Callable[[str], str] = real_version_at) -> list[str]:
    """The current VERSION tail must be certified by a tag in the save family."""
    tail = head_version_text.strip().split("+")[-1]
    family = [t for t in tags if SAVE_POINT_FAMILY_RE.match(t)]
    for tag in family:
        try:
            at = version_at(tag_target(tag))
        except RuntimeError:
            continue
        if at.strip().split("+")[-1] == tail:
            return []
    return [f"VERSION tail {tail!r} has no tag pointing at a commit with the "
            f"same tail (searched {len(family)} tags in the save family)"]


def test_numbered_version_tokens_all_have_tags() -> None:
    violations = check_numbered_tokens(VERSION_FILE.read_text(encoding="utf-8"),
                                       tag_names())
    assert not violations, "VERSION claims versions that are not tags:\n  " + "\n  ".join(violations)


def test_current_version_line_has_a_save_point_tag() -> None:
    violations = check_save_point(VERSION_FILE.read_text(encoding="utf-8"), tag_names())
    assert not violations, "current standing is not a recorded save point:\n  " + "\n  ".join(violations)


# ------------------------------------------------------------------ negative tests
# These inject a fake VERSION resolver, so they exercise the checker itself
# instead of depending on which tags happen to exist right now.
def test_guard_fires_for_a_claimed_version_with_no_tag() -> None:
    """The exact defect this guard was written for: a version named in VERSION
    that no tag carries."""
    fake = "0.4-prelim+v40.62-N15ReviewResponse+v40.99-MadeUpRound"
    violations = check_numbered_tokens(
        fake, ["v40.62-N15ReviewResponse", "v40.63-N16ReviewResponse"],
        version_at=lambda commit: fake)
    assert any("v40.99" in v and "no tag starts with" in v for v in violations), violations


def test_guard_fires_for_a_tag_anchored_on_the_wrong_tree() -> None:
    """A correctly-named tag whose tree predates the token must not satisfy the
    claim - satisfying the name while misstating the tree is the failure mode."""
    claimed = "0.4-prelim+v40.63-N16ReviewResponse"
    older_tree = "0.4-prelim+v40.62-N15ReviewResponse"
    violations = check_numbered_tokens(
        claimed, ["v40.63-N16ReviewResponse"], version_at=lambda commit: older_tree)
    assert any("anchored" in v for v in violations), violations


def test_guard_fires_when_no_tag_certifies_the_current_version_line() -> None:
    never = "0.4-prelim+SomeRoundNoTagHas-2099-01-01"
    violations = check_save_point(
        never, ["v40.63-N16ReviewResponse", "v19.2-F-RecordSave-v1.17"],
        version_at=lambda commit: "0.4-prelim+v40.63-N16ReviewResponse")
    assert violations and "2099-01-01" in violations[0], violations


def test_documented_rename_satisfies_a_numeric_token() -> None:
    """v40.58 is tagged as v19.2-F-Phase3-CLOSED-r40.58. The rename map has to
    let it through, otherwise the guard could only be satisfied by renaming tags,
    which would rewrite published references to that milestone."""
    token_text = "0.4-prelim+v40.58-Phase3-CLOSED"
    violations = check_numbered_tokens(
        token_text, ["v19.2-F-Phase3-CLOSED-r40.58"],
        version_at=lambda commit: token_text)
    assert violations == [], violations
