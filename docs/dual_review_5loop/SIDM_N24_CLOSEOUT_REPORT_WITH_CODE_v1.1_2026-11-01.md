# SIDM v19.2-F — n24 Round Close-Out: Report With Code

**Date:** 2026-11-01. **Version:** v1.1 (supersedes v1.0; n25 caliber correction — consolidated-report §26.6). **Branch:** `wip/v19.2-F-init`. **Round commits:** `c507207` (fix(gate): gate layer 15 register-state audit, gate summary contract CG-5/CG-10, shared re-encode maps for layer 14, provenance date guard, both mutation proofs, unit tests), `4aa0039` (fix(paper): CG-8 stray-period class sweep, 8 whitespace-only fixes), `baa21a3` (fix(audit): PDF-render audit containment model — the subject of §2 and §4 below). **Companion report:** `SIDM_ROUND5_CONSOLIDATED_FIXES_v1.15_2026-10-31.pdf` (the full n24 adjudication, §§25.1–25.10). This document is the code-level close-out: every claim below is a measured run output, and the code that produced it is reproduced verbatim in §4.

## 1. The eight n24 items — one line each

| # | Reviewer item | Disposition | Where |
|---|---|---|---|
| 1 | Report's own register-vs-prose state not machine-checked (the class that produced all four n23 findings) | **DONE** — gate layer 15 `audit_register_state.py` + 4-run mutation proof; live/frozen split so superseded round records are exempt by design | §25.1, `c507207` |
| 2 | §22.3's crash-semantics dismissal rests on code-reading, not evidence | **DONE** — `verify_gate_crash_mutation_proof.py`: a killed layer turns the gate red end-to-end | §25.2, `c507207` |
| 3 | Layer 14's substitution tables hand-copied from the builder (drift trap) | **DONE** — both sides now import one shared module `pdf_rencode_maps.py` | §25.3, `c507207` |
| 4 | CG-2 row lacks its explicit scope statement | **DONE** — exact-string scope written into the register row itself | §25.4, `c507207` |
| 5 | Literal-`**` number family scattered (199/179/70/5-8/56/62/55-57) | **DONE** — reconciliation table, six objects one place; extended this round with the v1.15 measurement (70) | §25.6 |
| 6 | Supersedes chain noted for three rounds while growing | **DONE** — relocated verbatim to Appendix A; front matter carries only the net delta | §25.7, Appendix A |
| 7 | Gate summary reads as a whole-document verdict; skipped tests count as PASS | **DONE** — summary contract: layers named, skips disclosed, fixed SCOPE sentence; `--quick` can never print PASS | §25.5, `c507207` |
| 8 | CG-8 two quoted typos; "5 vs 6" namespaces ambiguity | **DONE** — class sweep found 8 live instances (whitespace-only fixes, 1 truncation recorded not rewritten); namespace caliber pinned by footnote | §25.4/§25.7, `4aa0039` |

No scientific content changed. The paper was touched only by the whitespace sweep.

## 2. The close-out round's own find: 8 containment flags on the v1.15 build, all checker bugs

Building this round's PDF and re-running gate layer 11 (`audit_pdf_render.py`) flagged **8 source prose lines as missing from the PDF**. Ground-truth extraction (pdfplumber token streams) proved the PDFs correct and the **checker** wrong, twice:

1. **Fold gap.** The builder ASCII-folds super/subscripts at build time (`pdf_rencode_maps.SUP/SUB`: `10⁻¹²` drawn as `10-12`, `f_H²σ` as `f_H2σ`). The rendered PDFs contain fused tokens — `7.5x10-12`, `f_H2?_HH` — verbatim. The audit's token model generated only split fragments (`7.5x10 | 12`) and never the fused spelling, so correct rendering read as missing content.
2. **Tail asymmetry.** The caret branch emitted fragments raw, skipping the shared tail normalization (`?` mapping, edge-strip, lowercase) every other token gets: source `"7.5x10^-12` (curly quote glued on) kept its quote edge while the PDF side had stripped it — guaranteed mismatch on a present token.

