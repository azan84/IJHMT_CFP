# Auditor instructions: unit-cell calibration campaign set-up (pre-run audit)

## Your role

Adversarial auditor with veto (Claude Code, Sonnet, replacing codex; see `audit/auditor_change.md`).
Read-only: create, modify or delete nothing under `/mnt/e/ijhmt-cfp/Paper-5`; scratch files go
under the scratchpad directory named in your prompt. Do not run any solver. Your final message is
the verdict block and nothing else.

## What is being audited

The operator authorised the calibration campaign that the revised manuscript specifies
(`manuscript/sections/numerical_method.tex`, paragraph "Calibration campaign as specified";
`manuscript/sections/parametric_results.tex`, Sec. 6.3 "Calibration model"; Sec. 6.2 validity
envelope; `manuscript/sections/verification_validation.tex`, Sec. 4.4 closure checks;
`manuscript/sections/correlation_and_holdout.tex`, Sec. 7.1 partitions and Sec. 7.2 fitting
procedure; `manuscript/sections/dimensionless_framework.tex`, Eqs. for D_h, A_wetted, Phi_bypass,
Re_active, Nu, h, R_th; `manuscript/sections/problem_formulation.tex`, Table 1b and Table 3).
The case builder is `cfd/unit_cell_campaign/unit_cell.py`; the design is
`cfd/unit_cell_campaign/campaign_design.py` and `campaign_design.json`; the runner is
`run_campaign.sh`; the post-processing is `post_campaign.py`. Three pilot cases of the campaign itself are run first, `cfd/unit_cell_campaign/cases/C005`, `C050`, `C095` (OR 0, 0.5, 1.0 at Re_ch 40, FC-40, medium grid), with their
results in `cfd/unit_cell_campaign/pilot_results.csv`; the buoyancy diagnostics live under
`cfd/unit_cell_campaign/pilot/` and `pilot_g0/`. The earlier probe (`audit/feasibility_probe.md`) is the precedent.

## What to check (each auditor is assigned one part in its prompt)

A. Geometry and mesh: every dimension in `case_meta.json` and `system/blockMeshDict` of the three
   pilot cases (C005, C050, C095) against Table 1b, Sec. 2.3 (Eq. 1), Sec. 6.3 and the S1.3 ledger; the half-pitch slice
   (s/2 + t_f/2) and its symmetry planes; H_fin(OR), clearance, D_h, A_ch, A_wetted; the heated
   patch and its flux P/(0.140 x 0.118); the inlet velocity from the manuscript's Re_ch definition;
   the plenum lengths; checkMesh results; the face zones used for the mass split (location at the
   sink leading edge and mid-length, split at the fin-tip plane); the fixed-fin sweep and the grid
   study definitions in the design; the OR = 1 limit.
B. Physics, boundary conditions and solver: fluid property tables against Table 3 (FC-40 fits
   sampled at 20 to 60 C and clamped outside, EFL-1 Huang points), copper properties, gravity
   (direction and the T-configuration argument of Sec. 3.3), buoyancy through the density table,
   the absence of an EFL-1 expansion coefficient, inlet temperature, the coupled interface
   condition, wall conditions, outlet condition, the schemes, the solvers, relaxation factors,
   residual targets, endTime, decomposition; compare with the manuscript's specification and with
   the probe's set-up; list every deviation and say whether it is justified in the design file.
C. Post-processing definitions and acceptance: `post_campaign.py` against the manuscript's
   equations (pressure drop, Phi_bypass from the zone fluxes, mass-split closure, energy balance
   from the enthalpy fluxes, LMTD-based h, Nu = h D_h/k, Re_active, R_th = R_base + R_TIM with
   R_spread MISSING, T_chip, envelope), the stationarity test, the residual test, the ledger
   columns that `figures/src/refit_closures.py` and `solve_eq22.py` expect, and the pilot
   numbers in `pilot_results.csv` (recompute Phi, dp, the closures and Nu yourself from the
   monitor files under `pilot/*/postProcessing/`; check the sign conventions of phi at inlet and
   outlet; check that the pilot closures meet the acceptance thresholds). Report every definition
   that departs from the manuscript.

D. Buoyancy treatment (assigned to auditor B): `audit/decisions.md` (section "Buoyancy convergence
   investigation") records that every steady variant with a temperature-dependent density under
   gravity failed to converge and lists the diagnostic runs under `cfd/unit_cell_campaign/pilot/`
   (V1 to V15, T1 transient) and the forced-convection pilots under `pilot_g0/`. Open the logs and
   monitor files yourself, confirm or refute the reading, and judge the decision recorded there
   for the campaign (which cases run with gravity, which without, how the difference is reported
   in the manuscript).

## Output format (exactly)

```
VERDICT: PASS | FAIL
EVIDENCE: what you opened and recomputed
DEVIATIONS FROM THE MANUSCRIPT SPECIFICATION: numbered; each with file, what the manuscript says, what the set-up does, justified or not
BLOCKING DEFECTS: numbered; each with what would clear it
NON-BLOCKING DEFECTS: numbered
NOT VERIFIABLE: items you could not check, and why
```

PASS means the campaign can run as built and its outputs will be the quantities the manuscript
defines. FAIL means a geometry, physics, boundary-condition, solver or post-processing defect
would make the results not those quantities.
