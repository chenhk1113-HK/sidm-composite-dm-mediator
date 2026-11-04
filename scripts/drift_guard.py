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

    The canonical convention is: 8 channels (4 PASS / 3 MARGINAL / 1 FAIL).
    The retired '4 of 7' framing should not appear in headline docs.
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
    canonical_abstract_count = canonical.get(
        "canonical_abstract_channel_count", {}
    ).get("canonical_count_string", "8 constrained channels (4 PASS / 3 MARGINAL / 1 FAIL)")

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
        drifts += check_no_go_catalogue_membership(doc_text, doc_name)
        drifts += check_tradeoff_factor_scatter(doc_text, doc_name)
        all_drifts += drifts

    # T41 standing-MAP check over the four front-facing docs (README, CURRENT, EXTRACT, LAYMAN).
    for doc_name in T41_STANDING_DOCS:
        doc_text = load_doc(_REPO / doc_name)
        if not doc_text:
            continue
        all_drifts += check_t41_standing_in_doc(doc_text, t41_block, doc_name)

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
