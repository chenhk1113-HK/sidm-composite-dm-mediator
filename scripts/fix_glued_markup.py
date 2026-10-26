"""Repair the glued-emphasis markup defect in PAPER_V1_DRAFT.md.

THE DEFECT
----------
Commit 799f4ef ("R88 paper cleanup") ran a bulk whitespace normalisation over the
paper that stripped the spaces around `**` emphasis markers and joined some
paragraphs (and headings) onto the line that followed them. The visible prose
was preserved, but the MARKDOWN SEMANTICS were destroyed.

Two concrete symptoms:

1. In any CommonMark renderer (GitHub, pandoc, VS Code preview) the marker run
   survives as LITERAL `**` text, because a `**` delimiter glued to an
   adjacent word can neither open nor close emphasis (CommonMark 6.2 flanking
   rules). Measured on the pre-fix paper: 70 lines left a literal `**`, and
   199 literal `**` survived in the whole document.

2. In the project's own PDF builder (`scripts/t237_pdf_build.py`, line 71:
   `text = line.replace('**','').replace('*','').replace('`','')`) the markers
   are STRIPPED, so the reader sees GLUED WORDS instead -- e.g.
   `the**effective free-parameter count**is` -> "theeffective free-parameter
   countis". 269 such glue points exist.

THE INVARIANT
-------------
A markup repair may change ONLY whitespace and emphasis markers. The `core()`
signature -- the text with all whitespace and all `*` removed -- must be
byte-identical before and after. That is what makes a mechanical repair safe:
not one word, number, symbol, or citation can change. A space inserted inside
a backtick code span also changes `core()`, which is exactly how the earlier
naive "insert a space" rule got caught (it fixed 0 of 70 lines and corrupted
69 of 70 by editing inside code spans).

THE ORACLE
----------
Emphasis PAIRING is decided by the parser over a whole block, so a per-run
flanking model cannot tell an opener from a closer. markdown-it is therefore
used as the ORACLE: a candidate repair is accepted only when the renderer
itself reports the block as clean.

REPAIR OPERATIONS (tried in this order, exhaustively, at each step)
-------------------------------------------------------------------
  1. SPACE   insert one space at a `**` boundary, restoring its flanking.
             Whitespace only -- the safest repair, and it fixes most blocks.
  2. ADD     add a missing closing `**` at the end of the phrase it governs
             (after a sentence end, or at the end of the line) and at a word
             boundary. This restores emphasis that 799f4ef's join left
             unmatched, without inventing a new one.
  3. REMOVE  drop a stray unmatched `**` that has no partner at all.

Every intermediate state is checked against the renderer AND against the
`core()` invariant; a state that violates either is rejected.

Usage:
    python scripts/fix_glued_markup.py            # dry run, prints a plan
    python scripts/fix_glued_markup.py --apply    # write the file
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

try:
    from markdown_it import MarkdownIt
except ImportError:  # pragma: no cover
    raise SystemExit("markdown_it is required: pip install markdown-it-py")

MD = MarkdownIt("commonmark")
WORD = re.compile(r"[^\W\s]", re.UNICODE)
SENT_END = re.compile(r"(?<![A-Za-z])[.!?](?=\s|$)")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def render_plain(text: str) -> str:
    """Render and strip tags: the text a reader actually sees."""
    return re.sub(r"<[^>]+>", "", MD.render(text))


def literal_count(text: str) -> int:
    """How many literal '**' survive the render."""
    return render_plain(text).count("**")


def core(text: str) -> str:
    """The signature a repair must preserve: no whitespace, no markers."""
    return re.sub(r"[\s*]+", "", text)


def code_span_ranges(line: str) -> list[tuple[int, int]]:
    """Character ranges covered by backtick code spans (never edit inside)."""
    prot: list[tuple[int, int]] = []
    i = 0
    while i < len(line):
        m = re.match(r"(`+)", line[i:])
        if not m:
            break
        ticks = m.group(1)
        close = line.find(ticks, i + len(ticks))
        if close == -1:
            break
        prot.append((i, close + len(ticks)))
        i = close + len(ticks)
    return prot


def in_code(pos: int, prot: list[tuple[int, int]]) -> bool:
    return any(a <= pos < b for a, b in prot)


def code_contents(text: str) -> list[str]:
    """Exact contents of each backtick code span."""
    out: list[str] = []
    i = 0
    while i < len(text):
        m = re.match(r"(`+)", text[i:])
        if not m:
            break
        ticks = m.group(1)
        close = text.find(ticks, i + len(ticks))
        if close == -1:
            break
        out.append(text[i + len(ticks):close])
        i = close + len(ticks)
    return out


def candidate_positions(line: str) -> list[int]:
    """Offsets where a space might restore a `**` run's flanking."""
    prot = code_span_ranges(line)
    positions: set[int] = set()
    for m in re.finditer(r"\*\*", line):
        s, e = m.span()
        if in_code(s, prot):
            continue
        for p in (s, e):
            if any(a < p < b for a, b in prot):
                continue
            positions.add(p)
    return sorted(positions)


