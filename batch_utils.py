"""
Structured logging + checkpoint/resume utilities for dm-sidm-pipeline.

Per peer review (2026-08-10, Short-Term #2):
    "Implement structured file logging + batch checkpoint/resume for all
     T1/T4/T6 galaxy batch runners. Batch fit scripts only print error text
     to stdout when a galaxy fit fails; there is no persistent structured
     logging (JSON/logfile), no checkpoint/resume functionality for long-
     running batch jobs."

Provides:
    - JSONL batch logger (one event per line, machine-parseable)
    - Checkpoint file: JSON listing completed galaxies + their fit summaries
    - Resume support: skip already-completed galaxies on re-run

Usage:
    from batch_utils import BatchLogger, CheckpointState

    cp = CheckpointState(checkpoint_path)
    logger = BatchLogger(log_path)

    for galaxy in galaxies:
        if cp.is_done(galaxy.name):
            continue
        try:
            result = fit_one(galaxy)
            cp.mark_done(galaxy.name, result_summary=...)
            logger.info("fit_complete", galaxy=galaxy.name, log_Z=result["log_Z"])
        except Exception as e:
            logger.error("fit_failed", galaxy=galaxy.name, error=str(e))
            cp.mark_failed(galaxy.name, error=str(e))

    cp.save()  # persists state to disk

The default checkpoint/log locations are derived from config.py
(checkpoint_v0<N>.json, batch_run_v0<N>.jsonl) so users don't hardcode.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Optional
from config import get_version_paths


class BatchLogger:
    """JSONL batch event logger.

    Each event is a single JSON line with at minimum:
        {ts, level, event, ...}

    Levels: debug, info, warn, error.
    """

    def __init__(self, log_path: Path, batch_name: str = "batch"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.batch_name = batch_name

    def _log(self, level: str, event: str, **fields):
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "batch": self.batch_name,
            "level": level,
            "event": event,
            **fields,
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

    def debug(self, event: str, **fields): self._log("debug", event, **fields)
    def info(self,  event: str, **fields): self._log("info",  event, **fields)
    def warn(self,  event: str, **fields): self._log("warn",  event, **fields)
    def error(self, event: str, **fields): self._log("error", event, **fields)


class CheckpointState:
    """Persistent checkpoint file for batch runners.

    Tracks per-galaxy state:
        done:    {galaxy_name: result_summary_dict}
        failed:  {galaxy_name: error_string}
        pending: {galaxy_name: started_at_or_None}
    """

    def __init__(self, checkpoint_path: Path):
        self.path = Path(checkpoint_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._state = {"done": {}, "failed": {}, "pending": {}}
        if self.path.exists():
            try:
                self._state = json.loads(self.path.read_text(encoding="utf-8"))
                # Ensure all expected keys exist (backward compat)
                for k in ("done", "failed", "pending"):
                    self._state.setdefault(k, {})
            except json.JSONDecodeError:
                # Corrupted checkpoint → start fresh, but keep backup
                backup = self.path.with_suffix(".corrupt.json")
                self.path.rename(backup)
                self._state = {"done": {}, "failed": {}, "pending": {}}

    def is_done(self, galaxy_name: str) -> bool:
        return galaxy_name in self._state["done"]

    def is_failed(self, galaxy_name: str) -> bool:
        """Returns True if a galaxy has FAILED (so we skip on resume, but
        optionally retry by setting retry_failed=True in mark_failed)."""
        return galaxy_name in self._state["failed"]

    def mark_pending(self, galaxy_name: str):
        self._state["pending"][galaxy_name] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.save()

    def mark_done(self, galaxy_name: str, result_summary: Optional[dict] = None):
        self._state["done"][galaxy_name] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            **(result_summary or {}),
        }
        self._state["pending"].pop(galaxy_name, None)
        self.save()

    def mark_failed(self, galaxy_name: str, error: str, retry: bool = False):
        if retry and galaxy_name in self._state["failed"]:
            del self._state["failed"][galaxy_name]
        self._state["failed"][galaxy_name] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "error": error,
        }
        self._state["pending"].pop(galaxy_name, None)
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    @property
    def n_done(self) -> int: return len(self._state["done"])
    @property
    def n_failed(self) -> int: return len(self._state["failed"])
    @property
    def n_pending(self) -> int: return len(self._state["pending"])

    def summary(self) -> dict:
        return {
            "n_done": self.n_done,
            "n_failed": self.n_failed,
            "n_pending": self.n_pending,
            "checkpoint_path": str(self.path),
        }


def get_batch_paths(version: str, batch_name: str = "main") -> dict:
    """Convenience: get default checkpoint + log paths for a given version."""
    paths = get_version_paths(version)
    return {
        "checkpoint": paths["results"] / f"checkpoint_{batch_name}.json",
        "log": paths["results"] / f"batch_log_{batch_name}.jsonl",
    }


__all__ = ["BatchLogger", "CheckpointState", "get_batch_paths"]