"""n27-round gate hardening tests (CG-19 / CG-20 / CG-21, 2026-11-02).

Covers the three machine defences the n27 review demanded:
  * CG-21  build-time table cell-width validation (scripts/table_cells.py)
           — the D6 fix was given a detector, same standard as D5's.
  * CG-19  version-aware (numeric) deliverable selection in BOTH gate layers
           8 and 9 — previously both audited frozen v1.10/v1.8 snapshots.
  * CG-20  layer-8 filename-existence sub-check: a .md filename named in
           prose must exist in the worktree or git history; the phantom
           allowlist is machine-guarded against hiding a real file.
Plus the n27 item-6 snapshot attestation anchor and a source-level guard
that the builder and the tests share the same table-cell logic.
"""

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import table_cells as tc                       # noqa: E402
import audit_doc_anchors as ada                # noqa: E402
import audit_model_provenance as amp           # noqa: E402


# --------------------------------------------------------------- CG-21 ----
HEADER = "| A | B | C | D | E | F |"
SEP = "|---|---|---|---|---|---|"


def test_uniform_table_passes():
    rows = [tc.split_cells(HEADER),
            tc.split_cells("| 1 | 2 | 3 | 4 | 5 | 6 |"),
            tc.split_cells("| a | b | c | d | e | f |")]
    assert tc.validate_rows(rows) == 6


def test_d5_mutation_missing_closing_pipe_fails():
    # The exact D5 shape: a 6-cell header, a row missing its trailing pipe.
    ragged = "| x | y | z | w | v |"          # 5 cells
    rows = [tc.split_cells(HEADER), tc.split_cells(ragged)]
    with pytest.raises(ValueError, match="TABLE WIDTH MISMATCH"):
        tc.validate_rows(rows)


def test_d6_escaped_pipes_stay_inside_cells():
    # The CG-11 mutation-proof content quoted as Markdown inside a cell:
    # escaped pipes are literal text, the row stays 6 cells wide.
    row = ("| cw | walker | CLOSED | Mutation-verified: injecting "
           "(`\\| Single-Yukawa \\| 1.42 \\| PASS and FAIL \\|`) reproduces "
           "`1 issues` | closed | done |")
    cells = tc.split_cells(row)
    assert len(cells) == 6
    assert "\\|" not in cells[3] and "| Single-Yukawa |" in cells[3]
    assert tc.validate_rows([tc.split_cells(HEADER), cells]) == 6


def test_d6_mutation_unescaped_wide_row_fails():
    # The D6 shape: the same content with pipes NOT escaped — 10 cells
    # against a 6-cell header. The width gate catches it loudly.
    row = ("| cw | walker | CLOSED | injecting \\| Single-Yukawa \\| 1.42 "
           "\\| PASS and FAIL \\| now UNESCAPED via split | closed | done |")
    wide = "| cw | walker | CLOSED | injecting | Single-Yukawa | 1.42 " \
           "| PASS and FAIL | now UNESCAPED via split | closed | done |"
    rows = [tc.split_cells(HEADER), tc.split_cells(wide)]
    assert len(rows[1]) == 10
    with pytest.raises(ValueError, match="TABLE WIDTH MISMATCH"):
        tc.validate_rows(rows)


def test_builder_and_tests_share_the_same_cell_logic():
    # Regression guard: the shipped builder must split/validate through
    # scripts/table_cells.py, so this test file cannot drift from what the
    # PDF build actually enforces.
    src = (REPO / "scripts" / "build_round5_report_pdfs.py").read_text(
        encoding="utf-8")
    assert "import table_cells as tc" in src
    assert "tc.validate_rows" in src and "tc.split_cells" in src
    helper = (REPO / "scripts" / "table_cells.py").read_text(encoding="utf-8")
    assert "TABLE WIDTH MISMATCH" in helper


# --------------------------------------------------------------- CG-19 ----
def _seed_versions(dirpath: Path):
    for v in ("v1.8", "v1.9", "v1.10", "v1.16"):
        (dirpath / f"DOC_{v}_2026-01-01.md").write_text(f"# {v}\n",
                                                        encoding="utf-8")


@pytest.mark.parametrize("module", [ada, amp], ids=["layer8", "layer9"])
def test_selection_is_numeric_not_lexicographic(module, tmp_path):
    # 'v1.9' sorts ABOVE 'v1.16' as a string; the selection must not.
    _seed_versions(tmp_path)
    old = module.DOCS
    module.DOCS = tmp_path
    try:
        pick = module._latest("DOC_")
        assert pick.name == "DOC_v1.16_2026-01-01.md"
    finally:
        module.DOCS = old