def insert_spaces(line: str, positions: list[int]) -> str:
    out: list[str] = []
    for i, ch in enumerate(line):
        if i in positions:
            out.append(" ")
        out.append(ch)
        if i + 1 in positions:
            out.append(" ")
    return "".join(out)


def phrase_close_positions(line: str) -> list[int]:
    """Offsets where a closing '**' may be added.

    The unmatched opener (if any) is the LAST `**` run in the block.
    The natural place to close it is at the end of the line/block, or
    after the last sentence. We avoid abbreviation issues entirely by
    simply preferring the latest possible position.
    """
    prot = code_span_ranges(line)
    out: list[int] = []

    # The most natural place: end of line (where a dangling opener
    # would naturally close).
    if line and not line[-1].isspace():
        p = len(line)
        if not any(a < p < b for a, b in prot):
            before = line[p - 1]
            if not WORD.match(before):
                out.append(p)

    # Also consider sentence ends, but only AFTER the last `**` run
    # (so we don't accidentally close too early).
    last_run_end = -1
    for m in re.finditer(r"\*\*", line):
        if not in_code(m.start(), code_span_ranges(line)):
            last_run_end = max(last_run_end, m.end())
    
    for m in SENT_END.finditer(line):
        p = m.end()
        if p <= last_run_end:
            continue
        if p < len(line) and not line[p].isspace():
            continue
        before = line[p - 1] if p > 0 else ""
        after = line[p] if p < len(line) else ""
        b_word = bool(before) and bool(WORD.match(before))
        a_word = bool(after) and bool(WORD.match(after))
        if not b_word and not a_word:
            out.append(p)

    if line and not line[-1].isspace():
        p = len(line)
        if not any(a < p < b for a, b in prot):
            before = line[p - 1]
            if not WORD.match(before):
                out.append(p)
    
    return sorted(set(out))


# --------------------------------------------------------------------------
# block discovery
# --------------------------------------------------------------------------
def find_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """Consecutive non-blank lines form one CommonMark block."""
    out: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].strip():
            j += 1
        out.append((i, j))
        i = j
    return out


# --------------------------------------------------------------------------
# the repair search
# --------------------------------------------------------------------------
def _preserved(block: list[str], base_core: str, base_code: list[str]) -> bool:
    text = "\n".join(block)
    return core(text) == base_core and code_contents(text) == base_code


def _space_candidates(block, base_core, base_code):
    out = []
    for k, line in enumerate(block):
        for p in candidate_positions(line):
            cand = list(block)
            cand[k] = insert_spaces(line, [p])
            if _preserved(cand, base_core, base_code):
                out.append(cand)
    return out


def _add_candidates(block, base_core, base_code):
    out = []
    for k, line in enumerate(block):
        for p in phrase_close_positions(line):
            cand = list(block)
            cand[k] = line[:p] + "**" + line[p:]
            if _preserved(cand, base_core, base_code):
                out.append(cand)
    return out


def _remove_candidates(block, base_core, base_code):
    out = []
    for k, line in enumerate(block):
        prot = code_span_ranges(line)
        for m in re.finditer(r"\*\*", line):
            s, e = m.span()
            if in_code(s, prot):
                continue
            cand = list(block)
            cand[k] = line[:s] + line[e:]
            if _preserved(cand, base_core, base_code):
                out.append(cand)
    return out


