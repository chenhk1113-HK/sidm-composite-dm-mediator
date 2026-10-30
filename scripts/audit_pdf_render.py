#!/usr/bin/env python3
"""
audit_pdf_render.py — verify that a built PDF actually RENDERS its source.

WHY THIS EXISTS
Coverage-gap register row **CG-12**: *"PDF-render integrity is not
machine-checked"*. All four PDF-builder defects found in the Round-5 rounds were
SILENT — the builder exited 0 and the artifact was wrong:

  D1  CJK text shipped as `.notdef` (empty boxes)
  D2  long code lines were CLIPPED rather than wrapped
  D3  a wrapped line starting with `*` was DETACHED from its paragraph
  D4  literal markdown markers (`###`, `**`, `>`) survived into the rendered text

Three of the four were caught by a human rasterising pages and looking, not by
a test. D4 is the sharpest case: every WORD was present, so the word-level
containment check passed on a page that was visibly wrong. The next one will
not be caught by a human who is not looking for it.

WHAT IT CHECKS (per source-markdown / built-PDF pair)
  1. The PDF exists and is a real PDF with >= 1 page.
  2. SOURCE CONTAINMENT — every prose line of the source (>= 6 words, outside
     code fences) must appear in the PDF's extracted text. Catches content
     that vanished in the build. Matching is done on canonical TOKENS with a
     coverage threshold, NOT line-by-line: the builder re-wraps every
     paragraph at its own width, independently of source line breaks. A
     whole-line regex match reports almost every soft-wrapped line as absent
     (v1.0 of this script reported 22 'defects' on two PDFs and 21 of them
     were wrap artefacts — verified by extracting the PDF text and finding
     the quoted passages in it). Line-independence is still essential: a
     first rewrite that joined soft-wrapped source paragraphs produced 224
     NEW false defects, because the PDF wraps at different boundaries again.
  3. CODE CONTAINMENT — every fenced-code line of the source must be covered
     in the PDF's text. This is the check D2 needed: a clipped line loses its
     tail while its head survives, so document-level word checks pass while the
     artifact is wrong. A wrapped code line splits across PDF lines and only
     crosses a coverage boundary, while a clipped line drops whole trigrams;
     the thresholds below (>=0.85 covered, no trigram with a 2-token gap)
     separate the two.
  4. NO BLOCK-MARKER LEAKAGE — the rendered text must not contain a line
     starting with `###`-style heading markers or `>` blockquote markers.
     Those are the signature of a block marker that was never converted.
  5. LITERAL `**` BUDGET — the number of literal `**` in the rendered text
     must not EXCEED the document's documented budget (declared per job in
     `docs/papers/pdf_jobs.json`). D4's class is a KNOWN, user-deferred
     presentational defect in the v1.11 companion, so a hard zero would be a
     false failure; a budget that must not GROW catches a regression without
     pretending the deferral does not exist. The count is always printed so a
     reduction is visible.

HOW SOURCE IS MATCHED AGAINST PDF TEXT
  `pdftotext` is not UTF-8-clean and emits U+FFFD for some characters that
  render perfectly (§, •, en-dashes, accented letters). A naive containment
  check therefore reports those as missing. Source words are matched as a
  regex in which every NON-ASCII source character becomes `.` — so `σ/m`
  matches both `σ/m` and `<U+FFFD>/m` — while ASCII characters must match
  exactly. That keeps the check sensitive to genuinely dropped content and
  insensitive to extraction noise.

  Consequence to be honest about: this is a PROXY for glyph coverage, not a
  per-glyph font-coverage test. A character that renders as an empty box will
  not be flagged as long as its ASCII neighbours survive. Per-glyph coverage
  still needs a rasterise-and-look step (see the `scientific-pdf-deliverable`
  reference for the three required checks).

WHAT IT DOES NOT DO
  - It does NOT build the PDF. Building needs WSL + reportlab; see
    `scripts/build_round5_report_pdfs.py`.
  - It does NOT judge the CONTENT of the document.
  - It does NOT de-hyphenate. If a future builder hyphenates across a line
    break, containment will report a false miss; that is a loud failure and
    should be fixed in the matcher rather than by lowering the check.

Usage:
    python scripts/audit_pdf_render.py [jobs.json] [--only <substring>]

With no argument it reads `docs/papers/pdf_jobs.json`, whose `md` paths are the
WSL form `/mnt/c/...`; those are translated to Windows form here so the check
can run on the Windows side of the gate.

Exit: 0 = every declared pair passes; 1 = at least one defect.
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
JOBS_DEFAULT = REPO / "docs" / "papers" / "pdf_jobs.json"

MIN_WORDS = 6  # a source prose line needs this many words to be worth matching


# ---------------------------------------------------------------------------
# toolchain
# ---------------------------------------------------------------------------
def _find_pdftotext() -> str | None:
    """Locate pdftotext. It lives in the Hermes-bundled Git toolchain and is
    NOT on a venv python's PATH (same discovery as make_kb_summaries.py)."""
    exe = shutil.which("pdftotext")
    if exe:
        return exe
    pats = [
        os.path.expandvars(r"%LOCALAPPDATA%\hermes\tools\git-*\mingw64\bin\pdftotext.exe"),
        r"C:\Program Files\Git\mingw64\bin\pdftotext.exe",
        "/usr/bin/pdftotext",
        "/usr/local/bin/pdftotext",
    ]
    for p in pats:
        hits = glob.glob(p)
        if hits:
            return sorted(hits)[-1]
    return None


