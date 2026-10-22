#!/usr/bin/env python3
"""local_model.py -- switch the local model between the fast incumbent and
the deep Strata reviewer.

WHY A SWAP AND NOT TWO SERVERS
-------------------------------
This host has 96 GB of RAM with a 32 GB UMA carve-out, so the OS sees
63.62 GiB. The two local models cannot coexist:

    incumbent  Qwen3.6-35B-A3B-UD-Q4_K_M   22.6 GB   18.03 tok/s   (llama.cpp :50113)
    deep       Qwen3.8-Flash-Next IQ3_XXS    75.8 GB   12.7-16.2 tok/s (Strata :8080)

Strata's own engine warns that its commit limit has ~2.5 GiB of headroom, so
starting it while the incumbent holds 22.6 GB is a guaranteed failure. The
swap is therefore the only correct design: one at a time, on a shared port.

USAGE
-----
    python local_model.py status              # what is running, and the port
    python local_model.py use fast            # incumbent (Qwen3.6-35B-A3B) on :50113
    python local_model.py use deep            # Strata (Flash-Next) on :8080
    python local_model.py use deep --wait 600 # wait up to 600 s for it to be ready
    python local_model.py stop                # stop whatever is running

    python local_model.py ask "what is 2+2?"           # ask the running model
    python local_model.py ask --deep "..." --max-tokens 2000
    python local_model.py ask --deep --file prompt.md  # a prompt from a file

The `ask` helper exists because the deep model reasons before answering and
can burn the whole token budget on thinking with no answer. It sends
`reasoning_budget_tokens` so the answer is never eaten by the thinking, and
it prints the engine's own decode rate when the server exposes one.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERMES = Path(r"C:\Users\lamkuenai\AppData\Local\hermes")
STRATA = Path(r"C:\Users\lamkuenai\Strata")
STRATA_DATA = Path(r"C:\Users\lamkuenai\Strata-data")
PY = r"C:\Users\lamkuenai\AppData\Local\Python\pythoncore-3.14-64\python.exe"

FAST = {
    "name": "Qwen3.6-35B-A3B-UD-Q4_K_M",
    "port": 50113,
    "model": "Qwen3.6-35B-A3B-UD-Q4_K_M",
    "exe": HERMES / "tools" / "llamacpp-vulkan-11370-win32-x64" / "llama-server.exe",
    "gguf": HERMES / "models" / "Qwen3.6-35B-A3B-UD-Q4_K_M.gguf",
    "start": ["-m", "{gguf}", "--port", "{port}", "-ngl", "99",
              "-c", "32768", "-t", "16", "--cache-type-k", "q8_0",
              "--cache-type-v", "q8_0", "-fa", "on", "--host", "127.0.0.1"],
    "note": "35B total / 3B active. 18.03 tok/s. The fast reviewer.",
}
DEEP = {
    "name": "Qwen3.8-Flash-Next-IQ3_XXS (Strata)",
    "port": 8080,
    "model": "qwen3.8-flash-next-iq3_xxs",
    "note": "125B total / 6B active. 12.7-16.2 tok/s. The deep reviewer.",
}


def http_json(url: str, timeout: int = 15, data: dict | None = None):
    req = urllib.request.Request(
        url, data=json.dumps(data).encode() if data else None,
        headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def port_alive(port: int) -> bool:
    try:
        http_json(f"http://127.0.0.1:{port}/v1/models", timeout=6)
        return True
    except Exception:
        return False


def strata_health() -> dict | None:
    try:
        return http_json("http://127.0.0.1:8080/health", timeout=8)
    except Exception:
        return None


def pids_on_port(port: int) -> list[int]:
    out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
    pids = set()
    for line in out.splitlines():
        if f":{port} " in line and "LISTENING" in line:
            parts = line.split()
            if len(parts) >= 5 and parts[-1].isdigit():
                pids.add(int(parts[-1]))
    return sorted(pids)


def kill_port(port: int, label: str) -> bool:
    pids = pids_on_port(port)
    if not pids:
        return False
    print(f"  stopping {label} on :{port} (pid {', '.join(map(str, pids))}) ...")
    for pid in pids:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                       capture_output=True, text=True)
    time.sleep(2)
    return True


def start_fast() -> None:
    exe = FAST["exe"]
    gguf = FAST["gguf"]
    if not exe.exists():
        sys.exit(f"  missing: {exe}")
    if not gguf.exists():
        sys.exit(f"  missing: {gguf}")
    args = [a.format(gguf=str(gguf), port=FAST["port"]) for a in FAST["start"]]
    log = HERMES / "logs" / "local_fast_server.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    print(f"  starting {FAST['name']} on :{FAST['port']} ...")
    with open(log, "a", encoding="utf-8", errors="replace") as f:
        subprocess.Popen([str(exe)] + args, cwd=str(exe.parent), stdout=f,
                         stderr=subprocess.STDOUT, creationflags=0x08000000)
    for _ in range(120):
        if port_alive(FAST["port"]):
            print(f"  ready on :{FAST['port']}  (log: {log})")
            return
        time.sleep(1)
    print(f"  did not come up in 120 s -- check {log}")


def start_deep() -> None:
    engine = STRATA / "engine" / "strata.exe"
    cfg = STRATA / "strata-iq3_xxs.json"
    if not engine.exists():
        sys.exit(f"  missing: {engine}")
    log = STRATA / "strata-iq3_xxs.log"
    print(f"  starting {DEEP['name']} on :{DEEP['port']} (loading 24,576 experts, ~3.5 min) ...")
    env = dict(os.environ)
    env["PATH"] = str(STRATA / "engine" / "rocm" / "bin") + os.pathsep + env.get("PATH", "")
    with open(log, "a", encoding="utf-8", errors="replace") as f:
        subprocess.Popen([PY, str(STRATA / "serve" / "server.py"), "--engine", "strata",
                          "--config", str(cfg), "--port", str(DEEP["port"])],
                         cwd=str(STRATA), stdout=f, stderr=subprocess.STDOUT, env=env,
                         creationflags=0x08000000)
    print("  waiting for /health ...")
    for _ in range(240):
        h = strata_health()
        if h and h.get("loaded"):
            print(f"  ready on :{DEEP['port']}  (log: {log})")
            return
        time.sleep(2)
    print(f"  did not come up -- check {log}")


def use(which: str, wait: int, force: bool = False) -> None:
    if which == "fast":
        kill_port(DEEP["port"], DEEP["name"])
        if force:
            kill_port(FAST["port"], FAST["name"])
        if not port_alive(FAST["port"]):
            start_fast()
        else:
            print(f"  {FAST['name']} already running on :{FAST['port']}")
    else:
        kill_port(FAST["port"], FAST["name"])
        if force:
            kill_port(DEEP["port"], DEEP["name"])
        if not port_alive(DEEP["port"]):
            start_deep()
        else:
            print(f"  {DEEP['name']} already running on :{DEEP['port']}")


def status() -> None:
    print("=" * 70)
    print("LOCAL MODEL STATUS")
    print("=" * 70)
    for tag, m in (("FAST", FAST), ("DEEP", DEEP)):
        alive = port_alive(m["port"])
        mark = "RUNNING" if alive else "stopped"
        print(f"  {tag:4s} :{m['port']:<6d} {mark:8s}  {m['name']}")
        print(f"        {m['note']}")
    h = strata_health()
    if h:
        print(f"\n  Strata health: {json.dumps(h)}")
    print("\n  Only ONE can run at a time (RAM: 63.62 GiB visible to the OS).")
    print("  Use: local_model.py use fast | use deep")


def ask(args) -> None:
    which = "deep" if args.deep else ("fast" if args.fast else None)
    # for `ask`, the first free positional is the prompt (argparse fills
    # `which` with it); `which` only means fast/deep for the `use` action.
    prompt = args.prompt
    if prompt is None and args.which and args.which not in ("fast", "deep"):
        prompt = args.which
    if which is None and args.which in ("fast", "deep"):
        which = args.which
    if which:
        if which == "deep" and not port_alive(DEEP["port"]):
            print("  the deep model is not running -- starting it (this takes ~3.5 min) ...")
            use("deep", args.wait, args.force)
        if which == "fast" and not port_alive(FAST["port"]):
            print("  the fast model is not running -- starting it ...")
            use("fast", args.wait, args.force)
    port = DEEP["port"] if which == "deep" else FAST["port"]
    model = DEEP["model"] if which == "deep" else FAST["model"]
    if args.file:
        prompt = Path(args.file).read_text(encoding="utf-8", errors="replace")
    if not prompt:
        sys.exit("  give a prompt, --file <path>, or use --probe")
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": args.max_tokens, "temperature": args.temperature}
    if which == "deep":
        # the deep model reasons first and can spend the whole budget thinking
        body["reasoning_budget_tokens"] = args.reasoning_budget
    t0 = time.time()
    d = http_json(f"http://127.0.0.1:{port}/v1/chat/completions", timeout=3600, data=body)
    el = time.time() - t0
    u = d.get("usage", {})
    msg = d["choices"][0]["message"]
    text = msg.get("content") or ""
    if not text and msg.get("reasoning_content"):
        text = msg["reasoning_content"]
    print()
    print(text)
    print()
    print(f"--- {model} | {el:.1f}s | prompt {u.get('prompt_tokens')} "
          f"completion {u.get('completion_tokens')} | finish {d['choices'][0].get('finish_reason')}")
    if not text:
        print("    (empty answer -- the model spent the budget thinking; raise --reasoning-budget or --max-tokens)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["status", "use", "stop", "ask"])
    # 'which' is only meaningful for `use`; for `ask` the positional is the
    # prompt, so it must not be constrained to {fast, deep} or argparse
    # rejects a free-text prompt.
    ap.add_argument("which", nargs="?")
    ap.add_argument("prompt", nargs="?")
    ap.add_argument("--fast", action="store_true", help="target the fast model")
    ap.add_argument("--deep", action="store_true", help="target the deep model")
    ap.add_argument("--file", help="read the prompt from a file")
    ap.add_argument("--max-tokens", type=int, default=1500)
    ap.add_argument("--reasoning-budget", type=int, default=700)
    ap.add_argument("--temperature", type=float, default=0.1)
    ap.add_argument("--wait", type=int, default=600)
    ap.add_argument("--force", action="store_true",
                    help="restart the target even if it is already running "
                         "(needed after a config change: the server reads its "
                         "config only at start)")
    a = ap.parse_args()

    if a.action == "status":
        status()
    elif a.action == "use":
        if a.which not in ("fast", "deep"):
            sys.exit("  say which: use fast | use deep")
        use(a.which, a.wait, a.force)
    elif a.action == "stop":
        kill_port(FAST["port"], FAST["name"])
        kill_port(DEEP["port"], DEEP["name"])
        print("  stopped.")
    elif a.action == "ask":
        ask(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
