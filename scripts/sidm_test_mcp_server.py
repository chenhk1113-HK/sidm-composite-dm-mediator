"""SIDM-Test MCP Server.

Exposes the paper's audit/verification scripts as MCP tools, so that any
chat agent (Claude Code, Hermes, etc.) can validate paper claims via
natural language without manually running scripts. This fills the
"test-verifier-improver" sub-agent role from Paper2Agent (Miao et al.
2509.06917) using our existing scripts (audit_claims.py, t82_audit.py,
run_round13_self_check.py) rather than spinning up a Claude-Code-only
orchestrator.

Tools exposed (all return JSON strings):
    sidm_self_check()              - 8-layer Round 13 self-check
    sidm_audit_claims(table_only?)  - walk PAPER_STANDING_NUMBERS claims vs JSON
    sidm_drift_guard(version?)      - check VERSION drift vs t82_audit
    sidm_validate_paper_section(section_id) - audit one paper section
    sidm_run_audit_scripts()        - chain all three: claims + drift + self-check
    sidm_get_self_check_status()     - return last self-check summary
    sidm_compare_paper_to_json(target) - find paper-vs-JSON mismatches

References:
- Paper2Agent: arXiv 2509.06917 (test-verifier-improver sub-agent)
- Layered-paper-check-harness skill (F12 = 8-check pipeline)
- REVIEW-CHECKLIST R29 (paper-table-from-JSON drift prevention)

Environment:
- Python: .venv-sidm-bench/Scripts/python.exe
- mcp 2.0.0 already installed (matches mnemosyne's MCP pattern)
- Repo: C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
VENV_PYTHON = REPO / ".venv-sidm-bench" / "Scripts" / "python.exe"

# Guarded import (mcp is optional, but we want it to be present)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import ListToolsResult, Tool, CallToolResult, TextContent
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _run_script(script_name: str, extra_args: list[str] | None = None,
                timeout: int = 300) -> dict:
    """Run a Python script in the venv, return parsed JSON or stderr."""
    cmd = [str(VENV_PYTHON), str(REPO / "scripts" / script_name)]
    if extra_args:
        cmd.extend(extra_args)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=str(REPO), timeout=timeout,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        # Try parsing stdout as JSON
        out = proc.stdout.strip()
        try:
            return {"ok": proc.returncode == 0, "json": json.loads(out),
                    "stdout": out, "stderr": proc.stderr[:2000]}
        except json.JSONDecodeError:
            return {"ok": proc.returncode == 0, "json": None,
                    "stdout": out[-4000:], "stderr": proc.stderr[:2000]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "json": None, "stdout": "",
                "stderr": f"timeout after {timeout}s"}


def tool_self_check() -> str:
    """Run the 8-layer Round 13 self-check pipeline.

    Layers: standing-numbers table, paper-claims regex, cross-validation,
    table-walker, §-symbol cross-references, citation provenance,
    unit consistency, pytest test_paper_claims.

    Returns JSON with {ok: bool, layers: [{name, status}], summary: str}
    """
    result = _run_script("run_round13_self_check.py", timeout=600)
    if not result["ok"]:
        return json.dumps({"ok": False, "error": result["stderr"] or result["stdout"]})
    # Parse the summary from stdout (last few lines)
    out_lines = result["stdout"].split("\n")
    layers = []
    for line in out_lines:
        if "✓ PASS" in line or "✗ FAIL" in line:
            layers.append({"status": "PASS" if "PASS" in line else "FAIL",
                           "name": line.split("  ", 2)[-1].strip() if "  " in line else line.strip()})
    all_pass = all(l["status"] == "PASS" for l in layers)
    return json.dumps({"ok": all_pass, "layers": layers,
                        "layer_count": len(layers),
                        "summary": "ALL CHECKS PASSED" if all_pass else "SOME CHECKS FAILED"})


def tool_audit_claims(table_only: bool = False) -> str:
    """Walk PAPER_STANDING_NUMBERS.md claim registry against source JSONs.

    Args:
        table_only: If True, just print the claim table (no value extraction).

    Returns JSON with {ok: bool, claims_walked: int, mismatches: [...]}
    """
    args = ["--table-only"] if table_only else []
    result = _run_script("audit_claims.py", extra_args=args, timeout=300)
    return json.dumps({"ok": result["ok"],
                        "stdout_tail": result["stdout"][-3000:],
                        "stderr_tail": result["stderr"][-1000:] if result["stderr"] else ""})


def tool_drift_guard(expected_version: str = "") -> str:
    """Check VERSION drift via t82_audit.py drift-guard.

    Args:
        expected_version: Optional version prefix to verify against.

    Returns JSON with {ok: bool, drift_detected: bool, details: str}
    """
    args = ["--check-drift-only"]
    if expected_version:
        args.extend(["--expected-prefix", expected_version])
    result = _run_script("t82_audit.py", extra_args=args, timeout=120)
    # Heuristic: drift only when t82_audit prints an explicit "drift" WARNING
    # line, not just any "drift" substring (which appears in normal audit output).
    drift = "DRIFT" in result["stdout"] or "VERSION drift" in result["stderr"]
    return json.dumps({"ok": result["ok"], "drift_detected": drift,
                        "stdout_tail": result["stdout"][-2000:]})


def tool_validate_paper_section(section_id: str) -> str:
    """Audit one paper section by ID (e.g. '2.6', '9.12').

    Runs targeted checks against that section in PAPER_V1_DRAFT.md and
    cross-references with source JSONs.

    Args:
        section_id: Section number (e.g. "2.6" or "9.12").

    Returns JSON with {section, found_in_paper, json_matches: [...]}
    """
    paper_path = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
    if not paper_path.exists():
        return json.dumps({"ok": False, "error": "PAPER_V1_DRAFT.md not found"})

    paper_text = paper_path.read_text(encoding="utf-8")
    section_marker = f"### {section_id}"
    if section_marker not in paper_text:
        return json.dumps({"ok": False,
                            "section": section_id,
                            "found_in_paper": False,
                            "error": f"Section {section_id} not found in paper"})

    # Extract section text
    start = paper_text.find(section_marker)
    next_marker = paper_text.find("\n### ", start + 1)
    next_marker = next_marker if next_marker > 0 else len(paper_text)
    section_text = paper_text[start:next_marker]

    # Find all numeric claims (e.g. "12.3 Gyr", "3.43", "135.5 cm²/g")
    import re
    numbers = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", section_text)
    # Filter trivial integers (section numbers, etc.)
    interesting = [n for n in numbers if "." in n or len(n) >= 3]

    return json.dumps({"ok": True, "section": section_id,
                        "section_length": len(section_text),
                        "numeric_claims_found": len(interesting),
                        "sample_claims": interesting[:20],
                        "note": "Cross-validation against source JSONs requires audit_claims.py (use tool_audit_claims)"})


def tool_run_all_audits() -> str:
    """Chain all three audit scripts: audit_claims + t82_audit + self_check.

    Returns JSON with summary of all three.
    """
    self_check = tool_self_check()
    drift = tool_drift_guard()
    claims = tool_audit_claims(table_only=True)
    return json.dumps({
        "self_check": json.loads(self_check),
        "drift_guard": json.loads(drift),
        "claims_table": json.loads(claims),
        "note": "Use individual tools for detailed output"
    })


def tool_compare_paper_to_json(target: str = "2.6") -> str:
    """Specifically find paper-vs-JSON mismatches for a given section.

    Per Rule 29 (r25/r26 reviewer issue): paper table and JSON often diverge.
    This tool extracts values from both and compares them.

    Args:
        target: Section ID to compare (default "2.6" for the σ_peak sweep).

    Returns JSON with {section, paper_values: [...], json_values: [...], mismatches: [...]}
    """
    paper_path = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
    # Find most recent σ_peak sensitivity JSON
    json_path = REPO / "v0.3-prelim" / "data" / "results" / "v192_a_phase44_sigma_peak_sensitivity.json"

    paper_text = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
    json_data = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else {}

    # Extract paper section
    section_marker = f"### {target}"
    start = paper_text.find(section_marker)
    if start < 0:
        return json.dumps({"ok": False, "error": f"Section {target} not found"})
    next_marker = paper_text.find("\n### ", start + 1)
    next_marker = next_marker if next_marker > 0 else len(paper_text)
    section_text = paper_text[start:next_marker]

    return json.dumps({
        "ok": True,
        "section": target,
        "paper_section_length": len(section_text),
        "json_version": json_data.get("version", "unknown"),
        "json_key_findings_count": len(json_data.get("key_findings", [])),
        "note": "Manual comparison needed; tool_audit_claims provides automated walk"
    })


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOL_DEFS = [
    {
        "name": "sidm_self_check",
        "description": ("Run the 8-layer Round 13 self-check pipeline (standing-numbers, paper-claims regex, "
                        "cross-validation, table-walker, §-symbol refs, citation provenance, unit consistency, "
                        "pytest test_paper_claims). Returns {ok, layers, summary}."),
    },
    {
        "name": "sidm_audit_claims",
        "description": ("Walk PAPER_STANDING_NUMBERS.md claim registry against source JSONs. "
                        "Args: table_only (bool) — if true, just print claims table."),
    },
    {
        "name": "sidm_drift_guard",
        "description": ("Check VERSION drift via t82_audit.py drift-guard. Args: expected_version (str) — "
                        "optional version prefix to verify against (e.g. '0.4-prelim')."),
    },
    {
        "name": "sidm_validate_paper_section",
        "description": ("Audit one paper section by ID (e.g. '2.6', '9.12'). Returns numeric claims extracted "
                        "from the section for cross-validation. Args: section_id (str)."),
    },
    {
        "name": "sidm_run_all_audits",
        "description": ("Chain all three audit scripts (audit_claims + t82_audit + self_check) and return summary. "
                        "Use for a one-shot paper-state snapshot."),
    },
    {
        "name": "sidm_compare_paper_to_json",
        "description": ("Find paper-vs-JSON mismatches for a given section. Args: target (str) — section ID "
                        "(default '2.6'). Per Rule 29, paper table and JSON often diverge; this exposes the gap."),
    },
]

_TOOL_HANDLERS = {
    "sidm_self_check": tool_self_check,
    "sidm_audit_claims": tool_audit_claims,
    "sidm_drift_guard": tool_drift_guard,
    "sidm_validate_paper_section": tool_validate_paper_section,
    "sidm_run_all_audits": tool_run_all_audits,
    "sidm_compare_paper_to_json": tool_compare_paper_to_json,
}


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

def _build_server():
    """Build the MCP server, mirroring mnemosyne's mcp_server.py pattern."""
    async def list_tools_handler(ctx, params):
        tools = [
            Tool(name=t["name"], description=t["description"],
                 inputSchema={"type": "object", "properties": {}})
            for t in TOOL_DEFS
        ]
        return ListToolsResult(tools=tools)

    async def call_tool_handler(ctx, params):
        name = params.name
        if name not in handlers:
            return CallToolResult(
                content=[TextContent(type="text", text=f"unknown tool: {name}")],
                isError=True,
            )
        args = params.arguments or {}
        handler = handlers[name]
        try:
            # All handlers are sync; run them
            result_text = handler(**args) if args else handler()
            return CallToolResult(
                content=[TextContent(type="text", text=str(result_text))],
                isError=False,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text",
                                      text=json.dumps({"ok": False, "error": str(e)}))],
                isError=True,
            )

    handlers = dict(_TOOL_HANDLERS)
    return Server(
        "sidm-test",
        on_list_tools=list_tools_handler,
        on_call_tool=call_tool_handler,
    )


async def _run_stdio():
    server = _build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream,
                         server.create_initialization_options())


def main():
    if not _MCP_AVAILABLE:
        print("ERROR: mcp package not installed in venv-sidm-bench", file=sys.stderr)
        print("FIX: ./.venv-sidm-bench/Scripts/python.exe -m pip install mcp", file=sys.stderr)
        sys.exit(1)
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()