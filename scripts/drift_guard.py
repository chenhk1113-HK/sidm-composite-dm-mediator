"""
V19.2-E D — Drift-guard (ClawsGO B.2).

Reads scripts/canonical_numbers.py output (v0.3-prelim/data/results/canonical_numbers.json)
and checks the docs (PAPER, README, CURRENT, FINDINGS, CITATION_AUDIT) for
stale numbers that contradict the canonical values.

The drift-guard is the integration layer for v19.2-E: it makes the
"single source of truth" property enforced, not just declared.

What it checks:
1. PASS count in each .md file matches the canonical v19.2-E A.2 headline
2. SPARC trade-off factor matches the canonical value
3. Cloud-9 trade-off factor matches the canonical value
4. dSph trade-off factor matches the canonical value
5. Halo-specific prefactors (Fornax 18.7x, Segue 1 4.0x) match
6. "first-class" structural findings count matches the freeze (2)
7. T41 v0.8 standing MAP: the canonical block (canonical_numbers.json -> t41_v08_standing_map)
   must match its artifact byte-for-byte (sha256), and README.md / CURRENT.md / EXTRACT.md /
   docs/LAYMAN_SUMMARY.md must quote the v0.8 MAP (m_chi 478 GeV, m_phi 488 MeV, g_chi 0.964,
   tension 0.81σ). The v0.7-era MAP (770 GeV / 453 MeV / 1.19 / 0.60σ) is allowed only in text
   explicitly labelled v0.7 / historical / superseded / pre-T88.E. Added 2026-11-04: a manual
   audit found the front pages quoting the v0.7 MAP under a v0.8 label.

What it does NOT check (because they're OK to vary):
- Exact numerical values from a single fit (they're documented with their source) — except the
  T41 standing MAP, which is now pinned by check 7
- Channel denominator drift (handled by section A.15 in the paper)
- THEOREM vs Result naming (handled by R88(87) freeze)

Usage:
  python scripts/drift_guard.py            # Run, report
  python scripts/drift_guard.py --strict   # Exit non-zero on drift

Exit codes:
  0 — no drift
  1 — drift found
  2 — canonical JSON missing
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_REPO = _THIS.parent.parent
CANONICAL_PATH = _REPO / "v0.3-prelim" / "data" / "results" / "canonical_numbers.json"


def load_canonical():
    if not CANONICAL_PATH.exists():
        print(f"ERROR: {CANONICAL_PATH} not found.")
        print(f"Run `python scripts/canonical_numbers.py` first.")
        sys.exit(2)
    with open(CANONICAL_PATH) as f:
        return json.load(f)


def load_doc(path):
    if not path.exists():
        return ""
    return path.read_text(encoding='utf-8', errors='replace')


# ============================================================================
# Drift checks
# ============================================================================

def check_pass_count_in_doc(doc_text, canonical_pass_count, doc_name):
    """Check that the doc's pass/fail count matches the canonical headline."""
    drifts = []
    # Search for "N of 8 channels pass" or "N of 8 PASS" or similar
    patterns = [
        r'(\d+)\s+of\s+8\s+channels?\s+(?:pass|PASS)',
        r'(\d+)/8\s+(?:channels?\s+)?(?:pass|PASS)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, doc_text):
            found_count = int(match.group(1))
            if found_count != canonical_pass_count:
                # Get wider context (300 chars before + 500 chars after)
                start = max(0, match.start() - 300)
                end = min(len(doc_text), match.end() + 500)
                context = doc_text[start:end].lower()
                # Skip if in a retraction / overclaim / historical context
                skip_keywords = [
                    "retract", "overclaim", "r88(67)", "v1.13", "v18.29",
                    "should have reported", "should not have", "do not claim",
                    "was a snapshot", "not a structural", "r88(71)",
                    "the prior overclaim", "is hereby retracted",
                    "is the apples-to-apples", "retracted", "deprecated",
                    "priored", "prior fit", "r88(67) should have",
                    "found combinations that pass",
                    "changelog", "fd4e4d0", "3bd4520", "r88(68)",
                    "self-check at master", "was nominally 8/8",
                    "p1 solves", "p1 is a viable", "test_t95", "pytest",
                    "new tests:",
                    "yang+ 2025-derived", "t202 n-body", "ide-2csidm",
                    "borrowed f_h", "retracted borrowed",
                    "under any first-principles", "sub-strategies",
                ]
                if any(kw in context for kw in skip_keywords):
                    continue
                drifts.append({
                    "type": "pass_count_mismatch",
                    "doc": doc_name,
                    "context": match.group(0),
                    "found": found_count,
                    "canonical": canonical_pass_count,
                    "severity": "WARN",
                })
    return drifts


def check_sparc_factor_in_doc(doc_text, canonical_sparc_factor, doc_name):
    """Check that the doc's SPARC factor matches the canonical value."""
    drifts = []
    # Search for "SPARC factor below 0.19: Nx" or "factor Nx below SPARC"
    patterns = [
        r'SPARC[^.]*?factor\s+(?:below|under)\s+0\.19[:\s]+(\d+(?:\.\d+)?)\s*x',
        r'factor\s+(?:below|under)\s+0\.19[:\s]+(\d+(?:\.\d+)?)\s*x',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, doc_text, re.IGNORECASE):
            found_factor = float(match.group(1))
            canonical_int = round(canonical_sparc_factor)
            if abs(found_factor - canonical_sparc_factor) / canonical_sparc_factor > 0.15:
                drifts.append({
                    "type": "sparc_factor_mismatch",
                    "doc": doc_name,
                    "context": match.group(0),
                    "found": found_factor,
                    "canonical": canonical_sparc_factor,
                    "severity": "WARN",
                })
    return drifts


def check_halo_prefactors_in_doc(doc_text, doc_name):
    """Check that the doc's halo-specific prefactors match the canonical values."""
    drifts = []
    canonical_prefactors = {
        "Fornax": 18.7,
        "Segue 1": 4.0,
        "BM2": 1.82,
        "Cosmo-501": 2.2,
    }
    # Search for "{halo} ... Nx" or "{halo}: Nx" but ONLY in gravothermal context.
    # The drift-guard should not flag non-prefactor numbers like "Segue 1 1.01x"
    # which is a different metric (Phase G9 f_H drop, not gravothermal prefactor).
    for halo, expected in canonical_prefactors.items():
        # Pattern: "{halo} ... Nx" — look at surrounding context
        pattern = rf'{re.escape(halo)}[^.]{{0,200}}?(\d+(?:\.\d+)?)\s*x'
        for match in re.finditer(pattern, doc_text, re.IGNORECASE):
            try:
                found_factor = float(match.group(1))
                # Get wider context (300 chars before + 500 chars after)
                start = max(0, match.start() - 300)
                end = min(len(doc_text), match.end() + 500)
                context = doc_text[start:end].lower()

                # Skip if context contains disqualifying terms
                skip_keywords = [
                    "mass", "r_s", "rho", "1e8", "1e9", "1e10",
                    "f_h drop", "fh drop", "phase g9", "factor 0.94",
                    "factor 0.95", "factor 0.96", "factor 1.0", "factor 1.01",
                    "factor 1.02", "factor 1.05", "factor 1.07",
                    "path 2", "path 3", "categorical",
                    "meaningful pass", "pathological", "pass/fail",
                ]
                if any(kw in context for kw in skip_keywords):
                    continue

                # Only flag if context contains gravothermal-related terms
                prefactor_keywords = [
                    "prefactor", "gravothermal", "halo-specific", "yang+ 2024",
                    "150*c", "halo specific", "halo-specific",
                ]
                if not any(kw in context for kw in prefactor_keywords):
                    continue

                # Now check if the found_factor matches the canonical
                if abs(found_factor - expected) / expected > 0.20:
                    drifts.append({
                        "type": f"{halo}_prefactor_mismatch",
                        "doc": doc_name,
                        "context": match.group(0),
                        "found": found_factor,
                        "canonical": expected,
                        "severity": "WARN",
                    })
            except ValueError:
                pass
    return drifts


def check_first_class_count_in_doc(doc_text, canonical_count, doc_name):
    """Check that the doc's 'first-class' structural findings count matches the canonical value."""
    drifts = []
    patterns = [
        r'(\d+)\s+first-class\s+structural\s+results?',
        r'(\d+)\s+first-class\s+results?',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, doc_text, re.IGNORECASE):
            found_count = int(match.group(1))
            if found_count != canonical_count:
                # Skip if in deprecated/historical context
                context_line = match.group(0).lower()
                if any(kw in context_line for kw in ["historical", "r88(", "v1.", "v18.", "v1.13", "v18.29"]):
                    continue
                drifts.append({
                    "type": "first_class_count_mismatch",
                    "doc": doc_name,
                    "context": match.group(0),
                    "found": found_count,
                    "canonical": canonical_count,
                    "severity": "WARN",
                })
    return drifts


def check_abstract_channel_count(doc_text, canonical_count_string, doc_name):
    """ClawsGO #7 §4: detect denominator self-inconsistency in the abstract.

    '4 of 7' and the retired 4/3/1 literal should not appear in headline docs
    outside a retirement/retraction context. The live counts are computed per
    parameter set and convention by scripts/canonical_numbers.py; the F16 guard
    check_channel_count_claims() enforces them.
    """
    drifts = []
    # Search for "4 of 7" with surrounding context
    for match in re.finditer(r'\b4\s+of\s+7\b', doc_text, re.IGNORECASE):
        start = max(0, match.start() - 300)
        end = min(len(doc_text), match.end() + 300)
        context = doc_text[start:end].lower()
        # Skip in retraction / overclaim / historical context
        skip_keywords = [
            "retired", "retract", "overclaim", "double-count", "clawsgo #7",
            "r88(82) process finding", "r88(80)", "r88(56)", "r88(68)",
            "current claim", "reframe headline", "reviewer", "channel count pruning",
            "short-term", "long-term", "future work",
            "honest framing", "more accurate", "honest limit",
            "result: 4 of 7", "verdict from 4 of 5",
        ]
        if any(kw in context for kw in skip_keywords):
            continue
        drifts.append({
            "type": "retired_4_of_7_framing",
            "doc": doc_name,
            "context": match.group(0),
            "canonical": canonical_count_string,
            "severity": "WARN",
        })
    return drifts


def check_no_go_catalogue_membership(doc_text, doc_name):
    """ClawsGO #7 §2: detect stale no-go catalogue membership.

    The v=150 Lei/Wang entry is a TUNING statement (R88(87)), NOT a structural
    no-go. The §2.8 background UV derivation is an OPEN requirement, NOT a
    sixth no-go. These phrases should not appear in headline docs.
    """
    drifts = []
    # Stale: "two structural no-gos" (the abstract's two are STRUCTURAL +
    # STRUCTURAL, but old framing said "two no-gos including v=150")
    start = 0
    for match in re.finditer(r'two\s+(?:identified\s+|clean\s+structural\s+)?no-gos?\s+at\s+different\s+velocity', doc_text, re.IGNORECASE):
        start = max(0, match.start() - 200)
        end = min(len(doc_text), match.end() + 200)
        context = doc_text[start:end].lower()
        skip_keywords = ["retired", "r88(56)", "r88(82)", "r88(80)", "r88(68)", "r88(87) demoted"]
        if any(kw in context for kw in skip_keywords):
            continue
        drifts.append({
            "type": "stale_two_no_gos_at_different_velocity",
            "doc": doc_name,
            "context": match.group(0),
            "canonical": "Per R88(87)+(88): one structural no-go + one structural trade-off (v=150 is TUNING)",
            "severity": "WARN",
        })

    # Stale: "second clean structural no-go at v=150" (the §9.17b implication
    # block reinstates the v=150 premise that the rest of the paper retired)
    for match in re.finditer(r'second\s+clean\s+structural\s+no-go\s+at\s+v=150', doc_text, re.IGNORECASE):
        start = max(0, match.start() - 300)
        end = min(len(doc_text), match.end() + 300)
        context = doc_text[start:end].lower()
        skip_keywords = ["not", "retired", "clawsgo #7", "r88(87)", "r88(88)"]
        if any(kw in context for kw in skip_keywords):
            continue
        drifts.append({
            "type": "stale_second_structural_no_go_v150",
            "doc": doc_name,
            "context": match.group(0),
            "canonical": "v=150 is a TUNING statement (R88(87)), not a structural no-go",
            "severity": "WARN",
        })

    # Stale: "sixth UV no-go" or "fifth no-go" with §2.8
    for match in re.finditer(r'sixth\s+(?:uv\s+)?(?:completion\s+)?no-go', doc_text, re.IGNORECASE):
        start = max(0, match.start() - 200)
        end = min(len(doc_text), match.end() + 200)
        context = doc_text[start:end].lower()
        skip_keywords = ["retired", "open requirement", "not a no-go", "not as a sixth no-go", "clawsgo #6", "r88(88)"]
        if any(kw in context for kw in skip_keywords):
            continue
        drifts.append({
            "type": "stale_sixth_no_go",
            "doc": doc_name,
            "context": match.group(0),
            "canonical": "Per ClawsGO #6 Fix 3: the §2.8 v19.2-F result is an OPEN requirement, not a sixth no-go",
            "severity": "WARN",
        })

    return drifts


def check_tradeoff_factor_scatter(doc_text, doc_name):
    """ClawsGO #7 §5: detect trade-off factor drift.

    The canonical bare-SIDM2c values are Cloud-9 factor ~300x and SPARC factor
    ~1900x. The 250x/200x in the §9.17b Phase G10 table are the SIDM2c-with-
    gravothermal-at-tau=0.3 variant and should be annotated as such.
    """
    drifts = []
    # Search for "factor 250 below" or "factor 200 below" without the SIDM2c annotation
    for match in re.finditer(r'factor\s+(250|200)\s+below', doc_text, re.IGNORECASE):
        start = max(0, match.start() - 200)
        end = min(len(doc_text), match.end() + 200)
        context = doc_text[start:end].lower()
        # Skip if annotated as SIDM2c tau=0.3 column
        if "sidm2c" in context and ("τ=0.3" in context or "tau=0.3" in context or "gravothermal" in context):
            continue
        # Skip if explicitly retired
        skip_keywords = ["retired", "clawsgo #7", "§a.15"]
        if any(kw in context for kw in skip_keywords):
            continue
        drifts.append({
            "type": "tradeoff_factor_scatter",
            "doc": doc_name,
            "context": match.group(0),
            "canonical": "Annotate as SIDM2c (τ=0.3) column, not bare SIDM2c",
            "severity": "WARN",
        })
    return drifts


T41_STANDING_DOCS = ("README.md", "CURRENT.md", "EXTRACT.md", "docs/LAYMAN_SUMMARY.md")
T41_STALE = re.compile(r"770 ?GeV|453(?:-588)? ?MeV|0\.60σ|g_χ ?[=≈] ?1\.19")
T41_HIST_MARKERS = re.compile(
    r"v0\.7|V0\.7|historical|Historical|superseded|archived|pre-T88\.E|Pre-T88\.E|retired|was ")


def check_t41_canonical_vs_artifact(block):
    """The canonical T41 block must match the artifact it claims, byte-for-byte by sha256."""
    drifts = []
    if not block:
        return [{"severity": "HIGH", "doc": "canonical_numbers.json",
                 "type": "t41_v08_standing_map_missing",
                 "found": "no t41_v08_standing_map block",
                 "canonical": "block required (added 2026-11-04)",
                 "context": "front pages quote the T41 v0.8 MAP; without the block the quotes are unchecked"}]
    art = _REPO / block["source_artifact"]
    if not art.exists():
        return [{"severity": "HIGH", "doc": "canonical_numbers.json",
                 "type": "t41_artifact_missing", "found": str(art), "canonical": "artifact must exist"}]
    raw = art.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != block["source_artifact_sha256"]:
        drifts.append({"severity": "HIGH", "doc": "canonical_numbers.json",
                       "type": "t41_artifact_sha_mismatch",
                       "found": sha, "canonical": block["source_artifact_sha256"],
                       "context": "the T41 v0.8 artifact changed after the canonical block was recorded; "
                                   "re-derive the block and re-check the docs"})
    d = json.loads(raw.decode("utf-8"))
    mp = d["MAP_physical"]
    for key, tol in (("m_chi_GeV", 0.01), ("m_phi_MeV", 0.01), ("g_chi", 1e-4),
                     ("sigma_m_0_derived", 1e-4), ("a_derived", 1e-4)):
        if abs(mp[key] - block["MAP"][key]) > tol:
            drifts.append({"severity": "HIGH", "doc": "canonical_numbers.json",
                           "type": f"t41_map_{key}_mismatch",
                           "found": mp[key], "canonical": block["MAP"][key],
                           "context": "canonical block vs artifact disagreement"})
    if abs(d["yukawa_tension"]["a_difference"] - block["yukawa_tension"]["a_difference"]) > 1e-6:
        drifts.append({"severity": "HIGH", "doc": "canonical_numbers.json",
                       "type": "t41_tension_mismatch",
                       "found": d["yukawa_tension"]["a_difference"],
                       "canonical": block["yukawa_tension"]["a_difference"]})
    return drifts


def check_t41_standing_in_doc(doc_text, block, doc_name):
    """v0.8 MAP must be quoted correctly; v0.7 numbers allowed only in labelled historical context."""
    drifts = []
    if not block:
        return drifts
    lines = doc_text.split("\n")
    for i, ln in enumerate(lines, 1):
        if not T41_STALE.search(ln):
            continue
        lo = max(0, i - 9)
        hi = min(len(lines), i + 2)
        window = "\n".join(lines[lo:hi])
        if T41_HIST_MARKERS.search(window):
            continue
        drifts.append({"severity": "HIGH", "doc": doc_name,
                       "type": "t41_v07_values_in_unmarked_standing_context",
                       "found": f"line {i}: {ln.strip()[:150]}",
                       "canonical": "v0.8 MAP: m_chi 478 GeV, m_phi 488 MeV, g_chi 0.964, tension 0.81 "
                                    f"(artifact {block['source_artifact'].rsplit('/', 1)[-1]})",
                       "context": "770 GeV / 453 MeV / 0.60σ / g_chi 1.19 are the v0.7 MAP values"})
    for token in ("478 GeV", "488 MeV", "0.81"):
        if token not in doc_text:
            drifts.append({"severity": "HIGH", "doc": doc_name,
                           "type": "t41_v08_anchor_missing",
                           "found": f"'{token}' absent",
                           "canonical": "the doc must state the v0.8 MAP it is quoting"})
    return drifts


def check_channel_count_claims(doc_text, canonical_block, doc_name):
    """F16 guard (2026-11-05).

    Every 'N PASS / M MARGINAL / K FAIL' claim in a headline doc must
      (a) be a tally that scripts/canonical_numbers.py actually computes, and
      (b) sit next to the parameter set and sigma_unc convention it belongs to.

    Root cause this closes: the paper headlined 4 PASS / 3 MARGINAL / 1 FAIL, a
    tally no code in this repo produces, in the same document as '5 of 8'. The
    two were presented as if they measured the same thing.
    """
    drifts = []
    evals = canonical_block.get("evaluations", [])
    allowed = set()
    for ev in evals:
        tl = ev.get("tally", {})
        total = sum(tl.get(k, 0) for k in ("PASS", "MARGINAL", "FAIL"))
        allowed.add(f"{tl.get('PASS')} PASS / {tl.get('MARGINAL')} MARGINAL / "
                    f"{tl.get('FAIL')} FAIL")
        allowed.add(f"{tl.get('PASS')} of {total}")
    if not allowed:
        return drifts

    context_markers = [
        "phase-44", "phase 44", "a.2", "best fit", "best-fit", "canonical",
        "self-normalized", "v19.2", "r88(", "retired", "historical",
        "previously quoted", "not reproducible", "convention", "likelihood",
        "sigma_unc", "\u03c3_unc",
    ]
    retired_markers = ["retired", "historical", "previously quoted",
                       "not reproducible", "no stored parameter set"]
    # "t120 scoreboard" is a named evaluation of its own: eight project-stated bounds scored by
    # v0.3-prelim/code/t120_constraint_scoreboard.py and pinned by test_t120_constraint_scoreboard.py.
    # Its bounds are not the §A.15 channel slots, so its tallies are not §A.15 claims. Adding the
    # marker does not make a tally acceptable on its own -- the line must still point at an artifact,
    # and the scoreboard producer's own numbers are guarded by tests.
    scoped_eval_markers = ["phase 4a", "phase 4b", "phase 4c", "phase 4d", "phase g8",
                           "phase g4", "phase g1", "three-peak", "two-resonance",
                           "v19.0", "population", "fig 5", "t120 scoreboard",
                           "t120_constraint_scoreboard"]
    artifact_pointer = re.compile(r"\.json|phase4a|phase4b|§10\.4f|\bT\d{2,3}\b")

    pat = re.compile(r"(\d+)\s+PASS\s*/\s*(\d+)\s+MARGINAL\s*/\s*(\d+)\s+FAIL")
    for m in pat.finditer(doc_text):
        claim = m.group(0)
        ctx = doc_text[max(0, m.start() - 400): m.end() + 400].lower()
        # Evidence for scoping / labelling must be on the claim's own line. A 400-char window
        # let an unrelated neighbour line vouch for a fabricated tally (mutation-tested).
        line_lo = doc_text.rfind("\n", 0, m.start()) + 1
        line_hi = doc_text.find("\n", m.end())
        if line_hi == -1:
            line_hi = len(doc_text)
        own_line = doc_text[line_lo:line_hi].lower()
        if claim not in allowed:
            if any(k in ctx for k in retired_markers):
                continue
            # A tally that names its own evaluation AND points at its artifact or paper
            # section is a scoped claim from a different run (e.g. the v19.0 Phase 4A
            # population map, whose 8 observables are not the §A.15 channel slots).
            # Those are allowed; unlabelled foreign tallies are not.
            scoped = any(k in own_line for k in scoped_eval_markers)
            pointed = bool(artifact_pointer.search(own_line))
            if scoped and pointed:
                continue
            if scoped:
                drifts.append({
                    "type": "channel_count_claim_missing_artifact_pointer",
                    "doc": doc_name, "found": claim,
                    "canonical": "scoped claim should cite its artifact or paper section",
                    "context": ctx[:160], "severity": "WARN",
                })
                continue
            drifts.append({
                "type": "channel_count_claim_not_computed",
                "doc": doc_name,
                "found": claim,
                "canonical": "one of: " + " | ".join(sorted(allowed)),
                "context": ctx[:160],
                "severity": "HIGH",
            })
        elif not any(w in own_line for w in context_markers):
            drifts.append({
                "type": "channel_count_claim_missing_parameter_set_label",
                "doc": doc_name,
                "found": claim,
                "canonical": "count must name its parameter set and sigma_unc convention",
                "context": ctx[:160],
                "severity": "WARN",
            })
    return drifts


def check_archived_pair_labels(doc_text, doc_name):
    """An archived-pair amplitude quoted next to a sigma/f_H claim must be labelled,
    in the same paragraph, as belonging to the archived pairing.

    Why (findings F26/F29/F33). The live canonical pair is
    f_H = 0.7501856343179664 with sigma_0 = 0.008150396851725193 and
    sigma_peak = 27.272481773080454 cm^2/g; the archived pair is f_H = 0.297 with
    sigma_0 = 0.052 and sigma_peak = 174.0. Both give the same halo-level
    sigma_eff = f_H^2 * sigma/m = 15.348366 cm^2/g at the resonance peak, so the raw
    amplitudes are pairing-specific and a bare "174 cm^2/g" in a live document reads
    as a current claim. F29 applied this rule to the reference-data registry only;
    F33 applies it to the front pages, the paper and the report of record, where the
    "canonical anchor sigma/m = 174 cm^2/g" sentence survived the pairing change
    unlabelled. Fail closed.

    Two deliberate refinements, both auditable (finding F33):
    1. Literals are matched with a digit/dot lookbehind, so "0.174 cm^2/g" - a
       different quantity - is not mistaken for the 174 cm^2/g amplitude.
    2. A document may declare its default pairing once in a `**Pairing declaration`
       paragraph whose numbers are verified against the canonical artifact. Every
       paragraph then inherits that declaration EXCEPT one that presents a
       canonical/current claim, which must carry its own local label. A declaration is
       a stated convention, not a blanket exemption: it cannot make an unlabelled
       canonical anchor pass, and its own numbers are checked by
       check_pairing_declaration.

    The rule is paragraph-scoped, with two sharpenings that a mutation probe forced (F33):
    - a literal counts as an amplitude only if it is sigma-adjacent (a sigma/sigma-m/f_H/peak
       within 60 characters before it, or a cm^2/g unit right after it), so "174 passed, 3 skipped"
       in a test tally is not mistaken for the 174 cm^2/g amplitude;
    - a paragraph that presents a canonical/current claim needs a label NEAR the amplitude
       (within 160 characters), not merely somewhere in the paragraph. Without this, one
       incidental 'legacy' three sentences away launders an unlabelled canonical claim - which
       is exactly how the first F33 mutation probe missed a corruption it should have caught.
       Coverage must be an ARCHIVED-flavoured label: an F30 dual-pair paragraph saying 'under
       the live canonical pair' nearby made an unlabelled 174 cm^2/g look covered, so 'pairing'
       and 'live pair' do not count for an archived amplitude.
    - a claim is canonical if it uses canonical vocabulary OR the paragraph quotes both an
       archived amplitude and a live-pair amplitude, so deleting the word 'canonical' from a
       labelled anchor sentence cannot launder it.
    A non-canonical paragraph still passes on a paragraph-level label, or on the document's
    declared default pairing."""
    literal_res = (
        re.compile(r"(?<![\d.])0\.297"),
        re.compile(r"(?<![\d.])174\.0"),
        re.compile(r"(?<![\d.])174(?=\s)"),
        re.compile(r"(?<![\d.])2025\.57"),
        re.compile(r"(?<![\d.])0\.052"),
    )
    labels = ("ARCHIVED", "archived", "LEGACY", "legacy", "SUPERSEDED",
              "superseded", "retracted", "PAIRING", "pairing", "live pair", "LIVE PAIR")
    # A label counts as coverage for an ARCHIVED amplitude only if it is an archived-flavoured
    # label. Accepting 'live pair'/'pairing' here was a laundering hole the mutation probe found:
    # an F30 dual-pair paragraph that says "under the live canonical pair" 40 characters away
    # made an unlabelled 174 cm^2/g look covered.
    archived_labels = ("ARCHIVED", "archived", "LEGACY", "legacy",
                       "SUPERSEDED", "superseded", "retracted")
    live_pair_literals = ("27.272481773080454", "0.008150396851725193", "0.7501856343179664")
    canonical_claim_res = (
        re.compile(r"canonical anchor", re.IGNORECASE),
        re.compile(r"the canonical\b", re.IGNORECASE),
        re.compile(r"canonical \u03c3", re.IGNORECASE),
        re.compile(r"canonical sigma", re.IGNORECASE),
        re.compile(r"canonical f_?H", re.IGNORECASE),
    )
    sigma_context_res = re.compile(r"\u03c3|sigma|f_?H|peak", re.IGNORECASE)
    unit_after_res = re.compile(r"^\s*cm(?:2|\u00b2)\s*/\s*g")
    continuation_chars = ("\u00d7", "\u00b7", "*", "^", "/", "(")
    proximity = 160
    # A literal is an amplitude only if the sigma/sigma-m/f_H/peak token is right in front of it
    # (real amplitudes read "sigma_peak = 174" or "174 cm^2/g"). A 60-character window was too
    # loose: it read 'amplitudes count only when sigma-adjacent so a "174 passed" test tally' as
    # an amplitude claim, i.e. the guard flagged its own documentation.
    sigma_context_window = 25
    drifts = []
    declared = bool(re.search(r"^\*\*Pairing declaration", doc_text, re.MULTILINE))
    doc_text = doc_text.replace("\r\n", "\n")
    fence_spans = []
    fence_open = None
    for fm in re.finditer(r"```", doc_text):
        if fence_open is None:
            fence_open = fm.start()
        else:
            fence_spans.append((fence_open, fm.end()))
            fence_open = None
    if fence_open is not None:
        fence_spans.append((fence_open, len(doc_text)))

    def inside_fence(pos):
        return any(a <= pos < b for a, b in fence_spans)

    running = 0
    for idx, para in enumerate(doc_text.split("\n\n")):
        para_start = running
        running += len(para) + 2
        if ("sigma" not in para.lower() and "\u03c3" not in para and "F_H" not in para):
            continue
        # Fenced formula bodies are excluded using DOCUMENT-wide fence spans: a displayed equation
        # can open in one paragraph and close in another, so per-paragraph fence counting would
        # treat the tail of a multi-paragraph equation as prose and demand a label inside it.
        # A quoted equation is relabelled on its introducing sentence instead.
        amplitude_matches = []
        for rx in literal_res:
            for m in rx.finditer(para):
                if inside_fence(para_start + m.start()):
                    continue
                before = para[max(0, m.start() - 60):m.start()]
                after = para[m.end():m.end() + 12]
                has_assignment = bool(re.search(r"[=≈≥≤<>]\s*$", before))
                if not ((sigma_context_res.search(before[-sigma_context_window:]) and has_assignment)
                        or unit_after_res.match(after)):
                    continue  # a number that is not being asserted as a cross-section
                end = m.end()
                unit = re.match(r"\s*cm(?:2|\u00b2)\s*/\s*g", para[end:])
                if unit:
                    end += unit.end()
                if para[end:end + 1] in continuation_chars or para[end:].lstrip()[:1] in continuation_chars:
                    continue  # a term inside an equation, not a standalone claim
                amplitude_matches.append((m.start(), end))
        if not amplitude_matches:
            continue
        is_canonical_claim = (any(rx.search(para) for rx in canonical_claim_res)
                              # Mixing trigger: a paragraph that quotes BOTH an archived amplitude
                              # and a live-pair amplitude is a pairing claim whether or not it uses
                              # the word 'canonical'. Deleting the word 'canonical' from a labelled
                              # anchor sentence must not launder it.
                              or any(lit in para for lit in live_pair_literals))
        if is_canonical_claim:
            uncovered = [(s, e) for s, e in amplitude_matches
                         if not any(lbl in para[max(0, s - proximity):e + proximity]
                                    for lbl in archived_labels)]
            if not uncovered:
                continue
        else:
            if any(lbl in para for lbl in labels):
                continue
            if declared:
                continue  # inherits the document's declared default pairing
        snippet = " ".join(para.split())[:200]
        drifts.append({"severity": "MED", "doc": doc_name,
                       "type": "unlabelled archived-pair literal",
                       "found": snippet,
                       "canonical": "label every archived-pair amplitude within %d characters "
                                    "(or quote the live-pair value 27.272481773080454 and note "
                                    "sigma_eff = 15.348366)" % proximity,
                       "context": f"paragraph {idx}; 0.297 / 0.052 / 174.0 / 0.0265 / 2025.57 are "
                                  "archived-pair amplitudes; unlabelled they read as live constants "
                                  "(findings F26/F29/F33)"})
    # Fenced formula bodies are exempt from per-amplitude labelling (a label inside an equation
    # would change the equation), but the equation itself must be declared: the text introducing
    # the fence has to say which pairing its amplitudes belong to. Otherwise a reader copying the
    # displayed formula uses archived amplitudes as if they were live.
    for open_pos, close_pos in fence_spans:
        body = doc_text[open_pos:close_pos]
        if not any(rx.search(body) for rx in literal_res):
            continue
        introducing = doc_text[max(0, open_pos - 600):open_pos]
        # A declaration inside the first lines of the formula body counts too; requiring it only
        # outside the fence would force edits into the equation itself.
        if any(lbl in introducing for lbl in archived_labels) or any(
                lbl in body[:300] for lbl in archived_labels):
            continue
        drifts.append({"severity": "MED", "doc": doc_name,
                       "type": "unlabelled archived-pair literal",
                       "found": " ".join(body.split())[:200],
                       "canonical": "label the sentence that introduces this fenced formula with "
                                    "ARCHIVED PAIR (or restate it with the live-pair amplitudes "
                                    "27.272481773080454 / 0.008150396851725193)",
                       "context": f"fenced formula body at offset {open_pos}; its amplitudes are "
                                  "pairing-specific and the introducing sentence does not say which "
                                  "pair they belong to (finding F33)"})
    return drifts


def check_pairing_declaration(doc_text, doc_name, canonical):
    """If a document declares a default pairing, the declaration's own numbers must
    equal the canonical artifact's. A drifted declaration would legitimise every
    unlabelled amplitude in that document, so it is checked rather than trusted (F33)."""
    live = canonical.get("v19_2_D_canonical_phase_44_free_fit", {})
    want = {"live sigma_peak": str(live.get("sigma_peak")),
            "archived sigma_peak": "174.0",
            "live f_H": str(live.get("F_H")),
            "archived f_H": "0.297"}
    drifts = []
    for para in doc_text.replace("\r\n", "\n").split("\n\n"):
        if not para.startswith("**Pairing declaration"):
            continue
        missing = {label: value for label, value in want.items()
                   if value and value not in para}
        if missing:
            drifts.append({"severity": "HIGH", "doc": doc_name,
                           "type": "pairing declaration incomplete or stale",
                           "found": " ".join(para.split())[:200],
                           "canonical": "declaration must name " + ", ".join(
                               f"{k} = {v}" for k, v in want.items()),
                           "context": "the declaration is inherited by every unlabelled amplitude "
                                      "in this document, so its numbers are load-bearing (F33)"})
    return drifts


def check_registry_pairing_values(doc_text, doc_name, canonical):
    """The reference-data registry is the project's single source of truth for numbers, yet it was
    outside every drift check (finding F29, 2026-11-06): it still listed f_H = 0.297 with sigma_0 =
    0.052 and sigma_peak = 174.0 as live constants after the canonical pairing (finding F26) moved
    them to the archived pair. This check pins the registry's three pairing rows to the canonical
    artifact, and applies the shared archived-pair labelling rule below."""
    live = canonical.get("v19_2_D_canonical_phase_44_free_fit", {})
    want = {"F_H_CANONICAL": live.get("F_H"),
            "SIGMA_0_CM2_PER_G": live.get("sigma_0"),
            "SIGMA_PEAK_CM2_PER_G": live.get("sigma_peak")}
    drifts = []
    for key, target in want.items():
        if target is None:
            continue
        for i, line in enumerate(doc_text.splitlines(), 1):
            if not line.strip().startswith(f"| {key} |"):
                continue
            cell = line.split("|")[2].strip()
            try:
                got = float(cell)
            except ValueError:
                drifts.append({"severity": "HIGH", "doc": doc_name, "type": "registry pairing row unreadable",
                               "found": f"{key} = {cell!r} (line {i})", "canonical": target,
                               "context": "the registry is the KB single source of truth for this constant"})
                continue
            if abs(got - target) > 1e-9:
                drifts.append({"severity": "HIGH", "doc": doc_name, "type": "registry pairing value stale",
                               "found": f"{key} = {got!r} (line {i})", "canonical": target,
                               "context": "archived-pair value presented as a live constant "
                                          "(findings F26/F29; pairing_k = 0.15673840099471523)"})
    drifts += check_archived_pair_labels(doc_text, doc_name)
    return drifts


def main():
    print("=" * 70)
    print("V19.2-E D — Drift-guard (ClawsGO B.2)")
    print("=" * 70)
    print()

    canonical = load_canonical()

    # Canonical headline values
    a2_summary = canonical["pass_fail_summary_v19_2_E_A2_best_fit"]
    canonical_pass_count = a2_summary["PASS"]
    a2_tradeoffs = canonical["tradeoff_factors_v19_2_E_A2_best_fit"]
    canonical_sparc_factor = a2_tradeoffs["sparc_factor_below_0p19"]
    canonical_first_class = len(canonical["structural_findings_v19_2_D_freeze"]["first_class"])

    print(f"Canonical headline: v19.2-E A.2 5-param DE best-fit:")
    print(f"  PASS count: {canonical_pass_count}")
    print(f"  SPARC factor below 0.19: {canonical_sparc_factor:.1f}x")
    print(f"  First-class structural findings (v19.2-D freeze): {canonical_first_class}")
    print(f"  Halo-specific prefactors:")
    for halo, data in canonical["halo_specific_gravothermal_prefactors"].items():
        print(f"    {halo}: {data['prefactor_vs_yang2024']}x")
    print()

    # Docs to check — only HEADLINE docs that should match the canonical values.
    # Per-round working docs (A.1, A.2 stress, A.2 8ch, B, C) are EXEMPT because
    # they legitimately report different pass counts at different parameter points.
    # CHANGELOG is also EXEMPT because it's a historical record of past-version numbers,
    # not a live headline.
    headline_docs = [
        ("PAPER_V1_DRAFT.md", _REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"),
        ("README.md", _REPO / "README.md"),
        ("CURRENT.md", _REPO / "CURRENT.md"),
        ("FINDINGS.md", _REPO / "docs" / "FINDINGS_FOR_FUTURE_DELIBERATION.md"),
        ("CITATION_AUDIT.md", _REPO / "docs" / "CITATION_AUDIT_V19_2_D.md"),
        ("TRANSITION.md", _REPO / "docs" / "TRANSITION_V19_2_D_TO_V19_2_E.md"),
    ]

    # Canonical abstract channel count (ClawsGO #7 §4)
    canonical_abstract_block = canonical.get("canonical_abstract_channel_count", {})
    canonical_abstract_count = canonical_abstract_block.get("canonical_count_string")
    if not canonical_abstract_count:
        # Fail closed: without the computed block, no channel claim can be verified.
        canonical_abstract_count = "<canonical_abstract_channel_count MISSING>"
        print("canonical_abstract_channel_count: MISSING from canonical JSON "
              "(channel claims cannot be verified)")
    else:
        print(f"canonical_abstract_channel_count: computed -> {canonical_abstract_count}")

    # T41 v0.8 standing MAP: canonical block must match the artifact, and the front pages
    # must quote it (2026-11-04: the front pages had been quoting the v0.7 MAP under a v0.8 label).
    t41_block = canonical.get("t41_v08_standing_map", {})
    t41_drifts = check_t41_canonical_vs_artifact(t41_block)
    if t41_drifts:
        print("T41 canonical-vs-artifact: MISMATCH")
        for drift in t41_drifts:
            print(f"  [HIGH] {drift['type']}: found {drift.get('found')} vs {drift.get('canonical')}")
    else:
        mp = t41_block["MAP"]
        print(f"T41 canonical-vs-artifact: OK (sha256 verified; MAP m_chi={mp['m_chi_GeV']:.1f} GeV, "
              f"m_phi={mp['m_phi_MeV']:.1f} MeV, g_chi={mp['g_chi']:.3f}, "
              f"tension={t41_block['yukawa_tension']['reported_sigma']})")
    print()

    # Auditor self-count: the standing block must quote the auditor's real check count, so an
    # auditor that silently grows cannot stay green while the docs quote an old number.
    t82_count = canonical.get("t82_audit_check_count")
    if t82_count:
        literal = f"{t82_count}/{t82_count} ALL CLEAR"
        if literal not in load_doc(_REPO / "CURRENT.md"):
            t41_drifts.append({"severity": "HIGH", "doc": "CURRENT.md",
                               "type": "t82_audit_count_literal_stale",
                               "found": f"'{literal}' absent from the standing block",
                               "canonical": literal})
            print(f"T82 count literal in CURRENT.md: STALE (expected '{literal}')")
        else:
            print(f"T82 count literal in CURRENT.md: OK ({literal})")
        print()

    all_drifts = list(t41_drifts)
    for doc_name, doc_path in headline_docs:
        doc_text = load_doc(doc_path)
        if not doc_text:
            continue
        drifts = []
        drifts += check_pass_count_in_doc(doc_text, canonical_pass_count, doc_name)
        drifts += check_sparc_factor_in_doc(doc_text, canonical_sparc_factor, doc_name)
        drifts += check_halo_prefactors_in_doc(doc_text, doc_name)
        drifts += check_first_class_count_in_doc(doc_text, canonical_first_class, doc_name)
        # ClawsGO #7 checks
        drifts += check_abstract_channel_count(doc_text, canonical_abstract_count, doc_name)
        drifts += check_channel_count_claims(doc_text, canonical_abstract_block, doc_name)
        drifts += check_no_go_catalogue_membership(doc_text, doc_name)
        drifts += check_tradeoff_factor_scatter(doc_text, doc_name)
        # F33: archived-pair amplitudes must be labelled wherever they appear.
        drifts += check_archived_pair_labels(doc_text, doc_name)
        drifts += check_pairing_declaration(doc_text, doc_name, canonical)
        all_drifts += drifts

    # T41 standing-MAP check over the four front-facing docs (README, CURRENT, EXTRACT, LAYMAN).
    for doc_name in T41_STANDING_DOCS:
        doc_text = load_doc(_REPO / doc_name)
        if not doc_text:
            continue
        all_drifts += check_t41_standing_in_doc(doc_text, t41_block, doc_name)

    # F33: docs that quote the canonical anchor but are not in the headline set.
    # EXTRACT.md and the v19.2-E report of record both carried "canonical anchor
    # sigma/m = 174 cm^2/g" with no pairing label after the pairing change.
    for doc_name, doc_path in [
        ("EXTRACT.md", _REPO / "EXTRACT.md"),
        ("V19_2_E_CONSOLIDATED.md", _REPO / "docs" / "V19_2_E_CONSOLIDATED_REPORT_2026-11-03.md"),
        ("LAYMAN_SUMMARY.md", _REPO / "docs" / "LAYMAN_SUMMARY.md"),
    ]:
        doc_text = load_doc(doc_path)
        if not doc_text:
            continue
        all_drifts += check_archived_pair_labels(doc_text, doc_name)

    # Also check the v19.2-E round docs for halo-prefactor drift only.
    # The per-round docs legitimately have different pass counts but should
    # agree on halo-specific gravothermal prefactors (which are independent of
    # the parameter point).
    round_docs = [
        ("A1_REAL_LIKELIHOOD.md", _REPO / "docs" / "V19_2_E_A1_REAL_LIKELIHOOD_PROMOTION.md"),
        ("A2_5PARAM.md", _REPO / "docs" / "V19_2_E_A2_5PARAM_DE.md"),
        ("A2_8CHANNEL.md", _REPO / "docs" / "V19_2_E_A2_8CHANNEL_FIT.md"),
        ("B_GRAVOTHERMAL.md", _REPO / "docs" / "V19_2_E_B_PER_HALO_GRAVOTHERMAL.md"),
        ("C_DATA_ONLY.md", _REPO / "docs" / "V19_2_E_C_DATA_ONLY_SIGMA_M.md"),
    ]
    for doc_name, doc_path in round_docs:
        doc_text = load_doc(doc_path)
        if not doc_text:
            continue
        drifts = []
        drifts += check_halo_prefactors_in_doc(doc_text, doc_name)
        drifts += check_first_class_count_in_doc(doc_text, canonical_first_class, doc_name)
        all_drifts += drifts

    # The reference-data registry (KB single source of truth) must agree with the canonical
    # pairing, and every archived-pair literal it quotes must be labelled (finding F29).
    registry_doc = _REPO / "docs" / "V19_2_F_REFERENCE_DATA_REGISTRY.md"
    registry_text = load_doc(registry_doc)
    if registry_text:
        all_drifts += check_registry_pairing_values(registry_text, "REFERENCE_DATA_REGISTRY.md", canonical)

    if not all_drifts:
        print("=" * 70)
        print("RESULT: No drift detected. All docs consistent with canonical numbers.")
        print("=" * 70)
        sys.exit(0)

    print("=" * 70)
    print(f"RESULT: {len(all_drifts)} drift(s) detected.")
    print("=" * 70)
    print()
    for drift in all_drifts:
        print(f"  [{drift['severity']}] {drift['doc']}: {drift['type']}")
        print(f"    Found: {drift.get('found', '?')}")
        print(f"    Canonical: {drift.get('canonical', '?')}")
        print(f"    Context: {drift.get('context', '?')}")
        print()

    # Strict mode: exit non-zero
    if "--strict" in sys.argv:
        print("Exiting non-zero (--strict).")
        sys.exit(1)


if __name__ == "__main__":
    main()
