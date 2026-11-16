#!/usr/bin/env python3
"""fetch_fermi_mcdaniel.py — fetch and verify the McDaniel+2024 Fermi-LAT dSph bundle.

RE-PINNING (2026-11-16). The old fetcher carried its own hand-copied table
`file_id|md5|name|size` inside fetch_external_data.sh. Two things were wrong with that:

1. The authority was never stated. The hashes were true -- they equal figshare's own
   `computed_md5` for article 24058650 -- but nothing in the repository said where they came
   from or how to re-derive them, so a future mismatch could only be "fixed" by trusting
   whatever the download happened to return.
2. The size column was parsed and never enforced, and `curl -sS` (no `-f`) saved a
   `403 Forbidden` nginx page AS dSphs.csv (146 bytes) in a clone on 2026-11-15 before the md5
   check could reject it.

Pins now live in scripts/figshare_24058650_pins.json: figshare's `computed_md5` and `size`
for each file, read from the metadata API
(https://api.figshare.com/v2/articles/24058650), which answers 200 even when the download
endpoint rate-limits with 403. `--repin` re-derives the table from that API; `--check`
verifies the files already on disk without touching the network.

Data: McDaniel et al. 2024 (arXiv:2311.04982), figshare DOI 10.6084/m9.figshare.24058650.v2,
CC BY 4.0. Reference: docs/REVIEWER_AUDIT_R11.md G11 (2026-08-14).

Usage:
    python scripts/fetch_fermi_mcdaniel.py            # fetch missing files, verify all
    python scripts/fetch_fermi_mcdaniel.py --check    # verify on-disk files only (no network)
    python scripts/fetch_fermi_mcdaniel.py --repin    # re-derive pins from the metadata API
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (REPO_ROOT honours DM_SIDM_PROJECT_ROOT so a clone/worktree works)

REPO = paths.REPO_ROOT
PINS_PATH = Path(__file__).resolve().parent / "figshare_24058650_pins.json"
DEST = REPO / "v0.3-prelim/data/external/fermi_mcdaniel2024"
USER_AGENT = "sidm-composite-dm-mediator/1.0 (external data integrity verification)"
HTML_MARKERS = (b"<html", b"<!DOCTYPE", b"<!doctype", b"<HTML")


def load_pins(pins_path: Path | None = None) -> dict:
    path = pins_path or PINS_PATH
    if not path.exists():
        raise SystemExit(f"missing pin file {path} (run: python scripts/fetch_fermi_mcdaniel.py --repin)")
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_targets(pins: dict) -> list[dict]:
    return [f for f in pins["files"] if f.get("fetched_by_this_project")]


def md5_of(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def verify_bytes(data: bytes, pin: dict) -> list[str]:
    """Why a body is or is not the file the pin describes. Pure: no network, no disk.

    figshare's own computed_md5 is the authority. A body that hashes to it IS the file,
    whatever it looks like: basic_data_usage.html is a 961,845-byte HTML document because the
    deposit itself is a rendered notebook, and a sniff that rejects anything starting with
    '<!DOCTYPE' condemns a correct file. An earlier version of this function did exactly that,
    reported the verified copy as an error page, deleted it, and then could not re-download it
    (finding F42). So: hash first; if the hash matches, nothing else gets a vote. Only when the
    hash mismatches does the body's shape explain WHICH failure happened -- anti-bot challenge,
    truncation, or a replaced file -- because those call for different responses.
    """
    digest = md5_of(data)
    if digest == pin["computed_md5"]:
        return []
    problems: list[str] = []
    head = data[:64].lstrip()
    challenged = (any(head.startswith(m) for m in HTML_MARKERS)
                  or b"awsWaf" in data[:4096] or b"403 Forbidden" in data[:512])
    if len(data) != pin["size"]:
        problems.append(f"{pin['name']}: {len(data)} bytes, pin says {pin['size']}")
    if challenged:
        reason = ("the body is an HTML/anti-bot challenge page -- figshare's ndownloader endpoint "
                  "sits behind AWS WAF, which challenges non-browser clients (202 with a challenge "
                  "body, or 403); the metadata API that produced these pins does not")
    else:
        reason = "the bytes differ from the pinned file"
    problems.append(
        f"{pin['name']}: md5 {digest} != figshare computed_md5 {pin['computed_md5']} -- {reason}"
    )
    return problems


def _open(url: str, timeout: int = 120):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}),
                                  timeout=timeout)


def download(pin: dict, timeout: int = 180) -> tuple[bytes | None, list[str]]:
    url = pin.get("download_url") or f"https://ndownloader.figshare.com/files/{pin['file_id']}"
    try:
        with _open(url, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            if status == 202:
                # Measured 2026-11-16: figshare answers 202 with an empty body (or a 2 KB AWS WAF
                # challenge) for clients it does not recognise, and 403 from the bare
                # ndownloader host even in a browser. The bytes never arrive.
                return None, [f"{pin['name']}: HTTP 202 from {url} -- figshare queued the download "
                              "instead of serving it; retry later or fetch from a browser session"]
            if status != 200:
                return None, [f"{pin['name']}: HTTP {status} from {url}"]
            data = resp.read()
    except urllib.error.HTTPError as exc:
        # A 4xx/5xx body is never data: refuse it instead of writing it to the destination.
        return None, [f"{pin['name']}: HTTP {exc.code} from {url} (body not written)"]
    except urllib.error.URLError as exc:
        return None, [f"{pin['name']}: network error reaching {url}: {exc.reason}"]
    problems = verify_bytes(data, pin)
    if problems:
        return None, problems
    return data, []


def check_local(pins: dict, dest: Path) -> list[str]:
    problems: list[str] = []
    for pin in fetch_targets(pins):
        path = dest / pin["name"]
        if not path.is_file():
            problems.append(f"{pin['name']}: not present at {path}")
            continue
        problems.extend(verify_bytes(path.read_bytes(), pin))
    return problems


def extract_tarball(pins: dict, dest: Path) -> str:
    tar = dest / "dSphs.tar.gz"
    out = dest / "dSphs"
    if out.is_dir():
        return "dSphs/ already extracted"
    if not tar.is_file():
        return "dSphs.tar.gz missing; nothing extracted"
    with tarfile.open(tar, "r:gz") as tf:
        # Reject members that would escape the destination directory.
        for member in tf.getmembers():
            parts = Path(member.name).parts
            if member.name.startswith("/") or ".." in parts:
                raise SystemExit(f"refusing unsafe tar member {member.name!r}")
        tf.extractall(dest)
    return f"extracted {tar.name} -> {out}"


def repin(dest_json: Path | None = None) -> int:
    """Re-derive every size/md5 from the figshare metadata API, keeping the fetch subset."""
    pins = load_pins()
    url = pins["metadata_api"]
    try:
        with _open(url, timeout=60) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"FAIL: could not reach {url}: {exc}", file=sys.stderr)
        return 1
    upstream = {f["id"]: f for f in meta["files"]}
    changed: list[str] = []
    for pin in pins["files"]:
        up = upstream.get(pin["file_id"])
        if up is None:
            changed.append(f"{pin['name']}: file_id {pin['file_id']} no longer in the article")
            continue
        if up["size"] != pin["size"] or up["computed_md5"] != pin["computed_md5"]:
            changed.append(
                f"{pin['name']}: {pin['size']}/{pin['computed_md5']} -> "
                f"{up['size']}/{up['computed_md5']}"
            )
            pin["size"], pin["computed_md5"] = up["size"], up["computed_md5"]
        pin["download_url"] = up.get("download_url", pin.get("download_url"))
    extra = sorted(set(upstream) - {p["file_id"] for p in pins["files"]})
    pins["retrieved_at"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (dest_json or PINS_PATH).write_text(json.dumps(pins, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8")
    print(json.dumps({"retrieved_at": pins["retrieved_at"], "changed": changed,
                      "new_files_upstream": extra}, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="verify on-disk files, no network")
    ap.add_argument("--repin", action="store_true", help="re-derive pins from the metadata API")
    ap.add_argument("--force", action="store_true", help="re-download even if the file verifies")
    args = ap.parse_args()

    pins = load_pins()
    if args.repin:
        return repin()

    DEST.mkdir(parents=True, exist_ok=True)
    print(f"# figshare {pins['article_id']} ({pins['doi']}) -> {DEST}")
    failed: list[str] = []
    for pin in fetch_targets(pins):
        path = DEST / pin["name"]
        if path.is_file() and not args.force:
            problems = verify_bytes(path.read_bytes(), pin)
            if not problems:
                print(f"[OK]   {pin['name']} ({pin['size']} bytes, matches computed_md5)")
                continue
            print(f"[WARN] {pin['name']}: {'; '.join(problems)} -- attempting re-fetch")
        data, problems = download(pin)
        if data is None:
            failed.extend(problems)
            # The local copy stays exactly where it was. A failed download must never leave the
            # destination worse than it found it (finding F42).
            print(f"[FAIL] {'; '.join(problems)} -- local copy left untouched", file=sys.stderr)
            continue
        if path.exists():
            path.unlink()   # only now, with verified bytes already in memory
        path.write_bytes(data)
        print(f"[OK]   {pin['name']} ({len(data)} bytes, matches computed_md5)")

    if not failed:
        print(f"[OK]   {extract_tarball(pins, DEST)}")
        ts = DEST / "dSphs" / "TS_profiles"
        if ts.is_dir():
            print(f"[OK]   TS profiles: {len(list(ts.iterdir()))} files")
    else:
        print(f"# {len(failed)} file(s) failed verification; cited data left untouched",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
