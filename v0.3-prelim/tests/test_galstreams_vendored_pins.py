"""Guards for the vendored galstreams catalog (finding F39, closed 2026-11-16).

The invariant being protected is not "the files exist" but "the numbers in
v0.3-prelim/outputs/t95/multi_stream_real_galstreams.json can be re-derived from data that
travels with the repository". Every test here either re-derives something or proves that the
checker fails when the data is wrong -- F36/F38/F40 were all guards that asserted how things
are written instead of what they do, and each passed while its invariant was broken.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent.parent  # v0.3-prelim/tests -> repository root
sys.path.insert(0, str(REPO / "scripts"))

import galstreams_pins as gp  # noqa: E402

VENDOR = REPO / "v0.3-prelim" / "data" / "external_data" / "galstreams"
TRACKS = VENDOR / "tracks"
MANIFEST_PATH = VENDOR / "MANIFEST.json"
ARTIFACT = REPO / "v0.3-prelim" / "outputs" / "t95" / "multi_stream_real_galstreams.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ the pin itself
def test_vendored_catalog_matches_its_manifest():
    """Every declared file is present, byte-exact, and no undeclared file snuck in."""
    problems = gp.check()
    assert not problems, problems


def test_manifest_declares_upstream_provenance_and_licence():
    m = _manifest()
    assert m["upstream_repo"] == gp.UPSTREAM_REPO
    assert len(m["upstream_commit"]) == 40, "upstream must be pinned to a full commit sha"
    assert m["license"] == "BSD-3-Clause"
    assert "Mateu" in m["citation"]
    licence = VENDOR / m["license_file"]
    assert licence.exists(), "the upstream licence text must travel with the vendored data"
    text = licence.read_text(encoding="utf-8", errors="replace")
    assert "BSD 3-Clause" in text and "Cecilia Mateu" in text


def test_manifest_and_readme_name_no_host_path():
    """A data manifest that spells out one machine's home directory is not portable.

    The username being banned is read from the running host instead of written as a literal.
    Spelled literally, the guard's own source contains the host username, which is exactly what
    CG-16 forbids in live-scope code -- and CG-16 duly flagged this file on this round's first
    gate run. The check still bites; it simply does not advertise the machine it was written on.
    """
    host_user = Path.home().name
    assert host_user, "no host username available to check against"
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    assert host_user not in text, f"host username {host_user!r} appears in the data manifest"
    # A drive-letter path (C:\x or C:/x). The negative lookahead is deliberate: the manifest
    # legitimately carries https:// provenance URLs, and a pattern that flags "s://" would be a
    # guard that fails on the thing it is supposed to certify.
    assert re.search(r"\b[A-Za-z]:[\\/](?![\\/])", text) is None, (
        "absolute windows path in the manifest")
    assert "/home/" not in text, "posix home path in the data manifest"
    readme = (VENDOR / "README.md").read_text(encoding="utf-8", errors="replace")
    assert "BSD" in readme and "galstreams" in readme.lower()


def test_vendored_files_are_in_the_pinned_line_ending_form():
    """The pin is the LF form; git checkout handing CRLF would silently break every hash.

    This is the failure mode the re-pin was about: the upstream checkout on the vendoring
    machine is core.autocrlf (CRLF), while this repository normalises to LF. A pin recorded in
    the CRLF form would have verified on that one machine and failed in every clone.
    """
    m = _manifest()
    offenders = []
    for entry in m["files"]:
        data = (TRACKS / entry["name"]).read_bytes()
        if data != gp.to_lf(data):
            offenders.append(entry["name"])
        if len(data) != entry["bytes"]:
            offenders.append(f"{entry['name']} (size {len(data)} != pinned {entry['bytes']})")
    assert not offenders, f"{len(offenders)} file(s) not in the pinned LF form: {offenders[:5]}"


# ------------------------------------------------------------------ what the data must support
def test_vendored_copy_supports_the_certified_stream_census():
    """The artifact's stream count must be derivable from the vendored files alone."""
    m = _manifest()
    stream_names = {
        p.name[len("track.st."):].split(".")[0] for p in TRACKS.glob("track.st.*.summary.ecsv")
    }
    declared = m["expected_artifact_stats"]["n_streams_available"]
    assert len(stream_names) >= declared, (
        f"vendored copy offers {len(stream_names)} stream names but the certified artifact "
        f"reports {declared}"
    )
    assert m["counts"]["summary_files"] == len(stream_names), (
        "one summary serving two stream names would make the census depend on which files "
        "happen to be present"
    )


