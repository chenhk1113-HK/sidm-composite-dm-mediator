#!/usr/bin/env python3
"""
r5_local_review.py -- Round 5 Reviewer 1 via the LOCAL llama.cpp server.

WHY
---
OpenRouter's free tier is account-blocked for this host today (HTTP 429
"free-models-per-day" on every free model, including the delegated
Nemotron 3 Ultra 550B). The fallback chain in config.yaml points at a
LOCAL llamacpp endpoint serving Qwen3.6-35B-A3B-UD-Q4_K_M. This script
calls that local server directly so the dual-review loop still has TWO
independent reviewers today instead of collapsing to one.

This is a different model FAMILY from the OpenCode-side reviewer
(DeepSeek/GLM/MiMo), so the two opinions remain independent in the sense
the loop needs: they fail differently.

TWO THINGS THAT MATTER FOR THIS SCRIPT
-------------------------------------
1. The excerpt is INLINED into the prompt. The local server is a bare
   OpenAI-compatible endpoint with NO tool support, so a prompt that says
   "read docs/R5_EXCERPT.md with the read tool" yields a model that
   answers from imagination (it burned 3000 tokens on reasoning and
   emitted nothing). Inline the content instead.
2. `chat_template_kwargs: {"enable_thinking": False}`. This model is a
   hybrid reasoning model; with thinking on, the entire token budget is
   consumed by the reasoning trace and `content` comes back EMPTY
   (observed: finish_reason=length, content=""). With thinking off it
   answers in ~2 s.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")

# The port lives in local_model.py -- read it from there rather than repeating
# the number, so the two can never drift apart again. It was 50113 until
# 2026-10-25, when that turned out to be inside the Windows-reserved TCP range
# 50060-50159 (bind fails with WinError 10013; `netstat` shows nothing
# listening, which is what made it look like a free port).
_spec = importlib.util.spec_from_file_location(
    "local_model", PROJECT / "scripts" / "local_model.py")
_local = importlib.util.module_from_spec(_spec)
sys.modules["local_model"] = _local
_spec.loader.exec_module(_local)

FAST_PORT = _local.FAST["port"]
FAST_MODEL = _local.FAST["model"]
FAST_ENDPOINT = f"http://127.0.0.1:{FAST_PORT}/v1/chat/completions"

# Strata (the deep 125B reviewer) is the PRIMARY reviewer as of 2026-10-25.
# The 35B is the STANDBY: it is only loaded when Strata has failed. That is not
# a policy we enforce here -- it is what the Hermes fallback chain already
# does. The chain order is
#     openrouter -> nvidia -> strata -> llamacpp(35B)
# so the 35B is only reached when every earlier slot, including Strata, has
# failed. The 35B itself is served by the Hermes-managed llama.cpp runtime
# (:18434), whose router has models_autoload=true: the weights are loaded on
# the first request that names the model and the supervisor idle-unloads them
# again after IDLE_UNLOAD_S (960 s), so "loaded only when Strata failed" is
# also true of the RESIDENCY, not just of the routing.
DEEP_PORT = _local.DEEP["port"]
DEEP_MODEL = _local.DEEP["model"]
DEEP_ENDPOINT = f"http://127.0.0.1:{DEEP_PORT}/v1/chat/completions"

# The Hermes-managed llama.cpp runtime: base_url + api_key live in its state
# file. Preferred over the project's own :11437 server for the standby path
# because it is ONE copy of the 22.6 GB GGUF, it autoloads on demand and it
# self-releases the RAM when idle -- so the standby costs nothing while
# Strata is healthy.
_RUNTIME_STATE = Path(
    r"C:\Users\lamkuenai\AppData\Local\hermes\runtimes\llamacpp\server.json")


def managed_llamacpp() -> tuple[str, str] | None:
    """(base_url, api_key) of the Hermes-managed 35B runtime, or None."""
    try:
        st = json.loads(_RUNTIME_STATE.read_text(encoding="utf-8"))
    except Exception:
        return None
    base = str(st.get("base_url") or "").strip()
    key = str(st.get("api_key") or "").strip()
    if not base:
        return None
    return base.rstrip("/"), key or "no-key-required"


OUT = PROJECT / "docs" / "LOCAL_REVIEW_R5.md"
EXCERPT = PROJECT / "docs" / "R5_EXCERPT.md"

PROMPT = """You are Reviewer 1 for the SIDM composite dark matter paper (velocity-dependent self-interacting dark matter).

