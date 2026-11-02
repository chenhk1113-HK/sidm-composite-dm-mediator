"""doc_version.py — shared numeric document-version selection (CG-19).

Gate layers 8 and 9 both had the same disease: frozen constants naming the
deliverables (v1.10 report / v1.8 companion) long after the deliverables
moved. Both layers now select the CURRENT version through this one helper,
so the two layers cannot drift apart or re-grow a frozen constant.

Selection is by REAL version numbers, never lexicographic: 'v1.9' sorts
above 'v1.16' as a string, which is the trap the n25 round documented.
"""
from __future__ import annotations

import re
from pathlib import Path

_VERSION_RE = re.compile(r"v(\d+)\.(\d+)_")


def latest(docs_dir: Path, prefix: str) -> Path | None:
    """Newest doc matching <prefix>vMAJOR.MINOR_*.md by (major, minor)."""
    best, best_v = None, None
    for p in docs_dir.glob(f"{prefix}v*.md"):
        m = _VERSION_RE.search(p.name)
        if not m:
            continue
        v = (int(m.group(1)), int(m.group(2)))
        if best_v is None or v > best_v:
            best, best_v = p, v
    return best
