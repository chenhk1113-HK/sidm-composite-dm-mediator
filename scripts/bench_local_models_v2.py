"""Local model head-to-head benchmark v2 — CORRECTED.

v1 had three defects that made its scores untrustworthy. This version fixes
all three:

  DEFECT 1 (scorer): the wrong-answer list for Q-direction contained the
    literal "more restrictive", which also matches inside the CORRECT
    answer "not more restrictive" / "is LESS restrictive". Naive substring
    matching scored a correct answer as confidently wrong.
    FIX: strip negated forms before checking the wrong list.

  DEFECT 2 (truncation): v1 saved only the first 220 chars of each answer
    and re-scored from that preview, so any correct number appearing
    later in the answer was invisible.
    FIX: save the FULL answer text and score from that.

  DEFECT 3 (unanswerable questions): Q-dupe, Q-section-order and Q-table
    were asked against R5_EXCERPT.md, which does not contain the §2.6a
    block, the §9.13/§10 boundary, or the §10.3 table. Both models
    GUESSED; scoring the guesses was meaningless.
    FIX: each question group is asked against the excerpt that actually
    contains its evidence (R5_EXCERPT.md for the numeric questions,
    R5_STRUCTURAL_EXCERPT.md for the structural ones).

GROUND TRUTH: every answer was independently recomputed by the controller
against the post-fix paper (commit ae4b763) before this script was run.
See the docstring of v1 for the derivation of each.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
NUM_EXCERPT = PROJECT / "docs" / "R5_EXCERPT.md"
STR_EXCERPT = PROJECT / "docs" / "R5_STRUCTURAL_EXCERPT.md"

# id, question, expected[], wrong[], group
QUESTIONS = [
    ("Q-floor",
     "The paper's sigma_peak viability window at c=12 has a FLOOR requiring "
     "sigma_peak >= 51.96 cm^2/g. The floor comes from requiring sigma/m(28) >= 50. "
     "The paper quotes sigma/m(28) = 48.14 at sigma_peak = 50. Compute the floor: "
     "50 * 50 / 48.14 = ? Is the paper's 51.96 correct? Show your arithmetic. "
     "(The quoted 48.14 already includes BOTH the Gaussian resonance term and the "
     "power-law background sigma_0*(100/v)^a_slope with sigma_0=0.052, a_slope=1.93.)",
     ["51.93", "51.9", "51.96", "52.0", "51.95", "51.9319"], [], "num"),
    ("Q-cap",
     "The paper's sigma_peak causality CAP at c=12 requires sigma_peak <= 47.67. "
     "It comes from interpolating ratio = K/sigma_peak, given ratio = 2.86 at "
     "sigma_peak = 50, with the cap at ratio = 3.0. Compute K and then the cap. "
     "Is 47.67 correct? Show your arithmetic.",
     ["47.67", "47.666", "47.7", "47.6667"], ["47.65", "47.71"], "num"),
    ("Q-empty",
     "Using the floor (51.96) and cap (47.67) from the sigma_peak window at c=12, "
     "is the viable sigma_peak window EMPTY? And what does that imply for the "
     "canonical sigma_peak = 174 cm^2/g? By what factor does 174 exceed the floor?",
     ["empty", "no viable", "disjoint", "3.35", "3.3", "3.4"], [], "num"),
    ("Q-gauss",
     "The paper states that at sigma_1 = 3.0 km/s the Gaussian resonance tail at "
     "v = 15 km/s is exp[-(15-29.4)^2/(2*3.0^2)] = 1.0e-5. Compute this value. "
     "Is the paper's 1.0e-5 correct? Show your arithmetic.",
     ["9.9e-6", "9.93e-6", "1.0e-5", "1e-05", "9.93", "1.0e-05", "9.9"],
     ["8e-5", "8.0e-5", "2.5e-9"], "num"),
    ("Q-schannel",
     "The paper's s-channel resonance condition is "
     "v_res = c*sqrt(8*DeltaM/(2*m_chi)) with DeltaM/(2*m_chi) = 1.2e-9. "
     "Compute v_res in km/s using c = 299792.458 km/s. Does it give 29.4 km/s? "
     "Show your arithmetic.",
     ["29.4", "29.37", "29.38", "29.373", "29.37"], [], "num"),
    ("Q-direction",
     "The paper's hierarchy constraint under sigma_1 = 1.0 (D-5) gives "
     "g_N/g_chi < 2.84e-13 at v=28, while the sigma_1 = 4.4 headline gives "
     "g_N/g_chi < 1.74e-13. Is the D-5 bound MORE restrictive or LESS restrictive "
     "than the headline? Explain numerically.",
     ["less restrictive", "looser", "weaker"], ["stricter", "tighter"], "num"),
    ("Q-thresholds",
     "The paper uses THREE different Horigome+ 2025 limits: 0.8 cm^2/g "
     "(w=10 km/s velocity-dependent), 0.2 cm^2/g (decisive CDM-preference "
     "threshold), and 0.04 cm^2/g (velocity-independent w->infinity). "
     "For sigma/m(15) = 2.85 cm^2/g, what is the factor against EACH of the "
     "three? List all three factors.",
     ["3.56", "14.25", "71.25", "3.6", "14.2"], [], "num"),
    ("Q-abstract",
     "In the abstract, the framework score states a channel count. The paper's "
     "A.15 Block 2 gives a DIFFERENT count for the SAME canonical parameters at "
     "the promoted published-sigma_unc likelihood. What are the two counts?",
     ["4 PASS", "1 PASS", "7 FAIL", "5 of 8", "5/8"], [], "num"),
    ("Q-fH",
     "The paper's canonical f_H value: constants.py fixes f_H = 0.297, but some "
     "text says f_H = 0.30. What is the drift in sigma_eff = f_H^2 * sigma/m "
     "between them? Compute both squares and the ratio.",
     ["0.0882", "0.088209", "2%", "2.0", "1.02", "0.09"], [], "num"),
    ("Q-dupe",
     "Does the section 2.6a content appear ONCE or TWICE in the excerpt? "
     "Count the occurrences of the 'First-class result (R88(26))' marker and of "
     "the 'Continuous viable sigma_peak window' table row.",
     ["once", "1 occurrence", "only once", "not duplicated", "single"],
     ["twice", "duplicated", "two occurrences", "two times"], "str"),
    ("Q-section-order",
     "In the PHYSICAL excerpt, does section 9.13 sit BEFORE or AFTER the "
     "'## 10.' heading? Is §9.13-§9.18 nested inside §10, or does it come "
     "before §10? Quote the line numbers you see.",
     ["before", "not inside", "outside", "prior to", "precedes", "1206", "1685"],
     ["nested inside", "inside §10", "within §10"], "str"),
    ("Q-table",
     "In section 10.3 the 'Best configuration found' table: how many value "
     "columns do the DATA ROWS have (e.g. the g_h_SM row)? And how many columns "
     "does the HEADER ROW declare? Do they match? Quote both.",
     ["5 and 4", "5 vs 4", "five", "mismatch", "do not match", "do not",
      "5 columns", "4 columns", "four"],
     [], "str"),
]

NEG_FORMS = [
    "not more restrictive", "no more restrictive", "rather than more restrictive",
    "is less restrictive", "less restrictive than", "not stricter",
    "not tighter", "does not match", "do not match", "don't match",
    "not duplicated", "not nested inside", "is not inside",
]


def ask(port: int, model: str, prompt: str, max_tokens: int = 800) -> dict:
    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0.1,
            "chat_template_kwargs": {"enable_thinking": False}}
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1200) as r:
        d = json.loads(r.read())
    return {"text": d["choices"][0]["message"].get("content") or "",
            "elapsed": time.time() - t0,
            "ct": d.get("usage", {}).get("completion_tokens", 0),
            "pt": d.get("usage", {}).get("prompt_tokens", 0),
            "finish": d["choices"][0].get("finish_reason")}


def score(ans: str, expected: list[str], wrong: list[str]) -> tuple[int, str]:
    """Negative-context aware scoring over the FULL answer text."""
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
                        "full_text": r["text"]})
        print(f"  [{s:+d}] {qid:16s} {why:18s} {r['elapsed']:6.1f}s  {r['ct']:5d}tok")
    n = len(QUESTIONS)
    net = sum(x["score"] for x in results)
    print(f"\n  {label}")
    print(f"    {net:+d} / {n}   correct {sum(1 for x in results if x['score']==1)}, "
          f"wrong {sum(1 for x in results if x['score']==-1)}, "
          f"no-answer {sum(1 for x in results if x['score']==0)}")
    print(f"    time {tt:.1f}s   {tc} completion tokens   "
          f"{tc/tt:.2f} tok/s generation-only")
    return {"label": label, "model": model, "port": port, "net": net, "n": n,
            "correct": sum(1 for x in results if x["score"] == 1),
            "wrong": sum(1 for x in results if x["score"] == -1),
            "no_answer": sum(1 for x in results if x["score"] == 0),
            "total_time": round(tt, 1), "total_ct": tc,
            "tps": round(tc / tt, 2), "results": results}


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
                   "A. CURRENT  Qwen3.6-35B-A3B-UD-Q4_K_M (MoE 35B/3B-active, Q4_K_M)"))
    print()
    out.append(run(50114, "Qwen3.8-27B-GSQ-RCO-IQ2_S",
                   "B. NEW      Qwen3.8-27B-GSQ-RCO-IQ2_S (dense 27B, 2.75 bpw)"))
    print()
    out.append(run(50115, "Qwen3.8-27B-GSQ-RCO-IQ3_XXS",
                   "C. NEW      Qwen3.8-27B-GSQ-RCO-IQ3_XXS (dense 27B, 3.00 bpw)"))
    op = PROJECT / "v0.3-prelim/data/results/local_model_headtohead_v2.json"
    op.parent.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n" + "=" * 78)
    print("SUMMARY (v2, corrected scoring)")
    print("=" * 78)
    for o in out:
        print(f"  {o['label']:56s} {o['net']:+3d}/{o['n']}  {o['tps']:6.2f} tok/s"
              f"  {o['total_time']:8.1f}s")
    print(f"\n  saved -> {op}")