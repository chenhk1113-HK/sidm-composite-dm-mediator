#!/bin/bash
# fetch_cited_papers.sh — downloads the papers the PAPER BODY actually leans on
# (option-2 set, agreed 2026-10-27). Complements download_papers.sh, which
# covers the older Cloud-9/gravothermal subset.
#
# Naming convention per registry §8:
#   docs/papers/verified/<arxiv_id>_<author>_<year>.pdf
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

# <arxiv_id>|<author_year>
SET="
2510.11006|yu_2026
1508.03339|kaplinghat_2016
1005.4678|feng_2010
1810.04709|chu_2019
2406.18643|benitezllambay_2024
2206.14395|girmohanta_2022
2210.01132|girmohanta_2023
2609.16740|lei_2026
2609.19132|wang_2026
2601.17118|jia_2026
1103.0007|boylankolchin_2011
1804.10385|duerr_2018
2503.10748|nadler_2025
2601.23264|engelhardt_2026
"

ok=0; skip=0; fail=0
for row in $SET; do
  id="${row%%|*}"; who="${row##*|}"
  f="$OUT/${id}_${who}.pdf"
  if [ -s "$f" ]; then
    echo "  [skip] $f ($(stat -c%s "$f") bytes)"; skip=$((skip+1)); continue
  fi
  sleep 4    # arXiv politeness: never hammer the API
  curl -sL --max-time 180 "https://arxiv.org/pdf/${id}" -o "$f"
  sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
  magic=$(head -c 4 "$f" 2>/dev/null)
  if [ "$magic" = "%PDF" ] && [ "$sz" -gt 50000 ]; then
    echo "  [ok]   $f ($sz bytes)"; ok=$((ok+1))
  else
    echo "  [FAIL] $f size=$sz magic='$magic' -- deleting, will retry next run"
    rm -f "$f"; fail=$((fail+1))
  fi
done
echo ""
echo "=== fetch_cited_papers: ok=$ok skip=$skip fail=$fail ==="
ls -l --time-style=+%H:%M "$OUT"/*.pdf 2>/dev/null | awk '{print "   ", $5, $6, $7}'
