#!/usr/bin/env bash
# fetch_external_data.sh — compatibility wrapper for scripts/fetch_fermi_mcdaniel.py.
#
# Kept as a shell entry point because tests, docs/DATA_SOURCES.md, docs/REVIEWER_AUDIT_R11.md
# and scripts/bootstrap_gate_inputs.py all name this path. It deliberately carries NO data
# pins: the sizes and hashes live once, in scripts/figshare_24058650_pins.json, as figshare's
# own `computed_md5` values for article 24058650.v2 (McDaniel+ 2024, arXiv:2311.04982, CC BY 4.0;
# the three fetched files total 5,286,740 bytes). A second hand-copied table is how a clone
# wrote a 403 error page into dSphs.csv on 2026-11-15 with no way to tell which number was the
# authoritative one.
#
#   bash scripts/fetch_external_data.sh              # fetch + verify + extract
#   bash scripts/fetch_external_data.sh --check      # verify on-disk files, no network
#   bash scripts/fetch_external_data.sh --repin      # re-derive pins from the metadata API
#   bash scripts/fetch_external_data.sh --force      # re-download even if the file verifies
#
# Reference: docs/REVIEWER_AUDIT_R11.md G11 (2026-08-14); finding F41 (2026-11-16).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FETCHER="${ROOT}/scripts/fetch_fermi_mcdaniel.py"
# On MSYS/git-bash, $ROOT is a POSIX path (/c/Users/...) that a NATIVE Windows python cannot
# open -- it resolves to C:\c\Users\... and fails with "can't open file". cygpath converts it
# for the Windows interpreter; on Linux/WSL there is no cygpath and the POSIX path is correct.
if command -v cygpath >/dev/null 2>&1; then
    FETCHER="$(cygpath -w "${FETCHER}")"
fi

PY="${PYTHON:-}"
if [[ -z "${PY}" ]]; then
    for candidate in python3 python; do
        if command -v "${candidate}" >/dev/null 2>&1; then PY="${candidate}"; break; fi
    done
fi
if [[ -z "${PY}" ]]; then
    echo "no python on PATH; set PYTHON=/path/to/python (the project venv is .venv-sidm-bench)" >&2
    exit 1
fi

exec "${PY}" "${FETCHER}" "$@"
