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

# Absolute anchoring (fixed 2026-11-13): the old `cd "$(dirname "$0")/.."` landed in
# `docs/` rather than the repo root, and each block's relative `cd ../..` then nested
# one level deeper, writing PDFs into docs/docs/docs/... See the header note.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"   # docs/papers -> repo root
cd "$ROOT"

# Verified: full text read and key values confirmed
mkdir -p "$ROOT/docs/papers/verified"
cd "$ROOT/docs/papers/verified"
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

# 2026-11-09 intake (user's "Useful papers.docx"; registry §7.11). These keep KB-style filenames
# because their .md summaries are named that way; astro-ph IDs are flattened with underscores.
mkdir -p "$ROOT/docs/papers/verified"
cd "$ROOT/docs/papers/verified"
echo ""
echo "=== Downloading 2026-11-09 intake papers ==="
for pair in "2411.11945|2411.11945_tran_2026.pdf" "2512.15869|2512.15869_despali_2026.pdf" "2607.08818|2607.08818_sarratoalos_2026.pdf" "2002.02102|2002.02102_yang_2020.pdf" "2403.11403|2403.11403_zhang_2024.pdf" "astro-ph/9611107|9611107_nfw_1997.pdf" "astro-ph/9508025|9508025_nfw_1996.pdf" "astro-ph/9703057|9703057_burkert_1997.pdf" "astro-ph/9504041|9504041_burkert_1995.pdf"; do
  url_id="${pair%%|*}"; out="${pair##*|}"
  if [ -f "$out" ]; then
    echo "  [skip] $out already exists"
  else
    curl -sL "https://arxiv.org/pdf/${url_id}" -o "$out"
    echo "  Downloaded ${url_id} -> $out ($(stat -c%s "$out" 2>/dev/null || stat -f%z "$out") bytes)"
  fi
done
echo "  NOTE: Burkert 1995 (ApJ 447, DOI 10.1086/309560) has NO arXiv record and cannot be fetched"
echo "        by this script; see registry §7.5."

# To-verify: downloaded but full read pending
mkdir -p "$ROOT/docs/papers/to_verify"
cd "$ROOT/docs/papers/to_verify"
echo ""
echo "=== Downloading to-verify papers ==="
# Target names match the KB filenames on disk (the .md summaries use the same names), so
# re-running really does skip; the old bare-id list re-downloaded 6 duplicate PDFs every run.
for pair in "1007.4198|1007.4198_simon_2011_segue1.pdf" "1306.5010|1306.5010.pdf" "1705.02358|1705.02358_tulin_yu_2018.pdf" "1712.02521|1712.02521.pdf" "1808.06634|1808.06634_read_2019_core_nfw.pdf" "2012.06611|2012.06611_andrade_2022.pdf" "2309.03253|2309.03253_benitezllambay_2023.pdf" "2508.20157|2508.20157_anand_2025_cloud9.pdf"; do
  url_id="${pair%%|*}"; out="${pair##*|}"
  if [ -f "$out" ]; then
    echo "  [skip] $out already exists"
  else
    echo "  Downloading ${url_id}..."
    curl -sL "https://arxiv.org/pdf/${url_id}" -o "$out"
    echo "    $(stat -c%s "$out" 2>/dev/null || stat -f%z "$out") bytes"
  fi
done

# 2026-11-13 LSB core-check intake (registry §7.12). PDFs are gitignored
# (docs/papers/.gitignore:11 `*.pdf`) so they are LOCAL-ONLY and reproduce from this
# script; each .md summary records the sha256 of the exact PDF the audit read.
mkdir -p "$ROOT/docs/papers/verified"
cd "$ROOT/docs/papers/verified"
echo ""
echo "=== Downloading 2026-11-13 LSB intake (verified) ==="
for pair in "astro-ph/0506345|astro-ph_0506345_sanchezsalcedo_2005_ngc5963.pdf"; do
  url_id="${pair%%|*}"; out="${pair##*|}"
  if [ -f "$out" ]; then
    echo "  [skip] $out already exists"
  else
    curl -sL "https://arxiv.org/pdf/${url_id}" -o "$out"
    echo "  Downloaded ${url_id} -> $out ($(stat -c%s "$out" 2>/dev/null || stat -f%z "$out") bytes)"
  fi
done

mkdir -p "$ROOT/docs/papers/to_verify"
cd "$ROOT/docs/papers/to_verify"
echo ""
echo "=== Downloading 2026-11-13 LSB intake (to_verify) ==="
for pair in "2605.05588|2605.05588_kitazawa_2026_lsb_cores.pdf" "2509.24270|2509.24270_wang_2026_dmdg_collisions.pdf"; do
  url_id="${pair%%|*}"; out="${pair##*|}"
  if [ -f "$out" ]; then
    echo "  [skip] $out already exists"
  else
    curl -sL "https://arxiv.org/pdf/${url_id}" -o "$out"
    echo "  Downloaded ${url_id} -> $out ($(stat -c%s "$out" 2>/dev/null || stat -f%z "$out") bytes)"
  fi
done

echo ""
echo "=== Done ==="
ls -la "$ROOT/docs/papers/verified/"*.pdf "$ROOT/docs/papers/to_verify/"*.pdf 2>&1 | wc -l
echo "PDFs in docs/papers/"
