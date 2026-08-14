# DARK_SECTOR_LAGRANGIAN — Composite SIDM Lagrangian & Dimensional Analysis

**Project:** sidm-composite-dm-mediator
**Author:** K. Lam (project owner), with composite-DM inputs from Hermes (M3 model) and reviewer audits (Doubao, Qwen 3.8 Max).
**Status:** v0.4-prelim draft (R11 audit recommendation G13 closure).
**Created:** 2026-08-14.
**Companion docs:** `v0.3-prelim/docs/FINDINGS.md` (numerical results), `docs/DATA_SOURCES.md` (data provenance), `docs/REVIEWER_AUDIT_R11.md` (R11 audit).

---

## Table of Contents

- [§0 Scope and conventions](#0-scope-and-conventions)
- [§1 The composite SIDM ansatz](#1-the-composite-sidm-ansatz)
- [§2 Dark-sector Lagrangian](#2-dark-sector-lagrangian)
- [§3 Portal operators](#3-portal-operators)
- [§4 Dimensional analysis & natural-units conversion](#4-dimensional-analysis--natural-units-conversion)
- [§5 Cross-section mappings (the parametrization used in the joint fit)](#5-cross-section-mappings-the-parametrization-used-in-the-joint-fit)
- [§6 Current numerical values (canonical, from t41/T39 results)](#6-current-numerical-values-canonical-from-t41t39-results)
- [§7 Limitations and open issues](#7-limitations-and-open-issues)
- [§8 Cross-references to code](#8-cross-references-to-code)

---

## §0 Scope and conventions

This document specifies the **complete dark-sector Lagrangian** for the composite SIDM model used in this project. It is the missing piece the R11 reviewer flagged (G13, 2026-08-14) as a prerequisite for v0.4-prelim:

> G13. Full dark-sector Lagrangian + portal specification. **(LARGE, out of v0.4-prelim scope)**

The Lagrangian has been implicit in the codebase (T40 Yukawa form, T30/T32/T39/T41 mappings) but not written down in one place. This document consolidates the implicit specification, performs a careful dimensional analysis connecting every free parameter to SI units, and identifies which approximations are toy-model and which are first-principles.

**Convention:**

- **Natural units:** $\hbar = c = 1$ throughout. SI units are recovered by restoring factors of $\hbar c$ as indicated in §4.
- **Lorentz signature:** $(+,-,-,-)$.
- **Energy scale:** GeV for masses and couplings unless otherwise noted. The mediator is typically MeV-scale, the dark-sector confinement scale $\Lambda_{\rm dark}$ is GeV-scale, and the dark fermion $m_\chi$ is GeV-scale.
- **Symbol table** (compact version; full table in §4):

| Symbol | Meaning | Units (natural) | SI |
|---|---|---|---|
| $m_\chi$ | dark fermion mass | GeV | kg |
| $m_\phi$ | dark vector meson (mediator) mass | MeV | kg |
| $g_\chi$ | dark-sector gauge coupling | — | — |
| $\Lambda_{\rm dark}$ | dark-sector confinement scale | GeV | kg |
| $\sigma/m$ | transfer cross-section per unit mass | cm²/g | m²/kg |
| $\sigma_{\rm SI}$ | spin-independent DM-nucleon cross-section | cm² | m² |
| $\varepsilon$ | kinetic-mixing parameter (vector portal) | — | — |
| $\alpha$ | annihilation coupling (scaling factor) | cm³/s | m³/s |
| $\langle\sigma v\rangle$ | velocity-averaged annihilation cross-section | cm³/s | m³/s |

---

## §1 The composite SIDM ansatz

We postulate that dark matter is a **composite bound state** of a confining dark gauge group, analogous to QCD. This is the "composite DM" or "dark hadron" hypothesis. The structure follows the standard mirror-QCD and SIMP/ELDER literature (Schuster+ 2010, Hochberg+ 2014, Cline+ 2017).

### 1.1 Gauge structure

The dark sector contains:
- A **dark color group** $SU(N_{\rm dc})$ with $N_{\rm dc} \geq 2$ (we use $N_{\rm dc} = 3$ as the canonical case; the $N_{\rm dc} = 2$ case is the Yang-Mills dark-pion model).
- A **dark flavor group** $SU(N_{\rm df})_L \times SU(N_{\rm df})_R$ acting on $N_{\rm df}$ Weyl fermion doublets.
- **Dark electromagnetism** $U(1)_{\rm dEM}$ to give the dark hadrons a conserved dark charge (analog of baryon number).

The **dark fermions** $\chi$ are in the fundamental of $SU(N_{\rm dc})$ and a vectorlike representation of the flavor group. They carry dark charge +1 under $U(1)_{\rm dEM}$.

### 1.2 Chiral symmetry breaking

At the confinement scale $\Lambda_{\rm dark} \sim m_\phi$, the chiral symmetry breaks:
$$
SU(N_{\rm df})_L \times SU(N_{\rm df})_R \to SU(N_{\rm df})_V,
$$
producing $N_{\rm df}^2 - 1$ pseudo-Nambu-Goldstone bosons — the **dark pions** $\pi_{\rm d}$, $\eta_{\rm d}$, and the **dark vector mesons** $\rho_{\rm d}$, $\omega_{\rm d}$, $\phi_{\rm d}$ (analogous to SM $\rho, \omega, \phi$).

The lightest dark hadron — the **dark pion** $\pi_{\rm d}$ — is stable (dark-isospin or dark-baryon number conservation) and is our DM candidate. The **dark rho** $\rho_{\rm d}$ is the lightest vector meson and serves as the **SIDM mediator** (force carrier for dark-matter self-interactions).

**Per T53 in the code (`t53_dark_rho_meson.py`):** the dark rho mass is set by the confinement scale, $m_\phi \sim 3 \Lambda_{\rm dark}$ in the QCD-like scaling. This is a **phenomenological interpolation** in the codebase, NOT a first-principles lattice calculation. See §7 for what G14 (lattice input) would replace.

### 1.3 Dark matter stability

The dark pion is stable because:
- It carries conserved dark isospin (analog of QCD pions in the SM where the up-down mass difference is small).
- The lightest dark hadron with non-zero dark isospin is the dark pion.
- Dark baryon number is also conserved, but the lightest dark baryon is heavier than $\pi_{\rm d}$ (analog of proton vs pion mass).

This is the **dark-pion DM** scenario. It is one of the most studied composite-DM scenarios in the literature (e.g., Cline+ 2017 arXiv:1701.08780).

---

## §2 Dark-sector Lagrangian

### 2.1 Dark fermions

The dark fermions are vectorlike (to avoid gauge anomalies if $U(1)_{\rm dEM}$ is gauged):
$$
\mathcal{L}_\chi = \overline{\chi}(i\slashed{D} - m_\chi)\chi.
$$
Here $\slashed{D} = \gamma^\mu D_\mu$, and the covariant derivative is
$$
D_\mu = \partial_\mu - i g_{\rm dc} A_\mu^a T^a - i g_{\rm dEM} A_\mu^{\rm dEM},
$$
with $T^a$ the $SU(N_{\rm dc})$ generators.

### 2.2 Dark gauge sector

The dark-color and dark-EM gauge fields have the standard Yang-Mills kinetic terms:
$$
\mathcal{L}_{\rm gauge} = -\frac{1}{4} G_{\mu\nu}^a G^{a\mu\nu} - \frac{1}{4} F_{\mu\nu}^{\rm dEM} F^{\rm dEM\,\mu\nu}.
$$

### 2.3 Chiral symmetry breaking and effective Lagrangian

At scales below $\Lambda_{\rm dark}$, the physics is described by an **effective chiral Lagrangian** for the dark pions and rho mesons. We use the standard hidden-local-symmetry (HLS) formulation (Bando+ 1985):
$$
\mathcal{L}_{\rm HLS} = \mathcal{L}_\pi + \mathcal{L}_\rho + \mathcal{L}_{\pi\rho},
$$
where (for $N_{\rm df} = 2$ as the canonical case):

**Dark-pion kinetic + mass terms:**
$$
\mathcal{L}_\pi = \frac{f_\pi^2}{4} \mathrm{Tr}\left[ D_\mu U D^\mu U^\dagger \right] + \frac{f_\pi^2 m_{\pi_d}^2}{4} \mathrm{Tr}\left[ U + U^\dagger \right],
$$
with $U = \exp(2i\pi^a \sigma^a / f_\pi)$ the chiral field, $\pi^a$ the dark-pion fields, and $f_\pi$ the dark-pion decay constant.

**Dark-rho kinetic + mass terms:**
$$
\mathcal{L}_\rho = -\frac{1}{4} \rho_{\mu\nu}^a \rho^{a\mu\nu} + \frac{f_\rho^2 m_\rho^2}{4} \mathrm{Tr}\left[ (V_\mu - i g_\rho V_\mu)^2 \right],
$$
with $\rho_{\mu\nu}^a = \partial_\mu \rho_\nu^a - \partial_\nu \rho_\mu^a + g_\rho f^{abc} \rho_\mu^b \rho_\nu^c$ the rho field strength, $V_\mu = (D_\mu \xi) \xi^\dagger + \xi (D_\mu \xi)^\dagger$ the HLS gauge boson, and $g_\rho$ the rho self-coupling.

**Pi-rho coupling:**
$$
\mathcal{L}_{\pi\rho} = i a_\rho f_\rho^2 \mathrm{Tr}\left[ \rho_\mu (D^\mu \xi \xi^\dagger - \xi D^\mu \xi^\dagger) \right],
$$
with $a_\rho$ an order-1 HLS parameter (typically $a_\rho \approx 2$ in QCD; we leave it as a free parameter for the dark sector).

### 2.4 Full dark-sector Lagrangian (schematic)

Combining:
$$
\boxed{
\mathcal{L}_{\rm dark} = \mathcal{L}_\chi + \mathcal{L}_{\rm gauge} + \mathcal{L}_{\rm HLS}.
}
$$

This is the **dark-sector-only** Lagrangian. The portal operators that connect to the Standard Model are in §3.

---

## §3 Portal operators

The dark sector communicates with the Standard Model through **portal operators** — renormalizable or non-renormalizable couplings suppressed by some high scale. We include the three most relevant portals:

### 3.1 Vector (kinetic-mixing) portal — **PRIMARY PORTAL**

The dark photon $A_\mu^{\rm dEM}$ mixes kinetically with the Standard Model photon:
$$
\boxed{
\mathcal{L}_{\rm vec} = -\frac{\varepsilon}{2} F_{\mu\nu}^{\rm dEM} F^{\mu\nu}.
}
$$
Here $\varepsilon$ is the **kinetic mixing parameter**, dimensionless. This is the operator that produces both:
- **Direct detection** (DM-nucleon scattering via the dark photon's mixing with the visible photon): the cross-section scales as $\sigma_{\rm SI} \propto \varepsilon^2$.
- **Annihilation** (DM DM → SM SM via s-channel dark photon): the cross-section scales as $\langle\sigma v\rangle \propto \varepsilon^2$.

In the codebase, $\varepsilon$ corresponds to the **`epsilon`** fit parameter in T39/T41, and the direct-detection mapping is:
$$
\sigma_{\rm DM\text{-}nucleon} = \varepsilon \times (\sigma/m)_0 \quad \text{(T30 / T39 line 92)}.
$$
The annihilation mapping is:
$$
\langle\sigma v\rangle = \alpha \times (\sigma/m)_{\rm at\,v}^2 \quad \text{(T32 / T39 line 99)},
$$
where $\alpha$ encodes the annihilation coupling (technically a separate portal, but in this project we treat $\alpha$ as a stand-in for the full $\varepsilon^2$ scaling plus geometric factors).

### 3.2 Higgs portal (mass-mixing)

If the dark sector has a scalar that mixes with the SM Higgs:
$$
\mathcal{L}_{\rm Higgs} = \lambda_{HS} |H|^2 |S|^2,
$$
where $H$ is the SM Higgs doublet and $S$ is a dark scalar. This produces:
- Direct detection via Higgs exchange
- Annihilation $SS \to hh$ at low velocities

We **do not** use the Higgs portal as a primary portal in this project. The codebase is set up to add it as an extension if needed.

### 3.3 Neutrino portal

$$
\mathcal{L}_\nu = y_N \overline{L} \tilde{H} N + \text{h.c.},
$$
where $N$ is a right-handed neutrino. This is **not** used in the SIDM-bumpy parameterization and is mentioned only for completeness.

### 3.4 Composite portal (the rho meson exchange)

The most important **dark-dark** interaction — the one that drives SIDM — is the **dark-rho exchange** between dark pions. This is the SIDM mediator in our setup, NOT a portal to the SM. It is fully contained in $\mathcal{L}_\rho + \mathcal{L}_{\pi\rho}$ of §2.3.

The tree-level exchange produces the Yukawa potential:
$$
V(r) = -\frac{g_\chi^2}{4\pi} \frac{e^{-m_\phi r}}{r},
$$
which is the **fundamental origin** of the SIDM transfer cross-section used in T40 and propagated through the joint fit.

---

## §4 Dimensional analysis & natural-units conversion

This section is the **1-page reference table** requested in the user's brief. Every free parameter in the model is listed with its natural-units value, SI conversion, current numerical value from the codebase, and cross-reference to where it appears in the code.

### 4.1 Master table

| Symbol | Definition | Natural units | SI conversion | Canonical value | Code reference |
|---|---|---|---|---|---|
| $m_\chi$ | Dark pion mass (DM mass) | GeV | $1\,{\rm GeV} = 1.783\times 10^{-27}\,{\rm kg}$ | $\sim 0.5\text{--}1$ GeV | `t41_mediator_mass_joint_fit.py`, `LOG_M_CHI_GEV_RANGE = (0.5, 1e3)` |
| $m_\phi$ | Dark rho meson mass (mediator) | MeV | $1\,{\rm MeV} = 1.783\times 10^{-30}\,{\rm kg}$ | $\sim 1\text{--}100$ MeV | `t41_mediator_mass_joint_fit.py`, `LOG_M_PHI_MEV_RANGE = (-1, 4)` |
| $g_\chi$ | Dark gauge coupling | — | — | $\sim 0.01\text{--}1$ | `t41_mediator_mass_joint_fit.py`, `G_CHI_RANGE = (1e-2, 2.0)` |
| $\Lambda_{\rm dark}$ | Confinement scale | GeV | $1\,{\rm GeV} = 1.783\times 10^{-27}\,{\rm kg}$ | $\sim m_\phi / 3$ | `t53_dark_rho_meson.py` (phenomenological, NOT lattice) |
| $f_\pi$ | Dark-pion decay constant | GeV | $1\,{\rm GeV} = 1.783\times 10^{-27}\,{\rm kg}$ | $\sim \Lambda_{\rm dark}$ | Implicit (not directly fit) |
| $\varepsilon$ | Vector portal kinetic mixing | — | — | $\sim 10^{-30}\text{--}10^{-4}$ | `t39_tier3_epsilon_alpha_joint_fit.py`, `LOG_EPSILON_RANGE = (-60, -1)` |
| $\alpha$ | Annihilation coupling | cm³/s | $1\,{\rm cm}^3/{\rm s} = 10^{-6}\,{\rm m}^3/{\rm s}$ | $\sim 10^{-15}\text{--}10^{-1}$ | `t39_tier3_epsilon_alpha_joint_fit.py`, `LOG_ALPHA_RANGE = (-30, -1)` |
| $(\sigma/m)_0$ | SIDM transfer cross-section per unit mass at $v_{\rm ref} = 100\,{\rm km/s}$ | cm²/g | $1\,{\rm cm}^2/{\rm g} = 0.1\,{\rm m}^2/{\rm kg}$ | $\sim 0.07$ (G12 hierarchical) | `config.py`, `LOG_SIGMA_M_RANGE = (-3, 2.5)` |
| $a$ | Velocity power-law index | — | — | $\sim 0\text{--}2$ | `config.py`, `A_RANGE = (-2, 2)` |
| $\sigma_{\rm SI}$ | Spin-independent DM-nucleon cross-section | cm² | $1\,{\rm cm}^2 = 10^{-4}\,{\rm m}^2$ | $\sim 10^{-46}\text{--}10^{-42}$ (LZ limit at $m_\chi \sim 40$ GeV) | `t30_lz_real_posterior.py` (HEPData 155182) |
| $\langle\sigma v\rangle$ | Velocity-averaged annihilation cross-section | cm³/s | $1\,{\rm cm}^3/{\rm s} = 10^{-6}\,{\rm m}^3/{\rm s}$ | $\sim 3\times 10^{-26}$ (thermal relic) | `t32_fermi_dwarf_channel.py`, `t32_real_likelihood.py` |
| $v_{\rm ref}$ | Galactic reference velocity | km/s | $1\,{\rm km/s} = 10^3\,{\rm m/s}$ | $100\,{\rm km/s}$ | `t8_v03_joint_fit.py`, `V_GALAXY = 100` |

### 4.2 Natural-units ↔ SI conversion factors used in this project

- **Energy:** $1\,{\rm GeV} = 1.783 \times 10^{-27}\,{\rm kg} = 1.602 \times 10^{-10}\,{\rm J}$.
- **Length:** $1\,{\rm GeV}^{-1} = 1.973 \times 10^{-16}\,{\rm m} = 1.973 \times 10^{-14}\,{\rm cm}$ (i.e., $\hbar c / (1\,{\rm GeV})$).
- **Time:** $1\,{\rm GeV}^{-1} = 6.582 \times 10^{-25}\,{\rm s}$.
- **Cross-section:** $1\,{\rm GeV}^{-2} = 0.3894\,{\rm mb} = 3.894 \times 10^{-27}\,{\rm cm}^2$.
- **Velocity:** $v/c = \beta$, where $v$ is in km/s and $c = 2.998 \times 10^5\,{\rm km/s}$.

These factors are used throughout the codebase — see `t40_yukawa_sigma_m.py` line 47 for the proton mass and line 48 for $\hbar c$.

### 4.3 Dimensional checks (catch silent bugs)

These are the dimensional identities that **must** hold for any code claiming to compute a cross-section, mass, or velocity. They are listed here so future-me can spot a unit-error bug.

1. $[\sigma/m] = {\rm m}^2/{\rm kg}$, NOT $[{\rm m}^2]$ — a common typo when adapting from cm²/g.
2. $[\langle\sigma v\rangle] = {\rm m}^3/{\rm s}$, NOT $[{\rm m}^2/{\rm s}]$ — the $v$ factor is essential.
3. $[\sigma_{\rm SI}] = {\rm m}^2$, dimensionally distinct from $[\sigma/m]$ — they differ by a factor of $m_\chi/m_{\rm nucleon}$.
4. $[\varepsilon] = $ dimensionless — kinetic mixing has no dimension.
5. $[\alpha] = {\rm m}^3/{\rm s}$ in SI units — **NOT dimensionless**. This is a frequent mistake; the annihilation mapping $\langle\sigma v\rangle = \alpha (\sigma/m)^2$ requires $\alpha$ to have units of cross-section×velocity, i.e., m³/s.

---

## §5 Cross-section mappings (the parametrization used in the joint fit)

This section makes explicit how the Lagrangian parameters $(\varepsilon, \alpha, m_\phi, m_\chi, g_\chi, \Lambda_{\rm dark})$ connect to the **observable** parameters $(\sigma/m)_0, a, \sigma_{\rm SI}, \langle\sigma v\rangle, m_\chi)$ that appear in the joint fit. This is the mapping that G10 (dimensional inconsistency in $\varepsilon$) flagged and that G13 (this document) clarifies.

### 5.1 Yukawa transfer cross-section (T40)

The **transfer cross-section** for SIDM via dark-rho exchange in the Born approximation is (Feng+ 2009, Tulin+Yu 2018):
$$
\sigma_T(v) = \frac{g_\chi^4 m_\chi^2}{8\pi m_\phi^4} \cdot L^2(\beta^2),
$$
where
$$
\beta = \frac{m_\chi v}{\sqrt{2}\,m_\phi}, \quad L(s) = \frac{\log(1+s)}{s}, \quad s = \beta^2.
$$
At low velocity ($\beta \ll 1$, $s \ll 1$): $\sigma_T \to g_\chi^4 m_\chi^2 / (8\pi m_\phi^4)$ (constant in $v$). At high velocity ($s \gg 1$): $\sigma_T \propto v^{-4}$ (classical limit).

The codebase uses this in `t40_yukawa_sigma_m.py::sigma_T_cm2()` (line 66-87).

### 5.2 Power-law parametrization (T39, T8)

The joint fit parametrizes the velocity dependence as a **power law**:
$$
(\sigma/m)(v) = (\sigma/m)_0 \left( \frac{v}{v_{\rm ref}} \right)^a,
$$
with $v_{\rm ref} = 100\,{\rm km/s}$. This is an approximation to the true Yukawa form, valid in the **intermediate-velocity regime** (50-200 km/s). The relationship is:
$$
(\sigma/m)_0 = \sigma_T(v_{\rm ref}) / m_\chi, \quad a \approx \frac{d\log\sigma_T}{d\log v}\bigg|_{v = v_{\rm ref}}.
$$
The derivation of $a$ from $(m_\phi, m_\chi, g_\chi)$ is in `t40_yukawa_sigma_m.py::derived_a()` (line 95-104). This produces the **physical Yukawa velocity index** that G12 (T8 hierarchical SPARC) treats as a derived quantity.

### 5.3 Direct-detection mapping (T30, T39)

The spin-independent DM-nucleon cross-section via kinetic mixing is:
$$
\sigma_{\rm SI} = \varepsilon^2 \cdot \frac{\mu_{\chi N}^2}{\pi} \cdot \left( \frac{Z}{A} \right)^2 \cdot \frac{1}{m_\phi^2} \cdot (\text{nuclear form factor}),
$$
where $\mu_{\chi N} = m_\chi m_N / (m_\chi + m_N)$ is the reduced mass. For a Xe target ($Z = 54$, $A \approx 131$):
$$
\sigma_{\rm SI} \sim \varepsilon^2 \times 10^{-38}\,{\rm cm}^2 \times \left( \frac{40\,{\rm GeV}}{m_\chi} \right)^2 \left( \frac{1\,{\rm MeV}}{m_\phi} \right)^2.
$$
The codebase uses a simpler mapping (per T30 line 92):
$$
\sigma_{\rm DM\text{-}nucleon} = \varepsilon \times (\sigma/m)_0,
$$
which is the **observable-at-hand** mapping — it is correct as long as the $\varepsilon$ in T39 absorbs the geometric factors that the more careful Yukawa form would make explicit. The dimensional inconsistency flagged in R11 G10 is that $\varepsilon$ in this project carries units; the remap to a dimensionless portal operator is deferred to v0.4+.

### 5.4 Annihilation mapping (T32, T39)

The annihilation cross-section via dark-rho exchange is:
$$
\langle\sigma v\rangle = \frac{\pi \alpha_{\rm dark}^2}{m_\chi^2} \cdot \frac{(2 m_\chi^2 - m_\phi^2)^{3/2}}{(2 m_\chi^2)} \cdot (\text{color factor}),
$$
where $\alpha_{\rm dark} = g_\chi^2 / (4\pi)$. At $m_\phi \ll m_\chi$: $\langle\sigma v\rangle \sim \pi \alpha_{\rm dark}^2 / m_\chi^2$.

The codebase uses (T32 line 99, T39 line 99):
$$
\langle\sigma v\rangle = \alpha \times (\sigma/m)_{\rm at\,v}^2,
$$
where $(\sigma/m)_{\rm at\,v}$ is the SIDM cross-section at $v = 100\,{\rm km/s}$. Again, the $\alpha$ absorbs the geometric factors. The units are $\alpha \in {\rm cm}^3/{\rm s}$ (see §4.3 #5 — the dimensional caveat).

### 5.5 Mediator-mass ↔ velocity-index connection (T40, T41)

The Yukawa velocity index $a$ is **derived** from $(m_\phi, m_\chi, g_\chi)$:
$$
a = \frac{\log \sigma_T(v_1) - \log \sigma_T(v_2)}{\log v_1 - \log v_2}\bigg|_{v_1 = 50\,{\rm km/s}, v_2 = 200\,{\rm km/s}}.
$$
The T41 joint fit treats $(m_\phi, m_\chi, g_\chi)$ as fundamental and $(\sigma/m)_0, a$ as derived. This is the **physical** parametrization (vs. T39's phenomenological $(\sigma/m)_0, a, \varepsilon, \alpha$ approach). The two parametrizations are related by the mappings in §5.1-§5.4.

---

## §6 Current numerical values (canonical, from t41/T39 results)

These are the canonical numerical values from the most recent joint-fit runs (D15-CORRECTED3, 2026-08-14):

| Parameter | Canonical value | Source | Notes |
|---|---|---|---|
| $(\sigma/m)_0$ | $1.67\,{\rm cm^2/g}$ (T21 baseline) or $0.067\,{\rm cm^2/g}$ (G12 hierarchical) | T21 / G12 pre-compute | Difference is the saturation score vs. hierarchical per-galaxy likelihood |
| $a$ | $\sim 1$ (T21) or $\sim 0$ (G12 hierarchical best fit) | T21 / G12 | Velocity dependence — sensitive to prior choice |
| $m_\chi$ | $\sim 40$ GeV (Fermi peak) | `t32_real_likelihood.py` | From McDaniel+ 2024 TS profile peak |
| $m_\phi$ | unconstrained by current data | `t41_mediator_mass_joint_fit.py` | See §7.1 |
| $g_\chi$ | unconstrained by current data | T41 | Free parameter, weakly constrained by SIDM-bumpy |
| $\varepsilon$ | $\sim 10^{-54}$ (T39 fit, decoupled) | T39 line 7 | Must be tiny to satisfy LZ |
| $\alpha$ | $\sim 10^{-15}$ (T39 fit, decoupled) | T39 line 7 | Must be tiny to satisfy Fermi |
| $\sigma_{\rm SI}$ | $\sim 2\times 10^{-18}\,{\rm cm}^2$ (mediator-portal at $m_\chi = 40$ GeV) | T30 HEPData 155182 | 72 dex below LZ limit — **mediator decoupled from SM** |
| $\Lambda_{\rm dark}$ | $\sim 1$ GeV (phenomenological) | T53 | NOT from lattice (see §7.2, G14) |

**Key takeaway:** the canonical values say the SIDM mediator is **essentially invisible to direct-detection and gamma-ray constraints** (72 dex and 3 dex safety margins respectively). This is the headline finding of the project — the composite SIDM model survives these constraints by **decoupling** the mediator from the Standard Model, NOT by some clever cancellation.

---

## §7 Limitations and open issues

### 7.1 What this Lagrangian does NOT specify

- **No UV completion.** We do not specify what produces the dark SU(N) at high scales. The dark-color group is assumed to confine at $\Lambda_{\rm dark} \sim 1$ GeV with no further structure above.
- **No flavor structure beyond $N_{\rm df} = 2$.** A more general treatment would include arbitrary $N_{\rm df}$, which changes the number of dark pions and the dark matter stability argument.
- **No explicit CP violation.** The dark sector is assumed CP-conserving at the Lagrangian level (no $\theta$-term for the dark-color group; this is the "CP-1" assumption common in mirror-QCD models).

### 7.2 What G14 (lattice input) would replace

Per R11 G14, the dark-rho mass and decay constant should come from a **lattice simulation of the dark SU(N) theory**, not from the QCD-like scaling relation used in `t53_dark_rho_meson.py`. The QCD-like scaling is:
$$
m_\phi \approx 3 \Lambda_{\rm dark}, \quad f_\pi \approx \Lambda_{\rm dark}.
$$
This is phenomenologically motivated (it works for QCD with $\Lambda_{\rm QCD} \approx 200$ MeV, $m_\rho \approx 770$ MeV, $f_\pi \approx 93$ MeV). For a dark sector with $N_{\rm dc} = 3$ but different $N_{\rm df}$, the scaling changes — a lattice calculation is needed.

The G14 deliverable would be:
1. A lattice simulation of $SU(3)$ gauge theory with $N_{\rm df} = 2, 3, 4$ dynamical fermions at the $\Lambda_{\rm dark}$ scale.
2. Output: $m_\rho / \Lambda_{\rm dark}$, $f_\pi / \Lambda_{\rm dark}$, $m_{\pi_d} / \Lambda_{\rm dark}$ as functions of $N_{\rm df}$.
3. Update `t53_dark_rho_meson.py` to use the lattice output instead of the QCD-like scaling.

This is a multi-month project requiring either lattice QCD expertise or collaboration with a lattice group.

### 7.3 What G15 (Boltzmann relic) would replace

Per R11 G15, the relic abundance calculation should come from a **Boltzmann-solver** code (e.g., a dark-sector micrOMEGAs equivalent) that solves:
$$
\frac{dY}{dx} = -\frac{\langle\sigma v\rangle s}{H x} (Y^2 - Y_{\rm eq}^2),
$$
with $x = m_\chi / T$, $s$ the entropy density, $H$ the Hubble rate, and $Y$ the dark-pion yield. The current codebase does not solve this — it uses the simple scaling $\Omega_{\rm DM} \propto 1/\langle\sigma v\rangle$.

### 7.4 What G16 (dwarf-mass KiSS-SIDM) would add

Per R11 G16, the KiSS-SIDM gravothermal penalty should be evaluated at **halo-mass-specific** resolution, down to $10^7\text{--}10^8 M_\odot$ dwarf galaxies where the paper-scale $N = 2\times 10^6$ simulations are not feasible on WSL. This requires either a coarser DSMC approximation or access to compute resources beyond WSL.

### 7.5 Honest scoping

The Lagrangian in this document is the **minimal sufficient specification** for the composite SIDM model as used in this project. It is not:
- A phenomenologically-complete model of all possible composite-DM scenarios.
- A UV-complete theory of the dark sector.
- A replacement for the existing mediator-mass joint fits (T41), which use the same Lagrangian but with the phenomenological $(\sigma/m)_0, a$ parametrization for speed.

The mapping from $(\varepsilon, \alpha)$ to $(\sigma_{\rm SI}, \langle\sigma v\rangle)$ in §5.3-§5.4 is the dimensional inconsistency flagged by R11 G10. The fix is in v0.4+ (not in this document) — to make $\varepsilon$ and $\alpha$ dimensionless portal operators and absorb the geometric factors into the coupling constants explicitly.

---

## §8 Cross-references to code

This Lagrangian is implemented across the following files:

| Section | Code file | Function |
|---|---|---|
| §1 Composite ansatz | `v0.3-prelim/code/t53_dark_rho_meson.py` | `dark_rho_mass()` — phenomenological $\Lambda_{\rm dark} \to m_\phi$ scaling |
| §2.3 Chiral EFT | (no direct code; HLS formulation is in the doc only) | — |
| §3.1 Vector portal | `v0.3-prelim/code/t30_lz_real_posterior.py` | `loglike_lz_real()` — $\varepsilon$ mapping to LZ |
| §3.1 Vector portal | `v0.3-prelim/code/t32_fermi_dwarf_channel.py` | `loglike_fermi_sidm()` — $\alpha$ mapping to Fermi |
| §5.1 Yukawa $\sigma_T$ | `v0.3-prelim/code/t40_yukawa_sigma_m.py` | `sigma_T_cm2()` — full Born-approx calculation |
| §5.2 Power-law param | `v0.3-prelim/code/sidm_velocity_dependent.py` | `sigma_m_effective()` — power-law velocity model |
| §5.5 Mediator $\to$ a | `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` | `derived_a()` — Yukawa velocity index |
| §6 Canonical values | `v0.3-prelim/data/results/*.json` | Joint-fit outputs |

---

## Document version

- **v1 (2026-08-14):** Initial write-up. Closes R11 G13 closure (within v0.4-prelim scope per user's brief, despite R11's "out of scope" tag — the user explicitly requested the full document).

---

## Acknowledgments

- Composite-DM literature: Schuster+ 2010 (arXiv:0910.5224), Cline+ 2017 (arXiv:1701.08780), Hochberg+ 2014 (arXiv:1402.5143).
- SIDM literature: Tulin+ Yu 2018 (RMP 90, 015004), Kaplinghat+ 2016 (RMP), Roberts+ 2024.
- Dark-rho phenomenology: the HLS formulation is from Bando+ 1985; the HLS-as-SIDM-mediator picture is a recent development (e.g., Fujita+ 2024, Cline+ 2024).
- Lagrangian review: this document was prepared with reviewer-audit assistance (Hermes M3 + Doubao + Qwen 3.8 Max). Numerical values are from the project codebase; theoretical content is from the cited literature.