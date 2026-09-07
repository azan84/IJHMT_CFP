PASS. I independently recomputed the fits, predictions, interpolation, statistics, counts, and case inventory directly from the 170-row ledger. No numerical discrepancy was found.

### 1. Closure refit and statistics

Using the 34 accepted calibration rows, the independent bounded fits gave:

- Eq. (23): \(C_1=0.2365466550,\ m=1.358046564,\ n=0.4439926592\)
- Effective bypass fit: \(C_{1,\mathrm{eff}}=0.0253485440,\ m_{\mathrm{eff}}=1.867968109,\ n_{\mathrm{eff}}=0.4141963230\)
- Eq. (24): \(C_2=0.8751010064,\ p=0.4650560603\)
- \(R_\mathrm{fixed}=0.00776610602\ \mathrm{K/W}\)
- SSRs: \(0.00308060402,\ 0.0338383839,\ 6.44391148\) for \(\Phi,\Phi_\mathrm{eff},Nu\), respectively.

The SEs and 95% CI half-widths also reproduce:

- SE: \(0.00502105,0.01770727,0.01116046;\ 0.00392919,0.08525857,0.03744160;\ 0.17064460,0.03868251\)
- CI half-widths: \(0.01024050,0.03611422,0.02276190;\ 0.00801364,0.17388601,0.07636264;\ 0.34759168,0.07879368\)

Independent metrics, ordered as \(\Phi\) MAE [pp], \(\Phi\) MAPE [%], Nu MAPE [%], \(R_\mathrm{th}\) MAPE [%], RMSE, maximum error, \(R^2\):

| Partition | N | Phi MAE | Phi MAPE | Nu MAPE | Rth MAPE | RMSE | Max. | R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Calibration | 34 | 0.645178 | 2.57172 | 3.56950 | 4.51375 | 0.00481182 | 0.0258756 | 0.913734 |
| EFL-1 | 6 | 0.561902 | 2.24300 | 3.72151 | 6.54670 | 0.00444142 | 0.0104691 | 0.904930 |
| Thermal load | 5 | 0.00234730 | n/a | 5.96087 | 1.06892 | 0.000224243 | 0.000322739 | −7.73426 |
| Cross-combinations | 2 | 0.428997 | 0.826762 | 4.53134 | 1.80888 | 0.000414148 | 0.000563243 | 0.969731 |
| Fixed-fin sweep, accepted | 2 | 3.35777 | 16.3911 | 2.26238 | 7.21779 | 0.00290397 | 0.00405224 | 0.840930 |

These match [refit_stats.csv](/mnt/e/ijhmt-cfp/Paper-5/audit/refit_stats.csv) and [tab_statistics.tex](/mnt/e/ijhmt-cfp/Paper-5/manuscript/tables/tab_statistics.tex). The CSV rounds metrics to four decimal places—for example, 0.000414 becomes 0.0004—while the TeX table retains the requested three significant figures.

Every calibration subgroup in the TeX table also reproduced:

| Subgroup | N | Phi MAE | Phi MAPE | Nu MAPE | Rth MAPE | RMSE | Max. | R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OR = 0 | 9 | 0.00338 | n/a | 5.39 | 1.81 | 0.00130 | 0.00377 | 0.991 |
| \(0<\mathrm{OR}\le0.3\) | 19 | 0.920 | 3.05 | 2.94 | 5.38 | 0.00607 | 0.0259 | 0.826 |
| \(0.3<\mathrm{OR}\le0.7\) | 6 | 0.738 | 1.06 | 2.84 | 5.83 | 0.00349 | 0.00560 | 0.950 |
| \(0.7<\mathrm{OR}\le1\) | 0 | — | — | — | — | — | — | — |
| \(Re_{ch}\le10\) | 5 | 0.307 | 1.81 | 3.74 | 11.5 | 0.0118 | 0.0259 | 0.232 |
| \(10<Re_{ch}\le50\) | 7 | 1.16 | 3.90 | 2.97 | 2.72 | 0.00118 | 0.00247 | 0.994 |
| \(Re_{ch}>50\) | 22 | 0.558 | 2.29 | 3.72 | 3.49 | 0.00199 | 0.00560 | 0.983 |

### 2. Coolant comparison

The ledger directly confirms C017 versus E006 at \(\mathrm{OR}=0.1,\ Re_{ch}=150\):

| Fluid/case | Q [LPM] | m [kg/s] | Re | Pr | Phi | Rth [K/W] | dp [Pa] | Pump [W] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FC-40 C017 | 43.995626 | 1.360198 | 150 | 67.542637 | 0.1606008 | 0.01772215 | 746.267 | 0.5472081 |
| EFL-1 E006 | 53.401040 | 1.681240 | 150 | 94.966364 | 0.1617812 | 0.01711533 | 1153.764 | 1.0268700 |

Independent power-law/log-log interpolation between C017 and C018 gave:

- At E006’s \(Q=53.401040\) LPM: \(m=1.650981\), \(Re=182.0671\), \(Pr=67.542637\), \(\Phi=0.1553672\), \(R_\mathrm{th}=0.01728212\), \(\Delta p=934.6028\) Pa, \(W_\mathrm{pump}=0.8318127\) W.
- At E006’s \(W_\mathrm{pump}=1.0268700\) W: \(Q=58.867533\) LPM, \(m=1.819986\), \(Re=200.7047\), \(Pr=67.542637\), \(\Phi=0.1527994\), \(R_\mathrm{th}=0.01706491\), \(\Delta p=1046.6244\) Pa.

