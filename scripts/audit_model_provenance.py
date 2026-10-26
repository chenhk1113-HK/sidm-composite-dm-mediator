#!/usr/bin/env python3
"""
audit_model_provenance.py — Gate layer 9: model/provider provenance of the
reports' self-description.

WHY THIS EXISTS
---------------
The consolidated report's section 19 describes HOW the n20 verification was
run. Its first draft made five claims about that run, and the agent log
disproved every one:

  1. "a *different* model family (deepseek-v4.1-flash, not the Nemotron used
     for the n18/n19 audits)" - the delegation was DISPATCHED on Nemotron and
     fell back twice to deepseek-v4.1-flash, and the n19 and third-pass audits
     ran on that SAME effective model. Not deliberate, and not different.
  2. "edited no files" - it wrote three throwaway scripts in the scratch dir.
  3. "28 tool calls" - 28 was the terminal-call count; the real total was 39
     tool invocations across 3 tools, over 27 API calls.
  4. "a 16B-class dense model" - it is a 552B MoE with 8B/16B active.
  5. (plus two dangling section anchors - layer 8's job.)

None of the existing 7 gate layers can catch any of this: they validate the
PAPER against the CODE. The report's account of its own verification is a
prose claim about an execution, and prose claims about executions are exactly
what this layer checks.

WHAT THIS LAYER CHECKS
----------------------
For each delegation the deliverables reference by id, this layer reads the
ON-DISK EVIDENCE - the delegation manifest and the agent log - and checks
the deliverables' claims against it:

  dispatch model / provider   manifest `model` + `provider`
  effective model / provider  the task-level `model` in the manifest
  fallback chain              "Fallback activated" lines in the agent log
  API call count              "API call #N:" lines for that session id
  tool invocation count       tool lines in the delegation's live transcript

It then greps the deliverables for the specific CLAIM PATTERNS that were
wrong, and fails if a prohibited phrasing is present:

  * a model described as belonging to a "different model family" when the
    manifest shows the same effective model as another referenced delegation
  * a "N tool calls" / "N API calls" figure that disagrees with the log
  * "edited no files" where the transcript shows a write
  * a parameter-count description that contradicts the model's card facts

The layer also enforces a hard rule learned from this episode: a report may
NOT assert model independence unless the manifests prove it.

EVIDENCE SOURCES
----------------
  manifest : <hermes home>/cache/delegation/live/<id>/manifest.json
  log      : <hermes home>/logs/agent.log
  transcript: the manifest's per-task `log` path

If the evidence for a referenced delegation is absent (cache pruned, log
rotated), the layer reports UNVERIFIABLE for that delegation rather than
silently passing it. Unverifiable is reported as a FAIL by default because a
provenance claim that cannot be checked is exactly the failure mode this
layer exists to prevent; --allow-unverifiable downgrades it to a warning.

Usage:
    python scripts/audit_model_provenance.py
    python scripts/audit_model_provenance.py --json
    python scripts/audit_model_provenance.py --allow-unverifiable

Exit: 0 = every provenance claim checked and consistent; 1 = a claim is
contradicted by the evidence, or a claim is unverifiable (without the flag).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs" / "dual_review_5loop"
REPORT = DOCS / "SIDM_ROUND5_CONSOLIDATED_FIXES_v1.10_2026-10-26.md"
COMPANION = DOCS / "SIDM_ROUND5_CHANGED_CODE_v1.8_2026-10-26.md"

# ---------------------------------------------------------------- hermes home
def hermes_home():
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    return Path.home() / "AppData" / "Local" / "hermes"

HERMES = hermes_home()
LIVE_DIR = HERMES / "cache" / "delegation" / "live"
AGENT_LOG = HERMES / "logs" / "agent.log"

DELEGATION_ID_RE = re.compile(r"\bdeleg_([0-9a-f]{8})\b")
API_CALL_RE = re.compile(
    r"\[([0-9]{8}_[0-9]{6}_[0-9a-f]+)\].*?API call #(\d+): model=(\S+) provider=(\S+)")
FALLBACK_RE = re.compile(
    r"\[([0-9]{8}_[0-9]{6}_[0-9a-f]+)\].*?Fallback activated: (.+?)\s*$")
TOOL_LINE_RE = re.compile(r"^\d\d:\d\d:\d\d tool\s+\| -> (\w+)\(")

# Claims that must never appear unless the evidence supports them.
# Each entry: (regex, description). Matched case-insensitively.
PROHIBITED_CLAIM_PATTERNS = [
    (r"different model famil", "asserts model-family independence"),
    (r"not the Nemotron used for", "asserts a different model from earlier audits"),
    (r"\bedited no files\b", "claims zero file writes"),
    (r"\b16B-class dense\b", "misstates the model architecture"),
    (r"\b28 tool calls\b", "quotes the terminal-only count as the total"),
]

# A CORRECTION CONTEXT marks the prohibited phrasing as a QUOTATION of the
# error rather than a fresh assertion of it. The deliverables quote their own
# earlier wrong wording in order to say it was wrong - "so §19's 'a *different*
# model family' was wrong twice over" - and that is the opposite of a live
# false claim.
#
# Without this, the layer would flag the very corrections it exists to
# protect, and a gate that fires on its own fix notes gets disabled.
CORRECTION_CONTEXT_RE = re.compile(
    r"was wrong"
    r"|were wrong"
    r"|wrong twice"
    r"|corrected"
    r"|corrects"
    r"|correction"
    r"|not deliberate"
    r"|not different"
    r"|rather than"
    r"|misstate"
    r"|mislabelled"
    r"|that was wrong"
    r"|superseded"
    r"|is wrong"
    r"|was a mistake"
    r"|instead of"
    r"|not the terminal-only",
    re.IGNORECASE,
)

# A paragraph that DISCUSSES the verification run is the subject of the
# provenance claims this layer checks. Paragraphs that merely mention model
# families in another context (the companion's reviewer-block, for instance)
# are out of scope.
SUBJECT_MARKER_RE = re.compile(
    r"the verifier"
    r"|the verification"
    r"|the n20 (verification|response|adjudication)"
    r"|the earlier audits"
    r"|the n19 and third-pass"
    r"|deleg_[0-9a-f]{8}"
    r"|§19"
    r"|§10\b"
    r"|the provenance claims",
    re.IGNORECASE,
)

# Facts about the effective model that the deliverables are allowed to state.
# Keyed by the model id; a claim that contradicts these is a failure.
MODEL_FACTS = {
    "deepseek-ai/deepseek-v4.1-flash": {
        "family": "MoE",
        "total_params": 552,
        "active_prefill": 8,
        "active_decode": 16,
    },
    "nvidia/nemotron-3-ultra-550b-a55b:free": {
        "family": "MoE",
        "total_params": 550,
        "active_prefill": 53,
        "active_decode": 53,
    },
}

# Claims about a count that the log can decide.
COUNT_CLAIM_RES = [
    (re.compile(r"(\d+)\s+API calls?"), "api_calls"),
    (re.compile(r"(\d+)\s+tool invocations?"), "tool_invocations"),
    (re.compile(r"(\d+)\s+tool calls?"), "tool_invocations"),
]


def load_delegations():
    """Return {deleg_id: manifest_dict} for every cached delegation."""
    out = {}
    if not LIVE_DIR.exists():
        return out
    for d in sorted(LIVE_DIR.iterdir()):
        mf = d / "manifest.json"
        if not mf.exists():
            continue
        try:
            out[d.name] = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def load_agent_log():
    """Return (api_calls_by_session, fallbacks_by_session).

    api_calls_by_session: {session_id: {model, provider, n_calls}}
    fallbacks_by_session: {session_id: [chain strings]}
    """
    api = {}
    fb = {}
    if not AGENT_LOG.exists():
        return api, fb
    try:
        with AGENT_LOG.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "API call #" in line:
                    m = API_CALL_RE.search(line)
                    if m:
                        sid, num, model, provider = m.groups()
                        rec = api.setdefault(sid, {"models": set(),
                                                   "providers": set(),
                                                   "n_calls": 0})
                        rec["models"].add(model)
                        rec["providers"].add(provider)
                        rec["n_calls"] = max(rec["n_calls"], int(num))
                elif "Fallback activated" in line:
                    m = FALLBACK_RE.search(line)
                    if m:
                        fb.setdefault(m.group(1), []).append(m.group(2))
    except OSError:
        pass
    return api, fb


def tool_counts(transcript_path):
    """Count tool invocations by tool name in a delegation transcript."""
    counts = {}
    if not transcript_path or not Path(transcript_path).exists():
        return None, 0
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = TOOL_LINE_RE.match(line)
                if m:
                    counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    except OSError:
        return None, 0
    return counts, sum(counts.values())


def session_for_delegation(manifest, api):
    """Find the agent-log session id belonging to a delegation.

    The manifest records the delegation's start time; the agent log's session
    ids begin with YYYYMMDD_HHMMSS. So the delegation's own session is the one
    whose id starts with the manifest's start timestamp.

    That is the PRIMARY method, and it is primary for a reason: the
    model-matching fallback picks the WRONG session whenever several
    delegations ran the same model on the same day. On 2026-10-26 three
    delegations ran deepseek-v4.1-flash within three hours, and matching by
    model returned the PARENT session (380 API calls) for two of them - a
    100x error in the reported count, and exactly the kind of confidently
    wrong number this layer exists to prevent.
    """
    started = manifest.get("started")
    if started:
        import datetime as _dt
        try:
            t0 = _dt.datetime.strptime(started, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            t0 = None
        if t0 is not None:
            near = []
            for sid in api:
                try:
                    ts = _dt.datetime.strptime(sid[:15], "%Y%m%d_%H%M%S")
                except ValueError:
                    continue
                delta = abs((ts - t0).total_seconds())
                # The manifest's `started` and the log's session id can differ
                # by a second or two (clock rounding at the dispatch
                # boundary), so the window is a few seconds, not exact.
                if delta <= 5:
                    near.append((delta, sid))
            if near:
                near.sort()
                sids = [s for _, s in near]
                # Several delegations can share a start second (a fan-out).
                return sids if len(sids) > 1 else sids[0]
    # Fallback: match by the effective model. Only reached when the
    # timestamp does not match any session (e.g. the log was rotated).
    want = {t.get("model") for t in manifest.get("tasks", []) if t.get("model")}
    best, best_n = None, 0
    for sid, rec in api.items():
        if want and want & rec["models"]:
            if rec["n_calls"] > best_n:
                best, best_n = sid, rec["n_calls"]
    return best


def iter_sections(text):
    """Yield (section_name, body) for every '## N. Title' section.

    The section name is the heading text; the body is everything up to the
    next heading of the same or higher level. Used to attribute a numeric
    claim to the delegation that section is about.
    """
    lines = text.split("\n")
    starts = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{2,4})\s+(.+?)\s*$", line)
        if m:
            starts.append((i, len(m.group(1)), m.group(2)))
    for idx, (i, level, name) in enumerate(starts):
        end = len(lines)
        for j, lvl2, _ in starts[idx + 1:]:
            if lvl2 <= level:
                end = j
                break
        yield name, "\n".join(lines[i + 1:end])


def deliverable_texts():
    out = []
    for label, path in (("report", REPORT), ("companion", COMPANION)):
        if path.exists():
            out.append((label, path.read_text(encoding="utf-8")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-unverifiable", action="store_true",
                    help="downgrade unverifiable provenance claims to a warning")
    args = ap.parse_args()

    mans = load_delegations()
    api, fb = load_agent_log()
    docs = deliverable_texts()

    referenced = set()
    for _, text in docs:
        referenced.update(f"deleg_{m}" for m in DELEGATION_ID_RE.findall(text))

    findings = []
    unverifiable = []
    evidence = {}

    # ---- per-delegation evidence ------------------------------------------
    for did in sorted(referenced):
        man = mans.get(did)
        if man is None:
            unverifiable.append((did, "manifest not found in the delegation cache"))
            continue
        task_models = [t.get("model") for t in man.get("tasks", []) if t.get("model")]
        sid = session_for_delegation(man, api)
        sids = sid if isinstance(sid, list) else ([sid] if sid else [])
        recs = [api[s] for s in sids if s in api]
        # A fan-out delegation has one session per task; the delegation's
        # API-call count is the sum over its sessions, and its tool count is
        # the sum over its task transcripts.
        api_calls = sum(r["n_calls"] for r in recs) if recs else None
        api_models = sorted({m for r in recs for m in r["models"]})
        api_providers = sorted({pr for r in recs for pr in r["providers"]})
        chains = []
        for s in sids:
            chains.extend(fb.get(s, []))
        # de-duplicate the chains while preserving order
        seen, fallbacks = set(), []
        for c in chains:
            if c not in seen:
                seen.add(c)
                fallbacks.append(c)
        tools, tool_total = {}, 0
        for t in man.get("tasks", []):
            c, n = tool_counts(t.get("log"))
            if c is None:
                continue
            for k, v in c.items():
                tools[k] = tools.get(k, 0) + v
            tool_total += n
        evidence[did] = {
            "dispatch_model": man.get("model"),
            "dispatch_provider": man.get("provider"),
            "effective_models": task_models,
            "session_id": sids[0] if len(sids) == 1 else sids,
            "api_calls": api_calls,
            "api_models": api_models,
            "api_providers": api_providers,
            "fallbacks": fallbacks,
            "tool_counts": tools,
            "tool_total": tool_total or None,
        }

    # ---- claim consistency ------------------------------------------------
    for did, ev in evidence.items():
        eff = set(ev["effective_models"])
        if not eff:
            unverifiable.append((did, "manifest carries no task-level model"))
            continue
        for other_id, other_ev in evidence.items():
            if other_id == did:
                continue
            if eff & set(other_ev["effective_models"]):
                # Same effective model -> the deliverables must NOT claim a
                # different family between them.
                for label, text in docs:
                    for m in re.finditer(
                            r"[^.\n]{0,140}deleg_" + did[6:] + r"[^.\n]{0,140}",
                            text):
                        seg = m.group(0)
                        if other_id not in seg:
                            continue
                        for pat, desc in PROHIBITED_CLAIM_PATTERNS:
                            if re.search(pat, seg, re.IGNORECASE):
                                findings.append(
                                    (did, other_id, label, desc, seg.strip()[:150]))
        # Count claims. A count is attributed to a delegation by the
        # SECTION it appears in: the section names the delegation (the
        # report's §19 names it in its prose), and the number inside that
        # section describes that delegation's run.
        #
        # Scoping to the sentence alone was too narrow - the call-count
        # sentence says "It ran 27 API calls" without repeating the
        # delegation id - and scoping to the whole document was too broad,
        # because it would compare every count against every delegation.
        for label, text in docs:
            for sec_name, sec_body in iter_sections(text):
                named = [d for d in referenced
                         if d in sec_body or d[6:] in sec_body]
                if did not in named:
                    continue
                candidates = []
                for d in named:
                    if d in evidence:
                        candidates.append({
                            "id": d,
                            "api_calls": evidence[d]["api_calls"],
                            "tool_invocations": evidence[d]["tool_total"],
                        })
                for rx, kind in COUNT_CLAIM_RES:
                    for cm in rx.finditer(sec_body):
                        n = int(cm.group(1))
                        actual = (ev["api_calls"] if kind == "api_calls"
                                  else ev["tool_total"])
                        if actual is None:
                            continue
                        # The count is checked against EVERY delegation the
                        # section mentions. A section that describes one run
                        # but names several delegations (as §19 does) is only
                        # contradicted if NO candidate agrees - otherwise the
                        # count belongs to the one it does describe.
                        if any(cand[kind] == n for cand in candidates
                               if cand.get(kind) is not None):
                            continue
                        findings.append(
                            (did, None, label,
                             f"claims {n} {kind.replace('_', ' ')} in "
                             f"{sec_name}; the log/transcript show "
                             + ", ".join(
                                 f"{c.get(kind)}" for c in candidates
                                 if c.get(kind) is not None),
                             sec_body.strip()[:150]))

    # ---- model-family independence assertions -----------------------------
    # If the deliverables claim two delegations ran on different families,
    # that claim must be TRUE for at least one pair.
    distinct_pairs = set()
    for a_id, a_ev in evidence.items():
        for b_id, b_ev in evidence.items():
            if a_id >= b_id:
                continue
            if not (set(a_ev["effective_models"]) & set(b_ev["effective_models"])):
                distinct_pairs.add((a_id, b_id))

    prohibited_hits = []
    for label, text in docs:
        # Scope each check to the paragraph that discusses the VERIFICATION.
        # "different model family" is legitimate elsewhere in these documents:
        # the companion's reviewer-block says the second reviewer used a
        # different model family from the OpenCode-side reviewer, which is a
        # true statement about a DIFFERENT pair of agents. The prohibited
        # claim is specifically that the n20-verification delegation was
        # independent of the earlier audits by model family.
        for para in re.split(r"\n\s*\n", text):
            if not SUBJECT_MARKER_RE.search(para):
                continue
            # The correction-context test is applied PER SENTENCE, not to a
            # character window around the match. A window bleeds into the
            # neighbouring sentence, so a live false claim sitting one
            # sentence away from a correction note was silently exempted -
            # which is how this layer passed its own mutation test.
            for sent in re.findall(r"[^.\n]*\.[^.\n]*", para):
                for pat, desc in PROHIBITED_CLAIM_PATTERNS:
                    for m in re.finditer(pat, sent, re.IGNORECASE):
                        ctx = sent.strip().replace("\n", " ")
                        prohibited_hits.append((label, desc, m.group(0), ctx))

    # A prohibited phrasing is a failure only when the evidence contradicts it
    # AND the text is ASSERTING it rather than quoting it in order to correct
    # it. Two independent exemptions, both required to be evidenced:
    #   (a) correction context - the phrasing appears inside a sentence that
    #       says it was wrong. This is how the deliverables quote their own
    #       earlier wording to correct it.
    #   (b) genuine model independence - two referenced delegations really did
    #       run on different models, so the claim is true.
    for label, desc, matched, ctx in prohibited_hits:
        if CORRECTION_CONTEXT_RE.search(ctx):
            continue
        if desc.startswith("asserts model-family") or desc.startswith("asserts a different model"):
            ok = False
            for a_id, b_id in distinct_pairs:
                if a_id[6:] in ctx and b_id[6:] in ctx:
                    ok = True
                    break
            if ok:
                continue
        findings.append((None, None, label, f"prohibited phrasing: {desc}", ctx[:170]))

    # ---- architecture claims vs MODEL_FACTS --------------------------------
    for label, text in docs:
        # Attribute each parameter figure to the model named in the SAME
        # sentence. A window-based attribution picks up the wrong model
        # whenever one sentence discusses two of them, which is exactly what
        # the deliverables' §19 does.
        for sent_m in re.finditer(r"[^.\n]*\.[^.\n]*", text):
            sent = sent_m.group(0)
            ids = [mid for mid in MODEL_FACTS if mid in sent]
            if len(ids) != 1:
                continue
            model_id = ids[0]
            facts = MODEL_FACTS[model_id]
            for m in re.finditer(r"(\d+)\s*B\b", sent):
                stated = int(m.group(1))
                if stated in (facts["total_params"], facts["active_decode"],
                              facts["active_prefill"]):
                    continue
                findings.append(
                    (None, None, label,
                     f"states {stated}B for {model_id} "
                     f"(card: {facts['total_params']}B total, "
                     f"{facts['active_prefill']}B prefill / "
                     f"{facts['active_decode']}B decode active)",
                     sent.strip()[:170]))

    ok = (not findings) and (not unverifiable or args.allow_unverifiable)

    if args.json:
        print(json.dumps({
            "referenced_delegations": sorted(referenced),
            "evidence": evidence,
            "findings": findings,
            "unverifiable": unverifiable,
            "distinct_model_pairs": sorted(distinct_pairs),
            "result": "PASS" if ok else "FAIL",
        }, indent=2, default=str))
        return 0 if ok else 1

    print("=" * 74)
    print("MODEL-PROVENANCE AUDIT (gate layer 9)")
    print("=" * 74)
    print(f"Hermes home : {HERMES}")
    print(f"Agent log   : {AGENT_LOG} "
          f"({'present' if AGENT_LOG.exists() else 'ABSENT'})")
    print(f"Delegations referenced by the deliverables: {len(referenced)}")
    print()
    for did in sorted(referenced):
        ev = evidence.get(did)
        if ev is None:
            print(f"  {did}: UNVERIFIABLE")
            continue
        print(f"  {did}")
        print(f"     dispatch : {ev['dispatch_model']} ({ev['dispatch_provider']})")
        print(f"     effective: {ev['effective_models']}")
        print(f"     session  : {ev['session_id']}  "
              f"api_calls={ev['api_calls']}  tool_total={ev['tool_total']}")
        if ev["tool_counts"]:
            print(f"     tools    : {ev['tool_counts']}")
        for chain in ev["fallbacks"]:
            print(f"     fallback : {chain}")
    print()

    if unverifiable:
        print("-" * 74)
        print("UNVERIFIABLE provenance claims (evidence absent - a claim that "
              "cannot be checked is the failure mode this layer prevents):")
        print("-" * 74)
        for did, why in unverifiable:
            print(f"  {did}: {why}")
        print()

    if findings:
        print("-" * 74)
        print(f"CONTRADICTED provenance claims ({len(findings)}):")
        print("-" * 74)
        for did, other, label, desc, ctx in findings:
            who = did or "—"
            print(f"  [{label}] {who}: {desc}")
            print(f"      {ctx[:150]}")
        print()
        print("RESULT: FAIL")
        return 1

    if unverifiable and not args.allow_unverifiable:
        print("RESULT: FAIL (unverifiable provenance claims; rerun with "
              "--allow-unverifiable to downgrade)")
        return 1

    print("OK: every provenance claim in the deliverables is consistent with "
          "the manifests,\nthe agent log, and the delegation transcripts.")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