def repair_block(block: list[str], max_rounds: int = 12
                 ) -> tuple[list[str], str] | None:
    """Repair one block.

    At each round the three operation classes are tried in the order
    SPACE, ADD, REMOVE. The first class that can drive the block's literal
    count to zero wins. If no class can, the class that makes the most
    progress is used and the search continues, so a block needing several
    spaces still gets them.
    """
    text = "\n".join(block)
    base_core = core(text)
    base_code = code_contents(text)
    if literal_count(text) == 0:
        return block, "clean"

    work = list(block)
    for _ in range(max_rounds):
        cur_lit = literal_count("\n".join(work))
        if cur_lit == 0:
            return work, "repaired"

        best: tuple[int, list[str], str] | None = None
        for kind, gen in (("space", _space_candidates),
                          ("add", _add_candidates),
                          ("remove", _remove_candidates)):
            cands = gen(work, base_core, base_code)
            if not cands:
                continue
            scored = [(literal_count("\n".join(c)), c) for c in cands]
            best_lit = min(s for s, _ in scored)
            if best_lit == 0:
                return next(c for s, c in scored if s == 0), f"{kind}-final"
            if best is None or best_lit < best[0]:
                best = (best_lit, next(c for s, c in scored if s == best_lit), kind)
        if best is None or best[0] >= cur_lit:
            return None
        work = best[1]
    return None


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the file")
    ap.add_argument("--report", help="write a JSON report of the plan here")
    args = ap.parse_args()

    original = PAPER.read_text(encoding="utf-8")
    lines = original.split("\n")

    blocks = find_blocks(lines)
    dirty = [(i, j) for i, j in blocks
             if literal_count("\n".join(lines[i:j])) > 0]
    print(f"blocks with a literal '**' after rendering: {len(dirty)}")

    plan: list[dict] = []
    failures: list[tuple[int, int]] = []
    for i, j in dirty:
        blk = lines[i:j]
        res = repair_block(blk)
        if res is None:
            failures.append((i, j))
            continue
        new_block, method = res
        plan.append({
            "start": i, "end": j, "method": method,
            "before": blk, "after": new_block,
        })

    print(f"planned repairs: {len(plan)}   unresolved: {len(failures)}")
    for m, c in Counter(p["method"] for p in plan).most_common():
        print(f"    {m}: {c}")
    if failures:
        print("\nUNRESOLVED (need manual review):")
        for i, j in failures:
            print(f"  L{i+1}-{j}: {lines[i][:110]}")

    if args.report:
        Path(args.report).write_text(json.dumps(plan, indent=1, ensure_ascii=False),
                                     encoding="utf-8")
        print(f"plan written to {args.report}")

    if args.apply and plan:
        out = list(lines)
        for p in sorted(plan, key=lambda p: -p["start"]):
            s, e = p["start"], p["end"]
            assert out[s:e] == p["before"], f"block at L{s+1} changed underneath us"
            out[s:e] = p["after"]
        new_text = "\n".join(out)
        PAPER.write_text(new_text, encoding="utf-8")
        print(f"\nwrote {PAPER}")

        final = PAPER.read_text(encoding="utf-8")
        flines = final.split("\n")
        print("--- verification ---")
        print(f"  literal '**' in the whole document: "
              f"{literal_count(final)} (was {literal_count(original)})")
        still = [i + 1 for i, l in enumerate(flines)
                 if "**" in l and literal_count(l) > 0]
        print(f"  lines still leaving a literal '**': {len(still)} {still[:10]}")
        print(f"  core() signature preserved: {core(original) == core(final)}")
        print(f"  code spans preserved: "
              f"{code_contents(original) == code_contents(final)}")

        def glue_points(text: str) -> int:
            n = 0
            for l in text.split("\n"):
                prot = code_span_ranges(l)
                for m in re.finditer(r"\*\*", l):
                    s, e = m.span()
                    if in_code(s, prot):
                        continue
                    cb = l[s - 1] if s > 0 else ""
                    ca = l[e] if e < len(l) else ""
                    if cb and ca and WORD.match(cb) and WORD.match(ca):
                        n += 1
            return n

        print(f"  glue points (fused words): "
              f"{glue_points(final)} (was {glue_points(original)})")
        print(f"  line count: {len(lines)} -> {len(flines)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
