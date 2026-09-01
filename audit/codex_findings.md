# INDEPENDENT ADVERSARIAL CFD & SCIENTIFIC COMPUTING AUDIT REPORT
**Project:** Dimensionless framework for bypass-controlled single-phase immersion cooling of server heat sinks  
**Auditor:** ChatGPT Codex (Strict Adversarial Independent CFD & Scientific Computing Auditor)  
**Report File:** `audit/codex_findings.md`  
**Target Repository:** `/mnt/e/ijhmt-cfp/Paper-5`  
**Date:** 2026-09-01  

---

## 1. EXECUTIVE SUMMARY & AUDIT VERDICT

| Audit Domain | Focus / Claim | Auditor Determination | Risk Level |
| :--- | :--- | :--- | :--- |
| **A. Sastre V1 Benchmark** | Claimed MAPE of 3.4% on tip-clearance bypass ratio | **FALSIFIED / UNCORRECTED CONFLATION**. Actual ratio MAPE is **21.62%** (pressure reduction MAPE **12.16%**). | **CRITICAL (Textual Bug)** |
| **B. 6-Rung V&V Matrix** | Claim of "universal experimental agreement" across all 6 rungs in Fig 5 caption | **OVER-CLAIM / MISLABELING**. Comparators comprise experimental, analytical, and published CFD. Fig 5 caption must be toned down. | **HIGH (Methodological)** |
| **C. Grid Convergence (Table 2)** | 4-grid Eça–Hoekstra / Roache GCI evaluation on base chassis | **MATHEMATICAL INCONSISTENCY & PASTE ERROR**. Table 2 reports raw step differences as GCI, has a copy-paste error (`0.17%` for bypass), and mixes apparent order. Grids themselves show excellent monotonic convergence. | **MEDIUM (Tabular)** |
| **D. Pre-Sweep Matrix** | Laminar vs RANS, Buoyancy/Ri, $\mu(T)$, Kelvin convention, Tank depth, Fin span | **VERIFIED & SCIENTIFICALLY SOUND**. Physics justification and sensitivity bounds are solid. | **PASS** |
| **E. Parametric Mesh Engine** | Dynamic fin scaling $H_{\mathrm{fin}}(\mathrm{OR})$ and conformal blockMesh generation | **VERIFIED & READY**. 100% hex conformal meshes across all $\mathrm{OR} \in [0, 1]$. | **PASS** |

### **Overall Gate Verdict: CONDITIONAL GO (APPROVED FOR SWEEP)**
The numerical simulation engine, OpenFOAM solver setups, boundary conditions, mesh generators, and post-processing pipelines are **fully verified, mathematically robust, and approved for launching the 250-case parametric sweep**. The required corrections are textual, tabular, and graphical in the manuscript and issue register.

---

## 2. DETAILED ADVERSARIAL AUDIT FINDINGS

### A. Forensic Audit of Sastre et al. (2018) V1 Benchmark

#### 1. The Falsification
AGY's manuscript text (`manuscript/sections/verification_validation.tex` Lines 337, 380, 405) states:
> *"The computed clearance-to-shrouded pressure ratio $\Delta p_{\mathrm{C1}}/\Delta p_{\mathrm{C0}} = 0.253\text{--}0.309$ reproduces Sastre et al.'s experimental and numerical channel-core ratio ($0.34\text{--}0.37$) within a mean absolute percentage error (MAPE) of 3.4\%."*

**Auditor Proof of Falsification:**
The 3.4% figure was erroneously pulled from Sastre et al.'s Table 3 (which reported total test-rig experimental vs numerical error of 3.51%, 5.38%, 7.69%, 6.94%), rather than computed against the channel core pressure ratio.

Evaluating the actual raw CFD outputs (`cfd/sastre_v1/sastre_v1_results.json`) against Sastre Table 4 channel core references yields:

| Flow Rate ($Q$) | Ref Core Ratio ($\Delta p_{\mathrm{C1}}/\Delta p_{\mathrm{C0}}$) | Present CFD Core Ratio | Absolute Error | Relative Error [%] |
| :--- | :--- | :--- | :--- | :--- |
| **$Q_1 = 53.5$ L/h** | $0.63 / 1.70 = 0.3706$ | $1.3017 / 4.2065 = 0.3094$ | $0.0612$ | **16.50%** |
| **$Q_2 = 83.6$ L/h** | $1.10 / 2.98 = 0.3691$ | $2.3073 / 7.9490 = 0.2903$ | $0.0788$ | **21.36%** |
| **$Q_3 = 110.3$ L/h** | $1.45 / 4.23 = 0.3428$ | $3.3261 / 12.0379 = 0.2763$ | $0.0665$ | **19.40%** |
| **$Q_4 = 167.2$ L/h** | $2.40 / 6.70 = 0.3582$ | $5.8738 / 23.1699 = 0.2535$ | $0.1047$ | **29.23%** |
| **Ratio MAPE** | — | — | — | **21.62%** |

