# Campaign results summary (93 finished cases in the ledger)

Source: cfd/unit_cell_campaign/dataset_ledger_unitcell.csv unless stated.

## Calibration partition (FC-40, 700 W)
finished 93 | inside envelope 34 | converged 34 | accepted 34 | at cap (12000 or more iterations, not converged) 0 | solver exit code != 0 3
iterations of accepted cases: min 1201, median 5329, max 18504
closures of accepted cases: mass split max 4.13e-07 %, energy balance max 0.277 %, stationarity max 9.34e-04
wall temperature of accepted cases: 31.5 to 68.4 C; chip (base max + TIM): 36.1 to 73.0 C
OR 0.0: accepted at Re_ch [2, 5, 10, 20, 40, 70, 100, 150, 250]; outside the wall bound at []
OR 0.1: accepted at Re_ch [5, 10, 20, 40, 70, 100, 150, 250]; outside the wall bound at [2]
OR 0.2: accepted at Re_ch [20, 40, 70, 100, 150, 250]; outside the wall bound at [2, 5, 10]
OR 0.3: accepted at Re_ch [40, 70, 100, 150, 250]; outside the wall bound at [2, 5, 10, 20]
OR 0.4: accepted at Re_ch [70, 100, 150, 250]; outside the wall bound at [2, 5, 10, 20, 40]
OR 0.5: accepted at Re_ch [150, 250]; outside the wall bound at [2, 5, 10, 20, 40, 70, 100]
OR 0.6: accepted at Re_ch []; outside the wall bound at [2, 5, 10, 20, 40, 70, 100, 150, 250]
OR 0.7: accepted at Re_ch []; outside the wall bound at [2, 5, 10, 20, 40, 70, 100, 150, 250]
OR 0.8: accepted at Re_ch []; outside the wall bound at [2, 5, 10, 20, 40, 70, 100, 150, 250]
OR 0.9: accepted at Re_ch []; outside the wall bound at [2, 5, 10, 20, 40, 70, 100, 150, 250]
OR 1.0: accepted at Re_ch []; outside the wall bound at [2, 5, 10]

## Bypass split (accepted cases)
OR 0.0: Phi leading edge [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]; mid [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]; trailing edge [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]; Phi_eff [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] (Re_ch [2, 5, 10, 20, 40, 70, 100, 150, 250])
OR 0.1: Phi leading edge [0.436, 0.37, 0.292, 0.229, 0.193, 0.176, 0.161, 0.147]; mid [0.614, 0.658, 0.623, 0.54, 0.464, 0.417, 0.369, 0.316]; trailing edge [0.538, 0.652, 0.673, 0.624, 0.554, 0.505, 0.449, 0.385]; Phi_eff [0.585, 0.629, 0.603, 0.528, 0.453, 0.407, 0.359, 0.307] (Re_ch [5, 10, 20, 40, 70, 100, 150, 250])
OR 0.2: Phi leading edge [0.595, 0.499, 0.426, 0.387, 0.35, 0.315]; mid [0.897, 0.858, 0.791, 0.737, 0.673, 0.595]; trailing edge [0.907, 0.914, 0.876, 0.835, 0.777, 0.696]; Phi_eff [0.884, 0.858, 0.795, 0.74, 0.673, 0.591] (Re_ch [20, 40, 70, 100, 150, 250])
OR 0.3: Phi leading edge [0.687, 0.616, 0.57, 0.522, 0.471]; mid [0.953, 0.932, 0.906, 0.863, 0.794]; trailing edge [0.968, 0.969, 0.958, 0.934, 0.884]; Phi_eff [0.95, 0.937, 0.914, 0.873, 0.802] (Re_ch [40, 70, 100, 150, 250])
OR 0.4: Phi leading edge [0.748, 0.71, 0.664, 0.609]; mid [0.976, 0.97, 0.954, 0.917]; trailing edge [0.987, 0.987, 0.983, 0.969]; Phi_eff [0.976, 0.973, 0.961, 0.93] (Re_ch [70, 100, 150, 250])
OR 0.5: Phi leading edge [0.772, 0.725]; mid [0.986, 0.975]; trailing edge [0.994, 0.992]; Phi_eff [0.987, 0.981] (Re_ch [150, 250])

