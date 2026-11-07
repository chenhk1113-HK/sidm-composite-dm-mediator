"""Finding F33 — a live-facing document may not present an archived-pair amplitude as current.

What happened: finding F26 (2026-11-06) made f_H = 0.7501856343179664 with
sigma_peak = 27.272481773080454 cm^2/g the live canonical pair and moved
f_H = 0.297 / sigma_peak = 174.0 to the archived pair. The halo-level effective
predictions did not change (f_H^2 * sigma/m = 15.348366 cm^2/g either way), but the
front pages, the paper and the v19.2-E report of record kept calling
"the canonical anchor sigma/m = 174 cm^2/g" - which after F26 is an archived-pair raw
amplitude, not the live one. F29 applied the labelling rule only to the reference-data
registry, so the rest of the documentation stayed unlabelled until a reader asked.

This test pins the repair:
1. every live-facing document declares its default pairing once, in a paragraph whose
   four numbers are verified against the canonical artifact;
2. no live-facing document contains an unlabelled archived-pair amplitude;
3. the guard is wired into the drift layer for those documents, not just written;
4. the guard still fires when a label is deleted from a canonical claim, and when a
   declaration's own number is corrupted (a declaration cannot become a blank cheque);
5. the fenced canonical sigma/m(v) formula was relabelled on its introducing sentence
   and the formula body itself is unchanged.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CANON_JSON = REPO / "v0.3-prelim" / "data" / "results" / "canonical_numbers.json"
DRIFT = REPO / "scripts" / "drift_guard.py"

DECLARED_DOCS = {
    "PAPER.md": REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md",
    "README.md": REPO / "README.md",
    "CURRENT.md": REPO / "CURRENT.md",
    "EXTRACT.md": REPO / "EXTRACT.md",
    "FINDINGS.md": REPO / "docs" / "FINDINGS_FOR_FUTURE_DELIBERATION.md",
    "V19_2_E_CONSOLIDATED.md": REPO / "docs" / "V19_2_E_CONSOLIDATED_REPORT_2026-11-03.md",
    "LAYMAN_SUMMARY.md": REPO / "docs" / "LAYMAN_SUMMARY.md",
}
# Documents the drift layer scans for unlabelled archived amplitudes.
SCANNED_DOCS = dict(DECLARED_DOCS)
SCANNED_DOCS["CITATION_AUDIT.md"] = REPO / "docs" / "CITATION_AUDIT_V19_2_D.md"
SCANNED_DOCS["TRANSITION.md"] = REPO / "docs" / "TRANSITION_V19_2_D_TO_V19_2_E.md"

LIVE_PEAK = "27.272481773080454"
LIVE_FH = "0.7501856343179664"
ARCH_PEAK = "174.0"
ARCH_FH = "0.297"


def _drift_module():
    spec = importlib.util.spec_from_file_location("drift_guard_f33", DRIFT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def dg():
    return _drift_module()


@pytest.fixture(scope="module")
def canonical():
    return json.loads(CANON_JSON.read_text(encoding="utf-8"))


def test_declared_documents_are_the_ones_the_drift_layer_scans(dg, canonical):
    """A declaration is inherited by every unlabelled amplitude in its document, so the
    documents allowed to declare must be exactly the documents the drift layer scans."""
    src = DRIFT.read_text(encoding="utf-8")
    for name in SCANNED_DOCS:
        if name in DECLARED_DOCS:
            continue
        assert name in src, f"{name} is scanned but was not considered by the relabel pass"
    assert "check_archived_pair_labels(doc_text, doc_name)" in src, (
        "the labelling guard exists but main() never calls it on the headline documents")
    assert "check_pairing_declaration(doc_text, doc_name, canonical)" in src, (
        "the declaration guard exists but main() never calls it, so a drifted declaration "
        "would legitimise every unlabelled amplitude in its document")


def test_every_live_document_declares_its_pairing_with_verified_numbers(dg, canonical):
    live = canonical["v19_2_D_canonical_phase_44_free_fit"]
    assert f"{live['sigma_peak']}" == LIVE_PEAK
    assert f"{live['F_H']}" == LIVE_FH
    for name, path in DECLARED_DOCS.items():
        text = path.read_text(encoding="utf-8")
        paragraphs = [p for p in text.replace("\r\n", "\n").split("\n\n")
                      if p.startswith("**Pairing declaration")]
        assert len(paragraphs) == 1, f"{name} has {len(paragraphs)} pairing declarations, expected exactly 1"
        decl = paragraphs[0]
        for value in (LIVE_PEAK, LIVE_FH, ARCH_PEAK, ARCH_FH):
            assert value in decl, f"{name}: declaration omits {value}"
        assert "sigma" in decl.lower() or "\u03c3" in decl
        assert dg.check_pairing_declaration(text, name, canonical) == []
        # The declaration must say which pairing an unlabelled amplitude defaults to,
        # otherwise inheriting it is undefined rather than a convention.
        assert "unless a sentence says otherwise" in decl.lower(), (
            f"{name}: declaration does not state the default pairing for unlabelled amplitudes")


def test_no_live_document_has_an_unlabelled_archived_amplitude(dg):
    offenders = {}
    for name, path in SCANNED_DOCS.items():
        if not path.exists():
            continue
        drifts = dg.check_archived_pair_labels(path.read_text(encoding="utf-8"), name)
        if drifts:
            offenders[name] = [d["found"][:160] for d in drifts]
    assert not offenders, f"unlabelled archived-pair amplitudes remain: {offenders}"


def test_deleting_a_label_from_a_canonical_claim_re_fires_the_guard(dg):
    """The declaration must not become a blanket exemption: a paragraph that presents a
    canonical claim still needs its own label."""
    path = REPO / "CURRENT.md"
    text = path.read_text(encoding="utf-8")
    target = None
    for para in text.replace("\r\n", "\n").split("\n\n"):
        if "174 cm\u00b2/g" in para and "ARCHIVED pair" in para and "anchor" in para.lower():
            target = para
            break
    assert target is not None, "no labelled anchor claim found in CURRENT.md to corrupt"
    corrupted = target.replace("(ARCHIVED pair)", "")
    corrupted = corrupted.replace("\u03c3/m = 174 cm\u00b2/g (ARCHIVED pair)", "\u03c3/m = 174 cm\u00b2/g")
    assert corrupted != text, "removing the label did not change the document"
    drifts = dg.check_archived_pair_labels(corrupted, "CURRENT.md")
    assert drifts, "an unlabelled canonical anchor claim passed the guard"
    assert any("174" in d["found"] for d in drifts)


def test_a_stale_declaration_number_fires_the_declaration_guard(dg, canonical):
    """Inherited conventions are load-bearing: corrupting one number in the declaration
    must be caught, because every unlabelled amplitude in that document relies on it."""
    path = REPO / "README.md"
    text = path.read_text(encoding="utf-8")
    assert dg.check_pairing_declaration(text, "README.md", canonical) == []
    corrupted = text.replace(f"\u03c3_peak = {LIVE_PEAK}", f"\u03c3_peak = {ARCH_PEAK}", 1)
    assert corrupted != text, "the declaration anchor was not found"
    drifts = dg.check_pairing_declaration(corrupted, "README.md", canonical)
    assert drifts, "a declaration that quotes only the archived peak passed the guard"
    assert drifts[0]["severity"] == "HIGH"


def test_fenced_canonical_formula_body_is_untouched_and_its_lead_is_labelled():
    paper = (REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md").read_text(encoding="utf-8")
    formula = "\u03c3/m(v) = 0.052 \u00d7 (100/v)^1.93 + 174 \u00d7 exp(-(v - 29.4)\u00b2 / (2 \u00d7 4.4\u00b2))"
    assert paper.count(formula) == 1, (
        "the fenced canonical sigma/m(v) formula was edited; F33 relabels the introducing "
        "sentence, never the equation body")
    lead = re.search(r"\*\*v19\.2-F canonical \u03c3/m\(v\) form[^\n]*", paper)
    assert lead is not None, "the introducing sentence for the canonical form is missing"
    assert "ARCHIVED pair" in lead.group(0), "the fenced formula's introducing sentence is unlabelled"
    assert LIVE_PEAK in lead.group(0), "the labelled lead does not give the live-pair equivalent"


def test_relabel_is_a_label_change_not_a_number_change():
    """The relabel must not have 'fixed' 174 by swapping in the live amplitude anywhere."""
    paper = (REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md").read_text(encoding="utf-8")
    assert paper.count("(archived pair)") >= 20, "expected the paper's canonical claims to be labelled"
    # 174 as an amplitude must still appear; it is the archived-pair value, not deleted.
    amplitude_re = re.compile(r"(?<![\d.])174\s*cm\u00b2/g")
    assert amplitude_re.search(paper), "the archived-pair amplitude disappeared from the paper"
    current = (REPO / "CURRENT.md").read_text(encoding="utf-8")
    assert "174 cm\u00b2/g" in current
    assert LIVE_PEAK in current, "CURRENT.md does not state the live canonical raw peak"


def test_amplitude_eligibility_accepts_real_claims_and_rejects_prose(dg):
    """The eligibility rule decides what counts as a cross-section claim. Both directions matter:
    a real unlabelled amplitude must fire, and prose that merely mentions a test tally must not."""
    prose = ("## Current status\n\nCanonical results below. The guard counts an amplitude only when it is\n"
             "sigma-adjacent so a \"174 passed, 3 skipped\" test tally is not read as the amplitude, "
             "and 0.297 of the suite was deselected.\n")
    assert not dg.check_archived_pair_labels(prose, "PROSE.md")
    real = ("## Current status\n\nThe canonical anchor is sigma/m = 174 cm\u00b2/g at 29.4 km/s, "
            "with sigma_peak = 174.0 from the A.2 fit.\n")
    fires = dg.check_archived_pair_labels(real, "REAL.md")
    assert len(fires) >= 1, "an unlabelled amplitude claim was not caught"


def test_fenced_formula_needs_a_declaration_and_losing_it_re_fires_the_guard(dg):
    """Equations are exempt from per-amplitude labels, so every fenced formula that quotes
    archived amplitudes must carry the pairing declaration on its introducing sentence.
    Deleting that declaration has to re-fire the guard (F33)."""
    paper = (REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md").read_text(encoding="utf-8")
    heading = ("**Table: Canonical \u03c3/m(v) \u2014 Gaussian form, Phase 44 free fit "
               "\u2014 ARCHIVED pair raw amplitudes")
    assert paper.count(heading) == 1, "the canonical table lost its pairing declaration"
    assert paper.count("174 cm\u00b2/g (archived pair)") >= 1, "no labelled archived amplitude in the paper"
    assert not dg.check_archived_pair_labels(paper, "PAPER_V1_DRAFT.md")
    stripped = paper.replace(heading, "**Table: Canonical \u03c3/m(v) \u2014 Gaussian form, "
                                      "Phase 44 free fit")
    fires = dg.check_archived_pair_labels(stripped, "PAPER_V1_DRAFT.md")
    assert fires, "an unlabelled fenced formula was accepted"
    assert any("fenced formula body" in d["context"] for d in fires), fires[0]["context"]
