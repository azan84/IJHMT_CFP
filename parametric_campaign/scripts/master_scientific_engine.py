#!/usr/bin/env python3
"""
Master Scientific Analysis, Verification, and Exact Post-Processing Engine for IJHMT Paper-5.
Enforces 100% SI consistency, exact physics-constrained closures, thermal decomposition,
feasibility mapping, and programmatic figure/table generation.
"""

import os
import sys
import json
import csv
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Thermophysical fluid properties at reference 25 C
FLUID_DB = {
    'FC-40': {'rho': 1855.0, 'cp': 1052.0, 'k': 0.0654, 'mu': 3.50e-3, 'nu': 1.887e-6, 'Pr': 56.3},
    'PAO-4': {'rho': 795.0, 'cp': 2210.0, 'k': 0.1430, 'mu': 1.42e-2, 'nu': 1.786e-5, 'Pr': 219.5},
    'EFL-1': {'rho': 1889.0, 'cp': 1165.0, 'k': 0.0680, 'mu': 2.77e-3, 'nu': 1.466e-6, 'Pr': 47.46}
}

CHASSIS = {
    'height_m': 0.04445,
    'width_m': 0.140,
    'length_m': 0.400,
    'dh_m': (2 * 0.04445 * 0.140) / (0.04445 + 0.140), # 0.0675 m
    'area_m2': 0.04445 * 0.140 # 0.006223 m^2
}

def load_all_cases():
    json_path = '/mnt/e/ijhmt-cfp/Paper-5/parametric_campaign/results/parametric_results.json'
    with open(json_path) as f:
        data = json.load(f)
    cases = data['cases']
    
    # Enrich and strictly recompute all derived thermodynamic and hydraulic metrics
    for c in cases:
        q_lpm = float(c['flow_rate_LPM'])
        q_m3_s = q_lpm / 60000.0
        dp_pa = float(c['pressure_drop_total_Pa'])
        r_th = float(c['thermal_resistance_K_W'])
        t_max = float(c['T_chip_max_C'])
        
        # Exact SI Pumping Power
        w_pump_w = q_m3_s * dp_pa
        w_pump_uW = w_pump_w * 1e6
        c['W_pump_W'] = w_pump_w
        c['W_pump_uW'] = w_pump_uW
        
        # Exact SI Figure of Merit
        if w_pump_w > 1e-12 and r_th > 1e-6:
            c['FOM_SI_K_inv_W_inv'] = 1.0 / (r_th * w_pump_w)
        else:
            c['FOM_SI_K_inv_W_inv'] = 0.0
            
        # Thermal Resistance Decomposition
        # R_total = R_TIM + R_spread + R_conv
        r_tim = 0.035
        r_spread = 0.025
        r_conv = max(0.001, r_th - r_tim - r_spread)
        c['R_TIM_K_W'] = r_tim
        c['R_spread_K_W'] = r_spread
        c['R_conv_K_W'] = r_conv
        c['f_conv_pct'] = (r_conv / r_th) * 100.0
        
        # Operating Regime Classification
        if t_max <= 85.0:
            c['regime'] = 'FEASIBLE_SAFE'
        elif t_max <= 115.0:
            c['regime'] = 'MARGINAL_THROTTLING'
        else:
            c['regime'] = 'FAILURE_UNREALIZABLE'
            
    return cases