## Nusselt number (accepted cases; length-averaged, and local in the first and last fifth)
OR 0.0: Nu [7.55, 8.16, 8.24, 8.44, 8.99, 9.84, 10.61, 11.72, 13.5]; Nu_B0 [6.4, 8.1, 9.0, 10.3, 12.3, 14.5, 16.1, 18.4, 21.6]; Nu_B4 [8.65, 7.96, 7.81, 7.71, 7.78, 8.14, 8.59, 9.33, 10.59]; Re_active [2.0, 5.0, 10.0, 20.0, 40.0, 70.0, 100.0, 150.0, 250.0]
OR 0.1: Nu [7.38, 7.99, 8.22, 8.44, 8.92, 9.48, 10.41, 12.02]; Nu_B0 [6.8, 8.4, 9.3, 10.9, 12.9, 14.5, 16.7, 19.9]; Nu_B4 [7.12, 6.89, 7.45, 7.55, 7.56, 7.73, 8.22, 9.29]; Re_active [2.8, 6.3, 14.2, 30.8, 56.5, 82.4, 125.9, 213.2]
OR 0.2: Nu [8.04, 8.36, 8.49, 8.72, 9.27, 10.54]; Nu_B0 [8.9, 9.8, 11.4, 12.8, 14.8, 17.9]; Nu_B4 [5.33, 7.1, 7.47, 7.42, 7.46, 8.07]; Re_active [8.1, 20.0, 40.2, 61.3, 97.5, 171.4]
OR 0.3: Nu [8.16, 8.42, 8.51, 8.71, 9.42]; Nu_B0 [9.6, 10.4, 11.4, 13.1, 16.0]; Nu_B4 [4.36, 6.43, 7.18, 7.33, 7.35]; Re_active [12.5, 26.9, 43.0, 71.8, 132.3]
OR 0.4: Nu [8.16, 8.39, 8.55, 8.87]; Nu_B0 [10.0, 10.6, 11.8, 14.2]; Nu_B4 [3.5, 5.02, 6.48, 7.2]; Re_active [17.6, 29.0, 50.4, 97.7]
OR 0.5: Nu [8.35, 8.65]; Nu_B0 [11.0, 12.7]; Nu_B4 [3.63, 5.68]; Re_active [34.2, 68.7]

## Temperature budget of the base maximum (accepted cases) [K]: base drop | interface span | mean film | bulk rise | P/(m(1-Phi_in)cp) | P/(m(1-Phi_eff)cp)
C001 OR 0.0 Re 2: total 38.49 | 0.40 | 14.37 | 2.41 | 32.38 | 33.10 | 33.10
C002 OR 0.0 Re 5: total 20.63 | 0.42 | 10.45 | 2.20 | 13.10 | 13.24 | 13.24
C003 OR 0.0 Re 10: total 14.59 | 0.43 | 8.41 | 2.17 | 6.55 | 6.62 | 6.62
C004 OR 0.0 Re 20: total 11.34 | 0.43 | 7.06 | 2.12 | 3.24 | 3.31 | 3.31
C005 OR 0.0 Re 40: total 9.51 | 0.44 | 6.23 | 1.98 | 1.59 | 1.66 | 1.66
C006 OR 0.0 Re 70: total 8.53 | 0.44 | 5.79 | 1.81 | 0.89 | 0.95 | 0.95
C007 OR 0.0 Re 100: total 8.01 | 0.44 | 5.56 | 1.68 | 0.61 | 0.66 | 0.66
C008 OR 0.0 Re 150: total 7.49 | 0.44 | 5.31 | 1.52 | 0.40 | 0.44 | 0.44
C009 OR 0.0 Re 250: total 6.89 | 0.44 | 5.00 | 1.32 | 0.24 | 0.26 | 0.26
C011 OR 0.1 Re 5: total 37.68 | 0.41 | 13.58 | 2.71 | 30.24 | 26.01 | 35.34
C012 OR 0.1 Re 10: total 26.00 | 0.41 | 11.88 | 2.48 | 19.02 | 11.64 | 19.78
C013 OR 0.1 Re 20: total 16.99 | 0.42 | 9.18 | 2.40 | 9.70 | 5.18 | 9.24
C014 OR 0.1 Re 40: total 11.95 | 0.43 | 7.12 | 2.33 | 4.27 | 2.38 | 3.88
C015 OR 0.1 Re 70: total 9.84 | 0.43 | 6.18 | 2.21 | 2.09 | 1.30 | 1.92
C016 OR 0.1 Re 100: total 8.97 | 0.44 | 5.81 | 2.08 | 1.32 | 0.89 | 1.24
C017 OR 0.1 Re 150: total 8.21 | 0.44 | 5.48 | 1.89 | 0.79 | 0.58 | 0.76
C018 OR 0.1 Re 250: total 7.41 | 0.44 | 5.11 | 1.64 | 0.42 | 0.34 | 0.42
C022 OR 0.2 Re 20: total 35.65 | 0.39 | 14.99 | 2.77 | 29.92 | 10.17 | 35.40
C023 OR 0.2 Re 40: total 20.60 | 0.40 | 10.62 | 2.65 | 14.78 | 4.10 | 14.51
C024 OR 0.2 Re 70: total 13.47 | 0.42 | 7.61 | 2.60 | 6.56 | 2.05 | 5.72
C025 OR 0.2 Re 100: total 11.09 | 0.43 | 6.52 | 2.53 | 3.72 | 1.34 | 3.17
C026 OR 0.2 Re 150: total 9.51 | 0.43 | 5.82 | 2.38 | 1.95 | 0.84 | 1.68
C027 OR 0.2 Re 250: total 8.24 | 0.44 | 5.29 | 2.09 | 0.89 | 0.48 | 0.80
C032 OR 0.3 Re 40: total 39.05 | 0.38 | 16.63 | 3.10 | 34.45 | 7.49 | 46.83
C033 OR 0.3 Re 70: total 24.01 | 0.39 | 11.97 | 2.98 | 19.33 | 3.49 | 21.34
C034 OR 0.3 Re 100: total 17.08 | 0.41 | 9.05 | 2.95 | 11.42 | 2.18 | 10.93
C035 OR 0.3 Re 150: total 12.45 | 0.42 | 6.90 | 2.87 | 5.65 | 1.30 | 4.90
C036 OR 0.3 Re 250: total 9.67 | 0.43 | 5.65 | 2.65 | 2.24 | 0.71 | 1.89
C042 OR 0.4 Re 70: total 43.79 | 0.36 | 18.53 | 3.59 | 40.09 | 6.16 | 65.50
C043 OR 0.4 Re 100: total 32.37 | 0.37 | 15.16 | 3.47 | 28.80 | 3.74 | 39.82
C044 OR 0.4 Re 150: total 21.40 | 0.39 | 10.84 | 3.39 | 16.95 | 2.15 | 18.81
C045 OR 0.4 Re 250: total 13.18 | 0.42 | 7.00 | 3.26 | 6.81 | 1.11 | 6.18
C053 OR 0.5 Re 150: total 41.82 | 0.35 | 18.57 | 4.14 | 38.76 | 3.79 | 67.84
C054 OR 0.5 Re 250: total 25.14 | 0.37 | 12.44 | 3.98 | 21.54 | 1.88 | 27.63

