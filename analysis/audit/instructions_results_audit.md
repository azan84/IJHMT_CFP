# Audit instructions: campaign results in the manuscript (round 3, results audit, round 1)

You are the adversarial auditor (Claude, Sonnet, by the operator's instruction) of the results that were written
into the manuscript from the unit-cell calibration campaign. Repository root: /mnt/e/ijhmt-cfp/Paper-5. You have no
knowledge of how the text was produced; verify every number and claim against the raw files. READ-ONLY: create,
modify or delete nothing under the repository; temporary files go under the scratchpad directory you are given.
Do not run any solver.

Text under audit (the promoted copy, `manuscript/`): the abstract and highlights in `main.tex`;
`sections/dimensionless_framework.tex` (fin efficiency, references to Table tab:coefficients, Phi_eff);
`sections/verification_validation.tex` (grid convergence paragraph, subsection "Sealed-channel pressure drop against
the fully developed solution", closure paragraph); `sections/parametric_results.tex` (all); `sections/correlation_and_holdout.tex`
(all); `sections/discussion.tex` (all); `sections/conclusions.tex` (all); `sections/numerical_method.tex` paragraph
"Calibration campaign as performed"; the generated tables `manuscript/tables/*.tex`; figures `figures/fig_phi_bypass.png`,
`fig_profiles.png`, `fig_rth_or.png`, `fig_dp_pump.png`, `fig_parity.png`; `supplementary/S1_ledgers.tex` section S1.4.

Sources of record: `cfd/unit_cell_campaign/dataset_ledger_unitcell.csv` (written by `post_campaign.py`; one row per
finished case; read the column meanings in the script's docstring), `audit/refit_stats.csv` (written by
`figures/src/refit_closures.py`), `audit/campaign_results_summary.md` (written by `audit/src/campaign_results_summary.py`),
`audit/sealed_dp_check.csv` (`audit/src/sealed_dp_check.py`), `audit/feasibility_map.csv` and `audit/optimum.csv`
(`figures/src/solve_eq22.py`), `audit/decisions.md` (sections dated 4 and 5 September 2026), `audit/provenance.csv`
(the provenance ledger of every numeric token of the manuscript), `cfd/unit_cell_campaign/campaign_design.json`,
the case directories `cfd/unit_cell_campaign/cases/<id>/` (monitors under postProcessing/, `posthoc_zoneT.json`,
`DONE`, `CONVERGED_STOP`, `ENVELOPE_STOP`, `case_meta.json`, `log.chtMultiRegionSimpleFoam`).

## Part A: numbers
1. Every number in the text under audit that is a campaign result must agree with its source to the printed
   precision. Recompute, do not trust the summary: pick at least twelve numbers across the sections (counts,
   fractions, temperatures, Nu values, resistances, pressure drops, pumping powers, fit coefficients, error
   statistics, feasibility statements) and recompute them from the ledger or the case monitors yourself; list every
   disagreement with file and line.
2. Recompute the fit independently: with `dataset_ledger_unitcell.csv`, fit Eq. (23) (phi_field against OR and
   Re_recomputed_ch_Eq1_140mm, the model in `refit_closures.py`) on the accepted calibration rows with scipy and
   compare with `refit_stats.csv`; do the same for Eq. (24) with Nu_field, Nu_fd = 7.85, Gz from Re (1 - Phi_pred) Pr D_h/L;
   then evaluate the resistance network of Eq. (rth_sum) as the manuscript states it (Section 7.2 and Eq. (eta_o),
   eta_fin = tanh(mH)/(mH), m = sqrt(2h/(k t)), k_fin = 387.6, R_fixed as the mean residual, caloric term with the
   effective fraction fit) and compare the MAPE, RMSE, maximum error and R^2 with the text.
3. Check that the three script corrections recorded in `audit/decisions.md` (section "Resistance network of Eq.
   (rth_sum) as fitted") are what the script now does, and that the manuscript reports them.
4. Check the acceptance counts of Table tab:campaign_counts against the ledger (and the design for the total), and
   the acceptance map statements (which OR/Re levels are accepted, envelope-stopped, diverged).

## Part B: definitions and claims
5. The Nusselt-number definition in Section 7.2 must be what `post_campaign.py` computes from `posthoc_zoneT.json`
   (version 2: five bins, six stations); the bypass fraction at the leading edge must be Eq. (phibypass) on the
   chanIn/clearIn face zones; Phi_eff as stated. Recompute Nu, Nu_B0, Nu_B4 and Phi_eff for two accepted cases
   from their `posthoc_zoneT.json` and compare with the ledger.
6. Every claim of causation or mechanism in Sections 6, 8 and 9 (why the split falls with Re, why the caloric term
   overpredicts at OR >= 0.3, why the convective term varies little, the starvation statement) must be either
   supported by a number in the text or marked as an interpretation; flag any claim that the data do not support.
7. Statements about what is MISSING or pending (holdouts, grid study, fixed-fin sweep, EFL-1) must be consistent
   across the abstract, Sections 5.3, 6.9, 7.1, 7.3, 8.2, 8.3, 9 and the table captions.
8. Wording rules: English, neutral register, past tense for what was done, no em dashes, none of the words
   genuinely, honestly, robust, rigorous, seamlessly, comprehensive, novel; no number in the text without a source in
   `audit/provenance.csv` (spot-check ten tokens of the new sections in the ledger and confirm the stated source
   holds the value).

## Part C: figures and tables
9. Each figure's data must be the ledger's accepted rows (and the crosses the rejected rows); captions must say what
   is plotted; the parity figure's dotted lines must be +-20 %. Check `figures/src/fig_campaign.py`.
10. `manuscript/tables/tab_statistics.tex` subgroup rows must be reproducible from the ledger with the coefficients
    of `tab_coefficients.tex`; `tab_calibration_ledger.tex` (S1.4) must list every calibration case of the ledger.

## Verdict
End your reply with exactly this block:
```
BLOCKING (a wrong number, an unsupported claim, a definition that does not match the code, or a rule violation): numbered list or "none"
NON-BLOCKING: numbered list or "none"
NOT VERIFIABLE: numbered list or "none"
VERDICT: PASS | FAIL
```

## Round 2 (after the round-1 FAIL)
Round 1 (`audit/results_audit_round1_FAIL.md`) found four blocking and four non-blocking items. Re-check each
against the current files: (1) `manuscript/tables/tab_campaign_counts.tex` now has separate columns for
envelope stops, unconverged cap stops and diverged cases from the ledger's new `stop_type` column
(`post_campaign.py`); confirm the counts from the ledger and that Section 6.4's text describes the columns.
(2) The abstract, Sections 6.4, 7.2 and 9 now disclose that 93 of the 99 calibration cases had finished and
that the OR >= 0.6 statement covers the finished cases; confirm against the ledger (note: the count may have
advanced since, because the second machine keeps importing; a count that was true at the ledger's timestamp
is not a finding, an undisclosed incompleteness is). (3) The "as performed" paragraph of `numerical_method.tex`
now states the third pass to 20,000 iterations; confirm against `audit/decisions.md` and the DONE files of
C012, C022, C023, C034, C042. (4) `audit/provenance.csv` was regenerated: confirm that no campaign-result token
is traced to `parametric_campaign/doe_definition.json` (list the tokens that still are and judge whether they
describe the empty-duct campaign). Non-blocking: the energy-balance range of rejected cases
(`verification_validation.tex`), the surface-efficiency numbers (`discussion.tex`), the abstract's list of
pending sets. Then read the changed paragraphs once more for wording rules. Give the verdict block.
