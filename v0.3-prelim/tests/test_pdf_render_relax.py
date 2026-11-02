"""n24-round containment unit test (2026-11-01): exponent-fold semantics.

The report builder ASCII-folds super/subscripts at BUILD time
(pdf_rencode_maps.SUP/SUB: '10⁻¹²' -> '10-12', 'f_H²σ' -> 'f_H2σ'), so the
rendered PDFs carry the exponent as ONE fused token. audit_pdf_render's
relax_tokens must model BOTH rendering worlds — split fragments for
raised-baseline glyphs, the fused form for the builder fold — and score
them as SEPARATE variants (merging dilutes coverage with stray fragments).
Before this fix the fused spelling was invisible to the audit and eight
correctly-rendered exponent lines on the frozen-good v1.14 PDF were
flagged as missing content.

Tests import the REAL functions from the audit module (module-level after
the 2026-11-01 lift; no re-implemented copies).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import audit_pdf_render as apr


def test_split_variant_unchanged():
    # tail() normalization now applies to fragments too (symmetric pipeline):
    # '-12' loses its glyph-drop leading hyphen exactly as a caret-free token
    # would; the exponent digits are preserved.
    out = apr.relax_tokens(["7.5x10^-12"])
    assert out == ["7.5x10", "12"]


def test_quote_edge_is_stripped_on_both_sides():
    # The n24 bug: source token '"7.5x10^-12' (curly quote glued on) kept the
    # quote in the caret branch while the PDF side stripped it -> a present
    # token read as absent. tail() now runs on every emitted variant.
    src = apr.relax_tokens(['\u201c7.5x10^-12'], fuse=True)
    pdf = apr.relax_tokens(['\u201c7.5x10-12'])
    assert src == pdf == ["7.5x10-12"]


def test_fused_variant_emits_builder_fold():
    out = apr.relax_tokens(["7.5x10^-12"], fuse=True)
    assert out == ["7.5x10-12"]


def test_fused_variant_superscript_letters():
    # canonical() maps unicode superscript ² via the caret expansion; the
    # fold rejoins neighbours and tail() applies '?'->'-' + lowercase on
    # both variants symmetrically — matching the builder-folded PDF token
    # 'f_H2?_HH' exactly.
    out = apr.relax_tokens(["f_H^2?_HH"], fuse=True)
    assert out == ["f_h2-_hh"]
    out2 = apr.relax_tokens(["f_H^2?_HH"])
    assert out2 == ["f_h", "2-_hh"]
    # and the real PDF token relaxes to the identical fused spelling:
    assert apr.relax_tokens(["f_H2?_HH"]) == ["f_h2-_hh"]


def test_coverage_matches_builder_folded_pdf_only_via_fused():
    # PDF-side token stream as extracted from the real folded PDF.
    pdf_tokens = ["reviewer", "b", "claim", "3", "7.5x10-12", "is",
                  "inconsistent", "with", "the", "canonical"]
    tri = apr._trigrams(pdf_tokens)
    tri_set = set(tri)
    src = ["reviewer", "b", "claim", "3", "7.5x10^-12", "is",
           "inconsistent", "with", "the", "canonical"]
    cov_split, miss_split = apr._coverage(apr.relax_tokens(src), tri_set)
    cov_fused, miss_fused = apr._coverage(apr.relax_tokens(src, fuse=True), tri_set)
    assert cov_fused == 1.0 and miss_fused == 0
    assert cov_split < 1.0 and miss_split > 0  # split fails in the folded world


def test_true_absence_still_caught():
    # If the exponent content is genuinely absent from the PDF, NEITHER
    # variant may rescue it. The production rescue gate is
    #   if max(cov_r, cov_r_f) >= PROSE_COVERAGE: rescued
    # so the negative control must assert the max of BOTH variants stays
    # below the gate. An `or` here would pass even if one variant falsely
    # reached 1.0 and rescued a truly-missing exponent (n25 finding 1).
    pdf_tokens = ["the", "canonical", "value", "is", "inconsistent",
                  "regime", "labels", "differ"]
    tri_set = set(apr._trigrams(pdf_tokens))
    src = ["the", "canonical", "value", "10^-13", "is", "inconsistent",
           "regime", "labels", "differ"]
    cov_s, miss_s = apr._coverage(apr.relax_tokens(src), tri_set)
    cov_f, miss_f = apr._coverage(apr.relax_tokens(src, fuse=True), tri_set)
    assert miss_s > 0 and miss_f > 0
    # the exact production gate, mirrored: max(...) < PROSE_COVERAGE
    assert max(cov_s, cov_f) < apr.PROSE_COVERAGE
    # belt-and-braces: both variants individually below threshold
    assert cov_s < apr.PROSE_COVERAGE and cov_f < apr.PROSE_COVERAGE




# ---------------------------------------------------------------------------
# n24 addendum (2026-11-01): wrapped-comment whitelist.
# A fenced comment longer than CODE_WRAP is hard-wrapped by the builder into
# several PDF lines. The leak whitelist must know the builder's EXACT
# fragments, and the only safe way to know them is to import the same module
# the builder uses. These tests lock that contract.
# ---------------------------------------------------------------------------

def _wrapping_fragments():
    from pdf_rencode_maps import render_code_block, CODE_WRAP
    comment = ("# (pdf_rencode_maps.SUP/SUB -- '10-12' is drawn as '10-12' "
               "and 'f_H2' as 'f_H2'), so these PDFs carry the exponent as "
               "ONE fused token whenever the fold applies")
    assert len(comment) > CODE_WRAP
    return render_code_block(comment), comment


def test_wrapped_comment_fragments_start_with_hash_or_cont():
    frags, _ = _wrapping_fragments()
    assert len(frags) >= 2
    assert frags[0].startswith("#")
    # continuation lines carry the builder's indent (>= 2 spaces), never '#'
    assert all(not f.startswith("#") and f.startswith("  ") for f in frags[1:])


def test_wrap_preserves_every_word():
    frags, src = _wrapping_fragments()
    src_words = src.split()
    frag_words = " ".join(frags).split()
    assert frag_words == src_words  # hard-wrap at spaces: no word lost


def test_builder_uses_the_shared_functions_not_local_copies():
    """Anti-drift lock (source-level, dependency-free): build_round5_report_pdfs
    must import the shared wrap/fold pipeline from pdf_rencode_maps.py and must
    never redefine it locally (the layer-14 drift class). Deliberately checked
    against SOURCE TEXT rather than by importing the builder, so this test runs
    in every venv - the gate venv has no reportlab, and an import-based check
    there fails for the wrong reason (dependency), not the guarded reason."""
    scripts = Path(__file__).resolve().parents[2] / "scripts"
    src = (scripts / "build_round5_report_pdfs.py").read_text(encoding="utf-8")
    maps_src = (scripts / "pdf_rencode_maps.py").read_text(encoding="utf-8")
    imports = [ln for ln in src.splitlines() if "from pdf_rencode_maps import" in ln]
    assert imports, "builder no longer imports pdf_rencode_maps"
    for name in ("ascii_fold", "fold_mono", "wrap_code_lines", "CODE_WRAP"):
        assert any(name in ln for ln in imports), f"builder does not import shared {name}"
        assert f"def {name}(" not in src, f"builder redefines {name} locally (drift class)"
    assert "CODE_WRAP =" not in src, "builder assigns CODE_WRAP locally (drift class)"
    for name in ("ascii_fold", "fold_mono", "wrap_code_lines"):
        assert f"def {name}(" in maps_src, f"shared module missing {name}"
    assert "CODE_WRAP = 108" in maps_src


def test_audit_whitelist_includes_wrapped_fragments():
    """The audit's leak whitelist must accept a builder-wrapped comment
    fragment that starts with '#', not flag it as a heading leak."""
    import audit_pdf_render as a
    frags, src = _wrapping_fragments()
    # Build the probe set exactly as the audit does (its code_probes loop)
    import re
    probes = set()
    for cl in [src]:
        n = a._norm(cl)
        probes.add(n)
        probes.add(re.sub(r"^#+\s*", "", n))
        probes.add(re.sub(r"\s{2,}", " ", n))
        probes.add(re.sub(r"^#+\s*", "", re.sub(r"\s{2,}", " ", n)))
        for frag in a.render_code_block(cl):
            f = a._norm(frag)
            probes.add(f)
            probes.add(re.sub(r"^#+\s*", "", f))
    leaked_like = frags[0].strip()          # the flagged line form
    n = a._norm(leaked_like)
    assert n in probes or re.sub(r"^#+\s*", "", n) in probes


def test_wrap_terminates_on_spaceless_long_line():
    """Regression (n24 closeout probe 2026-11-01): the pre-fix wrap searched
    for a break point over the WHOLE line width, could cut on a continuation
    line's own indent spaces, and looped forever on a >CODE_WRAP line with no
    usable space. Wrap must terminate and produce only non-empty fragments."""
    from pdf_rencode_maps import wrap_code_lines, CODE_WRAP
    line = "# " + "x" * (CODE_WRAP + 44)
    out = wrap_code_lines(line)          # must RETURN (the old code hung)
    frags = out.splitlines()
    assert len(frags) >= 2
    assert all(f.strip() for f in frags)
    # no character lost across the wrap (spaces are where the breaks happen)
    assert "".join(f.replace(" ", "") for f in frags) == line.replace(" ", "")


# ---------------------------------------------------------------------------
# n25 addendum (2026-11-01): D5 leaked-table-row detector + budget ratchet.
# The detector must catch the real CG-2 leak shape from the shipped v1.15
# PDF and must NOT flag the intentional quoted review rows (the pipe rows
# inside '> | ... |' blockquotes) — those render with pipes by design.
# ---------------------------------------------------------------------------

CG2_LEAK_SHAPE = ("| CG-2 | a resurrected stale value in the prose (a value "
                  "that a later fix removed, reintroduced by a later edit) | this")
QUOTED_ROW_SHAPE = ("| Yukawa-only (no Gaussian peak) | 0.61 | 0.054 | "
                    "230 Gyr | 0.06 | YES")
QUOTED_ROW_SOURCE = ("> | Yukawa-only (**no** Gaussian peak) | 0.61 | 0.054 | "
                     "230 Gyr | 0.06 | **YES (max-core)** |")


def test_pipe_row_whitelist_recognizes_quoted_source():
    prefixes = apr.pipe_row_whitelist([QUOTED_ROW_SOURCE])
    assert prefixes
    # the wrapped PDF line IS a token prefix of the source line
    assert apr.is_leaked_table_row(QUOTED_ROW_SHAPE, set(), prefixes) is False


def test_pipe_row_detector_catches_d5_shape():
    # same whitelisted quoted row present — the CG-2 leak must STILL be caught
    prefixes = apr.pipe_row_whitelist([QUOTED_ROW_SOURCE])
    assert apr.is_leaked_table_row(CG2_LEAK_SHAPE, set(), prefixes) is True


def test_pipe_row_detector_rejects_normal_text_and_code():
    assert apr.is_leaked_table_row("a normal line | with one pipe", set(), []) is False
    assert apr.is_leaked_table_row("no pipes at all", set(), []) is False
    assert apr.is_leaked_table_row("| alone", set(), []) is False
    fenced = apr._norm(QUOTED_ROW_SHAPE)
    assert apr.is_leaked_table_row(QUOTED_ROW_SHAPE, {fenced}, []) is False


def test_budget_rise_without_evidence_is_defect():
    d = apr.budget_rise_defect("x.pdf", 75, {"marker_budget": 75,
                                             "marker_budget_prev": 70})
    assert d and "70" in d and "budget_rise_evidence" in d


def test_budget_rise_with_evidence_passes():
    j = {"marker_budget": 75, "marker_budget_prev": 70,
         "budget_rise_evidence": "evidence_n25/budget_attribution.txt"}
    assert apr.budget_rise_defect("x.pdf", 75, j) is None


def test_budget_flat_or_tightened_needs_no_evidence():
    assert apr.budget_rise_defect("x.pdf", 70, {"marker_budget": 70,
                                                "marker_budget_prev": 70}) is None
    assert apr.budget_rise_defect("x.pdf", 66, {"marker_budget": 66,
                                                "marker_budget_prev": 70}) is None
    # legacy jobs with no prev declared keep the old behaviour
    assert apr.budget_rise_defect("x.pdf", 99, {"marker_budget": 99}) is None


# ---------------------------------------------------------------------------
# n25 review-2 item 3: every rescue path of the matcher must be provably
# narrow — a TRULY-absent word must survive ALL rescues (word-set pass and
# glyph-fragment NOTE path included), not just the coverage variants already
# guarded by test_true_absence_still_caught. Fixtures use the real sentinel
# semantics of relax_tokens/canonical (non-ASCII -> '?', interior '?' -> '-',
# dropped σ leaves 'eff/m' on the PDF side).
# ---------------------------------------------------------------------------

def _hay(plain_hay):
    toks = apr.relax_tokens(plain_hay)
    return ({t.replace("-", "") for t in toks},
            {"".join(c for c in t if c.isalnum()) for t in toks},
            sorted({"".join(c for c in t if c.isalnum()) for t in toks}))


def test_wordset_pass_flags_true_absence():
    # 'hydrostatic' and 'equilibrium' genuinely absent from the PDF text:
    # they carry no glyph sentinel, so the glyph-fragment rule must not
    # excuse them, and the line stays a defect.
    plain = "the analysis includes hydrostatic equilibrium across the section grid"
    hay_norm, hay_stem, hay_sample = _hay(
        ["the", "analysis", "across", "the", "section", "grid"])
    r = apr.wordset_pass(plain, hay_norm, hay_stem, hay_sample)
    assert r is not None
    absent, glyph_frag, real_absent = r
    assert "hydrostatic" in real_absent and "equilibrium" in real_absent
    assert "hydrostatic" not in glyph_frag and "equilibrium" not in glyph_frag


def test_wordset_pass_rescues_glyph_fragments_only():
    # Real-world shape: source '?_eff/m' (canonical 'σ_eff/m'), PDF side
    # 'eff/m' after pdftotext drops σ entirely. The distinctive key '_eff/m'
    # is absent from the PDF token set, but its alphanumeric stem 'effm'
    # exists — extraction damage, NOT missing content: rescued as glyph
    # fragment (NOTE), real_absent empty. The same line WITH 'hydrostatic'
    # additionally absent must flag exactly that word: the rescue path must
    # not launder a true absence sitting next to a glyph artifact.
    hay_norm, hay_stem, hay_sample = _hay(
        ["the", "canonical", "eff/m", "value", "is", "tabulated",
         "across", "the", "section", "grid"])
    r = apr.wordset_pass(
        "the canonical ?_eff/m value is tabulated across the section grid",
        hay_norm, hay_stem, hay_sample)
    assert r is not None
    absent, glyph_frag, real_absent = r
    assert real_absent == [] and glyph_frag  # legitimate NOTE rescue
    r2 = apr.wordset_pass(
        "the canonical ?_eff/m hydrostatic value is tabulated across the grid",
        hay_norm, hay_stem, hay_sample)
    assert r2 is not None
    absent2, glyph_frag2, real_absent2 = r2
    assert real_absent2 == ["hydrostatic"]        # true absence survives ALL rescues
    assert "_eff/m" in glyph_frag2


def test_wordset_pass_no_distinctive_anchor_returns_none():
    assert apr.wordset_pass("a b c d e", set(), set(), []) is None


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("ALL PASS")
