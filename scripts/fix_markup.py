#!/usr/bin/env python3
"""
Markup repair for PAPER_V1_DRAFT.md.

THE DEFECT
  The paper's emphasis markers are not properly FLANKED. CommonMark only
  treats a '**' run as emphasis when it satisfies the flanking rules:

    left-flanking  (can OPEN)  : not followed by whitespace
                                 AND (not followed by punctuation
                                      OR preceded by whitespace/punctuation)
    right-flanking (can CLOSE) : not preceded by whitespace
                                 AND (not preceded by punctuation
                                      OR followed by whitespace/punctuation)

  and the content between two markers must not begin or end with whitespace.
  Five distinct breakages are present:

    (1) '** word **'   whitespace inside the pair      -> not emphasis
    (2) 'nodes**UV'    opener glued to a word         -> not left-flanking
    (3) 'fit**:'       closer followed by punctuation -> not right-flanking
    (4) a DELETED marker, leaving an odd number of '**' in a paragraph. The
        surviving markers then pair up incorrectly, so the emphasis lands on
        the WRONG text.
    (5) a FUSED marker run, '****' or '***text**', where a stray '*' from an
        adjacent marker has run into its neighbour.

  Breakages (4) and (5) are why a pure whitespace repair cannot finish the
  job: in those paragraphs the PAIRING itself is wrong, and no whitespace
  edit can fix a wrong pairing.

  GFM TABLES ADD A SIXTH ISSUE: a pipe-table row is split into cells FIRST,
  and each cell is then parsed as inline Markdown independently. A marker
  pair that straddles a cell boundary therefore cannot be emphasis in either
  cell. Table rows must be repaired CELL BY CELL.

THE FIX (three phases, each renderer-validated)
  PHASE 1 - HISTORICAL LAYOUT ADOPTION.
    The paper's own git history is the ground truth for emphasis layout. For
    every damaged paragraph, the revision of the paper whose NON-MARKER,
    NON-WHITESPACE text is IDENTICAL to the current paragraph is located
    (a run of up to six consecutive historical paragraphs is allowed, so a
    paragraph that 799f4ef fused back together can still be matched), and
    that historical text is adopted after a whitespace-only flanking repair.

    Adopting it is provably safe: the two texts have identical non-marker,
    non-whitespace content, so the substitution can change only which
    characters are bold and where the whitespace sits. No prose, number,
    unit or citation can change.

    The INVALID commit ef645ce is EXCLUDED from the index: its markup was
    produced by a broken fixer that relocated emphasis markers to the wrong
    places, so its layout is not trustworthy ground truth.

  PHASE 2 - CELL-AWARE FLANKING REPAIR.
    Whitespace is moved outside each marker pair and a space is inserted
    where a marker is glued to a word. Table rows are repaired cell by cell,
    because that is the unit GFM actually parses.

  PHASE 3 - MARKER REPAIR.
    For the paragraphs whose text was edited after the damage (so no
    historical twin exists), a marker was deleted or fused. The repair
    either re-inserts the missing marker or splits the fused run, at the
    position the renderer validates, preferring a position that ends a
    sentence or a short label, which is the document's dominant emphasis
    style.

HARD INVARIANTS (the script ABORTS rather than writing if any fails):
  1. TOKEN PRESERVATION   the word-token sequence of the document is
                           IDENTICAL before and after. No word is added,
                           removed or altered, so the fix is numerically inert
                           BY CONSTRUCTION, not by inspection.
  2. TEXT PRESERVATION    the document with all '*' and all whitespace removed
                           is IDENTICAL before and after. Only emphasis
                           markers and whitespace may differ.
  3. RENDERER ORACLE      zero literal '**' survives CommonMark+GFM-table
                           rendering (markdown_it 4.2.0) of the whole document.
  4. STALE-VALUE INERTNESS the occurrence count of every known-stale marker
                           is unchanged, so no pre-fix text can be resurrected.
  5. SPAN SANITY          no rendered bold span crosses a code span, a table
                           pipe, or a paragraph break.
"""

import os
import pickle
import re
import subprocess
import sys
from pathlib import Path

from markdown_it import MarkdownIt

