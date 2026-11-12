#!/usr/bin/env python3
"""Seed-and-interval audit (ReviewResponse round, 2026-11-11).

Question this answers: for every stored result, is the number reproducible (is the seed in the
artifact?) and is it falsifiable (is there an interval for the sampled quantity?).

Scope is deliberately limited to STOCHASTIC artifacts - files that present output of a sampler, a
Monte Carlo, a bootstrap, an N-body run or a random initialisation. An analytic derivation with no
random numbers does not need a seed, and demanding one there trains people to write filler.
Detection is structural (sampler-shaped keys, or sampler-naming text in a method-like field), not
"the word posterior appears somewhere in the blob": the first version of this audit false-flagged a
path inventory and a bound re-derivation exactly that way.

Dating: the forward rule is applied to the run date, in this order of trust
  1. an explicit date recorded inside the artifact (date / run_date / completed_at / ...),
  2. the last git commit that touched the file (when git is available and the file is tracked),
  3. the filesystem mtime, labelled as weak evidence.
Filesystem mtime alone is NOT trustworthy here: a `git checkout` refreshed nine artifacts' mtimes
to 2026-11-11 while their contents were unchanged since 2026-11-05/06, which would have wrongly
condemned them.

Two verdicts:
  * LEGACY GAP (informational): stochastic artifacts dated before repro_contract.CONDUCT_DATE
    that lack a seed and/or an interval. Their intervals cannot be recovered - the chain was never
    stored - so they are reported, not rewritten.
  * FORWARD RULE (fail closed): any stochastic artifact dated on or after CONDUCT_DATE must
    record a seed and an interval.

Integrity findings (a stored artifact that cannot even be parsed) fail closed too. Known, disclosed
cases sit in CORRUPT_ALLOWLIST with a reason, in the style of the phantom-file allowlists elsewhere
in this repo: printed on every run, never silently skipped.

Writes docs/evidence/seed_interval_inventory.json. Run:
    python scripts/seed_interval_audit.py [--json]
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
sys.path.insert(0, str(paths.CODE_DIR))
from repro_contract import CONDUCT_DATE  # noqa: E402

SEED_KEYS = {"seed", "rng_seed", "random_seed", "numpy_seed", "seed_value", "rng_seed_master"}

# An interval is anything that brackets a sampled number. Bookkeeping keys are excluded so that
# "elapsed_s" or "n_steps" can never pass as an uncertainty.
INTERVAL_KEY_RE = re.compile(
    r"(credible|interval|percentile|_q(0?2|05|16|50|84|95)$|^(q0?2|q05|q16|q50|q84|q95)|"
    r"ci_low|ci_high|upper_limit|lower_limit|confiden|\berror\b|_err$|_sigma$)",
    re.IGNORECASE,
)
NON_INTERVAL_KEYS_RE = re.compile(
    r"elapsed|runtime|wall|duration|timestamp|_at$|^date|n_steps|n_walkers|n_burn|nlive|"
    r"acceptance|autocorr|convergence|n_samples",
    re.IGNORECASE,
)

# Structural evidence that a file is the output of a stochastic run.
SAMPLER_KEY_RE = re.compile(
    r"^(n_?walkers?|walkers|n_?steps|n_?burn|burn_?in|nlive|n_?live_points|n_?live|"
    r"n_?chains?|n_?draws|n_?samples|acceptance|chain|logz|log_?z|log_?Z|posterior_|prior_|"
    r"ese|ess|sampler|ensemble|resampl|tau|n_?body|simulation_|simulat|nbody|monte_?carlo|"
    r"bootstrap|replica|seed)",
    re.IGNORECASE,
)
# Only these fields' text counts as evidence of a sampling method. A filename mentioned inside a
# path inventory is evidence of nothing.
METHOD_VALUE_KEYS = {
    "method", "description", "purpose", "sampler", "tool", "algorithm", "pipeline",
    "notes", "note", "summary", "run_type", "engine", "kind_of_run", "code",
}
SAMPLER_TEXT_RE = re.compile(
    r"emcee|dynesty|nested sampl|mcmc|markov|walker|nlive|monte.?carlo|bootstrap|"
    r"default_rng|burn.?in|sampler|resampl|n-body|n_body|chain samples",
    re.IGNORECASE,
)

DATE_KEY_RE = re.compile(r"^(date|run_date|completed_at|recorded_at|generated_at|created_at|"
                         r"finished_at|timestamp|run_at|written_at)$", re.IGNORECASE)
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Files that live in data/results but are inventories/registries rather than run output. Disclosed:
# adding a name requires a reason, and the audit prints the list on every run.
NON_RESULT_ALLOWLIST = {
    "cg16_host_path_inventory.json":
        "CG-16 path inventory (docs artifact): lists file paths, stores no sampled quantity",
    "standing_numbers.json":
        "registry of canonical values, not the output of a stochastic run",
}

# Known-truncated / unparseable artifacts, disclosed so the forward rule stays enforceable.
CORRUPT_ALLOWLIST = {
    "amuse_focused_rerun_with_sashimi_2026_09_12.json":
        "truncated at 203,917 bytes mid-value (ends at '\"core_collapsed\":'); the AMUSE benchmark "
        "writer cut the file off. Archived 2026-11-12 to "
        "v0.3-prelim/data/results/_archive_amuse_20261112/ (branch dropped 2026-11-11; no AMUSE "
        "number is cited anywhere). Entry retained so the disclosure stays on the record.",
}


def walk(obj, prefix=""):
    """Yield (key, value, path) for every dict key anywhere in a JSON tree."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v, f"{prefix}/{k}"
            yield from walk(v, f"{prefix}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{prefix}[{i}]")