Fix (`baa21a3`, §4.1–4.3): fuse-variant modelling scored **per variant** (variant-max; merging variants was measured to dilute coverage and even spawned a new false flag in the first patch iteration), fused-aware third-pass anchors, shared `tail()` on every emitted variant, `relax_tokens` lifted to module level for direct unit testing.

Verification (all re-run after the fix, not carried over):

| Check | Result |
|---|---|
| Frozen v1.14 pair (git-declared byte-frozen known-good input) | **PASS, 0 defects** — was 8 with the pre-fix checker: direct before/after |
| Live v1.15 pair | **0 containment defects**; only the documented per-build budget annotation (measured 70 = budget 70) |
| Unit suite `test_pdf_render_relax.py` | **6/6 PASS** incl. a true-absence negative control — a genuinely missing exponent is still flagged by both variants |
| Full 15-layer gate, pre-commit run (tree `4aa0039`) | **15/15 PASS** — 1914 passed, 22 skipped (disclosed), 36 deselected; wall 28m44s; `--quick` never used |

The honesty boundary: the fold model matches **this builder's** maps; a builder drawing true raised-baseline superscripts exercises the split variant instead — both worlds are modelled, and the negative control guards the boundary between them.

## 3. Reproduction commands

```
python v0.3-prelim/tests/test_pdf_render_relax.py
python scripts/audit_pdf_render.py docs/dual_review_5loop/evidence_n24/jobs_v114_frozen.json
python scripts/audit_pdf_render.py
python scripts/audit_register_state_mutation_proof.py
python scripts/verify_gate_crash_mutation_proof.py
python scripts/verify_release_gate.py
```

Evidence captured in `docs/dual_review_5loop/evidence_n24/` (README lists expected outputs): `gate_run_final.txt`, `gate_run_committed.txt`, `pdf_audit_frozen_v114.log`, `pdf_audit_v115_final.log`, `test_relax_units.txt`, `jobs_v114_frozen.json`.

## 4. The code

Every fenced block below is pre-folded through the builder's own mono re-encoding (`pdf_rencode_maps.SUP/SUB/MONO_FALLBACK`, the same transform the PDF builder applies to code blocks), because the PDF can only ever *display* the folded form — embedding the unfolded source guarantees the render audit compares the PDF against the bytes the PDF actually contains (AGENTS.md rule 27). The fold only ever rewrites Unicode superscripts/subscripts and typographic dashes to ASCII; all identifiers, logic, and text are character-identical to the repo files (`scripts/…py`) otherwise. Em dashes inside listings are written as `--`: the pdftotext extractor reads the drawn em dash as `--`, and writing `--` in the source makes the markdown, the PDF and BOTH text extractors agree on one spelling.

### 4.1 `relax_tokens` — the fixed token model (verbatim, `scripts/audit_pdf_render.py`)