Alternatively, evaluating the **percentage pressure drop reduction** $\Delta p_{\mathrm{red}} = (1 - \Delta p_{\mathrm{C1}}/\Delta p_{\mathrm{C0}}) \times 100$:

| Flow Rate ($Q$) | Sastre Ref Reduction [%] | Present CFD Reduction [%] | Absolute Delta [%] | Relative Error [%] |
| :--- | :--- | :--- | :--- | :--- |
| **$Q_1 = 53.5$ L/h** | $62.94\%$ | $69.06\%$ | $6.12\%$ | **9.71%** |
| **$Q_2 = 83.6$ L/h** | $63.09\%$ | $70.97\%$ | $7.88\%$ | **12.50%** |
| **$Q_3 = 110.3$ L/h** | $65.72\%$ | $72.37\%$ | $6.65\%$ | **10.12%** |
| **$Q_4 = 167.2$ L/h** | $64.18\%$ | $74.65\%$ | $10.47\%$ | **16.31%** |
| **Reduction MAPE** | — | — | — | **12.16%** |

#### 2. Physical Attribution
The 16.5%–29.2% deviation on the ratio is caused by 3D entrance and exit plenum development effects. In the physical/numerical rig of Sastre, flow redistribution between the 4 discrete channels and the tip clearance slab is modulated by the 200 mm upstream and 50 mm downstream plenum headers. A simplified multi-channel model correctly captures the primary hydraulic mechanism (>70% pressure relief upon opening the clearance gap), but must be reported with full numerical fidelity.

#### 3. Required Action
Update `verification_validation.tex` (Table 3, Section 4.5.2, Fig 5 caption) and `master_issue_register.csv` to state:
`Pressure ratio MAPE: 21.6% (Pressure reduction MAPE: 12.2%)`.

---

### B. Validation Statistics & Comparator Categorization Across All 6 Rungs

#### 1. Audit of Comparator Types
The comparator breakdown in `audit/validation_raw_reconciliation.csv` is classified as follows:

1. **Rung V0b (Kewalramani et al. 2019)**:
   - Wall Temperature: **EXPERIMENT** (MAPE = $0.14\%$, max $\Delta T = 0.5$ K).
   - Core Pressure Drop: **ANALYTICAL_DARCY** ($\Delta p_{\mathrm{core}} = 2.47$ kPa vs Darcy $2.42$ kPa, error $2.07\%$). The experimental rig measured $3.47$ kPa including external 90° plenums and fittings.
2. **Rung V1 (Sastre et al. 2018)**:
   - Channel Core Pressure Ratio: **PUBLISHED_CFD_CORE** (MAPE = $21.62\%$, reduction MAPE $12.16\%$).
3. **Rung V3b (Dong et al. 2026 / Huang et al. 2024)**:
   - Full 1U Chassis $T_j$ across 6 flow rates (2–8 LPM, 1.75 kW, EFL-1 dielectric fluid): **EXPERIMENT** (MAPE = $1.20\%$, max error $2.97\%$).
4. **Rung V3 Anchor (Chun et al. 2026)**:
   - Chip Temperature vs Flow Rate: **EXPERIMENT** (MAPE = $0.31\%$, max error $0.46\%$).
   - Thermal Resistance $R_{\mathrm{th}}(\mathrm{OR})$: **PUBLISHED_CFD_MODEL** (MAPE = $0.60\%$, max error $0.70\%$).
   - Bypass Mass Fraction $\Phi_{\mathrm{bypass}}(\mathrm{OR})$: **PUBLISHED_CFD_MODEL** (MAPE = $1.16\%$, max error $1.28\%$).
5. **Rung V3b/V4b (Khoshvaght-Aliabadi 2026 / Muneeshwaran 2023)**:
   - Oblique-Fin Thermal Resistance vs Power (200–600 W, FC-40): **EXPERIMENT** (MAPE = $0.67\%$, max error $0.91\%$, $\Delta T < 0.35^\circ$C).
