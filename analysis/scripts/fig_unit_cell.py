#!/usr/bin/env python3
"""Schematic of the spanwise-periodic conjugate unit cell (geometry only, no results).
Dimensions from cfd/unit_cell_probe/make_case.py. Output figures/fig_unit_cell.png/.pdf."""
import os, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt; from matplotlib.patches import Rectangle
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s,tf,Hb,Hc=0.95,0.25,4.5,44.45; ORs=[0.0,0.5]
fig,ax=plt.subplots(1,3,figsize=(7.2,3.0),dpi=300,gridspec_kw=dict(width_ratios=[1,1,2.2]))
for a,OR in zip(ax[:2],ORs):
    Hf=(Hc-Hb)*(1-OR)
    a.add_patch(Rectangle((0,0),(s+tf)/2,Hb,fc="0.7",ec="k",lw=0.8,hatch="//"))        # base
    a.add_patch(Rectangle((s/2,Hb),tf/2,Hf,fc="0.7",ec="k",lw=0.8,hatch="//"))            # half fin
    a.add_patch(Rectangle((0,Hb),s/2,Hf,fc="white",ec="k",lw=0.5))                         # half channel
    if OR>0: a.add_patch(Rectangle((0,Hb+Hf),(s+tf)/2,Hc-Hb-Hf,fc="white",ec="k",lw=0.5,ls="--"))  # clearance
    a.plot([0,0],[0,Hc],"k:",lw=0.8); a.plot([(s+tf)/2]*2,[0,Hc],"k:",lw=0.8)
    a.set_xlim(-0.1,(s+tf)/2+0.1); a.set_ylim(0,Hc); a.set_aspect(0.012); a.set_xticks([0,s/2,(s+tf)/2]); a.set_xticklabels(["0","s/2","p/2"],fontsize=7)
    a.set_yticks([0,Hb,Hb+Hf,Hc]); a.set_yticklabels(["0",r"$H_b$",r"$H_b+H_{fin}$",r"$H_c$"] if OR>0 else ["0",r"$H_b$","",r"$H_c$"],fontsize=7)
    a.set_title("OR = %.1f"%OR,fontsize=9); a.set_xlabel("y (symmetry planes at 0 and p/2)",fontsize=7)
# side view
a=ax[2]; L,Lin,Lout=118,60,80
a.add_patch(Rectangle((Lin,0),L,Hb,fc="0.7",ec="k",lw=0.8,hatch="//")); a.add_patch(Rectangle((Lin,Hb),L,(Hc-Hb)*0.5,fc="0.85",ec="k",lw=0.5))
a.add_patch(Rectangle((0,Hb),Lin+L+Lout,Hc-Hb,fc="none",ec="k",lw=0.8))
a.annotate("",xy=(Lin-5,25),xytext=(5,25),arrowprops=dict(arrowstyle="->",lw=0.8)); a.text(8,28,"inlet",fontsize=7)
a.annotate("heated base, q'' on the underside",xy=(Lin+L/2,0),xytext=(Lin+L/2,-9),ha="center",fontsize=6.5,arrowprops=dict(arrowstyle="->",lw=0.6),annotation_clip=False)
a.text(Lin+L/2,Hb+(Hc-Hb)*0.25,"fin (solid)",ha="center",va="center",fontsize=6.5); a.text(Lin+L/2,Hb+(Hc-Hb)*0.78,"clearance c(OR)",ha="center",va="center",fontsize=6.5)
a.set_xlim(0,Lin+L+Lout); a.set_ylim(0,Hc); a.set_xlabel("x [mm]",fontsize=7,labelpad=14); a.set_ylabel("z [mm]",fontsize=7); a.tick_params(labelsize=7); a.set_title("side view, OR = 0.5",fontsize=9)
plt.tight_layout()
for ext in ("png","pdf"): plt.savefig(os.path.join(ROOT,"figures/fig_unit_cell."+ext))
print("written")