@pytest.mark.parametrize("module", [ada, amp], ids=["layer8", "layer9"])
def test_layers_resolve_current_deliverables_not_frozen_constants(module):
    # The frozen-constant disease (v1.10 report / v1.8 companion) is gone:
    # both layers point at the highest numeric version on disk today.
    assert module.REPORT.name >= "SIDM_ROUND5_CONSOLIDATED_FIXES_v1.16"
    assert int(module.REPORT.name.split("_v1.")[-1].split("_")[0]) >= 16
    assert module.COMPANION.name == "SIDM_ROUND5_CHANGED_CODE_v1.9_2026-10-26.md"


@pytest.mark.parametrize("module", [ada, amp], ids=["layer8", "layer9"])
def test_frozen_selection_is_blind_to_new_sections(module, tmp_path):
    # Version-rollback mutation proof: a claim that exists ONLY in the
    # current version is invisible to a frozen-selection scan domain.
    new_doc = tmp_path / "DOC_v1.16_2026-01-01.md"
    old_doc = tmp_path / "DOC_v1.10_2026-01-01.md"
    claim = "deleg_deadbeef made 42 API calls (fabricated for mutation test)"
    new_doc.write_text(f"## 26.\n{claim}\n", encoding="utf-8")
    old_doc.write_text("## 24.\nnothing of interest\n", encoding="utf-8")
    old = module.DOCS
    module.DOCS = tmp_path
    try:
        current = module._latest("DOC_")
        assert current.name == "DOC_v1.16_2026-01-01.md"
        # frozen selection (the pre-CG-19 behaviour) would scan the v1.10
        # text, which does NOT contain the claim -> blind, silently.
        assert claim not in old_doc.read_text(encoding="utf-8")
        assert claim in current.read_text(encoding="utf-8")
    finally:
        module.DOCS = old


# --------------------------------------------------------------- CG-20 ----
def test_phantom_filename_is_detected():
    texts = {"report": "the file SIDM_NOT_A_REAL_FILE_zzz.md was edited"}
    defects = ada.check_filenames(texts)
    assert any(d["name"] == "SIDM_NOT_A_REAL_FILE_zzz.md" for d in defects)


def test_real_and_historical_names_pass():
    texts = {"report": "see PAPER_V1_DRAFT.md and "
           "SIDM_ROUND5_CONSOLIDATED_FIXES_v1.0_2026-10-25.md"}
    # v1.0 was superseded and deleted from disk — it exists only in git
    # history, which is a legitimate citation of a historical version.
    defects = ada.check_filenames(texts)
    assert defects == []


def test_allowlisted_phantom_passes_and_is_machine_guarded():
    texts = {"report": "SIDM_SEARCHABLE_v19_2_F.md never existed"}
    assert ada.check_filenames(texts) == []          # disclosed phantom

    # Guard: an allowlist entry for a REAL file is itself a defect —
    # the allowlist can never be used to hide an existing file.
    old = dict(ada.PHANTOM_ALLOWLIST)
    ada.PHANTOM_ALLOWLIST["PAPER_V1_DRAFT.md"] = "bogus cover"
    try:
        defects = ada.check_filenames({"report": "PAPER_V1_DRAFT.md"})
        assert any("actually exists" in d["problem"] for d in defects)
    finally:
        ada.PHANTOM_ALLOWLIST.clear()
        ada.PHANTOM_ALLOWLIST.update(old)


def test_live_documents_have_no_phantom_citations():
    # Whole-repo live check: every .md cited in the audited deliverables
    # exists (this is exactly what the gate layer runs on every build).
    texts = {
        "report": ada.REPORT.read_text(encoding="utf-8"),
        "closeout": ada.CLOSEOUT.read_text(encoding="utf-8"),
        "companion": ada.COMPANION.read_text(encoding="utf-8"),
        "paper": ada.PAPER.read_text(encoding="utf-8"),
    }
    assert ada.check_filenames(texts) == []


# ------------------------------------------------- n27 item 6 anchor ----
def test_snapshot_entries_carry_attestation_anchors():
    snap = json.loads(amp.SNAPSHOT.read_text(encoding="utf-8"))
    for did, entry in snap.items():
        att = entry.get("attested")
        assert att, f"{did}: snapshot entry without attestation anchor"
        assert att.get("commit") and att.get("evidence_log")


def test_provenance_script_surfaces_and_flags_attestation():
    src = (REPO / "scripts" / "audit_model_provenance.py").read_text(
        encoding="utf-8")
    assert "api_calls_attested" in src
    assert "snapshot_warnings" in src
    assert "attested at commit" in src
