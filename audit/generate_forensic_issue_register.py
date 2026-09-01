#!/usr/bin/env python3
"""
Generate Master Forensic Issue Register for IJHMT Paper-5.
"""

import csv
import os

issues = [
    {
        "Issue_ID": "ISSUE-A01",
        "Manuscript_Location": "Section 4 (Table 2) vs Section 6 (Table 4 / Table 11)",
        "Current_Value_Claim": "Grid study reports T_max=61.85 C, dp=344.8 Pa at OR=0.50, Re=250; Parametric sweep reports R_th=0.2506 K/W (T_max=200.4 C), dp=0.080 Pa",
        "Conflicting_Value_Claim": "Re=250 condition shows 4000x difference in dp (344.8 Pa vs 0.080 Pa) and 138 C difference in T_max",
        "Likely_Cause": "Discrepancy in Re definition (Re_core based on fin spacing at Q=10 LPM in Chun anchor vs Re_chassis based on full duct hydraulic diameter at u_in=0.007 m/s in sweep) and geometry (lateral inter-blade bypass vs overhead tip clearance)",
        "Source_Files_Scripts": "cfd/chun_v3/run_chun_validation.py, parametric_campaign/scripts/generate_doe_matrix.py, manuscript/sections/verification_validation.tex",
        "Action_Required": "Explicitly define and document Re_global vs Re_core in Section 2, document exact flow rates (2.61 LPM vs 10 LPM), and separate lateral bypass from overhead clearance",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-B01",
        "Manuscript_Location": "Section 6 (Table 4), Section 5.3, Fig 9",
        "Current_Value_Claim": "W_pump reported as 3.48 mW, FOM reported as 39,904 K^-1 W^-1 at OR=0.50, Re=250",
        "Conflicting_Value_Claim": "SI calculation: Q=2.61 LPM (4.35e-5 m^3/s) * dp=0.080 Pa = 3.48e-6 W = 3.48 uW (not 3.48 mW). True FOM = 1/(0.2506 * 3.48e-6) = 1.15e6 K^-1 W^-1",
        "Likely_Cause": "1000x unit label error (mW instead of uW) and inconsistent FOM formula scaling",
        "Source_Files_Scripts": "parametric_campaign/scripts/postprocess_case.py, manuscript/sections/parametric_results.tex",
        "Action_Required": "Recompute W_pump in explicit SI (W and uW), recompute exact FOM across all 250 cases, update Table 4, Fig 9, and manuscript narrative",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-C01",
        "Manuscript_Location": "Section 2.2, Section 5.2, Nomenclature",
        "Current_Value_Claim": "Chun open ratio (lateral inlet area ratio without tip clearance) conflated with vertical tip clearance OR = c / (H_chassis - H_base)",
        "Conflicting_Value_Claim": "Two distinct physical bypass mechanisms represented with same acronym 'OR'",
        "Likely_Cause": "Direct translation from Chun et al. (2026) without geometric decoupling for 1U top-clearance chassis",
        "Source_Files_Scripts": "manuscript/sections/problem_formulation.tex, manuscript/sections/dimensionless_framework.tex",
        "Action_Required": "Standardize vertical tip clearance definition OR = c / (H_chassis - H_base) throughout all equations, figures, and text; designate Chun's lateral bypass as an independent validation tier",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-D01",
        "Manuscript_Location": "Section 5.2 (Eq. 24), Section 7.2 (Eq. 30)",
        "Current_Value_Claim": "Fitted bypass equation with delta=0.1052 yields Phi(0) = 15.22% and Phi(1) = 67.74%",
        "Conflicting_Value_Claim": "Violates theoretical physical bounds lim_{OR->0} Phi = 0% and lim_{OR->1} Phi = 100% as stated in Section 5",
        "Likely_Cause": "Unconstrained curve fitting with offset delta to capture flat-duct flow",
        "Source_Files_Scripts": "parametric_campaign/scripts/fit_dimensionless_framework.py, manuscript/sections/correlation_and_holdout.tex",
        "Action_Required": "Refit using physics-constrained functional form Phi = 1 / [1 + C1 ((1-OR)/OR)^m Re^n Pr^k] strictly enforcing boundary limits, and report exact calibration vs holdout metrics",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-E01",
        "Manuscript_Location": "Abstract, Introduction, Section 5",
        "Current_Value_Claim": "Abstract claims Pr = 9.2 to 210, but parametric campaign tested FC-40 (Pr=67.5), PAO-4 (Pr=72.0-219.5), and EFL-1 (Pr=47.5)",
        "Conflicting_Value_Claim": "Surveyed fluids (Novec 7100 Pr=9.2, Mineral oil Pr=210) included in claim without being in parametric matrix",
        "Likely_Cause": "Broad literature survey range combined with simulated sweep range",
        "Source_Files_Scripts": "manuscript/main.tex, parametric_campaign/scripts/generate_doe_matrix.py",
        "Action_Required": "State exact simulated Pr range (Pr = 47.5 to 219.5) in abstract and results; separate simulated fluid matrix from literature survey",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-F01",
        "Manuscript_Location": "Introduction (L105-109), Discussion (Section 8.1)",
        "Current_Value_Claim": "Coolant ranking inverts across open ratios",
        "Conflicting_Value_Claim": "Ranking depends strongly on comparison basis (matched Q vs matched pumping power vs matched Re)",
        "Likely_Cause": "Comparing fluids at equal Reynolds number without accounting for 10x kinematic viscosity differences",
        "Source_Files_Scripts": "manuscript/main.tex, manuscript/sections/discussion.tex",
        "Action_Required": "Systematically compare coolants on 3 distinct bases: matched volumetric flow Q, matched pumping power W_pump, and matched Re; report exact conditions where crossovers occur",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-G01",
        "Manuscript_Location": "Section 6.2, Table 4, Section 8",
        "Current_Value_Claim": "Reporting peak temperatures up to 376.4 C at low flow rates (Re=25-50, 700 W)",
        "Conflicting_Value_Claim": "FC-40 boiling point is 155-165 C; single-phase model cannot physically operate at 376 C",
        "Likely_Cause": "Executing full DOE factorial matrix without pre-filtering thermal failure limits",
        "Source_Files_Scripts": "parametric_campaign/results/parametric_results.json, manuscript/sections/parametric_results.tex",
        "Action_Required": "Classify all 250 cases into (1) Feasible Operating Envelope (T_chip <= 85 C), (2) Throttling Envelope (85-115 C), and (3) Failure Envelope (>115 C); construct 2D Feasible Operating Map",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-H01",
        "Manuscript_Location": "Section 7.1 (Partitioning and holdout strategy)",
        "Current_Value_Claim": "Text claims 151 holdout cases, but subgroups (35+35+24+24+25+16) sum to 159",
        "Conflicting_Value_Claim": "Sum of subgroups (159) exceeds stated total holdout size (151) out of 250 total cases",
        "Likely_Cause": "Subgroup overlap between thermal load sweep and baseline geometries",
        "Source_Files_Scripts": "manuscript/sections/correlation_and_holdout.tex, audit/master_case_ledger.csv",
        "Action_Required": "Define strict mutually exclusive partitions in audit/master_case_ledger.csv: 99 calibration, 70 fluid holdout, 48 topology holdout, 25 power holdout, 16 cross-validation holdout",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-I01",
        "Manuscript_Location": "Abstract, Introduction, Section 6, Section 7, Section 9, Tables",
        "Current_Value_Claim": "Multiple discrepancies: PAO-4 Nu MAPE reported as 3.18% in Table 6 vs 31.79% in CSV; bypass MAE 5.72 vs 6.74 pp; R_th error 0.75% vs 1.45%",
        "Conflicting_Value_Claim": "Internal text vs table vs CSV statistical contradictions across manuscript sections",
        "Likely_Cause": "Iterative draft updates without automated manuscript-wide data reconciliation",
        "Source_Files_Scripts": "manuscript/main.tex, manuscript/sections/*.tex, audit/final_holdout_validation_statistics.csv",
        "Action_Required": "Write and run automated verification script audit/verify_manuscript_numbers.py to enforce 100% agreement across all sections and CSVs",
        "Status": "OPEN - REMEDIATING"
    },
    {
        "Issue_ID": "ISSUE-J01",
        "Manuscript_Location": "Section 5.3, Section 7.3",
        "Current_Value_Claim": "R_th prediction error is <0.84% across all holdout fluids even when Nu error is 31.79%",
        "Conflicting_Value_Claim": "Apparent paradox: high Nu error produces low R_th error without physical explanation",
        "Likely_Cause": "Conjugate thermal resistance breakdown: conductive base and TIM resistance (R_TIM + R_spread) dampen convective sensitivity",
        "Source_Files_Scripts": "parametric_campaign/scripts/scientific_analysis_and_figures.py, manuscript/sections/correlation_and_holdout.tex",
        "Action_Required": "Decompose R_total = R_TIM + R_spread + R_conv, compute fraction of convective resistance across OR and Re, and evaluate errors on Nu, h, R_conv, and R_th independently",
        "Status": "OPEN - REMEDIATING"
    }
]

