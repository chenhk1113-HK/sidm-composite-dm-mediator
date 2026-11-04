#!/usr/bin/env bash
# fetch_uncited_kb.sh — politely fetch arXiv metadata for uncited/unverified KB IDs.
#
# Purpose: gap-fill the citation KB for IDs reported by
#   scripts/check_fabrication.py  ("Unverified arXiv IDs in docs: N (in M unique)").
#
# Usage:
#   docs/papers/fetch_uncited_kb.sh                 # fetch the built-in ID list
#   docs/papers/fetch_uncited_kb.sh 2311.04982 ...  # fetch the IDs given on argv
#
# Output: one raw Atom XML file per ID named <id>.xml in $OUT (default: a scratch dir).
# Etiquette: ONE request per ID, >=3 s apart (arXiv API rate-limit policy).
#
# NOTE: the export endpoint answers http:// with a 301 -> https redirect, so -L is required.
set -u

OUT="${OUT:-C:/Users/lamkuenai/AppData/Local/hermes/cache/scratch/arxiv_xml}"
mkdir -p "$OUT"

# 26 unique unverified IDs from check_fabrication.py (2026-11-04 run), highest-use first.
IDS_DEFAULT=(
  2311.04982 2410.17036 2505.15903 2408.00703
  1308.0009 1312.3325 1701.08780 1807.06209 2506.22997
  0808.3902 0910.5224 1402.5143 1711.10981 2011.04679
  2106.01403 2207.03764 2302.10246 2409.19493 2501.03750
  2504.03305 2504.10597 2506.15644 2510.23771 2601.04735
  2605.24174 2606.12909
)

if [ "$#" -gt 0 ]; then
  IDS=("$@")
else
  IDS=("${IDS_DEFAULT[@]}")
fi

first=1
for id in "${IDS[@]}"; do
  if [ "$first" -eq 0 ]; then sleep 3; fi   # polite interval between requests
  first=0
  code=$(curl -sL --max-time 60 -w "%{http_code}" \
    "http://export.arxiv.org/api/query?id_list=${id}" -o "$OUT/${id}.xml")
  entries=$(grep -c "<entry>" "$OUT/${id}.xml" 2>/dev/null || echo 0)
  printf "%-12s HTTP=%s entries=%s\n" "$id" "$code" "$entries"
done
echo "raw XML written to: $OUT"
