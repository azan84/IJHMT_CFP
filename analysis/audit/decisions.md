# Phase 2 decisions (B1 to B5, B8, B12, B13, plus C1), corrected after Gate 2 round 1 (`audit/gate_2_codex_round1.md`)

Every decision below is conditioned on the Phase 1 finding that no thermal or bypass CFD data
exist (OD-01 to OD-09). Where an item asks for a refit, a re-solved optimisation or a
data-driven decomposition, the decision is BLOCKED: it cannot be executed on formula outputs
without re-presenting them as simulation results, which Hard Rules 1 and 2 forbid. Items that
are decidable on principle are decided.

| Item | Decision | Evidence | Manuscript sections affected |
|---|---|---|---|
| B1 | (i) State in Sec. 2.3 and Sec. 6 that OR as defined by Eq. (1) couples fin height, wetted area, D_h, fin efficiency and clearance (the analytic definition; the executed campaign varied none of them: its meshes have no fins or base, and its post-processing used a fixed wetted area 0.052 m2, a fixed thermal D_h 4.2 mm and the fixed duct D_h 67.5 mm), that no base thickness exists in the meshes, and that the Table 1 base sink (H_f = 20.9 mm) corresponds to OR = 1 - 20.9/39.95 = 0.477, written 0.48, under Eq. (1). (ii) Rename to "structural recess ratio". (iii) The analytic decomposition of Delta R_th into the A_wetted(OR) and (1 - Phi) terms is BLOCKED: there is no R_th data to decompose. The fixed-fin sweep is deferred to the operator (see feasibility probe). | `audit/table1b_geometry_as_run.csv`; `audit/rth_trace.md` | 2.3, 5, 6, 8.1 |
| B2 | Eq. (23) as printed returns Phi = 1.000 at OR = 1 (epsilon = 1e-4) but Phi(0) = 0.0224, i.e. 2.24 %, at OR = 0 and Re = 250: with a fixed epsilon the sealed limit is approximate, not exact, so the frozen sentence "strictly satisfies the limiting bounds" was false on both counts. The "CFD" endpoint 59.3 % was the formula `(1 - e^-3.5)(48.41 + 18.2 log10(Re/50))` (59.285 %). Neither number is a simulation result. Decision: delete the fitted coefficients and the limiting-bounds sentences; keep Eq. (23) only as a functional form whose limits hold as epsilon -> 0. Option (a)/(b) and the MAE re-report are BLOCKED until real data exist; the rule written into Sec. 5.2 is option (b) of the brief: if the residual at the recessed end of a future fit exceeds the stated tolerance, restrict the closure to OR <= 0.75 and refit. | `audit/src/physics_checks.py` (B2 lines); `audit/formula_reproduction.csv` | 5.2.1, 7.1.1, Table 12 |
| B3 | The Pr exponent (k = -0.0086) and its confidence interval were fitted to formula data in which Phi does not depend on the fluid at all (the formula has no fluid input); the exponent is therefore an artefact and Pr is dropped from the closure form. The matched-Q against matched-Re paragraph for Sec. 7.1.1 is written on principle (the two comparisons differ by the factor nu_PAO-4/nu_FC-40 = 9.5 in flow rate) without numbers. | `parametric_campaign/scripts/postprocess_case.py` lines 48-56 (no fluid dependence in Phi; the viscosity ratio nu_PAO-4/nu_FC-40 on the campaign constants is 1.786e-5/1.887e-6 = 9.47) | 7.1.1, 8.2 |
| B4 | Envelope defined: wall temperature <= 70 C (Sec. 2.4 viscosity fit valid 20-60 C plus 10 C margin) and T_chip <= 165 C (FC-40 boiling point). No wall temperature exists in any file, so the ledger flag applies both bounds to the formula chip temperature as a proxy (73 of 250 below 165 C, 2 of 250 below 70 C, hence 2 flagged "inside"); this is a bookkeeping count on formula output, not an envelope evaluation. Refit and re-reporting BLOCKED. The envelope stays in the manuscript as the acceptance rule for any future campaign. | `audit/dataset_ledger.csv` (`passed_validity_envelope`) | 2.4, 6, 7, Table 12 |
| B5 | Eq. (22) cannot be solved on the corrected data because there are none. On the formula's own numbers at 700 W and Re <= 1000: for FC-40 (the basis of the frozen claim) the feasible set is empty (formula floor R_th = 0.1363 K/W gives T_chip >= 120 C; file value 123.5 C), and for EFL-1 likewise (floor 0.1523 K/W); for PAO-4 four formula rows satisfy both constraints, the lowest pumping power being DOE_Case_104 (OR = 0.10, Re label 250, R_th 0.0802 K/W, 82.6 C). So the frozen conclusion OR <= 0.15 does not follow from the FC-40 data that produced it, and the PAO-4 rows are formula output on unsourced properties (B12). Decision: delete the optimum, the 85 C envelope claim and Fig. 7(b); keep Eq. (22) as the stated design problem. | `audit/src/physics_checks.py` (B5 and B6 lines); `parametric_campaign/results/parametric_results.csv` | 5.5, 6.3, 6.4, 8.3, 9, abstract |
| B6 | Pumping-power reduction at OR = 0.15 interpolated from Table 11 is 17.8 % (13.3 % at OR 0.10, 26.6 % at OR 0.25), not 25-40 %; but Table 11 itself is formula output, so all five occurrences are deleted rather than replaced. | `audit/src/physics_checks.py` | abstract, 5.5, 6.4, 8.3, 9 |
| B8 | Nu_fd for the manuscript channels from the Shah and London rectangular-duct polynomials: alpha = s/H_fin = 0.0238 at OR = 0 (39.95 mm) gives 7.85 (H1) and 7.09 (T); alpha = 0.0475 at OR = 0.5 (20.0 mm) gives 7.49 and 6.69; the Table 1 base sink (20.9 mm, alpha = 0.0455) gives 7.52 and 6.72; against 4.36 (circular tube). Decision: state the rectangular-duct asymptote (H1, 7.85 at alpha 0.024, 7.49 at alpha 0.048, 7.52 for the base sink) in Eq. (24); remove the fitted 4.4303; 4.36 is retained only as the contrast value it replaces. Refit BLOCKED. | `audit/src/physics_checks.py` (B8 lines) | 5.4, 7.1.2 |
| B9 | Ri at 3 LPM and 1 LPM on the Table 1 channel recomputed as 0.66 and 5.95 (manuscript: 0.4 and 3.7; the difference is Gr with D_h = 1.817 mm and the quoted Re). Wording replaced by "mixed convection" with the buoyancy effect on Phi, T_chip and Delta p left as MISSING (Table 10 has no source). | `audit/src/physics_checks.py` (B9 lines) | 3.3 |
| B11 | Eq. (15) presented as a physically motivated form with limits, not as a derivation. Decidable on principle; no data needed. | manuscript Eq. (13)-(15) | 5.2 |
| B12 | GC-5X moved to the anchor-comparison subsection; "two working fluids" framing removed. FC-40: the Table 3 value Pr = 67.5 at 25 C is consistent with Chun's kelvin fits (mu = 4.20 mPa s, k = 0.0654, cp = 1052), whereas the campaign constants (mu = 3.50 mPa s, Pr = 56.3) have no source; the manuscript keeps 67.5. EFL-1 constants (rho 1889, cp 1165, k 0.068, mu 2.77 mPa s, Pr 47.5) match Huang et al. 2024 Table 2 (`extraction/huang-energy297-high-power-server.md` lines 58-64) but k and mu are the 40 C entries (20 C: k 0.062, mu 6.31 mPa s, Pr 118.6), so the campaign mixed a 40 C EFL-1 with a 25 C FC-40; Table 3 must state the temperature; PAO-4 constants (795, 2210, 0.143, 14.2 mPa s, Pr 219.5) have no source anywhere in the repository and are written as MISSING. Abstract Pr range: no regression exists, so the range is deleted. | `parametric_campaign/scripts/generate_doe_matrix.py`; `audit/provenance.csv` | 2.4, Table 3, abstract, 6-9 |
| B13 | The DOE contains duct Reynolds numbers 25 to 1000 only; the 350/1000/1748 ladder of Sec. 3.4 never ran (no case). Sec. 3.4 is rewritten to state the range actually meshed and that the channel Reynolds number of Sec. 2.1 was 1 to 39 at OR = 0 (up to 322 at OR = 0.9) for the same flows. Abstract range deleted with the regression. | `audit/re_recompute.csv`; `audit/case_inventory.csv` | 3.4, abstract |
| C1 | The PAO-4 R_th MAPE of 33.97 % is not a physics result. The evaluation script predicts R_th with fixed resistances 0.035 + 0.025 K/W, a wetted area 0.065 m2, D_h 3.6 mm and a single scale factor 1.0474 calibrated on FC-40 (master_scientific_engine.py lines 136-167), while the data-generating formula uses R_TIM = 0.009 K/W, no spreading term, 0.052 m2 and D_h 4.2 mm; the scale factor absorbs the mismatch for FC-40 (k = 0.0654) and cannot for PAO-4 (k = 0.143). Replacing the script's network by the generator's, with the same fitted Nu, lowers the PAO-4 MAPE from 33.97 % to 7.72 % (`audit/src/physics_checks.py`, C1 line): the network mismatch is the dominant part of the error, the remainder is the Nu closure's own misfit. The three physical hypotheses in the brief (R_spread transferability, viscosity-ratio term, caloric term) cannot be tested without data. Decision: delete the PAO-4 statistics and the explanation. | `parametric_campaign/scripts/master_scientific_engine.py` lines 136-167; `audit/src/physics_checks.py` (C1 line); `scientific_analysis_and_figures.py` line 120 (k = 0.068 hard-coded for all fluids) | 7.2, abstract, 9 |