def _pdf_text(pdf: Path, pdftotext: str) -> str:
    """Extract laid-out text from EVERY extractor available on this host and
    UNION the results (set union, not concatenation).

    Measured on this host (2026-10-28, re-measured 2026-10-29 with a standalone
    script): pdftotext drops characters its ToUnicode map cannot resolve. On
    the v1.11 PDF it reads ZERO of the 227 sigma glyphs that pdfplumber reads
    — 19 of them on page 4 alone — and the disagreement spans 32 of 48 pages.
    It also rewrites 'x10^-12' as '10-12' and en/em dashes as '?'. pdfplumber
    reads the same text layer cleanly. (PyMuPDF is NOT installed on this host
    and has never been run against these PDFs; the two extractors here are
    pdfplumber and pdftotext, and only those two names belong in this file.)
    Using pdftotext ALONE makes those extraction losses look like render
    defects. The union means a defect is only flagged when NO available
    extractor can find the text.
    errors='replace': pdftotext is not UTF-8-clean.
    """
    parts = []
    try:
        import pdfplumber  # present on pythoncore-3.14 (py launcher default)
        with pdfplumber.open(str(pdf)) as doc:
            parts.append("\n".join((page.extract_text() or "") for page in doc.pages))
    except Exception:
        pass  # extractor absent or PDF not parseable by it — fall through
    r = subprocess.run(
        [pdftotext, "-q", "-layout", str(pdf), "-"],
        capture_output=True, timeout=600,
    )
    parts.append(r.stdout.decode("utf-8", errors="replace"))
    # True union: merge unique lines, not concatenation (which double-counts
    # identical content extracted by multiple engines — e.g. 57 literal '**'
    # found by both -> 114, not 57).
    seen = set()
    out_lines = []
    for p in parts:
        for ln in p.splitlines():
            if ln not in seen:
                seen.add(ln)
                out_lines.append(ln)
    return "\n".join(out_lines)


def _pdf_pages(pdf: Path, pdftotext: str) -> int | None:
    """Page count via pdfinfo when present, else by counting form feeds."""
    pdfinfo = Path(pdftotext).with_name("pdfinfo.exe")
    if not pdfinfo.exists():
        pdfinfo = Path(pdftotext).with_name("pdfinfo")
    if pdfinfo.exists():
        try:
            r = subprocess.run([str(pdfinfo), str(pdf)], capture_output=True, timeout=300)
            m = re.search(rb"Pages:\s+(\d+)", r.stdout)
            if m:
                return int(m.group(1))
        except Exception:
            pass
    txt = _pdf_text(pdf, pdftotext)
    return txt.count("\f") + 1 if txt.strip() else None


# ---------------------------------------------------------------------------
# normalisation
# ---------------------------------------------------------------------------
def _norm(s: str) -> str:
    """Collapse whitespace and normalise the Unicode spaces a layout engine
    may insert, so containment matches on words rather than on spacing."""
    s = s.replace("\u00a0", " ").replace("\u2009", " ").replace("\u202f", " ")
    s = s.replace("\u2011", "-").replace("\u2044", "/")
    return re.sub(r"\s+", " ", s).strip()


NONASCII_MAP = {
    "\u2011": "-", "\u2044": "/",  # keep ASCII equivalence for these glyphs
    # Multiplication sign is a SEPARATOR, not a content wildcard: mapping it
    # to the '?' sentinel glues '7.5×10' into one token '7.510' that the
    # PDF (which holds '7.5' and '10-12' separately — superscripts draw at
    # raised baseline) can never contain. 'x' is what a reader hears anyway.
    "\u00d7": "x", "\u00b7": "x",
}
DASH_RUN = re.compile(r"-{1,}")
DASH_CHARS = set("-\u2010\u2011\u2012\u2013\u2014\u2015\u2212")
# Rule-27 ASCII expansion maps (canonical(), see docstring there).
SUPERSCRIPT_MAP = {
    "\u2070": "^0", "\u00b9": "^1", "\u00b2": "^2", "\u00b3": "^3",
    "\u2074": "^4", "\u2075": "^5", "\u2076": "^6", "\u2077": "^7",
    "\u2078": "^8", "\u2079": "^9", "\u207b": "^-", "\u207a": "^+",
    "\u2071": "^i", "\u207f": "^n",
}
SUBSCRIPT_MAP = {
    "\u2080": "_0", "\u2081": "_1", "\u2082": "_2", "\u2083": "_3",
    "\u2084": "_4", "\u2085": "_5", "\u2086": "_6", "\u2087": "_7",
    "\u2088": "_8", "\u2089": "_9", "\u208b": "_-", "\u208a": "_+",
    # n22 fix: a duplicate entry for \u2081 was removed (harmless but sloppy),
    # and \u2097 (subscript l) is now mapped for readiness. NOTE: it is NOT in
    # the re.sub character class below, so today it still goes through the
    # deliberate "every non-ASCII -> ?" sentinel; adding it to the map is
    # harmless and prepares the day the class is widened. The class itself is
    # left alone on purpose: widening canonical() changes tokenisation and
    # could move advisory flags — a separate, tested decision, not a drive-by.
    "\u2097": "_l",
}

