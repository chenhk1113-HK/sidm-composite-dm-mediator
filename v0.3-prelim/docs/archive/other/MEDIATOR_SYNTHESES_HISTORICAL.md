# Historical Mediator Detection Synthesis (v2 – v11) — Archive Bundle

> **Status:** ARCHIVED 2026-09-03 (T86.7f doc-pack restructure).
> These ten Mediator Detection Synthesis docs (v2 through v11) were
> superseded by [`MEDIATOR_DETECTION_SYNTHESIS_v12.md`](MEDIATOR_DETECTION_SYNTHESIS_v12.md)
> (current canonical synthesis).
>
> **Why bundled:** the synthesis series iterated on a single
> ongoing analysis; only the latest version (v12) is canonical.
> Keeping all ten intermediates in-tree invites confusion about
> which is current. Full content remains in git history.

---

## Index

1. v2 through v11 — sequential iterations of the same analysis
2. v12 — current canonical (kept in place)

## Each version captured the same analytic thread

The Mediator Detection Synthesis series tracked the project's
running feasibility analysis of mediator detection channels. v2
established the framework; each subsequent version added data,
channels, or numerical refinements. By v12 the document converged
on the final analysis that the project stands on today.

## v2 — v11 originals

| File | Bytes | Approx role |
|---|---|---|
| v2.md | 7,223 | Initial framework |
| v3.md | 6,146 | + KiSS-SIDM integration |
| v4.md | 8,706 | + Tier 1 channels |
| v5.md | 6,685 | pre-R12 baseline |
| v6.md | 6,254 | R12 P0-A fixes reflected |
| v7.md | 6,684 | post-R12 sanity |
| v8.md | 6,009 | Tier 2 channels |
| v9.md | 6,735 | Tier 3 channels |
| v10.md | 8,015 | v0.5 KSFR-enabled rerun |
| v11.md | 6,899 | bridge to v12 |

## v12 — current canonical

[`MEDIATOR_DETECTION_SYNTHESIS_v12.md`](MEDIATOR_DETECTION_SYNTHESIS_v12.md)
is the current canonical version. All earlier versions are
superseded.

---

## How to retrieve any historical version

```bash
for v in 2 3 4 5 6 7 8 9 10 11; do
  git log --all --diff-filter=D --pretty=format:"%H" \
    -- "v0.3-prelim/docs/MEDIATOR_DETECTION_SYNTHESIS_v${v}.md" | \
    head -1 | \
    xargs -I {} git show {}:"v0.3-prelim/docs/MEDIATOR_DETECTION_SYNTHESIS_v${v}.md" \
    > "mediator_v${v}.recovered.md"
done
```

## Provenance

> T86.7f (2026-09-03): bundled ten superseded synthesis versions
> into `v0.3-prelim/docs/MEDIATOR_SYNTHESES_HISTORICAL.md` with
> a unified index. Deleted the originals. v12 stays in place as
> canonical. Git history preserves all originals.

— Hermes Agent (MiniMax-M3)
