r"""Producer for v0.3-prelim/data/results/fH_pairing_registry.json (finding F26).

Why this generator exists: the earlier registry was a by-product of a mutating helper — it recorded
a module as archived-pair when the helper found a live-looking import to pin. After the rename pass
those imports no longer exist, so the registry lost 15 genuinely archived-pair modules. A registry
that states intent must be derived from what the source says now.

Scope discipline (an earlier version of this generator over-counted 73 modules by treating any
hardcoded 0.297/174.0 as a pairing contract):
  * the PAIRING CONTRACT is what a module imports from scripts/constants.py or
    scripts/canonical_numbers.py — that is the choice it publishes, and it is testable;
  * a module that hardcodes archived numbers without importing them is listed as a disclosure, not
    as a contract holder;
  * tests legitimately reference both pairs and are excluded from the contract buckets.

Usage:
    python scripts/fH_pairing_registry.py            # regenerate the registry
    python scripts/fH_pairing_registry.py --check    # rebuild and compare against the file
"""
import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]  # repo root, independent of CWD
SKIP_DIRS = {".git", ".venv-sidm-bench", "__pycache__", "scratch", "archive", "deprecated"}
ARCHIVED_MARKERS = ("LEGACY_PAIR", "_ARCHIVED", "F_H_LEGACY", "F_H_PLACEHOLDER_G7", "ARCHIVED_PAIR")
# Only these names are pairing commitments. Literature f_H scenarios (F_H_YANG_PLUS_LOW,
# F_H_T202_NBODY, ...) are separate physical hypotheses, not the project's amplitude pairing, and
# invariant knobs (A_SLOPE, V_TARGET_KMS, M_CHI_GEV) carry no pairing at all — a classifier that
# counts them produces a registry full of false "mixed" modules.
LIVE_PAIRING_NAMES = {
    "SIGMA_0_CM2_PER_G", "SIGMA_PEAK_CM2_PER_G", "F_H", "F_H_CANONICAL",
    "SIGMA_EFF_CM2_PER_G_AT_CLOUD9", "PAIRING_SIGMA_EFF_PEAK_CM2_PER_G",
}
SOURCE_MODULE_STEMS = {"constants", "canonical_numbers"}  # import stems
SOURCE_MODULE_FILES = {"constants.py", "canonical_numbers.py"}  # the modules that define both pairs
ARCHIVED_LITERALS = {"0.297", "174.0", "0.052", "0.088209"}

CANONICAL_PAIR_VALUES = {
    "f_H": 0.7501856343179664, "sigma_0_cm2_per_g": 0.008150396851725193,
    "sigma_peak_cm2_per_g": 27.272481773080454,
}
ARCHIVED_PAIR_VALUES = {"f_H": 0.297, "sigma_0_cm2_per_g": 0.052, "sigma_peak_cm2_per_g": 174.0}
PAIRING_RULE = (
    "Every module publishes exactly one pairing through what it imports. An archived-pair module "
    "binds archived-looking names and carries the '# PAIRING: ARCHIVED PAIR' declaration; a "
    "canonical-pair module imports the live amplitudes with f_H = 0.7501856343179664. "
    "sigma_eff = f_H^2 * sigma/m is identical between the pairs, so the choice decides which "
    "number is the particle-level cross section, not any halo-level prediction.")


def scan():
    contract = {"canonical_pair_modules": [], "archived_pair_modules": [], "mixed_pair_modules": []}
    hardcoded, undeclared = [], []
    for path in sorted(REPO.rglob("*.py")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        if path.name in SOURCE_MODULE_FILES:
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue
        live, archived, hardcoded_lits = set(), set(), set()
        for node in ast.walk(tree):
            bound = []
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[-1] in SOURCE_MODULE_STEMS:
                bound = [a.asname or a.name for a in node.names]
            elif isinstance(node, ast.Assign):
                bound = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if isinstance(node.value, ast.Constant) and str(node.value.value) in ARCHIVED_LITERALS:
                    hardcoded_lits.update(bound)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # A default argument is a pairing commitment made at def time: it binds whichever
                # pairing was live when the module was written, and a later flip changes behaviour
                # without touching the call site. scripts/constants.py's own
                # g_chi_from_sigma_peak(sigma_peak=SIGMA_PEAK_CM2_PER_G) is the canonical example.
                defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d]
                bound = [d.id for d in defaults if isinstance(d, ast.Name)]
            for name in bound:
                if "NUISANCE" in name:
                    continue  # a deliberately-zeroed nuisance knob is not a pairing commitment
                if any(m in name for m in ARCHIVED_MARKERS):
                    archived.add(name)
                elif name in LIVE_PAIRING_NAMES:
                    live.add(name)
        is_test = "/tests/" in rel or path.name.startswith("test_")
        declares = "PAIRING: ARCHIVED PAIR" in source
        if archived and live:
            # A test may reference both pairs on purpose; a producer may not.
            if not is_test:
                contract["mixed_pair_modules"].append(rel)
        elif archived:
            contract["archived_pair_modules"].append(rel)
            if not declares and not is_test:
                undeclared.append(rel)
        elif live and not is_test:
            contract["canonical_pair_modules"].append(rel)
        if hardcoded_lits and not archived and not live and not is_test and not declares:
            hardcoded.append({"module": rel, "names": sorted(hardcoded_lits)})

    out = dict(contract)
    out["archived_contract_modules_missing_declaration"] = undeclared
    out["hardcoded_archived_literals_no_contract"] = hardcoded
    out["counts"] = {k: len(v) for k, v in out.items() if k.endswith(("modules", "declaration"))}
    out["canonical_pair_values"] = CANONICAL_PAIR_VALUES
    out["archived_pair_values"] = ARCHIVED_PAIR_VALUES
    out["pairing_k_legacy_to_canonical"] = 0.15673840099471523
    out["pairing_rule"] = PAIRING_RULE
    return out


def main():
    out = scan()
    target = REPO / "v0.3-prelim" / "data" / "results" / "fH_pairing_registry.json"
    if "--check" in sys.argv:
        stored = json.loads(target.read_text(encoding="utf-8"))
        for key in ("canonical_pair_modules", "archived_pair_modules", "mixed_pair_modules",
                    "archived_contract_modules_missing_declaration"):
            if sorted(stored.get(key, [])) != sorted(out[key]):
                added = sorted(set(out[key]) - set(stored.get(key, [])))
                dropped = sorted(set(stored.get(key, [])) - set(out[key]))
                raise SystemExit(f"registry stale in {key}: +{added} -{dropped}")
        print("registry matches the current source state")
        return
    out["generated_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(out["counts"], indent=1))
    print("MIXED (defect):", out["mixed_pair_modules"])
    print("ARCHIVED WITHOUT DECLARATION (defect):", out["archived_contract_modules_missing_declaration"])
    print("hardcoded-literal disclosures:", len(out["hardcoded_archived_literals_no_contract"]))
    print("registry ->", target)


if __name__ == "__main__":
    main()
