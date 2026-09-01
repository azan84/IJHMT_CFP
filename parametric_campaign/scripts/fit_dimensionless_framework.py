#!/usr/bin/env python3
"""
Scientific Analysis & Physics-Based Dimensionless Framework Fitting Engine.
Refined parallel hydraulic resistance model with finite base-flow area.
"""

import os
import sys
import json
import glob
import csv
import numpy as np
from scipy.optimize import curve_fit

def load_dataset(results_json_path):
    with open(results_json_path, 'r') as f:
        raw = json.load(f)
    if isinstance(raw, dict) and 'cases' in raw:
        cases = raw['cases']
    elif isinstance(raw, list):
        cases = raw
    else:
        cases = []
    return [c for c in cases if c.get('status') == 'COMPLETED_CONVERGED']

def fit_bypass_fraction(calibration_data):
    """
    Parallel Hydraulic Resistance Model with finite base-duct conductance:
    Phi_bypass = 1 / [ 1 + C1 * ((1 - OR + delta) / (OR + delta))^m * (Re / 100)^n * (Pr / 50)^k ]
    """
    ors, res, prs, phis = [], [], [], []
    pr_map = {'FC-40': 67.5, 'NOVEC-7100': 9.2, 'Mineral-Oil': 210.0, 'PG-Water': 45.0, 'EFL-1': 47.5, 'PAO-4': 72.0}
    
    for c in calibration_data:
        or_val = float(c.get('open_ratio', 0.0))
        re_val = float(c.get('reynolds_number', 100))
        fluid = c.get('fluid', 'FC-40')
        pr_val = pr_map.get(fluid, 67.5)
        phi_val = float(c.get('bypass_fraction_pct', 0.0)) / 100.0
        
        ors.append(or_val)
        res.append(re_val)
        prs.append(pr_val)
        phis.append(phi_val)
        
    ors = np.array(ors)
    res = np.array(res)
    prs = np.array(prs)
    phis = np.array(phis)
    
    def model(X, C1, m, n, k, delta):
        o, r, p = X
        # Geometric conductance ratio
        ratio = (1.0 - o + delta) / (o + delta)
        re_scale = r / 100.0
        pr_scale = p / 50.0
        denom = 1.0 + C1 * (ratio**m) * (re_scale**n) * (pr_scale**k)
        return np.clip(1.0 / denom, 0.0, 1.0)
        
    p0 = [0.45, 1.4, 0.12, -0.02, 0.15]
    bounds = ([0.01, 0.1, -1.0, -1.0, 0.01], [10.0, 4.0, 1.0, 1.0, 1.0])
    
    try:
        popt, _ = curve_fit(model, (ors, res, prs), phis, p0=p0, bounds=bounds, maxfev=20000)
    except Exception as e:
        print(f'[WARN] Curve fit failed: {e}')
        popt = p0
        
    return popt, (ors, res, prs, phis)

def fit_nusselt_number(calibration_data):
    """
    Thermally developing Graetz / Sieder-Tate Model:
    Nu = [ Nu_fd^3 + ( C2 * (Re_active * Pr * Dh/L)^p )^3 ]^(1/3)
    """
    re_actives, prs, nus = [], [], []
    pr_map = {'FC-40': 67.5, 'NOVEC-7100': 9.2, 'Mineral-Oil': 210.0, 'PG-Water': 45.0, 'EFL-1': 47.5, 'PAO-4': 72.0}
    
    for c in calibration_data:
        re_val = float(c.get('reynolds_number', 100))
        phi_val = float(c.get('bypass_fraction_pct', 0.0)) / 100.0
        re_act = max(1.0, re_val * (1.0 - phi_val))
        fluid = c.get('fluid', 'FC-40')
        pr_val = pr_map.get(fluid, 67.5)
        nu_val = float(c.get('nusselt_number', 4.0))
        
        re_actives.append(re_act)
        prs.append(pr_val)
        nus.append(nu_val)
        
    re_actives = np.array(re_actives)
    prs = np.array(prs)
    nus = np.array(nus)
    
    dh_l = 0.16875
    
    def model(X, nu_fd, C2, p):
        r_a, pr = X
        gz = r_a * pr * dh_l
        term_dev = C2 * (gz**p)
        return (nu_fd**3 + term_dev**3)**(1.0/3.0)
        
    p0 = [3.66, 1.86, 0.333]
    bounds = ([2.0, 0.5, 0.2], [6.0, 5.0, 0.5])
    
    try:
        popt, _ = curve_fit(model, (re_actives, prs), nus, p0=p0, bounds=bounds, maxfev=10000)
    except Exception:
        popt = p0
        
    return popt, (re_actives, prs, nus)

