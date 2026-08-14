#!/usr/bin/env python
"""
Test the BatchLogger + CheckpointState utilities (peer-review Short-Term #2).

Tests cover:
    1. BatchLogger writes valid JSONL
    2. CheckpointState is created empty when no file exists
    3. CheckpointState is created from existing file on init
    4. mark_done, mark_failed, mark_pending persist across reload
    5. is_done / is_failed return correct boolean
    6. summary() reports correct counts
    7. Corrupted checkpoint → starts fresh + saves backup
"""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
import sys

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from batch_utils import BatchLogger, CheckpointState


def test_logger_writes_jsonl(tmp_path: Path):
    log_path = tmp_path / "test.jsonl"
    logger = BatchLogger(log_path, batch_name="test")
    logger.info("start", n_galaxies=10)
    logger.error("oops", galaxy="NGC2403", error="numerical issue")
    text = log_path.read_text()
    lines = [json.loads(line) for line in text.strip().split("\n")]
    assert len(lines) == 2
    assert lines[0]["level"] == "info"
    assert lines[0]["event"] == "start"
    assert lines[0]["n_galaxies"] == 10
    assert lines[1]["level"] == "error"
    assert lines[1]["galaxy"] == "NGC2403"
    print("  PASS test_logger_writes_jsonl")


def test_checkpoint_creates_empty(tmp_path: Path):
    cp_path = tmp_path / "cp.json"
    cp = CheckpointState(cp_path)
    assert cp.n_done == 0
    assert cp.n_failed == 0
    assert cp.n_pending == 0
    print("  PASS test_checkpoint_creates_empty")


def test_checkpoint_persists(tmp_path: Path):
    cp_path = tmp_path / "cp.json"
    cp1 = CheckpointState(cp_path)
    cp1.mark_done("NGC2403", result_summary={"log_Z": -42.5})
    cp1.mark_failed("NGC2841", error="divergence")
    cp1.mark_pending("NGC6946")

    # Reload from disk
    cp2 = CheckpointState(cp_path)
    assert cp2.n_done == 1
    assert cp2.n_failed == 1
    assert cp2.n_pending == 1
    assert cp2.is_done("NGC2403")
    assert cp2.is_failed("NGC2841")
    print("  PASS test_checkpoint_persists")


def test_checkpoint_corrupted(tmp_path: Path):
    """Corrupted checkpoint should be backed up + a fresh state created."""
    cp_path = tmp_path / "cp.json"
    cp_path.write_text("{this is not valid JSON", encoding="utf-8")
    cp = CheckpointState(cp_path)
    # Should have backed up the corrupted file
    backup = cp_path.with_suffix(".corrupt.json")
    assert backup.exists()
    # And should start fresh
    assert cp.n_done == 0
    print("  PASS test_checkpoint_corrupted")


def test_checkpoint_summary(tmp_path: Path):
    cp_path = tmp_path / "cp.json"
    cp = CheckpointState(cp_path)
    cp.mark_done("a"); cp.mark_done("b"); cp.mark_done("c")
    cp.mark_failed("d", error="mock failure")
    s = cp.summary()
    assert s["n_done"] == 3
    assert s["n_failed"] == 1
    assert str(cp_path) == s["checkpoint_path"]
    print("  PASS test_checkpoint_summary")


def test_mark_done_removes_pending(tmp_path: Path):
    cp_path = tmp_path / "cp.json"
    cp = CheckpointState(cp_path)
    cp.mark_pending("g1")
    assert cp.n_pending == 1
    cp.mark_done("g1")
    assert cp.n_pending == 0
    assert cp.n_done == 1
    print("  PASS test_mark_done_removes_pending")


if __name__ == "__main__":
    print("=== batch_utils tests ===")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_logger_writes_jsonl(tmp_path)
        test_checkpoint_creates_empty(tmp_path)
        test_checkpoint_persists(tmp_path)
        test_checkpoint_corrupted(tmp_path)
        test_checkpoint_summary(tmp_path)
        test_mark_done_removes_pending(tmp_path)
    print("\nAll batch_utils tests passed.")