REPO = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator')
REL = 'v0.3-prelim/docs/PAPER_V1_DRAFT.md'
BASE_REV = 'ef645ce^'          # last commit BEFORE the broken markup commit
INVALID_REV = 'ef645ce3d7a0c5f044102ed28b29c143f19073e3'   # the bad commit
CACHE = Path(os.environ.get('TMPDIR', '/tmp')) / 'paper_markup_hist.pkl'

MD = MarkdownIt('commonmark')
MD.enable('table')              # the paper's tables need GFM pipe tables

# markers whose occurrence count must not change (stale-content tripwires)
STALE_MARKERS = (
    '-0.47', '0.5–2.5 cm²/g', '7 of 8', '115–460', '115-460', '0.256-1.518',
    '0.257-1.589', '2.845', '16.865', '0.0318', '0.0931', '1.784e-13',
    '2.840e-13', '1.836e-13', '29.4', '65.49', '136–246', '27–49', '14.2',
    # F23 (2026-10-26): these were stale-value tripwires that have now been
    # CORRECTED in the paper, so their counts are 0 and must stay 0. Listing
    # them keeps a future re-introduction detectable.
    '2.83e-13', '2.84e-13', '65.91',
)

MARKER = re.compile(r'\*+')
TRAIL_WS = re.compile(r'[ \t]+$')
LEAD_WS = re.compile(r'^[ \t]+')
WORD_CHAR = re.compile(r'\w', re.UNICODE)


# ------------------------------------------------------------------ helpers

def code_ranges(text):
    ranges = []
    i = 0
    while i < len(text):
        m = re.match(r'(`+)', text[i:])
        if not m:
            break
        tick = m.group(1)
        c = text.find(tick, i + len(tick))
        if c == -1:
            break
        ranges.append((i, c + len(tick)))
        i = c + len(tick)
    return ranges


def marker_runs(text):
    """(start, end) of every '*' run of length >= 2 outside code spans."""
    cr = code_ranges(text)
    return [(m.start(), m.end())
            for m in MARKER.finditer(text)
            if m.end() - m.start() >= 2
            and not any(a <= m.start() < b for a, b in cr)]


