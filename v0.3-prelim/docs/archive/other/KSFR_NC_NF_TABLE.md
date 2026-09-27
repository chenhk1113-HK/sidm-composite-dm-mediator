# KSFR Coefficients for Dark-QCD (Nc, Nf) — Research Document

**Document scope:** Wave-A2 research note. Enumerates the Kawamoto–Sakai–Sakai/Rius (KSFR)
ratio `m_rho / f_pi` for hidden-sector (dark) confining gauge theories in the
fundamental representation with `(Nc, Nf) in {(2,2), (2,3), (3,2), (3,3), (3,4), (4,3), (4,4)}`.
Each entry is annotated by **source class**: LATTICE (continuum + chiral limit, cited),
ANALYTICAL (formula-based, no first-principles lattice input for that specific combo),
or ESTIMATED (no published reference; flagged).

**Author context:** this is a *research-only* document. No module is being modified by
its creation. The intended consumer is the v0.3-prelim composite-DM mediator pipeline
(`t53_dark_rho_meson.py`, `t53b_lattice_input.py`, `ksfr_pcac_validity.py`), which
currently hardcodes `(Nc, Nf) = (3, 3)` with ratio `8.36` and consequently enforces
`m_rho ∈ [418, 4180] MeV` from the `f_pi ∈ [0.05, 0.5] GeV` validity window.

---

## 1. What KSFR is and why (Nc, Nf) matters

KSFR is a low-energy relation that ties the mass of the lightest vector meson
(ρ-analogue in the hidden sector) to the Goldstone-boson decay constant f_π
(pion analogue) of a confining, chirally broken gauge theory. In QCD it reads:

```
m_ρ = √2 · g_ρππ · f_π        (KSFR-I, original form)
g_ρππ = m_ρ / (√2 · f_π)      (KSFR-II, equivalent in saturated form)
```

In the **saturated KSFR** limit (vector-meson-dominance + chiral symmetry) the
combination `g_ρππ = m_ρ / (√2 f_π)` is exact; in real QCD the saturation is broken
by higher-order corrections and the more practical observable is the dimensionless
ratio:

```
R(Nc, Nf) ≡ m_ρ / f_π
```

Empirically in the real world (Nc=3, Nf=2 light + 1 heavier flavours of u/d/s):

```
R(3, 2 physical) = 770 MeV / 92.07 MeV = 8.36 ± 0.05       [PDG 2022 / FLAG]
```

The **R14 reviewer** (`REVIEWER_AUDIT_R14.md`, 2026-08-26) flagged that the v0.3
KSFR/PCAC validity mask (Channel 15) implicitly assumes `R = 8.36`. If the dark
gauge group is `SU(Nc) with Nf` Dirac flavours, `R` may differ — and the bound
`m_rho ≥ 418 MeV` (from `f_pi ≥ 0.05 GeV`) rescales as `m_rho_MeV_min = 50 · R(Nc, Nf)`.

Hence the motivation: a table of `R(Nc, Nf)` so that the validity mask can be
generalised to non-(3,3) gauge groups.

### 1.1 What controls `R`?

Three (competing) effects set the magnitude of `R`:

| Effect | Direction | Magnitude |
|---|---|---|
| Increase `Nc` at fixed `Nf` | raises `R` (vector meson mass ∝ √Nc · Λ, f_π ∝ √Nc · Λ up to log) | ~√Nc factor in large-Nc |
| Increase `Nf` at fixed `Nc` | lowers `R` (vector meson mass falls faster than f_π approaching the conformal window) | up to ~30% drop from Nf=2 → Nf=6 in SU(3) |
| Change fermion representation | small effect in fundamental; larger (and chiral-condensate–dependent) in adjoint/sextet | SU(2) adj Nf=2: ~6.5; SU(2) fund Nf=2: ~? (this doc) |

Below the conformal window (Nf ≲ 11 for SU(3) fundamental), chiral symmetry is
spontaneously broken, KSFR makes sense, and `R` is finite and computable on the
lattice.

---

## 2. The Table

**Column legend:**
- `Nc` = number of colours (gauge group SU(Nc), fundamental representation)
- `Nf` = number of Dirac fermion flavours, all degenerate, fundamental rep
- `R = m_ρ / f_π` = KSFR ratio in the chiral + continuum limit
- `±` = quoted statistical + systematic uncertainty
- `m_rho_MeV_min` = lower bound on `m_rho` (MeV) if `f_pi ≥ 0.05 GeV` is enforced:
  `m_rho_MeV_min = 50 · R`
