#!/usr/bin/env python3
"""Figure 1: Coolant comparison (FC-40 vs withheld EFL-1 at OR = 0.1).
Elsevier journal standard (greyscale-safe, 390 pt canvas width, 5.5-9.0 pt typography).
Generates out/fig_coolant_comparison.png (300 dpi) and out/fig_coolant_comparison.pdf.
"""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = HERE
DATA_PATH = os.path.join(os.path.dirname(HERE), 'data', 'coolant_comparison.csv')

def save(fig, name):
    for ext in ('png', 'pdf'):
        p = os.path.join(FIGDIR, f'{name}.{ext}')
        fig.savefig(p, dpi=300)
    plt.close(fig)
    print(f'Wrote {name}.png and {name}.pdf to {FIGDIR}')

def main():
    df = pd.read_csv(DATA_PATH)
    
    # 390 pt width canonical single-column width (STYLE_GUIDE.md Section 1.10)
    width_in = 390.0 / 72.0
    height_in = 2.65
    
    plt.rcParams.update({
        'font.size': 7.0,
        'axes.labelsize': 7.2,
        'legend.fontsize': 5.8,
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
    
    bases = ['matched Re_ch', 'matched Q_full_sink_LPM', 'matched W_pump_W']
    x_labels = ['Matched\n' + r'$\mathrm{Re}_{ch}$', 'Matched\n' + r'$Q$', 'Matched\n' + r'$W_{\mathrm{pump}}$']
    
    fig, axes = plt.subplots(1, 3, figsize=(width_in, height_in))
    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.28, top=0.90, wspace=0.46)
    
    metrics = [
        ('Phi_in', r'$\Phi_{\mathrm{bypass}}$ [%]', 100.0, (-0.5, 2.5), (15.0, 16.5)),
        ('R_th_K_W', r'$R_{\mathrm{th}}$ [$\mathrm{K\cdot W^{-1}}$]', 1.0, (-0.5, 2.5), (0.0168, 0.0180)),
        ('W_pump_W', r'$W_{\mathrm{pump}}$ [W]', 1.0, (-0.5, 2.5), (0.45, 1.15))
    ]
    
    x = np.arange(len(bases))
    
    data_ranges = {}
    
    for i, (col, ylabel, scale, xlim, ylim) in enumerate(metrics):
        ax = axes[i]
        fc_vals = []
        efl_vals = []
        for b in bases:
            sub = df[df.basis == b]
            fc = sub[sub.fluid.str.contains('FC-40')][col].values[0] * scale
            efl = sub[sub.fluid == 'EFL-1'][col].values[0] * scale
            fc_vals.append(fc)
            efl_vals.append(efl)
            
        fc_vals = np.array(fc_vals)
        efl_vals = np.array(efl_vals)
        data_ranges[col] = {
            'fc40_min': float(fc_vals.min()),
            'fc40_max': float(fc_vals.max()),
            'efl1_val': float(efl_vals[0]),
            'all_min': float(min(fc_vals.min(), efl_vals.min())),
            'all_max': float(max(fc_vals.max(), efl_vals.max()))
        }
        
        # Vertical guide lines for each basis category
        for xi in x:
            ax.axvline(xi, color='0.92', lw=0.7, zorder=0)
            # Dotted connector between the paired points
            ax.plot([xi - 0.15, xi + 0.15], [fc_vals[xi], efl_vals[xi]], ':', color='0.6', lw=0.7, zorder=1)
            
        # Markers: FC-40 open circle, EFL-1 filled dark-grey square (greyscale safe)
        p1, = ax.plot(x - 0.15, fc_vals, 'o', color='k', mfc='white', mew=1.1, ms=4.6, zorder=3, label='FC-40 (interpolated*)')
        p2, = ax.plot(x + 0.15, efl_vals, 's', color='k', mfc='0.35', mew=1.0, ms=4.6, zorder=3, label='EFL-1 (withheld)')
        
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, fontsize=6.2)
        ax.set_ylabel(ylabel, fontsize=7.2, labelpad=2.5)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(True, ls=':', lw=0.5, axis='y', color='0.80')
        ax.set_title(f'({chr(97+i)})', loc='left', fontweight='bold', fontsize=8.0)
    
    # Legend in panel (a)
    axes[0].legend(frameon=False, loc='upper left', fontsize=5.6, handletextpad=0.25, borderaxespad=0.25)
    
    # Embedded explanatory note wrapped cleanly into 2 lines
    note_text = (
        r'*Note: FC-40 at matched $Q$ (53.4 LPM) and $W_{\mathrm{pump}}$ (1.03 W) interpolated onto EFL-1 operating points.' + '\n' +
        r'EFL-1 is the withheld-coolant validation partition ($\mathrm{OR}=0.10$, $\mathrm{Re}_{ch}=150$).'
    )
    fig.text(0.5, 0.03, note_text, ha='center', va='bottom', fontsize=5.8, color='0.25', style='italic', linespacing=1.3)
    
    save(fig, 'fig_coolant_comparison')
    
    print('Figure 1 Data Ranges plotted:')
    for k, v in data_ranges.items():
        print(f'  {k}: FC-40 [{v["fc40_min"]:.6f}, {v["fc40_max"]:.6f}], EFL-1 = {v["efl1_val"]:.6f}, Overall = [{v["all_min"]:.6f}, {v["all_max"]:.6f}]')

if __name__ == '__main__':
    main()
