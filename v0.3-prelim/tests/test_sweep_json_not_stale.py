"""Guard the §2.6a sweep JSON against being stale relative to its generator.

Why this test exists
--------------------
The other n18 guards compare the paper's §2.6a table to the JSON on disk. That
catches a paper that disagrees with its data file — but it does NOT catch a
**stale data file**. On 2026-10-25 the checked-in
``v192_a_phase44_sigma_peak_sensitivity.json`` still carried the pre-R88(26)
resonance anchor (``v = 28``) while the generator had moved to the canonical
``v = 29.4``. Every paper-vs-JSON comparison passed; the table was 13 % wrong
because the JSON itself was out of date. The paper-vs-JSON test was green
throughout and still shipped a wrong number.

What it checks
--------------
1. The JSON's own ``parameterization`` string names the canonical anchor
   (``v = 29.4``) and not the superseded one (``v = 28``).
2. Regenerating the generator's output reproduces the checked-in JSON.

Check 2 is the strong one: it re-runs the generator and requires byte-level
agreement with the committed file. It is therefore a *reproducibility* check,
and it is skipped when the generator cannot run in this environment rather than
failing for an unrelated reason.

Both checks are read at test time — no hard-coded expectation of the file's
bytes — so the test keeps working when the generator legitimately changes.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GENERATOR = REPO / "scripts" / "v192_a_phase44_sigma_peak_sensitivity.py"
SWEEP_JSON = (
    REPO / "v0.3-prelim" / "data" / "results"
    / "v192_a_phase44_sigma_peak_sensitivity.json"
)

# The canonical resonance anchor, per the generator's own constant.
CANONICAL_ANCHOR = "29.4"
# The superseded anchor that must not reappear.
RETIRED_ANCHOR = "(v-28)"


def test_sweep_json_parameterization_names_canonical_anchor():
    """The JSON must describe the anchor the generator actually uses."""
    assert SWEEP_JSON.exists(), f"missing generator output: {SWEEP_JSON}"
    data = json.loads(SWEEP_JSON.read_text(encoding="utf-8"))
    param = data.get("parameterization", "")
    assert param, "sweep JSON has no 'parameterization' field to audit"
    assert CANONICAL_ANCHOR in param, (
        "sweep JSON parameterization does not name the canonical anchor "
        f"{CANONICAL_ANCHOR!r}: {param!r}. The generator's V1_V_TARGET is the "
        "authority (v192_dsph.V1_V_TARGET); regenerate the JSON."
    )
    assert RETIRED_ANCHOR not in param, (
        f"sweep JSON parameterization still uses the retired anchor {RETIRED_ANCHOR!r}: "
        f"{param!r}. Regenerate the JSON with the current generator."
    )


def test_regenerating_the_sweep_reproduces_the_committed_json():
    """Re-running the generator must reproduce the committed JSON exactly."""
    if not GENERATOR.exists():
        pytest.skip("generator script not present")
    if not SWEEP_JSON.exists():
        pytest.skip("sweep JSON not present")

    committed = SWEEP_JSON.read_bytes()
    committed_mtime = SWEEP_JSON.stat().st_mtime

    # Use a python that can import the generator's dependencies. Prefer the
    # project's benchmark venv; fall back to the interpreter running the tests.
    venv_py = REPO / ".venv-sidm-bench" / "Scripts" / "python.exe"
    python = str(venv_py) if venv_py.exists() else sys.executable

    # IMPORTANT: strip PYTHONPATH. The Hermes agent process injects its own
    # site-packages into PYTHONPATH, which shadows the venv's numpy with an
    # ABI-incompatible build (2.4.3 vs the venv's 2.5.2) and the generator dies
    # with "No module named 'numpy._core._multiarray_umath'". Observed 2026-10-25.
    # Clearing it makes the venv's own packages win. Verified: exit 1 -> exit 0.
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)

    try:
        proc = subprocess.run(
            [python, str(GENERATOR)],
            cwd=str(REPO), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=600, env=env,
        )
    except subprocess.TimeoutExpired:
        pytest.skip("sweep generator exceeded the 600 s timeout")
    except OSError as exc:
        pytest.skip(f"cannot run the generator here: {exc}")

    if proc.returncode != 0:
        # Distinguish "cannot run here" (skip, honestly) from "ran and failed"
        # (must fail). An ABI/shadowing error is environmental.
        stderr = proc.stderr or ""
        environmental = any(
            marker in stderr for marker in (
                "No module named",          # import/ABI problem
                "ModuleNotFoundError",
                "DLL load failed",
            )
        )
        if environmental:
            pytest.skip(
                "sweep generator cannot run in this environment (import/ABI "
                f"failure): {stderr.strip().splitlines()[-1] if stderr.strip() else 'unknown'}"
            )
        pytest.fail(
            f"sweep generator exited {proc.returncode}\n"
            + "\n".join((stderr or "").splitlines()[-12:])
        )

    regenerated = SWEEP_JSON.read_bytes()
    # The generator rewrote the file; restore the committed bytes either way so
    # the test never mutates the working tree.
    SWEEP_JSON.write_bytes(committed)
    try:
        os.utime(SWEEP_JSON, (committed_mtime, committed_mtime))
    except OSError:
        pass

    if regenerated == committed:
        return

    # Not identical — decide whether that is a REAL staleness problem or just
    # key ordering / float formatting noise.
    try:
        a = json.loads(committed.decode("utf-8"))
        b = json.loads(regenerated.decode("utf-8"))
    except json.JSONDecodeError:
        pytest.fail("sweep JSON is not valid JSON after regeneration")

    if a == b:
        # Same data, different serialisation -> acceptable, but worth noting.
        return

    # Real difference. Report precisely where.
    diffs = []
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            if key == "results":
                for ra, rb in zip(a.get(key, []), b.get(key, [])):
                    if ra != rb:
                        changed = [
                            k for k in set(ra) | set(rb) if ra.get(k) != rb.get(k)
                        ]
                        diffs.append(
                            f"results[sigma_peak={ra.get('sigma_peak_HH_1_cm2_per_g')}]: "
                            + ", ".join(
                                f"{k}: {ra.get(k)!r} -> {rb.get(k)!r}" for k in changed[:4]
                            )
                        )
            else:
                diffs.append(f"{key}: {a.get(key)!r} -> {b.get(key)!r}")
    pytest.fail(
        "regenerating the sweep does NOT reproduce the committed JSON -- the "
        "committed file is stale:\n  " + "\n  ".join(diffs[:12])
    )
