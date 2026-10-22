"""Scored A/B: Strata / Qwen3.8-Flash-Next IQ3_XXS vs the incumbent local model.

Same 12 questions, same ground truth, same scoring as
scripts/bench_local_models_v2.py -- the numbers are directly comparable to
the incumbent's +11/12 result.

Only the transport differs: Strata serves an OpenAI-compatible API on
http://127.0.0.1:8080/v1, the incumbent on http://127.0.0.1:50113/v1.

The questions are imported from the v2 script so the two benchmarks can
never drift apart. Each answer is scored with the same negation-aware,
stance-based matcher.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
sys.path.insert(0, str(PROJECT / "scripts"))

# reuse the exact question set + ground truth from the v2 benchmark
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bench_v2", PROJECT / "scripts" / "bench_local_models_v2.py")
v2 = importlib.util.module_from_spec(spec)
sys.modules["bench_v2"] = v2
spec.loader.exec_module(v2)
QUESTIONS = v2.QUESTIONS
NUM_EXCERPT = v2.NUM_EXCERPT
STR_EXCERPT = v2.STR_EXCERPT

NEG_FORMS = v2.NEG_FORMS


def score(ans: str, expected: list[str], wrong: list[str]) -> tuple[int, str]:
    """Negation-aware, stance-based. Identical to the v2 benchmark."""
    low = ans.lower()
    cleaned = low
    for neg in NEG_FORMS:
        cleaned = cleaned.replace(neg, "<<neg>>")
    for w in wrong:
        if w.lower() in cleaned:
            return -1, "confidently wrong"
    if any(e.lower() in low for e in expected):
        return 1, "correct"
    return 0, "no-answer"


def ask(port: int, model: str, prompt: str, max_tokens: int = 1400) -> dict:
    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    body = {"model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "reasoning_budget_tokens": 700}
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        d = json.loads(r.read())
    el = time.time() - t0
    u = d.get("usage", {})
    msg = d["choices"][0]["message"]
    # Strata splits thinking out; the answer is in content
    txt = (msg.get("content") or "")
    if not txt and msg.get("reasoning_content"):
        txt = msg["reasoning_content"]
    return {"text": txt, "elapsed": el,
            "ct": u.get("completion_tokens", 0),
            "pt": u.get("prompt_tokens", 0),
            "finish": d["choices"][0].get("finish_reason")}


def run(port: int, model: str, label: str) -> dict:
    num = NUM_EXCERPT.read_text(encoding="utf-8")
    st = STR_EXCERPT.read_text(encoding="utf-8")
    results = []
    tt = 0.0
    tc = 0
    for qid, q, exp, wrong, group in QUESTIONS:
        excerpt = num if group == "num" else st
        prompt = ("You are auditing a physics paper. Read the excerpt, then answer "
                  "the question with the arithmetic shown.\n\n=== PAPER EXCERPT ===\n"
                  + excerpt + "\n=== END EXCERPT ===\n\nQUESTION: " + q)
        r = ask(port, model, prompt)
        s, why = score(r["text"], exp, wrong)
        tt += r["elapsed"]
        tc += r["ct"]
        results.append({"id": qid, "group": group, "score": s, "why": why,
                        "elapsed": round(r["elapsed"], 1), "ct": r["ct"],
                        "pt": r["pt"], "finish": r["finish"],
                        "full_text": r["text"]})
        print(f"  [{s:+d}] {qid:16s} {why:18s} {r['elapsed']:7.1f}s  {r['ct']:5d}tok",
              flush=True)
    n = len(QUESTIONS)
    net = sum(x["score"] for x in results)
    print(f"\n  {label}")
    print(f"    {net:+d} / {n}   correct {sum(1 for x in results if x['score']==1)}, "
          f"wrong {sum(1 for x in results if x['score']==-1)}, "
          f"no-answer {sum(1 for x in results if x['score']==0)}")
    print(f"    time {tt:.1f}s   {tc} completion tokens")
    return {"label": label, "model": model, "port": port, "net": net, "n": n,
            "correct": sum(1 for x in results if x["score"] == 1),
            "wrong": sum(1 for x in results if x["score"] == -1),
            "no_answer": sum(1 for x in results if x["score"] == 0),
            "total_time": round(tt, 1), "total_ct": tc, "results": results}


if __name__ == "__main__":
    out = run(8080, "qwen3.8-flash-next-iq3_xxs",
              "STRATA  Qwen3.8-Flash-Next IQ3_XXS (125B-A6B)")
    op = PROJECT / "v0.3-prelim" / "data" / "results" / "strata_scored_ab.json"
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n  saved -> {op}")
    print("\n  INCUMBENT (Qwen3.6-35B-A3B-UD-Q4_K_M, llama.cpp) scored +11/12 "
          "at 18.03 tok/s generation-only in the v2 benchmark.")