## Thermal resistance, pressure drop, pumping power (accepted cases)
C001 OR 0.0 Re 2: R_th 0.0610 K/W (R_base 0.0550 + R_TIM 0.006); dp 7.859 Pa; Q_full 0.650 LPM; W_pump 8.515e-05 W; T_chip 67.7 C
C002 OR 0.0 Re 5: R_th 0.0355 K/W (R_base 0.0295 + R_TIM 0.006); dp 32.05 Pa; Q_full 1.625 LPM; W_pump 0.0008681 W; T_chip 49.8 C
C003 OR 0.0 Re 10: R_th 0.0268 K/W (R_base 0.0208 + R_TIM 0.006); dp 71.28 Pa; Q_full 3.251 LPM; W_pump 0.003862 W; T_chip 43.8 C
C004 OR 0.0 Re 20: R_th 0.0222 K/W (R_base 0.0162 + R_TIM 0.006); dp 149.5 Pa; Q_full 6.501 LPM; W_pump 0.01619 W; T_chip 40.5 C
C005 OR 0.0 Re 40: R_th 0.0196 K/W (R_base 0.0136 + R_TIM 0.006); dp 306.5 Pa; Q_full 13.002 LPM; W_pump 0.06642 W; T_chip 38.7 C
C006 OR 0.0 Re 70: R_th 0.0182 K/W (R_base 0.0122 + R_TIM 0.006); dp 543.9 Pa; Q_full 22.754 LPM; W_pump 0.2063 W; T_chip 37.7 C
C007 OR 0.0 Re 100: R_th 0.0174 K/W (R_base 0.0114 + R_TIM 0.006); dp 783.1 Pa; Q_full 32.505 LPM; W_pump 0.4243 W; T_chip 37.2 C
C008 OR 0.0 Re 150: R_th 0.0167 K/W (R_base 0.0107 + R_TIM 0.006); dp 1185 Pa; Q_full 48.758 LPM; W_pump 0.963 W; T_chip 36.7 C
C009 OR 0.0 Re 250: R_th 0.0158 K/W (R_base 0.0098 + R_TIM 0.006); dp 1999 Pa; Q_full 81.264 LPM; W_pump 2.708 W; T_chip 36.1 C
C011 OR 0.1 Re 5: R_th 0.0598 K/W (R_base 0.0538 + R_TIM 0.006); dp 7.883 Pa; Q_full 1.467 LPM; W_pump 0.0001927 W; T_chip 66.9 C
C012 OR 0.1 Re 10: R_th 0.0431 K/W (R_base 0.0371 + R_TIM 0.006); dp 21.4 Pa; Q_full 2.933 LPM; W_pump 0.001046 W; T_chip 55.2 C
C013 OR 0.1 Re 20: R_th 0.0303 K/W (R_base 0.0243 + R_TIM 0.006); dp 56.13 Pa; Q_full 5.866 LPM; W_pump 0.005487 W; T_chip 46.2 C
C014 OR 0.1 Re 40: R_th 0.0231 K/W (R_base 0.0171 + R_TIM 0.006); dp 143.3 Pa; Q_full 11.732 LPM; W_pump 0.02802 W; T_chip 41.1 C
C015 OR 0.1 Re 70: R_th 0.0201 K/W (R_base 0.0141 + R_TIM 0.006); dp 294.9 Pa; Q_full 20.531 LPM; W_pump 0.1009 W; T_chip 39.0 C
C016 OR 0.1 Re 100: R_th 0.0188 K/W (R_base 0.0128 + R_TIM 0.006); dp 458.7 Pa; Q_full 29.330 LPM; W_pump 0.2242 W; T_chip 38.2 C
C017 OR 0.1 Re 150: R_th 0.0177 K/W (R_base 0.0117 + R_TIM 0.006); dp 746.3 Pa; Q_full 43.996 LPM; W_pump 0.5472 W; T_chip 37.4 C
C018 OR 0.1 Re 250: R_th 0.0166 K/W (R_base 0.0106 + R_TIM 0.006); dp 1351 Pa; Q_full 73.326 LPM; W_pump 1.651 W; T_chip 36.6 C
C022 OR 0.2 Re 20: R_th 0.0569 K/W (R_base 0.0509 + R_TIM 0.006); dp 13.81 Pa; Q_full 5.231 LPM; W_pump 0.001204 W; T_chip 64.8 C
C023 OR 0.2 Re 40: R_th 0.0354 K/W (R_base 0.0294 + R_TIM 0.006); dp 48.15 Pa; Q_full 10.462 LPM; W_pump 0.008396 W; T_chip 49.8 C
C024 OR 0.2 Re 70: R_th 0.0252 K/W (R_base 0.0192 + R_TIM 0.006); dp 124.3 Pa; Q_full 18.309 LPM; W_pump 0.03792 W; T_chip 42.7 C
C025 OR 0.2 Re 100: R_th 0.0218 K/W (R_base 0.0158 + R_TIM 0.006); dp 218.7 Pa; Q_full 26.155 LPM; W_pump 0.09533 W; T_chip 40.3 C
C026 OR 0.2 Re 150: R_th 0.0196 K/W (R_base 0.0136 + R_TIM 0.006); dp 400 Pa; Q_full 39.233 LPM; W_pump 0.2616 W; T_chip 38.7 C
C027 OR 0.2 Re 250: R_th 0.0178 K/W (R_base 0.0118 + R_TIM 0.006); dp 811.8 Pa; Q_full 65.388 LPM; W_pump 0.8847 W; T_chip 37.4 C
C032 OR 0.3 Re 40: R_th 0.0618 K/W (R_base 0.0558 + R_TIM 0.006); dp 16.06 Pa; Q_full 9.192 LPM; W_pump 0.002461 W; T_chip 68.2 C
C033 OR 0.3 Re 70: R_th 0.0403 K/W (R_base 0.0343 + R_TIM 0.006); dp 47.35 Pa; Q_full 16.086 LPM; W_pump 0.01269 W; T_chip 53.2 C
C034 OR 0.3 Re 100: R_th 0.0304 K/W (R_base 0.0244 + R_TIM 0.006); dp 91.83 Pa; Q_full 22.980 LPM; W_pump 0.03517 W; T_chip 46.3 C
C035 OR 0.3 Re 150: R_th 0.0238 K/W (R_base 0.0178 + R_TIM 0.006); dp 188.3 Pa; Q_full 34.470 LPM; W_pump 0.1082 W; T_chip 41.6 C
C036 OR 0.3 Re 250: R_th 0.0198 K/W (R_base 0.0138 + R_TIM 0.006); dp 437 Pa; Q_full 57.451 LPM; W_pump 0.4184 W; T_chip 38.9 C
C042 OR 0.4 Re 70: R_th 0.0686 K/W (R_base 0.0626 + R_TIM 0.006); dp 18.27 Pa; Q_full 13.864 LPM; W_pump 0.004222 W; T_chip 73.0 C
C043 OR 0.4 Re 100: R_th 0.0522 K/W (R_base 0.0462 + R_TIM 0.006); dp 36.88 Pa; Q_full 19.805 LPM; W_pump 0.01217 W; T_chip 61.6 C
C044 OR 0.4 Re 150: R_th 0.0366 K/W (R_base 0.0306 + R_TIM 0.006); dp 80.65 Pa; Q_full 29.708 LPM; W_pump 0.03993 W; T_chip 50.6 C
C045 OR 0.4 Re 250: R_th 0.0248 K/W (R_base 0.0188 + R_TIM 0.006); dp 208.2 Pa; Q_full 49.513 LPM; W_pump 0.1718 W; T_chip 42.4 C
C053 OR 0.5 Re 150: R_th 0.0657 K/W (R_base 0.0597 + R_TIM 0.006); dp 33.09 Pa; Q_full 24.945 LPM; W_pump 0.01376 W; T_chip 71.0 C
C054 OR 0.5 Re 250: R_th 0.0419 K/W (R_base 0.0359 + R_TIM 0.006); dp 89.53 Pa; Q_full 41.576 LPM; W_pump 0.06204 W; T_chip 54.3 C