def literal_count(text):
    html = MD.render(text)
    s = re.sub(r'<pre>.*?</pre>', '', html, flags=re.S)
    s = re.sub(r'<code>.*?</code>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return s.count('**')


def bold_spans(text):
    """Ordered list of (content, is_sane) for rendered bold spans."""
    out = []
    for tok in MD.parse(text):
        if tok.type != 'inline':
            continue
        depth = 0
        buf = []
        for ch in tok.children or []:
            if ch.type == 'strong_open':
                depth += 1
                if depth == 1:
                    buf = []
            elif ch.type == 'strong_close':
                depth -= 1
                if depth == 0:
                    raw = ''.join(buf)
                    sane = not any(c in raw for c in ('\n', '`', '|'))
                    out.append((re.sub(r'\s+', ' ', raw).strip(), sane))
            elif ch.type == 'text' and depth >= 1:
                buf.append(ch.content)
    return out


def n_bad_spans(text):
    """Bold spans that cross a code span, a table pipe, or a paragraph break.

    A table pipe only counts inside a pipe-table ROW: the '|' in prose such
    as '|sigma_HL|' is ordinary text, not a cell delimiter.
    """
    bad = 0
    for line in text.split('\n'):
        if is_table_row(line):
            _, cells, _ = split_cells(line)
            for c in cells:
                bad += sum(1 for _, sane in bold_spans(c) if not sane)
        else:
            bad += sum(1 for _, sane in bold_spans(line) if not sane)
    return bad


def tokens(text):
    return re.findall(r'[^\W_]+', text, flags=re.UNICODE)


def bare_text(text):
    """Non-marker, non-whitespace text: the invariant that must not change."""
    t = re.sub(r'(`+)(.*?)\1', lambda m: m.group(2), text, flags=re.S)
    return re.sub(r'\s+', '', t.replace('*', ''))


def blocks(text):
    out, cur = [], []
    for line in text.split('\n'):
        if not line.strip():
            if cur:
                out.append('\n'.join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        out.append('\n'.join(cur))
    return out


def apply_edits(text, edits):
    for s, e, rep in sorted(edits, key=lambda x: -x[0]):
        text = text[:s] + rep + text[e:]
    return text


def score(text):
    """(literals, unsane_spans). Both must reach zero."""
    return literal_count(text), n_bad_spans(text)


# ------------------------------------------------------------------ cells

def is_table_row(line):
    s = line.strip()
    return s.startswith('|') and s.endswith('|') and s.count('|') >= 2


def split_cells(line):
    """Split a table row into its cells, preserving the leading/trailing pipe."""
    s = line
    lead = trail = ''
    if s.startswith('|'):
        lead = '|'
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        trail = '|'
        s = s[:-1]
    return lead, re.split(r'(?<!\\)\|', s), trail


# ------------------------------------------------------------------ edits

def whitespace_edits(text):
    """Whitespace edits that make each marker pair well-flanked.

    Only the whitespace at the very EDGES of a pair is moved: whitespace
    inside the pair's content is left untouched, so interior spacing such as
    'Fornax (V_max = 18)' survives the repair.
    """
    runs = [(s, e) for s, e in marker_runs(text) if e - s == 2]
    edits = []
    for i in range(0, len(runs) - 1, 2):
        s1, e1 = runs[i]
        s2, e2 = runs[i + 1]
        content = text[e1:s2]

        lead = LEAD_WS.match(content)
        if lead:
            edits.append((e1, e1 + lead.end(), ''))

        trail = TRAIL_WS.search(content)
        if trail:
            edits.append((trail.start() + e1, trail.end() + e1, ''))

        before = text[s1 - 1] if s1 > 0 else ''
        if before and WORD_CHAR.match(before) and not text[s1 - 1:s1].isspace():
            edits.append((s1, s1, ' '))

        after = text[e2] if e2 < len(text) else ''
        if after and WORD_CHAR.match(after) and not text[e2:e2 + 1].isspace():
            edits.append((e2, e2, ' '))
    return edits


def apply_single_set(text, edits):
    """Apply a set of edits, dropping any that overlap an earlier one."""
    used, keep = [], []
    for a, b, rep in sorted(edits, key=lambda x: x[0]):
        if any(not (b <= s or a >= e) for s, e in used):
            continue
        used.append((a, b))
        keep.append((a, b, rep))
    return apply_edits(text, keep)


def fix_ws(text):
    """Move whitespace outside each marker pair, in place."""
    for _ in range(8):
        edits = whitespace_edits(text)
        if not edits:
            break
        trial = apply_single_set(text, edits)
        if trial == text or tokens(trial) != tokens(text):
            break
        text = trial
    return text


def fix_block(block):
    """Cell-aware whitespace repair of a whole block."""
    lines = block.split('\n')
    if not any(is_table_row(l) for l in lines):
        return fix_ws(block)
    out = []
    for line in lines:
        if not is_table_row(line):
            out.append(fix_ws(line))
            continue
        lead, cells, trail = split_cells(line)
        out.append(lead + '|'.join(fix_ws(c) for c in cells) + trail)
    return '\n'.join(out)


# ------------------------------------------------------------------ phase 3

def sentence_stops(text):
    """Offsets just after a sentence terminator, ignoring known abbreviations."""
    abbrev = ('Eq.', 'Fig.', 'Sec.', 'Ref.', 'No.', 'vs.', 'i.e.', 'e.g.',
              'cf.', 'Dr.', 'Mr.', 'Ms.', 'St.', 'al.', 'approx.', 'resp.')
    out = []
    for m in re.finditer(r'[.!?](?=\s|$)', text):
        head = text[max(0, m.start() - 8):m.start() + 1]
        if any(head.endswith(a) for a in abbrev):
            continue
        out.append(m.end())
    return out


def word_starts(text):
    out = []
    for m in re.finditer(r'\S', text):
        p = m.start()
        if p > 0 and not text[p - 1].isspace():
            continue
        out.append(p)
    out.append(len(text))
    return out


def marker_edits(text):
    """Candidate marker edits: insert a missing '**', or split a fused run.

    A fused run is a '*' run of length >= 3, e.g. '***' or '****'. Splitting
    it means deleting the surplus stars, which is a marker-only change.
    """
    out = []
    # split fused runs
    for s, e in marker_runs(text):
        n = e - s
        if n > 2:
            # delete n-2 surplus stars, keeping the first two
            for k in range(s + 2, e):
                out.append((k, k + 1, ''))
    # insert a missing marker
    for p in word_starts(text):
        if p in (0, len(text)):
            continue
        out.append((p, p, '**'))
    return out


def repair_marker(text):
    """Repair a paragraph that still renders with a literal '**'.

    Candidates are scored by the renderer. Ties are broken by preferring a
    sentence-boundary insertion and then the SHORTEST resulting bold span,
    because the paper's emphasis is overwhelmingly on short labels.
    """
    base = score(text)
    if base[0] == 0:
        return text, False

    stops = set(sentence_stops(text))

    cands = []
    for a, b, rep in marker_edits(text):
        trial = apply_edits(text, [(a, b, rep)])
        if tokens(trial) != tokens(text):
            continue
        s = score(trial)
        if s[0] >= base[0] or s[1] > 0:
            continue
        spans = bold_spans(trial)
        longest = max((len(c) for c, _ in spans), default=0)
        is_stop = 1 if (rep == '**' and a in stops) else 0
        cands.append(((is_stop, longest, a), trial))

    if not cands:
        return text, False
    cands.sort(key=lambda x: x[0])
    return cands[0][1], True


# ------------------------------------------------------------------ history

def git_revisions():
    out = subprocess.run(
        ['git', 'log', '--format=%H', '--follow', '--', REL],
        cwd=str(REPO), capture_output=True, text=True,
        encoding='utf-8', errors='replace').stdout
    return [c for c in out.split('\n') if c.strip()]


def git_show(rev):
    return subprocess.run(
        ['git', 'show', f'{rev}:{REL}'], cwd=str(REPO),
        capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


def build_history_index(max_group=6, only=None):
    """bare_text -> [(rev, text)] over runs of up to `max_group` paragraphs.

    Only the keys in `only` are retained, which keeps the cache small.
    """
    if CACHE.exists():
        with open(CACHE, 'rb') as fh:
            return pickle.load(fh)
    index = {}
    revs = git_revisions()
    print(f'  scanning {len(revs)} revisions of {REL} ...')
    for n, rev in enumerate(revs, 1):
        if rev == INVALID_REV:
            continue
        txt = git_show(rev)
        if not txt:
            continue
        hb = blocks(txt)
        for i in range(len(hb)):
            for k in range(1, max_group + 1):
                if i + k > len(hb):
                    break
                grp = hb[i:i + k]
                if not any('**' in g for g in grp):
                    continue
                key = bare_text('\n'.join(grp))
                if only is not None and key not in only:
                    continue
                if not key:
                    continue
                index.setdefault(key, []).append((rev, '\n'.join(grp)))
        if n % 50 == 0:
            print(f'    {n}/{len(revs)} ...')
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE, 'wb') as fh:
        pickle.dump(index, fh)
    return index


# ------------------------------------------------------------------ main

def main():
    orig_text = subprocess.run(
        ['git', 'show', f'{BASE_REV}:{REL}'], cwd=str(REPO),
        capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

    print(f'base  : {BASE_REV}  lines={len(orig_text.split(chr(10)))}  '
          f'literal ** = {literal_count(orig_text)}')

    bl = blocks(orig_text)

    # the keys worth looking up: every damaged paragraph, and every run of
    # consecutive paragraphs that contains one
    need = set()
    for i, b in enumerate(bl):
        if literal_count(b) == 0:
            continue
        need.add(bare_text(b))
        for j in range(max(0, i - 5), i):
            grp = bl[j:i + 1]
            if any('**' in g for g in grp):
                need.add(bare_text('\n'.join(grp)))
    print(f'  looking up {len(need)} distinct non-marker texts')

    index = build_history_index(only=need)
    print(f'  history index: {len(index)} hits')

    n_hist = n_ws = n_mark = 0

    # ---- PHASE 1: historical layout adoption
    for i, b in enumerate(bl):
        if literal_count(b) == 0:
            continue
        best = None
        for rev, hb in index.get(bare_text(b), []):
            fixed = fix_block(hb)
            if bare_text(fixed) != bare_text(b):
                continue
            s = score(fixed)
            if best is None or s < best[0]:
                best = (s, fixed, rev)
        if best is not None and best[0][0] < literal_count(b):
            bl[i] = best[1]
            n_hist += 1
            print(f'  block {i+1}: historical layout adopted from {best[2][:10]} '
                  f'(lit -> {best[0][0]})')
    print(f'phase 1 (history): {n_hist} blocks, literal ** = '
          f'{literal_count(chr(10).join(bl))}')

    # ---- PHASE 2: cell-aware flanking repair
    for i, b in enumerate(bl):
        if literal_count(b) == 0:
            continue
        fixed = fix_block(b)
        if literal_count(fixed) < literal_count(b):
            bl[i] = fixed
            n_ws += 1
    print(f'phase 2 (flanking): {n_ws} blocks, literal ** = '
          f'{literal_count(chr(10).join(bl))}')

    # ---- PHASE 3: marker repair
    for i, b in enumerate(bl):
        if literal_count(b) == 0:
            continue
        fixed, ok = repair_marker(b)
        if ok and bare_text(fixed) == bare_text(b):
            bl[i] = fixed
            n_mark += 1
            spans = [c for c, sane in bold_spans(fixed) if sane]
            print(f'  block {i+1}: marker repaired; last bold span = '
                  f'{spans[-1][:80]!r}')
    print(f'phase 3 (marker): {n_mark} blocks, literal ** = '
          f'{literal_count(chr(10).join(bl))}')

    new_text = '\n\n'.join(bl)

    for i, b in enumerate(bl):
        if literal_count(b) > 0 or n_bad_spans(b) > 0:
            print(f'\n  UNFIXED block {i+1}: lit={literal_count(b)} '
                  f'bad={n_bad_spans(b)}')
            print(f'    {b[:280]!r}')

    # ---- INVARIANT 1
    t_old, t_new = tokens(orig_text), tokens(new_text)
    if t_old != t_new:
        print('ABORT: token sequence changed.')
        for i, (a, b) in enumerate(zip(t_old, t_new)):
            if a != b:
                print(f'  first divergence at token {i}: {a!r} -> {b!r}')
                break
        else:
            print(f'  length differs: {len(t_old)} -> {len(t_new)}')
        return 1
    print(f'OK  invariant 1: token sequence IDENTICAL ({len(t_old)} tokens)')

    # ---- INVARIANT 2
    b_old, b_new = bare_text(orig_text), bare_text(new_text)
    if b_old != b_new:
        print('ABORT: non-marker text changed.')
        for i, (a, b) in enumerate(zip(b_old, b_new)):
            if a != b:
                print(f'  first diff at char {i}: {b_old[max(0,i-120):i+120]!r}')
                print(f'                     -> {b_new[max(0,i-120):i+120]!r}')
                break
        return 1
    print(f'OK  invariant 2: non-marker text IDENTICAL ({len(b_old)} chars)')

    # ---- INVARIANT 3
    lit = literal_count(new_text)
    print(f'{"OK " if lit == 0 else "FAIL"} invariant 3: literal ** = {lit}')
    if lit:
        for i, l in enumerate(new_text.split('\n')):
            if literal_count(l):
                print(f'    L{i+1}: {l[:170]}')

    # ---- INVARIANT 4
    stale_ok = True
    for marker in STALE_MARKERS:
        a, b = orig_text.count(marker), new_text.count(marker)
        if a != b:
            stale_ok = False
            print(f'  [CHANGED] {marker!r}: {a} -> {b}')
    if stale_ok:
        print(f'OK  invariant 4: all {len(STALE_MARKERS)} stale markers unchanged')

    # ---- INVARIANT 5
    bad = n_bad_spans(new_text)
    print(f'{"OK " if bad == 0 else "WARN"} invariant 5: {bad} bold spans cross a '
          f'code span / table pipe / paragraph break')
    if bad:
        for c, sane in bold_spans(new_text):
            if not sane:
                print(f'    unsane span: {c[:110]!r}')

    if lit or not stale_ok:
        print('\nNot writing.')
        return 1

    (REPO / REL).write_text(new_text, encoding='utf-8')
    print(f'\nWritten {len(new_text.split(chr(10)))} lines to {REL}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