Every value in [coolant_comparison.csv](/mnt/e/ijhmt-cfp/Paper-5/audit/coolant_comparison.csv) and its E006 summary lines matches. The additional E005/C014 summary numbers and its matched-\(Q\) and matched-pump interpolations also reproduce.

### 3. Withheld-load chip-temperature check

| Case | P [W] | Predicted Rth [K/W] | Field Tchip [°C] | Predicted Tchip [°C] | Error [°C] |
|---|---:|---:|---:|---:|---:|
| L001 | 300 | 0.019345 | 30.900255 | 30.803433 | −0.096822 |
| L006 | 500 | 0.019347 | 34.811803 | 34.673735 | −0.138068 |
| L011 | 850 | 0.019352 | 41.612468 | 41.449321 | −0.163147 |
| L016 | 1000 | 0.019354 | 44.508326 | 44.354128 | −0.154198 |
| L021 | 1200 | 0.019357 | 48.350463 | 48.228108 | −0.122355 |

Thus:

- RMSE \(=0.136968^\circ\mathrm C\), reported \(0.137^\circ\mathrm C\)
- Maximum absolute error \(=0.163147^\circ\mathrm C\), reported \(0.163^\circ\mathrm C\)
- Mean error \(=-0.134918^\circ\mathrm C\), reported \(-0.135^\circ\mathrm C\)

### 4. Fixed-fin sweep

| Case | Phi field | Phi closure | Difference [pp] | Rth field | Rth closure | Difference |
|---|---:|---:|---:|---:|---:|---:|
| F001 | 0 | 0.00002347 | +0.00235 | 0.0212936 | 0.021961 | +3.134% |
| F002 | 0.409563 | 0.476694 | +6.713 | 0.0358558 | 0.0399080 | +11.3015% |
| F003 | 0.677988 | 0.700095 | +2.211 | 0.0721262 | 0.0868514 | +20.4152% |
| F004 | 0.842588 | 0.848496 | +0.591 | 0.118611 | 0.237287 | +100.054% |

All quoted rounded values, including F002’s 0.4096/0.4767, 0.03586/0.03991 and +11.3%, are correct.

### 5. Campaign counts and inventory

The published rows reproduce exactly:

| Partition | Finished | Converged | Envelope | At cap | Diverged | In envelope | Accepted |
|---|---:|---:|---:|---:|---:|---:|---:|
| Calibration | 99 | 34 | 51 | 7 | 4 | 34 | 34 |
| EFL-1 | 32 | 6 | 18 | 3 | 4 | 10 | 6 |
| Thermal load | 23 | 5 | 12 | 5 | 1 | 11 | 5 |
| Cross-combinations | 14 | 2 | 8 | 3 | 1 | 5 | 2 |
| Fixed-fin sweep | 4 | 2 | 2 | 0 | 0 | 2 | 2 |
| Grid study | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Here “converged” is the ledger closure boolean and “at cap” is `stop_type == cap` and not converged. Raw calibration `stop_type` counts are 34/51/10/4 for converged/envelope/cap/diverged; three cap cases, C001–C003, passed closure and therefore are not counted as “at cap without converging.”

The case listing contains 177 designed directories and metadata files, 170 `DONE` markers, and exactly the same 170 unique cases as the ledger. The missing cases are precisely E001–E003, G001–G002, L020 and L025. Finished plus missing therefore gives 99, 35, 25, 14, 4 and 2 for the six designed partitions. X013 and X014 belong to both cross-combinations and EFL-1, explaining the two-count overlap in partition totals.

### 6. Diverged cases

All ten stated cases and attributes are correct:

- C075: OR 0.80, Re 10, calibration
- C083: OR 0.90, Re 5, calibration
- C086: OR 0.90, Re 40, calibration
- C095: OR 1.00, Re 40, calibration
- E004: OR 0.10, Re 10, EFL-1
- E026: OR 0.80, Re 40, EFL-1
- E028: OR 0.90, Re 10, EFL-1
- E029: OR 0.90, Re 40, EFL-1
- L002: OR 0.25, Re 40, thermal load
- X010: OR 0.85, Re 15, cross-combinations

### 7. Row-joining fix

[make_campaign_tables.py](/mnt/e/ijhmt-cfp/Paper-5/figures/src/make_campaign_tables.py:41) now uses a real `"\n".join(rows)`. Neither the source nor [tab_campaign_counts.tex](/mnt/e/ijhmt-cfp/Paper-5/manuscript/tables/tab_campaign_counts.tex) contains a literal backslash-`n` token. The TeX has exactly five distinct physical data rows, each with a valid `\\` terminator.

As an additional source check, all 103 rows and 11 fields of [feasibility_map.csv](/mnt/e/ijhmt-cfp/Paper-5/audit/feasibility_map.csv) reproduce from the ledger, including 13 feasible rows; maximum floating-point differences were below \(4\times10^{-15}\).

```
CONFIRMED (reproduced to 3 significant figures): 1. Eq. (23), effective-bypass and Eq. (24) fits, uncertainties, SSRs and R_fixed; 2. all partition and calibration-subgroup statistics; 3. C017/E006 coolant pairing and matched-Q/matched-pump interpolation; 4. five withheld-load T_chip predictions, RMSE and maximum error; 5. F001-F004 closure comparisons; 6. every campaign count, designed total and missing-case ID; 7. all ten diverged-case attributes; 8. table row-joining fix and five-row TeX output; 9. all 103 feasibility-map rows
DISCREPANCIES: none
NOT VERIFIABLE: none
VERDICT: PASS
```