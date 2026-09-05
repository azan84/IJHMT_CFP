# Analysis outputs of the unit-cell calibration campaign (state of 5 September 2026)

Everything here is generated from the case results by the scripts in `scripts/`; nothing is typed in by hand.

| File | Content | Produced by |
|---|---|---|
| `dataset_ledger_unitcell.csv` | one row per finished case (133 rows at this date: the 90 workstation cases and the 43 imported from `../unit_cell_campaign/results/`): bypass fractions at the leading edge, mid-length and trailing edge, the effective fraction, the length-averaged and local Nusselt numbers, base and wall temperatures, thermal resistance, pressure drop, pumping power, closures, stop type, acceptance flags and the columns the fitting script reads | `../unit_cell_campaign/post_campaign.py` |
| `refit_stats.csv` | fitted coefficients of the bypass closure (leading-edge and effective), the Nusselt closure and the resistance sum, with standard errors, 95 % intervals and the error statistics on the accepted calibration cases | `scripts/refit_closures.py` |
| `feasibility_map.csv`, `optimum.csv` | the constrained design problem (resistance within 10 % of the sealed sink, chip below 85 C) on the accepted cases | `scripts/solve_eq22.py` |
| `campaign_results_summary.md` | every number quoted in the manuscript's results, with its source row: acceptance map, bypass split per case, Nusselt numbers, temperature budget, resistance ratios, network terms, feasibility per Reynolds level | `scripts/campaign_results_summary.py` |
| `sealed_dp_check.csv` | verification of the sealed cases against the fully developed Shah-London pressure drop at three property temperatures | `scripts/sealed_dp_check.py` |
| `figures/` | bypass fraction against recess ratio with the fitted closure; streamwise profiles; resistance; pressure drop and pumping power; parity of the three closures; the unit cell | `scripts/fig_campaign.py` |
| `tables/` | LaTeX tables of the manuscript: case counts, coefficients, statistics, calibration ledger (grid study and fixed-fin tables appear when those cases are imported) | `scripts/make_campaign_tables.py` |
| `audit/` | the audit trail: decision log of the round-3 revision, the campaign set-up audits (codex-role auditor, Sonnet), the remote set-up audits (Gemini 3.7 Flash, rounds 1 to 4), the results audits (Sonnet, rounds 1 and 2) and their instruction files, and the reproduction log of the diverging bare-duct case | auditors, verbatim |

Raw results: `../unit_cell_campaign/results/` holds the cases solved on the second machine and on the workstation's
share of the common list (one tarball per case with all monitors, logs, the streamwise zone extraction and the
dictionaries as run); `../unit_cell_campaign/results_local/` holds the same for the 90 cases of the workstation's
own share. The final volume fields of every case (about 10 MB per case) stay on the machine that solved it and are
not in the repository. The campaign was paused on 5 September 2026 with 44 cases of the common list still to run;
the holdout, grid-study and fixed-fin statistics are therefore absent from `refit_stats.csv` and the tables.

`MANIFEST_sha256.txt` lists the SHA-256 of every file under `analysis/`, `../unit_cell_campaign/results/` and
`../unit_cell_campaign/results_local/` at the time of the push.