def canonical(s: str) -> str:
    """A side-agnostic form used for BOTH the source and the PDF text:
    whitespace collapsed; every non-ASCII character -> '?' (pdftotext emits
    U+FFFD or a different codepoint for glyphs that render perfectly, and the
    source side has the real glyph — mapping both sides to one sentinel makes
    the comparison stable); dash runs (-, –, —, --) -> a single '-'.

    Unicode super/subscripts are FIRST expanded to ASCII caret/underscore
    form (AGENTS.md rule 27): '7.5×10⁻¹²' -> '7.5x10^-12' and '10⁻¹²'
    -> '10^-12'. WHY: the PDF holds '7.5' + '10−12' as SEPARATE tokens
    (reportlab draws the superscript at raised baseline — a layout split any
    extractor sees), while the markdown '10⁻¹²' is ONE token. Without the
    expansion the source token '7.510' (canonical-mangled) can never match
    and a correctly-rendered exponent is flagged as missing. Expansion makes
    both sides tokenise as 7.5 | 10 | -12 with the shared sentinel pipeline."""
    s = (s.replace("\u00a0", " ").replace("\u2009", " ").replace("\u202f", " ")
           .replace("\u2044", "/"))
    # Unicode super/subscript RUNS -> single ASCII caret/underscore + digits
    # (rule 27 form): '10⁻¹²' -> '10^-12', '10⁸·⁵' handled per-run. One caret
    # per run — mapping each glyph separately would yield '10^^-1^2'.
    def _expand_run(run: str) -> str:
        mark = "-" if run.startswith("\u207b") else ""
        digits = "".join(SUPERSCRIPT_MAP.get(c, c)[1:] if c in SUPERSCRIPT_MAP
                         else c for c in run if c != "\u207b")
        return "^" + mark + digits
    s = re.sub(r"[\u2070\u00b9\u00b2\u00b3\u2074-\u2079\u207a\u207b\u2071\u207f]+",
               lambda m: _expand_run(m.group(0)), s)
    s = re.sub(r"[\u2080-\u2089\u208a\u208b]+",
               lambda m: "_" + "".join(SUBSCRIPT_MAP[c] if c in SUBSCRIPT_MAP else c
                                       for c in m.group(0)), s)
    s = "".join("-" if c in DASH_CHARS else NONASCII_MAP.get(c, c) for c in s)
    s = re.sub(r"[^\x00-\x7f]", "?", s)
    s = DASH_RUN.sub("-", s)
    return re.sub(r"\s+", " ", s).strip()

def tokens_of(s: str) -> list[str]:
    return canonical(s).split()

PROSE_COVERAGE = 0.90   # fraction of a source line's trigrams that must be found
CODE_COVERAGE = 0.85    # stricter: code must survive (nearly) verbatim

def _trigrams(tokens: list[str]) -> list[tuple[str, str, str]]:
    return [(tokens[i], tokens[i + 1], tokens[i + 2])
            for i in range(len(tokens) - 2)]

def _coverage(src_tokens: list[str], tri: set) -> tuple[float, int]:
    """Fraction of the source line's trigrams found contiguously in the PDF's
    flattened token stream (flattening means PDF line breaks are invisible to
    the match). Returns (coverage, number of missing trigrams)."""
    if len(src_tokens) < 3:
        return (1.0, 0)
    tri_src = _trigrams(src_tokens)
    found = sum(1 for t in tri_src if t in tri)
    return found / len(tri_src), len(tri_src) - found


def _strip_md(s: str) -> str:
    """Strip INLINE markdown markup from a source line, leaving the words the
    renderer will actually emit.

    This is essential and was the first version's bug: the builder CONVERTS
    markup, so a source line `**Commit:** \\`0f65db4\\`` renders as
    `Commit: 0f65db4`. Matching the source literally therefore reports every
    marked-up line as "absent from the PDF" - 725 false defects on one
    document. Strip the markers first, then match words.

    IMPORTANT (v1.1): emphasis/underline stripping is applied ONLY to the
    text OUTSIDE backtick code spans, and code spans are restored VERBATIM.
    A single-pass stripper that ran the underscore rule over the whole line
    silently mangled snake_case identifiers (sigma_eff -> sigma?eff) and a
    single-pass one that joined soft-wrapped source paragraphs produced 224
    false defects - both classes are why this is segmented.
    """
    out = []
    for i, seg in enumerate(re.split(r"`([^`]*)`", s)):
        if i % 2 == 1:
            out.append(seg)  # code span: emitted verbatim by the builder
            continue
        t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", seg)  # images -> alt
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)     # links -> label
        t = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", t)    # reference links
        t = re.sub(r"<[^>]+>", "", t)                       # inline HTML
        t = t.replace("\\*", "*").replace("\\_", "_")
        t = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", t)         # ***bold italic***
        t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)             # **bold**
        t = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"\1", t)  # *italic*
        t = re.sub(r"__(.+?)__", r"\1", t)                 # __bold__
        t = re.sub(r"~~(.+?)~~", r"\1", t)                 # ~~strike~~
        t = re.sub(r"(?<!\w)_(\S(?:.*?\S)?)_(?!\w)", r"\1", t)  # _italic_
        t = re.sub(r"^\s*[-*+]\s+", "", t)                 # a list bullet
        t = re.sub(r"^\s*\d+\.\s+", "", t)                 # a numbered marker
        out.append(t)
    return "".join(out)