## Ratios to the sealed case at the same Re_ch (accepted cases): R_th/R_th,sealed; W_pump/W_pump,sealed
C011 OR 0.1 Re 5: 1.687; 0.222
C012 OR 0.1 Re 10: 1.607; 0.271
C013 OR 0.1 Re 20: 1.364; 0.339
C014 OR 0.1 Re 40: 1.178; 0.422
C015 OR 0.1 Re 70: 1.103; 0.489
C016 OR 0.1 Re 100: 1.078; 0.529
C017 OR 0.1 Re 150: 1.061; 0.568
C018 OR 0.1 Re 250: 1.047; 0.610
C022 OR 0.2 Re 20: 2.564; 0.074
C023 OR 0.2 Re 40: 1.809; 0.126
C024 OR 0.2 Re 70: 1.388; 0.184
C025 OR 0.2 Re 100: 1.252; 0.225
C026 OR 0.2 Re 150: 1.173; 0.272
C027 OR 0.2 Re 250: 1.122; 0.327
C032 OR 0.3 Re 40: 3.155; 0.037
C033 OR 0.3 Re 70: 2.216; 0.062
C034 OR 0.3 Re 100: 1.742; 0.083
C035 OR 0.3 Re 150: 1.424; 0.112
C036 OR 0.3 Re 250: 1.251; 0.155
C042 OR 0.4 Re 70: 3.771; 0.020
C043 OR 0.4 Re 100: 2.994; 0.029
C044 OR 0.4 Re 150: 2.190; 0.041
C045 OR 0.4 Re 250: 1.568; 0.063
C053 OR 0.5 Re 150: 3.937; 0.014
C054 OR 0.5 Re 250: 2.646; 0.023

