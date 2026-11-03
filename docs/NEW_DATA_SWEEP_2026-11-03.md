# NEW_DATA_SWEEP — 2026-11-03 (v19.2-E chain, stage 2: new-data search)

**User directive chain (2026-11-03):** housekeeping save -> search new data (Euclid, Roman, DESI, etc.) -> use real galaxy merger data (Path 3) -> consolidate and report. This document is stage 2's adjudicated record. Stage 1 save point: tag `v19.2-F-RecordSave-v1.17` -> `ef427e6`.

## 1. Method and verification discipline

Three parallel literature sweeps were run: (A) Euclid + Roman window 2025-06 -> 2026-11 (44 arXiv queries); (B) DESI + adjacent surveys (38 queries); (C) citation watch on the project's v=150 anchor papers via Semantic Scholar + OpenAlex. Sweep outputs are self-reports; **every cited arXiv ID was re-verified against the live arXiv `id_list` API before intake** (32/32 resolved). Semantic Scholar was hard rate-limited (429) for children A/B; OpenAlex substituted where needed (child C), disclosed here.

## 2. Headline adjudications

1. **NO revision of the v=150 anchors exists in window.** Sameie+ 2020 (arXiv:1904.07872, PRL 124, 141102; KB-verified) has 22 in-window citers, all methods/simulation work, none revising its numbers. Lei+ 2026 (arXiv:2609.16740) and Wang+ 2026 (arXiv:2609.19132) have exactly one in-window citer each (arXiv:2609.29114, Yang & Fan), which *explains* the Lei/Wang inner-DM deficit via inelastic DM rather than revising it. **The R88(87) status of the v=150 entry (tuning statement, demoted no-go) is unchanged by current literature.** The dissolution criterion (shift ~2x in sigma_eff at v=150) has NOT fired.
2. **Cloud-9 semantics confirmed: the project's Cloud-9 is the M94 RELHIC** (Zhou+ 2023 [15a]; BLN24 [15b]; Anand+ 2025 2508.20157 [15c]). The sweep dispatch context had conflated it with the GD-1 stellar-stream spur (a different object in 2025-26 literature). GD-1 results below are intake for the *substructure channel*, not for the Cloud-9 anchor. New directly-on-anchor paper: 2608.04362 (Ohana+ 2026, CDM vs SIDM interpretations of Cloud-9) — already in KB verified.
3. **Roman Space Telescope: no measured dark-matter data in window** (launch ~late 2026). All Roman hits are forecasts/proposals; nothing worth integrating yet.
4. **Euclid now contributes measured data touching project channels** (first time): Q1 extragalactic-stream halo geometry (2606.21774), DR1 Fornax-7 ultra-faint companion (2609.14535), ERO globular-cluster FDM bound method (2609.11328).

## 3. Tiered intake table (all IDs arXiv-API verified)

### Tier 1 — could move project numbers (full read required before any citation or reuse)

| arXiv | Title / first author | Status | Why it matters here |
|---|---|---|---|
| 2610.28890 | Not so Fast: Revised Calibration of SIDM Core Collapse (bosch) | MNRAS accepted | Recalibrates gravothermal fluid equations vs DSMC N-body; claims collapse is MUCH slower once optically thick. Direct pressure on the Yang+ 2024 [43] parametric t_c prefactor used for the dSph collapse prediction (paper already records BM2 vs Cosmo-501 10.7x calibration spread). READ before quoting any t_core. |
| 2610.31881 | Semi-Analytic Predictions for Strong-Lensing Perturbers in CDM and SIDM (tekverk) | preprint | Reproduces the three perturbers with sigma0/m = 147.1 cm^2/g — numerically identical to the [43]-derived canonical sigma0/m of 147.1 (w differs: 120 vs 24.33 km/s). Must read to determine same-calibration vs independent tension with canonical sigma_peak=174 @ 29.4. |
| 2610.40766 | Hints of self-interacting dark matter from strong gravitational lensing (gilman) | PRL submitted | Measured 29 quadruply-imaged quasars; converts to sigma/m ~ 10^2-10^4 cm^2/g at ~10 km/s with MeV mediator. Closest published neighbour to our 174 cm^2/g resonance (different velocity, plausibility support only). |
| 2609.35974 | JWST lensed quasar DM survey V (gilman) | PRD submitted | 29 quads; Bayes factor 8:1-24:1 for core-collapsed SIDM over CDM. Population-level support for the core-collapse regime our framework occupies. |

### Tier 2 — new channel data (intake; no posterior shift without dedicated re-runs)

