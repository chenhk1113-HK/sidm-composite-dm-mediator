"""CG-16 inventory: where every host absolute path in the repository lives, and why.

The decision recorded here (owner-approved 2026-11-08):
  LIVE scope   = scripts/**, tests/**, v0.3-prelim/tests/**, config.py
                 -> no host absolute path may remain in code; scripts/paths.py is the single source.
  FROZEN scope = the historical analysis code under v0.3-prelim/code/** (and its scripts)
                 -> inventoried, deliberately NOT rewritten. Those runs already produced the
                 artefacts on disk; re-pointing their reads risks a silent re-computation against
                 different data, which is a worse failure than a non-portable path.
  DOCS / DATA  = prose and produced artefacts -> recorded, never rewritten by tooling.

Usage:  python scripts/cg16_scan.py            # refresh v0.3-prelim/data/results/cg16_host_path_inventory.json
        python scripts/cg16_scan.py --check    # fail if the inventory no longer matches the tree
"""
from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INVENTORY = REPO / "v0.3-prelim" / "data" / "results" / "cg16_host_path_inventory.json"

LIVE_PREFIXES = ("scripts/", "tests/", "v0.3-prelim/tests/")
LIVE_EXACT = {"config.py"}
PINNED_SOURCE = {"scripts/paths.py", "scripts/cg16_convert.py", "scripts/cg16_scan.py"}
PINNED_EXCEPTION = {
    "scripts/paths.py": "the single source",
    "v0.3-prelim/code/kiss_sidm_julia_bridge.py": "WSL-side tool defaults must stay WSL-spelled",
    "v0.3-prelim/tests/test_config_split_brain.py": "asserts the historical split-brain defect",
    "v0.3-prelim/tests/test_no_hardcoded_host_paths_cg16.py": "the guard must spell the spellings it forbids",
}
HOST_MARKERS = ("lamkuenai",)
PATTERNS = [
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator",
    "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator",
    "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator",
    "/home/lamkuenai/sidm-composite-dm-mediator",
    r"C:\Users\lamkuenai\AppData\Local\hermes",
    r"C:\Users\lamkuenai\Strata",
    "/home/lamkuenai",
]


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True)
    return sorted(p.decode() for p in out.stdout.split(b"\0") if p)


def masked_source(src: str) -> str:
    """Source with comments and docstrings blanked out: what the guard actually prohibits."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    hidden = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    hidden.update(range(body[0].lineno, body[0].end_lineno + 1))
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        toks = []
    lines = src.splitlines()
    out = []
    for i, line in enumerate(lines, 1):
        if i in hidden:
            out.append("")
            continue
        comments = [t for t in toks if t.type == tokenize.COMMENT and t.start[0] == i]
        if comments:
            cut = min(t.start[1] for t in comments)
            line = line[:cut]
        out.append(line)
    return "\n".join(out)


def host_hits(rel: str):
    p = REPO / rel
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    hits = []
    for i, line in enumerate(src.splitlines(), 1):
        if any(m in line for m in HOST_MARKERS):
            hits.append((i, line.strip()[:160]))
    return hits


def build():
    inventory = {
        "decision": {
            "live_scope": list(LIVE_PREFIXES) + sorted(LIVE_EXACT),
            "live_rule": "no host absolute path in code; scripts/paths.py is the single source",
            "frozen_scope": ["v0.3-prelim/code/**", "v0.3-prelim/data/**", "docs/**", "*.md"],
            "frozen_rule": "inventoried, deliberately not rewritten (artefacts already exist; "
                           "re-pointing reads risks silent re-computation)",
        },
        "pinned": {k: v for k, v in PINNED_EXCEPTION.items()},
        "categories": {},
    }
    cats = {
        "live_clean": [], "live_prose_only": [], "pinned_source": [], "pinned_exception": [],
        "historical_frozen_code": [], "docs_prose": [], "data_artifact": [], "other": [],
    }
    for rel in tracked_files():
        hits, code_hits = [], []
        p = REPO / rel
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            src = ""
        for i, line in enumerate(src.splitlines(), 1):
            if any(m in line for m in HOST_MARKERS):
                hits.append((i, line.strip()[:160]))
        if rel.endswith(".py") and src:
            masked = masked_source(src)
            code_hits = [(i, line.strip()[:160]) for i, line in enumerate(masked.splitlines(), 1)
                         if any(m in line for m in HOST_MARKERS)]
        in_live = rel.startswith(LIVE_PREFIXES) or rel in LIVE_EXACT
        if rel in PINNED_SOURCE:
            cats["pinned_source"].append({"path": rel, "host_path_lines": len(hits)})
        elif rel in PINNED_EXCEPTION:
            cats["pinned_exception"].append({"path": rel, "host_path_lines": len(hits)})
        elif in_live:
            if code_hits:
                cats["live_prose_only"].append({"path": rel, "host_path_lines": len(hits),
                                                "code_lines_with_host_path": len(code_hits)})
            elif hits:
                cats["live_prose_only"].append({"path": rel, "host_path_lines": len(hits),
                                                "code_lines_with_host_path": 0})
            else:
                cats["live_clean"].append(rel)
        elif rel.startswith("v0.3-prelim/data/") or rel.startswith("data/"):
            if hits:
                cats["data_artifact"].append({"path": rel, "host_path_lines": len(hits)})
        elif rel.endswith(".py"):
            if hits:
                cats["historical_frozen_code"].append({"path": rel, "host_path_lines": len(hits)})
        else:
            if hits:
                cats["docs_prose"].append({"path": rel, "host_path_lines": len(hits)})
    inventory["counts"] = {k: len(v) for k, v in cats.items()}
    inventory["categories"] = cats
    inventory["patterns"] = PATTERNS
    return inventory


def main():
    check = "--check" in sys.argv
    inv = build()
    if check:
        if not INVENTORY.exists():
            print("FAIL: v0.3-prelim/data/results/cg16_host_path_inventory.json missing")
            sys.exit(1)
        old = json.loads(INVENTORY.read_text(encoding="utf-8"))
        if old.get("counts") != inv["counts"]:
            print("FAIL: inventory counts drifted")
            print(" recorded:", old.get("counts"))
            print(" current :", inv["counts"])
            sys.exit(1)
        bad = [e for e in inv["categories"]["live_prose_only"]
               if e.get("code_lines_with_host_path")]
        if bad:
            print("FAIL: host absolute path in LIVE-scope code:")
            for e in bad:
                print("  ", e["path"], e["code_lines_with_host_path"])
            sys.exit(1)
        print("OK: inventory matches the tree; no host path in live-scope code")
        return
    INVENTORY.write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {INVENTORY}")
    print(json.dumps(inv["counts"], indent=2))


if __name__ == "__main__":
    main()