## Caloric term against the measured channel exit rise (accepted cases with OR > 0): underestimation factor with the leading-edge Phi min 1.16 max 11.4; with Phi_eff: within 1 K in 16 of 25 cases; error range -15.0% to 4.0% at OR <= 0.2 (excluding the lowest accepted Re of each OR: C011, C022), -16% to 75% at OR >= 0.3
C011 OR 0.1 Re 5: rise 30.24 K | P/(m(1-Phi_in)cp) 26.01 | P/(m(1-Phi_eff)cp) 35.34 | error +5.10 K (+16.9 %) | underestimation 1.16
C012 OR 0.1 Re 10: rise 19.02 K | P/(m(1-Phi_in)cp) 11.64 | P/(m(1-Phi_eff)cp) 19.78 | error +0.76 K (+4.0 %) | underestimation 1.63
C013 OR 0.1 Re 20: rise 9.70 K | P/(m(1-Phi_in)cp) 5.18 | P/(m(1-Phi_eff)cp) 9.24 | error -0.46 K (-4.7 %) | underestimation 1.87
C014 OR 0.1 Re 40: rise 4.27 K | P/(m(1-Phi_in)cp) 2.38 | P/(m(1-Phi_eff)cp) 3.88 | error -0.38 K (-9.0 %) | underestimation 1.79
C015 OR 0.1 Re 70: rise 2.09 K | P/(m(1-Phi_in)cp) 1.30 | P/(m(1-Phi_eff)cp) 1.92 | error -0.17 K (-8.2 %) | underestimation 1.61
C016 OR 0.1 Re 100: rise 1.32 K | P/(m(1-Phi_in)cp) 0.89 | P/(m(1-Phi_eff)cp) 1.24 | error -0.08 K (-6.1 %) | underestimation 1.48
C017 OR 0.1 Re 150: rise 0.79 K | P/(m(1-Phi_in)cp) 0.58 | P/(m(1-Phi_eff)cp) 0.76 | error -0.02 K (-3.1 %) | underestimation 1.35
C018 OR 0.1 Re 250: rise 0.42 K | P/(m(1-Phi_in)cp) 0.34 | P/(m(1-Phi_eff)cp) 0.42 | error +0.00 K (+0.8 %) | underestimation 1.22
C022 OR 0.2 Re 20: rise 29.92 K | P/(m(1-Phi_in)cp) 10.17 | P/(m(1-Phi_eff)cp) 35.40 | error +5.48 K (+18.3 %) | underestimation 2.94
C023 OR 0.2 Re 40: rise 14.78 K | P/(m(1-Phi_in)cp) 4.10 | P/(m(1-Phi_eff)cp) 14.51 | error -0.26 K (-1.8 %) | underestimation 3.60
C024 OR 0.2 Re 70: rise 6.56 K | P/(m(1-Phi_in)cp) 2.05 | P/(m(1-Phi_eff)cp) 5.72 | error -0.84 K (-12.8 %) | underestimation 3.21
C025 OR 0.2 Re 100: rise 3.72 K | P/(m(1-Phi_in)cp) 1.34 | P/(m(1-Phi_eff)cp) 3.17 | error -0.56 K (-15.0 %) | underestimation 2.78
C026 OR 0.2 Re 150: rise 1.95 K | P/(m(1-Phi_in)cp) 0.84 | P/(m(1-Phi_eff)cp) 1.68 | error -0.27 K (-14.0 %) | underestimation 2.32
C027 OR 0.2 Re 250: rise 0.89 K | P/(m(1-Phi_in)cp) 0.48 | P/(m(1-Phi_eff)cp) 0.80 | error -0.09 K (-10.1 %) | underestimation 1.86
C032 OR 0.3 Re 40: rise 34.45 K | P/(m(1-Phi_in)cp) 7.49 | P/(m(1-Phi_eff)cp) 46.83 | error +12.38 K (+35.9 %) | underestimation 4.60
C033 OR 0.3 Re 70: rise 19.33 K | P/(m(1-Phi_in)cp) 3.49 | P/(m(1-Phi_eff)cp) 21.34 | error +2.00 K (+10.4 %) | underestimation 5.55
C034 OR 0.3 Re 100: rise 11.42 K | P/(m(1-Phi_in)cp) 2.18 | P/(m(1-Phi_eff)cp) 10.93 | error -0.49 K (-4.3 %) | underestimation 5.25
C035 OR 0.3 Re 150: rise 5.65 K | P/(m(1-Phi_in)cp) 1.30 | P/(m(1-Phi_eff)cp) 4.90 | error -0.75 K (-13.3 %) | underestimation 4.33
C036 OR 0.3 Re 250: rise 2.24 K | P/(m(1-Phi_in)cp) 0.71 | P/(m(1-Phi_eff)cp) 1.89 | error -0.35 K (-15.7 %) | underestimation 3.17
C042 OR 0.4 Re 70: rise 40.09 K | P/(m(1-Phi_in)cp) 6.16 | P/(m(1-Phi_eff)cp) 65.50 | error +25.42 K (+63.4 %) | underestimation 6.51
C043 OR 0.4 Re 100: rise 28.80 K | P/(m(1-Phi_in)cp) 3.74 | P/(m(1-Phi_eff)cp) 39.82 | error +11.02 K (+38.3 %) | underestimation 7.69
C044 OR 0.4 Re 150: rise 16.95 K | P/(m(1-Phi_in)cp) 2.15 | P/(m(1-Phi_eff)cp) 18.81 | error +1.86 K (+11.0 %) | underestimation 7.87
C045 OR 0.4 Re 250: rise 6.81 K | P/(m(1-Phi_in)cp) 1.11 | P/(m(1-Phi_eff)cp) 6.18 | error -0.62 K (-9.2 %) | underestimation 6.12
C053 OR 0.5 Re 150: rise 38.76 K | P/(m(1-Phi_in)cp) 3.79 | P/(m(1-Phi_eff)cp) 67.84 | error +29.08 K (+75.0 %) | underestimation 10.24
C054 OR 0.5 Re 250: rise 21.54 K | P/(m(1-Phi_in)cp) 1.88 | P/(m(1-Phi_eff)cp) 27.63 | error +6.09 K (+28.3 %) | underestimation 11.44