def fit_physics_constrained_models(cal_cases):
    """
    Fit physics-constrained models strictly enforcing physical limiting bounds.
    """
    ors = np.array([float(c['open_ratio']) for c in cal_cases])
    res = np.array([float(c['reynolds_number']) for c in cal_cases])
    prs = np.array([FLUID_DB[c['fluid']]['Pr'] for c in cal_cases])
    phis_true = np.array([float(c['bypass_fraction_pct'])/100.0 for c in cal_cases])
    nus_true = np.array([float(c['nusselt_number']) for c in cal_cases])
    
    # 1. Physics-Constrained Bypass Model:
    # Phi = 1 / [ 1 + C1 * ((1 - OR) / (OR + 1e-5))^m * (Re/100)^n * (Pr/50)^k ]
    # lim_{OR->0} Phi = 0, lim_{OR->1} Phi = 1
    def phi_model(X, C1, m, n, k):
        o, r, p = np.array(X[0], dtype=float), np.array(X[1], dtype=float), np.array(X[2], dtype=float)
        eps = 1e-4
        ratio = np.maximum(0.0, 1.0 - o) / np.maximum(eps, o)
        re_s = r / 100.0
        pr_s = p / 50.0
        denom = 1.0 + C1 * (ratio**m) * (re_s**n) * (pr_s**k)
        return 1.0 / denom
        
    p0_phi = [1.25, 1.48, 0.05, -0.02]
    bounds_phi = ([0.01, 0.1, -1.0, -1.0], [20.0, 4.0, 1.0, 1.0])
    popt_phi, _ = curve_fit(phi_model, (ors, res, prs), phis_true, p0=p0_phi, bounds=bounds_phi, maxfev=20000)
    
    # 2. Thermally Developing Graetz Nusselt Model:
    dh_l = 0.16875
    cal_phi_p = phi_model((ors, res, prs), *popt_phi)
    re_acts = np.maximum(1.0, res * (1.0 - cal_phi_p))
    
    def nu_model(X, nu_fd, C2, p):
        r_a, pr = np.array(X[0], dtype=float), np.array(X[1], dtype=float)
        gz = r_a * pr * dh_l
        return (nu_fd**3 + (C2 * (gz**p))**3)**(1.0/3.0)
        
    p0_nu = [3.66, 1.84, 0.333]
    bounds_nu = ([2.0, 0.1, 0.1], [6.0, 5.0, 0.6])
    popt_nu, _ = curve_fit(nu_model, (re_acts, prs), nus_true, p0=p0_nu, bounds=bounds_nu, maxfev=10000)
    
    return popt_phi, popt_nu, phi_model, nu_model

def evaluate_statistical_metrics(cases, popt_phi, popt_nu, phi_model, nu_model):
    """
    Evaluate statistical accuracy without data leakage.
    """
    subsets = {
        'Calibration (FC-40, Plate-Fin)': [c for c in cases if c.get('campaign_group') == 'Baseline_OpenRatio_Reynolds'],
        'Holdout Coolant: PAO-4 (Pr=219.5)': [c for c in cases if c.get('fluid') == 'PAO-4' and c.get('topology') == 'Plate-Fin'],
        'Holdout Coolant: EFL-1 (Pr=47.5)': [c for c in cases if c.get('fluid') == 'EFL-1' and c.get('topology') == 'Plate-Fin'],
        'Holdout Topology: Micro-Pin-Fin': [c for c in cases if c.get('topology') == 'Micro-Pin-Fin'],
        'Holdout Topology: Oblique-Fin': [c for c in cases if c.get('topology') == 'Oblique-Fin'],
        'Holdout Thermal Load (300-1200 W)': [c for c in cases if c.get('campaign_group') == 'ThermalLoad_Sensitivity'],
        'Holdout Cross-Combinations': [c for c in cases if c.get('campaign_group') == 'OutOfSample_Validation']
    }
    
    # Calibrate fixed thermal resistance scale factor ON CALIBRATION SET ONLY
    cal_cases = subsets['Calibration (FC-40, Plate-Fin)']
    cal_ors = np.array([float(c['open_ratio']) for c in cal_cases])
    cal_res = np.array([float(c['reynolds_number']) for c in cal_cases])
    cal_prs = np.array([FLUID_DB[c['fluid']]['Pr'] for c in cal_cases])
    cal_phi_p = phi_model((cal_ors, cal_res, cal_prs), *popt_phi)
    cal_re_acts = np.maximum(1.0, cal_res * (1.0 - cal_phi_p))
    cal_nu_p = nu_model((cal_re_acts, cal_prs), *popt_nu)
    cal_h_p = cal_nu_p * 0.0654 / (2.0 * 0.0018)
    cal_rth_raw = 0.035 + 0.025 + 1.0 / (0.85 * cal_h_p * 0.065)
    cal_rth_true = np.array([float(c['thermal_resistance_K_W']) for c in cal_cases])
    fixed_scale_fac = float(np.mean(cal_rth_true) / np.mean(cal_rth_raw))
    
    results_summary = []
    
    for name, sub in subsets.items():
        ors = np.array([float(c['open_ratio']) for c in sub])
        res = np.array([float(c['reynolds_number']) for c in sub])
        prs = np.array([FLUID_DB[c['fluid']]['Pr'] for c in sub])
        k_fluids = np.array([FLUID_DB[c['fluid']]['k'] for c in sub])
        phi_t = np.array([float(c['bypass_fraction_pct']) for c in sub])
        rth_t = np.array([float(c['thermal_resistance_K_W']) for c in sub])
        nu_t = np.array([float(c['nusselt_number']) for c in sub])
        
        # Predictions
        phi_p = phi_model((ors, res, prs), *popt_phi) * 100.0
        re_act = np.maximum(1.0, res * (1.0 - phi_p/100.0))
        nu_p = nu_model((re_act, prs), *popt_nu)
        
        # Physical un-leaked R_th prediction using calibration-fixed scale factor
        h_p = nu_p * k_fluids / (2.0 * 0.0018)
        rth_p = (0.035 + 0.025 + 1.0 / (0.85 * h_p * 0.065)) * fixed_scale_fac
        
        # Bypass MAE and masked MAPE (OR >= 0.10)
        phi_mae = float(np.mean(np.abs(phi_p - phi_t)))
        mask_or = ors >= 0.10
        if np.sum(mask_or) > 0:
            phi_mape_unsealed = float(np.mean(np.abs(phi_p[mask_or] - phi_t[mask_or]) / phi_t[mask_or]) * 100.0)
        else:
            phi_mape_unsealed = 0.0
            
        # Nu MAPE and R^2
        nu_mape = float(np.mean(np.abs(nu_p - nu_t) / np.maximum(1.0, nu_t)) * 100.0)
        ss_res_nu = np.sum((nu_t - nu_p)**2)
        ss_tot_nu = np.sum((nu_t - np.mean(nu_t))**2)
        nu_r2 = float(1.0 - ss_res_nu / max(ss_tot_nu, 1e-12))
        
        # R_th MAPE and R^2
        rth_mape = float(np.mean(np.abs(rth_p - rth_t) / rth_t) * 100.0)
        ss_res_rth = np.sum((rth_t - rth_p)**2)
        ss_tot_rth = np.sum((rth_t - np.mean(rth_t))**2)
        rth_r2 = float(1.0 - ss_res_rth / max(ss_tot_rth, 1e-12))
        
        results_summary.append({
            'Partition': name,
            'Sample_N': len(sub),
            'Phi_MAE_pp': round(phi_mae, 2),
            'Phi_MAPE_OR_ge_01': round(phi_mape_unsealed, 2),
            'Nu_MAPE': round(nu_mape, 2),
            'Nu_R2': round(nu_r2, 4),
            'Rth_MAPE': round(rth_mape, 2),
            'Rth_R2': round(rth_r2, 4)
        })
        
    return results_summary, fixed_scale_fac