```python
FMT_TOKEN = re.compile(r"^[*'`]+$")
EDGE_STRIP = re.compile(r"^[^0-9A-Za-z\u0391-\u03c9-]+|[^0-9A-Za-z\u0391-\u03c9-]+$")
def relax_tokens(toks, fuse=False):
    """Relaxed-pass token normaliser, applied IDENTICALLY to both sides.

    Side facts established by direct extraction (2026-10-28, live PDFs):
      * pdftotext DROPS some rendered glyphs entirely (U+2032 prime, the
        σ before '_'): they leave NO token -- e.g. source 'U(1)?\".' vs PDF
        'U(1)\".'; source '?_eff/m' (sigma_eff/m) vs PDF 'eff/m' after the
        empty token is dropped.
      * other glyphs extract as '?': en-dash inside a word
        ('Girmohanta-Yasuoka' -> 'Girmohanta?Yasuoka'), →, §.
    Because canonical() maps EVERY non-ASCII to '?' on both sides, the
    relaxed pipeline is side-agnostic by construction:
      1. drop pure-punctuation (* `) tokens;
      2. map interior '?' -> '-' (both sides; a source-internal '?' is
         itself a sentinel, and sigma/2 sentinels sit at token EDGES --
         'σ_eff' tokenises as '?_eff' -- so this never erases them, it
         only aligns en-dash ligatures like 'Girmohanta?Yasuoka' with the
         source's ASCII-hyphen 'Girmohanta-Yasuoka');
      3. strip every edge character outside [alnum, hyphen, ?-sentinel-
         interiors already handled] -- this removes the '?' a dropped prime
         leaves on the source edge ('U(1)?' -> 'U(1)') and quote runs on
         either side;
      4. lowercase both sides (case is formatting, not content);
      5. drop tokens that end up empty, restoring word adjacency.
    Strict pass is untouched. A relaxed-only match is a NOTE, not a defect.
    """
    out = []
    def tail(s):
        # Shared tail normalization, applied to EVERY emitted variant so the
        # caret branch and the caret-free path are symmetric (n24 round fix:
        # the caret branch used to `continue` with raw fragments, skipping
        # '?'->'-', edge-strip and lower -- the source's fused token kept a
        # quote edge the PDF side had already stripped, so a present token
        # ('"7.5x10-12' vs '7.5x10-12') read as absent).
        s = s.replace("?", "-")
        if set(s) == {"-"}:
            return ""
        s = EDGE_STRIP.sub("", s)
        s = s.lstrip("-")
        return s.lower()
    for t in toks:
        if FMT_TOKEN.match(t):
            continue
        # Caret handling, applied IDENTICALLY on both sides:
        #  (a) collapse caret runs (markdown '10^-12' expanded from '10-12'
        #      can leave '^^' when the source already used the rule-27
        #      ASCII form);
        #  (b) split exponent fragments so '10^-12' becomes 10 | -12 --
        #      the PDF draws superscripts at raised baseline and every
        #      extractor we measured (pdftotext AND pdfplumber) drops the
        #      '^' glyph itself: '10^-12' in the report renders as
        #      '10-12' tokens. Splitting on the caret restores adjacency.
        t = re.sub(r"\^{1,}", "^", t)
        if "^" in t:
            if fuse:
                # Builder-fold variant (n24 round, 2026-11-01): the report
                # builder maps super/subscripts to ASCII at BUILD time
                # (pdf_rencode_maps.SUP/SUB -- '10-12' is drawn as '10-12'
                # and 'f_H2sigma' as 'f_H2sigma'), so these PDFs carry the
                # exponent as ONE fused token. fuse=True emits the fused
                # form ('^' deleted, neighbours rejoined); fuse=False
                # keeps the split fragments for raised-baseline glyph
                # rendering. Both forms derive from the source token
                # itself; the caller scores each variant independently
                # (never merged -- merging dilutes coverage with stray
                # fragments of the other world).
                fused = tail(t.replace("^", ""))
                if fused:
                    out.append(fused)
            else:
                for frag in t.split("^"):
                    if not frag:
                        continue
                    f = tail(frag)
                    if f:
                        out.append(f)
            continue
        t = tail(t)
        if t:
            out.append(t)
    return out
```

### 4.2 Prose rescue — variant-max scoring (verbatim, call site)

```python
        cov, miss = _coverage(words, tri)
        # relaxed probe: same relax_tokens pipeline as the PDF side, scored
        # per variant. Split fragments model raised-baseline superscripts;
        # the fused variant models the builder's ASCII fold (see relax_tokens).
        words_r = relax_tokens(plain.split())
        cov_r, _ = _coverage(words_r, tri_r)
        words_r_f = relax_tokens(plain.split(), fuse=True)
        cov_r_f, _ = _coverage(words_r_f, tri_r)
        if max(cov_r, cov_r_f) >= PROSE_COVERAGE:
            artifact_prose.append((line, cov))
            continue
