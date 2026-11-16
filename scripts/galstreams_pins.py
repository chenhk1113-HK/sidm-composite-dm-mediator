"""Vendor the galstreams files that T95.9 actually reads, with pinned hashes (finding F39).

The curated multi-stream artifact v0.3-prelim/outputs/t95/multi_stream_real_galstreams.json
is produced by v0.3-prelim/code/t95_v25_multi_stream_real_galstreams.py, which until
2026-11-16 opened a host-pinned directory (C:/Users/.../galstreams/galstreams/tracks).
A fresh clone on another machine therefore could not rebuild it (measured in the F39
clone run). This module copies the EXACT file set the script opens into the repository
and pins every file by md5.

How the file set was obtained (not guessed): t95_v25 was run inside a scratch clone with
pandas.read_csv instrumented, so the 251 paths it really opened were recorded —
127 track.st.*.summary.ecsv (stream census) and 124 full track files (one per stream,
chosen by the script's own "prefer ibata2024" rule). 118 MB of upstream tracks were
considered; only the 44.8 MB actually read are vendored.

Upstream provenance (BSD-3-Clause, redistribution permitted with attribution):
  repository : https://github.com/cmateu/galstreams
  pinned at  : 6a304c05bea7f774390a11082ea127719e99b70a ("install fixes", 2026-06-03)
  library    : galstreams v1.2; described in Mateu, C. 2023, MNRAS 520, 5225
  license    : BSD 3-Clause, Copyright (c) 2017 Cecilia Mateu (LICENSE.galstreams)

LINE ENDINGS ARE PART OF THE PIN. The upstream checkout on this host has core.autocrlf=true,
so its .ecsv files hold CRLF, while this repository normalizes text to LF on commit and
checks it out as LF (.gitattributes: `* text=auto eol=lf`). A CRLF md5 would match the
machine that vendored the files and fail in every clone -- a pin that only works where it
was made. Everything here is pinned in the LF (git-canonical) form: `md5`/`bytes` are LF
values and `md5_crlf` records the CRLF form of the local file that was vendored, so the
provenance is auditable in both directions. Measured: track.st.300S.fu2018.ecsv is
4d0abc68b4bb5d9cf678f217ac494849 as LF -- exactly what raw.githubusercontent.com serves --
and 2b3492e2859cbc764e91ed79e1f5127e as CRLF.

A latent determinism defect is closed by vendoring: the script's selection rule
`sorted(candidates, key=lambda p: 'ibata2024' in p, reverse=True)` is a STABLE sort, so
when a stream has several track variants and none is ibata2024, the variant that wins
depends on the order the filesystem returns (measured: 5 streams in that situation on
this host, Orphan-Chenab among them, with 4 variants). In the vendored directory each
stream has exactly the variant the certified run used, so the selection is no longer
order-dependent.

Modes:
  --install-from-host   copy the pinned file set from a live catalog into the repo
                        (catalog root: $DM_SIDM_GALSTREAMS_ROOT, else ~/galstreams/galstreams/tracks)
  --fetch               download the pinned file set from the pinned upstream commit
  --verify              recompute md5s of the vendored files and compare with the manifest
  --census              print the stream census derivable from the vendored directory

Keep this module stdlib-only: it is invoked by scripts/bootstrap_gate_inputs.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENDOR_ROOT = REPO / "v0.3-prelim" / "data" / "external_data" / "galstreams"
TRACKS_DIR = VENDOR_ROOT / "tracks"
MANIFEST = VENDOR_ROOT / "MANIFEST.json"
LICENSE_FILE = VENDOR_ROOT / "LICENSE.galstreams"

UPSTREAM_REPO = "https://github.com/cmateu/galstreams"
UPSTREAM_COMMIT = "6a304c05bea7f774390a11082ea127719e99b70a"
UPSTREAM_SUBDIR = "galstreams/tracks"
LICENSE_KIND = "BSD-3-Clause"
LICENSE_HOLDER = "Copyright (c) 2017 Cecilia Mateu"
CITATION = "Mateu, C. 2023, MNRAS 520, 5225 (galstreams); library v1.2"

# The artifact this vendoring exists to make rebuildable, and the numbers it must produce.
ARTIFACT = "v0.3-prelim/outputs/t95/multi_stream_real_galstreams.json"
EXPECTED_ARTIFACT_STATS = {
    "n_streams_available": 123,
    "streams_with_gap_data": 10,
    "distance_range_kpc": [1.0, 95.0],
    "master_combined_loglik": -12.03806858128687,
}
LINE_ENDING_POLICY = (
    "md5 and bytes are the LF (git-canonical) form; md5_crlf records the CRLF form of the "
    "local checkout that was vendored. This repository normalizes text to LF "
    "(* text=auto eol=lf), so clones see LF bytes and the pin matches everywhere."
)


def host_catalog_root() -> Path:
    """Where a locally installed galstreams catalog lives (no host name spelled out)."""
    env = os.environ.get("DM_SIDM_GALSTREAMS_ROOT")
    if env:
        return Path(env)
    return Path.home() / "galstreams" / "galstreams" / "tracks"


def to_lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _digests(data: bytes) -> tuple[str, str, int]:
    """(md5 of the LF form, md5 of the CRLF form, size of the LF form) for one file."""
    lf = to_lf(data)
    crlf = lf.replace(b"\n", b"\r\n")
    return hashlib.md5(lf).hexdigest(), hashlib.md5(crlf).hexdigest(), len(lf)


def _entry(name: str, data: bytes) -> dict:
    md5_lf, md5_crlf, size = _digests(data)
    return {"name": name, "md5": md5_lf, "bytes": size, "md5_crlf": md5_crlf}


def _load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _manifest_files(manifest: dict) -> list[dict]:
    return manifest["files"]


def write_manifest(files: list[dict], source: str) -> dict:
    files = sorted(files, key=lambda e: e["name"])
    manifest = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "upstream_repo": UPSTREAM_REPO,
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_subdir": UPSTREAM_SUBDIR,
        "license": LICENSE_KIND,
        "license_holder": LICENSE_HOLDER,
        "license_file": LICENSE_FILE.name,
        "citation": CITATION,
        "line_ending_policy": LINE_ENDING_POLICY,
        "supports_artifact": ARTIFACT,
        "expected_artifact_stats": EXPECTED_ARTIFACT_STATS,
        "counts": {
            "files": len(files),
            "summary_files": sum(1 for f in files if f["name"].endswith(".summary.ecsv")),
            "full_track_files": sum(1 for f in files if not f["name"].endswith(".summary.ecsv")),
            "bytes": sum(f["bytes"] for f in files),
        },
        "files": files,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def install_from_host() -> int:
    root = host_catalog_root()
    if not root.is_dir():
        print(f"FAIL: no galstreams catalog at {root}")
        print("      set DM_SIDM_GALSTREAMS_ROOT to the directory holding track.st.*.ecsv")
        return 1
    previous = _load_manifest() if MANIFEST.exists() else None
    if previous is None:
        print("FAIL: no MANIFEST.json yet; the pinned file set must be declared before copying")
        return 1
    TRACKS_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    missing: list[str] = []
    for want in _manifest_files(previous):
        src = root / want["name"]
        if not src.is_file():
            missing.append(want["name"])
            continue
        entry = _entry(want["name"], src.read_bytes())
        if entry["md5"] != want["md5"]:
            print(f"FAIL: {want['name']}: LF md5 {entry['md5']} != pinned {want['md5']} "
                  f"(its CRLF form is {entry['md5_crlf']})")
            return 1
        (TRACKS_DIR / want["name"]).write_bytes(to_lf(src.read_bytes()))
        entries.append(entry)
    if missing:
        print(f"FAIL: {len(missing)} pinned file(s) absent from {root}:")
        for name in missing[:10]:
            print("  ", name)
        return 1
    manifest = write_manifest(entries, source="local catalog (LF-normalised, md5-verified)")
    print(f"vendored {manifest['counts']['files']} files "
          f"({manifest['counts']['bytes'] / 1e6:.1f} MB, LF form) into {TRACKS_DIR}")
    return 0


def fetch() -> int:
    previous = _load_manifest() if MANIFEST.exists() else None
    if previous is None:
        print("FAIL: no MANIFEST.json; --fetch needs the pinned file list")
        return 1
    TRACKS_DIR.mkdir(parents=True, exist_ok=True)
    base = f"https://raw.githubusercontent.com/{_repo_slug()}/{UPSTREAM_COMMIT}/{UPSTREAM_SUBDIR}"
    entries: list[dict] = []
    for want in _manifest_files(previous):
        dest = TRACKS_DIR / want["name"]
        url = f"{base}/{want['name']}"
        if dest.is_file():
            have = _entry(want["name"], dest.read_bytes())
            if have["md5"] == want["md5"]:
                entries.append(have)
                continue
        req = urllib.request.Request(url, headers={"User-Agent": "sidm-composite-dm-mediator data pin"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read()
        except Exception as exc:  # noqa: BLE001 - report, do not guess
            print(f"FAIL: {want['name']}: download error {type(exc).__name__}: {exc}")
            return 1
        got = _entry(want["name"], body)
        if got["md5"] != want["md5"]:
            print(f"FAIL: {want['name']}: upstream LF md5 {got['md5']} != pinned {want['md5']}")
            print(f"      url was {url}")
            return 1
        dest.write_bytes(to_lf(body))
        entries.append(got)
    manifest = write_manifest(entries, source=f"upstream download at commit {UPSTREAM_COMMIT}")
    print(f"fetched {manifest['counts']['files']} files from {UPSTREAM_REPO}")
    return 0


def _repo_slug() -> str:
    # github.com/cmateu/galstreams -> cmateu/galstreams, without spelling any host path.
    return UPSTREAM_REPO.split("github.com/", 1)[1].strip("/")


def verify() -> int:
    problems = check()
    if problems:
        print("FAIL: galstreams vendored copy does not match its manifest")
        for p in problems:
            print("  ", p)
        return 1
    manifest = _load_manifest()
    c = manifest["counts"]
    print(f"OK: {c['files']} vendored files verified ({c['bytes'] / 1e6:.1f} MB) "
          f"against {MANIFEST.relative_to(REPO)}")
    return 0


def check(manifest: dict | None = None, tracks_dir: Path | None = None) -> list[str]:
    """Independent re-derivation of everything the manifest asserts. Used by the guard test."""
    manifest = manifest or (_load_manifest() if MANIFEST.exists() else None)
    tracks_dir = tracks_dir or TRACKS_DIR
    if manifest is None:
        return [f"missing manifest at {MANIFEST}"]

    problems: list[str] = []
    for key in ("upstream_repo", "upstream_commit", "license", "license_file", "files", "counts"):
        if key not in manifest:
            problems.append(f"manifest missing required key '{key}'")
    if problems:
        return problems

    if manifest["license"] != LICENSE_KIND:
        problems.append(f"license recorded as {manifest['license']!r}, expected {LICENSE_KIND!r}")
    if not (tracks_dir.parent / manifest["license_file"]).exists():
        problems.append(f"license file {manifest['license_file']} not beside the vendored tracks")

    want_names = set()
    for entry in manifest["files"]:
        name = entry["name"]
        want_names.add(name)
        path = tracks_dir / name
        if not path.is_file():
            problems.append(f"{name}: declared in manifest but not vendored")
            continue
        raw = path.read_bytes()
        md5_lf, md5_crlf, size = _digests(raw)
        if raw != to_lf(raw):
            # .gitattributes pins these files to LF. A CRLF file on disk is a real divergence,
            # not cosmetics: reading the vendored copy in its CRLF form is exactly how the
            # original pin became clone-hostile, so the checker says which form it found.
            problems.append(
                f"{name}: on-disk bytes are CRLF but the pin and .gitattributes require LF "
                f"(CRLF md5 {md5_crlf}, pinned LF md5 {entry['md5']})"
            )
        if md5_lf != entry["md5"]:
            problems.append(f"{name}: LF md5 {md5_lf} != pinned {entry['md5']}")
        if size != entry["bytes"]:
            problems.append(f"{name}: LF size {size} != pinned {entry['bytes']}")

    extra = sorted(p.name for p in tracks_dir.glob("*.ecsv") if p.name not in want_names)
    if extra:
        problems.append(f"{len(extra)} file(s) present but not declared: {extra[:5]}")

    counts = manifest["counts"]
    actual_files = len(manifest["files"])
    if counts["files"] != actual_files:
        problems.append(f"counts.files {counts['files']} != {actual_files} declared files")
    actual_bytes = sum(e["bytes"] for e in manifest["files"])
    if counts["bytes"] != actual_bytes:
        problems.append(f"counts.bytes {counts['bytes']} != recomputed {actual_bytes}")
    n_summ = sum(1 for e in manifest["files"] if e["name"].endswith(".summary.ecsv"))
    if counts["summary_files"] != n_summ:
        problems.append(f"counts.summary_files {counts['summary_files']} != recomputed {n_summ}")
    if counts["full_track_files"] != actual_files - n_summ:
        problems.append("counts.full_track_files disagrees with the declared files")

    # The census the artifact depends on has to be derivable from the vendored copy alone.
    streams = {
        p.name[len("track.st."):].split(".")[0]
        for p in tracks_dir.glob("track.st.*.summary.ecsv")
    }
    if len(streams) < counts["summary_files"]:
        problems.append(
            f"stream census collapse: {len(streams)} stream names from {counts['summary_files']} summaries"
        )
    expected = manifest.get("expected_artifact_stats")
    if expected and expected.get("n_streams_available") and len(streams) < expected["n_streams_available"]:
        problems.append(
            f"vendored copy supports {len(streams)} streams but the artifact reports "
            f"{expected['n_streams_available']}"
        )
    return problems


def census() -> int:
    if not TRACKS_DIR.is_dir():
        print(f"FAIL: {TRACKS_DIR} not vendored yet (run --install-from-host or --fetch)")
        return 1
    problems = check()
    if problems:
        print("FAIL: vendored copy is inconsistent")
        for p in problems:
            print("  ", p)
        return 1
    summaries = sorted(TRACKS_DIR.glob("track.st.*.summary.ecsv"))
    full = sorted(p for p in TRACKS_DIR.glob("track.st.*.ecsv") if not p.name.endswith(".summary.ecsv"))
    streams = {p.name[len("track.st."):].split(".")[0] for p in summaries}
    print(json.dumps({
        "vendored_files": len(summaries) + len(full),
        "summary_files": len(summaries),
        "full_track_files": len(full),
        "stream_names": len(streams),
        "bytes_lf": sum(len(to_lf(p.read_bytes())) for p in summaries + full),
    }, indent=2))
    return 0


def seed_manifest_from_catalog() -> int:
    """Bootstrap helper: declare the pinned file set from a live catalog (first time only)."""
    if MANIFEST.exists():
        print("MANIFEST.json already exists; refusing to overwrite (use --install-from-host)")
        return 1
    root = host_catalog_root()
    if not root.is_dir():
        print(f"FAIL: no catalog at {root}")
        return 1
    entries = [_entry(p.name, p.read_bytes()) for p in sorted(root.glob("*.ecsv"))]
    manifest = write_manifest(entries, source="seeded from local catalog (declare-before-copy)")
    print(f"declared {manifest['counts']['files']} candidate files; prune to the read set")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install-from-host", action="store_true")
    group.add_argument("--fetch", action="store_true")
    group.add_argument("--verify", action="store_true")
    group.add_argument("--census", action="store_true")
    group.add_argument("--seed-manifest", action="store_true", help=argparse.SUPPRESS)
    group.add_argument("--check-json", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.install_from_host:
        return install_from_host()
    if args.fetch:
        return fetch()
    if args.verify:
        return verify()
    if args.census:
        return census()
    if args.seed_manifest:
        return seed_manifest_from_catalog()
    problems = check()
    print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
