"""Verify the effect of changing the AMD Adrenalin UMA carve-out.

Run this BEFORE and AFTER the carve-out change + reboot. It captures the
four things that can move, and prints a diff-friendly key=value block.

    C:/Python314/python.exe scripts/verify_carveout.py

What it measures
  1. OS-visible RAM and the Windows commit limit (RAM + page file)
  2. Vulkan memory heaps (device-local vs host-visible) via vulkaninfo
  3. The INCUMBENT model's speed via llama-bench -- this is the regression
     guard. If tg128 drops after the carve change, the change hurt.
  4. Which Vulkan memory type the model lands in (dedicated vs shared)

Baseline recorded 2026-10-22, carve-out = 32 GB:
  OS visible 63.62 GiB | commit 84.88 GiB | pagefile 21.26 GB
  heap[0] host-visible 26.54 GiB | heap[1] device-local 53.08 GiB
  llama-bench tg128 19.93 +/- 0.11 | pp512 405.82 +/- 0.77
  model sits in DEDICATED VRAM (22.65 GB dedicated usage observed)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERMES = Path(r"C:\Users\lamkuenai\AppData\Local\hermes")
LLAMA = HERMES / "tools" / "llamacpp-vulkan-11370-win32-x64"
MODEL = HERMES / "models" / "Qwen3.6-35B-A3B-UD-Q4_K_M.gguf"
OUT = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\carveout_verify.json")

GIB = 1024 ** 3


def ps(script: str) -> str:
    p = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script],
                       capture_output=True, text=True)
    return p.stdout


def mem() -> dict:
    s = ps(r'''
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$pf = Get-CimInstance Win32_PageFileUsage
$mem = Get-CimInstance Win32_PhysicalMemory
$total = ($mem | Measure-Object Capacity -Sum).Sum
$o = [ordered]@{}
$o.total_installed_gib = [math]::Round($total/1GB,2)
$o.os_visible_gib = [math]::Round($os.TotalVisibleMemorySize/1MB,2)
$o.os_free_gib = [math]::Round($os.FreePhysicalMemory/1MB,2)
$o.commit_total_gib = [math]::Round($os.TotalVirtualMemorySize/1MB,2)
$o.commit_free_gib = [math]::Round($os.FreeVirtualMemory/1MB,2)
$o.pagefile_gib = if ($pf) { [math]::Round(($pf | Measure-Object AllocatedBaseSize -Sum).Sum/1024,2) } else { 0 }
$o.pagefile_auto = (Get-CimInstance Win32_ComputerSystem).AutomaticManagedPagefile
$o | ConvertTo-Json -Compress
''')
    try:
        return json.loads(s.strip().splitlines()[-1])
    except Exception:
        return {"raw": s.strip()}


def heaps() -> dict:
    try:
        p = subprocess.run(["vulkaninfo"], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        return {"error": "vulkaninfo not found"}
    txt = p.stdout
    out = {"heaps": []}
    for m in re.finditer(r"memoryHeaps\[(\d+)\]:\s*\n\s*size\s*=\s*(\d+)", txt):
        idx, size = int(m.group(1)), int(m.group(2))
        out["heaps"].append({"index": idx, "gib": round(size / GIB, 2)})
    for m in re.finditer(r"memoryTypes\[\d+\]:\s*\n\s*heapIndex\s*=\s*(\d+)\s*\n\s*propertyFlags\s*=\s*0x([0-9a-f]+)", txt):
        out.setdefault("types", []).append(
            {"heap": int(m.group(1)), "flags": m.group(2)})
    out["total_gib"] = round(sum(h["gib"] for h in out["heaps"]), 2)
    return out


def device_list() -> str:
    p = subprocess.run([str(LLAMA / "llama-server.exe"), "--list-devices"],
                       capture_output=True, text=True, timeout=120)
    line = [l for l in (p.stdout + p.stderr).splitlines() if "Vulkan0" in l]
    return line[0].strip() if line else "?"


def gpu_mem_counters() -> list:
    s = ps(r'''
Get-Counter '\GPU Adapter Memory(*)\Dedicated Usage','\GPU Adapter Memory(*)\Shared Usage' -EA SilentlyContinue |
  Select-Object -ExpandProperty CounterSamples |
  ForEach-Object { [ordered]@{ path=$_.Path; gib=[math]::Round($_.CookedValue/1GB,2) } } |
  ConvertTo-Json -Compress
''')
    try:
        d = json.loads(s.strip().splitlines()[-1])
        return d if isinstance(d, list) else [d]
    except Exception:
        return []


def bench() -> dict:
    if not MODEL.exists():
        return {"error": f"model missing: {MODEL}"}
    cmd = [str(LLAMA / "llama-bench.exe"), "-m", str(MODEL), "-ngl", "99",
           "-p", "512", "-n", "128", "-t", "16",
           "--cache-type-k", "q8_0", "--cache-type-v", "q8_0", "-fa", "on", "-r", "2"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return {"error": "llama-bench timed out"}
    txt = p.stdout + p.stderr
    res = {}
    for m in re.finditer(r"qwen35moe.*?\|\s*(pp512|tg128)\s*\|\s*([\d.]+)\s*±\s*([\d.]+)", txt):
        res[m.group(1)] = {"tps": float(m.group(2)), "sd": float(m.group(3))}
    res["ok"] = bool(res)
    return res


if __name__ == "__main__":
    report = {
        "timestamp": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "memory": mem(),
        "vulkan_heaps": heaps(),
        "vulkan_device": device_list(),
        "gpu_mem_counters": gpu_mem_counters(),
        "incumbent_bench": bench(),
    }
    print("=" * 70)
    print("CARVE-OUT VERIFICATION")
    print("=" * 70)
    m = report["memory"]
    print(f"  installed            : {m.get('total_installed_gib')} GiB")
    print(f"  OS visible           : {m.get('os_visible_gib')} GiB  "
          f"(free {m.get('os_free_gib')})")
    print(f"  commit limit         : {m.get('commit_total_gib')} GiB  "
          f"(free {m.get('commit_free_gib')})")
    print(f"  page file            : {m.get('pagefile_gib')} GiB  auto={m.get('pagefile_auto')}")
    h = report["vulkan_heaps"]
    for x in h.get("heaps", []):
        print(f"  vulkan heap[{x['index']}]        : {x['gib']} GiB")
    print(f"  vulkan total         : {h.get('total_gib')} GiB")
    print(f"  device               : {report['vulkan_device']}")
    b = report["incumbent_bench"]
    print(f"  incumbent tg128      : {b.get('tg128')}")
    print(f"  incumbent pp512      : {b.get('pp512')}")
    if b.get("ok"):
        tg = b["tg128"]["tps"]
        print()
        if tg < 15.0:
            print(f"  *** REGRESSION: tg128 {tg} < 15 tok/s -- REVERT the carve-out change ***")
        else:
            print(f"  OK: tg128 {tg} tok/s (baseline was 19.93) -- no regression")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  saved -> {OUT}")