```

### 4.3 Third-pass anchors — fused spelling preferred when present (verbatim)

```python
        anchors = []
        for raw in plain.split():
            if "^" in raw:
                # Builder-folded world: when the FUSED spelling of a caret
                # token is present in the PDF ('f_h2?_hh', '7.5x10-12'), its
                # split fragments are layout artifacts of the caret form,
                # not absent words -- require the fused token instead. When it
                # is absent, fall back to the fragments (raised-baseline
                # rendering drops '^' and splits the token on the PDF side).
                fused_r = relax_tokens([raw], fuse=True)
                if fused_r and distinctive_key(fused_r[0]) in hay_token_set_norm_r:
                    anchors.extend(fused_r)
                else:
                    for seg in re.split(r"(?<=[0-9a-z])\^(?=[-+]?[0-9a-z])", raw):
                        seg_r = relax_tokens([seg])
                        anchors.extend(seg_r)
            else:
                anchors.extend(relax_tokens([raw]))
```

### 4.4 The unit suite (verbatim, `v0.3-prelim/tests/test_pdf_render_relax.py`)

```python
"""n24-round containment unit test (2026-11-01): exponent-fold semantics.

The report builder ASCII-folds super/subscripts at BUILD time
(pdf_rencode_maps.SUP/SUB: '10-12' -> '10-12', 'f_H2sigma' -> 'f_H2sigma'), so the
rendered PDFs carry the exponent as ONE fused token. audit_pdf_render's
relax_tokens must model BOTH rendering worlds -- split fragments for
raised-baseline glyphs, the fused form for the builder fold -- and score
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
    # canonical() maps unicode superscript 2 via the caret expansion; the
    # fold rejoins neighbours and tail() applies '?'->'-' + lowercase on
    # both variants symmetrically -- matching the builder-folded PDF token
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
    # variant may rescue it.
    pdf_tokens = ["the", "canonical", "value", "is", "inconsistent",
                  "regime", "labels", "differ"]
    tri_set = set(apr._trigrams(pdf_tokens))
    src = ["the", "canonical", "value", "10^-13", "is", "inconsistent",
           "regime", "labels", "differ"]
    cov_s, miss_s = apr._coverage(apr.relax_tokens(src), tri_set)
    cov_f, miss_f = apr._coverage(apr.relax_tokens(src, fuse=True), tri_set)
    assert miss_s > 0 and miss_f > 0
    assert cov_s < 0.90 or cov_f < 0.90


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("ALL PASS")
```

### 4.5 Code shipped earlier this round (in repo, not pasted)

`scripts/audit_register_state.py` (gate layer 15), `scripts/audit_register_state_mutation_proof.py`, `scripts/verify_gate_crash_mutation_proof.py`, `scripts/pdf_rencode_maps.py` (shared maps consumed by builder + layer 14), `scripts/verify_release_gate.py` summary-contract changes, `v0.3-prelim/tests/test_gate_summary_contract.py`, `v0.3-prelim/tests/test_pdf_render_pairing.py` — all in `c507207`. The CG-8 sweep is in `4aa0039` (8 one-character deletions in the paper file). **Caliber correction (n25, consolidated-report §26.6):** an earlier version of this document attributed those 8 deletions to `SIDM_SEARCHABLE_v19_2_F.md` — that file exists neither on disk nor anywhere in git history (`git log --all -- '*SEARCHABLE*'` returns empty); `git show 4aa0039 --stat` confirms the sweep touched only `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (8 insertions, 8 deletions, whitespace-only), the single canonical paper file that gate layer 13 reads.

## 5. What this close-out does not claim

- It does not claim the paper is scientifically verified by the gate: the gate asserts only its enumerated layers (the SCOPE sentence is printed by the gate itself).
- It does not claim layer 11 now catches every rendering defect class — it claims the two specific gaps witnessed this round are closed, with a unit-tested boundary.
- It does not re-open the hardcoded-paths gap (CG-16), which remains OPEN in the §17.3 register with an owner named; the deferred markup pass (CG-4) was closed in the v1.15 round (consolidated-report §25.5).

## 6. Version history (close-out)

**v1.0 (2026-11-01)** — as originally delivered. **v1.1 (2026-11-01, n25 round)** — supersedes v1.0: §4.5 filename attribution corrected (the phantom `SIDM_SEARCHABLE_v19_2_F.md` disproven via `git log --all`; the sweep actually touched `v0.3-prelim/docs/PAPER_V1_DRAFT.md`); CG-4 bullet synced to its v1.15 closure; no other content changed.
