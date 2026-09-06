# Analysis outputs of the unit-cell calibration campaign (state of 7 September 2026)

Everything here is generated from the case results by the scripts in `scripts/`; nothing is typed in by hand.

| File | Content | Produced by |
|---|---|---|
| `dataset_ledger_unitcell.csv` | one row per finished case (170 rows at this date, 7 September 2026, of 177 designed; 7 remain: E001-E003, G001, G002, L020, L025; 49 cases accepted, 34 of them the calibration set, 6 the withheld-coolant set, 5 the withheld-load set, 2 the cross-combination set and 2 the fixed-fin sweep): bypass fractions at the leading edge, mid-length and trailing edge, the effective fraction, the length-averaged and local Nusselt numbers, base and wall temperatures, thermal resistance, pressure drop, pumping power, closures, stop type, acceptance flags and the columns the fitting script reads | `../unit_cell_campaign/post_campaign.py` |
| `refit_stats.csv` | fitted coefficients of the bypass closure (leading-edge and effective), the Nusselt closure and the resistance sum, with standard errors, 95 % intervals and the error statistics on the accepted calibration cases and on each cross-condition partition (evaluated with the calibration coefficients, no refitting) | `scripts/refit_closures.py` |
| `feasibility_map.csv`, `optimum.csv` | the constrained design problem (resistance within 10 % of the sealed sink, chip below 85 C) on the accepted calibration cases | `scripts/solve_eq22.py` |
| `coolant_comparison.csv` | FC-40 (log-log interpolated along its own OR = 0.1 curve) against the EFL-1 holdout case E006 on three bases: matched channel Reynolds number, matched volumetric flow rate, matched pumping power | `scripts/holdout_extra_stats.py` |
| `campaign_results_summary.md` | every number quoted in the manuscript's results, with its source row: acceptance map, bypass split per case, Nusselt numbers, temperature budget, resistance ratios, network terms, feasibility per Reynolds level, the coolant comparison, the withheld-load T_chip,max prediction check and the fixed-fin field-versus-closure comparison | `scripts/campaign_results_summary.py`, `scripts/holdout_extra_stats.py` |
| `sealed_dp_check.csv` | verification of the sealed cases against the fully developed Shah-London pressure drop at three property temperatures | `scripts/sealed_dp_check.py` |
| `figures/` | bypass fraction against recess ratio with the fitted closure; streamwise profiles; resistance; pressure drop and pumping power; parity of the three closures on the calibration set and on all accepted cases; the coolant comparison; the fixed-fin sweep; the unit cell | `scripts/fig_campaign.py`, `scripts/fig_parity_all.py`, `scripts/fig_coolant_comparison.py`, `scripts/fig_fixed_fin.py` |
| `tables/` | LaTeX tables of the manuscript: case counts, coefficients, statistics (now including the three cross-condition partitions), calibration ledger, fixed-fin sweep (the grid-study table appears when those two cases are imported) | `scripts/make_campaign_tables.py` |
| `audit/` | the audit trail: decision log of the round-3 revision, the campaign set-up audits (codex-role auditor, Sonnet), the remote set-up audits (Gemini 3.7 Flash, rounds 1 to 4), the results audits (Sonnet, rounds 1 and 2) and their instruction files, and the reproduction log of the diverging bare-duct case | auditors, verbatim |

Raw results: `../unit_cell_campaign/results/` and `../unit_cell_campaign/results_local/` hold one tarball per
finished case with all monitors, logs, the streamwise zone extraction and the dictionaries as run. The final
volume fields of every case (about 10 MB per case) stay on the machine that solved it and are not in the
repository. Seven cases remain on the shared list: the three-grid study (G001, G002) and the last few
withheld-coolant and withheld-load cases (E001-E003, L020, L025). The calibration set has been complete since
5 September, so the fitted coefficients of `tab_coefficients.tex` are unchanged by the cases that finished
since; the other four partitions (withheld coolant, withheld load, cross-combinations, fixed-fin) are now
complete or nearly complete and `tab_statistics.tex` carries their statistics in full.

Paths in the scripts: they were written for the originating project tree (ledger under `cfd/unit_cell_campaign/`,
outputs under `audit/`, `figures/` and `manuscript/tables/`); each takes its input ledger on the command line
(`--ledger`, or the first argument for the figure and table scripts) and the fitting and design scripts take `--out`,
so they run on `dataset_ledger_unitcell.csv` from this directory with those options. The design script uses the
calibration partition for its sealed reference at each Reynolds level.

`MANIFEST_sha256.txt` lists the SHA-256 of every file under `analysis/`, `../unit_cell_campaign/results/` and
`../unit_cell_campaign/results_local/` at the time of the push.