| arXiv | Title / first author | Venue | Channel touched |
|---|---|---|---|
| 2609.22581 | Hunting Thermal Relics in DESI DR1 Ly-alpha Forest (silva) | preprint | Ly-alpha/warmness: m_s^eff < 0.061 eV, N_eff < 3.41 (95%), measured. Mediator ~0.5 GeV not threatened; register as channel data. |
| 2601.21432 | DESI DR1 Ly-alpha 1D PSD (chavesmontero) | JCAP accepted | Measurement layer under the bound above. |
| 2610.26877 | Revisiting SIDM with DESI DR2 BAO (zhu) | A&A | Concludes velocity-dependent sigma/m needed; BAO-scale only, no small-scale number. |
| 2510.02247 | Measurement of Substructure from GD-1 kinematics (nibauer) | ApJ 1004, 62 | Substructure channel: 4-sigma excess, f_sub = 0.05 (+0.08/-0.03), prefers compact-than-CDM subhalos. Measured. |
| 2604.20958 | GD-1 with DESI DR2: thin stream + hot cocoon (jarvis) | submitted | 608 members; sigma_V 2.49/6.13 km/s decomposition. Measured. |
| 2510.17956 | Strong-lensing detectability of steep-inner-profile subhalos (kollmann) | MNRAS | Sensitivity of core-collapsed (beta=2.2) detection ~1 dex below NFW. Forecast with quantitative numbers. |
| 2604.05237 | Minimum CDM halo mass via strong lensing (nierenberg) | PRL | m_low < 10^8.3 M_sun at 10:1 odds, 28 lenses. Measured SHMF floor. |
| 2512.01361 | Joint FDM+WDM from MW & M31 satellites (liu) | ApJ accepted | m_WDM > 6.20 keV (95%). Measured. |
| 2606.10006 | Mixed DM limits from MW satellites (crumrine) | preprint | Measured + LSST forecast. |
| 2602.20889 | Salpeter IMF + NFW via double-source-plane lens (li) | MNRAS | Inner-density channel counterpoint to Lei/Wang deficit (this lens prefers NFW). Measured. |
| 2606.21774 | Euclid Q1: geometry of DM halos from extragalactic streams (Euclid Collab) | A&A submitted | First Euclid measured stream-based halo-shape data. |
| 2609.14535 | Euclid DR1: Fornax-7 ultra-faint companion (saifollahi) | A&A submitted | New satellite near Fornax; faint-end population relevant to dSph channels. |
| 2609.11328 | Euclid ERO FDM mass bound via GCs in dwarfs (besnard) | A&A submitted | FDM not SIDM; method analogue only. |

### Tier 3 — methodological caveats to cite when relevant

| arXiv | Title | Caveat |
|---|---|---|
| 2610.41842 | Multiple origins of spurs in stellar streams (guillaume) | Bar/merger structure also produces stream spurs; spur morphology alone is not a DM measurement. |
| 2605.16200 | No Stream Left Unscathed: host-galaxy imprint (arora) | ~3/4 of ~15,000 simulated streams develop spurs/kinks/cocoons from the host potential alone. Strengthens the same caveat. |
| 2610.28745 | Gravothermal evolution across Knudsen numbers (gurian) | Collapse times depend strongly on Knudsen number at sigma/m 50-250,000 cm^2/g with sigma ~ v^-4. |
| 2609.29114 | Mass-dependent DM deficit from inelastic scattering (yang) | Theoretical companion to Lei/Wang measurements (support, not revision). |

### Tier 4 — anchors and already-cited references re-confirmed

Sameie+ 2020 1904.07872 (KB verified); Horigome+ 2025 2503.13650 = paper [27] (KB verified); Ohana+ 2026 2608.04362 (KB verified); SIDM Concerto 2503.10748 (KB verified); Fischer & Yu 2026 2603.04508 = [19] (KB verified); Yang+ 2024 parametric 2305.16176 = [43] (KB). No new intake needed for these.

## 4. Sweep defects caught during adjudication

1. **ID collision:** one sweeper cited the core-collapse recalibration as 2609.28890 — that ID is a solar chromospheric-flows paper. Correct target **2610.28890**. Caught by arXiv-API verification.
2. **Anchor description drift:** the citation-watch brief described Sameie+ 2020 as a "mass function from flux-ratio anomalies" paper; no such paper exists. Sameie+ 2020 is 1904.07872 (MW-tide core collapse of SIDM subhalos, PRL 124, 141102) — matches the project registry. The v=150 tuning entry in the paper already documents this anchor under R88(87)/ClawsGO #7 (Sameie and Lei/Wang counted as the same constraint under different names). No action beyond this confirmation.
3. **Cloud-9 conflation** (see headline 2) — resolved in the project's favour; sweep context fixed for stage 3.

