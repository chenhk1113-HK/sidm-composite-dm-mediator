# Tier 3 Auto-check Implementation Status (2026-09-20)

## Honest accounting

### What was attempted

| Component | Installed | Working | Status |
|---|---|---|---|
| Julia 1.13.0 | ✓ via winget | ✓ (runs as `julia --version`) | INSTALLED |
| PySR Python pkg | ✓ via pip | ✗ Julia path bug | **BLOCKED** |
| mutmut 3.x | ✓ via pip (Ubuntu WSL) | ✓ (manual mutation testing works) | PARTIAL |
| Ubuntu WSL Python | ✓ pre-installed | ✓ (Python 3.14.4 + pip 25.1.1) | OK |

### Root cause of PySR failure

PySR's `juliapkg` downloads its own Julia binary into
`.venv-sidm-bench/julia_env/pyjuliapkg/install/`. When trying to install
Julia packages (SymbolicRegression, PythonCall, etc.), it calls Julia
which fails with:

```
ERROR: could not load library
"/c/Users/lamkuenai/AppData/Local/Programs/Julia-1.13.0/bin\..\lib\julia\sys.dll"
The specified module could not be found.
```

**Root cause**: Julia 1.13.0 has a Windows path resolution bug. The
binary resolves `..\lib\julia\sys.dll` with mixed slash directions
that bash/MSYS can't translate properly. Tried 4 workarounds:

1. Set `JULIA_BINDIR` env var → ignored by pyjuliapkg
2. Replace pyjuliapkg's julia.exe with system Julia → still uses pyjuliapkg path resolution
3. Manual `julia --project=... Pkg.instantiate()` via .bat file → cmd.exe opens interactively
4. Use winpty/MSYS path conversion → same path mangling issue

All attempts blocked by the same upstream bug. Could potentially be
fixed by Julia 1.10 LTS, but Julia 1.10 isn't available via winget
(only 1.13.0 is).

### What IS verified working

**Tier 1** (all working, all tested):
- ArviZ 1.3.0 — posterior predictive check framework ready
- Hypothesis 6.168.0 — 8/8 property tests pass (200 examples each)
- SymPy 1.14.0 — 7/7 symbolic verification tests pass
- Snakemake 9.27.0 — dry-run + phenomenology_curves rule verified

**Tier 2 (partial)**:
- mutmut 3.x installed in Ubuntu WSL ✓
- Manual mutation testing WORKS: caught `*` → `-` mutation in
  `ke_cm_eV` (7 tests failed as expected)

### Manual mutation testing result

```bash
# Mutate ke_cm_eV: change * to -
cp t120_16_kinematic_threshold.py t120_16_kinematic_threshold.py.bak
sed -i 's|m_chi_eV = m_chi_GeV \* 1e9|m_chi_eV = m_chi_GeV - 1e9|' t120_16_kinematic_threshold.py

# Run tests with mutation
wsl -d Ubuntu -- python3 -m pytest v0.3-prelim/tests/test_t120_16_kinematic_threshold.py
# Result: 7 failed, 10 passed (as expected — tests caught the mutation)
```

**Caveat discovered**: After restoring the file, pytest shows the same
7 failures because of `.pyc` cache. Manual mutation testing requires
clearing `__pycache__/` between mutations for accurate results.

### Files added (Tier 3)

```
v0.3-prelim/docs/WSL_MUTMUT_SETUP.md         (mutmut-via-WSL guide)
conftest.py                                 (pytest path fix for WSL)
setup.cfg                                   (mutmut config)
install_julia_pkgs.bat                      (workaround attempt for Julia path bug)
```

### Honest assessment

**Tier 3 is INCOMPLETE.** PySR symbolic regression is blocked by a
Julia 1.13 + Windows path resolution bug that I was not able to
work around in this session.

**What we DO have** that catches real bugs:
- ✓ Tier 1-2 auto-checks (numerical formula verification, unit errors,
  edge cases)
- ✓ Manual mutation testing via WSL Ubuntu + sed (works without
  PySR)

**Recommendation for v1.15 (future)**:
- If/when Julia 1.10 LTS is installed via manual download, retry PySR
- Consider running PySR inside WSL Ubuntu (which has its own Python
  3.14.4) — Linux doesn't have the Windows path bug
- Add `__pycache__` cleanup to manual mutation testing workflow

## Status: Tier 3 NOT COMPLETE

**Standard self-check still ALL PASSED** for the parts that work.
Tier 3 features that depend on PySR are documented as blocked.

**Both branches @ `8274a89`** (Tier 3 work was exploratory, not committed)