out_csv = '/mnt/e/ijhmt-cfp/Paper-5/audit/forensic_issue_register.csv'
with open(out_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(issues[0].keys()))
    writer.writeheader()
    for row in issues:
        writer.writerow(row)

out_md = '/mnt/e/ijhmt-cfp/Paper-5/audit/forensic_issue_register.md'
with open(out_md, 'w') as f:
    f.write('# MASTER FORENSIC ISSUE REGISTER (Q1-Level Audit)\n')
    f.write('**Project:** Dimensionless framework for bypass-controlled single-phase immersion cooling of server heat sinks\n')
    f.write('**Standard:** International Journal of Heat and Mass Transfer (IJHMT) / Applied Thermal Engineering\n\n')
    f.write('| Issue ID | Manuscript Location | Current Value / Claim | Conflicting Value / Claim | Likely Cause | Source Files | Action Required | Status |\n')
    f.write('| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n')
    for r in issues:
        f.write(f"| **{r['Issue_ID']}** | {r['Manuscript_Location']} | {r['Current_Value_Claim']} | {r['Conflicting_Value_Claim']} | {r['Likely_Cause']} | `{r['Source_Files_Scripts']}` | {r['Action_Required']} | **{r['Status']}** |\n")

print(f'Generated forensic issue register with {len(issues)} items in CSV and MD.')
