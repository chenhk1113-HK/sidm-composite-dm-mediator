"""Guard against the two failure modes a coordinated rename actually produces (finding F28).

During the f_H pairing rename (F26) four modules were left syntactically invalid — an import block
mangled into unmatched parentheses — and eight more had their ASSIGNMENT renamed while the USES
stayed behind, so they would raise NameError the moment they ran. Neither class was caught by the
test suite: a broken import in a script that no test imports is invisible, and a NameError inside a
function body only fires when that function is called.

This test parses every tracked module and checks that every pairing-looking name it loads is bound
in that module. It is deliberately narrow about what counts as a pairing name so it does not become
a generic lint that nobody can satisfy.
"""
import ast
import builtins
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCAN_DIRS = [REPO / "scripts", REPO / "v0.3-prelim" / "code"]
PAIRING_STEMS = ("SIGMA_0", "SIGMA_PEAK", "F_H")
BUILTINS = set(dir(builtins))


def _binding_names(tree):
    bound = set()
    star_import = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                if a.name == "*":
                    star_import = True
                bound.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    bound.add(t.id)
                elif isinstance(t, (ast.Tuple, ast.List)):
                    bound.update(e.id for e in t.elts if isinstance(e, ast.Name))
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)) and isinstance(node.target, ast.Name):
            bound.add(node.target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
            args = node.args if hasattr(node, "args") else None
            if args is not None:
                bound.update(a.arg for a in args.args + args.kwonlyargs + args.posonlyargs)
                if args.vararg:
                    bound.add(args.vararg.arg)
                if args.kwarg:
                    bound.add(args.kwarg.arg)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            bound.update(node.names)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            target = getattr(node, "target", None)
            if target is not None:
                for t in (target,) if isinstance(target, ast.Name) else getattr(target, "elts", []):
                    if isinstance(t, ast.Name):
                        bound.add(t.id)
        elif isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name):
            bound.add(node.target.id)
        elif isinstance(node, ast.withitem) and node.optional_vars is not None:
            t = node.optional_vars
            for x in (t,) if isinstance(t, ast.Name) else getattr(t, "elts", []):
                if isinstance(x, ast.Name):
                    bound.add(x.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                if a.name == "*":
                    star_import = True
    return bound, star_import


def _modules():
    for d in SCAN_DIRS:
        for path in sorted(d.glob("*.py")):
            yield path


@pytest.mark.parametrize("path", sorted(_modules()), ids=lambda p: str(p.relative_to(REPO)))
def test_module_parses(path):
    """A mangled import block is not a warning, it is an unrunnable producer."""
    try:
        ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:
        pytest.fail(f"{path.relative_to(REPO)} does not parse: {exc}")


@pytest.mark.parametrize("path", sorted(_modules()), ids=lambda p: str(p.relative_to(REPO)))
def test_pairing_names_used_are_bound(path):
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.skip("covered by test_module_parses")
    bound, star_import = _binding_names(tree)
    if star_import:
        pytest.skip("star import makes local binding analysis unsound")
    missing = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            name = node.id
            if any(stem in name for stem in PAIRING_STEMS) and name not in bound and name not in BUILTINS:
                missing.setdefault(name, node.lineno)
    assert not missing, (
        f"{path.relative_to(REPO)} loads {sorted(missing)} with no import or assignment in the "
        "module — a rename changed one side and left the other; those lines raise NameError")