def evaluate_metrics(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    abs_errors = np.abs(y_pred - y_true)
    # MAPE with floor on denominator
    denom = np.where(np.abs(y_true) < 1.0, 1.0, np.abs(y_true))
    rel_errors = abs_errors / denom * 100.0
    
    mape = float(np.mean(rel_errors))
    max_err = float(np.max(rel_errors))
    rmse = float(np.sqrt(np.mean((y_pred - y_true)**2)))
    
    # R^2
    ss_res = np.sum((y_true - y_pred)**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    r2 = float(1.0 - ss_res / max(ss_tot, 1e-12))
    
    return {
        'R2': round(r2, 4),
        'MAPE_pct': round(mape, 2),
        'Max_Err_pct': round(max_err, 2),
        'RMSE': round(rmse, 4)
    }

def main():
    results_path = '/mnt/e/ijhmt-cfp/scratch_git/repo/parametric_campaign/results/parametric_results.json'
    if not os.path.exists(results_path):
        print(f'[ERROR] Results database not found at {results_path}')
        return
        
    data = load_dataset(results_path)
    print(f'[INFO] Loaded {len(data)} completed simulation cases.')
    
    cal_cases = [c for c in data if not c.get('is_out_of_sample', False) and c.get('fluid') == 'FC-40' and c.get('topology') == 'Plate-Fin']
    holdout_cases = [c for c in data if c.get('is_out_of_sample', True) or c.get('fluid') in ['EFL-1', 'PAO-4'] or c.get('topology') in ['Micro-Pin-Fin', 'Oblique-Fin']]
    
    print(f'[INFO] Calibration dataset: {len(cal_cases)} cases')
    print(f'[INFO] Out-of-sample holdout dataset: {len(holdout_cases)} cases')
    
    if len(cal_cases) < 5:
        print('[WARN] Insufficient calibration cases completed yet for full regression.')
        return
        
    popt_phi, (ors, res, prs, phis) = fit_bypass_fraction(cal_cases)
    print(f'[FIT] Bypass Fraction Parameters: C1={popt_phi[0]:.4f}, m={popt_phi[1]:.4f}, n={popt_phi[2]:.4f}, k={popt_phi[3]:.4f}, delta={popt_phi[4]:.4f}')
    
    o, r, p = ors, res, prs
    ratio = (1.0 - o + popt_phi[4]) / (o + popt_phi[4])
    re_scale = r / 100.0
    pr_scale = p / 50.0
    phi_pred_cal = 1.0 / (1.0 + popt_phi[0] * (ratio**popt_phi[1]) * (re_scale**popt_phi[2]) * (pr_scale**popt_phi[3]))
    cal_phi_metrics = evaluate_metrics(phis * 100.0, phi_pred_cal * 100.0)
    print(f'[METRICS] Calibration Phi_bypass: R2={cal_phi_metrics["R2"]}, MAPE={cal_phi_metrics["MAPE_pct"]}%, MaxErr={cal_phi_metrics["Max_Err_pct"]}%, RMSE={cal_phi_metrics["RMSE"]}')
    
    popt_nu, (re_acts, prs_nu, nus) = fit_nusselt_number(cal_cases)
    print(f'[FIT] Nusselt Number Parameters: Nu_fd={popt_nu[0]:.4f}, C2={popt_nu[1]:.4f}, p={popt_nu[2]:.4f}')
    
    dh_l = 0.16875
    nu_pred_cal = (popt_nu[0]**3 + (popt_nu[1] * (re_acts * prs_nu * dh_l)**popt_nu[2])**3)**(1.0/3.0)
    cal_nu_metrics = evaluate_metrics(nus, nu_pred_cal)
    print(f'[METRICS] Calibration Nu: R2={cal_nu_metrics["R2"]}, MAPE={cal_nu_metrics["MAPE_pct"]}%, MaxErr={cal_nu_metrics["Max_Err_pct"]}%, RMSE={cal_nu_metrics["RMSE"]}')

if __name__ == '__main__':
    main()
