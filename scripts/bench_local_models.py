"""Local model head-to-head benchmark — SCORED against known ground truth.

The ground truth comes from the 5-round dual-review work actually performed
on v0.3-prelim/docs/PAPER_V1_DRAFT.md. Every question below has a
verified answer, and the source lines were re-checked against the
post-fix paper (commit ae4b763) so the benchmark reflects current state.

Scoring:
  +1  correct answer (numerically right AND direction right)
   0  wrong / no answer / hedged
  -1  confidently WRONG (e.g. the floor-calculation false positive)

This is deliberately the SAME kind of task the model is being asked to do
in production: read a paper excerpt, do arithmetic, report a finding.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
EXCERPT = PROJECT / "docs" / "R5_EXCERPT.md"

# (id, question, expected-substring-list, wrong-substring-list)
# A response scores +1 if it contains ANY expected substring and NO wrong one.
QUESTIONS = [
    (
        "Q-floor",
        "In the paper, the sigma_peak viability window at c=12 has a FLOOR that "
        "requires sigma_peak >= 51.96 cm^2/g. That floor comes from requiring "
        "sigma/m(28) >= 50. The paper quotes sigma/m(28) = 48.14 at sigma_peak = 50. "
        "Compute the floor: 50 * 50 / 48.14 = ? Is the paper's 51.96 correct? "
        "Show your arithmetic. (IMPORTANT: the paper's sigma/m(v) is the sum of a "
        "Gaussian resonance term AND a power-law background term "
        "sigma_0*(100/v)^a_slope with sigma_0=0.052, a_slope=1.93; the quoted "
        "48.14 already includes both.)",
        ["51.93", "51.9", "51.96", "52.0", "51.95"],
        ["52.42", "52.6", "52.5961"],
    ),
    (
        "Q-cap",
        "The paper's sigma_peak causality CAP at c=12 requires sigma_peak <= 47.67. "
        "It comes from interpolating ratio = K/sigma_peak, given ratio = 2.86 at "
        "sigma_peak = 50, with the cap at ratio = 3.0. Compute K and then the cap. "
        "Is 47.67 correct? Show your arithmetic.",
        ["47.67", "47.666", "47.7"],
        ["47.65", "47.71"],
    ),
    (
        "Q-empty",
        "Using the floor (51.96) and cap (47.67) from the sigma_peak window at c=12, "
        "is the viable sigma_peak window EMPTY? And what does that imply for the "
        "canonical sigma_peak = 174 cm^2/g? By what factor does 174 exceed the floor?",
        ["empty", "EMPTY", "no viable", "disjoint", "not empty", "3.3", "3.4", "3.35"],
        [],
    ),
    (
        "Q-gauss",
        "The paper states that at sigma_1 = 3.0 km/s, the Gaussian resonance tail at "
        "v = 15 km/s is exp[-(15-29.4)^2/(2*3.0^2)] = 1.0e-5. Compute this value. "
        "Is the paper's 1.0e-5 correct? Show your arithmetic.",
        ["9.9e-6", "9.93e-6", "1.0e-5", "1e-05", "9.9", "1.0e-05"],
        ["8e-5", "8.0e-5", "2.5e-9", "2.5e-09"],
    ),
    (
        "Q-schannel",
        "The paper's s-channel resonance condition at L82 is "
        "v_res = c*sqrt(8*DeltaM/(2*m_chi)) with DeltaM/(2*m_chi) = 1.2e-9. "
        "Compute v_res in km/s using c = 299792.458 km/s. Does it give 29.4 km/s? "
        "Show your arithmetic.",
        ["29.4", "29.37", "29.38", "29.373"],
        [],
    ),
    (
        "Q-direction",
        "The paper's hierarchy constraint under sigma_1 = 1.0 (D-5) gives "
        "g_N/g_chi < 2.84e-13 at v=28, while the sigma_1 = 4.4 headline gives "
        "g_N/g_chi < 1.74e-13. Is the D-5 bound MORE restrictive or LESS restrictive "
        "than the headline? Explain numerically.",
        ["less restrictive", "looser", "weaker", "not more restrictive"],
        ["more restrictive", "stricter", "tighter"],
    ),
    (
        "Q-thresholds",
        "The paper uses THREE different Horigome+ 2025 limits: 0.8 cm^2/g "
        "(w=10 km/s velocity-dependent), 0.2 cm^2/g (decisive CDM-preference "
        "threshold), and 0.04 cm^2/g (velocity-independent w->infinity). "
        "For sigma/m(15) = 2.85 cm^2/g, what is the factor against EACH of the "
        "three? List all three factors.",
        ["3.56", "3.6", "14.25", "14.2", "71", "71.25", "3.56x"],
        [],
    ),
    (
        "Q-dupe",
        "Look at the paper excerpt for section 2.6a (the sigma_peak viability at "
        "LambdaCDM-standard concentration). Does the section 2.6a content appear "
        "ONCE or TWICE in the document? Look for the 'First-class result (R88(26))' "
        "marker and the 'Continuous viable sigma_peak window' table row. "
        "Count the occurrences.",
        ["once", "1 occurrence", "appears once", "only once", "not duplicated"],
        ["twice", "2 occurrences", "appears twice", "duplicated", "two times"],
    ),
    (
        "Q-abstract",
        "In the abstract, the framework score states a channel count. The paper's "
        "A.15 Block 2 gives a DIFFERENT count for the SAME canonical parameters at "
        "the promoted published-sigma_unc likelihood. What are the two counts?",
        ["4 PASS", "1 PASS", "7 FAIL", "4/8", "1/8", "5 of 8", "5/8"],
        [],
    ),
    (
        "Q-fH",
        "The paper's canonical f_H value: constants.py fixes f_H = 0.297, but some "
        "text says f_H = 0.30. What is the drift in sigma_eff = f_H^2 * sigma/m "
        "between them? Compute both squares and the ratio.",
        ["0.0882", "0.09", "2%", "2.04", "1.02", "0.088209"],
        [],
    ),
    (
        "Q-table",
        "In section 10.3 the 'Best configuration found' table: how many value "
        "columns do the DATA ROWS have (e.g. the g_h_SM row)? And how many columns "
        "does the HEADER ROW declare? Do they match?",
        ["5 and 4", "5 vs 4", "five and four", "mismatch", "do not match",
         "five columns", "4 header"],
        [],
    ),
    (
        "Q-section-order",
        "The paper's announced section order is §1 -> §2 -> §9 -> §10 -> §11. "
        "In the PHYSICAL document, where does section 9.13 sit relative to the "
        "'## 10.' heading? Is §9.13-§9.18 nested inside §10, or does it come "
        "before §10?",
        ["before", "not inside", "outside", "prior to", "correctly placed",
         "§9.13 comes before"],
        ["inside §10", "nested inside", "within §10"],
    ),
]


def ask(port: int, model: str, prompt: str, max_tokens: int = 700) -> dict:
    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    t0 = time.time()
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=900) as r:
        d = json.loads(r.read())
    el = time.time() - t0
    u = d.get("usage", {})
    return {
        "text": d["choices"][0]["message"].get("content") or "",
        "elapsed": el,
        "ct": u.get("completion_tokens", 0),
        "pt": u.get("prompt_tokens", 0),
        "finish": d["choices"][0].get("finish_reason"),
    }


def score(ans: str, expected: list[str], wrong: list[str]) -> tuple[int, str]:
    low = ans.lower()
    if any(w.lower() in low for w in wrong):
        return -1, "confidently wrong"
    if any(e.lower() in low for e in expected):
        return 1, "correct"
    return 0, "wrong/no-answer"


def run(port: int, model: str, label: str) -> dict:
    excerpt = EXCERPT.read_text(encoding="utf-8")
    results = []
    total_time = 0.0
    total_ct = 0
    for qid, q, exp, wrong in QUESTIONS:
        prompt = (
            "You are auditing a physics paper. Read the excerpt, then answer the "
            "question with the arithmetic shown.\n\n"
            "=== PAPER EXCERPT ===\n" + excerpt + "\n=== END EXCERPT ===\n\n"
            "QUESTION: " + q
        )
        r = ask(port, model, prompt)
        s, why = score(r["text"], exp, wrong)
        total_time += r["elapsed"]
        total_ct += r["ct"]
        results.append({
            "id": qid, "score": s, "why": why,
            "elapsed": round(r["elapsed"], 1), "ct": r["ct"],
            "head": r["text"][:220].replace("\n", " "),
        })
        print(f"  [{s:+d}] {qid:16s} {why:18s} {r['elapsed']:6.1f}s  {r['text'][:90]!r}")
    n = len(QUESTIONS)
    net = sum(x["score"] for x in results)
    correct = sum(1 for x in results if x["score"] == 1)
    wrong = sum(1 for x in results if x["score"] == -1)
    print(f"\n  {label}")
    print(f"    score: {net:+d} / {n}   (correct {correct}, wrong {wrong}, "
          f"no-answer {n-correct-wrong})")
    print(f"    total time {total_time:.1f}s   total completion tokens {total_ct}")
    print(f"    throughput {total_ct/total_time:.2f} tok/s (generation only)")
    return {
        "label": label, "model": model, "port": port,
        "net": net, "n": n, "correct": correct, "wrong": wrong,
        "total_time": round(total_time, 1), "total_ct": total_ct,
        "tps": round(total_ct / total_time, 2),
        "results": results,
    }


if __name__ == "__main__":
    out = []
    # Ports come from local_model.py: 50113/50114 are inside the Windows-reserved
    # TCP range 50060-50159 and can never be bound (WinError 10013).
    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        "local_model", PROJECT / "scripts" / "local_model.py")
    _local = importlib.util.module_from_spec(_spec)
    sys.modules["local_model"] = _local
    _spec.loader.exec_module(_local)
    out.append(run(_local.FAST["port"], _local.FAST["model"],
                   "A. CURRENT Qwen3.6-35B-A3B (MoE, Q4_K_M)"))
    print()
    out.append(run(50114, "Qwen3.8-27B-GSQ-RCO-IQ2_S",
                   "B. NEW Qwen3.8-27B-GSQ-RCO-IQ2_S"))
    dst = PROJECT / "docs" / "R5_EXCERPT.md"
    outpath = PROJECT / "v0.3-prelim" / "data" / "results" / "local_model_headtohead.json"
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    for o in out:
        print(f"  {o['label']:52s} {o['net']:+3d}/{o['n']}  "
              f"{o['tps']:6.2f} tok/s  {o['total_time']:7.1f}s")
    print(f"\n  saved -> {outpath}")