## 5. KB operations this round

Project policy note (verified live): `.gitignore` keeps KB PDFs **local-only** (on-disk, regenerable via `docs/papers/fetch_all_cited_papers.sh` / arXiv; only 4 historical PDFs are git-tracked, and gitignore only affects untracked files). Registry rule 8 requires a LOCAL PDF + summary — satisfied on disk.

- **21 new intake PDFs placed in `docs/papers/to_verify/` (local, not committed — gitignore policy)**: 2510.02247_nibauer_2025, 2510.17956_kollmann_2025, 2512.01361_liu_2025, 2601.21432_chavesmontero_2026, 2602.20889_li_2026, 2604.05237_nierenberg_2026, 2604.20958_jarvis_2026, 2605.16200_arora_2026, 2606.10006_crumrine_2026, 2606.21774_collaboration_2026, 2609.11328_besnard_2026, 2609.14535_saifollahi_2026, 2609.22581_silva_2026, 2609.29114_yang_2026, 2609.35974_gilman_2026, 2610.26877_zhu_2026, 2610.28745_gurian_2026, 2610.28890_bosch_2026, 2610.31881_tekverk_2026, 2610.40766_gilman_2026, 2610.41842_guillaume_2026.
- **Retracted mid-round claim:** an earlier draft of this section claimed a "rule-8 gap" for Lei/Wang/Three-Birds PDFs being "uncommitted". FALSE — their verified PDFs are on disk (verified/2510.11006_yu_2026.pdf 0.4MB, verified/2609.16740_lei_2026.pdf 4.7MB, verified/2609.19132_wang_2026.pdf 3.6MB, on disk since 2026-10-27), which is what rule 8 requires. Untracked status is the intended policy, not drift. The re-fetched duplicate copies in to_verify/ were deleted.
- **Duplicate removals:** 2508.20157 (Anand), 2503.13650 (Horigome), 2608.04362 (Ohana) already committed in verified/ — fetched copies deleted.
- **Oversized PDFs** (any future commit would breach the 5 MB pre-commit cap; integrity anchors, sha256 prefixes): 2610.28890_bosch 20de6fa86eab9d04, 2610.31881_tekverk e0b69db66638a2b8, 2604.20958_jarvis e3f965077f24e9ae, 2606.21774_collaboration ebea9aa46fb51518, 2609.14535_saifollahi 88205ef759a4421a, 2609.35974_gilman a5449836bac0806f.
- All intake sits in **to_verify**: nothing is "verified" until actually read end-to-end (registry rule). `.md` summaries for the new items are deferred to the registry-integration round (make_kb_summaries.py requires a verified reference entry first).

## 6. What this sweep does NOT change

- No no-go dissolved; no posterior shift; no canonical number moved. The v=150 entry stays a tuning statement per R88(87).
- Tier-2 items are channel data, not re-fits: incorporating DESI Ly-alpha numbers into the Ly-alpha channel is a future dedicated re-run, not an automatic posterior move.
- Roman contributes nothing measured (launch pending).

## 7. Tier-1 read verdicts (2026-11-03, reads completed)

All four Tier-1 papers read end-to-end; KB summaries live in `docs/papers/verified/` (status VERIFIED 2026-11-03). Verdicts:

1. **2610.28890 (van den Bosch & Tokayer, MNRAS accepted) — ADOPT as calibration caveat.** New GTF conductivity calibration (alpha, beta) = (0.5, 0.9) for NFW; LMFP collapse somewhat shorter, but collapse slows dramatically once the core is optically thick; self-similar LMFP t_c formulae (the [43] eq. 2.2 family — they recompute our exact constants alpha = 1.0, C = 0.75) underestimate late-time collapse. No existing claim killed: the project has no BH-seed claim (grep confirmed empty). OPEN ITEM: high-σ Cloud-9-type states (174 cm^2/g at ~29 km/s) become optically thick earlier — RELHIC formation timing needs a dedicated recheck before any high-σ t_core quote.
2. **2610.31881 (Tekverk+, JCAP submitted) — CORROBORATES Model III, CONTESTS Model I at cluster scales only.** Simultaneous reproduction of all three perturbers requires w >~ 10^2 km/s and sigma0/m >~ 10^2; at w = 24.33 the J0946 massive perturber cannot form. The project already carries both variants (`sashimi_parametric.py`: Model I dwarf-favored / Model III cluster-favored); Tekverk independently adopts (147.1, 120) from Nadler+ 2023 L39. Canonical Model I usage (Cloud-9/dwarf scales) not hit. Future perturber-channel claims must state their (sigma0, w) pairing.
3. **2610.40766 (Gilman+, PRL letter) — CORROBORATION; no numeric collision with 174@29.4.** σ = 10^2-10^4 cm^2/g at 10 km/s via MeV mediator, smooth Yukawa velocity dependence (no resonance peak); CDM disfavored 8:1-24:1, not formally excluded; collapse floor t_c,min ≈ 10^2(rs/vs) — echoes verdict 1's "not arbitrarily fast".
4. **2609.35974 (Gilman+, PRD, survey V) — ADOPT as population-level regime support.** Core-collapsed (sub)halos favored 8:1-24:1; escaping them requires excess GC abundance AND more subhalos than N-body predicts. Same lens sample as 40766 — do not double-count.

