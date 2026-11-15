#!/usr/bin/env bash
# fetch_external_data.sh — Download external scientific data products.
#
# Idempotent: skips files that already exist with the correct size.
# Verifies md5 against the figshare-computed hashes.
#
# Data sources:
#   1. McDaniel et al. 2024 (arXiv:2311.04982) — 14-year Fermi-LAT dSph
#      TS profiles + SED fits. CC BY 4.0. figshare DOI:
#      10.6084/m9.figshare.24058650.v2. ~5.2 MB.
#
# Output:
#   v0.3-prelim/data/external/fermi_mcdaniel2024/
#
# Reference: docs/REVIEWER_AUDIT_R11.md G11 (2026-08-14).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/v0.3-prelim/data/external/fermi_mcdaniel2024"

mkdir -p "${DEST}"
cd "${DEST}"

# figshare files (file_id, expected_md5, friendly_name)
declare -a FILES=(
    "44477168|1627630e27c73cded88370a9344c66a2|dSphs.csv|3897"
    "42263853|53ece3239910abec1934432c621c54b0|dSphs.tar.gz|4320998"
    "42768949|ab1c7009473e6f456004d28c89f5d172|basic_data_usage.html|961845"
)

for entry in "${FILES[@]}"; do
    IFS='|' read -r file_id expected_md5 name expected_size <<< "$entry"
    if [[ -f "${name}" ]]; then
        actual_md5=$(md5sum "${name}" | cut -d' ' -f1)
        if [[ "${actual_md5}" == "${expected_md5}" ]]; then
            echo "[OK]   ${name} (md5 match, skipping)"
            continue
        else
            echo "[WARN] ${name} md5 mismatch (got ${actual_md5}, expected ${expected_md5}) — re-downloading"
            rm -f "${name}"
        fi
    fi
    echo "[GET]  ${name} from figshare file_id=${file_id}"
    # -f: fail on HTTP 4xx/5xx instead of saving the error body as if it were data.
    # Measured 2026-11-16: figshare answered a clone-side request with nginx "403 Forbidden",
    # and without -f a 146-byte HTML page was written to dSphs.csv before the md5 check ran.
    curl -fsS -L -o "${name}" "https://ndownloader.figshare.com/files/${file_id}" || {
        echo "[FAIL] ${name}: figshare returned an HTTP error (no data written)" >&2
        exit 1
    }
    # Reject an HTML/error body even if it arrived with a 200, and honour the pinned size.
    head_bytes=$(head -c 16 "${name}" 2>/dev/null || true)
    case "${head_bytes}" in
        *"<html"*|*"<!DOCTYPE"*|*"<!doctype"*)
            echo "[FAIL] ${name}: server returned an HTML page, not data" >&2
            rm -f "${name}"
            exit 1 ;;
    esac
    if [[ -n "${expected_size}" && "$(stat -c%s "${name}" 2>/dev/null || stat -f%z "${name}")" != "${expected_size}" ]]; then
        echo "[FAIL] ${name}: size $(stat -c%s "${name}" 2>/dev/null || stat -f%z "${name}") != pinned ${expected_size}" >&2
        rm -f "${name}"
        exit 1
    fi
    # Verify md5
    actual_md5=$(md5sum "${name}" | cut -d' ' -f1)
    if [[ "${actual_md5}" != "${expected_md5}" ]]; then
        echo "[FAIL] ${name} md5 mismatch after download (got ${actual_md5}, expected ${expected_md5})" >&2
        exit 1
    fi
    echo "[OK]   ${name} verified"
done

# Extract the TS profiles tarball (idempotent)
if [[ -d "dSphs" ]]; then
    echo "[OK]   dSphs/ already extracted"
else
    echo "[GET]  extracting dSphs.tar.gz..."
    tar -xzf dSphs.tar.gz
    echo "[OK]   extracted"
fi

echo
echo "External data ready at: ${DEST}"
ls -la "${DEST}" | head -10
echo "TS profile count: $(ls "${DEST}/dSphs/TS_profiles/" 2>/dev/null | wc -l)"