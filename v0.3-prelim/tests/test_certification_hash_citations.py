"""F49 pin: every git object id quoted in a certification artifact must resolve, to the type it claims.

Finding F48 was a certification artifact citing an identifier that does not exist. The annotated tag
`T215WallTimeMeasurementAndLocalDensityReference-2026-11-17` was first cut with the sentence "the strict
15-layer gate ran on commit `cbcdba1` (tree `f4d458443b6c...`)". The tree of `cbcdba1` is
`f4d45844da2d1a2f7bfde6df9a49b5327da982fe`; the quoted hash resolves to no object at all
(`git cat-file -t <hash>` -> exit 128). It was typed from working notes instead of read back, and no gate
layer read a tag message, so a 15/15 green gate certified a tag that pointed at a phantom object.

The invariant this guard holds, in three rules:

1. RESOLVES. Every 40-hex token inside a certification artifact -- an annotated tag message, a filed gate
   log (`docs/evidence/gate_run*.txt`), or a front page (README, CURRENT, EXTRACT, CITATION.cff,
   CHANGELOG, INTEGRITY_FINDINGS) -- is a git object. A token that resolves to nothing is a violation
   UNLESS the enclosing block (contiguous non-blank lines) shows it is being quoted as an error -- naming
   `cat-file`, a resolution failure, or calling the value wrong -- or names the external repository it
   belongs to (an upstream commit sha such as the WIMpy_NREFT pin). The exemption is per block, so an
   unresolved hash cannot hide in an unrelated certification sentence.
2. RIGHT TYPE. A token introduced by a label -- `tree <hash>`, `commit <hash>`, `tag object <hash>`,
   `blob <hash>` -- must resolve to exactly that type. This is the F44 shape (a parser that read a log's
   tree sha as its commit because a tree peels to itself), caught on the citation side.
3. PAIRS. A `Tree under certification:` line must be the tree of the `Commit under certification:` line in
   the same log. A tag message that cites a tree must name at least one commit whose tree it is (its own
   target counts). Prose of the form "the tree of <sha> is <sha>" must state the true pair.

Out of scope by construction, so no non-git hex string can be mistaken for a citation: a 64-hex sha256 or
a 32-hex md5 never matches (the pattern asserts non-hex on both sides, so a longer hex run is skipped
whole), and a 39-hex typo is not treated as a citation either.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent.parent

FULL_HEX_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
HEX_TOKEN_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])")
# A citation label is a type word sitting directly in front of the token on the same line,
# with at most a short filler ("tree hash `x`", "tag object `x`").
LABEL_RE = re.compile(r"\b(tree|commit|blob|tag)\b[^0-9a-f`'\"]{0,14}$", re.IGNORECASE)
# "the tree of <sha> is <sha>" / "tree of <sha> was <sha>" -- an explicit pair claim in prose.
TREE_OF_CLAIM_RE = re.compile(
    r"\btree of\b[^0-9a-f]{0,4}(?<![0-9a-f])([0-9a-f]{7,40})(?![0-9a-f])"
    r"[^\n]{0,80}?(?<![0-9a-f])([0-9a-f]{40})(?![0-9a-f])",
    re.IGNORECASE,
)
COMMIT_HEADER_RE = re.compile(
    r"^Commit under certification:\s*(?<![0-9a-f])([0-9a-f]{40})(?![0-9a-f])\s*$", re.MULTILINE
)
TREE_HEADER_RE = re.compile(
    r"^Tree under certification:\s*(?<![0-9a-f])([0-9a-f]{40})(?![0-9a-f])\s*$", re.MULTILINE
)

# A block may quote a non-resolving hash only if it says so, in words that prove the hash is being
# reported as broken rather than relied on.
DISCLOSURE_MARKERS = (
    "cat-file",
    "no object",
    "could not get object",
    "no such object",
    "exit 128",
    "not a git object",
    "does not resolve",
    "resolves to no",
    "wrong",
    "erroneous",
    "incorrect",
    "bogus",
    "f48",
)
# A block may quote a hash that lives in another repository only if it names that repository.
EXTERNAL_MARKERS = ("github.com/", "git+https", "direct_url.json", "upstream", "external")

# Filed gate logs older than finding F42 printed `<HEAD at run time>` instead of a commit and tree, so
# they carry no certification header to check. The exemption is a closed list: a NEW log that omits the
# header goes red, and an exemption that no longer matches a real headerless log goes red too. F42 was
# closed in the clone-reproducibility round, whose own log (gate_run_f39_bootstrap_20261116.txt) is the
# first one with a header.
PRE_F42_GATE_LOGS = frozenset(
    {
        "gate_run_20261113.txt",
        "gate_run_20261113_final.txt",  # 851 bytes: a truncated capture, cited as such in the findings
        "gate_run_badge_fixed_20261115.txt",
        "gate_run_committed_20261115.txt",
        "gate_run_failed_ast_guard_20261115.txt",
        "gate_run_failed_cg16_20261115.txt",
        "gate_run_final_20261112.txt",
        "gate_run_repair_final_20261115.txt",
    }
)

FRONT_PAGES = (
    "README.md",
    "CURRENT.md",
    "EXTRACT.md",
    "CITATION.cff",
    "CHANGELOG.md",
    "docs/INTEGRITY_FINDINGS_2026-11-04.md",
)
GATE_LOG_GLOB = "gate_run*.txt"


def _git(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        input=stdin,
    )


def _is_full_hex(token: str) -> bool:
    return re.fullmatch(r"[0-9a-f]{40}", token) is not None


_TYPE_CACHE: dict[str, str | None] = {}


def object_types(tokens) -> dict[str, str | None]:
    """Resolve many object ids in one `git cat-file --batch-check` call (None = not an object)."""
    wanted = sorted({t for t in tokens if t not in _TYPE_CACHE})
    if wanted:
        proc = _git("cat-file", "--batch-check", stdin="\n".join(wanted) + "\n")
        lines = proc.stdout.splitlines()
        if len(lines) == len(wanted):
            # One output line per input line, in order; the first field is echoed canonically.
            for token, line in zip(wanted, lines):
                parts = line.split()
                _TYPE_CACHE[token] = None if (len(parts) < 2 or parts[1] == "missing") else parts[1]
        else:
            # Guard against a future git changing the pairing: fall back to one call per token.
            for token in wanted:
                one = _git("cat-file", "--batch-check", stdin=token + "\n").stdout.splitlines()
                parts = one[0].split() if one else []
                _TYPE_CACHE[token] = None if (len(parts) < 2 or parts[1] == "missing") else parts[1]
    return {t: _TYPE_CACHE.get(t) for t in tokens}


def object_type(token: str) -> str | None:
    return object_types([token]).get(token)


def resolve_commit(token: str) -> str | None:
    """Canonical commit sha for a full or abbreviated id, or None if it is not a commit."""
    if not re.fullmatch(r"[0-9a-f]{7,40}", token or ""):
        return None
    proc = _git("rev-parse", "--quiet", "--verify", f"{token}^{{commit}}")
    out = proc.stdout.strip()
    return out if _is_full_hex(out) else None


def tree_of(commit: str) -> str | None:
    sha = resolve_commit(commit)
    if sha is None:
        return None
    proc = _git("rev-parse", "--quiet", "--verify", f"{sha}^{{tree}}")
    out = proc.stdout.strip()
    return out if _is_full_hex(out) else None


# --------------------------------------------------------------------------- corpus

def annotated_tag_messages() -> dict[str, str]:
    """{tag name: message body} for every annotated tag in the repo."""
    names = _git(
        "for-each-ref", "refs/tags", "--format=%(refname:short)\t%(objecttype)"
    ).stdout.splitlines()
    out: dict[str, str] = {}
    for line in names:
        parts = line.split("\t")
        if len(parts) != 2 or parts[1] != "tag":
            continue
        name = parts[0]
        body = _git("cat-file", "tag", name).stdout
        # The tag object is "object/type/tag/tagger" headers, a blank line, then the message.
        _, _, message = body.partition("\n\n")
        out[name] = message
    return out


def gate_logs() -> dict[str, str]:
    return {
        p.name: p.read_text(encoding="utf-8", errors="replace")
        for p in sorted((REPO / "docs" / "evidence").glob(GATE_LOG_GLOB))
    }


def front_pages() -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in FRONT_PAGES:
        path = REPO / rel
        if path.exists():
            out[rel] = path.read_text(encoding="utf-8", errors="replace")
    return out


# --------------------------------------------------------------------------- helpers

def _blocks(text: str) -> tuple[list[str], dict[int, int], dict[int, str]]:
    """Split into blocks of contiguous non-blank lines; map line index -> block id -> block text."""
    lines = text.splitlines()
    block_of: dict[int, int] = {}
    block_text: dict[int, str] = {}
    bid = -1
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        bid += 1
        j = i
        while j + 1 < len(lines) and lines[j + 1].strip():
            j += 1
        block_text[bid] = "\n".join(lines[i : j + 1])
        for ln in range(i, j + 1):
            block_of[ln] = bid
        i = j + 1
    return lines, block_of, block_text


def _label_before(line: str, col: int) -> str | None:
    match = LABEL_RE.search(line[:col])
    return match.group(1).lower() if match else None


def _exemption(block: str) -> str | None:
    lowered = block.lower()
    for marker in DISCLOSURE_MARKERS:
        if marker in lowered:
            return f"disclosure:{marker}"
    for marker in EXTERNAL_MARKERS:
        if marker in lowered:
            return f"external:{marker}"
    return None


def scan_citations(source: str, text: str) -> list[dict]:
    """Rules 1-2 plus the prose pair claim, over one text. Returns violations (empty = clean)."""
    lines, block_of, block_text = _blocks(text)
    tokens = FULL_HEX_RE.findall(text)
    types = object_types(tokens)
    violations: list[dict] = []

    for match in FULL_HEX_RE.finditer(text):
        token = match.group(0)
        line_index = text.count("\n", 0, match.start())
        line = lines[line_index] if line_index < len(lines) else ""
        col = match.start() - (text.rfind("\n", 0, match.start()) + 1)
        actual = types.get(token)
        block = block_text.get(block_of.get(line_index, -1), "")
        if actual is None:
            reason = _exemption(block)
            if reason is None:
                violations.append(
                    {
                        "source": source,
                        "line": line_index + 1,
                        "kind": "unresolved-citation",
                        "token": token,
                        "detail": "quoted as a git object id; git cat-file -t finds no object, and the "
                        "surrounding block neither reports it as broken nor names an external repository",
                    }
                )
            continue
        claimed = _label_before(line, col)
        if claimed and claimed != actual:
            violations.append(
                {
                    "source": source,
                    "line": line_index + 1,
                    "kind": "type-mismatch",
                    "token": token,
                    "detail": f"labelled '{claimed}' but git cat-file -t says '{actual}'",
                }
            )

    for claimed_commit, claimed_tree in TREE_OF_CLAIM_RE.findall(text):
        real_tree = tree_of(claimed_commit)
        line_index = text.count("\n", 0, text.find(claimed_commit, 0))
        if real_tree is None:
            violations.append(
                {
                    "source": source,
                    "line": line_index + 1,
                    "kind": "tree-pair",
                    "token": claimed_commit,
                    "detail": "'the tree of <sha> is <sha>' names a commit that does not resolve",
                }
            )
        elif _is_full_hex(claimed_tree) and claimed_tree != real_tree:
            violations.append(
                {
                    "source": source,
                    "line": line_index + 1,
                    "kind": "tree-pair",
                    "token": claimed_tree,
                    "detail": f"stated as the tree of {claimed_commit} which is {real_tree}",
                }
            )
    return violations


def check_gate_log(source: str, text: str) -> list[dict]:
    """Rule 3 for a gate log: its Tree line must be the tree of its Commit line."""
    commits = COMMIT_HEADER_RE.findall(text)
    trees = TREE_HEADER_RE.findall(text)
    if not commits and not trees:
        return []
    violations: list[dict] = []
    if len(commits) != 1 or len(trees) != 1:
        violations.append(
            {
                "source": source,
                "line": 1,
                "kind": "gate-log-header",
                "token": "",
                "detail": f"expected exactly one Commit and one Tree certification line, found "
                f"{len(commits)} and {len(trees)}",
            }
        )
        return violations
    commit, tree = commits[0], trees[0]
    if object_type(commit) != "commit":
        violations.append(
            {
                "source": source,
                "line": 1,
                "kind": "gate-log-header",
                "token": commit,
                "detail": f"'Commit under certification' is not a commit object (git says {object_type(commit)})",
            }
        )
    if object_type(tree) != "tree":
        violations.append(
            {
                "source": source,
                "line": 1,
                "kind": "gate-log-header",
                "token": tree,
                "detail": f"'Tree under certification' is not a tree object (git says {object_type(tree)})",
            }
        )
    real = tree_of(commit)
    if real is not None and real != tree:
        violations.append(
            {
                "source": source,
                "line": 1,
                "kind": "gate-log-header",
                "token": tree,
                "detail": f"log certifies commit {commit} whose tree is {real}",
            }
        )
    return violations


def check_tag_message(name: str, message: str, target: str) -> list[dict]:
    """Rule 3 for a tag message: a cited tree must belong to a commit the message names."""
    cited = [t for t in FULL_HEX_RE.findall(message) if object_type(t) == "tree"]
    if not cited:
        return []
    owned: set[str] = set()
    target_tree = tree_of(target)
    if target_tree:
        owned.add(target_tree)
    for token in set(HEX_TOKEN_RE.findall(message)):
        tree = tree_of(token)
        if tree:
            owned.add(tree)
    return [
        {
            "source": f"tag {name}",
            "line": 0,
            "kind": "tag-tree-citation",
            "token": tree_sha,
            "detail": "tag message cites a tree that is not the tree of any commit the message names "
            "(its target tree and every named commit's tree are the only admissible values)",
        }
        for tree_sha in cited
        if tree_sha not in owned
    ]


# --------------------------------------------------------------------------- fixtures

@pytest.fixture(scope="module")
def corpus():
    tags = annotated_tag_messages()
    logs = gate_logs()
    pages = front_pages()
    texts = {**{f"tag-message:{n}": m for n, m in tags.items()}, **logs, **pages}
    violations: list[dict] = []
    for source, text in texts.items():
        violations.extend(scan_citations(source, text))
    return {"tags": tags, "logs": logs, "pages": pages, "texts": texts, "violations": violations}


def _tag_targets() -> dict[str, str]:
    out = {}
    for line in _git("for-each-ref", "refs/tags", "--format=%(refname:short)\t%(objectname)").stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            out[parts[0]] = parts[1]
    return out


def _unused_hash() -> str:
    """A 40-hex token that is certainly not an object in this repo."""
    candidate = "f4d45844" + "0" * 32
    assert object_type(candidate) is None, candidate
    return candidate


# --------------------------------------------------------------------------- real-tree checks

def test_corpus_actually_covers_tag_messages_gate_logs_and_front_pages(corpus):
    """An inert guard is the F36 class: prove this scan is looking at real artifacts."""
    assert len(corpus["tags"]) >= 20, corpus["tags"].keys()
    assert len(corpus["logs"]) >= 3, list(corpus["logs"])
    assert len(corpus["pages"]) == len(FRONT_PAGES), list(corpus["pages"])
    tokens = sum(len(FULL_HEX_RE.findall(t)) for t in corpus["texts"].values())
    assert tokens >= 20, f"only {tokens} 40-hex citations in scope -- the scan is silent"


def test_no_citation_in_a_certification_artifact_fails_to_resolve_or_claims_the_wrong_type(corpus):
    hard = [v for v in corpus["violations"]]
    assert not hard, "\n".join(
        f"{v['source']}:{v['line']} {v['kind']} {v['token']} -- {v['detail']}" for v in hard
    )


def test_gate_log_headers_certify_a_commit_and_its_tree(corpus):
    checked = 0
    for name, text in corpus["logs"].items():
        found_commit = COMMIT_HEADER_RE.search(text)
        found_tree = TREE_HEADER_RE.search(text)
        if not (found_commit and found_tree):
            assert name in PRE_F42_GATE_LOGS, (
                f"{name} has no Commit/Tree certification header and is not a declared pre-F42 log"
            )
            continue
        violations = check_gate_log(name, text)
        assert not violations, violations
        checked += 1
    assert checked >= 3, checked


def test_the_pre_f42_log_exemption_is_exact_and_not_stale(corpus):
    """A closed exemption list: every headerless log is declared, and every declaration is still headerless."""
    headerless = {
        name
        for name, text in corpus["logs"].items()
        if not (COMMIT_HEADER_RE.search(text) and TREE_HEADER_RE.search(text))
    }
    undeclared = headerless - PRE_F42_GATE_LOGS
    stale = {n for n in PRE_F42_GATE_LOGS if n not in headerless}
    assert not undeclared, f"logs missing a header with no declared exemption: {sorted(undeclared)}"
    assert not stale, f"declared pre-F42 exemptions that now have a header or no longer exist: {sorted(stale)}"
    assert len(PRE_F42_GATE_LOGS) == len(headerless), (len(PRE_F42_GATE_LOGS), len(headerless))


def test_tag_messages_that_cite_a_tree_name_the_commit_whose_tree_it_is(corpus):
    targets = _tag_targets()
    citing = 0
    for name, message in corpus["tags"].items():
        violations = check_tag_message(name, message, targets[name])
        assert not violations, violations
        if any(object_type(t) == "tree" for t in FULL_HEX_RE.findall(message)):
            citing += 1
    assert citing >= 1, "no tag cites a tree -- the rule is untested on real data"


def test_prose_tree_of_claims_state_the_real_pair(corpus):
    claims = 0
    for source, text in corpus["texts"].items():
        for commit_sha, tree_sha in TREE_OF_CLAIM_RE.findall(text):
            claims += 1
            real = tree_of(commit_sha)
            assert real is not None, (source, commit_sha)
            assert tree_sha == real, (source, commit_sha, tree_sha, real)
    assert claims >= 1, "no 'tree of <sha> is <sha>' claim in scope -- rule 3 prose branch untested"


def test_the_f48_bogus_tree_hash_is_confined_to_blocks_that_call_it_broken(corpus):
    """The one knowingly-unresolvable hash in the docs stays quarantined inside its disclosure."""
    bogus = "f4d458443b6c5995b5c844990b20d6a974b7127b"
    assert object_type(bogus) is None
    occurrences = 0
    for source, text in corpus["texts"].items():
        lines, block_of, block_text = _blocks(text)
        for match in FULL_HEX_RE.finditer(text):
            if match.group(0) != bogus:
                continue
            occurrences += 1
            line_index = text.count("\n", 0, match.start())
            block = block_text.get(block_of.get(line_index, -1), "")
            assert _exemption(block) is not None, f"{source}:{line_index + 1} quotes the bogus hash without calling it broken"
    assert occurrences >= 2, occurrences
    # The correction is present wherever the error is quoted, so a reader gets the real value too.
    assert "f4d45844da2d1a2f7bfde6df9a49b5327da982fe" in corpus["pages"]["docs/INTEGRITY_FINDINGS_2026-11-04.md"]


def test_an_unresolvable_external_pin_is_cited_only_where_its_repository_is_named(corpus):
    """The WIMpy_NREFT commit sha is a real commit in another repository, not a citation here."""
    external = "50581c637069305a3def3865462ef1b4ed9a616d"
    assert object_type(external) is None
    seen = 0
    for source, text in corpus["texts"].items():
        lines, block_of, block_text = _blocks(text)
        for match in FULL_HEX_RE.finditer(text):
            if match.group(0) != external:
                continue
            seen += 1
            line_index = text.count("\n", 0, match.start())
            block = block_text.get(block_of.get(line_index, -1), "")
            assert "github.com/" in block or "git+https" in block, (
                f"{source}:{line_index + 1} cites an out-of-repo sha without naming its repository"
            )
    assert seen >= 1, seen


# --------------------------------------------------------------------------- falsification

def test_an_unresolved_hash_quoted_as_certification_is_caught():
    bogus = _unused_hash()
    head = _git("rev-parse", "HEAD").stdout.strip()
    violations = scan_citations("synthetic", f"the gate ran on commit {head} (tree {bogus})\n")
    assert len(violations) == 1 and violations[0]["kind"] == "unresolved-citation", violations


def test_an_unresolved_hash_quoted_as_an_error_is_not_flagged():
    bogus = _unused_hash()
    text = (
        "the tag quoted tree " + bogus + "; the hash resolves to no object "
        "(`git cat-file -t` -> exit 128)\n"
    )
    assert scan_citations("synthetic", text) == [], scan_citations("synthetic", text)


def test_a_real_tree_labelled_commit_is_caught_as_a_type_mismatch():
    tree = tree_of(_git("rev-parse", "HEAD").stdout.strip())
    assert tree
    violations = scan_citations("synthetic", f"certified commit {tree}\n")
    assert len(violations) == 1 and violations[0]["kind"] == "type-mismatch", violations


def test_a_real_commit_labelled_tree_is_caught_as_a_type_mismatch():
    head = _git("rev-parse", "HEAD").stdout.strip()
    violations = scan_citations("synthetic", f"certified tree {head}\n")
    assert len(violations) == 1 and violations[0]["kind"] == "type-mismatch", violations


def test_a_wrong_but_real_tree_in_a_tree_of_claim_is_caught():
    head = _git("rev-parse", "HEAD").stdout.strip()
    other = _git("rev-parse", "HEAD~1").stdout.strip()
    wrong_tree = tree_of(other)
    assert wrong_tree and wrong_tree != tree_of(head)
    violations = scan_citations("synthetic", f"the tree of {head[:10]} is {wrong_tree}\n")
    assert any(v["kind"] == "tree-pair" for v in violations), violations


def test_a_true_tree_of_claim_passes():
    head = _git("rev-parse", "HEAD").stdout.strip()
    text = f"the tree of {head[:10]} is {tree_of(head)}\n"
    assert scan_citations("synthetic", text) == [], scan_citations("synthetic", text)


def test_a_tag_citing_a_tree_it_does_not_own_is_caught():
    head = _git("rev-parse", "HEAD").stdout.strip()
    other_tree = tree_of(_git("rev-parse", "HEAD~3").stdout.strip())
    assert other_tree and other_tree != tree_of(head)
    message = f"Certification: the gate ran on {head[:9]} (tree {other_tree}).\n"
    violations = check_tag_message("synthetic-tag", message, head)
    assert len(violations) == 1 and violations[0]["kind"] == "tag-tree-citation", violations


def test_a_tag_citing_its_own_target_tree_passes():
    head = _git("rev-parse", "HEAD").stdout.strip()
    message = f"Certification: the gate ran on {head[:9]} (tree {tree_of(head)}).\n"
    assert check_tag_message("synthetic-tag", message, head) == []


def test_a_gate_log_whose_tree_line_is_not_its_commit_s_tree_is_caught():
    head = _git("rev-parse", "HEAD").stdout.strip()
    wrong_tree = tree_of(_git("rev-parse", "HEAD~1").stdout.strip())
    assert wrong_tree and wrong_tree != tree_of(head)
    text = (
        f"Commit under certification: {head}\n"
        f"Tree under certification:  {wrong_tree}\n"
        "\n[L1/15] ...\n"
    )
    violations = check_gate_log("synthetic_log.txt", text)
    assert any(v["kind"] == "gate-log-header" for v in violations), violations
    assert any(head in v["detail"] for v in violations), violations


def test_a_gate_log_that_drops_its_tree_line_is_caught():
    head = _git("rev-parse", "HEAD").stdout.strip()
    text = f"Commit under certification: {head}\n\n[L1/15] ...\n"
    violations = check_gate_log("synthetic_log.txt", text)
    assert any(v["kind"] == "gate-log-header" for v in violations), violations


def test_content_hashes_are_not_mistaken_for_git_object_citations():
    sha256 = "9" * 64
    md5 = "1" * 32
    text = f"sha256 {sha256} and md5 {md5} and a 39-hex typo {('7' * 39)}\n"
    assert scan_citations("synthetic", text) == [], scan_citations("synthetic", text)
    assert not FULL_HEX_RE.findall(text)


def test_the_scan_reproduces_finding_f48_itself():
    """The guard is credited only if it catches the error it was written for.

    This is the sentence the T215 tag was actually cut with (finding F48): the certified commit named
    with its true full sha, and a tree hash typed from working notes that resolves to no object. Nothing
    in that block reports the hash as broken, so rule 1 must fire.
    """
    f48_message = (
        "Certification: the strict 15-layer gate ran on commit "
        "cbcdba163767ab83a88e7731a22572d16f67d0fd "
        "(tree f4d458443b6c5995b5c844990b20d6a974b7127b) with T82_README_DRIFT_LENIENT unset: "
        "15/15 PASS.\n"
    )
    violations = scan_citations("tag-message:synthetic-f48", f48_message)
    assert len(violations) == 1, violations
    assert violations[0]["kind"] == "unresolved-citation", violations
    assert violations[0]["token"] == "f4d458443b6c5995b5c844990b20d6a974b7127b", violations
    # And the corrected sentence the tag now carries is clean.
    corrected = f48_message.replace(
        "f4d458443b6c5995b5c844990b20d6a974b7127b",
        "f4d45844da2d1a2f7bfde6df9a49b5327da982fe",
    )
    assert scan_citations("tag-message:synthetic-f48", corrected) == []


def test_the_scan_reports_every_violation_it_finds_not_only_the_first():
    bogus = _unused_hash()
    head = _git("rev-parse", "HEAD").stdout.strip()
    head_tree = tree_of(head)
    text = (
        f"first run certified commit {head} (tree {bogus})\n"
        "\n"
        f"second run certified commit {head_tree}\n"
    )
    violations = scan_citations("synthetic", text)
    kinds = sorted(v["kind"] for v in violations)
    assert kinds == ["type-mismatch", "unresolved-citation"], violations
    assert {v["line"] for v in violations} == {1, 3}, violations