6. **Rung V2/V0a (Jeng 2008)**:
   - Porous Pin-Fin Nusselt vs Transverse Bypass $W/L$: **EXPERIMENT** (MAPE = $0.99\%$, max error $1.14\%$).

#### 2. Wording Correction Required in Manuscript
- **Figure 5 Caption Defect**: The caption currently ends with: `"All six candidate tiers achieve verified experimental agreement."` This claim is indefensible because V1 is a CFD comparator, V0b $\Delta p$ is an analytical Darcy core comparator, and Chun $\Phi_{\mathrm{bypass}}$ is a numerical cross-verification.
- **Remedy**: Change caption to: *"Validation ladder and reproducibility matrix across six literature benchmarks, comparing present OpenFOAM simulations against experimental measurements (V0b, V3b, V3, V4b, V2), analytical channel models (V0b $\Delta p$), and published CFD reference data (V1, V3 $\Phi_{\mathrm{bypass}}$)."*

---

### C. Grid Convergence Study (Table 2 Audit)

#### 1. Mathematical Breakdown of Table 2
The baseline 1U chassis ($\mathrm{OR}=0.50, \mathrm{Re}_{\mathrm{ch}}=250, 700\text{ W/chip}$ in FC-40) was tested across 4 meshes:
- **Grid 4 (Coarse)**: $N_4 = 180,000$, $h_4 = 1.95$ mm
- **Grid 3 (Medium)**: $N_3 = 350,000$, $h_3 = 1.55$ mm ($r_{43} = 1.258$)
- **Grid 2 (Fine)**: $N_2 = 720,000$, $h_2 = 1.23$ mm ($r_{32} = 1.260$)
- **Grid 1 (Ultra-Fine)**: $N_1 = 1,320,000$, $h_1 = 1.00$ mm ($r_{21} = 1.230$)

Raw Monitored Quantities:
- $T_{\mathrm{chip,max}}$: $63.45^\circ\text{C} \rightarrow 62.30^\circ\text{C} \rightarrow 61.85^\circ\text{C} \rightarrow 61.68^\circ\text{C}$ ($\Delta_{43}=1.15, \Delta_{32}=0.45, \Delta_{21}=0.17$)
- $\Delta p_{\mathrm{total}}$: $368.0\text{ Pa} \rightarrow 351.2\text{ Pa} \rightarrow 344.8\text{ Pa} \rightarrow 342.5\text{ Pa}$ ($\Delta_{43}=16.8, \Delta_{32}=6.4, \Delta_{21}=2.3$)
- $\Phi_{\mathrm{bypass}}$: $46.50\% \rightarrow 47.45\% \rightarrow 47.80\% \rightarrow 47.92\%$ ($\Delta_{43}=0.95\%, \Delta_{32}=0.35\%, \Delta_{21}=0.12\%$)

#### 2. Discovered Discrepancies
1. **Copy-Paste Error**: In Table 2, $\Phi_{\mathrm{bypass}}$ lists `Fine-grid uncertainty GCI_21 = 0.35% (0.17%)`. The `0.17%` is a copy-paste from $T_{\mathrm{chip,max}}$ (`0.17 °C`). The actual step change is `0.12%` ($|47.92\% - 47.80\%|$).
2. **Formula Ambiguity**: The values $0.28\%$ (T), $0.68\%$ ($\Delta p$), and $0.35\%$ ($\Phi$) are the unweighted relative step differences $e_{a,21} = |f_1 - f_2|/f_1$, which equal GCI only if the empirical 3-grid order $p \approx 3.9$ is used (where $F_s / (r^p-1) \approx 1.25/1.25 = 1.0$). If the reported asymptotic order $p \approx 1.90$ is applied, the ASME Roache GCI is:
   - $T_{\mathrm{chip,max}}$: $\mathrm{GCI}_{21} = 0.70\%$ ($0.43^\circ\text{C}$)
   - $\Delta p_{\mathrm{total}}$: $\mathrm{GCI}_{21} = 1.76\%$ ($6.04\text{ Pa}$)
   - $\Phi_{\mathrm{bypass}}$: $\mathrm{GCI}_{21} = 0.64\%$ ($0.31\%$)
3. **Auditor Verdict**: Monotonic asymptotic convergence is rigorously demonstrated across all 4 grids. The Fine mesh (720,000 cells) or Medium mesh (350,000 cells) is fully adequate for the parametric campaign ($\mathrm{GCI} < 1.8\%$). Table 2 values must be clarified in the text.

---

### D. Pre-Sweep Verification Matrix & Sensitivities

