# Archived scripts from `outputs/` (2026-11-16)

**What this directory is.** Twenty shell and Python scripts that had been living in `outputs/`
— a directory `.gitignore:38` ignores **wholesale** — are now tracked here instead.

**Why they were moved.** The F41 finding (docs/INTEGRITY_FINDINGS_2026-11-04.md) was that a
fresh clone lacks not only the outputs but the *tools that produce them*: a test told the reader
to "run `outputs/fetch_external_data.sh` first", and a clone had never seen that file. The same
applies to every script in a gitignored directory: they exist on one machine, are invisible to
git, are lost in a clone, and cannot be reviewed. `git grep` across tracked files named none of
these twenty, so they were neither referenced nor reproducible -- the worst of both.

**What "archived" means here.** Not deleted: the scripts are kept verbatim for the record of how
conclusions were reached, and they remain runnable by anyone who wants to reproduce a past
diagnostic. They are **not** gate producers, **not** imported by any test, and their hard-coded
host paths (`/home/lamkuenai/...`) were deliberately left as-is because `archive/` is outside the
CG-16 live scope (`scripts/`, `tests/`, `v0.3-prelim/tests/`, `config.py`). Do not import from
here; do not treat anything in here as current code.

**The two that were NOT archived.** `downsample_for_reference.py` and `verify_reference.py` are
named by `data/reference/README.md` and `tests/test_reference_chains.py`, so they moved to
`scripts/` (tracked, live scope) and had their host paths replaced with `scripts/paths.py`
resolution. Their references were re-pointed in the same commit.

**Recurrence is now guarded.** `v0.3-prelim/tests/test_gitignored_scope_scripts.py` fails if a
`.py`/`.sh` appears in a gitignored scope without being declared as a bootstrap producer or
allowlisted with a reason -- the F41 class, caught at the gate rather than at the next clone.

| script | what it was for |
| --- | --- |
| `_peek_npz.py` | inspect a posterior `.npz` |
| `build_audit_pdf.py`, `build_review_bundle_pdf.py`, `extract_docx.py` | deliverable builders |
| `bulk_rename_paths.py` | one-off path rewrite across the tree |
| `debug_audit.py`, `debug_boltzmann.py` | debugging sessions |
| `diagnose_per_galaxy.py`, `diagnose_sparc_v3.py`, `diagnose_ts_sign.py` | SPARC / TS-sign diagnostics |
| `inspect_mcdaniel.py`, `inspect_sparc_grid.py` | external-data inspection |
| `smoke_test_r11.py`, `v05_smoke_test.py` | smoke tests superseded by the gate |
| `verify_remote.py` | remote-branch read-back check |
| `fetch_external_data.sh` | the original figshare fetcher, superseded by `scripts/fetch_external_data.sh` + `scripts/fetch_fermi_mcdaniel.py` (see F41/F42) |
| `h3_h4_master.sh`, `h3_h4_smoke.sh`, `nlive2000_master.sh`, `v05_master.sh` | long-running sweep launchers (dynesty / N-body), kept for reproduction of archived sweeps |