## Feasible operating map (audit/feasibility_map.csv; R_th <= 1.10 R_sealed(Re) and T_chip <= 85 C): 12 feasible of 91 rows
Re 2: feasible OR [0.0]; minimum W_pump at OR 0.0: 8.515e-05 W (sealed 8.515e-05 W, ratio 1.000), R_th ratio 1.000, T_chip 67.7 C
Re 5: feasible OR [0.0]; minimum W_pump at OR 0.0: 0.0008681 W (sealed 0.0008681 W, ratio 1.000), R_th ratio 1.000, T_chip 49.8 C
Re 10: feasible OR [0.0]; minimum W_pump at OR 0.0: 0.003862 W (sealed 0.003862 W, ratio 1.000), R_th ratio 1.000, T_chip 43.8 C
Re 20: feasible OR [0.0]; minimum W_pump at OR 0.0: 0.01619 W (sealed 0.01619 W, ratio 1.000), R_th ratio 1.000, T_chip 40.5 C
Re 40: feasible OR [0.0]; minimum W_pump at OR 0.0: 0.06642 W (sealed 0.06642 W, ratio 1.000), R_th ratio 1.000, T_chip 38.7 C
Re 70: feasible OR [0.0]; minimum W_pump at OR 0.0: 0.2063 W (sealed 0.2063 W, ratio 1.000), R_th ratio 1.000, T_chip 37.7 C
Re 100: feasible OR [0.0, 0.1]; minimum W_pump at OR 0.1: 0.2242 W (sealed 0.4243 W, ratio 0.529), R_th ratio 1.078, T_chip 38.2 C
Re 150: feasible OR [0.0, 0.1]; minimum W_pump at OR 0.1: 0.5472 W (sealed 0.963 W, ratio 0.568), R_th ratio 1.061, T_chip 37.4 C
Re 250: feasible OR [0.0, 0.1]; minimum W_pump at OR 0.1: 1.651 W (sealed 2.708 W, ratio 0.610), R_th ratio 1.047, T_chip 36.6 C

