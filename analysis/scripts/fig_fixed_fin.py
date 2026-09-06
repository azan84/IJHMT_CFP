#!/usr/bin/env python3
"""Figure 2: Fixed-fin clearance sweep vs the closure (cases F001-F004, Re_ch = 40).
Elsevier journal standard (greyscale-safe, 390 pt canvas width, 5.5-9.0 pt typography).
Generates out/fig_fixed_fin.png (300 dpi) and out/fig_fixed_fin.pdf.
"""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import types

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = HERE
ROOT = os.path.dirname(HERE)
DATA_LEDGER = os.path.join(ROOT, 'data', 'dataset_ledger_unitcell.csv')
DATA_STATS = os.path.join(ROOT, 'data', 'refit_stats.csv')
REF_DIR = os.path.join(ROOT, 'reference')

sys.path.insert(0, REF_DIR)
import refit_closures as rc

def save(fig, name):
    for ext in ('png', 'pdf'):
        p = os.path.join(FIGDIR, f'{name}.{ext}')
        fig.savefig(p, dpi=300)
    plt.close(fig)
    print(f'Wrote {name}.png and {name}.pdf to {FIGDIR}')

def main():
    stats = pd.read_csv(DATA_STATS).set_index('partition')
    fit = stats.loc['calibration']
    df = pd.read_csv(DATA_LEDGER)
    
    f_cases = df[df['case_id'].isin(['F001', 'F002', 'F003', 'F004'])].copy().sort_values('clearance_m')
    A_ = types.SimpleNamespace(k_fin=387.6, nu_fd=float(fit.Nu_fd))
    
    # 1. Discrete evaluations at the 4 cases
    phi_p = rc.phi_model((f_cases.OR.values.astype(float), f_cases.Re_recomputed_ch_Eq1_140mm.values.astype(float)),
                         fit.C1, fit.m, fit.n)
    gz = (f_cases.Re_recomputed_ch_Eq1_140mm.values.astype(float) *
          np.clip(1 - phi_p, 0, None) * f_cases.Pr.values * f_cases.D_h_over_L.values)
    phie = rc.phi_model((f_cases.OR.values.astype(float), f_cases.Re_recomputed_ch_Eq1_140mm.values.astype(float)),
                        fit.C1_eff, fit.m_eff, fit.n_eff)
    nu_p = rc.nu_model(gz, fit.C2, fit.p, fit.Nu_fd)
    rth_p = rc.rth_network(f_cases, nu_p, phie, fit.R_fixed, A_)
    
    f_cases['phi_pred'] = phi_p
    f_cases['rth_pred'] = rth_p
    
    # 2. Continuous closure curve across clearance c in [0, 20 mm]
    c_cont = np.linspace(0.0, 0.020, 250)
    Hf = 0.0209  # 20.9 mm fixed fin height
    or_cont = c_cont / (Hf + c_cont)
    re_val = 40.0
    pr_val = float(f_cases.Pr.mean())
    dhl_val = float(f_cases.D_h_over_L.mean())
    k_val = float(f_cases.k.mean())
    dh_val = float(f_cases.D_h.mean())
    aw_val = float(f_cases.A_wetted.mean())
    af_val = float(f_cases.A_fin_full_m2.mean())
    mf_val = float(f_cases.m_full_kg_s.mean())
    cp_val = float(f_cases.cp_inlet.mean())
    tf_val = float(f_cases.t_fin.mean())
    
    phi_cont = rc.phi_model((or_cont, np.full_like(or_cont, re_val)), fit.C1, fit.m, fit.n)
    phie_cont = rc.phi_model((or_cont, np.full_like(or_cont, re_val)), fit.C1_eff, fit.m_eff, fit.n_eff)
    gz_cont = re_val * np.clip(1 - phi_cont, 0, None) * pr_val * dhl_val
    nu_cont = rc.nu_model(gz_cont, fit.C2, fit.p, fit.Nu_fd)
    
    S_cont = pd.DataFrame(dict(
        k=np.full_like(c_cont, k_val),
        D_h=np.full_like(c_cont, dh_val),
        A_wetted=np.full_like(c_cont, aw_val),
        A_fin_full_m2=np.full_like(c_cont, af_val),
        t_fin=np.full_like(c_cont, tf_val),
        H_fin=np.full_like(c_cont, Hf),
        m_full_kg_s=np.full_like(c_cont, mf_val),
        cp_inlet=np.full_like(c_cont, cp_val)
    ))
    rth_cont = rc.rth_network(S_cont, nu_cont, phie_cont, fit.R_fixed, A_)
    
    # 390 pt width canonical single-column width (STYLE_GUIDE.md Section 1.10)
    width_in = 390.0 / 72.0
    height_in = 2.60
    
    plt.rcParams.update({
        'font.size': 7.0,
        'axes.labelsize': 7.5,
        'legend.fontsize': 5.8,
        'xtick.labelsize': 6.5,
        'ytick.labelsize': 6.5,
        'font.family': 'sans-serif',
        'mathtext.fontset': 'dejavusans',
        'axes.linewidth': 0.7,
        'xtick.major.width': 0.6,
        'ytick.major.width': 0.6,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.top': True,
        'ytick.right': True
    })
    
    fig, axes = plt.subplots(1, 2, figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.12, right=0.96, bottom=0.18, top=0.90, wspace=0.34)
    
    c_mm = f_cases.clearance_m.values * 1e3
    c_cont_mm = c_cont * 1e3
    acc = f_cases.accepted.values
    
    # --- PANEL (a): Bypass fraction vs clearance ---
    ax = axes[0]
    # Outside validity envelope shading (c > 5 mm)
    ax.axvspan(5.0, 20.8, color='0.96', zorder=0)
    ax.axvline(5.0, color='0.75', ls='--', lw=0.8, zorder=1)
    ax.text(5.4, 15, 'Validity limit\n($c = 5$ mm)', fontsize=5.8, color='0.45', va='bottom')
    
    # Closure prediction curve & discrete points
    ax.plot(c_cont_mm, 100 * phi_cont, '-', color='0.35', lw=1.2, zorder=2, label='Closure prediction (Eq. 23)')
    ax.plot(c_mm, 100 * phi_p, 'o', color='0.35', mfc='white', mew=1.1, ms=4.8, zorder=3, label='Closure at cases')
    
    # Field points: accepted (filled circle) vs outside envelope (grey 'x')
    ax.plot(c_mm[acc], 100 * f_cases.Phi_in.values[acc], 'o', color='k', mfc='k', ms=4.8, zorder=4, label='Field (accepted envelope)')
    ax.plot(c_mm[~acc], 100 * f_cases.Phi_in.values[~acc], 'x', color='0.45', mew=1.5, ms=5.5, zorder=4, label='Field (outside envelope)')
    
    # Annotate case IDs
    case_names = ['F001', 'F002', 'F003', 'F004']
    offsets_a = [(5.0, 3.0), (0.0, -10.0), (0.0, -10.0), (-1.0, -9.5)]
    for i, cid in enumerate(case_names):
        ax.annotate(cid, (c_mm[i], 100 * f_cases.Phi_in.values[i]),
                    xytext=offsets_a[i], textcoords='offset points',
                    fontsize=6.0, color='k', ha='left' if i == 0 else 'center', fontweight='bold')
        
    ax.set_xlabel('Clearance, $c$ [mm]', fontsize=7.5)
    ax.set_ylabel(r'Bypass fraction, $\Phi_{\mathrm{bypass}}$ [%]', fontsize=7.5)
    ax.set_xlim(-0.8, 20.8)
    ax.set_ylim(-5, 105)
    ax.grid(True, ls=':', lw=0.5, color='0.80')
    ax.set_title('(a)', loc='left', fontweight='bold', fontsize=8.0)
    ax.legend(frameon=False, loc='upper left', fontsize=5.6, handletextpad=0.25, borderaxespad=0.25)
    
    # --- PANEL (b): Thermal resistance vs clearance ---
    ax = axes[1]
    ax.axvspan(5.0, 20.8, color='0.96', zorder=0)
    ax.axvline(5.0, color='0.75', ls='--', lw=0.8, zorder=1)
    
    ax.plot(c_cont_mm, rth_cont, '-', color='0.35', lw=1.2, zorder=2, label='Closure prediction')
    ax.plot(c_mm, rth_p, 'o', color='0.35', mfc='white', mew=1.1, ms=4.8, zorder=3, label='Closure at cases')
    ax.plot(c_mm[acc], f_cases.R_th_K_W.values[acc], 'o', color='k', mfc='k', ms=4.8, zorder=4, label='Field (accepted)')
    ax.plot(c_mm[~acc], f_cases.R_th_K_W.values[~acc], 'x', color='0.45', mew=1.5, ms=5.5, zorder=4, label='Field (outside envelope)')
    
    # Validity limit text placed at lower left near x=5.3
    ax.text(5.4, 0.008, 'Validity limit\n($c = 5$ mm)', fontsize=5.8, color='0.45', va='bottom')
    
    # Divergence callout at F004 (c = 19.05 mm)
    # Field: 0.1186, Closure: 0.2373 -> +100%
    ax.annotate('Divergence: +100%\n(+0.119 K/W over-pred.)',
                xy=(19.05, rth_p[-1]), xytext=(17.5, 0.185),
                arrowprops=dict(arrowstyle='->', lw=0.7, color='0.2', shrinkB=4),
                fontsize=5.6, color='0.15', ha='right', va='top')
    
    # Dotted connector between field and closure at F004
    ax.plot([19.05, 19.05], [f_cases.R_th_K_W.values[-1], rth_p[-1]], ':', color='0.5', lw=0.8, zorder=2)
    
    # Annotate case IDs
    offsets_b = [(5.0, 3.0), (0.0, 7.0), (0.0, -11.0), (0.0, -11.0)]
    for i, cid in enumerate(case_names):
        ax.annotate(cid, (c_mm[i], f_cases.R_th_K_W.values[i]),
                    xytext=offsets_b[i], textcoords='offset points',
                    fontsize=6.0, color='k', ha='left' if i == 0 else 'center', fontweight='bold')
        
    ax.set_xlabel('Clearance, $c$ [mm]', fontsize=7.5)
    ax.set_ylabel(r'Thermal resistance, $R_{\mathrm{th}}$ [$\mathrm{K\cdot W^{-1}}$]', fontsize=7.5, labelpad=2.0)
    ax.set_xlim(-0.8, 20.8)
    ax.set_ylim(0.0, 0.26)
    ax.grid(True, ls=':', lw=0.5, color='0.80')
    ax.set_title('(b)', loc='left', fontweight='bold', fontsize=8.0)
    ax.legend(frameon=False, loc='upper left', fontsize=5.6, handletextpad=0.25, borderaxespad=0.25)
    
    save(fig, 'fig_fixed_fin')
    
    print('Figure 2 Data Ranges plotted:')
    print(f'  Clearance [mm]: [{c_mm.min():.2f}, {c_mm.max():.2f}] (F001: 0.00, F002: 5.00, F003: 10.00, F004: 19.05)')
    print(f'  Field Phi [%]: [{100*f_cases.Phi_in.min():.4f}, {100*f_cases.Phi_in.max():.4f}]')
    print(f'  Closure Phi [%]: [{100*phi_p.min():.4f}, {100*phi_p.max():.4f}] (continuous: [{100*phi_cont.min():.4f}, {100*phi_cont.max():.4f}])')
    print(f'  Field R_th [K/W]: [{f_cases.R_th_K_W.min():.6f}, {f_cases.R_th_K_W.max():.6f}]')
    print(f'  Closure R_th [K/W]: [{rth_p.min():.6f}, {rth_p.max():.6f}] (continuous: [{rth_cont.min():.6f}, {rth_cont.max():.6f}])')

if __name__ == '__main__':
    main()
