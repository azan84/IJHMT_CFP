#!/usr/bin/env python3
"""Figure 3: Parity plot extended to all accepted partitions (N = 49).
Elsevier journal standard (greyscale-safe, 390 pt canvas width, 5.5-9.0 pt typography).
Generates out/fig_parity_all.png (300 dpi) and out/fig_parity_all.pdf.
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
    L = pd.read_csv(DATA_LEDGER)
    L['acc'] = L.accepted.astype(str).str.lower().isin(['true', '1', 'y', 'yes'])
    
    A_ = types.SimpleNamespace(k_fin=387.6, nu_fd=float(fit.Nu_fd))
    
    def predict(S):
        phi_p = rc.phi_model((S.OR.values.astype(float), S.Re_recomputed_ch_Eq1_140mm.values.astype(float)),
                             fit.C1, fit.m, fit.n)
        gz = (S.Re_recomputed_ch_Eq1_140mm.values.astype(float) *
              np.clip(1 - phi_p, 0, None) * S.Pr.values * S.D_h_over_L.values)
        phie = rc.phi_model((S.OR.values.astype(float), S.Re_recomputed_ch_Eq1_140mm.values.astype(float)),
                            fit.C1_eff, fit.m_eff, fit.n_eff)
        nu_p = rc.nu_model(gz, fit.C2, fit.p, fit.Nu_fd)
        rth_p = rc.rth_network(S, nu_p, phie, fit.R_fixed, A_)
        return phi_p, nu_p, rth_p
    
    # 390 pt width canonical single-column width (STYLE_GUIDE.md Section 1.10)
    width_in = 390.0 / 72.0
    height_in = 2.25
    
    plt.rcParams.update({
        'font.size': 7.0,
        'axes.labelsize': 7.2,
        'legend.fontsize': 5.5,
        'xtick.labelsize': 6.2,
        'ytick.labelsize': 6.2,
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
    
    fig, ax = plt.subplots(1, 3, figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.22, top=0.88, wspace=0.38)
    
    # Five distinct partitions with greyscale-safe markers
    groups = [
        ('calibration', 'o', 'k', 'none', 'calibration'),
        ('holdout_EFL-1', 's', '0.35', 'none', 'holdout EFL-1'),
        ('holdout_thermal_load', '^', '0.35', '0.40', 'holdout thermal load'),
        ('cross_combinations', 'D', '0.35', 'none', 'cross combinations'),
        ('fixed_fin_sweep', 'v', 'k', '0.75', 'fixed fin sweep')
    ]
    
    partition_ranges = {}
    total_pts = 0
    
    for name, mk, col, mfc, lab in groups:
        S = L[L.acc & (L.partitions.astype(str) == name)]
        if S.empty:
            continue
        total_pts += len(S)
        pp, nn, rr = predict(S)
        
        partition_ranges[name] = {
            'N': len(S),
            'phi_field': (float(100*S.phi_field.min()), float(100*S.phi_field.max())),
            'phi_pred': (float(100*pp.min()), float(100*pp.max())),
            'nu_field': (float(S.Nu_field.min()), float(S.Nu_field.max())),
            'nu_pred': (float(nn.min()), float(nn.max())),
            'rth_field': (float(S.Rth_field.min()), float(S.Rth_field.max())),
            'rth_pred': (float(rr.min()), float(rr.max()))
        }
        
        ax[0].plot(100 * S.phi_field, 100 * pp, mk, color=col, mfc=mfc, ms=3.8, mew=0.9, label=lab, zorder=3)
        ax[1].plot(S.Nu_field, nn, mk, color=col, mfc=mfc, ms=3.8, mew=0.9, label=lab, zorder=3)
        ax[2].plot(S.Rth_field, rr, mk, color=col, mfc=mfc, ms=3.8, mew=0.9, label=lab, zorder=3)
        
    panels = [
        (ax[0], r'$\Phi_{\mathrm{bypass}}$ [%]', (0.0, 100.0)),
        (ax[1], r'$\mathrm{Nu}$ [-]', (7.0, 14.0)),
        (ax[2], r'$R_{\mathrm{th}}$ [$\mathrm{K\cdot W^{-1}}$]', (0.012, 0.095))
    ]
    
    for a, lab, lims in panels:
        lo, hi = lims
        m = [lo, hi]
        # 1:1 parity line
        a.plot(m, m, '-', color='0.5', lw=0.7, zorder=1)
        # +-20% error bound guide lines
        a.plot(m, [1.2 * v for v in m], ':', color='0.6', lw=0.6, zorder=1)
        a.plot(m, [0.8 * v for v in m], ':', color='0.6', lw=0.6, zorder=1)
        
        a.set_xlabel(f'field, {lab}', fontsize=7.2)
        a.set_ylabel(f'closure, {lab}', fontsize=7.2, labelpad=2.0)
        a.set_xlim(m)
        a.set_ylim(m)
        a.grid(True, ls=':', lw=0.5, color='0.80')
        
    ax[0].legend(frameon=False, fontsize=5.5, loc='upper left', handletextpad=0.25, borderaxespad=0.25, labelspacing=0.25)
    for a, t in zip(ax, ('(a)', '(b)', '(c)')):
        a.set_title(t, fontsize=8.0, loc='left', fontweight='bold')
        
    save(fig, 'fig_parity_all')
    
    print(f'Figure 3 Total accepted cases plotted: N = {total_pts}')
    print('Figure 3 Data Ranges plotted per partition:')
    for part, r_dict in partition_ranges.items():
        print(f'  [{part}] N = {r_dict["N"]}')
        print(f'    Phi [%]: field [{r_dict["phi_field"][0]:.2f}, {r_dict["phi_field"][1]:.2f}], pred [{r_dict["phi_pred"][0]:.2f}, {r_dict["phi_pred"][1]:.2f}]')
        print(f'    Nu [-]:  field [{r_dict["nu_field"][0]:.3f}, {r_dict["nu_field"][1]:.3f}], pred [{r_dict["nu_pred"][0]:.3f}, {r_dict["nu_pred"][1]:.3f}]')
        print(f'    Rth [K/W]: field [{r_dict["rth_field"][0]:.5f}, {r_dict["rth_field"][1]:.5f}], pred [{r_dict["rth_pred"][0]:.5f}, {r_dict["rth_pred"][1]:.5f}]')

if __name__ == '__main__':
    main()
