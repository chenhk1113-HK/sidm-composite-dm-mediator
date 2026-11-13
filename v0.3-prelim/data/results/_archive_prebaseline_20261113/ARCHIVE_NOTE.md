# ARCHIVE NOTE — superseded T13_v2 ladder artifact (2026-11-13)

**File:** `t13_v2_12channel_2025_2026.superseded_20261113.json` (4,313 bytes)
**Superseded by:** `v0.3-prelim/data/results/t13_v2_12channel_2025_2026.json`
(regenerated 2026-11-13 with a pinned seed).

## What this file is

The pre-rebaseline copy of the T13_v2 12-channel ladder posterior:
log Z = **-7.279**, median sigma/m_0 = **0.684 cm^2/g** [0.23, 3.97], a = 1.48.

## Why it is archived and not citable

1. It records **no seed and no nlive**, so its log Z cannot be reproduced.
2. The code that produced it has since changed: 13 commits touched the channel
   likelihoods after it was written, including `8629f10` (2026-08-17), which
   replaced the dSph Channel 2 **bimodal-dip surrogate** (peaks near sigma/m ~ 0.1
   AND ~10 cm^2/g) with Horigome+ 2025's **one-sided 0.2 cm^2/g upper limit**.
   At fixed theta the dSph term moved -0.88 -> -1.72 at (sigma/m_0 = 1.0, a = 1.5)
   and -1.43 -> -0.15 at (0.019, 1.22); the UFD and Bullet terms are identical.
3. The current seeded code gives log Z = **-5.749**, median sigma/m_0 = **0.130**
   [0.03, 1.49] at seed 20261113 (seed 20261114: -5.802, 0.123).

Every document that quoted **0.68 cm^2/g** as the live joint galaxy-scale value was
re-issued on 2026-11-13 with this file named as its source.

## Why the file was renamed

The backup was originally written as
`t13_v2_12channel_2025_2026.json.bak.20261113_pre_rebaseline`, which `.gitignore`
lines 83-84 (`*.bak`, `*.bak.*`) exclude — a "preserved" backup that git never
tracks exists only on one disk. It was therefore moved here with a tracked name,
matching the repo's existing archive convention (`_archive_amuse_20261112/`,
`_archive_multiportal_20261112/`).

## Restore

    mv v0.3-prelim/data/results/_archive_prebaseline_20261113/t13_v2_12channel_2025_2026.superseded_20261113.json \
       v0.3-prelim/data/results/t13_v2_12channel_2025_2026.json.bak.20261113_pre_rebaseline

Nothing was deleted.
