# AMUSE artifacts — ARCHIVED 2026-11-12 (superseded, not deleted)

Six files moved out of `v0.3-prelim/data/results/` into this directory. Nothing was
deleted; the bytes are unchanged and verifiable against the pre-archive listing.

| File | Size |
|---|---|
| `amuse_bullet_dwarf_calibration_2026_09_12.json` | 164,566 B |
| `amuse_focused_rerun_with_sashimi_2026_09_12.json` | 203,917 B (truncated mid-value) |
| `amuse_rerun_with_sashimi_2026_09_12.json` | 221,450 B (2026-11-11 overwrite) |
| `amuse_seed_comparison_2026_09_12.json` | 172,490 B |
| `amuse_simulation_benchmark_2026_09_12.json` | 1,553 B |
| `ch27_sigma_m_peak_from_amuse_2026_09_12.json` | 4,922 B |

## Why archived rather than re-run

The AMUSE branch was dropped on 2026-11-11 (see `CURRENT.md`, "DROPPED (2026-11-11)").
Three independent defects make no number from it citable:

1. Degenerate sigmoid slope fit: `n = 6.35 +/- 3478`.
2. Failed resolution check: SASHIMI `r_core = 0.126` kpc against softening `0.050` kpc —
   the measured core sits at or below AMUSE's own resolution.
3. Wrong regime: the encounter is 358 km/s against `V_max ~ 50` km/s for a 10^9 Msun halo
   (~7x), i.e. kinetic scattering, not the core-collapse regime the comparison assumes.

Re-running would cost compute to reproduce a result that cannot be cited. Archiving keeps
the evidence for why the branch was dropped.

## What depends on these files

Checked on 2026-11-12 by searching `v0.3-prelim/code`, `v0.3-prelim/tests` and `scripts`:

- **No claim depends on them.** Neither `amuse*` nor `ch27_sigma_m_peak_from_amuse*` appears
  in the `ref_json` claim map in `scripts/audit_claims.py`, nor in
  `v0.3-prelim/docs/PAPER_STANDING_NUMBERS.md`, nor in `v0.3-prelim/docs/PAPER_V1_DRAFT.md`.
- The only readers are their own producer scripts (`amuse_bullet_dwarf.py`,
  `amuse_focused_rerun.py`, `amuse_rerun_with_sashimi.py`, `amuse_simulation_benchmark.py`,
  `ch27_peak_from_amuse.py`), `v0.3-prelim/code/README_AMUSE.md` (deprecated banner), and the
  disclosed-defect allowlist in `scripts/seed_interval_audit.py`.
- `scripts/seed_interval_audit.py` still lists the truncated file in `CORRUPT_ALLOWLIST`; its
  reason string now points here. That allowlist entry is inert once the file is out of
  `data/results/` — the audit walks that directory only.

## Restoring

`mv _archive_amuse_20261112/<file> ../` puts an artifact back exactly as it was.

## Historical copy

The superseded 2026-09-12 fragment is also preserved at
`AppData/Local/hermes/cache/scratch/review_qwen4/amuse_fragment_backup_20260912.json`
(203,917 bytes), as recorded in `CURRENT.md`.
