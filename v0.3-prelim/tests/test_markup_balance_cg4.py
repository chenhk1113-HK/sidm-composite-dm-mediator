"""Guard for coverage gap CG-4: markdown emphasis must be balanced in every paragraph.

A block carrying an ODD number of `**` renders at least one literal `**`, and the reader sees
asterisks instead of emphasis. Before this round nothing in the gate looked at markup balance,
so a lost marker was invisible (measured: 21 such lines / 13 such blocks in the paper draft on
2026-11-07, repaired by the CG-4 markup pass; 70 lines historically).

Balance is checked per blank-line-separated block, which is the scope CommonMark actually
emphasises within: a bold span may legitimately wrap across lines inside one paragraph, so a
per-LINE rule would false-fire on ordinary wrapped prose.

Checked: the paper draft and the four front-page documents. Also checks that every pair is
well-formed under CommonMark flanking (opener not followed by a space, closer not preceded by
a space), which is the other way emphasis silently fails.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = [
    os.path.join(ROOT, "v0.3-prelim", "docs", "PAPER_V1_DRAFT.md"),
    os.path.join(ROOT, "CURRENT.md"),
    os.path.join(ROOT, "README.md"),
    os.path.join(ROOT, "EXTRACT.md"),
    os.path.join(ROOT, "docs", "LAYMAN_SUMMARY.md"),
]


def _strip_code_spans(body):
    """Replace inline-code spans with a sentinel so emphasis adjacency is preserved.

    `**Paper at `path`**` is valid emphasis; deleting the code span would leave `**Paper at **`
    and report a space-flanked closer that does not exist in the real document.
    """
    return re.sub(r"`[^`]*`", "\x00", body)


def _blocks(text):
    """Paragraph blocks as (start_line, joined_text); blank lines separate them."""
    blocks, cur, start = [], [], None
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            if cur:
                blocks.append((start, " ".join(cur)))
                cur, start = [], None
        else:
            if start is None:
                start = i
            cur.append(line)
    if cur:
        blocks.append((start, " ".join(cur)))
    return blocks


class MarkupBalance(unittest.TestCase):

    def test_documents_exist(self):
        for d in DOCS:
            self.assertTrue(os.path.exists(d), f"missing document under markup guard: {d}")

    def test_no_block_carries_an_unbalanced_emphasis_marker(self):
        bad = []
        for d in DOCS:
            with open(d, encoding="utf-8") as f:
                for start, body in _blocks(f.read()):
                    body = _strip_code_spans(body)
                    if body.count("**") % 2:
                        bad.append((os.path.basename(d), start, body.count("**")))
        self.assertEqual(bad, [], f"literal ** will render in these blocks: {bad[:10]}")

    # RATCHET, not a weakening. One residual malformed pair is known and pinned:
    # PAPER_V1_DRAFT.md, the §2.7 Concerto cross-check verdict block. Its emphasis markers are
    # mis-ordered by the author (a span opened at `**Conclusion:**` closes at `**First**`, so
    # "First" never becomes bold), and repairing it means rewriting the paragraph's prose - the
    # same block also shows dropped characters (`chain is valid.16σ` where the sentence states
    # 3.16σ later). Marker arithmetic cannot fix that without guessing physics prose, so it is
    # recorded as finding F34 for an author pass and pinned here. A NEW malformed pair anywhere
    # fails this test; when the residual is fixed, delete it from the pinned list.
    PINNED_MALFORMED = [
        ("PAPER_V1_DRAFT.md", "consistent across mass scale, but environmental and model"),
    ]

    def test_every_emphasis_pair_is_well_formed(self):
        found = []
        for d in DOCS:
            with open(d, encoding="utf-8") as f:
                for start, body in _blocks(f.read()):
                    body = _strip_code_spans(body)
                    pos = [m.start() for m in re.finditer(r"\*\*", body)]
                    for j in range(0, len(pos) - 1, 2):
                        o, c = pos[j], pos[j + 1]
                        opener_ok = o + 2 < len(body) and body[o + 2] != " "
                        closer_ok = c > 0 and body[c - 1] != " "
                        if not (opener_ok and closer_ok):
                            snippet = body[max(o, 0):min(c + 2, len(body))]
                            frag = next((s for s in self.PINNED_MALFORMED
                                         if s[1] in snippet), None)
                            if frag is not None:
                                continue
                            found.append((os.path.basename(d), start,
                                          body[max(o - 25, 0):c + 25]))
        self.assertEqual(found, [],
                         f"emphasis pairs that will not render (space-flanked): {found[:5]}")

    def test_pinned_residual_still_needs_the_author_pass(self):
        """Fails when F34's paragraph is rewritten, so the pinned list gets cleaned up."""
        residuals = 0
        for d in DOCS:
            with open(d, encoding="utf-8") as f:
                for _, body in _blocks(f.read()):
                    body = _strip_code_spans(body)
                    pos = [m.start() for m in re.finditer(r"\*\*", body)]
                    for j in range(0, len(pos) - 1, 2):
                        o, c = pos[j], pos[j + 1]
                        if (o + 2 < len(body) and body[o + 2] != " "
                                and c > 0 and body[c - 1] != " "):
                            continue
                        if any(s in body[max(o, 0):c + 2] for _, s in self.PINNED_MALFORMED):
                            residuals += 1
        self.assertEqual(residuals, len(self.PINNED_MALFORMED),
                         f"pinned markup residuals ({len(self.PINNED_MALFORMED)}) no longer match "
                         f"the {residuals} found - update PINNED_MALFORMED (F34 status)")


if __name__ == "__main__":
    unittest.main()