Below is an EXCERPT of the paper containing the exact numbered line ranges under review. Line numbers shown (e.g. "11|") are the paper's own line numbers.

Return findings ONLY, using exactly these tags:
[ERR] = definite error
[Q]   = question or unverifiable claim
[OK]  = checked and found correct

Cite the line number for every number you quote. If you compute anything, show the formula and the numbers. If you are unsure, say so with [Q] rather than asserting. Keep the whole review UNDER 700 WORDS.

CONTEXT: Round 5 is a final verification pass. Rounds 1-4 fixed 17 defects. Confirm each fix landed and find anything still broken.

VERIFY (answer each briefly):

F1 (L11) Abstract distinguishes microphysical sigma/m from sigma_eff = f_H^2 * sigma/m, states sigma_eff(15) = 0.251 is BELOW the 0.8 ceiling, and the "3.6-23.7x" excess is in sigma/m not sigma_eff. Coherent?

F2 (L36, L2205-2210) Horigome ceilings: 0.2 cm^2/g is the "decisive CDM-preference threshold" AND the w=10 km/s velocity-dependent limit; the velocity-independent w->infinity upper limit is 0.04. Labels correct? Are the 27-49x and 830x numbers right against 0.2?

F3 (L117) Gaussian tail at v=15: exp[-(15-29.4)^2/(2*3.0^2)]. COMPUTE this number. The paper should quote ~1.0e-5. Is it right?

F4 (L143-145) The hierarchy bound under sigma_1 = 1.0 is LOOSER than the sigma_1 = 4.4 headline. Does the paper say LOOSER/LESS restrictive? Check: v=28 bound 2.84e-13 vs headline 1.74e-13 -- is 2.84e-13 looser than 1.74e-13?

F5 (L57) Breit-Wigner normalization must have a unit peak (value 1 at v = v_t). Is it stated that way, with a note that the code uses the energy-space unit-peak form?

F6 (L82) s-channel resonance must be v_res = c*sqrt(8*DeltaM/(2*m_chi)), NOT v_res = (m_med/m_chi)*c. COMPUTE c*sqrt(8*1.2e-9) in km/s. Does it give 29.4?

F7 (L82) The "four mediators" claim must be gone; v2-v4 must be described as bookkeeping nodes not physical resonances (see L896-898). Is it?

F8 (L189-190) Both sigma_peak causality caps must read 47.67. COMPUTE: if ratio = K/sigma_peak and ratio(50) = 2.86, what is the cap where ratio = 3.0? Is 47.67 right?

F9 (L1012) The "7 of 8" must be framed as a RETRACTED v1.12/v1.13 placeholder claim, NOT a current finding, and must not contradict the adjacent statement that SPARC cannot be matched. Is it?

F10 (L1602-1604, L2264) Channel counts: 4 PASS / 3 MARGINAL / 1 FAIL over 8 constrained channels. Verify the named lists: PASS = Cluster v=500, dSph v=10, Cloud-9 v=28, SPARC v=100; MARGINAL = UFD v=3, v=5, v=15; FAIL = dSph v=7. Sum to 8? Consistent everywhere in the excerpt?

F11 (L189-190, L204) The viable sigma_peak window at c=12 is stated EMPTY because floor 51.96 > cap 47.67. Verify floor: 50*50/48.14 = ? and cap 143/3 = ? Is the EMPTY conclusion right?

