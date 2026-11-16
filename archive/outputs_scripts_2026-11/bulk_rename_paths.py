"""Bulk-replace 'dm-sidm-pipeline' -> 'sidm-composite-dm-mediator' in .py files.

Used to fix the rename gap flagged by Review 11 (config.py, scripts, tests,
v0.1/v0.2/v0.3-prelim modules all hardcode the old project name). This
is the root cause of clean-clone test failures per the R11 audit.

Safety: only touches .py files (NOT docs/REVIEWER_AUDIT_*.md, NOT
CHANGELOG.md, NOT PLAN_v0.1.md which preserve historical record per
the project's "preserve historical audit trail" convention).

Verification (AGENTS.md rule 18): py_compile on every modified file.
"""
import os
import sys
import shutil
import py_compile
from pathlib import Path

ROOT = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
OLD = "dm-sidm-pipeline"
NEW = "sidm-composite-dm-mediator"

# Files to SKIP (historical preservation)
skip_substrings = [
    os.path.join("docs", "REVIEWER_AUDIT_R2.md"),
    os.path.join("docs", "REVIEWER_AUDIT_R10.md"),
    os.path.join("docs", "REVIEWER_AUDIT_R11.md"),
    "CHANGELOG.md",
    "PLAN_v0.1.md",
    os.path.join("docs", "findings_2026_SIDM_papers.md"),
    os.path.join("docs", "MATHEMATICS.md"),
    os.path.join("docs", "DATA_SOURCES.md"),  # keeps provenance
    "outputs",  # gitignored
    ".git",
    "__pycache__",
]

modified = []
unchanged = []
errors = []

for root, dirs, files in os.walk(ROOT):
    # Skip unwanted dirs
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "outputs", "node_modules")]
    for f in files:
        if not f.endswith(".py"):
            continue
        p = Path(root) / f
        rel = str(p.relative_to(ROOT)).replace("\\", "/")

        # Skip historical files (just in case)
        if any(s.replace("\\", "/") in rel for s in skip_substrings):
            continue

        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append((str(p), "decode error"))
            continue

        if OLD not in content:
            unchanged.append(str(p))
            continue

        new_content = content.replace(OLD, NEW)
        # Backup
        backup = p.with_suffix(p.suffix + ".bak.r11")
        shutil.copy2(p, backup)
        p.write_text(new_content, encoding="utf-8")

        # Verify py_compile
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append((str(p), f"py_compile failed: {e}"))
            # Restore from backup
            shutil.copy2(backup, p)
            continue
        finally:
            # Always remove backup on success
            if backup.exists():
                try:
                    backup.unlink()
                except OSError:
                    pass

        modified.append((str(p), content.count(OLD)))

print(f"\nModified: {len(modified)} files, {sum(n for _, n in modified)} occurrences")
print(f"Unchanged: {len(unchanged)} files (no dm-sidm-pipeline refs)")
print(f"Errors: {len(errors)}")

if errors:
    print("\nERRORS:")
    for p, e in errors:
        print(f"  {p}: {e}")
    sys.exit(1)

if modified:
    print(f"\nFirst 10 modifications:")
    for p, n in modified[:10]:
        print(f"  {n}x  {p}")