## Refit, optimisation and subgroup statistics

`audit/refit_stats.csv` and `audit/optimum.csv` are written with a single row each stating
BLOCKED and the reason, so that the deliverable list is complete and codex can verify that no
statistic was produced from formula data. The fitting and optimisation scripts
(`figures/src/refit_closures.py`, `figures/src/solve_eq22.py`) implement the brief's
specification against the ledger schema: the refit fits Eq. (23) (C1, m, n) and Eq. (24) (C2, p
with Nu_fd fixed at the Shah-London value) with standard errors, t-based 95 % confidence
intervals, objective and bounds, and writes per-partition Phi MAE, Phi MAPE (OR >= 0.10), R_th
MAPE, RMSE, maximum error and R^2 to `audit/refit_stats.csv`; the optimisation enforces one
basis (fluid, topology, load), requires a unique sealed reference per Reynolds level, writes the
feasibility map (`audit/feasibility_map.csv`) and the optimum or NO_FEASIBLE_POINT to
`audit/optimum.csv`. Both refuse (exit 2) when `thermal_data_source` starts with "none" for every
row, which is the case for the archived ledger ("none (formula)"), and both carry a `--selftest`
that recovers known coefficients from synthetic data (a software check, not a result:
`audit/refit_stats_selftest.csv`, `audit/optimum_selftest.csv`, `audit/feasibility_map_selftest.csv`).

