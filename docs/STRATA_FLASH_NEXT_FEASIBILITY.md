# Strata + Qwen3.8-Flash-Next on this host — feasibility analysis

**Date:** 2026-10-22
**Host:** Minisforum, AMD Ryzen AI 9 HX 370 (12C/24T, Zen 5, AVX-512), Radeon 890M
(`gfx1150`, RDNA 3.5, 16 CUs, PCI `VEN_1002&DEV_150E`), 96 GB DDR5-5600, NVMe SSD, Windows 11 Pro.
**Question:** can the Strata inference engine enable a stronger MoE local model?

## Verdict

**Yes — and the evidence is measured on this exact machine.** Strata can run
**Qwen3.8-Flash-Next (125B total / 6B active)** here at **~11 tok/s decode** on
Windows, versus **18.03 tok/s** for the current `Qwen3.6-35B-A3B-UD-Q4_K_M`.
That is ~35–40% slower but a large jump in capability.

**Not a one-click install.** It needs a hand-built Windows HIP engine for
`gfx1150`, a raised page file, and a BIOS carve-out change. Budget 3–5 hours
including the 76 GB download.

## Why the prior "not supported" answer is wrong

The 2026-10-16 decision to drop Strata cited "Strata AI_SETUP.md explicitly says
integrated GPUs not supported". That was accurate then. It is no longer the whole
story:

- Strata **PR #2147** (`onionbutties`) added an opt-in
  `STRATA_EXPERIMENTAL_GFX1150=1` for the Radeon 890M/880M.
- Niko1221 confirmed on 2026-10-19 that the change **is merged into `main` for
  0.2.0-beta**. Current release: **0.2.2 / engine 0.1.47**.
- The *default* path still refuses iGPUs. The opt-in enables them.

`docs/AMD_HIP.md` in the current tree states it plainly: *"gfx1150 (Radeon 890M,
Ryzen AI 9 HX PRO 370, Strix Point, #1217): builds and runs from 0.1.40.2 as an
unvalidated target... Setup does not install for it yet: build by hand with
`-DCMAKE_HIP_ARCHITECTURES=gfx1150`."*

## The community report is this machine

PR #2147's reporter ran the same hardware class:

| | Community rig (PR #2147) | This host |
|---|---|---|
| CPU | Ryzen AI 9 HX 370, 12C/24T Zen 5 | identical |
| GPU | Radeon 890M, `gfx1150`, RDNA 3.5, 16 CUs, `1002:150E` | identical |
| RAM | 96 GB DDR5-5600 | 96 GB (2×48 GB) |
| Visible to OS | 63.6 GB (32 GB BIOS carve for iGPU) | 63.62 GB, 32.38 GB implied carve |
| OS | Windows 11 Pro build 26200 | Windows 11 Pro |

### Measured decode, GSQ-RCO IQ3_XXS, all 24,576 experts in the GPU pool

| Prompt tokens | Generated | Time | Decode |
|---:|---:|---:|---:|
| 34 | 161 | 14,772 ms | **10.9 tok/s** |
| 25 | 210 | 18,654 ms | **11.3 tok/s** |
| 25 | 188 | 15,910 ms | **11.8 tok/s** |

MTP `--spec 4` draft acceptance 46–54%. Short prompts read at 21.5–29.2 tok/s
(fixed overhead dominates at that size). The Linux variant of the same chip
(GTT raised to 64 GiB) reaches **15–19 tok/s** — the Windows gap is memory
pressure, not the engine.

## Capability delta

Qwen3.8-Flash-Next: 125B backbone + 51B n-gram embeddings + 4B MTP head,
**6B active per token**, 48 layers, 512 experts/layer, 262K context, multimodal.

Reported: SWE-bench Pro 62.5 · LiveCodeBench v6 91.9 · DeepSWE 1.1 58.7 ·
Toolathlon Verified 73.5 · JobBench 55.7 · CoWorkBench 73.9 · MathVision 95.7.
Qwen's own claim is that it outperforms Claude-4.6-Opus (Max).

Against the current `Qwen3.6-35B-A3B` (3B active) this is a different class of
model, not a quant tweak.

## Quant options and memory fit

| Size | Resident (shard 1) | N-gram shard 2 | Download | RAM needed |
|---|---:|---:|---:|---:|
| Q2_0 | 37.62 GB | 28.80 GB | 66.4 GB | ~47 GB |
| IQ2_XS | 39.23 GB | 28.80 GB | 68.0 GB | ~49 GB |
| **IQ3_XXS** | **47.04 GB** | **28.80 GB** | **75.8 GB** | **~57 GB** |
| IQ3_S | 54.82 GB | 28.80 GB | 83.6 GB | ~65 GB |

Plus a ~6 GB MTP draft layer on first start. N-gram shard 2 stays on the SSD and
is memory-mapped, so it is not resident RAM.

GSQ-RCO task-average quality: BF16 93.12 · Q2_0 89.07 · IQ2_XS 89.16 ·
**IQ3_XXS 92.57** · IQ3_S 93.26. IQ3_XXS is the sweet spot: 92.57 vs the BF16
baseline of 93.12, at 47 GB instead of 54.8 GB.

`IQ3_XXS` is the community-verified choice on this hardware and is what the
reporter ran.

## Host prerequisites — current state

| Requirement | Status |
|---|---|
| git 2.53.0 | **OK** |
| Python 3.14.7 | **OK** |
| MSVC C++ workload | **OK** — `C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools` |
| cmake 3.24+ | **MISSING** |
| ninja | **MISSING** (`py -3 -m pip install ninja`) |
| AMD driver | OK — 32.0.32015.7029 |
| ROCm | not installed; the engine bundles it (TheRock `10.2.0a20260930`, `rocm-sdk-device-gfx1150` is published for Windows) |
| Page file | **auto-managed at 21.26 GB — must be raised** |
| Free disk | 1.2 TB — ample |

### The memory trap

The 32 GB BIOS carve-out leaves the OS 63.6 GB, and the Windows commit limit
(RAM + page file) is ~68 GB. The engine's **default pinned expert arena is
39.97 GiB**, which exhausts that limit — the engine exits with `0xC0000409`.
Two fixes, both required:

1. `--mmap-experts` — map the GGUF instead of pinning an arena. This also lets
   all 24,576 experts into the GPU pool.
2. A **fixed** page file (~65 GB), not system-managed — a system-managed page
   file "may not grow in time" (upstream issue #60).

Also recommended: drop the BIOS iGPU carve-out from 32 GB to ~2 GB for
headroom, and keep `--conversation-cache-mib 2048`.

### The carve-out mechanism (measured on this host, 2026-10-22)

Adrenalin **Performance → Tuning → System** exposes three rows:

| Row | Value now | Meaning |
|---|---|---|
| Variable Graphics Memory (VGM) | Custom (Select an amount below) | BIOS-level reallocation of system RAM into dedicated graphics memory (Ryzen AI 300 feature) |
| Dedicated Graphics Memory | 32 GB | the carve-out; dropdown offers 0.5 / 1 / 2 / 4 / 8 / 16 / 32 / 48 GB |
| Remaining System Memory | (hidden by open dropdown) | live readout of what the OS keeps |

AMD's FAQ is explicit that *dedicated* must not be confused with *shared*: in
typical Windows systems 50% of RAM is already shared with the iGPU and stays
CPU-accessible.

Measured Vulkan heaps on this host:

```
heap[0] host-visible    26.54 GiB
heap[1] DEVICE_LOCAL    53.08 GiB
total GPU-addressable   79.62 GiB   (llama.cpp: 81528 MiB)
```

At carve = 32, `32 + 48 (50% of 96) = 80 GiB` matches the observed 79.62 GiB to
within the OS's own reserve. So **the shared block is ~48 GiB = 50% of total RAM
and is independent of the carve.**

Consequence — lowering the carve *shrinks* the GPU's total addressable pool:

| Carve | GPU-addressable | OS sees | Commit limit | Incumbent 22.6 GB model |
|---|---|---|---|---|
| 32 GB (now) | 79.62 GiB | 64.00 | 85.26 | in dedicated |
| 2 GB | ~50 GiB | 94.00 | 115.26 | spills to shared |
| 0.5 GB | ~48.5 GiB | 95.50 | 116.76 | spills to shared |

The model does not stop working — shared is still GPU-addressable
(host-visible + coherent) — but it runs over a slower path, and the
device-local heap shrinks. This is still the right direction for Strata, which
deliberately keeps experts in the shared pool and needs OS headroom for the
arena; the upstream Linux gfx1150 rig used a **512 MB** carve and reached
15–19 tok/s. But **2 GB beats 0.5 GB** for a stronger reason than before: 0.5 GB
gives +1.5 GiB less headroom *and* a 1.5 GiB smaller GPU pool.

The change requires a **reboot** ("System Restart Required"). The
**Remaining System Memory** readout is the single best live check: after
picking 2 GB it should read ~94 GB.

Verify with `scripts/verify_carveout.py` before and after; it flags
`tg128 < 15 tok/s` as a revert signal (baseline 20.30 at carve = 32).

## What it does NOT do — measured, 2026-10-22

**Strata is now INSTALLED AND RUNNING on this host.** Full result below. The
short version: it works, it matches the incumbent's accuracy, it is ~30% slower
per token, and it needs the whole machine to itself.

### Install record (all steps verified, exit 0)

```bash
# 1. toolchain (pip = user-scope, no admin; the Scripts dir must be on PATH)
py -3 -m pip install cmake ninja
#    -> cmake 4.4.4, ninja 1.13.2 in
#    C:\Users\lamkuenai\AppData\Local\Python\pythoncore-3.14-64\Scripts

# 2. repo
git clone --depth 1 https://github.com/Niko1221/Strata.git C:\Users\lamkuenai\Strata

# 3. the gfx1150 engine (no release ships one for this card)
cd C:\Users\lamkuenai\Strata
set STRATA_HIP_ARCHS=gfx1150
set STRATA_ROCM_VERSION=10.2.0a20260930
set STRATA_ROCM_INDEX=https://nightly.repo.amd.com/rocm/whl-next/
tools\hip\build_windows.bat          # -> dist\strata-windows-x64-hip.zip (145 MB)

# 4. unpack with unzip (it is a zip, not a tar)
unzip -q dist\strata-windows-x64-hip.zip -d engine\

# 5. device check (needs engine\rocm\bin on PATH)
strata-device.exe --selftest
#    -> "arch gfx1150, 75.6 GiB, wave32" + "strata-device selftest OK"

# 6. install (the opt-in is what makes setup.py accept the iGPU)
set STRATA_EXPERIMENTAL_GFX1150=1
py -3 setup.py --backend hip --prebuilt dist --yes --family qwen --model IQ3_XXS --context 65536 --no-start
#    -> "All set."

# 7. start
py -3 serve\server.py --engine strata --config strata-iq3_xxs.json --port 8080
```

Gotchas that cost time and are not in the upstream docs:

| Gotcha | Detail |
|---|---|
| Model files go in `Strata-data\models\IQ3_XXS\` | the tag is `fam["tag"] + model`; the **qwen family's tag prefix is empty**, so the dir is `IQ3_XXS`, not the model name |
| The HF repo stores shards in a subdirectory | `IQ3_XXS/Qwen3.8-...gguf` — a flat path 404s |
| The MTP draft comes from a different repo | `Qwen/Qwen3.8-Flash-Next`, not the GSQ-RCO repo: `py -3 tools/mtp_fetch.py fetch --out C:\Users\lamkuenai\Strata-data\mtp` |
| `setup.py` does NOT write `--mmap-experts` | it is **mandatory** per the upstream report; add it by hand, plus `--conversation-cache-mib` |
| `cmd //c` does not work in MSYS git-bash | it opens an interactive shell instead. Use `cmd.exe /c` |
| The zip needs `unzip`, not `tar` | `tar -xf` fails with "does not look like a tar archive" |

### Measured performance

| | Incumbent (llama.cpp) | Strata (Flash-Next IQ3_XXS) |
|---|---|---|
| Model | 35B total / 3B active | **125B total / 6B active** |
| Decode | 18.03 tok/s | **12.7–16.2 tok/s** |
| Prefill | 545 tok/s | 165 tok/s (13K prompt) / 420 tok/s (cached) |
| Scored paper-audit battery | **+11/12** | **+11/12** |
| Wall time for the battery | 237 s | 1524 s |
| MTP draft acceptance | n/a | 65–66% short, 85% at 13K context |

Upstream community figures on identical hardware: 10.9–11.8 tok/s (Windows rig),
15–19 tok/s (Linux rig). **This host matches or beats them.**

Both models miss the *same* question (the one asking about a table that is not in
the excerpt) and both handle it **honestly** — reporting the table is absent
rather than hallucinating a column count.

**Read the engine's own log line, not the client's wall clock.** The client
divides total time (including prefill) by completion tokens, which makes a
13K-token request look like 2.7 tok/s when the real decode figure is 15.1:

```
strata serve: prompt 13241 tokens = 0 reused + 13241 read in 90797 ms (145.8 tok/s),
              300 generated in 19811 ms (15.1 tok/s), drafts accepted 176 of 208
```

### Two open issues

1. **The PLE (n-gram) table I/O.** The engine auto-picks `--ple-io direct` and
   warns it measures only 25 MB/s of random 4 KiB reads on this SSD, so *"a
   prompt can spend minutes reading layer 1 and trip the stall watchdog"*.
   Upstream says `--ple-io mmap` is 40–100× faster on DRAM-less NVMe but 7×
   slower on SATA. This host has a **CT2000P310SSD8 (DRAM-less NVMe)**, so
   `--ple-io mmap` is correct — it moved prefill from 145.8 to 165.3 tok/s.

2. **The Windows commit limit is a live landmine.** The engine warns:
   *"the Windows commit limit is 84.9 GiB (RAM + page file) and 2.5 GiB of it is
   left … it can end at the limit with no message (exit code 0xC0000409, #1607)
   while RAM is still free."* Measured live: commit free fell to **0.98 GiB**
   during a 13K-token request. Mitigated without a reboot by lowering
   `--conversation-cache-mib` (2048→512), `--max-context` (65536→32768) and
   `--prefill` (auto→4096), which cut planned host allocations from 4.0 to
   2.5 GiB. **The real fix is a FIXED 65 GB page file** (commit limit →128.6
   GiB) — that needs admin rights, which the agent does not have; run
   `C:\Users\lamkuenai\Strata\fix_pagefile.ps1` elevated, then reboot.

### The verdict that follows from the numbers

Strata is **not** a drop-in replacement for the incumbent; it is a different tier.

- As the **primary** local reviewer: too slow (6.4× on the paper battery).
- As a **deep second opinion** on contested findings: worth it. 125B-A6B catches
  things a 35B/3B cannot, and being a different model family it fails
  differently — genuine independence for the two-reviewer loop.

The RAM does not allow both to run at once; the incumbent on :50113 was stopped
to give Strata the machine.

## The install sequence (from the upstream report)

```powershell
# 1. Toolchain
py -3 -m pip install ninja
# cmake 3.24+ and VS 2022+ Build Tools (C++ workload)

# 2. Build the gfx1150 Windows engine
set STRATA_HIP_ARCHS=gfx1150
tools\hip\build_windows.bat          # -> dist\strata-windows-x64-hip.zip

# 3. Unpack the zip; with rocm\bin on PATH:
strata-device.exe --list-devices     # expect: arch gfx1150, ~75.6 GiB
strata-device.exe --selftest

# 4. Install with the opt-in
set STRATA_EXPERIMENTAL_GFX1150=1
START-HERE.bat --backend hip --prebuilt dist --yes ^
  --family qwen --model IQ3_XXS --context 65536 --no-start

# 5. Add to the model config's args:
#    --mmap-experts --conversation-cache-mib 2048
# 5b. Set a fixed ~65 GB page file; drop BIOS iGPU carve-out to ~2 GB

# 6. Run
run-iq3_xxs.bat
curl http://127.0.0.1:8080/health
```

Expected health: `{"status":"ok","max_context":65536,"model":"qwen3.8-flash-next-iq3_xxs","loaded":true}`

## The llama.cpp alternative (cheaper experiment, weaker fit)

The local `llama.cpp b11370` **already contains `llama_model_qwen4exp`** —
Flash-Next's architecture. 10 hits in `llama.dll`, confirmed by direct byte
scan. So a Vulkan llama.cpp attempt needs no engine build at all.

Two facts cut against it:

1. **Memory.** Plain llama.cpp must hold the entire 75.8 GB resident. This host
   has 63.62 GB visible to the OS. It does not fit without pagefile thrash.
   Strata's tiered expert cache is precisely the mechanism that solves this.

2. **The HIP cliff does not apply to us.** llama.cpp issue #27856 documents a
   severe decode collapse on HIP/`gfx1151` past ~1K context (19–21 tok/s →
   ~6 tok/s), caused by `ggml_top_k` falling back to CPU past `ne <= 1024`
   columns without `GGML_CUDA_USE_CUB`. The reporter confirms it is
   **backend-specific** and that the **Vulkan/RADV path — which this host uses —
   stays flat across depth** with the same binary and model.

So the Vulkan llama.cpp route is technically viable and cheap to try, but the
resident-memory wall makes it a worse fit than Strata for a 125B model. Strata's
whole reason for existing is the thing llama.cpp cannot do here.

## Risks

- `gfx1150` remains an **unvalidated** upstream target. One machine, one report.
- The 32 GB carve-out is the binding constraint on Windows. Getting it wrong
  means `0xC0000409` on startup, not a slow run.
- The community report did **not** measure long prompts (4K/16K/128K), needles,
  answer quality, concurrency, or `--prefill 16384` on Windows. Only short-context
  decode and per-GEMM calibration.
- A GPU reset under transparent huge pages is a known hazard on iGPUs
  (`STRATA_NO_ARENA_THP=1` is set automatically for gfx1150).
- ~76 GB of model files plus a build tree. Disk is fine; the real cost is time.
- If this replaces the current model as the agent's local reviewer, the
  **scored** A/B protocol in `scripts/bench_local_models_v2.py` applies — the
  model-card benchmark table does not predict review quality.

## Recommendation

Worth doing, on these terms:

1. Treat it as a **second reviewer / specialist role**, not a replacement for
   `Qwen3.6-35B-A3B` (18.03 tok/s, +11/12 on the scored paper-audit battery).
   Keep the incumbent on :50113.
2. Run the install on a **separate port** (Strata defaults to 8080).
3. Budget **3–5 hours** and **~76 GB** of downloads.
4. Gate the decision on the **scored** A/B, not on tok/s or model-card numbers.
5. If the Windows memory wall proves unsolvable, the **Linux/WSL2 route** with
   GTT raised to 64 GiB is the documented alternative at 15–19 tok/s — but
   WSL2 Vulkan exposes only `llvmpipe` on this APU, so a native Linux box or
   the ROCm path in WSL2 would be needed, and that is a much larger commitment.

## Sources

- Strata PR #2147 — Windows 11 verification on Radeon 890M / 96 GB (the
  decisive source; contains the full reproduce recipe)
- `docs/AMD_HIP.md` — gfx1150 status, tuning table, integrated-GPU notes
- `docs/STRIX_HALO.md` — unified-memory APU handling, GTT mechanics
- `bench/results/2026-10-07-community-gfx1150/` — Linux 890M report, 15–19 tok/s
- `docs/RADEON_780M.md` — gfx1103 iGPU opt-in port
- llama.cpp issue #27856 — the HIP TOP_K cliff, and the Vulkan exemption
- `docs/MODELS.md` — quant sizes, RAM requirements, quality table