def main():
    cases = load_all_cases()
    print(f'[INFO] Loaded and enriched {len(cases)} simulation cases.')
    
    cal_cases = [c for c in cases if c.get('campaign_group') == 'Baseline_OpenRatio_Reynolds']
    popt_phi, popt_nu, phi_model, nu_model = fit_physics_constrained_models(cal_cases)
    
    print(f'[FITTED] Physics-Constrained Bypass: C1={popt_phi[0]:.4f}, m={popt_phi[1]:.4f}, n={popt_phi[2]:.4f}, k={popt_phi[3]:.4f}')
    print(f'         Boundary Checks: Phi(0) = {phi_model((np.array([0.0]), np.array([100]), np.array([50])), *popt_phi)[0]*100:.4f}%, Phi(1) = {phi_model((np.array([1.0]), np.array([100]), np.array([50])), *popt_phi)[0]*100:.4f}%')
    print(f'[FITTED] Developing Graetz Nu: Nu_fd={popt_nu[0]:.4f}, C2={popt_nu[1]:.4f}, p={popt_nu[2]:.4f}')
    
    stats_summary, fixed_scale_fac = evaluate_statistical_metrics(cases, popt_phi, popt_nu, phi_model, nu_model)
    
    print('\n' + '='*90)
    print('      RIGOROUS UN-LEAKED STATISTICAL VALIDATION & HOLDOUT SUMMARY')
    print('='*90)
    for s in stats_summary:
        print(f"[*] {s['Partition']} (N={s['Sample_N']}):")
        print(f"    - Bypass Split:   MAE = {s['Phi_MAE_pp']} pp | MAPE (OR>=0.1) = {s['Phi_MAPE_OR_ge_01']}%")
        print(f"    - Nusselt Nu:     MAPE = {s['Nu_MAPE']}% | R2 = {s['Nu_R2']}")
        print(f"    - Resistance Rth: MAPE = {s['Rth_MAPE']}% | R2 = {s['Rth_R2']}")
    print('='*90 + '\n')
    
    # Save CSV
    out_csv = '/mnt/e/ijhmt-cfp/Paper-5/audit/final_holdout_validation_statistics.csv'
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(stats_summary[0].keys()))
        writer.writeheader()
        for row in stats_summary:
            writer.writerow(row)
    print(f'[SUCCESS] Wrote exact un-leaked stats to {out_csv}')

if __name__ == '__main__':
    main()
