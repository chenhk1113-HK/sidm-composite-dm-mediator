#!/usr/bin/env python3
"""
dual_review.py — Run a physics review through TWO independent reviewers and
consolidate their findings.

WHY TWO REVIEWERS
------------------
A single LLM reviewer is a single point of failure for a specific class of error:
it agrees with the draft it is reviewing. Two reviewers on DIFFERENT model
families, seeing the SAME draft, fail differently -- and the disagreement
between them is itself the most informative signal in the whole loop. When
Reviewer A flags a unit error that Reviewer B misses, the finding is very likely
real. When they contradict each other on a number, that number is exactly the
one the controller must compute before shipping.

REVIEWER 1 -- Nemotron 3 Ultra 550B (free, via OpenRouter)
    Runs as a Hermes delegation child, pinned per-task to
    "nvidia/nemotron-3-ultra-550b-a55b:free" / provider "openrouter".
    Pro: a 550B MoE with strong physics/algebra reasoning.
    Con: shares the Nemotron family with the OpenCode reviewer below, so it is
    NOT a fully independent family opinion.

REVIEWER 2 -- OpenCode CLI free model (priority chain, this script)
    The OpenCode free tier is CLI-ONLY: a direct API call returns HTTP 403
    FreeTierError, so it CANNOT be wired as a Hermes delegation.provider. It
    must be driven by shelling out to the `opencode` CLI. That is exactly what
    this script does -- and it means the transport differs from Reviewer 1
    while the loop shape does not: the reviewer returns review text, and the
    controller still verifies every number.

    Priority chain (user-specified 2026-10-22), first live one wins:
      1. opencode/deepseek-v4.1-flash-free
      2. opencode/glm-5.3-flash-free
      3. opencode/mimo-v2.6-flash-free
      4. opencode/nemotron-3-ultra-free
      5. opencode/nemotron-3.5-super-vl-free

    Pro: a DIFFERENT model family from Nemotron (DeepSeek / GLM / MiMo), so
    the two reviewers genuinely disagree differently.
    Con: the free-tier flash models are weaker than Nemotron Ultra on algebra.
    Treat their findings as a second opinion to be verified, not as authority.

WHAT THIS SCRIPT DOES AND DOES NOT DO
--------------------------------------
DOES:  run the OpenCode reviewer over the priority chain, capture the review
       text, and write it to a file with provenance metadata.
DOES NOT: judge the review, verify numbers, or decide what to change. That is
       the controller's job (see the m3-nemotron-review-workflow skill:
       "Nemotron fabricates specific numbers -- always verify"). This script
       deliberately does not merge or rank the two reviews; it keeps them
       separate and lets the controller compare them.

USAGE
-----
    python dual_review.py --prompt-file scripts/review_prompt_v40_64.txt \\
                          --out docs/OPENCODE_REVIEW_V40_64.md
    python dual_review.py --prompt-file <file> --out <file> --model <id>   # force a model
    python dual_review.py --probe-only                                      # liveness only
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# The user's priority order. First LIVE model wins; the rest are fallbacks.
PRIORITY_CHAIN = [
    "opencode/deepseek-v4.1-flash-free",
    "opencode/glm-5.3-flash-free",
    "opencode/mimo-v2.6-flash-free",
    "opencode/nemotron-3-ultra-free",
    "opencode/nemotron-3.5-super-vl-free",
]

# Dead / do-not-use ids, recorded so nobody re-probes them by mistake.
# `nemotron-3-5-super-vl-free` (hyphen) is a DIFFERENT id from
# `nemotron-3.5-super-vl-free` (dot) and is retired upstream: verified
# 2026-10-22, returns "Error: Upstream request failed: Model is unavailable."
DEAD_IDS = {
    "opencode/nemotron-3-5-super-vl-free": "Model is unavailable (verified 2026-10-22)",
    "opencode/beam-free": "geo-blocked (per prior session note)",
    "opencode/longcat-2.5-preview-free": "access-disabled (per prior session note)",
    "opencode/nemotron-3.5-lightning-free": "access-disabled (per prior session note)",
}

# Markers that mean the model is unavailable rather than "answered badly".
DEAD_PATTERNS = re.compile(
    r"(Model is unavailable|FreeTierError|403 Forbidden|"
    r"not found|no such model|Model not found|access[- ]disabled|"
    r"geo[- ]?blocked|not available|401 Unauthorized|unauthorized)",
    re.IGNORECASE,
)

PROBE_PROMPT = "Reply with exactly this and nothing else: READY-7"


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", s)


def _opencode_binary() -> str:
    exe = shutil.which("opencode")
    if exe:
        return exe
    for cand in ("opencode", "opencode.cmd", "opencode.exe"):
        for base in (Path.home() / "AppData/Roaming/npm",
                     Path("/c/Program Files/nodejs")):
            p = base / cand
            if p.exists():
                return str(p)
    raise FileNotFoundError(
        "opencode CLI not found on PATH. Install with: npm i -g opencode"
    )


def run_opencode(model: str, prompt: str, timeout: int = 300,
                 binary: str | None = None) -> dict:
    """Run one review through the opencode CLI. Never raises on model failure."""
    binary = binary or _opencode_binary()
    t0 = time.time()
    try:
        proc = subprocess.run(
            [binary, "run", "--model", model, "--format", "json", prompt],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return {"model": model, "ok": False, "reason": "TIMEOUT",
                "seconds": time.time() - t0, "text": ""}
    except Exception as exc:  # pragma: no cover
        return {"model": model, "ok": False, "reason": f"{type(exc).__name__}: {exc}",
                "seconds": time.time() - t0, "text": ""}

    out = _strip_ansi(proc.stdout or "")
    err = _strip_ansi(proc.stderr or "")
    seconds = time.time() - t0

    # --format json emits one JSON object per line; the assistant text lives in
    # the "text" events' part.text. Fall back to raw stdout if the shape moved.
    chunks: list[str] = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "text":
            part = ev.get("part") or {}
            txt = part.get("text")
            if txt:
                chunks.append(txt)
    text = "".join(chunks).strip()

    if not text:
        text = out.strip()

    # Availability check. Scan STDERR always, but scan STDOUT only when we
    # failed to extract any review text -- otherwise a legitimate review that
    # merely CONTAINS a phrase like "not found" or "401 Unauthorized" is
    # misclassified as a dead model. (Observed 2026-10-22: deepseek and glm
    # were wrongly flagged MODEL_UNAVAILABLE on a real prompt because the
    # review prose matched the pattern.)
    if DEAD_PATTERNS.search(err) or (not text and DEAD_PATTERNS.search(out)):
        return {"model": model, "ok": False, "reason": "MODEL_UNAVAILABLE",
                "seconds": seconds, "text": text,
                "detail": (err or out).strip()[:400]}

    if proc.returncode != 0 and not text:
        return {"model": model, "ok": False,
                "reason": f"EXIT_{proc.returncode}", "seconds": seconds, "text": "",
                "detail": (err or out).strip()[:400]}

    if not text:
        return {"model": model, "ok": False, "reason": "EMPTY_OUTPUT",
                "seconds": seconds, "text": "", "detail": (err or out).strip()[:400]}

    return {"model": model, "ok": True, "reason": "OK", "seconds": seconds,
            "text": text, "exit_code": proc.returncode}


def probe_model(model: str, timeout: int = 100, binary: str | None = None) -> dict:
    """Liveness check: does this model answer a trivial prompt at all?"""
    res = run_opencode(model, PROBE_PROMPT, timeout=timeout, binary=binary)
    if res["ok"] and "READY-7" in res["text"]:
        res["reason"] = "LIVE"
    elif res["ok"]:
        res["ok"] = False
        res["reason"] = "ANSWERED_BUT_NO_MARKER"
    return res


def run_with_fallback(prompt: str, chain: list[str] | None = None,
                       timeout: int = 300, binary: str | None = None,
                       verbose: bool = True) -> tuple[dict | None, list[dict]]:
    """Walk the priority chain until one model returns a real review."""
    chain = chain or PRIORITY_CHAIN
    attempts: list[dict] = []
    for model in chain:
        if model in DEAD_IDS:
            attempts.append({"model": model, "ok": False,
                             "reason": "KNOWN_DEAD", "seconds": 0.0,
                             "detail": DEAD_IDS[model]})
            if verbose:
                print(f"  SKIP {model} (known dead: {DEAD_IDS[model]})", flush=True)
            continue
        if verbose:
            print(f"  TRY  {model} ...", flush=True)
        res = run_opencode(model, prompt, timeout=timeout, binary=binary)
        attempts.append(res)
        if verbose:
            status = "OK" if res["ok"] else res["reason"]
            print(f"       -> {status} ({res['seconds']:.1f}s)", flush=True)
        if res["ok"]:
            return res, attempts
    return None, attempts


def write_review(res: dict, attempts: list[dict], out_path: Path,
                 prompt_path: Path | None, prompt_text: str) -> None:
    """Write the review to a markdown file with full provenance."""
    now = datetime.now(timezone.utc).astimezone()
    lines = [
        "# OpenCode CLI Review",
        "",
        f"**Model:** `{res['model']}`  ",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S %Z')}  ",
        f"**Duration:** {res['seconds']:.1f}s  ",
        "**Transport:** `opencode run --model <id>` (OpenCode free tier is CLI-only; "
        "direct API returns HTTP 403 FreeTierError)  ",
        "**Reviewer role:** second independent reviewer, different model family from "
        "the Nemotron/OpenRouter reviewer  ",
        "",
        "> **Status: UNVERIFIED SECOND OPINION.** This is one reviewer's critique. "
        "Every specific numerical claim below must be recomputed in Python before it is "
        "acted on -- the free-tier models fabricate plausible numbers. Compare against "
        "the Nemotron review: where they agree, the finding is likely real; where they "
        "disagree, that is the claim to compute first.",
        "",
    ]
    if prompt_path:
        lines += [f"**Prompt source:** `{prompt_path}`", ""]
    if attempts:
        lines += ["## Priority chain attempt log", "",
                  "| Model | Result | Seconds |", "|---|---|---|"]
        for a in attempts:
            lines.append(f"| `{a['model']}` | {a.get('reason')} | {a.get('seconds', 0):.1f} |")
        lines.append("")
    lines += ["## Review", "", res["text"], ""]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--prompt-file", help="file containing the review prompt")
    ap.add_argument("--prompt", help="review prompt as a literal string")
    ap.add_argument("--out", help="path to write the review markdown")
    ap.add_argument("--model", help="force a specific model (bypasses the chain)")
    ap.add_argument("--timeout", type=int, default=300, help="per-model timeout seconds")
    ap.add_argument("--probe-only", action="store_true",
                    help="probe the whole priority chain for liveness and exit")
    ap.add_argument("--json", action="store_true",
                    help="print the result summary as JSON on stdout")
    args = ap.parse_args(argv)

    if args.probe_only:
        print("Probing OpenCode free-model priority chain:\n")
        rows = []
        for m in PRIORITY_CHAIN:
            if m in DEAD_IDS:
                print(f"  {m:44s} KNOWN_DEAD  ({DEAD_IDS[m]})")
                rows.append({"model": m, "ok": False, "reason": "KNOWN_DEAD"})
                continue
            r = probe_model(m)
            print(f"  {m:44s} {r['reason']:10s} ({r['seconds']:.1f}s)")
            rows.append({"model": m, "ok": r["ok"], "reason": r["reason"],
                         "seconds": round(r["seconds"], 1)})
        if args.json:
            print(json.dumps(rows, indent=2))
        return 0

    prompt = args.prompt
    prompt_path = None
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt:
        print("ERROR: need --prompt-file or --prompt", file=sys.stderr)
        return 2

    attempts: list[dict] = []
    if args.model:
        print(f"Running forced model {args.model} ...", flush=True)
        res = run_opencode(args.model, prompt, timeout=args.timeout)
        attempts = [res]
    else:
        print("Running OpenCode reviewer over priority chain:\n", flush=True)
        res, attempts = run_with_fallback(prompt, timeout=args.timeout)

    if res is None:
        print("\nNo model in the priority chain returned a usable review.",
              file=sys.stderr)
        for a in attempts:
            print(f"  {a['model']}: {a.get('reason')} {a.get('detail','')[:200]}",
                  file=sys.stderr)
        return 1

    print(f"\nReview from {res['model']} ({res['seconds']:.1f}s)", flush=True)
    if args.out:
        out = Path(args.out)
        write_review(res, attempts, out, prompt_path, prompt)
        print(f"Written: {out}")
    else:
        print(res["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
