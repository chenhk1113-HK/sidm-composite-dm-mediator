# Vendored galstreams catalog (finding F39)

Third-party data, vendored into the repository on 2026-11-16 so the stream chain
reproduces from a fresh clone instead of from one machine's home directory.

## What is here

| file | what it is |
| --- | --- |
| `tracks/*.ecsv` | 251 files: 127 `track.st.*.summary.ecsv` + 124 full tracks (44.4 MB, LF) |
| `MANIFEST.json` | md5 (LF form) + size + upstream provenance for each of the 251 files |
| `LICENSE.galstreams` | the upstream BSD 3-Clause license text, unmodified |

Only the files `v0.3-prelim/code/t95_v25_multi_stream_real_galstreams.py` actually opens
are vendored. The upstream library ships 217 full track files (77.5 MB); the 93 that this
project never reads are not copied. The read set was measured, not guessed: t95_v25 was run
in a scratch clone with `pandas.read_csv` instrumented and the 251 opened paths recorded.

## Provenance and license

- Upstream: https://github.com/cmateu/galstreams, pinned at commit
  `6a304c05bea7f774390a11082ea127719e99b70a` ("install fixes", 2026-06-03), library v1.2.
- Citation: Mateu, C. 2023, MNRAS 520, 5225.
- License: BSD 3-Clause, Copyright (c) 2017 Cecilia Mateu. Redistribution with attribution
  is permitted; `LICENSE.galstreams` is included verbatim and this README names the source.

## Line endings

Files are stored in the LF (git-canonical) form because this repository normalizes text to
LF (`* text=auto eol=lf`, plus an explicit rule for `tracks/*.ecsv`). The upstream checkout
on the vendoring machine had CRLF, so `MANIFEST.json` records both forms per file:
`md5` (LF, the value that must match in any clone) and `md5_crlf` (the local file that was
copied). A pin that only matches the machine that created it is not a pin.

## Commands

```bash
python scripts/galstreams_pins.py --verify             # 251 md5s vs manifest
python scripts/galstreams_pins.py --census             # stream names derivable from the vendored copy
python scripts/galstreams_pins.py --fetch              # re-download from the pinned commit
python scripts/galstreams_pins.py --install-from-host  # re-copy from a local catalog ($DM_SIDM_GALSTREAMS_ROOT)
```

`DM_SIDM_GALSTREAMS_ROOT` still overrides the path for anyone who has the full upstream
catalog and wants to run against it; without it, `t95_v25` reads this vendored copy.