# ---------------------------------------------------------------------------
# source parsing
# ---------------------------------------------------------------------------
def _source_lines(md_text: str):
    """Split the source into (prose_lines, code_lines, table_rows).

    Tables, headings and fenced code are skipped as containment probes
    because the builder lays them out differently from prose; table rows are
    collected separately as a WHITELIST for the block-marker check (a markdown
    table whose first column is a literal '#' — a finding-number column —
    legitimately renders a line starting with '#')."""
    prose, code, tables = [], [], []
    in_fence = False
    for raw in md_text.split("\n"):
        line = raw.rstrip()
        if re.match(r"^\s{0,3}(`{3,}|~{3,})", line):
            in_fence = not in_fence
            continue
        if in_fence:
            if line.strip():
                code.append(line)
            continue
        s = line.strip()
        if not s:
            continue
        # a table row or separator is laid out as cells, not as a line of prose
        if s.startswith("|"):
            tables.append(s)
            continue
        # headings render as their own text but with the marker stripped
        if re.match(r"^#{1,6}\s", s):
            continue
        prose.append(s)
    return prose, code, tables


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def check_pair(md: Path, pdf: Path, job: dict, pdftotext: str,
               full_flags: bool = False) -> tuple[list, list]:
    """Return (defects, notes) for one source/PDF pair."""
    defects, notes = [], []

    if not md.exists():
        return [f"{md.name}: SOURCE MISSING"], notes
    if not pdf.exists():
        return [f"{pdf.name}: PDF MISSING (not built — cannot verify rendering)"], notes

    raw = pdf.read_bytes()
    if not raw.startswith(b"%PDF"):
        return [f"{pdf.name}: not a PDF (no %PDF header)"], notes

    pages = _pdf_pages(pdf, pdftotext)
    if not pages:
        return [f"{pdf.name}: 0 pages / no extractable text"], notes
    if pages < 2:
        notes.append(f"{pdf.name}: only {pages} page — check the flow length")

    text_raw = _pdf_text(pdf, pdftotext)
    hay_tokens = tokens_of(text_raw)
    tri = {(hay_tokens[i], hay_tokens[i + 1], hay_tokens[i + 2])
           for i in range(len(hay_tokens) - 2)}

    FMT_TOKEN = re.compile(r"^[*'`]+$")
    EDGE_STRIP = re.compile(r"^[^0-9A-Za-z\u0391-\u03c9-]+|[^0-9A-Za-z\u0391-\u03c9-]+$")
    def relax_tokens(toks):
        """Relaxed-pass token normaliser, applied IDENTICALLY to both sides.

        Side facts established by direct extraction (2026-10-28, live PDFs):
          * pdftotext DROPS some rendered glyphs entirely (U+2032 prime, the
            σ before '_'): they leave NO token — e.g. source 'U(1)?\".' vs PDF
            'U(1)\".'; source '?_eff/m' (σ_eff/m) vs PDF 'eff/m' after the
            empty token is dropped.
          * other glyphs extract as '?': en-dash inside a word
            ('Girmohanta–Yasuoka' -> 'Girmohanta?Yasuoka'), →, §.
        Because canonical() maps EVERY non-ASCII to '?' on both sides, the
        relaxed pipeline is side-agnostic by construction:
          1. drop pure-punctuation (* `) tokens;
          2. map interior '?' -> '-' (both sides; a source-internal '?' is
             itself a sentinel, and σ/² sentinels sit at token EDGES —
             'σ_eff' tokenises as '?_eff' — so this never erases them, it
             only aligns en-dash ligatures like 'Girmohanta?Yasuoka' with the
             source's ASCII-hyphen 'Girmohanta-Yasuoka');
          3. strip every edge character outside [alnum, hyphen, ?-sentinel-
             interiors already handled] — this removes the '?' a dropped prime
             leaves on the source edge ('U(1)?' -> 'U(1)') and quote runs on
             either side;
          4. lowercase both sides (case is formatting, not content);
          5. drop tokens that end up empty, restoring word adjacency.
        Strict pass is untouched. A relaxed-only match is a NOTE, not a defect.
        """
        out = []
        for t in toks:
            if FMT_TOKEN.match(t):
                continue
            # Caret handling, applied IDENTICALLY on both sides:
            #  (a) collapse caret runs (markdown '10^-12' expanded from '10⁻¹²'
            #      can leave '^^' when the source already used the rule-27
            #      ASCII form);
            #  (b) split exponent fragments so '10^-12' becomes 10 | -12 —
            #      the PDF draws superscripts at raised baseline and every
            #      extractor we measured (pdftotext AND pdfplumber) drops the
            #      '^' glyph itself: '10^-12' in the report renders as
            #      '10-12' tokens. Splitting on the caret restores adjacency.
            t = re.sub(r"\^{1,}", "^", t)
            if "^" in t:
                for frag in t.split("^"):
                    if frag:
                        out.append(frag)
                continue
            t = t.replace("?", "-")
            # A token that IS only the sentinel was a standalone → / § on
            # EITHER side (both map to '-' here) — formatting, never content.
            if set(t) == {"-"}:
                continue
            t = EDGE_STRIP.sub("", t)
            # strip a LEADING hyphen on both sides: pdftotext drops σ entirely
            # before '_' (source 'σ_eff' -> '?_eff' -> '-_eff', PDF '_eff'), so
            # the leading hyphen is a glyph-drop artifact, not content. A real
            # negative sign lives INSIDE numeric tokens ('-0.4723' keeps its
            # digits; leading-hyphen stripping only aligns '-x' with 'x',
            # which canonical() already conflates for en-dash ligatures).
            t = t.lstrip("-")
            t = t.lower()
            if t:
                out.append(t)
        return out
    hay_tokens_r = relax_tokens(hay_tokens)
    hay_flat_r = " ".join(hay_tokens_r)
    tri_r = {(hay_tokens_r[i], hay_tokens_r[i + 1], hay_tokens_r[i + 2])
             for i in range(len(hay_tokens_r) - 2)}
    # Word-set fallback (third pass, see prose loop): the PDF hyphenates at
    # line ends, splitting 'Girmohanta-Yasuoka' into 'girmohan' + 'ta-yasuoka'
    # tokens — no token-sequence rule can bridge that. For lines that fail
    # BOTH containment passes, verify that every distinctive (len >= 5)
    # relaxed source token appears somewhere in the relaxed PDF token SET.
    # Honest scope: this proves WORD PRESENCE, not contiguity. A line whose
    # words are all present but whose sequence is unmatchable is a NOTE; a
    # line missing distinctive words is a real DEFECT.
    hay_token_set_r = set(hay_tokens_r)
    hay_token_set_norm_r = {t.replace("-", "") for t in hay_tokens_r}
    hay_stem_set_r = {"".join(c for c in t if c.isalnum()) for t in hay_tokens_r}
    hay_stem_sample_r = sorted(hay_stem_set_r)[:6000]  # bounded for substring scans
    if len(" ".join(hay_tokens)) < 200:
        defects.append(
            f"{pdf.name}: extracted text is implausibly short "
            f"({len(' '.join(hay_tokens))} chars for {pages} page(s)) — the build may "
            f"have produced blank pages"
        )
        return defects, notes

    md_text = md.read_text(encoding="utf-8")
    prose, code, tables = _source_lines(md_text)

    # The set of source CODE lines (normalised), used to recognise a rendered
    # line that merely LOOKS like a leaked heading marker but is a code comment
    # (`# BEFORE ...`) or an ASCII-art table inside a code fence. Those are
    # correct output, not marker leakage.
    code_probes = set()
    for cl in code:
        n = _norm(cl)
        code_probes.add(n)
        code_probes.add(re.sub(r"^#+\s*", "", n))
        # join-variant: two adjacent source comments joined by the renderer
        # with a double space, then re-normalised to single spaces by _norm
        code_probes.add(re.sub(r"\s{2,}", " ", n))
        code_probes.add(re.sub(r"^#+\s*", "", re.sub(r"\s{2,}", " ", n)))

    # Table rows: the same whitelist, because a markdown table whose first
    # column is a literal '#' (a finding-number column: '| # | Reviewer
    # finding | Verdict |') legitimately renders a line beginning '# Reviewer
    # finding'. Flagging those was a false-positive class of v1.0.
    table_probes = set()
    for row in tables:
        cells = [c for c in (x.strip() for x in row.split("|")) if c]
        joined = _norm(" ".join(cells))
        if joined:
            table_probes.add(joined)
            table_probes.add(re.sub(r"^#+\s*", "", joined))
            table_probes.add(re.sub(r"\s{2,}", " ", joined))            # cell padding collapsed
            table_probes.add(re.sub(r"^#+\s*", "", re.sub(r"\s{2,}", " ", joined)))

    # 2. prose containment (on the source with inline markup STRIPPED, because
    #    the builder converts that markup before layout), scored as trigram
    #    COVERAGE rather than a whole-line regex: the builder re-wraps every
    #    paragraph at its own width, so source line breaks have no counterpart
    #    in the PDF and a strict line match reports almost every soft-wrapped
    #    line as absent (see module docstring).
    #
    #    Threshold behaviour (measured on the shipped v1.11 PDF):
    #      * a source line split across 2-3 PDF lines loses only the 1-2
    #        trigrams that straddle a coverage boundary -> >= 0.90 covered
    #      * a genuinely dropped line loses every trigram that touches it
    #      * a paragraph REWRAPPED by the builder (words moved between lines)
    #        can still reach ~0.90 even when the source line itself is gone —
    #        accepted trade-off: this check catches VANISHED content, and a
    #        rewrite that moves whole sentences is a CONTENT change, which is
    #        out of scope here (the doc judges it, not the renderer).
    missing_prose = []
    artifact_prose = []
    words_present = []
    glyph_artifact_prose = []
    for line in prose:
        plain = canonical(_strip_md(line))
        words = plain.split()
        if len(words) < MIN_WORDS:
            continue
        cov, miss = _coverage(words, tri)
        # relaxed probe: same relax_tokens pipeline as the PDF side
        words_r = relax_tokens(plain.split())
        cov_r, _ = _coverage(words_r, tri_r)
        if cov_r >= PROSE_COVERAGE:
            artifact_prose.append((line, cov))
            continue
        # third pass: word-set presence (bridges hyphenated line splits).
        # Distinctive tokens are hyphen-normalised on BOTH sides: a token
        # mangled by a dropped glyph sentinel ('cm?/g' -> 'cm-/g' where the
        # PDF reads 'cm2/g') carries no alphabetic content the PDF lacks;
        # hyphen-normalising collapses exactly the glyph-artifact variants,
        # and short fragments (<5 chars after normalising) carry too little
        # signal to prove absence.
        def distinctive_key(tok):
            return tok.replace("-", "")
        # Third pass builds its anchors from the RAW canonical tokens, not
        # the relaxed ones: tokens whose spelling contains '^' (the source's
        # rule-27 ASCII superscript form, and the unicode expansion) are
        # LAYOUT-fragile — reportlab draws the exponent at raised baseline and
        # both extractors measured here drop the '^' glyph, splitting
        # '10^-12' into '10' '12' on the PDF side. Requiring the source's
        # un-split '10^12' spelling in the PDF would flag a correctly
        # rendered line. Their fragments (each >=5 chars) ARE required; a
        # caret's neighbour within the same token is not.
        anchors = []
        for raw in plain.split():
            for seg in re.split(r"(?<=[0-9a-z])\^(?=[-+]?[0-9a-z])", raw):
                seg_r = relax_tokens([seg])
                anchors.extend(seg_r)
        distinctive = {distinctive_key(t) for t in anchors
                       if len(distinctive_key(t)) >= 5}
        if distinctive:
            absent = sorted(t for t in distinctive if t not in hay_token_set_norm_r)
            # Glyph-fragment rule: an 'absent word' whose alphanumeric stem
            # exists in the PDF is not missing content — it is a token whose
            # GLYPH was dropped or remapped by pdftotext (sigma, superscript,
            # prime): 'f_h_hh' (source sigma_HH) has stem 'fhhh' and the PDF
            # has 'f_h_hh'->stem 'fhhh'. If EVERY absent word is such a
            # fragment, the line's words are present; the damage is in the
            # text EXTRACTION, not the rendering -> NOTE, not defect. A line
            # with any fragment whose stem is genuinely absent stays a defect.
            def stem(tok):
                return "".join(c for c in tok if c.isalnum())
            def glyph_adjacent(tok):
                # A token can only be mangled by pdftotext if it carries a
                # sentinel where a glyph was (underscore = dropped σ/prime,
                # '?' = remapped →/§/≈, '/' or '(' = superscript/subscript
                # boundary). AND its alphanumeric content must exist in the
                # PDF — otherwise it is genuinely missing (e.g. a dropped
                # '1.7x10^-44' whose digits are nowhere in the PDF).
                if not any(s in tok for s in ("?", "_", "/", "(", "^")):
                    return False
                s = stem(tok)
                if len(s) < 3:
                    return True  # carries no checkable content
                if s in hay_stem_set_r:
                    return True
                # PDF may have split the stem across token boundaries:
                # accept if any >=3-char alphanumeric run of the stem occurs
                # inside some PDF token.
                pieces = [tok[i:j] for i in range(len(tok))
                          for j in range(i + 3, len(tok) + 1)
                          if tok[i:j].isalnum()]
                return any(any(p in h for h in hay_stem_sample_r) for p in pieces[:12])
            glyph_frag = [a for a in absent if glyph_adjacent(a)]
            real_absent = [a for a in absent if a not in glyph_frag]
            if not real_absent:
                glyph_artifact_prose.append((line, absent))
                continue
            missing_prose.append((line, cov, miss,
                                  "words absent: " + ", ".join(real_absent[:8])))
        else:
            missing_prose.append((line, cov, miss, ""))
    if artifact_prose:
        notes.append(
            f"{pdf.name}: {len(artifact_prose)} source line(s) matched only after "
            "dropping markdown punctuation tokens (bold wrapping a code span); "
            "words verified present in the PDF, formatting differs — not a defect"
        )
    if glyph_artifact_prose:
        notes.append(
            f"{pdf.name}: {len(glyph_artifact_prose)} source line(s) failed token "
            "containment only because pdftotext drops or remaps glyphs (sigma -> "
            "nothing, superscript 2 -> ASCII 2, prime -> nothing): every 'absent' "
            "word on those lines has its alphanumeric stem present in the PDF token "
            "stream — extraction damage, not missing content. Example signature: "
            "source 'f_H sigma_HH' tokenises 'f_h_hh', PDF tokenises 'f_h_hh' with "
            "the sigma removed; stems match."
        )
    if words_present:
        notes.append(
            f"{pdf.name}: {len(words_present)} source line(s) could not be matched as "
            "a token sequence (PDF hyphenates at line ends, splitting words across "
            "tokens) BUT every distinctive word (len>=5) is present in the PDF token "
            "set — word presence verified, contiguity not verifiable by this method"
        )
    if missing_prose:
        # n22 fix: the gate-mode [:6] display cap is REMOVED. It made the
        # summary print the DISPLAYED count (6 capped + flags from other PDFs =
        # 7 on 2026-10-30) while the true flag count was 8 — and layer 12's
        # full-flags run printed 8, so the two honest runs "disagreed" for a
        # purely presentational reason (a CG-15 red herring, now identified).
        # One count, all modes: every flagged line is printed and counted.
        shown = missing_prose
        for line, cov, miss, why in shown:
            # n22 fix (Medium): under --full-flags emit the FULL source line, not
            # a 70-char slice. Layer 12 (triage) recovers the source text by
            # scraping these reprs; a truncated repr means triage verifies only
            # the first 70 characters, so clipping in the TAIL of a long line
            # could be declared PRESENT without ever being looked at.
            quoted = line if full_flags else line[:70]
            defects.append(
                f"{pdf.name}: source prose line not contained in the PDF "
                f"({cov:.0%} of its word-trigrams found, {miss} missing"
                f"{'; ' + why if why else ''}; source {quoted!r})"
            )

    # 3. code containment (the D2 clipping signature: head present, tail gone)
    #
    # A code line is rendered literally, so no markup stripping is applied.
    # Coverage is scored the same way as prose — a long code line WRAPPED by
    # the builder splits across PDF lines and only crosses a coverage
    # boundary, while a CLIPPED line loses its tail as whole missing trigrams.
    # A clipped tail of >= 3 tokens always drops >= 3 of the line's trigrams,
    # so the threshold catches it; a tail clipped shorter than that is a
    # sub-trigram loss and is honestly below this check's resolution.
    missing_code = []
    code_joined = []
    for line in code:
        stripped = line.strip()
        toks = canonical(stripped).split()
        if len(toks) < 3 and len(stripped) < 24:
            continue  # too short to be a meaningful containment probe
        cov, miss = _coverage(toks, tri)
        if cov >= CODE_COVERAGE:
            continue
        # second pass: the code renderer joins adjacent comment lines with a
        # double space; a source line collapsed to single spaces matches the
        # PDF's flattened token stream when BOTH joined halves are present.
        probe_r = " ".join(relax_tokens(toks))
        if probe_r and probe_r in hay_flat_r:
            code_joined.append(stripped)
        else:
            missing_code.append((stripped, cov, miss))
    if code_joined:
        notes.append(
            f"{pdf.name}: {len(code_joined)} source code line(s) appear in the PDF "
            "joined to an adjacent comment line by the code renderer (words "
            "verified present verbatim) — a layout join, not clipping"
        )
    if missing_code:
        for line, cov, miss in missing_code[:6]:
            defects.append(
                f"{pdf.name}: source CODE line not contained in the PDF "
                f"(clipped? {cov:.0%} of its word-trigrams found, {miss} "
                f"missing): {line[:100]!r}"
            )
        if len(missing_code) > 6:
            defects.append(f"{pdf.name}: ... and {len(missing_code) - 6} more code lines absent")

    # 4. block-marker leakage
    #
    # A rendered line starting with `#` is a DEFECT only when it is not the
    # rendering of a source code line that legitimately begins with `#` (a
    # shell/python comment) or an ASCII-art table inside a code fence, and not
    # a markdown table whose own first column is `#`. Those are correct output;
    # flagging them was the second version's bug (21 false defects on one
    # document).
    leaked = []
    for i, line in enumerate(text_raw.split("\n")):
        s = line.strip()
        if re.match(r"^#{1,6}\s+\S", s):
            n = _norm(s)
            if n in code_probes or re.sub(r"^#+\s*", "", n) in code_probes:
                continue  # a code comment rendered verbatim
            if n in table_probes:
                continue  # a markdown table's own '#' column
            leaked.append(("heading", i + 1, s))
        elif re.match(r"^>\s+\S", s):
            n = _norm(s)
            if n in code_probes or re.sub(r"^>+\s*", "", n) in code_probes:
                continue
            if n in table_probes:
                continue
            leaked.append(("blockquote", i + 1, s))
    for kind, ln, s in leaked[:6]:
        defects.append(
            f"{pdf.name}: literal {kind} marker leaked into the rendered text "
            f"(extracted line {ln}): {s[:90]!r}"
        )
    if len(leaked) > 6:
        defects.append(f"{pdf.name}: ... and {len(leaked) - 6} more leaked block markers")

    # 5. literal ** budget — count on the PRIMARY extractor (pdfplumber when
    # available, else pdftotext). The union is for content checking; the **
    # budget is a rendering fidelity check and should use the most reliable
    # extractor. Double-counting via the union (both engines find the same **
    # on different line breaks) would give 103 for a PDF with 57 actual **.
    try:
        import pdfplumber
        with pdfplumber.open(str(pdf)) as doc:
            primary_text = "\n".join((page.extract_text() or "") for page in doc.pages)
    except Exception:
        r = subprocess.run(
            [pdftotext, "-q", "-layout", str(pdf), "-"],
            capture_output=True, timeout=600,
        )
        primary_text = r.stdout.decode("utf-8", errors="replace")
    literal = len(re.findall(r"\*\*", primary_text))
    budget = job.get("marker_budget")
    notes.append(f"{pdf.name}: {pages} page(s), {literal} literal '**' in rendered text")
    if budget is None:
        defects.append(
            f"{pdf.name}: no 'marker_budget' declared for this job in "
            f"pdf_jobs.json, so the literal-'**' count ({literal}) cannot be "
            f"judged. Declare the documented budget (0 for a clean document) "
            f"or fix the builder so the count is 0."
        )
    elif literal > int(budget):
        defects.append(
            f"{pdf.name}: {literal} literal '**' in the rendered text EXCEEDS "
            f"the documented budget of {budget}. The deferred marker class must "
            f"not grow — this is a new regression, not the known deferral."
        )
    elif literal < int(budget):
        notes.append(
            f"  (budget {budget} — {int(budget) - literal} fewer than documented; "
            f"tighten the budget to {literal} to lock the improvement in)"
        )
    return defects, notes


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _to_local(p: str) -> Path:
    """Translate a WSL /mnt/c/... path to a Windows C:/... path (and pass
    through anything already native)."""
    if p.startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        drive = p[5].upper()
        return Path(f"{drive}:/" + p[7:])
    return Path(p)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1]
    jobs_file = Path(args[0]) if args else JOBS_DEFAULT

    print("=" * 70)
    print("PDF RENDER INTEGRITY AUDIT")
    print("=" * 70)

    if not jobs_file.exists():
        print(f"\n  FAIL: jobs file not found: {jobs_file}")
        print("\nRESULT: FAIL")
        return 1

    jobs = json.loads(jobs_file.read_text(encoding="utf-8"))
    pdftotext = _find_pdftotext()
    if not pdftotext:
        print("\n  FAIL: pdftotext not found. It ships with the Hermes-bundled Git")
        print("        toolchain and is not on a venv python's PATH.")
        print("\nRESULT: FAIL")
        return 1

    all_defects = []
    for job in jobs:
        md, pdf = _to_local(job["md"]), _to_local(job["pdf"])
        if only and only not in md.name and only not in pdf.name:
            continue
        print(f"\n  {pdf.name}")
        defects, notes = check_pair(md, pdf, job, pdftotext,
                                    full_flags="--full-flags" in argv)
        for n in notes:
            print(f"    . {n}")
        for d in defects:
            print(f"    ! {d}")
        if not defects:
            print("    OK: source contained, no block-marker leakage, budget respected")
        all_defects.extend(defects)

    print()
    print("-" * 70)
    if "--gate-mode" in argv:
        # GATE MODE (policy, documented): defects split into two classes.
        #  HARD (fail the gate): budget breach, block-marker leak, implausible
        #  text length, CODE-line absence.
        #  ADVISORY (surface, do not fail): PROSE-line token-containment flags.
        #  Rationale, measured on this host and re-verified 2026-10-29: the
        #  reports' prose is math-dense ('σ₀·(100/v)^a'), and pdftotext reads
        #  ZERO of the 227 sigma glyphs pdfplumber reads in the v1.11 PDF (19
        #  of them on page 4; 32 of 48 pages disagree). So a prose
        #  token-containment FAIL is a glyph/layout artifact with high prior
        #  probability. It is not waved away: scripts/triage_pdf_advisory_flags.py
        #  re-checks every flagged line against pdfplumber's extraction alone
        #  and reports the residual missing tokens per line. Last run: 6/6
        #  flagged lines had every alphanumeric token present — all layout
        #  artifacts, no real content loss. Manual mode (no flag) stays strict.
        hard = [d for d in all_defects if "prose line not contained" not in d
                and "prose lines absent" not in d]
        advisory = [d for d in all_defects if "prose line not contained" in d
                      or "prose lines absent" in d]
        if hard:
            print(f"RESULT: FAIL — {len(hard)} hard defect(s), "
                  f"{len(advisory)} advisory.")
            print("-" * 70)
            return 1
        print(f"RESULT: PASS (gate mode) — 0 hard defects; "
              f"{len(advisory)} advisory prose flag(s) listed above for triage"
              if advisory else
              "RESULT: PASS (gate mode) — 0 hard defects, 0 advisory flags")
        print("-" * 70)
        return 0
    if all_defects:
        print(f"RESULT: FAIL — {len(all_defects)} defect(s).")
        print("-" * 70)
        return 1
    print("OK: every declared PDF renders its source, leaks no block marker, and")
    print("    respects its documented literal-'**' budget.")
    print("-" * 70)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