## Campaign design (3 September 2026, operator's go-ahead; unit-cell calibration campaign)

Recorded so that every choice not fixed by the manuscript is visible to the auditor
(`cfd/unit_cell_campaign/campaign_design.py`, `campaign_design.json`, `unit_cell.py`):

| Choice | Decision | Basis |
|---|---|---|
| Model | spanwise-periodic half-pitch conjugate unit cell (Sec. 6.3), `chtMultiRegionSimpleFoam`, medium grid (about 52k to 66k cells) | manuscript Sec. 6.3; feasibility probe |
| Channel Reynolds levels | 2, 5, 10, 20, 40, 70, 100, 150, 250 on the manuscript's channel definition (all flow through the fins, properties at the 25 C inlet) | Sec. 2.1 (base geometry 9 to 104 at 1 to 3 LPM), Sec. 3.4 (anchor 1.2 to 227); the archived duct labels are not used |
| Recess ratios | 0 to 1 in steps of 0.1; cross-combinations at 0.15, 0.35, 0.65, 0.85 | Sec. 7.1 |
| Partitions | calibration 99 (FC-40, 700 W); EFL-1 33 + 2 cross; thermal load 25 (300 to 1200 W at OR 0, 0.25, 0.5, 0.75, 1 and Re 40); cross-combinations 12 FC-40 + 2 EFL-1; grid study 2 (coarse, fine at OR 0.5, Re 150); fixed-fin sweep 4 (H_fin 20.9 mm, clearance 0, 5, 10, 19.05 mm at Re 40): 177 cases | Sec. 7.1 adapted: PAO-4 not run (properties have no source, Table 3); pin-fin and oblique-fin not representable |
| Fluid properties | FC-40: Chun fits of Table 3 tabulated at 20, 30, 40, 50, 60 C, linearly interpolated and clamped outside the band (OpenFOAM tabulated thermo); EFL-1: Huang Table 2 points at 20, 40, 60 C for mu and k, rho and cp single values | Sec. 3.3 "temperature-dependent mu, k, cp ... restricted to its validity band" |
| Buoyancy | gravity 9.81 m/s2 along -x (flow vertical upward, the base paper's T-configuration: coolant enters through the tank floor beneath the sink); density from the FC-40 table (subsumes the Boussinesq form of Sec. 3.3); no buoyancy for EFL-1 (no expansion coefficient sourced; density constant) | Sec. 3.3; Sec. 2.1; assumption on the direction recorded |
| Load | uniform flux on the base underside over the sink footprint, P/(0.140 x 0.118 m2) | Sec. 6.3 |
| Solver settings | GAMG p_rgh, smooth solvers U and h, relaxation p 0.3 / U 0.7 / h 0.9, residual targets p_rgh 1e-5, U 1e-5, h 1e-6 (tighter than the specified 1e-4 / 1e-6 so that the monitors are stationary), endTime 4000, 8 ranks per case | Sec. 3.5 |
| Acceptance | residual targets met; the four monitors of Sec. 3.5 stationary over the last 500 iterations within 0.5 %; mass-split closure 0.5 %; energy balance 0.5 % of the load; envelope wall <= 70 C, chip <= 165 C | Sec. 3.5, 4.4, 6.2 |
| Post-processing | Delta p from the inlet and outlet area-averaged static pressures; Phi from the face-zone mass fluxes at the sink leading edge (and mid-length as a check), split at the fin-tip plane; energy balance from the enthalpy fluxes; h from the fin-surface heat flux and the log-mean temperature difference; Nu = h D_h / k(T_film); Re_active = Re_ch (1 - Phi); R_th = (T_base,max - T_in)/P + R_TIM with R_spread MISSING (no sourced spreading model) | Sec. 4.4, 5.3, 5.4, 7.2; Eq. (tim) |
| Pilot | OR 0, 0.5, 1.0 at Re 40 run first and audited (geometry, physics and boundary conditions, solver, post-processing) before the campaign | operator's instruction |

### Buoyancy convergence investigation (4 September 2026, before the campaign)

The OR = 0.5, Re_ch = 40 pilot with gravity and the temperature-dependent density did not converge
(steady solver, 4000 iterations: p_rgh residual 0.39, continuity error of order 200, energy
balance 22 % off). Diagnostic variants of the same case (600 to 800 iterations each, 8 ranks):

| Variant | Gravity | Density | Other change | Result at the last iteration |
|---|---|---|---|---|
| V1 | off | FC-40 table | none | converging (p_rgh 8e-3, continuity 3e-3) |
| V2 | on | constant 1855 | none | converging (p_rgh 2e-3, continuity 6e-4) |
| V3 | on | Boussinesq, beta 1.16e-3 | const transport | not converging (p_rgh 0.38, continuity 194) |
| V4 | off | constant | none | converging |
| V5 | on | Boussinesq | outlet U pressureInletOutletVelocity | not converging |
| V6 | on | Boussinesq | relaxation p 0.2, U 0.5, h 0.7 | not converging, error growing |
| V7 | on | FC-40 table | outlet U pressureInletOutletVelocity | not converging |
| V8 | on | FC-40 table | OR 0.5, Re 150 | not converging (p_rgh 0.27) |
| V9 | on | FC-40 table | OR 0, Re 40 (sealed) | borderline (p_rgh 3e-3, continuity 1.8) |
| V10 | on | FC-40 table | OR 0.5, Re 250 | not converging (p_rgh 0.15) |
| V11 | on | FC-40 table | OR 0.2, Re 40 | not converging (p_rgh 0.03, continuity 17) |
| V12 | on | FC-40 table | relaxation p 0.7, U 0.3, h 0.5 | drifting (p_rgh 0.02, continuity 5) |
| V13 | on | FC-40 table | no momentum predictor | not converging |
| V14 | 0.1 g | FC-40 table | none | not converging (p_rgh 0.12, continuity 9) |

Reading: every variant with a temperature-dependent density under gravity fails, every variant
without buoyancy converges; the outlet condition, the momentum predictor and the relaxation
factors do not change the outcome, and one tenth of gravity is enough to spoil it. The buoyant
velocity scale (g beta Delta T L)^0.5 is about 0.16 m/s against an inlet velocity of 0.02 m/s at
Re 40 and a channel-gap Rayleigh number of order 1e7, so the flow is buoyancy dominated over most
of the design space with a clearance. Two diagnostics decide the treatment: a 3000-iteration
steady run with the best relaxation (V15) and a transient solve of the same case on the coarse
grid (T1, chtMultiRegionFoam, 40 s of physical time) to see whether a steady state exists.
Decision recorded below once they finish.

**Decision (4 September 2026, 08:20):** the campaign runs without the gravitational body force
(forced convection with the temperature-dependent property tables). Grounds: (i) with gravity and
a temperature-dependent density neither the steady solver (V3 to V15, up to 3000 iterations,
best case p_rgh residual 6e-3 and continuity error of order 1 with the integral monitors
stationary within 0.1 K) nor the transient solver (T1, T2: floating-point failures from the
pressure-work term and from the reduced-heat-capacity start; the corrected T2 advanced 0.29 s of
physical time in 40 minutes, which makes a 40 s transient per case infeasible for 177 cases) gives
an acceptable solution at the pilot conditions; (ii) without the body force the sealed case
converges to residuals below 1e-9 with the energy balance closed to 0.05 %; (iii) the framework
being calibrated (Eqs. 23 and 24) is a forced-convection framework in which buoyancy is not a
variable. Consequence for the manuscript: the "Boussinesq body force" of the specification is
replaced by a statement that the calibration runs are forced convection, the Richardson numbers
of Sec. 3.3 are kept as the measure of the neglected effect, and the buoyancy effect on the split
and on the temperatures at Ri of order 1 and above is recorded as an open item (a dedicated
transient study on a coarse grid at one or two low-Reynolds conditions). Hot, starved cases
(clearance open at low Reynolds number: base above 100 C in the OR 0.5 and OR 1 pilots at Re 40)
lie outside the validity envelope and converge slowly or not at all with the clamped property
tables; they are run to the iteration cap, reported with their final monitor values and
excluded by the envelope and acceptance filters. A residual watchdog stops each case once the
fluid residuals (U, p_rgh 1e-5; h 1e-6) are met after 600 iterations, since the steady
multi-region solver does not act on residualControl.

## Pressure-solver inner-iteration cap (4 September 2026, during batch 1)

Observation: in the low-Reynolds cases the GAMG solve of p_rgh stalled at a residual floor of about
3e-8 once the outer p_rgh residual fell below about 3e-6, so the relative tolerance (0.01) could not
be met and every SIMPLE step consumed the default 1000 inner iterations (C001: 1521 of the first
2183 steps; C002: 1250 of 3405; C004: 583 of 3115; C003: 142 of 4000; C050 at Re_ch 40: none).
Those steps cost about 0.9 s against 0.12 s for a step whose inner solve meets the tolerance (70 to
170 iterations in the sealed pilot C005).

Decision: `maxIter 200` was added to the p_rgh solver entry of `unit_cell.py` and to
`system/fluid/fvSolution` of every case not yet finished at 09:40 (the two running cases, C001 and
C002, picked it up through `runTimeModifiable`). The four cases finished before the change (C003,
C004, C005, C050) ran with the default of 1000. The cap bounds the inner solve only; the converged
solution is defined by the outer residual targets and the stationarity check, which are unchanged,
and a step whose inner solve meets the tolerance is unaffected. The change is a numerical control,
not a physical or boundary-condition change; it is reported to the auditor for the results audit.

## Iteration cap, envelope stop and continuation pass (4 September 2026, 11:10, during batch 1)

Observation after 26 finished cases: at OR = 0 every case met the acceptance residuals (U and p_rgh
below 1e-4, h below 1e-6), but at OR = 0.1 and 0.2 the cases with Re_ch <= 40 to 70 reached the
4000-iteration cap with residuals still falling by about a factor of two per 1000 iterations
(C014, OR 0.1, Re 40: Uz 4.1e-4, h 6.4e-5 at 4000; the four monitors stationary to 1e-5) while the
cases at Re_ch >= 70 to 100 converged in 700 to 3500 iterations. Cases outside the wall bound of
the envelope (C010, C019 to C021, C050: 79 to 198 C) are excluded whatever their residuals.

Decision: (i) the cap is 12,000 iterations for every case not yet started at 11:10 (`endTime` in
`system/controlDict`, `unit_cell.py` updated); (ii) the watchdog (`converge_watchdog.py`) stops a
case at or after 4000 iterations when its maximum fluid-solid interface temperature exceeds the
70 C wall bound (`ENVELOPE_STOP`), because such a case cannot enter the dataset; (iii) cases that
had already stopped at 4000 inside the wall bound and short of the acceptance residuals are
continued from their latest time to 12,000 iterations in a continuation pass
(`select_continuations.py`, `continue_cases.sh`; first-pass DONE and solver logs kept as
`DONE_pass1` and `log.chtMultiRegionSimpleFoam.pass1`) after batch 2; (iv) the monitor readers of
`post_campaign.py` and the watchdog order the time directories numerically so that a restart's
monitor files (`postProcessing/*/*/4000/`) follow the first pass. The acceptance criteria are
unchanged; a case still short of them at 12,000 iterations is reported as not converged.

Addendum (11:50): C018 (OR 0.1, Re_ch 250; the grid-study medium case) met the residual stop at 676
iterations but failed the stationarity test because the 500-iteration window reached back into the
initial transient (range 1.0 % against the 0.5 % tolerance). The watchdog's minimum iteration count
is therefore 1200 for every case started from now on (`run_campaign.sh`, `continue_cases.sh`), and
`select_continuations.py` also continues every case that stopped before 1200 iterations, so that the
stationarity window lies past the transient. Cases run before this change that stopped at or after
1200 iterations are unaffected.

## Driving temperature difference of the Nusselt number (4 September 2026, 11:50)

Observation on the first converged cases: at OR = 0 and Re_ch = 2, 5 and 10 the outlet bulk
temperature (330.5, 311.3, 304.8 K) exceeds the area-mean fluid-solid interface temperature (321.9,
307.9, 303.9 K), because the base is a uniform-flux boundary whose temperature rises along the sink
by more than the local wall-to-bulk difference. The isothermal-wall log-mean temperature difference
(LMTD) specified in Section 7.2 is then undefined (the script had fallen back to the inlet
difference, giving Nu = 0.77 at Re_ch = 2).

Decision: the ledger's Nu uses the arithmetic-mean bulk difference, T_wall,mean - (T_in + T_out)/2,
the uniform-heat-flux form consistent with the Shah-London H1 asymptote of Eq. (24); it is defined
for every case. The LMTD-based value is kept in the ledger as `Nu_lmtd` (NaN where undefined) for
comparison. The bulk temperatures are those of the whole cell flow (channel plus clearance) at the
cell inlet and outlet, so Nu is a cell-average coefficient. Section 7.2 was reworded before any fit
was made; no result depends on the earlier form. Reported to the auditor for the results audit.

Addendum (11:58): with the cell-mixed bulk the coefficient still carried the bypass split (the
clearance stream leaves nearly at the inlet temperature and lowers the mixed outlet temperature),
so it was not the channel coefficient that Eq. (24) models with Re_active. Face zones at the sink
trailing edge (x = L; `chanOut`, `clearOut`) were added post hoc to every finished case and the
mass-flux-weighted mean temperature and the mass flux on the leading-edge and trailing-edge zones
were read from the final written fields with `postProcess` (`posthoc_zone_T.py`, results in
`<case>/posthoc_zoneT.json`; empty zones skipped). The ledger's Nu uses the channel-stream bulk
temperatures at the two edges, T_wall,mean - (T_ch,in + T_ch,out)/2; the cell-mixed form is kept
as `Nu_cell` and the log-mean form as `Nu_lmtd`. The trailing-edge split is kept as `Phi_out`: the
first cases show the clearance share growing along the sink (C014, OR 0.1, Re_ch 40: 0.23 at the
leading edge, 0.54 at mid-length, 0.62 at the trailing edge), so the closure's Phi_bypass is the
leading-edge value as defined in Eq. (phibypass) and the migration is reported separately.

## Campaign split across two machines (4 September 2026, 18:15)

The operator made a second Linux machine (about 40 cores, OpenFOAM v2406) available. The 98 cases not yet
started at 18:15 were split: the 11 remaining FC-40 calibration cases (C080 to C090) stay on the
workstation (`run_list_local.txt`), the 87 others (batch 2: C091 to C099, E031 to E033, L005, L010, L015,
L020, L025, G001, G002; and E001 to E030, the remaining L, X and F cases) go to the second machine
(`run_list_remote.txt`). The remote share runs from a public repository
(git@github.com:azan84/IJHMT_CFP.git, directory `unit_cell_campaign/`) that carries the audited builder
and design, a checksum manifest of every dictionary of the 177 locally built cases (a remote build that
differs is refused), the watchdog, continuation and zone-extraction scripts as corrected on the first day,
and an orchestrator (`remote_run.py`) that detects the machine's resources, asks for the core count, runs
8 ranks per case and pushes each finished case's monitors, logs and zone extraction back as
`results/<case>.tar.gz`. The package was tested end to end on the workstation (case C091, 60 iterations)
and audited by Gemini 3.7 Flash at the operator's instruction (`audit/remote_setup_audit_gemini_*.md`)
before upload. Results are imported with `import_remote_results.py`; the local continuation pass and the
ledger post-processing run after the import. Solver, mesh, boundary conditions and acceptance rules are
identical on both machines by construction (same builder, verified by the manifest); the only difference
is the host name recorded in each case's DONE file.

Addendum (18:45): the remote package was audited by Gemini 3.7 Flash through the Antigravity CLI
(`agy --model gemini-3.7-flash-high`) on an isolated copy: round 1 FAIL
(`audit/remote_setup_audit_gemini_round1.md`; five blocking items: result push run from the wrong
directory with errors ignored, numpy undeclared, OpenFOAM path hard-coded in two scripts, a rank count
other than 8 breaking the decomposition, a stale convergence marker surviving a continuation; six
non-blocking), all fixed, and the same marker fix applied to the local `continue_cases.sh`; round 2
PASS with no findings (`audit/remote_setup_audit_gemini_round2.md`). The package was pushed as commit
30659ea to the public repository (main); a sparse clone for importing results is kept at
`cfd/IJHMT_CFP_clone/`.

Addendum (4 September 2026, 22:50): the local share (90 cases) finished at 21:09 after the continuation
pass (12 cases continued; 8 reached the residual stop, C012, C022 and C023 reached 12,000 with h residuals
of 1.9e-6, 1.0e-5 and 1.7e-6 against the 1e-6 acceptance target and monitors stationary to 4e-4 or better).
Of the 90 cases 34 lie inside the wall bound and 29 are accepted; every case at OR >= 0.6 lies outside it
at every Reynolds level, because the flow is set by the channel Reynolds label and the clearance takes
most of it, which is the starvation the framework describes. Five in-envelope cases short of the criteria
(C012, C022, C023, C034 on the energy residual; C042 on the energy closure, 0.503 % against 0.5 %) were
continued a third time to 20,000 iterations rather than relaxing the criteria.

Addendum (4 September 2026, 23:50): the first remote start refused to run because 35 freshly built cases
differed from the manifest: numpy.polyfit rounds the EFL-1 property fit differently on the other machine,
so the inlet velocity in case_meta.json of the EFL-1 cases differed in the last bits. The fit is now the
closed-form Lagrange quadratic in plain floating-point arithmetic (identical on every machine; values
unchanged beyond 1e-14 relative), the 35 local EFL-1 cases (none run locally) were rebuilt with it, the
manifest regenerated, and the verification treats floating-point text agreeing within 1e-9 relative as
equivalent. Pushed to the repository (main).

## Nusselt number from streamwise bins (5 September 2026, 00:40)

Observation on the calibration fit: with the edge-based mean (11:58 addendum) the sealed cases gave
Nu = 2.6 at Re_ch = 2 rising to 13.4 at Re_ch = 250, below the fully developed asymptote (7.85) at the
low end, and the composite Graetz form of Eq. (24), which cannot fall below its asymptote, fitted with
C2 = 3.0 +- 3.7 and an R_th network error of 47 % MAPE. The cause is the definition, not the flow: at
high NTU the fluid approaches the wall temperature within the first fifth of the sink, so a single
mean wall-to-bulk difference formed from end-point temperatures does not measure the film resistance.

Decision: the extraction (`posthoc_zone_T.py`, version 2, run through the solver's -postProcess mode
so that the wall heat flux is recomputed from the fields) now reads six streamwise stations
(x = i L/5: mass-flux-weighted channel and clearance temperatures and fluxes) and five interface bins
(area, bin-mean interface temperature, integrated wall heat flux; the edges lie on mesh faces of all
three grids). The ledger's Nu is the length-averaged coefficient h_m = q''_mean / dT_mean with
q''_mean = sum Q_i / sum A_i and dT_mean the area-weighted mean of (bin-mean interface temperature
minus the mean channel bulk temperature at the bin ends); the local values Nu_B0 to Nu_B4 and the
clearance share at the six stations Phi_X0 to Phi_X5 are kept as columns, and the earlier forms as
Nu_edge, Nu_cell and Nu_lmtd. Check on the sealed cases: the local Nu decays from about 12 at the
entrance to 7.8 in the last fifth at Re_ch = 40 and reaches 8.0 in the last fifth at Re_ch = 2, i.e.
the Shah-London asymptote is recovered where the flow is developed. Bin heat fluxes sum to the applied
2.998 W per half-pitch cell. All finished cases were re-extracted; the remote runner refreshes any
case extracted with version 1 at its next start and after its list.

## Resistance network of Eq. (rth_sum) as fitted (5 September 2026, 01:30)

Three corrections to the fitting script (`figures/src/refit_closures.py`), each forced by the data and
each traceable in the temperature budget of the accepted cases (base maximum minus inlet = base drop
0.35 to 0.44 K, interface maximum minus interface mean 5 to 19 K, mean wall-to-bulk difference 1.3 to
4.1 K, channel bulk rise 0.24 to 40 K):
1. The script had omitted the caloric term of Eq. (rth_sum); it is now included.
2. The fin efficiency used half the fin height; the fin is a straight fin of height H_fin with its
   root at the base and a free tip, so mL = sqrt(2h/(k t)) H_fin (eta_fin 0.25 instead of 0.49 at
   Re_ch = 250), which is what the interface span of the data requires.
3. The channel loses mass to the clearance along the sink (Phi rises from 0.23 at the leading edge
   to 0.62 at the trailing edge at OR 0.1, Re_ch 40; to 0.97 at OR 0.3), so the bulk rise follows
   the integral of dx/(m_ch(x) c_p), which exceeds P/(m_active,leading-edge c_p) by up to a factor of
   six. The ledger carries an effective bypass fraction Phi_eff = 1 - 1/<1/(1 - Phi(x))> (trapezoidal
   mean over the six stations); the same functional form as Eq. (23) is fitted to it (C1_eff, m_eff,
   n_eff) and the caloric term uses it. The leading-edge fit remains the framework's Phi_bypass.
Result on the 34 accepted calibration cases: Phi MAE 0.65 pp, Phi_eff MAE 2.0 pp, Nu MAPE 3.6 %,
R_th MAPE 4.5 % (RMSE 0.0048 K/W, maximum 0.026 K/W, R^2 0.91), R_fixed 0.0078 K/W against R_TIM =
0.006 K/W. Before corrections 2 and 3 the R_th error was 31 % (R^2 0.45). `audit/refit_stats.csv`.

## Manuscript updated with the calibration results (5 September 2026, 01:00 to 02:30)

Sections 6 (campaign, acceptance, bypass split and its growth along the sink, thermal development,
temperature budget, pressure drop), 7 (partitions as designed, fitting as performed, coefficients
and statistics), 5.3 (sealed-channel verification, closure results, grid study pending), 3.4 (fin
efficiency stated; effective fraction), 8 (attribution, design guidance from the feasibility map,
limitations) and 9, the abstract and the highlights were rewritten from the local share of the
campaign (90 of 177 cases; all 99 FC-40 calibration cases except the nine at OR = 1, which run on the
second machine and lie outside the envelope by the same mechanism as OR 0.6 to 0.9). Every number
traces to `dataset_ledger_unitcell.csv`, `audit/refit_stats.csv`, `audit/campaign_results_summary.md`,
`audit/sealed_dp_check.csv` or `audit/feasibility_map.csv` (ledger `audit/provenance.csv`, 1283
tokens, 0 untraced; the pre-results ledger is kept as `audit/provenance_before_campaign_results.csv`).
The withheld-coolant, withheld-load, cross-combination, grid-study and fixed-fin results are marked
MISSING in this build and enter through the generated tables when the remote share is imported.
Two table references (tab:grid, tab:fixed_fin) are undefined until then. Values corrected while
tracing: f_D Re 93.0 (not 92.9), margin to the boiling bound 92 K (not 90), median iteration count
5330 (5329.5), caloric-term span 180 (not 170), caloric-term error at OR >= 0.3 from -16 to +75 %
(not 10 to 75 %).

Addendum (5 September 2026, 03:30): results audit round 1 (Sonnet, `audit/results_audit_round1_FAIL.md`)
FAIL on four blocking items, all accepted: (1) the "at cap" column of the counts table counted every case
with 4000 or more iterations; the ledger now carries `stop_type` (converged, envelope, cap, diverged) and
the table counts envelope stops, unconverged cap stops and diverged cases separately; (2) the calibration
partition itself was incomplete (93 of 99 finished; six OR = 1 cases still on the second machine) without
disclosure; the abstract, Sections 6.4, 7.2 and 9 now say so, and the OR >= 0.6 statement is limited to the
finished cases; (3) the "as performed" paragraph omitted the third pass to 20,000 iterations for five
cases; stated; (4) six provenance tokens matched the empty-duct design file by coincidence (the design
rule ran before the campaign lookup and its context guard was loose); the rule is now restricted to
contexts about the empty-duct campaign and the campaign lookup runs first. Non-blocking items taken:
the rejected cases' energy balances stated as 0.26 to 148 % (median 5.4 %) instead of "reach 10 %"; the
overall surface efficiency range (0.27 to 0.60) given with the attribution statement; the abstract's
list of pending sets includes the cross-combinations.

## Divergence of the hottest corner (5 September 2026, 01:20)

The second machine reported C095 (OR = 1, Re_ch = 40) aborted by a floating-point exception at
iteration 16; the case was reproduced on the workstation from the same rebuilt files
(scratchpad copy, 60-iteration run): the solid temperature reaches 622 K in the first iteration
(the base alone, 4.5 mm of copper under 42.4 kW/m2, coupled to a still-cold fluid through the floor
only), the near-wall fluid enthalpy leaves the property table, and the enthalpy-to-temperature
inversion fails at iteration 14. The lower Reynolds levels at OR = 1 (C091 to C094) survived the
initial transient and ran to their envelope stops; the same mechanism produced the exit code of
C075, C083 and C086 (OR 0.8 and 0.9) on the workstation, whose interface temperatures ran to
3000 to 5500 K before the abort. Every one of these cases lies far outside the 70 C wall bound
(a bare 140 x 118 mm plate under 700 W in this flow has a film coefficient of order 100 W/m2 K),
so none can enter the dataset whatever its exit status. Decision: no solver-control change for
these cases (a per-case relaxation or a ramped load would make the campaign non-uniform for no
gain in the dataset); they are reported as diverged in the counts table and in Section 6.4, and
the statement that every finished case at OR >= 0.6 lies outside the envelope is qualified as
"stopped hot or diverged".

Addendum (5 September 2026, 04:10): results audit round 2 (`audit/results_audit_round2_FAIL.md`) cleared
all round-1 items and found one new blocking error in the corrected paragraph: the finished OR = 1
cases were three (C091 to C093, Re_ch 2, 5 and 10), not the two named; corrected. Non-blocking: the
third-pass sentence now distinguishes the four cases short on the energy residual from C042, short on
the energy closure by 0.003 points after a residual stop at 8490 iterations. The counts and ranges of
the rejected cases drift as the second machine's results are imported; the final build regenerates
every table, summary and count from the complete ledger and is audited again then.

## Campaign paused on the workstation (5 September 2026, 07:30)

The operator stopped the simulations on the workstation to prioritise another project. State at the
stop: the local share (90 cases) is complete and post-processed; the workstation had additionally run
about 30 cases of the shared remote list in reverse order (X001 to X014, F001 to F004, L014 to L024 and
neighbours) through `cfd/IJHMT_CFP_runner`, all pushed to the repository; the second machine had run
C091 to C099, E031 to E033, L005 to L025, G001, G002 and E001 onward, of which the results after L015
were still unpushed on that machine because of a git state its runner version could not repair (the
launcher in the repository now repairs the clone by itself and updates itself; commit 5318644). The
manuscript build of this date carries the calibration results; holdouts, grid study and fixed-fin
entries are MISSING until the remaining results are imported. Resume: on the workstation
`cd cfd/IJHMT_CFP_runner/unit_cell_campaign && python3 remote_run.py --reverse --cores 24` and
`cd cfd/unit_cell_campaign && CL=/mnt/e/ijhmt-cfp/Paper-5/cfd/IJHMT_CFP_clone bash auto_sync.sh` (import loop);
on the second machine `python3 run_remote_share.py --cores 16` with the launcher of commit 5318644 or later;
then post-process, refit, regenerate tables and figures, remove the MISSING entries, and run the
results audit round 3, the consistency sweep and the final audit.

Addendum (5 September 2026, 13:05): before the launcher is copied to the second machine, Gemini 3.7 Flash
audited the package again (round 3, `audit/remote_setup_audit_gemini_round3.md`, FAIL): a `--test` run
modified the first case's controlDict, so the next production start failed the manifest check and refused
to run; OPENFOAM_BASHRC was not consulted; the results directory could be missing at the first push; a
version-1 extraction newer than DONE was never refreshed by the post-processing; documentation gaps. All
fixed (commit 64b1d72): the test now runs on a copy under cases_test/ and packs into results_test/, the
manifest treats writeInterval as volatile and was regenerated, and the production start after two test
runs was verified in a sandbox (build, manifest check, first case start). Round 4 launched on the
corrected package. The launcher itself (`run_remote_share.py`) repairs the clone, pushes stranded results
and updates itself from the repository; verified on a reproduced copy of the second machine's state.

Addendum (5 September 2026, 14:10): round 4 of the Gemini 3.7 Flash audit PASS
(`audit/remote_setup_audit_gemini_round4.md`); its two non-blocking items were taken (the runner's repair
removes a stale index.lock; where both machines solve the same case, the result that reached the repository
first stays and the second is kept locally under results_duplicate/). The launcher and package are cleared
for the second machine.

Addendum (5 September 2026, 20:20): the four cases the workstation pushed at the pause (L011, L013, L014,
L017) were imported and the ledger regenerated (133 rows; all 99 calibration cases finished, 34 accepted;
three cross-combination cases inside the envelope await their continuation pass). The analysis outputs,
the audit trail, the 90 workstation case results (monitors, logs, extraction; fields excluded) and a
checksum manifest were pushed to the public repository under `analysis/` and
`unit_cell_campaign/results_local/` (commits 6d5b23b and after). The manuscript build of 02:30 states 93
finished calibration cases; the next build regenerates every count from the complete ledger.

Addendum (5 September 2026, 20:50): a byte-level comparison of every result tarball in the repository with the
local case directories (all 133 present) showed that the workstation's post-processing had re-run the
version-2 zone extraction on two imported cases (C091, C092: monitors only, no fields on this machine),
overwriting their extraction with values from the initial fields. `post_campaign.py` now runs the
extraction only when a written time directory with fluid fields exists locally; the two cases were restored
from their tarballs and the ledger regenerated (their Nu is undefined at OR = 1 in any case, and both are
outside the envelope). Pushed with the corrected ledger and summary.

Addendum (5 September 2026, 21:30): the repository completeness check by Gemini 3.7 Flash
(`audit/upload_check_gemini.md`, INCOMPLETE) found, beyond the two re-extracted cases already fixed: the
same contamination on X010 (imported, diverged on the shared list, no fields here), now cleaned to its
tarball state for every imported case; the vector PDFs of the figures excluded by the repository's old
`*.pdf` rule (now un-ignored for `analysis/figures/`); the unit-cell figure script missing from
`analysis/scripts/`; the decision log copied before its last addendum (it is copied last from now on); and
the design script blocked by the fixed-fin sealed case at Re 40 and by the off-grid Reynolds numbers of the
cross-combination cases (it now takes its sealed reference from the calibration partition and drops rows
without one, with a note; 13 feasible rows). Non-blocking: the scripts' project-relative paths are
documented in `analysis/README.md`.

Addendum (5 September 2026, 22:30): round 2 of the repository completeness check by Gemini 3.7 Flash
(`audit/upload_check_gemini_round2.md`): COMPLETE; every finished case's results and every analysis file are in
the public repository, byte-identical to the local originals (also confirmed by an independent comparison of all
7541 checksummed case files). The two remarks (script paths documented; the manifest listing its own hash) were
taken: the manifest now excludes itself.