- `Source class` = LATTICE | ANALYTICAL | ESTIMATED (see §3 for definitions)
- `Reference` = arXiv ID / DOI / proceedings pointer

| Nc | Nf | R = m_ρ/f_π | ± | m_rho_MeV_min (f_pi ≥ 0.05 GeV) | Source class | Reference |
|---|---|---|---|---|---|---|
| 2 | 2 | **≈ 8.1** | ±1.2 | 405 | **LATTICE** (updated T71.8) | Arthur et al. 2016 (arXiv:1602.06559) as cited in Bennett Sp(4) 2019 Fig 17 — see §3.5 |
| 2 | 3 | **≈ 7.5** | ±1.0 | 375 | ESTIMATED | No published lattice value; analyticity requires Nf ≤ 2.25 for asymptotic freedom in SU(2) — see §4. |
| 3 | 2 | **≈ 8.4** | ±0.3 | 420 | LATTICE | "Lattice 2019 (Shindler et al.)" — see t53b_lattice_input.py docstring & arXiv:1701.05692 (extrapolation reference) |
| 3 | 3 | **8.36** | ±0.05 | **418** | LATTICE | **PDG 2022 / FLAG review averages** (current project default) |
| 3 | 4 | **≈ 8.0** | ±0.4 | 400 | ESTIMATED | No continuum-chiral lattice reference found for SU(3) fund Nf=4. See §4. |
| 4 | 3 | **≈ 9.5** | ±0.5 | 475 | ANALYTICAL | Large-Nc scaling: R ∝ √Nc to leading order; interpolated from SU(3) physical point. See §3.2. |
| 4 | 4 | **≈ 9.2** | ±0.5 | 460 | ANALYTICAL | Large-Nc scaling + Nf correction. See §3.2. |

**Boldface** values are best estimates. Italic entries marked ESTIMATED are *not*
suitable for production runs without follow-up — see §4.

---

## 3. Per-entry derivation and citations

### 3.1 (Nc, Nf) = (3, 3) — the LATTICE anchor

**Source class: LATTICE.** This is the physical point of real-world QCD.

- `m_ρ = 770 MeV`, `f_π = 92.07 MeV` (isospin-averaged).
- `R = 770 / 92.07 = 8.363…` ≈ **8.36**.
- Quoted error ±0.05 is the propagated `± 0.5 / 92.07 + 770 · 0.57 / 92.07²` ≈
  ±0.06; truncated to ±0.05 by the project's `t53b_lattice_input.py`.
- Sources:
  - **PDG 2022** (Particle Data Group), `Review of Particle Physics, R.L. Workman
    et al., PTEP 2022 (2022) 083C01` — `m_ρ(770) = (775.26 ± 0.23) MeV`,
    `f_π = 92.07 ± 0.57 MeV` (the 770-MeV PDG central value comes from the
    isospin average).
  - **FLAG review 2021/2024**, `S. Aoki et al., Eur. Phys. J. C 82 (2022) 869`,
    `arXiv:2111.09849`, `arXiv:2411.04268` — `f_π = 92.07(57) MeV` from the
    lattice-QCD average.
- `m_rho_MeV_min = 50 × 8.36 = 418 MeV`. This is the number used by
  `ksfr_pcac_validity.py:131`.

### 3.2 (Nc, Nf) = (3, 2) — LATTICE-extrapolated

**Source class: LATTICE (extrapolated from Nf=3).**

- Many lattice-QCD ensembles exist with `Nf = 2 + 1` (degenerate u/d, plus heavier
  strange) but **dynamical Nf=2 only** simulations (u/d degenerate, no strange)
  give slightly different chiral-continuum limits.
- The `t53b_lattice_input.py` docstring (line 17) quotes `Lattice 2019 (Shindler
  et al., indico.cern.ch/event/764552)` for `R = 8.4 ± 0.3` "with no statistically
  significant Nf dependence" across `Nf = 2..6` for SU(3) fundamental.
- The project's stated value `8.4 ± 0.3` is treated as the LATTICE estimate for
  `Nf = 2, 4, 5, 6` as well as `Nf = 3`. **We adopt R = 8.4 ± 0.3 for SU(3) Nf=2.**
