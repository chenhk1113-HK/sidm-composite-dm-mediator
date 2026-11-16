"""Guards for the figshare re-pin (finding F41 follow-up, 2026-11-16).

The bundle itself was always correct: dSphs.csv is 3,897 bytes with md5
1627630e27c73cded88370a9344c66a2, and that equals figshare's own `computed_md5`. What was
missing was the authority chain -- where the hash came from, how to re-derive it, and whether
the verifier can actually fail. These tests pin all three.

Falsification runs through fermi.verify_bytes(), which is pure (bytes in, problems out), so a
broken check is provable without network access or a 4.4 GB download.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import fetch_fermi_mcdaniel as fermi  # noqa: E402

PINS_PATH = REPO / "scripts" / "figshare_24058650_pins.json"
WRAPPER = REPO / "scripts" / "fetch_external_data.sh"
DEST = REPO / "v0.3-prelim" / "data" / "external" / "fermi_mcdaniel2024"


def _pins() -> dict:
    return json.loads(PINS_PATH.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ the authority chain
def test_pin_file_states_where_the_hashes_come_from():
    pins = _pins()
    assert pins["article_id"] == 24058650
    assert pins["doi"] == "10.6084/m9.figshare.24058650.v2"
    assert "api.figshare.com/v2/articles/24058650" in pins["metadata_api"]
    assert "computed_md5" in pins["authority"], "the pin file must name its authority"
    assert "CC BY" in pins["license"]
    assert "arXiv:2311.04982" in pins["citation"]
    # A pin without a retrieval timestamp cannot be distinguished from a stale one.
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", pins["retrieved_at"]), pins["retrieved_at"]


def test_every_pin_is_a_well_formed_figshare_record():
    pins = _pins()
    assert pins["files"], "no files declared"
    for f in pins["files"]:
        assert re.fullmatch(r"[0-9a-f]{32}", f["computed_md5"]), f
        assert isinstance(f["size"], int) and f["size"] > 0, f
        assert f["download_url"].startswith("https://"), f
        assert f["name"], f


def test_fetch_subset_is_deliberate_and_explained():
    """The deposit carries 9 files, two of them ~4.47 GB. The project fetches 3, on purpose."""
    pins = _pins()
    fetched = fermi.fetch_targets(pins)
    names = {f["name"] for f in fetched}
    assert names == {"dSphs.csv", "dSphs.tar.gz", "basic_data_usage.html"}, names
    unfetched = [f for f in pins["files"] if not f.get("fetched_by_this_project")]
    assert unfetched, "the pin file should record the whole deposit, not only what was downloaded"
    assert max(f["size"] for f in unfetched) > 1_000_000_000, (
        "the not-fetched files should include the multi-GB blank_fields tarballs; that is the "
        "reason the subset is documented rather than assumed"
    )
    assert pins["fetch_total_bytes"] == sum(f["size"] for f in fetched)


def test_wrapper_delegates_and_keeps_no_second_copy_of_the_hashes():
    """Two hand-copied hash tables drift apart; only one location may hold the pins."""
    text = WRAPPER.read_text(encoding="utf-8", errors="replace")
    assert re.search(r"\b[0-9a-f]{32}\b", text) is None, (
        "the shell wrapper carries a hash literal; the pins belong in "
        "scripts/figshare_24058650_pins.json only"
    )
    assert "fetch_fermi_mcdaniel.py" in text, "the wrapper does not delegate to the fetcher"
    assert "--repin" in text and "--check" in text, "the wrapper hides the re-derive/verify modes"


# ------------------------------------------------------------------ falsification
def test_verifier_rejects_an_error_page():
    pins = _pins()
    pin = next(f for f in fermi.fetch_targets(pins) if f["name"] == "dSphs.csv")
    body = (b"<!DOCTYPE html>\n<html><head><title>403 Forbidden</title></head><body>"
            b"<h1>403 Forbidden</h1></body></html>\n")
    problems = fermi.verify_bytes(body, pin)
    assert problems, "a 403 HTML page passed verification -- this is how dSphs.csv got corrupted"
    assert any("HTML" in p or "error body" in p for p in problems), problems


def test_verifier_rejects_a_truncated_download():
    pins = _pins()
    pin = next(f for f in fermi.fetch_targets(pins) if f["name"] == "dSphs.csv")
    real = (DEST / pin["name"]).read_bytes() if (DEST / pin["name"]).is_file() else b""
    body = (real if real else b"x" * pin["size"])[: pin["size"] - 10]
    problems = fermi.verify_bytes(body, pin)
    assert problems, "a 10-byte-short file passed verification"
    assert any("bytes" in p for p in problems), problems


def test_verifier_rejects_a_replaced_file_of_the_exact_size():
    """Size and count can match while the content is different; md5 must be the backstop."""
    pins = _pins()
    pin = next(f for f in fermi.fetch_targets(pins) if f["name"] == "dSphs.csv")
    body = b"z" * pin["size"]
    problems = fermi.verify_bytes(body, pin)
    assert problems, "a fabricated file of the exact pinned size passed verification"
    assert any("computed_md5" in p for p in problems), problems


def test_verifier_accepts_the_bytes_that_are_cited():
    if not (DEST / "dSphs.csv").is_file():
        pytest.skip("fermi bundle not fetched on this machine")
    pins = _pins()
    for pin in fermi.fetch_targets(pins):
        path = DEST / pin["name"]
        if not path.is_file():
            continue
        problems = fermi.verify_bytes(path.read_bytes(), pin)
        assert not problems, f"{pin['name']}: {problems}"


def test_check_local_reports_a_missing_file(tmp_path):
    pins = _pins()
    problems = fermi.check_local(pins, tmp_path)
    assert len(problems) == len(fermi.fetch_targets(pins)), problems
    assert all("not present" in p for p in problems), problems


def test_tar_extractor_refuses_a_path_escaping_member(tmp_path):
    """The bundle is a third-party archive; extracting it must not be able to write outside it."""
    import tarfile

    pins = _pins()
    hostile = tmp_path / "dSphs.tar.gz"
    with tarfile.open(hostile, "w:gz") as tf:
        payload = tmp_path / "payload.txt"
        payload.write_text("escaped", encoding="utf-8")
        tf.add(payload, arcname="../escaped.txt")
    with pytest.raises(SystemExit) as exc:
        fermi.extract_tarball(pins, tmp_path)
    assert "unsafe tar member" in str(exc.value), exc.value


# ------------------------------------------------------------------ authority is still true
def test_pins_still_match_figshare_metadata_when_the_api_answers():
    """Re-derive from the source and compare. Skips offline rather than failing offline."""
    import urllib.error
    import urllib.request

    pins = _pins()
    req = urllib.request.Request(pins["metadata_api"], headers={"User-Agent": fermi.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        pytest.skip(f"figshare metadata API unreachable from this machine: {exc}")
    upstream = {f["id"]: f for f in meta["files"]}
    drift = []
    for pin in pins["files"]:
        up = upstream.get(pin["file_id"])
        if up is None:
            drift.append(f"{pin['name']}: file_id {pin['file_id']} gone from the article")
        elif (up["size"], up["computed_md5"]) != (pin["size"], pin["computed_md5"]):
            drift.append(f"{pin['name']}: {pin['size']}/{pin['computed_md5']} != "
                         f"{up['size']}/{up['computed_md5']}")
    assert not drift, f"pins drifted from figshare's own hashes: {drift}"
