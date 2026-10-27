#!/usr/bin/env python
"""make_kb_summaries.py — generate a grounded .md summary for a cited paper.

Reads the local PDF (via pdftotext), extracts the title / authors / abstract from
the first pages, and emits a KB summary in the registry §8 format:

    docs/papers/verified/<arxiv_id>_<author>_<year>.md

The "key findings" and "how v19.2-F uses it" sections are filled from the
paper's own text plus the body's use of that slot -- never invented. Numbers
quoted in the summary are extracted from the PDF, so a wrong number in a
summary is detectable by re-running the extraction.

Usage:
    python scripts/make_kb_summaries.py --slot 4 --id 0704.0261 --author randall_2008
    python scripts/make_kb_summaries.py --batch batch.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KB = REPO / "docs" / "papers"
VERIFIED = KB / "verified"
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

TEMPLATE = """# {title}

- **arXiv:** {aid}
- **Authors:** {authors}
- **Published:** {published}
- **Local PDF:** `docs/papers/verified/{fname}.pdf`
- **Slot(s) in the paper:** {slots}
- **Added:** 2026-10-27 (option-1 round: full 42-slot bibliography)

## Abstract (from the PDF)

> {abstract}

## How v19.2-F uses it

{usage}

## Key numbers extracted from the PDF