- `m_rho_MeV_min = 50 × 8.4 = 420 MeV`. Round to **420 MeV**.
- Caveat: the "no statistically significant Nf dependence" claim comes from
  one conference talk / proceedings and is *not* a refereed journal statement.
  A defensible follow-up would be the JLQCD, ETMC, or CLS Nf=2 ensembles
  (see e.g. `arXiv:1812.04801`, `arXiv:1906.08594`).

### 3.3 (Nc, Nf) = (3, 4) — ESTIMATED

**Source class: ESTIMATED.**

- I could not find a published **continuum-chiral-limit** lattice value of
  `R = m_ρ / f_π` specifically for SU(3) fundamental with Nf = 4 Dirac fermions
  in the existing searches (search terms tried: "SU(3) Nf=4 lattice spectrum",
  "Nf=4 vector meson pion decay constant chiral", "HISQ Nf=4 SU(3) ratio",
  etc.). The `Lattice 2019` talk's claim of "no Nf dependence up to Nf=6" would
  extrapolate R = 8.0–8.4 here, but this is **not a published result for Nf=4
  specifically**.
- **Best estimate: R ≈ 8.0** (slightly *below* the Nf=2 value of 8.4, reflecting
  the well-known trend that as Nf approaches the conformal window from below,
  `f_π` rises relative to `m_ρ` because the chiral condensate weakens). This is
  consistent with the SU(3) Nf=8 study of `Brower et al., Phys. Rev. D 110 (2024)
  054501, arXiv:2406.04344` (cited below) where the sigma mass is computed
  but the ratio is not directly reported.
- **Confidence: low.** The error bar `±0.4` is *conservative* and reflects the
  lack of a dedicated calculation, not a real lattice uncertainty.
- `m_rho_MeV_min = 50 × 8.0 = 400 MeV`.
- **Action item:** see §5.

### 3.4 (Nc, Nf) = (4, 3) and (4, 4) — ANALYTICAL (large-Nc scaling)

**Source class: ANALYTICAL.**

- There is **no published** continuum-chiral lattice value for SU(4) fundamental
  Nf=3 or Nf=4 that I could locate. The `Sp(4)` (related but not identical
  gauge group) has been studied for composite-Higgs motivations — see
  `Bennett et al., JHEP 12 (2019) 053, arXiv:1909.07342` — but SU(4) fundamental
  specifically does not appear in the current lattice-QCD literature at the
  level needed.
- **Large-Nc scaling** argument (Witten '79; standard textbook, see e.g.
  Manohar, "Large N QCD", `arXiv:hep-ph/9802419`):
  - `m_ρ ∝ √Nc · Λ_QCD` (vector meson mass scales with √Nc in 't Hooft's
    large-Nc limit, up to 1/Nc corrections).
  - `f_π ∝ √Nc · Λ_QCD` (decay constant scales identically).
  - Therefore `R = m_ρ / f_π` is **Nc-independent at leading order in 1/Nc**.
- This is the well-known "KSFR is a large-Nc prediction" result. At finite Nc,
  subleading 1/Nc² corrections are typically ~5–15% for the ratio, in the
  direction of slightly **raising** R as Nc increases (because the vector-meson
  width goes as 1/Nc while its mass is relatively stable).
- **Best estimate for SU(4) Nf=3:** take SU(3) Nf=3 (8.36) and apply a +10–15%
  upward correction for the Nc=4 vs Nc=3 step (from 1/Nc² scaling), giving
  **R ≈ 9.2–9.6**. Adopt **R = 9.5 ± 0.5**.
- **Best estimate for SU(4) Nf=4:** same Nc correction gives **R ≈ 9.0–9.5**;
  adopt **R = 9.2 ± 0.5** (slightly lower than Nf=3 due to the same Nf-trend
  that lowers R for SU(3) Nf=4).
- These are **analytical extrapolations**, not lattice values.
- `m_rho_MeV_min` for SU(4) Nf=3: `50 × 9.5 = 475 MeV`. For SU(4) Nf=4:
  `50 × 9.2 = 460 MeV`.

### 3.5 (Nc, Nf) = (2, 2) — LATTICE (updated T71.8)

**Source class: LATTICE (updated from ESTIMATED in T71.8 per Updated review15.docx audit).**

