#!/bin/bash
# fetch_all_cited_papers.sh — option 1: download EVERY paper the draft cites,
# so registry rule §8 ("NEVER cite a paper without local PDF + .md summary +
# registry entry") is satisfied for the full 42-slot bibliography.
#
# Supersedes fetch_cited_papers.sh (option-2 body-leaning subset). That script
# is kept because it documents the scope that was agreed first; this one is
# the complete set.
#
# Idempotent: skips files that already exist. Verifies the %PDF magic and a
# minimum size so a rate-limit HTML page is never mistaken for a paper.

set -u
# docs/papers sits TWO levels below the project root. An off-by-one here
# silently writes the PDFs into a sibling directory and still prints [ok],
# so this path is asserted rather than trusted.
cd "$(dirname "$0")/../.." || exit 1   # project root
if [ ! -f "v0.3-prelim/docs/PAPER_V1_DRAFT.md" ]; then
  echo "FATAL: cd landed in $(pwd), not the project root" >&2; exit 1
fi
OUT=docs/papers/verified
mkdir -p "$OUT"

# <arxiv_id>|<author_year>|<slot>
SET="
1504.01437|oman_2015|2
0704.0261|randall_2008|4
2102.02375|yang_yu_2021|13
1606.09251|lelli_2016|14
2306.05080|zhou_2023|15a
2508.20157|anand_2025|15c
2608.20911|trujillo_2026|15d
0910.0760|vegetti_2010|16
astro-ph/0110561|balberg_2002|18
2603.04508|fischer_yu_2026|19
1705.08513|vandokkum_2017|25
astro-ph/9810070|mateo_1998|26a
2504.02303|yang_tsaifan_2025|42
1611.03492|zhang_2017|45
2609.02823|lz_2026|50
2506.14898|yang_fan_hou_2026|50c
2305.16176|yang_parametric_2024|43
1302.3898|tulin_yu_zurek_2013|6
"

ok=0; skip=0; fail=0
for row in $SET; do
  id="${row%%|*}"; rest="${row#*|}"
  who="${rest%%|*}"; slot="${rest##*|}"
  f="$OUT/${id}_${who}.pdf"
  if [ -s "$f" ]; then
    echo "  [skip] [$slot] $f ($(stat -c%s "$f") bytes)"; skip=$((skip+1)); continue
  fi
  sleep 4    # arXiv politeness: never hammer the API
  curl -sL --max-time 240 "https://arxiv.org/pdf/${id}" -o "$f"
  sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
  magic=$(head -c 4 "$f" 2>/dev/null)
  if [ "$magic" = "%PDF" ] && [ "$sz" -gt 50000 ]; then
    echo "  [ok]   [$slot] $f ($sz bytes)"; ok=$((ok+1))
  else
    echo "  [FAIL] [$slot] $f size=$sz magic='$magic' -- deleting, will retry next run"
    rm -f "$f"; fail=$((fail+1))
  fi
done
echo ""
echo "=== fetch_all_cited_papers: ok=$ok skip=$skip fail=$fail ==="
echo "verified/ now holds $(ls -1 "$OUT"/*.pdf 2>/dev/null | wc -l) PDFs"
