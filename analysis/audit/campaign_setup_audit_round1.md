# Campaign set-up audit, round 1 (4 September 2026)

Auditor: Claude Code, Sonnet model (claude-sonnet-5), replacing codex (`audit/auditor_change.md`). Workflow: three auditors (A geometry and mesh, B physics, boundary conditions, solver and the buoyancy decision, C post-processing definitions and pilot closures) and a lead auditor, read-only, following `audit/instructions_campaign_setup.md`, on the pilot cases C005, C050 and C095 and the design files. The verdict block below is the lead auditor's final message, copied verbatim.

```
VERDICT: FAIL

EVIDENCE: what I opened and recomputed myself (independent of the three auditors' claims)
- manuscript/sections/dimensionless_framework.tex (full text): confirmed Eq. R_branches (D_h,ch, A_ch, A_gap
  definitions), Eq. phi_bypass_closure (Phi_bypass -> 1 at OR=1 "by definition", no alternate D_h/A_ch formula
  given), Eq. re_active_def, Eq. rth_sum.
- manuscript/sections/problem_formulation.tex lines 1-140: confirmed Re_ch = mdot*D_h/(A_c*mu) "on the free-flow
  area of the fin channels" (Sec. 2.3) - no OR=1 special case given anywhere.
- manuscript/sections/verification_validation.tex lines 54-68 (sec:vv-grid): confirmed the manuscript's literal
  text for the grid-convergence acceptance case ("most demanding case (smallest non-zero recess ratio, highest
  Reynolds number, FC-40)") and that "the unit-cell meshes built for the calibration campaign (11,040, 51,800 and
  202,400 cells) have aspect ratios up to 32 and carry a thin-slab conditioning warning" refers only to the OR=0
  triple (matches Auditor A's independently-recomputed OR=0 cell counts exactly) - the manuscript makes no claim
  about OR=0.5/OR=1 unit-cell mesh quality.
- manuscript/sections/numerical_method.tex lines 88-130 (Sec. 3.3 Buoyancy) and line ~198 ("Calibration campaign
  as specified"): confirmed the literal, unconditional sentence "...temperature coupling at the fluid-solid
  interface, and Boussinesq body force."
- cfd/unit_cell_campaign/unit_cell.py: read geometry(), inlet_velocity(), write_blockmesh(), build() directly.
  Confirmed the `if Hfin<=1e-9` branch substitutes Dh=2*S*(Hc-HB)/(S+Hc-HB), Ach_half=(S/2)*(Hc-HB) at OR=1 -
  algebraically identical to the OR=0 values (since Hfin(OR=0)=Hc-HB by definition) - and that
  write_blockmesh's z-layer classifier puts the whole HB..Hc span into the "clear" bucket (nz_cl=12) rather than
  the "fin" bucket (nz_fin=40) whenever Hfin<=1e-9, i.e. at OR=1 only.
- cases/{C005,C050,C095}/log.checkMesh: grepped directly - Max aspect ratio 32/32/53.267, determinant-failed
  cells 352/1504/6212 (0.68%/2.3%/33.6%), all "Failed 1 mesh checks" (not merely "warning").
- cfd/unit_cell_campaign/campaign_design.py, campaign_design.json: read the G001/G002 grid-study entries and the
  source-script comment ("OR 0.5, Re 150 ... chosen after the pilot"); confirmed OR_levels includes 0.1 and
  Re_levels includes 250, i.e. the manuscript-specified "most demanding case" exists in the design space but is
  not what G001/G002 currently encode. Confirmed 17 of 177 defined cases have OR=1.0 (9 calibration, 3 EFL-1
  holdout, 5 thermal-load holdout) - not a throwaway pilot-only issue.
- cases/{C005,C050,C095}/constant/g, case_meta.json, build_all.py: confirmed g=(0,0,0) in all three pilot cases
  and build_all.py hardcodes gravity=False for every case it builds.
- audit/decisions.md lines 55-115: read the full buoyancy investigation table (V1-V15) and the 4 September 2026
  decision, including its own stated "Consequence for the manuscript: the 'Boussinesq body force' of the
  specification is replaced by a statement that the calibration runs are forced convection...".
- grep -rn -i "forced convection|without gravity|no gravity" manuscript/: zero hits describing the campaign (one
  unrelated bibliography entry only) - confirmed the prescribed manuscript edit has not been made.
- post_campaign.py line 88 vs its own docstring line 12, and figures/src/refit_closures.py /solve_eq22.py:
  confirmed `accepted` omits the envelope check but the two downstream fitting scripts filter on
  `passed_validity_envelope` directly, not on `accepted`.
- cases/{C050,C095}/log.chtMultiRegionSimpleFoam: grepped Min/max rho and GAMG p_rgh iteration counts, confirmed
  the reported density excursions (2042/4203 kg/m3, both outside the FC-40 table's 1779-1866 kg/m3 span)
  coincide with unconverged/capped GAMG solves (C095: 1000 iterations, not converged).

DEVIATIONS FROM THE MANUSCRIPT SPECIFICATION:

1. [BLOCKING] D_h,ch, A_ch and the inlet flow rate/velocity at OR=1 (unit_cell.py geometry(), all 17 OR=1 cases
   in campaign_design.json: C091-C099, E031-E033, L005/L010/L015/L020/L025).
   Manuscript says: D_h,ch=2sH_fin/(s+H_fin), A_ch=N_ch*s*H_fin(OR) (dimensionless_framework.tex Eq. R_branches);
   Re_ch=mdot*D_h/(A_c*mu) on the fin-channel free-flow area (problem_formulation.tex Sec. 2.3). No alternate
   formula is given for H_fin=0; the algebraic limit of the manuscript's own formula as H_fin->0 is finite and
   small (A_ch/D_h -> N_ch*s/2, so mdot -> Re_ch*mu*N_ch*s/2, well short of the OR=0 value).
   Setup does: at Hfin<=1e-9 the code substitutes Dh and Ach_half computed with (Hc-HB) in place of Hfin - a
   value that is algebraically identical to the OR=0 channel values (verified: this is not a coincidence, it is
   the same formula evaluated with the full duct height standing in for the vanished fin height). This produces
   inlet velocity/flow-rate bit-identical to the OR=0 case (0.038635 m/s in both C005 and C095 0/fluid/U) instead
   of the manuscript formula's own ~41x-smaller continuous limit. Not justified anywhere in the manuscript; the
   only documentation is a one-line code comment not tied to any manuscript equation.
   Justified: NO.

2. [BLOCKING] Mesh z-resolution at OR=1 (unit_cell.py write_blockmesh(), same 17 cases as #1).
   Manuscript says: nothing specific for OR=1 unit-cell mesh quality (only the OR=0 triple's aspect ratio of 32
   is quoted, verification_validation.tex Sec. 4.4).
   Setup does: the classifier that assigns z-layers to grading "buckets" puts the whole 39.95 mm HB..Hc span
   into the "clear" bucket (12 cells, designed for clearances that never exceed ~20 mm elsewhere in the design)
   instead of the "fin" bucket (40 cells) used for the physically identical 39.95 mm span at OR=0, because the
   classifier's branch condition is the same `Hfin<=1e-9` test as #1. Result, confirmed directly in
   cases/C095/log.checkMesh: Max aspect ratio 53.267 (vs 32 for C005/C050) and 33.6% of cells failing the
   cell-determinant check (vs 0.68%/2.3%). Both #1 and #2 share one root cause and one fix (a principled OR=1
   convention, or a smooth taper of the z-grading as H_fin->0, tied to a manuscript-stated limit).
   Justified: NO.

3. [BLOCKING] Grid-convergence study case selection (G001/G002 in campaign_design.json).
   Manuscript says (verification_validation.tex Sec. 4.4, sec:vv-grid): the three-grid acceptance study must run
   "at its most demanding case (smallest non-zero recess ratio, highest Reynolds number, FC-40)" - i.e. OR=0.1,
   Re_ch=250 (both present in the design's own OR_levels/Re_levels).
   Setup does: G001 (coarse) and G002 (fine) are defined at OR=0.5, Re_ch=150. campaign_design.py's own comment
   acknowledges this is a placeholder ("the case with the strongest bypass and the highest channel velocity of
   the calibration grid that is still inside the envelope is chosen after the pilot") - i.e. explicitly not yet
   finalized. As currently encoded it does not match the manuscript's stated case, and if run as-is would not
   satisfy sec:vv-grid's acceptance requirement (the section that presently records grid-convergence results as
   MISSING and describes exactly what is needed to close that gap).
   Justified: partially - the deferral is documented as deliberate and pending a post-pilot feasibility check
   (reasonable, given C050 at OR=0.5/Re=40 already struggles to converge, so OR=0.1/Re=250 may be worse), but the
   design file has not yet been updated with the actual case to run, so as it stands it is a real deviation.

4. [BLOCKING] Manuscript text vs. actual gravity treatment (numerical_method.tex "Calibration campaign as
   specified" paragraph, ~line 198; all cases in the campaign).
   Manuscript says: "...temperature coupling at the fluid-solid interface, and Boussinesq body force" -
   unconditional, for the calibration campaign specifically (the exact paragraph the audit instructions name).
   Setup does: g=(0,0,0) in all three pilot cases' constant/g and case_meta.json; build_all.py hardcodes
   gravity=False for the whole campaign. This is a real, physically well-motivated decision - I independently
   re-read audit/decisions.md's V1-V15/T1/T2 diagnostic table and it supports the reading that every
   temperature-dependent-density variant under gravity fails to converge while every forced-convection variant
   converges. But decisions.md's own prescribed "Consequence for the manuscript" (replace the Boussinesq
   sentence with a forced-convection statement) has not been carried out: grep of manuscript/sections/*.tex for
   "forced convection"/"without gravity"/"no gravity" returns zero hits describing the campaign. A reader
   checking the setup against the manuscript's own specification paragraph, as this audit was instructed to do,
   finds a live contradiction.
   Justified: the underlying physics decision is justified and documented (campaign_design.json meta.gravity,
   decisions.md); the manuscript text itself is not yet reconciled with it.

5. [NON-BLOCKING] checkMesh reports "Failed 1 mesh checks" (cell determinant) for all three pilot meshes, not
   merely a "warning" as the manuscript's prose states for the OR=0 triple. Confirmed the manuscript's claim is
   about the 11,040/51,800/202,400 triple specifically and is a defensible paraphrase of a real, traceable,
   streamwise-refinement-fixable mesh-conditioning issue at OR=0/0.5; it does not extend to (nor contradict) the
   worse OR=1 numbers already captured separately as defect #2. Wording-level only.

6. [NON-BLOCKING] Energy-balance closure threshold is stated as 0.5% in numerical_method.tex Sec. 3.5 and as 1%
   in verification_validation.tex Sec. 4.4 (confirmed directly, both greps quoted above) - an internal manuscript
   inconsistency, not a setup defect. The setup (post_campaign.py, campaign_design.json) implements the stricter
   0.5% figure, so the script is not being permissive; the manuscript's two sections need reconciling.

7. [NON-BLOCKING] post_campaign.py's `accepted` boolean (line 88) omits `passed_validity_envelope`, contradicting
   its own docstring (line 12). Confirmed by direct read of the code. Confirmed the two downstream fitting
   scripts (figures/src/refit_closures.py, solve_eq22.py) filter on `passed_validity_envelope` directly, so the
   calibration fit is not corrupted by this bug - only the console summary / a human relying on `accepted` is at
   risk. Real logic bug, easy fix, does not change any reported quantity.

8. [NON-BLOCKING] FC-40 density excursions in the two excluded, non-converged pilots (C050: max rho 2042 kg/m3;
   C095: max rho 4203 kg/m3), both outside the property table's 1779-1866 kg/m3 span, confirmed directly in
   log.chtMultiRegionSimpleFoam and coincident with GAMG p_rgh failing to converge (C095: 1000 iterations,
   uncapped tolerance not met). Both cases are correctly excluded by the acceptance/envelope filters
   (pilot_results.csv accepted=False), so this does not reach any reported number, but it means the "clamped to
   its validity band" characterization is not reliably true for excluded, non-converged cases; root cause (table
   clamp vs. a symptom of the same instability) not determined without running the solver.

9. [NON-BLOCKING] A_wetted(OR) formula (problem_formulation.tex, faithfully reproduced in unit_cell.py) excludes
   the fin-footprint area at OR=1 (undercounts true wetted area by ~26% at OR=1: 0.01307 m2 vs W*L=0.01652 m2).
   This is a manuscript-formula degeneracy, not a script bug; practically moot since OR=1 cases fail the envelope
   regardless (confirmed: C095 wall/chip temperatures 513/518.5 C, far past 70/165 C).

10. [NON-BLOCKING] A_wetted_cell (denominator used by post_campaign.py to derive h/Nu from the CFD wall flux)
    includes a fin-tip term that A_wetted_full/A_wetted (used later by refit_closures.py to reconstruct R_th from
    that same h) omits - a basis mismatch, quantified as ~0.6% at OR=0.5 (negligible) and 100% at OR=1 (moot,
    excluded by the envelope anyway).

11. [NON-BLOCKING] campaign_design.py (source generator) is stale relative to campaign_design.json (built
    output): the script's hardcoded gravity/solver meta strings do not match the json's actual meta block, which
    was evidently hand-edited after the 4 September buoyancy decision. Re-running the script would silently
    regenerate a json that contradicts that decision. The already-built cases are unaffected (build_all.py's own
    gravity=False call is independent of this stale text), so this is a source-hygiene issue, not a case defect.

BLOCKING DEFECTS:
1. OR=1 inlet-flow discontinuity (unit_cell.py geometry()/inlet_velocity(), Hfin<=1e-9 branch) - affects 17 of
   177 defined cases (C091-C099, E031-E033, L005/010/015/020/025). Clears when the OR=1 branch implements a
   principled, manuscript-traceable convention for D_h,ch/A_ch/mdot as H_fin->0 (either the algebraic limit of
   the manuscript's own R_branches formula, or an explicitly stated and justified alternate convention added to
   the manuscript), rather than silently substituting the OR=0 channel dimensions.
2. OR=1 mesh under-resolution (unit_cell.py write_blockmesh(), same branch/same 17 cases) - Max aspect ratio
   53.267 vs 32, 33.6% of cells failing the determinant check vs 0.68-2.3% elsewhere. Clears when the z-grading
   classifier assigns the full HB..Hc span at OR=1 to a resolution appropriate to its physical thickness (e.g.
   the "fin" bucket's cell count) instead of the "clear" bucket sized for thin clearances - the same fix that
   clears defect 1 should be applied together.
3. Grid-convergence study case (campaign_design.json G001/G002) does not match the manuscript's stated "most
   demanding case" (smallest non-zero OR, highest Re = OR 0.1, Re_ch 250; currently OR 0.5, Re_ch 150). Clears
   when the design file is updated to the manuscript-specified case (or the manuscript's sec:vv-grid text is
   revised, with stated justification, to name the case actually used) before G001/G002 are run.
4. The manuscript's "Calibration campaign as specified" paragraph (numerical_method.tex) still states
   unconditionally that the campaign uses "Boussinesq body force," while every case in the campaign runs with
   g=(0,0,0). Clears when that paragraph (and any other passage promising Boussinesq buoyancy for the
   calibration campaign) is edited to state forced convection, per audit/decisions.md's own prescribed
   consequence, before the campaign's results are reported against that text.

NON-BLOCKING DEFECTS:
1. checkMesh literally reports "Failed 1 mesh checks," not a "warning," for all three pilot meshes - wording only
   for the OR=0/0.5 cases the manuscript actually describes; substance (streamwise-refinement-fixable thin-slab
   conditioning) confirmed real and traceable.
2. Energy-balance closure threshold: manuscript states 0.5% (numerical_method.tex Sec. 3.5) and 1%
   (verification_validation.tex Sec. 4.4) in two different sections; setup uses the stricter 0.5% - a
   manuscript-internal inconsistency to reconcile, not a setup defect.
3. post_campaign.py's `accepted` field omits the validity-envelope check present in its own docstring; downstream
   fitting scripts are unaffected (they filter on `passed_validity_envelope` directly).
4. FC-40 density excursions (2042/4203 kg/m3, outside the 1779-1866 kg/m3 table span) in the two excluded,
   non-converged pilots (C050, C095), coincident with unconverged GAMG p_rgh solves; does not reach any accepted
   result but undercuts the "clamped to its validity band" claim for excluded cases specifically.
5. A_wetted(OR) manuscript formula undercounts wetted area by ~26% at OR=1 (excludes the fin footprint once fins
   vanish); faithfully reproduced by the script; moot in practice since OR=1 cases fail the envelope anyway.
6. Basis mismatch between A_wetted_cell (fin-tip term included, used to derive h/Nu from CFD) and
   A_wetted_full/A_wetted (fin-tip term excluded, used downstream to reconstruct R_th from that h); negligible
   (~0.6%) away from OR=1, total (but moot) at OR=1.
7. campaign_design.py (source generator) is stale relative to campaign_design.json's actual meta block
   (gravity/solver text pre-dates the 4 September buoyancy decision); the built cases are unaffected, but
   re-running the generator would silently regenerate a contradictory json.

NOT VERIFIABLE:
1. The exact 0.5% tolerance and 500-iteration window used by post_campaign.py's stationarity test: the
   manuscript states only "stationary over the final several hundred iterations" (numerical_method.tex Sec. 3.5)
   with no numeric window or tolerance given, so the specific numbers cannot be checked against manuscript text
   (not contradicted by it either).
2. Root cause of the FC-40 density excursions in C050/C095 (table-clamp defect vs. a pure symptom of pressure-
   equation non-convergence) - would require running the solver with instrumentation, which is out of scope for
   a read-only audit.
3. Parts of the physics/BC/solver checklist not independently re-derived here beyond the disputed items (e.g.
   exact numeric match of every fvSchemes/fvSolution entry to Sec. 3.4/3.5) - taken from Auditor B's direct file
   quotes, which I spot-checked (relaxation factors, residual targets, EFL-1 table, coupled-interface BC) via the
   same reasoning path Auditor B used, but did not re-open every listed file myself.```