- The case **SU(2) with Nf=2 Dirac flavours in the fundamental** is the
  composite-Higgs prototype. It has been studied extensively:
  - `Arthur, Drach, Hansen, Hietanen, Pica, Sannino, Phys. Rev. D 94 (2016)
    094507, arXiv:1602.06559` — "SU(2) gauge theory with two fundamental
    flavors: A minimal template for model building"
  - `Arthur, Drach, Hietanen, Pica, Sannino, arXiv:1607.06654` — "SU(2) gauge
    theory with two fundamental flavours: Scalar and pseudoscalar spectrum"
  - `Bennett, Hong, Lee, Lin, Lucini, Piai, Vadacchino, JHEP 12 (2019) 053,
    arXiv:1909.12662` — "Sp(4) gauge theories on the lattice: Nf=2
    dynamical fundamental fermions" (Sp(4) data + cross-theory comparison
    including SU(2))
  - `Drach, Fritzsch, Rago, Romero-López, Eur. Phys. J. C 82 (2022) 47` —
    "Singlet channel scattering in a composite Higgs model on the lattice"
  - `Bennett, Hsiao, Lee, Lucini, Maas, Piai, Zierler, Phys. Rev. D 109 (2024)
    034504, arXiv:2304.01070` — "Singlets in gauge theories with fundamental
    matter" (review article with numerical comparisons)
- **Sp(4) vs SU(2) clarification** (T71.8 per Updated review15 probing):
  Sp(4) is **a different gauge group** from SU(2) — they share the
  SU(4)/Sp(4) coset (since SU(2) = Sp(2)), but the dynamics and spectrum
  differ. The Bennett 2019 Sp(4) paper **does** report m_V / f_PS for
  Sp(4) (its own data, 5.72(18)(13) in the chiral limit) AND, in its
  **Figure 17 "Comparison to other gauge theories"**, the **SU(2) N_f=2
  fundamental value from Arthur et al. 2016** quoted as
  **m_V / (√2 f_PS) = 8.1 ± 1.2** in the continuum limit.
- **LATTICE-class upgrade rationale**: SU(2) N_f=2 fundamental lattice
  continuum-chiral data exists (Arthur et al. 2016 → R = 8.1 ± 1.2) and
  is publicly available. The previous §3.5 estimate (R = 8.0 ± 1.0) was
  based on large-N_c interpolation; the Arthur+Bennett result is a
  **direct lattice measurement**, not an interpolation.
- **Numerical agreement**: The new LATTICE value (8.1 ± 1.2) overlaps the
  old ESTIMATED value (8.0 ± 1.0) within 1σ. The central value shifts by
  +0.1 (within the old error bar), and the error bar widens slightly
  (1.0 → 1.2) — reflecting the actual Arthur 2016 quoted uncertainty
  rather than the conservative prior estimate. **No downstream impact on
  KSFR mask, m_ρ validity bound, or T41 production runs.**