Tier-2 items remain background (no posterior shifts) until dedicated re-runs; registry coupling happens at citation time. Stage 3 (Path 3 merger histories) awaits TNG account approval; baseline docs: `docs/FUTURE_WORK_PLAN_V19_2_E.md` section 2.

## 8. Tier-2 read verdicts (CLOSED 2026-11-03 — all 17 read end-to-end)

Three delegated readers extracted all 17 papers; each was then adjudicated against the local PDF text (headline numbers grep-verified; three delegated misclassifications corrected: **Silva 2609.22581** is a DESI-Lyα sterile-neutrino paper, not a stream paper; **Crumrine 2606.10006** is mixed-DM satellite limits, not a white-dwarf paper; **Besnard 2609.11328** is FDM globular-cluster limits from Euclid ERO, not Sgr A*). KB entries in `docs/papers/verified/`.

| Group | Papers | Net effect |
|---|---|---|
| GD-1 streams | Nibauer 2510.02247, Jarvis 2604.20958, Liu 2512.01361, Chaves-Montero 2601.21432, Arora 2605.16200, Guillaume 2610.41842 | Streams channel DOWNgraded as single-encounter evidence: 75% of 15,000 Gaia velocity jumps are morphologically complex (Arora); merger/bar/subhalo spur rates 50/25/28% (Guillaume); GD-1 subhalo inference CDM-consistent, f_sub=0.05 (+0.121/−0.083), WDM M_hm<10^8.6 (Nibauer). Population-level steep-subhalo viability survives. |
| Lensing substructure | Kollmann 2510.17956, Nierenberg 2604.05237, Li 2602.20889 | Corroborates compact/steep SUBhalos (α≈2.1-2.2; 10^8.2-10^8.6 M_sun detections) while Li finds J0946+1006 MAIN halo NFW (α=1.04±0.10 — Sonnenfeld's 1.7 was arc-driven). Cite subhalo steepness, not main-halo steepness. |
| Gravothermal calibration | Gurian 2610.28745 | Two-source standing caveat with 2610.28890: Knudsen Kn=1 LMFP/SMFP boundary; Yang 150C family valid only LMFP C≳0.5 (Halo 1: Kn=6.65 at σ=250); SMFP t_c ∝ σ² — qualitative flip the [43] family misses; merger delay ≤18 t_r feeds stage 3. |
| Cosmology | Zhu 2610.26877, Silva 2609.22581, Crumrine 2606.10006 | Zhu (DESI DR2 BAO): first BAO-line interacting-DM preference (lnB 5.57/8.72), σ/m<0.01 at v~1000 km/s — WATCH: Model III predicts σ(1000)≈0.03 (mildly pressured), Model I ≈5×10⁻⁵ (safe). Silva background (Neff<3.41, m_s^eff<0.061 eV). Crumrine: mixed-DM (γ/ν/p-DM) limits support our mediator baryon-coupling ceiling. |
| Euclid | Q1 2606.21774, DR1 2609.14535, ERO 2609.11328 | New measured channels, no σ yet: q_proj=0.95±0.05 halo shapes from 13 stream hosts; Fornax-7 candidate satellite (170 M_sun, 10.4 Gyr, 2.8 kpc); FDM m22<1.46/1.09 from GC timing. Fornax cluster = emerging multi-probe lab. |
| Alternative SIDM theory | Yang & Fan 2609.29114 | Competing cluster-velocity explanation for inner-fraction deficits (exothermic inelastic DM, Δ=18.1 keV, σ(300)/m≈0.95). Different velocity regime from our 29.4 km/s anchor; watch item only. |

**Net posture:** no Tier-2 paper touches the canonical 174 cm²/g @ 29.4 km/s. Two GD-1 papers (Arora, Guillaume) materially weaken single-feature subhalo arguments. Zhu adds cluster-scale pressure on the demoted Model III tail. The gravothermal calibration caveat is now two-source (2610.28890 + 2610.28745). **Sweep intake closed: 21/21 adjudicated.**