{numbers}
"""


# pdftotext lives in the MSYS/Git-Bash toolchain, which is NOT on the PATH of
# the Windows venv python. Locate it rather than assuming.
PDFTOTEXT_CANDIDATES = [
    r"C:\Users\lamkuenai\AppData\Local\hermes\tools\git-2.53.0+3-win32-x64\mingw64\bin\pdftotext.exe",
    r"C:\Program Files\Git\usr\bin\pdftotext.exe",
    r"C:\Program Files\Git\mingw64\bin\pdftotext.exe",
    r"C:\msys64\usr\bin\pdftotext.exe",
    "pdftotext",
]


def _discover_pdftotext() -> list[str]:
    """Glob the Hermes-bundled Git toolchain: the path carries a version."""
    import glob as _glob
    hits = sorted(_glob.glob(
        os.path.expandvars(
            r"%LOCALAPPDATA%\hermes\tools\git-*\mingw64\bin\pdftotext.exe")))
    return hits


def find_pdftotext() -> str | None:
    import shutil
    for c in _discover_pdftotext():
        if os.path.isfile(c):
            return c
    for c in PDFTOTEXT_CANDIDATES:
        if os.path.isfile(c):
            return c
        w = shutil.which(c)
        if w:
            return w
    return None


def pdf_text(pdf: Path, first_pages: int = 2) -> str:
    """Extract text via pdftotext. Returns '' if the tool is unavailable."""
    exe = find_pdftotext()
    if not exe:
        return ""
    try:
        out = subprocess.run(
            [exe, "-q", "-f", "1", "-l", str(first_pages), str(pdf), "-"],
            capture_output=True, timeout=120,
        )
        # pdftotext output is NOT guaranteed UTF-8 (it can emit raw Latin-1 bytes
        # from ligature glyphs), so decode with errors="replace" rather than
        # letting the subprocess text-mode decoder raise.
        return out.stdout.decode("utf-8", errors="replace")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def clean(s: str) -> str:
    s = re.sub(r"arXiv:\S+", "", s)
    s = s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")
    s = s.replace("\u00a0", " ").replace("\ufffd", "")
    return re.sub(r"\s+", " ", s).strip()


# Lines that are arXiv stamps, journal banners or LaTeX preambles, never titles.
_STAMP = re.compile(
    r"^(arXiv:\S+|\[astro-ph[^\]]*\].*|\d{1,2}\s+\w{3,9}\s+\d{4}"
    r"|APJ IN PRESS.*|A&A manuscript.*|Astronomy & Astrophysics manuscript.*"
    r"|Accepted.*|Received.*|Dated:.*|Preprint .*|Preprint typeset.*"
    r"|Manuscript no\..*|\[.*\]\s*\d{1,2}\s+\w{3,9}\s+\d{4}.*"
    r"|Phys\. Rev\..*|\d+\s+\w+\s+\d{4}$)", re.I)

# A title line is long, has no digits-only stamp, and no affiliation marker.
_TITLE_HINT = re.compile(r"[A-Za-z]{4}")
_AFFIL = re.compile(r"(@|\d\s*,\s*\w|Universit|Instit|Center|Laborator|Depart|School|Academy"
                     r"|Observator|\^\d|\{\d)", re.I)


def split_title_authors(txt: str) -> tuple[str, str]:
    """Extract the title and author list from a paper's first page.

    The first non-empty line is often an arXiv stamp ("arXiv:0704.0261v1
    [astro-ph] 2 Apr 2007") or a journal banner ("APJ IN PRESS, APRIL 2002"),
    so those are skipped rather than mistaken for a title.
    """
    raw = [l.strip() for l in txt.split("\n")]
    lines = [l for l in raw if l]
    title = ""
    title_idx = -1
    for i, l in enumerate(lines[:14]):
        if _STAMP.match(l):
            continue
        # skip a bare date or a lone number
        if len(l) < 15 or not _TITLE_HINT.search(l):
            continue
        if _AFFIL.search(l):
            continue
        title = clean(l)
        title_idx = i
        break
    if not title:
        return "", ""
    # Some LaTeX preambles put the author list ABOVE the title (e.g. the ApJ
    # emulateapj style). If the lines before the title look like an author
    # list, prefer them.
    authors = ""
    for l in lines[max(0, title_idx - 4): title_idx]:
        if _STAMP.match(l):
            continue
        c = clean(l)
        if len(c) < 4 or re.fullmatch(r"(?i)(abstract|introduction|summary)\b.*", c):
            continue
        # an author list has 2+ capitalised "Firstname Lastname" tokens
        if len(re.findall(r"[A-Z][a-zA-Z\-]+\s+[A-Z]\.?[a-zA-Z\-]+", c)) >= 2:
            authors = c
            break
    if authors:
        return title, authors
    # the author line is the next non-stamp line that has a capitalised name
    for l in lines[title_idx + 1: title_idx + 8]:
        if _STAMP.match(l):
            continue
        c = clean(l)
        if len(c) < 4:
            continue
        # a bare section header is not an author list
        if re.fullmatch(r"(?i)(abstract|introduction|summary|contents)\b.*", c):
            continue
        if _AFFIL.search(c) and not re.search(r"[A-Z][a-z]+,?\s+[A-Z]\.?[a-z]*", c):
            continue
        authors = c
        break
    return title, authors


def extract_abstract(txt: str) -> str:
    """Grab the abstract block."""
    flat = clean(txt)
    m = re.search(r"Abstract\.?\s*(.{80,2400}?)(?:\bI\.\s*INTRODUCTION\b|\b1\s+INTRODUCTION\b|"
                  r"\bIntroduction\b|We (?:propose|present|show|investigate|develop))", flat, re.I)
    if m:
        return m.group(1).strip()[:1400]
    m = re.search(r"ABSTRACT\s*(.{80,2400}?)(?:\b1\s+INTRODUCTION\b|\bI\.\s*INTRODUCTION\b)", flat, re.I)
    if m:
        return m.group(1).strip()[:1400]
    return flat[:900]


def extract_numbers(txt: str) -> list[str]:
    """Distinct quantitative statements, most useful first."""
    flat = clean(txt)
    hits = []
    for m in re.finditer(r"[^.]*?(\d[\d,.]*\s*(?:cm2/g|cm\u00b2/g|km/s|Gyr|Myr|M\u2609|M_sun|Msun|dex|sigma|%)[^.]*\.)", flat):
        s = m.group(0).strip()
        if 20 < len(s) < 260:
            hits.append(s)
    seen, out = set(), []
    for h in hits:
        k = re.sub(r"\W+", "", h)[:40]
        if k not in seen:
            seen.add(k)
            out.append(h)
    return out[:10]


def body_usage(slot: str, limit: int = 4) -> str:
    """How the paper body cites this slot."""
    if not PAPER.exists():
        return "(paper draft not found)"
    txt = PAPER.read_text(encoding="utf-8")
    body = txt[: txt.find("## References")]
    lines = []
    for m in re.finditer(rf"\[{re.escape(slot)}\]", body):
        ls = max(0, body.rfind("\n", 0, m.start()))
        le = body.find("\n", m.end())
        seg = re.sub(r"\s+", " ", body[ls:le]).strip()
        if len(seg) > 25:
            lines.append(f"- L{body[:m.start()].count(chr(10)) + 1}: {seg[:230]}")
        if len(lines) >= limit:
            break
    if not lines:
        return "- (cited in the reference list; the body cites it by name rather than by slot)"
    return "\n".join(lines)


def ref_entry(slot: str) -> dict:
    """Pull title/authors/venue from the paper's own verified reference entry.

    The reference list was checked against arXiv/Crossref/publisher records
    during the 2026-10-27 citation rounds, so it is the authoritative source
    for the title and author list. PDF text extraction is used only for the
    abstract and the numbers.
    """
    if not PAPER.exists():
        return {}
    txt = PAPER.read_text(encoding="utf-8")
    ref = txt[txt.find("## References"):]
    m = re.search(rf"^\[{re.escape(slot)}\] (.+)$", ref, re.M)
    if not m:
        return {}
    ent = m.group(1)
    out = {}
    tm = re.search(r'"([^"]{15,})"', ent)
    if tm:
        out["title"] = tm.group(1)
    am = re.match(r'(.+?),\s*["\u201c]', ent)
    if am:
        out["authors"] = am.group(1).strip()
    vm = re.search(r"([^,]+?),\s*(\d+)", ent[ent.find('"') + 1:] if '"' in ent else ent)
    if vm:
        out["venue"] = vm.group(1).strip()
    return out


def make(entry: dict) -> Path:
    aid = entry["id"]
    fname = f"{aid}_{entry['author']}"
    pdf = VERIFIED / f"{fname}.pdf"
    if not pdf.exists():
        raise SystemExit(f"ERROR: no local PDF at {pdf}")
    txt = pdf_text(pdf, entry.get("pages", 2))
    if not txt.strip():
        raise SystemExit(f"ERROR: no text extracted from {pdf} (is pdftotext on PATH?)")
    title, authors = split_title_authors(txt)
    ref = ref_entry(entry["slot"])
    if ref.get("title"):
        title = ref["title"]
    if ref.get("authors"):
        authors = ref["authors"]
    abstract = extract_abstract(txt)
    numbers = extract_numbers(txt)
    num_txt = "\n".join(f"- {n}" for n in numbers) if numbers else "- (no quantitative statement extracted from the first two pages)"
    published = entry.get("published", "see the PDF")
    md = TEMPLATE.format(
        title=title or entry.get("title", ""),
        aid=aid,
        authors=authors or entry.get("authors", "see the PDF"),
        published=published,
        fname=fname,
        slots=entry.get("slots", ""),
        abstract=abstract,
        usage=body_usage(entry["slot"]),
        numbers=num_txt,
    )
    out = VERIFIED / f"{fname}.md"
    out.write_text(md, encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=Path, help="JSON list of entries")
    ap.add_argument("--slot"); ap.add_argument("--id"); ap.add_argument("--author")
    ap.add_argument("--slots"); ap.add_argument("--published"); ap.add_argument("--title")
    ap.add_argument("--authors"); ap.add_argument("--pages", type=int, default=2)
    a = ap.parse_args()
    if a.batch:
        entries = json.loads(a.batch.read_text(encoding="utf-8"))
    else:
        entries = [dict(slot=a.slot, id=a.id, author=a.author, slots=a.slots or "",
                        published=a.published or "", title=a.title or "", authors=a.authors or "",
                        pages=a.pages)]
    for e in entries:
        p = make(e)
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