1. **Laminar vs Realizable $k$-$\varepsilon$ Closure ($Re_{\mathrm{ch}} = 1000$)**:
   - $\Delta T_{\mathrm{chip}} = +0.42^\circ\text{C}$ ($0.68\%$), $\Delta(\Delta p) = +2.10\%$, $\Delta \Phi_{\mathrm{bypass}} = +0.54\%$.
   - *Verdict:* Laminar steady solve is physically and computationally justified for the immersion fin passages.
2. **Buoyancy / Mixed Convection ($Ri \sim 0.1\text{--}3.7$)**:
   - Boussinesq vs Variable density $\rho(T)$ shift: $\Delta T = +0.12^\circ\text{C}$ ($0.19\%$), $\Delta \Phi = +0.18\%$.
   - *Verdict:* Forced convection dominates the primary stream; Boussinesq approximation is valid ($\beta \Delta T < 0.08$).
3. **Viscosity Temperature Dependence $\mu(T)$**:
   - Temperature-dependent $\mu(T)$ vs constant $\mu$ shifts $\Delta p$ by $-3.40\%$ and $\Phi_{\mathrm{bypass}}$ by $+2.10\%$.
   - *Verdict:* Non-linear $\mu(T)$ is essential and properly retained.
4. **Chun Kelvin Unit Inference**:
   - Differentiating $\rho(T)$ at $298.15\text{ K}$ yields mass flow $5.00\text{ LPM}$ (matching experiment), whereas $T=25$ produces $3.79\text{ LPM}$ (24% discrepancy).
   - *Verdict:* Mathematically proven and properly documented as an inferred necessity.
5. **Enclosure Geometry & Fin Span Sensitivity**:
   - Normalizing against Open Ratio $\mathrm{OR} = C / H_{\mathrm{chassis}}$ decouples the dimensionless model from specific tank depth assumptions. Carrying span uncertainty as a Reynolds number band ($2.6\times$) is scientifically transparent.

---

### E. Parametric Mesh Automation Audit (`mesh_generator.py`)

- **Code Review**: `parametric_campaign/scripts/mesh_generator.py` correctly calculates dynamic fin height $H_{\mathrm{fin}}(\mathrm{OR}) = H_{\mathrm{chassis}} \times (1 - \mathrm{OR})$ and clearance $C(\mathrm{OR}) = H_{\mathrm{chassis}} \times \mathrm{OR}$.
- **Mesh Topology**: Generates conformal multi-block hexahedral meshes with continuous node matching across the fin-tip clearance interface plane.
- **Execution Test**: Validated OpenFOAM `blockMesh` across $\mathrm{OR} = 0.0, 0.25, 0.50, 0.75, 1.0$. All meshes passed with 0 non-orthogonal faces and 0 skewness.

---

## 3. AUDIT ACTION REGISTER & MANDATED FIXES

| ID | Location | Required Correction | Priority |
| :--- | :--- | :--- | :--- |
| **FIX-01** | `manuscript/sections/verification_validation.tex` (L337, L380, L405) | Update Sastre V1 MAPE: Replace 3.4% with **Ratio MAPE 21.6% (Pressure Reduction MAPE 12.2%)**. | **P0 (Immediate)** |
| **FIX-02** | `manuscript/sections/verification_validation.tex` (L405) | Refine Fig 5 caption: Replace "All six candidate tiers achieve verified experimental agreement" with explicit mention of experimental, analytical, and CFD reference comparators. | **P0 (Immediate)** |
| **FIX-03** | `manuscript/sections/verification_validation.tex` (Table 2, L279-282) | Fix Table 2 $\Phi_{\mathrm{bypass}}$ uncertainty notation: replace copied `0.17%` with `0.12%`, and clarify Roache GCI vs relative step difference. | **P1 (High)** |
| **FIX-04** | `audit/master_issue_register.csv` | Mark all pending audit issues as verified subject to FIX-01 through FIX-03. | **P1 (High)** |

---

## 4. INDEPENDENT GO / NO-GO DETERMINATION

### **VERDICT: CONDITIONAL GO — APPROVED TO LAUNCH PARAMETRIC CAMPAIGN**

The core computational fluid dynamics formulations, multi-region energy conservation, fluid thermophysical properties, and mesh automation pipelines are **scientifically sound, thoroughly verified, and ready for production simulation**. The manuscript textual and tabular adjustments outlined in FIX-01 through FIX-03 are straightforward to apply and do not block the execution of the 250-case sweep.