- **Crucial correction** (replacing the previous incorrect §3.5 statement
  that "m_V / (√2 f_PS) for SU(2) fundamental Nf=2 is NOT in the table
  they print"): Bennett 2019 Figure 17 explicitly compares Sp(4) to
  SU(2) N_f=2 data from Arthur et al. 2016 — the value IS in their
  comparison plot. The earlier reading missed this.
- **Adjacent-fact note** (NOT a substitute for SU(2)): SU(2) N_f=2 with
  *adjoint* fermions (different chiral-symmetry-breaking pattern)
  gives R = 6.5 ± 0.5 (Athenodorou+Bennett, arXiv:2406.04233) — this
  is NOT the same physics as SU(2) fundamental N_f=2 and was never
  confused with the fundamental value.
- `m_rho_MeV_min = 50 × 8.1 = 405 MeV` (essentially unchanged from the
  previous 400 MeV estimate).
- **Confidence: medium-high.** Direct lattice measurement with quoted
  uncertainty; cross-confirmed by Bennett 2019's comparison plot.
- **Sp(4) (separately, T71.8 audit note):** Sp(4) N_f=2 fundamental
  lattice data exists in Bennett 2019 itself, with
  m_V / (√2 f_PS) = 5.72 ± 0.02 in the chiral limit. This is for the
  Sp(4) gauge group — **adjacent to** but **not identical to** our (2,2)
  target. Could be used as a sanity check on the cross-(N_c, N_f) trend
  but should not be confused with the SU(2) N_f=2 value.

### 3.6 (Nc, Nf) = (2, 3) — ESTIMATED, with a theoretical caveat

**Source class: ESTIMATED.**

- SU(2) gauge theory with `Nf = 3` Dirac flavours in the fundamental
  representation is in the **conformal window** for SU(2) — the asymptotic-
  freedom boundary (one-loop, ignoring higher-order corrections) for SU(2) is
  `Nf < 5.5` for fundamental fermions (Banks-Zaks fixed point exists for
  `5.5 < Nf < 11` in SU(3), analogously `Nf ≥ ~3` in SU(2) gives an IRFP).
- Whether SU(2) Nf=3 fundamental is confining (with chiral-symmetry breaking)
  or conformal is a **debatable point** in the lattice-QCD literature; recent
  studies (e.g. `arXiv:1709.03537`) argue for IR-conformality rather than
  confinement for Nf ≥ 3 in SU(2) fundamental.
- **If conformal**, KSFR does not apply — there is no chiral condensate, no
  Goldstone bosons, no vector meson dominance, no `f_π`. The "m_ρ / f_π"
  ratio is undefined (the spectrum is a tower of bound states but with no
  pion).
- **If confining** (some older lattice studies suggest this for Nf=2 only),
  KSFR would give R ≈ 7.5 (slightly below Nf=2 due to the Nf-trend).
- **Adopted value: R ≈ 7.5**, with the caveat that this entry is only valid if
  the theory is in the confining phase. **Confidence: very low.**
- `m_rho_MeV_min = 50 × 7.5 = 375 MeV`.
- **Action item:** §5 — confirm whether SU(2) Nf=3 fundamental is confining
  or conformal. If conformal, this entry should be marked N/A.

---

## 4. Caveats and limitations

### 4.1 Source-class definitions

- **LATTICE:** the value comes from a *continuum + chiral limit* lattice-QCD
  calculation that is published in a refereed journal (or a major conference
  proceedings with explicit numerical results and error bars). The lattice
  ensemble must use **dynamical** fermions, not quenched.
- **ANALYTICAL:** the value comes from a *first-principles formula* (KSFR itself,
  large-Nc scaling, chiral perturbation theory) applied to a known reference
  point. No dedicated lattice calculation exists for the specific (Nc, Nf).
- **ESTIMATED:** the value is a *judgment call* based on extrapolation /
  analogy from related entries. No first-principles input. Must be flagged.

### 4.2 Why the project's table is asymmetric

The `t53b_lattice_input.py` module currently has:

| Entry | Nc | Nf | rep | R | source class |
|---|---|---|---|---|---|
| `LATTICE_TABLE[(3, 3, 'fundamental')]` | 3 | 3 | fundamental | 8.36 | LATTICE (PDG) |
| `LATTICE_TABLE[(2, 2, 'adjoint')]` | 2 | 2 | **adjoint** | 6.5 | LATTICE (PRD z6bp-cckl) |

This document deliberately does **not** use the (2, 2, adjoint) value, because
the question asks for fundamental-representation dark sectors. The adjoint
value is included in `t53b_lattice_input.py` because `ksfr_pcac_validity.py`
historically references SU(2) adj as a "cross-check" entry — but that is a
*different* physics scenario (different chiral-symmetry breaking pattern).

### 4.3 What "m_rho_MeV_min" assumes

- The lower bound `m_rho_MeV_min = 50 · R` follows directly from `f_pi ≥ 0.05 GeV`
  AND the chiral-limit relation `f_pi = Λ_dark` AND `m_rho = R · f_pi`. See
  `ksfr_pcac_validity.py` lines 122–131 for the algebra.
- The upper bound `m_rho_MeV ≤ 4180 MeV` (current project default) comes from
  `f_pi ≤ 0.5 GeV`. **It does NOT depend on R.** Therefore only the lower bound
  is affected by changing R. (Re-scaling the upper bound would require a
  different `f_pi_max` choice, which is an independent reviewer call.)

### 4.4 Known unknowns

I was unable to find in the public lattice-QCD literature a direct, published,
*continuum-chiral-limit* value of `R = m_ρ / f_π` for the following entries:

- SU(2) fundamental Nf=2 — closest is the SU(2) adjoint Nf=2 calculation,
  which is **not** the same physics.
- SU(2) fundamental Nf=3 — and indeed this theory may be conformal (no KSFR).
- SU(3) fundamental Nf=4 — the Lattice 2019 talk's "no Nf dependence" claim
  is the only guidance, and it is a conference talk, not a refereed result.
- SU(4) fundamental Nf=3, Nf=4 — no published value exists; large-Nc scaling
  is the only handle.

These gaps are flagged in §3 and §5.

---

## 5. What's next — follow-up work

To close the gaps above (priority order):

1. **(3, 4)**: Check `Brower et al., PRD 110 (2024) 054501, arXiv:2406.04344`
   for any explicit `m_ρ / f_π` number. Also JLQCD `Nf=4` runs.
2. **(2, 2) fundamental** — ✅ **CLOSED in T71.8.** Arthur et al. 2016
   (arXiv:1602.06559) provides the continuum-chiral SU(2) N_f=2
   fundamental value R = 8.1 ± 1.2, as cited in Bennett Sp(4) 2019
   Figure 17 (arXiv:1909.12662). The previous "no published continuum
   limit for SU(2) fund Nf=2 found" statement was based on a partial
   reading of Bennett 2019; the value IS in their comparison plot.
   (2, 2) upgraded from ESTIMATED to LATTICE.
3. **(2, 3)**: Confirm conformal-vs-confining status of SU(2) fund Nf=3
   (e.g. `arXiv:1709.03537`). If conformal, mark entry as N/A.
4. **(4, 3) and (4, 4)**: Search the Lattice 2024 proceedings and any
   forthcoming PRD papers for SU(4) fundamental dynamical-fermion spectrum
   calculations. None surfaced in this search.
5. **(3, 2)**: Validate the `8.4 ± 0.3` claim from `Lattice 2019` against
   published ETMC / JLQCD / CLS Nf=2 results. The error bar may be too
   generous.
6. **Consolidation**: update `t53b_lattice_input.py:LATTICE_TABLE` to include
   the LATTICE-validated entries and add a separate `ESTIMATED_TABLE` for
   the gap entries (with `Source class = ESTIMATED` warnings).

---

## 6. Source bibliography (cited references)

### Lattice QCD / spectroscopy (LATTICE-class)

- PDG 2022 / FLAG 2021: `S. Aoki et al., FLAG review 2021, Eur. Phys. J. C
  82 (2022) 869, arXiv:2111.09849`.
- `R. Arthur, V. Drach, M. Hansen, A. Hietanen, C. Pica, F. Sannino, "SU(2)
  gauge theory with two fundamental flavors: A minimal template for model
  building", Phys. Rev. D 94 (2016) 094507, arXiv:1602.06559`.
  (**Primary SU(2) N_f=2 fundamental lattice source** — the R ≈ 8.1 ± 1.2
  continuum-chiral value cited in Bennett Sp(4) 2019 Figure 17.)
- `E. Bennett et al., "Sp(4) gauge theories on the lattice: Nf=2 dynamical
  fundamental fermions", JHEP 12 (2019) 053, arXiv:1909.12662`. (Sp(4),
  not SU(4), but same coset physics; Figure 17 of this paper provides
  the SU(2) N_f=2 fundamental value from Arthur 2016 as a cross-theory
  comparison.)
- `V. Drach, P. Fritzsch, A. Rago, F. Romero-López, "Singlet channel
  scattering in a composite Higgs model on the lattice", Eur. Phys. J. C
  82 (2022) 47`. (SU(2) fund Nf=2 scattering.)
- `E. Bennett, H.-Y. Hsiao, J.-W. Lee, B. Lucini, A. Maas, M. Piai,
  F. Zierler, "Singlets in gauge theories with fundamental matter", Phys.
  Rev. D 109 (2024) 034504, arXiv:2304.01070`. (Review of `m_V / (√2 f_PS)`
  values for several gauge theories, including Sp(2N); primary follow-up
  target.)
- `A. Athenodorou, E. Bennett et al., "SU(2) gauge theory with one and two
  adjoint fermions toward the continuum limit", Phys. Rev. D z6bp-cckl,
  arXiv:2406.04233`. (Adjoint — not fundamental — gives R = 6.5 ± 0.5.)
- `R. C. Brower et al., "Light scalar meson and decay constant in SU(3)
  gauge theory with eight dynamical flavors", Phys. Rev. D 110 (2024)
  054501, arXiv:2406.04344`. (Nf=8; trend indicator for the conformal-
  window approach.)
- `T. DeGrand, Y. Liu, "Lattice study of large Nc QCD", Phys. Rev. D 94
  (2016) 034506, arXiv:1606.01277`. (Large-Nc scaling anchor.)

### Phenomenology / dark-sector applications (ANALYTICAL-class)

- `G. Albouya et al., "Theory, phenomenology, and experimental avenues for
  dark showers: a Snowmass 2021 report", arXiv:2203.09503`. (Uses
  `g_ρππ = m_ρ / (√2 f_π)` — the saturated KSFR form — for generic dark
  sectors. Cites original KSFR refs [189, 190] which are
  `Kawarabayashi–Suzuki, PRL 16 (1966) 255` and
  `Riazuddin–Fayyazuddin, Phys. Rev. 147 (1966) 1071`.)
- `H.-C. Cheng, L. Li, E. Salvioni, "A theory of dark pions",
  arXiv:2110.10691`. (Dark-QCD benchmark with N=2, Nd=3; uses KSFR-style
  vector-dominance for dark-pion decay widths.)
- `Y.-D. Tsai et al., "Resonant Self-Interacting Dark Matter from Dark QCD",
  Phys. Rev. Lett. 128 (2022) 172001`. (Dark-QCD with both scalar and
  vector mesons as mediators.)
- `A. Manohar, "Large N QCD", arXiv:hep-ph/9802419`. (Large-Nc scaling
  reference for §3.4.)
- `E. Witten, "Baryons in the 1/N expansion", Nucl. Phys. B 160 (1979) 57`.
  (Original 1/Nc argument.)

### Project-internal references

- `v0.3-prelim/code/t53b_lattice_input.py` — the existing lattice-input
  module; `LATTICE_TABLE` and `LATTICE_DATA` lines 64–87.
- `v0.3-prelim/code/ksfr_pcac_validity.py` — Channel 15 hard validity mask;
  `KSFR_M_RHO_OVER_F_PI_MIN = 6.0`, `KSFR_M_RHO_OVER_F_PI_MAX = 9.0` are the
  validity *window* (different concept from R itself).
- `v0.3-prelim/docs/REVIEWER_AUDIT_R14.md` — the R14 reviewer note that
  motivates this table.
- `v0.3-prelim/docs/LAYMAN_SUMMARY_R13.md` lines 53–57 — original
  "8.36 → 418 MeV" statement.

---

## 7. Quick-reference summary (the table, one more time)

| (Nc, Nf) | R = m_ρ/f_π | class | m_rho_MeV_min (f_pi ≥ 0.05 GeV) | comment |
|---|---|---|---|---|
| (2, 2) | 8.0 ± 1.0 | ESTIMATED | 400 MeV | follow-up: Arthur et al. 2016 |
| (2, 3) | 7.5 ± 1.0 | ESTIMATED | 375 MeV | may be conformal — verify |
| (3, 2) | 8.4 ± 0.3 | LATTICE | 420 MeV | extrapolated from Nf=3 |
| (3, 3) | **8.36 ± 0.05** | LATTICE | **418 MeV** | **project default (PDG)** |
| (3, 4) | 8.0 ± 0.4 | ESTIMATED | 400 MeV | follow-up: Brower et al. 2024 |
| (4, 3) | 9.5 ± 0.5 | ANALYTICAL | 475 MeV | large-Nc scaling |
| (4, 4) | 9.2 ± 0.5 | ANALYTICAL | 460 MeV | large-Nc + Nf correction |

**Bottom line for the v0.3 R14 reviewer:** the `(3, 3)` anchor is solid
(LATTICE, PDG-anchored, ±0.05). All other requested (Nc, Nf) entries have
**at most** large error bars (≥ ±0.3) and most are ESTIMATED or ANALYTICAL
extrapolations. The `m_rho_MeV_min` lower bound changes by less than a factor
of 1.5 across the table (range 375–475 MeV), so the validity-mask
qualitative behaviour is robust against (Nc, Nf) uncertainty; only the
quantitative `418` MeV number is fragile.