## Network terms of Eq. (rth_sum) with the fitted coefficients (accepted cases) [K/W]: R_fixed 0.0078 | convective 1/(eta_o h A) | caloric 1/(m(1-Phi_eff)cp) | predicted | field | error %; eta_fin, eta_o
convective term min 0.0074 max 0.0100 (ratio 1.35); caloric term min 0.0004 max 0.0682 (ratio 180); R_TIM 0.0060; implied R_spread = R_fixed - R_TIM = 0.0018
C001 OR 0.0 Re 2: conv 0.0097 | cal 0.0473 | pred 0.0647 | field 0.0610 | +6.2 % | eta_fin 0.333 eta_o 0.341 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 7.86
C002 OR 0.0 Re 5: conv 0.0096 | cal 0.0189 | pred 0.0363 | field 0.0355 | +2.3 % | eta_fin 0.330 eta_o 0.338 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 7.89
C003 OR 0.0 Re 10: conv 0.0096 | cal 0.0095 | pred 0.0268 | field 0.0268 | -0.2 % | eta_fin 0.328 eta_o 0.336 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 7.95
C004 OR 0.0 Re 20: conv 0.0094 | cal 0.0047 | pred 0.0219 | field 0.0222 | -1.2 % | eta_fin 0.325 eta_o 0.333 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 8.10
C005 OR 0.0 Re 40: conv 0.0092 | cal 0.0024 | pred 0.0194 | field 0.0196 | -1.2 % | eta_fin 0.318 eta_o 0.326 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 8.48
C006 OR 0.0 Re 70: conv 0.0089 | cal 0.0014 | pred 0.0180 | field 0.0182 | -1.1 % | eta_fin 0.307 eta_o 0.315 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 9.11
C007 OR 0.0 Re 100: conv 0.0085 | cal 0.0009 | pred 0.0173 | field 0.0174 | -1.1 % | eta_fin 0.296 eta_o 0.305 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 9.77
C008 OR 0.0 Re 150: conv 0.0081 | cal 0.0006 | pred 0.0165 | field 0.0167 | -1.3 % | eta_fin 0.281 eta_o 0.290 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 10.85
C009 OR 0.0 Re 250: conv 0.0074 | cal 0.0004 | pred 0.0156 | field 0.0158 | -1.8 % | eta_fin 0.259 eta_o 0.268 | Phi_pred 0.000 Phi_eff_pred 0.000 Nu_pred 12.80
C011 OR 0.1 Re 5: conv 0.0097 | cal 0.0682 | pred 0.0857 | field 0.0598 | +43.3 % | eta_fin 0.367 eta_o 0.375 | Phi_pred 0.447 Phi_eff_pred 0.693 Nu_pred 7.87
C012 OR 0.1 Re 10: conv 0.0096 | cal 0.0282 | pred 0.0456 | field 0.0431 | +5.7 % | eta_fin 0.365 eta_o 0.373 | Phi_pred 0.373 Phi_eff_pred 0.629 Nu_pred 7.90
C013 OR 0.1 Re 20: conv 0.0095 | cal 0.0119 | pred 0.0292 | field 0.0303 | -3.5 % | eta_fin 0.362 eta_o 0.370 | Phi_pred 0.304 Phi_eff_pred 0.560 Nu_pred 8.00
C014 OR 0.1 Re 40: conv 0.0094 | cal 0.0051 | pred 0.0222 | field 0.0231 | -3.6 % | eta_fin 0.356 eta_o 0.364 | Phi_pred 0.243 Phi_eff_pred 0.488 Nu_pred 8.28
C015 OR 0.1 Re 70: conv 0.0090 | cal 0.0026 | pred 0.0194 | field 0.0201 | -3.0 % | eta_fin 0.345 eta_o 0.354 | Phi_pred 0.201 Phi_eff_pred 0.431 Nu_pred 8.81
C016 OR 0.1 Re 100: conv 0.0087 | cal 0.0017 | pred 0.0182 | field 0.0188 | -3.1 % | eta_fin 0.335 eta_o 0.343 | Phi_pred 0.176 Phi_eff_pred 0.395 Nu_pred 9.38
C017 OR 0.1 Re 150: conv 0.0083 | cal 0.0011 | pred 0.0171 | field 0.0177 | -3.3 % | eta_fin 0.319 eta_o 0.328 | Phi_pred 0.152 Phi_eff_pred 0.355 Nu_pred 10.36
C018 OR 0.1 Re 250: conv 0.0076 | cal 0.0006 | pred 0.0160 | field 0.0166 | -3.7 % | eta_fin 0.294 eta_o 0.303 | Phi_pred 0.125 Phi_eff_pred 0.309 Nu_pred 12.21
C022 OR 0.2 Re 20: conv 0.0097 | cal 0.0398 | pred 0.0572 | field 0.0569 | +0.6 % | eta_fin 0.407 eta_o 0.415 | Phi_pred 0.568 Phi_eff_pred 0.852 Nu_pred 7.93
C023 OR 0.2 Re 40: conv 0.0095 | cal 0.0157 | pred 0.0330 | field 0.0354 | -7.0 % | eta_fin 0.401 eta_o 0.410 | Phi_pred 0.492 Phi_eff_pred 0.812 Nu_pred 8.10
C024 OR 0.2 Re 70: conv 0.0093 | cal 0.0074 | pred 0.0245 | field 0.0252 | -2.9 % | eta_fin 0.393 eta_o 0.402 | Phi_pred 0.430 Phi_eff_pred 0.775 Nu_pred 8.47
C025 OR 0.2 Re 100: conv 0.0090 | cal 0.0047 | pred 0.0215 | field 0.0218 | -1.8 % | eta_fin 0.384 eta_o 0.393 | Phi_pred 0.392 Phi_eff_pred 0.748 Nu_pred 8.91
C026 OR 0.2 Re 150: conv 0.0086 | cal 0.0027 | pred 0.0191 | field 0.0196 | -2.3 % | eta_fin 0.368 eta_o 0.377 | Phi_pred 0.350 Phi_eff_pred 0.715 Nu_pred 9.71
C027 OR 0.2 Re 250: conv 0.0079 | cal 0.0014 | pred 0.0171 | field 0.0178 | -3.7 % | eta_fin 0.342 eta_o 0.351 | Phi_pred 0.300 Phi_eff_pred 0.670 Nu_pred 11.34
C032 OR 0.3 Re 40: conv 0.0097 | cal 0.0430 | pred 0.0605 | field 0.0618 | -2.1 % | eta_fin 0.456 eta_o 0.465 | Phi_pred 0.668 Phi_eff_pred 0.922 Nu_pred 7.99
C033 OR 0.3 Re 70: conv 0.0095 | cal 0.0199 | pred 0.0372 | field 0.0403 | -7.7 % | eta_fin 0.450 eta_o 0.459 | Phi_pred 0.611 Phi_eff_pred 0.904 Nu_pred 8.22
C034 OR 0.3 Re 100: conv 0.0093 | cal 0.0122 | pred 0.0293 | field 0.0304 | -3.7 % | eta_fin 0.442 eta_o 0.451 | Phi_pred 0.572 Phi_eff_pred 0.890 Nu_pred 8.52
C035 OR 0.3 Re 150: conv 0.0090 | cal 0.0070 | pred 0.0238 | field 0.0238 | -0.1 % | eta_fin 0.429 eta_o 0.438 | Phi_pred 0.528 Phi_eff_pred 0.873 Nu_pred 9.12
C036 OR 0.3 Re 250: conv 0.0083 | cal 0.0035 | pred 0.0196 | field 0.0198 | -1.1 % | eta_fin 0.403 eta_o 0.412 | Phi_pred 0.471 Phi_eff_pred 0.847 Nu_pred 10.44
C042 OR 0.4 Re 70: conv 0.0099 | cal 0.0498 | pred 0.0674 | field 0.0686 | -1.6 % | eta_fin 0.517 eta_o 0.527 | Phi_pred 0.741 Phi_eff_pred 0.955 Nu_pred 8.06
C043 OR 0.4 Re 100: conv 0.0097 | cal 0.0303 | pred 0.0478 | field 0.0522 | -8.6 % | eta_fin 0.511 eta_o 0.521 | Phi_pred 0.709 Phi_eff_pred 0.949 Nu_pred 8.25
C044 OR 0.4 Re 150: conv 0.0094 | cal 0.0172 | pred 0.0344 | field 0.0366 | -5.9 % | eta_fin 0.501 eta_o 0.510 | Phi_pred 0.671 Phi_eff_pred 0.940 Nu_pred 8.66
C045 OR 0.4 Re 250: conv 0.0088 | cal 0.0085 | pred 0.0251 | field 0.0248 | +1.0 % | eta_fin 0.478 eta_o 0.488 | Phi_pred 0.619 Phi_eff_pred 0.927 Nu_pred 9.64
C053 OR 0.5 Re 150: conv 0.0100 | cal 0.0423 | pred 0.0601 | field 0.0657 | -8.5 % | eta_fin 0.586 eta_o 0.596 | Phi_pred 0.779 Phi_eff_pred 0.971 Nu_pred 8.32
C054 OR 0.5 Re 250: conv 0.0095 | cal 0.0207 | pred 0.0380 | field 0.0419 | -9.4 % | eta_fin 0.569 eta_o 0.579 | Phi_pred 0.738 Phi_eff_pred 0.964 Nu_pred 8.98