def has_seed(payload) -> bool:
    return any(k in SEED_KEYS for k, _v, _p in walk(payload))


def has_interval(payload) -> bool:
    for k, _v, _p in walk(payload):
        if NON_INTERVAL_KEYS_RE.search(k):
            continue
        if INTERVAL_KEY_RE.search(k):
            return True
    return False


def looks_stochastic(payload) -> bool:
    for k, v, _p in walk(payload):
        if SAMPLER_KEY_RE.search(k):
            return True
        if k in METHOD_VALUE_KEYS and isinstance(v, str) and SAMPLER_TEXT_RE.search(v):
            return True
    return False


def walk_dates(payload):
    out = []
    for k, v, _p in walk(payload):
        if DATE_KEY_RE.search(k) and isinstance(v, str):
            m = ISO_RE.search(v)
            if m:
                try:
                    out.append(dt.date.fromisoformat(m.group(0)))
                except ValueError:
                    pass
    return out


def git_dates_for_results(results_dir: Path) -> dict:
    """file name -> last commit date, from one git traversal ({} when git is unavailable)."""
    try:
        proc = subprocess.run(
            ["git", "log", "--no-color", "--date=short", "--name-only",
             "--pretty=format:@%cd", "--", str(results_dir)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=180, cwd=str(paths.REPO_ROOT),
        )
    except Exception:
        return {}
    if proc.returncode != 0:
        return {}
    out, current = {}, None
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("@"):
            try:
                current = dt.date.fromisoformat(line[1:].strip())
            except ValueError:
                current = None
        elif line and current is not None:
            out.setdefault(Path(line.replace("\\", "/")).name, current)  # newest-first: first hit wins
    return out


def main() -> int:
    results_dir = Path(paths.RESULTS_DIR)
    files = sorted(p for p in results_dir.glob("*.json") if p.is_file())
    conduct = dt.date.fromisoformat(CONDUCT_DATE)
    commits = git_dates_for_results(results_dir)

    counts = {"total": 0, "stochastic": 0, "seed": 0, "interval": 0, "both": 0,
              "legacy_gap": 0, "forward_violation": 0, "allowlisted_nonresult": 0,
              "corrupt": 0, "corrupt_allowlisted": 0, "date_from_artifact": 0,
              "date_from_git": 0, "date_from_mtime": 0}
    violations, corrupt, rows = [], [], []

    for p in files:
        counts["total"] += 1
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            counts["corrupt"] += 1
            entry = {"file": p.name, "problem": f"unparseable JSON ({type(exc).__name__})",
                     "size_bytes": p.stat().st_size,
                     "allowlisted": p.name in CORRUPT_ALLOWLIST,
                     "reason": CORRUPT_ALLOWLIST.get(p.name, "")}
            corrupt.append(entry)
            if p.name in CORRUPT_ALLOWLIST:
                counts["corrupt_allowlisted"] += 1
            else:
                violations.append({"file": p.name, "problem": entry["problem"]})
            continue

        if p.name in NON_RESULT_ALLOWLIST:
            counts["allowlisted_nonresult"] += 1

        seeded, intervalled = has_seed(payload), has_interval(payload)
        stochastic = looks_stochastic(payload)

        artifact_dates = walk_dates(payload)
        if artifact_dates:
            run_date, basis = max(artifact_dates), "artifact field"
        elif p.name in commits:
            run_date, basis = commits[p.name], "git commit date"
        else:
            run_date = dt.datetime.fromtimestamp(p.stat().st_mtime).date()
            basis = "filesystem mtime (weak evidence)"
        counts[{"artifact field": "date_from_artifact", "git commit date": "date_from_git",
                "filesystem mtime (weak evidence)": "date_from_mtime"}[basis]] += 1

        if seeded:
            counts["seed"] += 1
        if intervalled:
            counts["interval"] += 1
        if seeded and intervalled:
            counts["both"] += 1

        if stochastic and p.name not in NON_RESULT_ALLOWLIST:
            counts["stochastic"] += 1
            if not (seeded and intervalled):
                missing = [what for what, ok in (("seed", seeded), ("interval", intervalled))
                           if not ok]
                if run_date >= conduct:
                    counts["forward_violation"] += 1
                    violations.append({"file": p.name,
                                       "problem": f"stochastic artifact dated {run_date.isoformat()} "
                                                  f"({basis}) missing " + " and ".join(missing)})
                else:
                    counts["legacy_gap"] += 1
            rows.append({"file": p.name, "seed": seeded, "interval": intervalled,
                         "run_date": run_date.isoformat(), "date_basis": basis})

    # Allowlisted corrupt artifacts that have been ARCHIVED (moved out of
    # data/results) stay disclosed: the allowlist entry with its reason is the
    # record, and test_repro_contract asserts the disclosure never disappears.
    scanned_names = {p.name for p in files}
    for name, reason in sorted(CORRUPT_ALLOWLIST.items()):
        if name not in scanned_names:
            corrupt.append({"file": name,
                            "problem": "not present in data/results - archived; "
                                       "disclosure retained",
                            "size_bytes": None,
                            "allowlisted": True,
                            "reason": reason})
            counts["corrupt"] += 1
            counts["corrupt_allowlisted"] += 1

    inventory = {
        "generated_by": "scripts/seed_interval_audit.py",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "conduct_date": CONDUCT_DATE,
        "counts": counts,
        "forward_rule_violations": violations,
        "corrupt_artifacts": corrupt,
        "allowlisted_nonresults": NON_RESULT_ALLOWLIST,
        "legacy_gap_files": [r["file"] for r in rows if not (r["seed"] and r["interval"])],
        "per_stochastic_file": rows,
    }
    evidence_dir = Path(paths.REPO_ROOT) / "docs" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_path = evidence_dir / "seed_interval_inventory.json"
    out_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")

    json_mode = "--json" in sys.argv
    if json_mode:
        print(json.dumps({"counts": counts, "violations": violations,
                          "corrupt": corrupt, "inventory": str(out_path)}))
    else:
        print("=" * 72)
        print("SEED AND INTERVAL AUDIT")
        print("=" * 72)
        print(f"  artifacts scanned:                          {counts['total']}")
        print(f"  allowlisted as non-result:                  {counts['allowlisted_nonresult']}")
        print(f"  stochastic (seed + interval required):      {counts['stochastic']}")
        print(f"  record a seed:                              {counts['seed']}")
        print(f"  record an interval:                         {counts['interval']}")
        print(f"  record both:                                {counts['both']}")
        print(f"  legacy gap (dated before {CONDUCT_DATE}):    {counts['legacy_gap']}")
        print(f"  forward-rule violations:                    {counts['forward_violation']}")
        print(f"  unparseable artifacts:                      {counts['corrupt']} "
              f"(disclosed: {counts['corrupt_allowlisted']})")
        print(f"  run dates from: artifact {counts['date_from_artifact']} / "
              f"git {counts['date_from_git']} / mtime {counts['date_from_mtime']}")
        print(f"  inventory: {out_path}")

    if corrupt and not json_mode:
        print("\nOPEN INTEGRITY FINDING — stored artifacts that cannot be parsed:")
        for c in corrupt:
            flag = "disclosed" if c["allowlisted"] else "NOT DISCLOSED"
            print(f"  ! {c['file']} ({c['size_bytes']} bytes, {flag}): {c['problem']}")
            if c["reason"]:
                print(f"      note: {c['reason']}")

    if violations:
        if not json_mode:
            print("\nFAIL — stochastic artifacts dated on/after the conduct date that skip "
                  "the contract:")
            for v in violations:
                print(f"  ✗ {v['file']}: {v['problem']}")
        return 1
    if [c for c in corrupt if not c["allowlisted"]]:
        if not json_mode:
            print("\nFAIL — unparseable artifacts not disclosed in CORRUPT_ALLOWLIST.")
        return 1
    if not json_mode:
        print(f"\nRESULT: PASS — every stochastic artifact dated on/after {CONDUCT_DATE} records "
              "a seed and an interval; legacy gaps and disclosed defects are listed above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