FIND ANYTHING ELSE in the excerpt that is internally inconsistent or wrong. Report as [ERR] or [Q].
"""


def _post(url: str, payload: dict, timeout: int, api_key: str | None = None):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _try_endpoint(label: str, url: str, model: str, payload: dict,
                  timeout: int, api_key: str | None = None,
                  deep: bool = False) -> dict | None:
    """One review attempt. Returns the parsed body, or None if the endpoint
    could not answer (connection refused, or the model not loaded)."""
    body = dict(payload)
    body["model"] = model
    if deep:
        # Strata reasons first and can spend the whole token budget thinking.
        # A small budget keeps the answer from being eaten by the thinking.
        body["reasoning_budget_tokens"] = 256
        # Strata writes a MUCH fuller review than the 35B (it checks F1-F11 and
        # then adds its own findings), so it hits the 2000-token cap that was
        # sized for the 35B and gets cut off mid-sentence. Give it room.
        body["max_tokens"] = 4000
    else:
        body["chat_template_kwargs"] = {"enable_thinking": False}
    t0 = time.time()
    try:
        data = _post(url, body, timeout, api_key)
    except Exception as exc:  # noqa: BLE001
        print(f"  {label}: FAILED ({type(exc).__name__}: {str(exc)[:110]})")
        return None
    text = (data.get("choices", [{}])[0].get("message", {}) or {}).get("content") or ""
    if not text:
        print(f"  {label}: empty answer (finish="
              f"{data.get('choices',[{}])[0].get('finish_reason')!r})")
        return None
    print(f"  {label}: OK {time.time() - t0:.1f}s")
    return data


def main() -> int:
    excerpt = EXCERPT.read_text(encoding="utf-8")
    prompt = PROMPT + "\n=== PAPER EXCERPT BEGINS ===\n" + excerpt + "\n=== PAPER EXCERPT ENDS ==="

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.2,
    }

    # PRIMARY: Strata (the deep 125B reviewer). STANDBY: the 35B, tried only
    # if Strata could not answer. The standby is the Hermes-managed runtime
    # (autoloads the weights on demand, idle-unloads them after 960 s) so it
    # costs no RAM while Strata is healthy; the project's own :11437 server is
    # the last resort for it.
    attempts = [("strata (deep, :%d)" % DEEP_PORT, DEEP_ENDPOINT, DEEP_MODEL,
                 1800, None, True)]
    managed = managed_llamacpp()
    if managed:
        attempts.append(("llamacpp standby (managed :%s)" % managed[0].rsplit(":", 1)[-1],
                         managed[0] + "/chat/completions", FAST_MODEL, 900,
                         managed[1], False))
    attempts.append(("llamacpp standby (:%d)" % FAST_PORT, FAST_ENDPOINT,
                     FAST_MODEL, 900, None, False))

    data = None
    used = ""
    elapsed = 0.0
    for label, url, model, timeout, key, deep in attempts:
        t0 = time.time()
        data = _try_endpoint(label, url, model, payload, timeout, key, deep)
        if data is not None:
            used = label
            elapsed = time.time() - t0
            break
        data = None
    if data is None:
        print("FAILED: no local reviewer answered (Strata and the 35B standby "
              "both unreachable)", file=sys.stderr)
        return 2

    out_lines = [
        "# Local Review (Reviewer 1, Round 5)",
        "",
        f"**Model:** `{DEEP_MODEL if used.startswith('strata') else FAST_MODEL}` "
        f"({used})  ",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
        "**Transport:** direct local OpenAI-compatible `/v1/chat/completions`  ",
        "**Why local:** OpenRouter free tier is account-blocked for this host today "
        "(HTTP 429 `free-models-per-day` on every free model, including the delegated "
        "Nemotron 3 Ultra 550B).  ",
        "**Reviewer role:** second independent reviewer, different model family from the "
        "OpenCode-side reviewer (DeepSeek/GLM/MiMo).  ",
        f"**Excerpt source:** `{EXCERPT.name}` ({len(excerpt)} chars, inlined — the local "
        "endpoint has no tool support).  ",
        "",
        "> **Status: UNVERIFIED SECOND OPINION.** Every specific numerical claim below must "
        "be recomputed in Python before it is acted on.",
        "",
        "## Review",
        "",
    ]

    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    out_lines.append(text)
    out_lines += [
        "",
        "---",
        f"**Duration:** {elapsed:.1f}s  ",
        f"**Usage:** {usage}",
        "",
    ]
    OUT.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Local review written to {OUT}")
    print(f"Tokens: {usage}")
    print()
    print(text[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())