## Fit (audit/refit_stats.csv, calibration row)
N                                                                34
C1                                                         0.236547
m                                                          1.358047
n                                                          0.443993
k                                                      dropped (B3)
C1_eff                                                     0.025349
m_eff                                                      1.867968
n_eff                                                      0.414196
Nu_fd                                                          7.85
C2                                                         0.875101
p                                                          0.465056
R_fixed                                                    0.007766
SE                C1 0.005021; m 0.01771; n 0.01116; C1_eff 0.00...
CI95              C1 +-0.01024; m +-0.03611; n +-0.02276; C1_eff...
objective         SSR phi 0.003081; SSR phi_eff 0.03384; SSR Nu ...
bounds            phi ([0.01, 0.05, -1], [20, 4, 1]); Nu ([0.05,...
phi_MAE_pp                                                   0.6452
phi_MAPE                                                     2.5717
Rth_MAPE                                                     4.5138
Rth_RMSE                                                     0.0048
Rth_maxerr                                                   0.0259
R2                                                           0.9137
phi_eff_MAE_pp                                               2.0295
Nu_MAPE                                                      3.5695
status                                                       FITTED
reason            fit on rows inside the envelope with thermal_d...

## Sealed pressure drop against Shah-London (audit/sealed_dp_check.csv): ratio at film viscosity [0.891, 0.968, 0.975, 0.978, 0.98, 0.983, 0.986, 0.99, 0.998]; at inlet viscosity [0.481, 0.785, 0.873, 0.915, 0.939, 0.952, 0.959, 0.968, 0.979]
