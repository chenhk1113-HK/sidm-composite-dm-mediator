# Config duplication: design note (2026-09-12)

**Status:** RESOLVED via Option D. Two `config.py` files exist, but their relationship is now explicit and self-enforcing via a regression test.

---

## TL;DR — what was wrong, what's done

**The problem:** Two `config.py` files in the repository, only one of which Python actually imports. The other is a "snapshot" that's preserved for compatibility with v0.3-prelim scripts that explicitly `sys.path.insert(0, 'v0.3-prelim/code')`. Both files had drifted independently — including the LENS_SIGMA_M_LOG_WIDTH constant that we revised earlier in this session — and the divergence was invisible until a downstream test failed unexpectedly.

**What we did (Option D, 2026-09-12):**
1. Added a giant banner to `v0.3-prelim/code/config.py` saying "FROZEN SNAPSHOT — DO NOT EDIT"
2. Added a giant banner to project-root `config.py` saying "CANONICAL (LIVE) — edit here"
3. Added `tests/test_config_snapshot_consistency.py` with 16 assertions:
   - 10 KEY_CONSTANTS must match between canonical and snapshot
   - Snapshot must have the FROZEN banner
   - Snapshot banner must reference the canonical config path
   - Canonical must have the CANONICAL banner
4. Verified the test catches divergence (sanity test: temporary 0.7→0.5 in snapshot → test failed with clear divergence message → restored)

---

## The full diagnosis

### Two files, one canonical

| Location | Size | Source of truth? |
|---|---|---|
| `C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/config.py` | 15.6 KB | **Yes — Python imports this first** |
| `C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/code/config.py` | 14.2 KB | Frozen snapshot for backward compatibility |

The two files differ by ~1 KB of infrastructure code:
- The canonical version has env-var-based root detection (`DM_SIDM_PROJECT_ROOT` env var)
- The snapshot version has a simpler hardcoded path detection

Both define all the same scientific constants (sigma/m, channel widths, prior ranges, etc.).

### Why the snapshot exists

40+ scripts in `v0.3-prelim/code/` explicitly do:
```python
sys.path.insert(0, ".../v0.3-prelim/code")
import config
```

If we delete the snapshot, these scripts break. The snapshot is the path of least disruption.

### Why this was dangerous

**Symptom (2026-09-12):** I patched the ch04 width in `v0.3-prelim/code/config.py` thinking it was canonical. Python kept loading `LENS_WIDTH = 0.3` because the project-root config.py was being imported first via `sys.path` priority. The LOO-CV output was identical to the before-fix state even after the patch. I burned several tool calls before noticing.

**The trap:** nothing tells you which file Python actually loaded. Both have `LENS_SIGMA_M_LOG_WIDTH` at the top level. Both look like the canonical config. The versioned subdirectory name (`v0.3-prelim`) made the snapshot look MORE authoritative than the bare project root.

---

## Why Option D (not A, B, or C)

**Option A (symlink):** Windows + git + symlinks is fragile. Git on Windows sometimes doesn't follow symlinks correctly. The snapshot file would behave differently across hosts. Rejected.

**Option B (delete the snapshot):** Breaks 40+ scripts. Requires updating every importer or providing a shim. Too invasive for a "fix the trap" change. Rejected.

**Option C (banner only, no test):** Documents the relationship but doesn't enforce it. Future drift would still happen silently. Rejected.

**Option D (banner + test + named relationship):** Makes the relationship:
1. **Explicit** (both files say which one is canonical)
2. **Self-enforcing** (the test catches divergence)
3. **Reversible** (no renames, no deletions — adding the banner is fully reversible by removing it)

This is the minimum-change realization that solves the problem.

---

## How to use the system after this change

### If you need to change a config constant

1. **Edit the project-root `config.py` (canonical).** This is the one Python imports.
2. **Synchronize the snapshot** (`v0.3-prelim/code/config.py`) to match. This is a tracked change but doesn't affect runtime.
3. **Run `pytest tests/test_config_snapshot_consistency.py`** to verify they're in sync.
4. **Add to the ALLOWLIST** in the test file if the divergence is intentional (e.g., a frozen release snapshot for paper reproducibility).

### If you accidentally edit only the snapshot

The snapshot banner says "DO NOT EDIT" — but if you do edit it, the test will catch the divergence and fail with a clear message:
```
DIVERGENCE on 'LENS_SIGMA_M_LOG_WIDTH':
  Canonical (project-root config.py): 0.7
  Snapshot (v0.3-prelim/code/config.py): 0.5
ACTION: Edit the snapshot to match the canonical, OR add 'LENS_SIGMA_M_LOG_WIDTH' to the ALLOWLIST with a justification.
```

### If you need to delete the snapshot (Phase 2)

That's a separate decision. It would require updating all 40+ importers to use the project-root config. Estimated 1-2 hours of work. Not done in this session because:
- It's a structural change (not a bug fix)
- The trap is now mitigated (banner + test)
- Better done when there's a clear reason (e.g., before a release)

---

## Files modified

- `config.py` (canonical) — added "CANONICAL (LIVE)" banner
- `v0.3-prelim/code/config.py` (snapshot) — added "FROZEN SNAPSHOT" banner
- `tests/test_config_snapshot_consistency.py` — new file, 16 tests

## Reference

- AGENTS.md "edit the wrong file" trap: this same bug class hit us in 2026-09-08 and again in 2026-09-12. The banner + test combo is the minimum cost-effective mitigation.