def test_certified_artifact_numbers_are_what_the_pin_claims():
    """Cross-check the produced artifact against the numbers the manifest says it must produce."""
    if not ARTIFACT.exists():
        pytest.skip(f"{ARTIFACT.relative_to(REPO)} not produced yet; run t95_v25")
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    m = _manifest()
    stats = art["full_catalog_stats"]
    expected = m["expected_artifact_stats"]
    assert stats["n_streams_available"] == expected["n_streams_available"]
    assert stats["streams_with_gap_data"] == expected["streams_with_gap_data"]
    assert round(stats["distance_range_kpc"][0], 6) == round(expected["distance_range_kpc"][0], 6)
    assert round(stats["distance_range_kpc"][1], 6) == round(expected["distance_range_kpc"][1], 6)
    assert art["key_findings"]["master_combined_loglik"] == pytest.approx(
        expected["master_combined_loglik"], rel=1e-12
    )
    # The artifact must no longer record that it read a directory outside the repository.
    assert "external_data/galstreams" in art["galstreams_root"].replace("\\", "/"), (
        f"artifact still reads a catalog outside the repository: {art['galstreams_root']}"
    )


def test_stream_selection_is_no_longer_filesystem_order_dependent():
    """The script prefers an ibata2024 variant, but its sort is STABLE: with no ibata2024
    variant the winner is whatever the filesystem lists first. Vendoring must leave at most one
    variant per stream so the certified selection cannot change between machines."""
    variants: dict[str, list[str]] = {}
    for p in TRACKS.glob("track.st.*.ecsv"):
        if p.name.endswith(".summary.ecsv"):
            continue
        name = p.name[len("track.st."):].split(".")[0]
        variants.setdefault(name, []).append(p.name)
    multi = {k: v for k, v in variants.items() if len(v) > 1}
    assert not multi, (
        f"{len(multi)} stream(s) have several vendored track variants, so t95_v25's selection "
        f"depends on filesystem order again: {list(multi.items())[:3]}"
    )


# ------------------------------------------------------------------ falsifiability
def _tamper_dir(tmp_path: Path, *, drop: str | None = None, flip: str | None = None) -> tuple[dict, Path]:
    """Copy a slice of the vendored set into tmp_path, optionally breaking it."""
    m = _manifest()
    names = [e["name"] for e in m["files"]]
    if drop is None:
        drop = names[0]
    if flip is None:
        flip = names[1]
    keep = {drop, flip}
    slice_files = []
    for entry in m["files"]:
        if entry["name"] not in keep:
            continue
        data = (TRACKS / entry["name"]).read_bytes()
        if entry["name"] == flip:
            data = data[:-1]  # one byte shorter: same file, different bytes
        (tmp_path / "tracks").mkdir(parents=True, exist_ok=True)
        (tmp_path / "tracks" / entry["name"]).write_bytes(data)
        slice_files.append(dict(entry))
    m2 = dict(m)
    m2["files"] = slice_files
    m2["counts"] = {
        "files": len(slice_files),
        "summary_files": sum(1 for f in slice_files if f["name"].endswith(".summary.ecsv")),
        "full_track_files": sum(1 for f in slice_files if not f["name"].endswith(".summary.ecsv")),
        "bytes": sum(f["bytes"] for f in slice_files),
    }
    (tmp_path / "LICENSE.galstreams").write_text(
        (VENDOR / "LICENSE.galstreams").read_text(encoding="utf-8"), encoding="utf-8"
    )
    return m2, tmp_path


def test_checker_detects_altered_bytes(tmp_path):
    m2, dir2 = _tamper_dir(tmp_path)
    problems = gp.check(manifest=m2, tracks_dir=dir2 / "tracks")
    assert problems, "a byte-altered vendored file passed the integrity checker"
    assert any("md5" in p for p in problems), problems


def test_checker_detects_a_missing_declared_file(tmp_path):
    m2, dir2 = _tamper_dir(tmp_path)
    (dir2 / "tracks" / m2["files"][0]["name"]).unlink()
    problems = gp.check(manifest=m2, tracks_dir=dir2 / "tracks")
    assert problems, "a declared-but-absent vendored file passed the integrity checker"
    assert any("not vendored" in p for p in problems), problems


def test_checker_detects_a_crlf_checkout(tmp_path):
    """If a checkout hands back CRLF bytes, the checker must say so rather than call it corruption."""
    entry_name = _manifest()["files"][0]["name"]
    m2, dir2 = _tamper_dir(tmp_path, drop=entry_name, flip=entry_name)
    entry = m2["files"][0]
    lf = gp.to_lf((TRACKS / entry["name"]).read_bytes())
    (dir2 / "tracks" / entry["name"]).write_bytes(lf.replace(b"\n", b"\r\n"))
    problems = gp.check(manifest=m2, tracks_dir=dir2 / "tracks")
    assert problems, "a CRLF checkout passed an LF pin"
    assert any("CRLF" in p for p in problems), problems


def test_fetch_producer_is_tracked_and_rerunnable():
    producer = REPO / "scripts" / "galstreams_pins.py"
    assert producer.exists(), "the declared fetcher is not in the repository"
    m = _manifest()
    assert m["upstream_subdir"], "no upstream subdirectory recorded for the download path"
    url = f"https://raw.githubusercontent.com/{gp._repo_slug()}/{m['upstream_commit']}/{m['upstream_subdir']}/{m['files'][0]['name']}"
    assert url.startswith("https://raw.githubusercontent.com/cmateu/galstreams/6a304c05"), url
