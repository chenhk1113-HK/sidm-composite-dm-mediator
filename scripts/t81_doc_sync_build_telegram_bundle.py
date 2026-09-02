#!/usr/bin/env python3
"""T81 doc-sync gate — Telegram bundle builder.

Compresses the T81 wrap-up (Channel 19 + doc-sync gate) into a single
<500 KB Markdown file (the bundle is one MD because there are no new
plots/code in this commit — only doc-sync to existing T81 work
shipped 2026-09-02, msg 53721).

Output:
    $LOCALAPPDATA/Temp/t81_doc_sync_bundle/t81_doc_sync_wrap_up.md

Then the calling shell wraps it in <500 KB and posts to Telegram home.
"""
from __future__ import annotations

import datetime as _dt
import os
import sys
from pathlib import Path

CONTENT = '''# T81 Doc-Sync Gate — Closing the Wrap (2026-09-02, commit b6ad5cb)

> **For:** Project lead. Documents the doc-sync gate that landed after
> T81 was shipped (commit `7b16251`, msg 53721). The T81 commit
> introduced Channel 19 (XENONnT + PandaX-4T watch) but did not yet
> update the drift-guard sources. This commit (`b6ad5cb`) closes the
> gate without bumping the standing version (no posterior change).

## What landed in this commit

5 files changed, 46 insertions(+), 11 deletions(-):

| File | Purpose | Key change |
|---|---|---|
| `CITATION.cff` | Version-of-record | Add T80 + T81 bullets; bump version string |
| `EXTRACT.md` | 1-page extract | Channels 18→19, Tests 472→504, add T81 note |
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` | Standing posture doc | §0 header mentions T81 |
| `README.md` | Project frontpage | Headline table 18→19 + 472→504; new T81 milestone block; v0.4-prelim+T75+T81 row; citation block version string update |
| `docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md` | Layman brief | T75 → T75..T81; Channels 18→19; Tests 472→504; provenance footer updated |

## Standing version stays v0.4-prelim+T75

T81 was a refinement + Channel 19 addition — no posterior re-run. The
standing version is unchanged at `v0.4-prelim+T75`. The README
version table now lists `v0.4-prelim+T75+T81` as the most recent
round within that standing version, with a one-row summary of what T81
added (rhetoric softening + Channel 19 + conftest.py Windows-fix).

## Drift-guard verified (5/5 sources agree)

| Source | Version | Channels | Tests |
|---|---|---|---|
| `VERSION` | `0.4-prelim+T75` | — | — |
| `README.md` (headline table) | `0.4-prelim+T75` | **19** | **504 pass, 6 skip** |
| `README.md` (version table row) | `v0.4-prelim+T75+T81` | **19** | **504** |
| `CITATION.cff` | `0.4-prelim+T75 (...)` | **19** | **504** |
| `EXTRACT.md` | `0.4-prelim+T75` | **19** | **504** |
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §0` | `0.4-prelim+T75` (refined T78/T79, validated T80, **T81 watch**) | — | — |
| `docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md` | `v0.4-prelim+T75 Tier-1 Milestone (T72 → T81)` | **19** | **504** |
| `CHANGELOG.md` | `v0.4-prelim+T75` (T75/T76/T77/T78/T79/T80/T81 entries) | — | **504 pass, 6 skip** |

All sources agree. **No drift.**

## Test verification

Full test suite (excluding the 2 known-incompatible Tier-3 tests):

```
504 passed, 6 skipped, 3 warnings in 10.78s
```

13 new Channel 19 tests added by T81 (`test_channel_19_competitor_dd.py`):

```
v0.3-prelim/tests/test_channel_19_competitor_dd.py .............  [100%]
13 passed in 0.19s
```

## HEAD_MATCH verified

```
local  : b6ad5cbe331968363f895ddfafa8a41895202d8d
remote : b6ad5cbe331968363f895ddfafa8a41895202d8d   (master)
```

## Recap: full T72 → T81 milestone (Tier-1)

| Tier | Item | Doc | Status |
|---|---|---|---|
| Tier-1 | DAMPE POC (T72) | `T72_DAMPE_POC.md` | ✅ Shipped |
| Tier-1 | Channel 17 DAMPE wiring (T73) | `T73_*` | ✅ Shipped |
| Tier-1 | Channel 18 LSS Zhang+2025 (T74) | `T74_LSS_ZHANG_2025.md` | ✅ Shipped |
| Tier-1 | v0.7 rerun at nlive=2000 (T75) | `T75_V07_FULL_T41_RERUN.md` | ✅ Shipped |
| Tier-1 | nlive=2000 confirmation (T76) | `T76_V07_NLIVE2000.md` | ✅ Shipped |
| Tier-1 | LZ signal defensive doc (T77) | `T77_LZ_2026_09_UPDATE.md` | ✅ Shipped |
| Tier-1 | Kahlhoefer kinetic-mixing (T78) | `T78_KINETIC_MIXING_LZ_LINK.md` | ✅ Shipped |
| Tier-1 | Composite form factor F²(q) + relic check (T79) | `T79_COMPOSITE_FORM_FACTOR_REMNANT.md` | ✅ Shipped |
| Tier-1 | LZ paper compatibility check (T80) | `T80_LZ_PAPER_UPDATE.md` | ✅ Shipped |
| Tier-1 | LZ review response + Channel 19 (T81) | `T81_LZ_REVIEW_RESPONSE.md` | ✅ Shipped |
| Tier-1 | Doc-sync gate closure (T81.6) | this commit `b6ad5cb` | ✅ Shipped |

## What is still open

1. **KIV cron `080d2f590251` registered for 2026-11-01 09:00** — re-checks
   the LZ paper for any updates since 2026-09-02. Will run autonomously.
2. **No outstanding Tier-1 work.** Next up is v0.4 Tier-2 (Tier-2 of the
   `V0_6_ROADMAP.md`): 9 of 15 v0.6 roadmap items shipped; #10, #17,
   #19 are partial-closure candidates.
3. **Composite-DM UV completion** is a multi-week Tier-3 item; not in
   flight.

## Provenance

> T81 doc-sync gate (commit `b6ad5cb`) closes the wrap-up for the
> Tier-1 milestone first shipped in `7b16251` (msg 53721). Standing
> version remains `v0.4-prelim+T75`. Headline σ/m unchanged at 0.27
> cm²/g. All drift-guard sources agree. KIV cron on 2026-11-01.

— Hermes Agent (MiniMax-M3), 2026-09-02.
'''


def main() -> int:
    out_dir = Path(os.environ.get("TEMP", "/tmp")) / "t81_doc_sync_bundle"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "t81_doc_sync_wrap_up.md"
    out.write_text(CONTENT, encoding="utf-8")
    stamp = _dt.datetime.now().isoformat(timespec="seconds")
    print(f"[t81_doc_sync] wrote {out} ({len(CONTENT):,} bytes) at {stamp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
