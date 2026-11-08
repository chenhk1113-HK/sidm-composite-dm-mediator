"""CG-16 converter: replace host absolute paths in gate-run files with scripts/paths.py names.

Scope is deliberate: only the LIVE scope (scripts/, tests/, v0.3-prelim/tests/, config.py) is
rewritten. Frozen analysis scripts under v0.3-prelim/code/ are inventoried, not rewritten - their
outputs already exist on disk and re-pointing their reads risks a silent re-computation against
different data. See scripts/paths.py for the contract and the guard test for enforcement.

Reversibility: every change is an uncommitted working-tree edit, so `git diff` is the audit and
`git checkout -- <file>` is the revert. No .bak clutter for 60 files.

Usage:  python scripts/cg16_convert.py            # dry run: report only
        python scripts/cg16_convert.py --apply    # rewrite files
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APPLY = "--apply" in sys.argv

LIVE_DIRS = ("scripts/", "tests/", "v0.3-prelim/tests/")
LIVE_FILES = ("config.py",)
# Pinned: this file IS the single source, and its two WSL tool defaults must stay WSL-spelled
# (a Windows-side process resolving them against the Windows home would be wrong).
PINNED = {"scripts/paths.py": "the single source itself",
          "scripts/cg16_convert.py": "the converter must spell the host paths it detects",
          "scripts/cg16_scan.py": "the inventory scanner must spell the host paths it detects",
          "v0.3-prelim/code/kiss_sidm_julia_bridge.py": "WSL-side defaults must stay WSL-spelled",
          "v0.3-prelim/tests/test_no_hardcoded_host_paths_cg16.py": "the guard must spell the spellings it forbids"}
# Pinned: the test asserts the historical hardcoded-path behaviour itself.
EXCEPTIONS = {"v0.3-prelim/tests/test_config_split_brain.py":
              "asserts the historical defect (config.py existed only WSL-side); rewriting it deletes the test"}

REPO_WIN = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator"
REPO_FWD = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator"
WSL_LEGACY = "/home/lamkuenai/sidm-composite-dm-mediator"
WSL_MNT = "/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator"

# (literal prefix, replacement-for-bare, replacement-for-suffix-expression-builder, host-name used)
REPOS = [
    (REPO_WIN, "REPO", lambda s: 'str(REPO_ROOT / "%s")' % s),
    (REPO_FWD, "REPO", lambda s: 'str(REPO_ROOT / "%s")' % s),
    (WSL_MNT, "WSL_MNT_ROOT", lambda s: 'WSL_MNT_ROOT + "/%s"' % s),
    (WSL_LEGACY, "LEGACY_WSL_ROOT", lambda s: 'LEGACY_WSL_ROOT + "/%s"' % s),
]
EXTERNALS = [
    (r"C:\Users\lamkuenai\AppData\Local\hermes\runtimes\llamacpp\server.json", 'str(LLAMACPP_SERVER_JSON)'),
    (r"C:\Users\lamkuenai\AppData\Local\hermes\cache\scratch", 'str(SCRATCH_DIR / "%s")'),
    (r"C:/Users/lamkuenai/AppData/Local/hermes/cache/scratch", 'str(SCRATCH_DIR / "%s")'),
    (r"C:\Users\lamkuenai\AppData\Local\hermes\tools\git-2.53.0+3-win32-x64\mingw64\bin\pdftotext.exe", 'PDFTOTEXT_EXE'),
    (r"C:\Users\lamkuenai\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe", 'HERMES_VENV_PYTHON'),
    (r"C:\Users\lamkuenai\AppData\Local\hermes", 'str(HERMES_HOME)'),
    (r"C:/Users/lamkuenai/AppData/Local/hermes", 'str(HERMES_HOME)'),
    (r"C:\Users\lamkuenai\AppData\Local\Python\pythoncore-3.14-64\python.exe", 'REFERENCE_PYTHON'),
    (r"C:\Users\lamkuenai\Strata-data", 'str(STRATA_DATA_DIR)'),
    (r"C:\Users\lamkuenai\Strata", 'str(STRATA_DIR)'),
    (r"C:/Users/lamkuenai/.tng_api_key", 'TNG_KEY_FILE'),
    (r"C:\Users\lamkuenai\.tng_api_key", 'TNG_KEY_FILE'),
    ("/home/lamkuenai/.juliaup/bin/julia", "JULIA_BIN"),
    ("/home/lamkuenai/KiSS-SIDM", "KISS_SIDM_DIR"),
    ("/home/lamkuenai/.local/amuse-py310-venv/bin/python", "AMUSE_VENV_PYTHON"),
    ("/home/lamkuenai/.venv/bin/python", "WSL_VENV_PYTHON"),
    ("/home/lamkuenai/wimpy/bin/python", "WIMPY_VENV_PYTHON"),
    # Least specific last: the WSL home itself.
    ("/home/lamkuenai", "WSL_HOME"),
]

def _norm(p: str) -> str:
    """Canonical compare form: single backslashes, forward slashes, no trailing slash."""
    return p.replace("\\\\", "\\").replace("\\", "/").rstrip("/")


def _map_value(value: str):
    """Map a host absolute path to a scripts/paths.py expression, or None if it is not one."""
    norm = _norm(value)
    for lit_root, bare, suffix in REPOS:
        lit_norm = _norm(lit_root)
        if norm == lit_norm:
            return bare, {bare, "REPO_ROOT"}
        if norm.startswith(lit_norm + "/"):
            rest = norm[len(lit_norm) + 1:]
            return suffix(rest), {bare, "REPO_ROOT"}
    for lit_ext, expr in EXTERNALS:
        lit_norm = _norm(lit_ext)
        names = set(re.findall(r"[A-Z][A-Z0-9_]+", expr))
        if norm == lit_norm:
            return expr, names
        if norm.startswith(lit_norm + "/"):
            rest = norm[len(lit_norm) + 1:]
            if "%s" in expr:
                return expr % rest, names
            return f'{expr} + "/{rest}"', names
        # Literal of the form "<flag>=<host path>" (e.g. "--project=/home/.../KiSS-SIDM").
        if lit_norm in norm and not any(sep in norm.split(lit_norm)[0] for sep in "/\\"):
            prefix = value.split(lit_ext, 1)[0]
            tail = value.split(lit_ext, 1)[1]
            if not tail:
                return f'{prefix!r} + {expr}', names
            return f'{prefix!r} + {expr} + {tail!r}', names
    return None


def _between(src: str, a, b) -> str:
    """Raw source text between two (row, col) token positions."""
    lines = src.splitlines(keepends=True)
    if a[0] == b[0]:
        return lines[a[0] - 1][a[1]:b[1]]
    out = [lines[a[0] - 1][a[1]:]]
    out.extend(lines[a[0]:b[0] - 1])
    out.append(lines[b[0] - 1][:b[1]])
    return "".join(out)


def _offset(src: str, row: int, col: int) -> int:
    lines = src.splitlines(keepends=True)
    return sum(len(l) for l in lines[:row - 1]) + col


def convert_python(rel: str, src: str):
    """Replace host-path string literals with scripts/paths.py expressions.

    Works on token spans, including implicit multi-line string concatenation, because
    `Path("C:\\Users\\...")` in this repository is often written across two lines.
    """
    import io
    import tokenize

    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception as exc:  # unparsable file: never edit it blindly
        return src, set(), 0, [f"unparsable: {exc}"]

    # Docstrings are prose about this host, not a path dependency, and rewriting a docstring
    # literal into an expression would silently destroy __doc__. Skip them.
    docstring_lines: set[int] = set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = getattr(node, "body", [])
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    docstring_lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    except SyntaxError:
        pass

    strings = [t for t in toks if t.type == tokenize.STRING
               if t.start[0] not in docstring_lines]
    groups: list[list] = []
    cur: list = []
    for t in strings:
        if cur:
            prev = cur[-1]
            if _between(src, prev.end, t.start).strip() == "":
                cur.append(t)
                continue
            groups.append(cur)
        cur = [t]
    if cur:
        groups.append(cur)

    used: set[str] = set()
    edits = []
    residual = []
    for g in groups:
        text = "".join(t.string for t in g)
        try:
            value = ast.literal_eval(text)
        except Exception:
            continue
        if not isinstance(value, str) or "lamkuenai" not in value:
            continue
        mapped = _map_value(value)
        if mapped is None:
            residual.append(f"L{g[0].start[0]}: unmapped host path {value!r}")
            continue
        expr, names = mapped
        used |= names
        edits.append((_offset(src, g[0].start[0], g[0].start[1]),
                      _offset(src, g[-1].end[0], g[-1].end[1]), expr))
    if not edits:
        return src, set(), 0, residual
    for start, end, expr in sorted(edits, key=lambda e: -e[0]):
        src = src[:start] + expr + src[end:]
    n = sum(1 for t in edits)
    return src, used, n, residual


IMPORT_BLOCK = (
    "# CG-16: every host-dependent path is resolved by scripts/paths.py (single source).\n"
    "import sys as _sys, pathlib as _pathlib\n"
    "_CG16_ROOT = next(a for a in _pathlib.Path(__file__).resolve().parents\n"
    "                  if (a / \"scripts\" / \"paths.py\").exists())\n"
    "_sys.path.insert(0, str(_CG16_ROOT / \"scripts\"))\n"
    "from paths import {names}  # noqa: E402\n"
)


def insert_imports(src: str, names) -> str:
    block = IMPORT_BLOCK.format(names=", ".join(names))
    tree = ast.parse(src)
    line = 1
    if (tree.body and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)):
        line = tree.body[0].end_lineno  # keep the module docstring first
    lines = src.splitlines(keepends=True)
    if line < len(lines) and lines[line].startswith("from __future__"):
        line += 1
    lines.insert(line, block)
    return "".join(lines)


def live_python_files():
    files = []
    for f in sorted(REPO.rglob("*")):
        if not f.is_file():
            continue
        try:
            rel = f.relative_to(REPO).as_posix()
        except ValueError:
            continue
        if not (rel.startswith(LIVE_DIRS) or rel in LIVE_FILES):
            continue
        if not rel.endswith(".py"):
            continue
        if any(part in {"__pycache__", ".git"} for part in f.parts):
            continue
        files.append(rel)
    return files


def main():
    total_files = total_lines = 0
    report = []
    for rel in live_python_files():
        p = REPO / rel
        try:
            src = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "lamkuenai" not in src:
            continue
        if rel in PINNED or rel in EXCEPTIONS:
            reason = PINNED.get(rel) or EXCEPTIONS.get(rel)
            report.append((rel, f"PINNED/EXCEPTION: {reason}", 0))
            continue
        new, names, n, residual = convert_python(rel, src)
        if n == 0:
            note = "no mappable path literal"
            if residual:
                note += "; " + "; ".join(residual[:3])
            report.append((rel, note, 0))
            continue
        new = insert_imports(new, sorted(names))
        remaining = [l.strip()[:90] for l in new.splitlines() if "lamkuenai" in l]
        report.append((rel, f"converted {n} literal(s); imports {sorted(names)}; "
                            f"residual {len(remaining)}", n))
        total_files += 1
        total_lines += n
        if remaining:
            for r in remaining:
                report.append((rel, "  RESIDUAL: " + r, 0))
        if APPLY:
            p.write_text(new, encoding="utf-8")
            ast.parse(new)  # refuse to leave an unparsable file behind
    for rel, note, n in report:
        print(f"{rel}: {note}")
    print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: {total_files} files, {total_lines} path lines")


if __name__ == "__main__":
    main()
