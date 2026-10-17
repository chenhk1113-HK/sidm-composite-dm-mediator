#!/bin/bash
# download_papers.sh — Downloads all v19.2-F project papers to docs/papers/
#
# This script is the source of truth for what papers are part of the project.
# After running, the PDFs are in:
#   docs/papers/verified/*.pdf  (full-text verified)
#   docs/papers/to_verify/*.pdf (downloaded, full read pending)
#
# Re-running this script is idempotent (uses curl -O which overwrites).
# Each paper has a corresponding .md summary in the same directory.
#
# Total download: ~62 MB

set -e

cd "$(dirname "$0")/.."  # project root

# Verified: full text read and key values confirmed
mkdir -p docs/papers/verified
cd docs/papers/verified
echo "=== Downloading verified papers ==="
for url_id in "2207.13111" "2305.05067" "2508.20179" "2510.05682" "2605.00093"; do
  if [ -f "${url_id}.pdf" ]; then
    echo "  [skip] ${url_id}.pdf already exists"
  else
    echo "  Downloading ${url_id}..."
    curl -sL "https://arxiv.org/pdf/${url_id}" -o "${url_id}.pdf"
    echo "    $(stat -c%s ${url_id}.pdf 2>/dev/null || stat -f%z ${url_id}.pdf) bytes"
  fi
done
cd ../..

# To-verify: downloaded but full read pending
mkdir -p docs/papers/to_verify
cd docs/papers/to_verify
echo ""
echo "=== Downloading to-verify papers ==="
for url_id in "1007.4198" "1306.5010" "1705.02358" "1712.02521" "1808.06634" "2012.06611" "2309.03253" "2508.20157"; do
  if [ -f "${url_id}.pdf" ]; then
    echo "  [skip] ${url_id}.pdf already exists"
  else
    echo "  Downloading ${url_id}..."
    curl -sL "https://arxiv.org/pdf/${url_id}" -o "${url_id}.pdf"
    echo "    $(stat -c%s ${url_id}.pdf 2>/dev/null || stat -f%z ${url_id}.pdf) bytes"
  fi
done
cd ../..

echo ""
echo "=== Done ==="
ls -la docs/papers/verified/*.pdf docs/papers/to_verify/*.pdf 2>&1 | wc -l
echo "PDFs in docs/papers/"
