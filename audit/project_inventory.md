# Project Inventory: Bypass-Controlled Single-Phase Immersion Cooling

**Repository Path:** `/mnt/e/ijhmt-cfp/Paper-5` & `/mnt/e/ijhmt-cfp/scratch_git/repo`  
**Git Tag / Checkpoint:** `pre_full_sweep_validation_audit`  
**Active Working Branch:** `audit-and-verification`  
**Date:** 2026-09-01  

---

## 1. Manuscript Source Files

| File Path | Description | Current Status |
| :--- | :--- | :--- |
| `manuscript/main.tex` | Master LaTeX document (title, abstract, document structure) | Clean compile (49 pages, 0 errors) |
| `manuscript/references.bib` | Canonical BibTeX database | Complete with all author citations + Roache GCI |
| `manuscript/sections/introduction.tex` | Introduction, industry motivation, research gap | Drafted |
| `manuscript/sections/problem_formulation.tex` | 1U chassis geometry, dual-CPU layout, open ratio $\\mathrm{OR}$, fluid properties | Drafted |
| `manuscript/sections/numerical_method.tex` | Governing equations, CHT coupling, buoyancy, flow regime, solver schemes | Updated with verified metrics |
| `manuscript/sections/verification_validation.tex` | Reproducibility ladder, anchor case limits, GCI Table 2, validation benchmarks | Updated with defensible wording |
| `manuscript/figures/` | Rendered figure files (`fig1_domain.png` to `fig12_*.png`, `fig5_validation_ladder.png`) | Vector & high-res PNGs |

---

## 2. OpenFOAM CFD Case Directories

| Directory Path | Benchmark / Rung | Description & Status |
| :--- | :--- | :--- |
| `cfd/kewalramani_v0b/` | V0b (Kewalramani 2019) | $16.05\\text{M}$ cell multi-region CHT ($82\\text{ W}$, deionized water). Solved, mass balance err $3.13 \\times 10^{-7}\%$. |
| `cfd/sastre_v1/` | V1 (Sastre 2018) | 8 cases ($C0$ shrouded vs $C1$ clearance across $Q_1\\text{--}Q_4$). Solved. Special forensic check executed. |
| `cfd/dong_v3b/` | V3b (Dong 2026 / Huang 2024) | 1U server chassis ($1.75\\text{ kW}$ dual CPU in EFL-1 across 6 flow rates). Solved, MAPE $1.20\%$. |
| `cfd/chun_v3/` | V3 Anchor (Chun 2026) | 1U plate-fin server ($700\\text{ W}$/chip in FC-40 across $Q=6\\text{--}14\\text{ LPM}$ and $\\mathrm{OR}=0\\text{--}100\%$). Solved. |
| `parametric_campaign/template_case/` | Parametric Base Case | Templated OpenFOAM case with dynamic boundary conditions, probes, surfaceFieldValue pressureDrop. |

---

## 3. Automation, Meshing & Analysis Scripts

| Script Path | Purpose | Audit / Readiness |
| :--- | :--- | :--- |
| `parametric_campaign/scripts/mesh_generator.py` | Generates blockMeshDict with dynamic physical fin height scaling $H_{\\mathrm{fin}}(\\mathrm{OR})$. | Verified (supports fast, medium, high mesh tiers). |
| `parametric_campaign/scripts/postprocess_case.py` | Computes mass flow split, bypass fraction $\\Phi$, $R_{\\mathrm{th}}$, $\\Delta p$, pumping power, and energy balance. | Verified. |
| `parametric_campaign/scripts/render_contours.py` | Generates 300 DPI temperature isotherms and velocity streamlines. | Verified. |
| `parametric_campaign/run_parametric_campaign.py` | Orchestrates parallel multi-core CFD execution with resume check. | Ready. |
| `scratch/evaluate_gate_c_d_full.py` | Reconciles Gate C mass conservation and Gate D hydraulic/thermal errors. | Verified. |
| `scratch/gen_fig5.py` | Renders the 6-panel validation ladder figure. | Requires Sastre label update. |

---

## 4. Digitised Literature Datasets

| Dataset Location | Source Paper | Extracted Physical Quantities |
| :--- | :--- | :--- |
| `validation/digitised/min-jang-kim-tip-clearance_fig3.csv` | Min et al. (2004) | Thermal resistance vs tip clearance gap |
| `scratch/ref_crop_chun_fig8_9.png` | Chun et al. (2026) | Bypass mass fraction & thermal resistance vs OR |
| `scratch/ref_crop_muneeshwaran_fig6.png` | Muneeshwaran et al. (2023) | Thermal resistance vs power ($200\\text{--}600\\text{ W}$) |
| `scratch/ref_crop_jeng_fig5.png` | Jeng (2008) | Nusselt number vs transverse bypass ratio ($W/L$) |
| `scratch/ref_crop_sastre_fig4.png` | Sastre et al. (2018) | Core pressure drop across $C0$ and $C1$ |

---

## 5. Audit Trail & Register Files

| File Path | Description |
| :--- | :--- |
| `audit/project_inventory.md` | Complete inventory of all repository assets. |
| `audit/master_issue_register.csv` | Full tracking register of all scientific/numerical issues and blockers. |
| `audit/validation_raw_reconciliation.csv` | Machine-readable table of raw CFD vs comparator data for all 6 rungs. |
| `audit/codex_findings.md` | Independent adversarial audit report by ChatGPT Codex. |
| `audit/agy_responses.md` | AGY orchestrator responses and evidence resolutions to Codex findings. |
| `audit/pre_sweep_gate.md` | Formal Pre-Sweep GO/NO-GO gate determination document. |
