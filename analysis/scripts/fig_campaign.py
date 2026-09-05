#!/usr/bin/env python3
"""Campaign figures from the unit-cell dataset ledger and the refit statistics (revision round 3).
Inputs: cfd/unit_cell_campaign/dataset_ledger_unitcell.csv (post_campaign.py), audit/refit_stats.csv
(refit_closures.py), audit/feasibility_map.csv (solve_eq22.py). Only rows with accepted == True are
plotted as data; rejected rows (closure failure or outside the envelope) are shown as open grey markers
where the figure says so. Outputs figures/fig_phi_bypass.(png|pdf), fig_rth_or.(png|pdf),
fig_parity.(png|pdf), fig_dp_pump.(png|pdf), fig_grid.(png|pdf). Greyscale-readable (STYLE_GUIDE.md)."""
import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LED=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,"cfd/unit_cell_campaign/dataset_ledger_unitcell.csv")
STATS=os.path.join(ROOT,"audit/refit_stats.csv"); FMAP=os.path.join(ROOT,"audit/feasibility_map.csv")
EPS=1e-4
def phi_model(o,r,C1,m,n): return 1/(1+C1*((1-o)/(o+EPS))**m*(r/100)**n)
plt.rcParams.update({"font.size":8,"axes.labelsize":8,"legend.fontsize":6.5,"xtick.labelsize":7,"ytick.labelsize":7})
MK=["o","s","^","D","v","<",">","p","h","*","X"]
def save(fig,name):
    fig.tight_layout()
    for ext in ("png","pdf"): fig.savefig(os.path.join(ROOT,"figures",name+"."+ext),dpi=300)
    plt.close(fig); print("wrote",name)
L=pd.read_csv(LED); L["acc"]=L.accepted.astype(str).str.lower().isin(["true","1","y","yes"])
cal=L[L.partitions.astype(str).str.contains("calibration")&(L.fluid=="FC-40")]
A=cal[cal.acc]; R=cal[~cal.acc]
stats=pd.read_csv(STATS).set_index("partition") if os.path.exists(STATS) else None
fit=stats.loc["calibration"] if stats is not None and "calibration" in stats.index and str(stats.loc["calibration","status"])=="FITTED" else None
re_levels=sorted(cal.Re_label.unique())
# Fig: bypass fraction against OR per Re level, with the fitted closure
fig,ax=plt.subplots(figsize=(4.6,3.3))
o=np.linspace(0.01,0.99,200)
for i,re in enumerate(re_levels):
    S=A[A.Re_label==re]; mk=MK[i%len(MK)]
    if not S.empty: ax.plot(S.OR,100*S.phi_field,mk,color="k",mfc="none" if i%2 else "k",ms=4,label=r"$\mathrm{Re}_{ch}$ = %g"%re)
    if fit is not None and not S.empty: ax.plot(o,100*phi_model(o,float(re),fit.C1,fit.m,fit.n),"-",color="0.4",lw=0.7)
if not R.empty: ax.plot(R.OR,100*R.phi_field,"x",color="0.6",ms=4,label="rejected (closure or envelope)")
ax.set_xlabel(r"recess ratio $\mathrm{OR}$ [-]"); ax.set_ylabel(r"$\Phi_{\mathrm{bypass}}$ [%]"); ax.set_xlim(-0.02,1.02); ax.set_ylim(-2,102)
ax.grid(True,ls=":",lw=0.5); ax.legend(frameon=False,ncol=2); save(fig,"fig_phi_bypass")
# Fig: thermal resistance against OR per Re level (accepted rows), sealed value as reference
fig,ax=plt.subplots(figsize=(4.6,3.3))
for i,re in enumerate(re_levels):
    S=A[A.Re_label==re].sort_values("OR"); mk=MK[i%len(MK)]
    if not S.empty: ax.plot(S.OR,S.Rth_field,mk+"-",color="k",mfc="none" if i%2 else "k",ms=4,lw=0.6,label=r"$\mathrm{Re}_{ch}$ = %g"%re)
if not R.empty: ax.plot(R.OR,R.Rth_field,"x",color="0.6",ms=4,label="rejected")
ax.set_xlabel(r"recess ratio $\mathrm{OR}$ [-]"); ax.set_ylabel(r"$R_{\mathrm{th}}$ [K W$^{-1}$]"); ax.set_yscale("log"); ax.grid(True,which="both",ls=":",lw=0.5); ax.legend(frameon=False,ncol=2); save(fig,"fig_rth_or")
# Fig: parity of the closure against the field values (Phi, Nu, R_th), calibration and holdouts
if fit is not None:
    import importlib.util, types
    spec=importlib.util.spec_from_file_location("refit_closures",os.path.join(ROOT,"figures/src/refit_closures.py")); rc=importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
    A_=types.SimpleNamespace(k_fin=387.6,nu_fd=float(fit.Nu_fd))
    def predict(S):
        phi_p=rc.phi_model((S.OR.values.astype(float),S.Re_recomputed_ch_Eq1_140mm.values.astype(float)),fit.C1,fit.m,fit.n)
        gz=S.Re_recomputed_ch_Eq1_140mm.values.astype(float)*np.clip(1-phi_p,0,None)*S.Pr.values*S.D_h_over_L.values
        phie=rc.phi_model((S.OR.values.astype(float),S.Re_recomputed_ch_Eq1_140mm.values.astype(float)),fit.C1_eff,fit.m_eff,fit.n_eff) if "C1_eff" in fit and fit.C1_eff==fit.C1_eff else phi_p
        nu_p=rc.nu_model(gz,fit.C2,fit.p,fit.Nu_fd); rth_p=rc.rth_network(S,nu_p,phie,fit.R_fixed,A_)   # caloric term with the effective bypass fraction
        return phi_p,nu_p,rth_p
    fig,ax=plt.subplots(1,3,figsize=(7.0,2.5))
    groups=[("calibration","o","k"),("holdout_EFL-1","s","0.35"),("holdout_thermal_load","^","0.35"),("cross_combinations","D","0.35")]
    for name,mk,col in groups:
        S=L[L.acc&L.partitions.astype(str).str.contains(name,regex=False)]
        if S.empty: continue
        pp,nn,rr=predict(S)
        ax[0].plot(100*S.phi_field,100*pp,mk,color=col,mfc="none",ms=3.5,label=name.replace("_"," "))
        ax[1].plot(S.Nu_field,nn,mk,color=col,mfc="none",ms=3.5); ax[2].plot(S.Rth_field,rr,mk,color=col,mfc="none",ms=3.5)
    for a,lab,lo,hi in ((ax[0],r"$\Phi_{\mathrm{bypass}}$ [%]",0,100),(ax[1],r"$\mathrm{Nu}$ [-]",None,None),(ax[2],r"$R_{\mathrm{th}}$ [K W$^{-1}$]",None,None)):
        xl=a.get_xlim() if lo is None else (lo,hi); m=[min(xl[0],a.get_ylim()[0]),max(xl[1],a.get_ylim()[1])]
        a.plot(m,m,"-",color="0.5",lw=0.6); a.plot(m,[1.2*v for v in m],":",color="0.6",lw=0.5); a.plot(m,[0.8*v for v in m],":",color="0.6",lw=0.5)
        a.set_xlabel("field, "+lab); a.set_ylabel("closure, "+lab); a.set_xlim(m); a.set_ylim(m); a.grid(True,ls=":",lw=0.5)
    ax[0].legend(frameon=False); 
    for a,t in zip(ax,("(a)","(b)","(c)")): a.set_title(t,fontsize=8,loc="left")
    save(fig,"fig_parity")
# Fig: pressure drop and pumping power against OR per Re level
fig,ax=plt.subplots(1,2,figsize=(7.0,2.8))
for i,re in enumerate(re_levels):
    S=A[A.Re_label==re].sort_values("OR"); mk=MK[i%len(MK)]
    if S.empty: continue
    ax[0].plot(S.OR,S.dp_field,mk+"-",color="k",mfc="none" if i%2 else "k",ms=4,lw=0.6,label=r"$\mathrm{Re}_{ch}$ = %g"%re)
    ax[1].plot(S.OR,S.W_pump_W,mk+"-",color="k",mfc="none" if i%2 else "k",ms=4,lw=0.6)
ax[0].set_ylabel(r"$\Delta p_{\mathrm{sink}}$ [Pa]"); ax[1].set_ylabel(r"$W_{\mathrm{pump}}$ [W]")
for a,t in zip(ax,("(a)","(b)")): a.set_xlabel(r"recess ratio $\mathrm{OR}$ [-]"); a.set_yscale("log"); a.grid(True,which="both",ls=":",lw=0.5); a.set_title(t,fontsize=8,loc="left")
ax[0].legend(frameon=False,ncol=2); save(fig,"fig_dp_pump")
# Fig: streamwise profiles of the clearance share and the local Nusselt number for accepted cases at Re_ch 250 and 40
fig,ax=plt.subplots(1,2,figsize=(7.4,2.8),gridspec_kw=dict(width_ratios=[1.35,1])); xs=[0,0.2,0.4,0.6,0.8,1.0]; xb=[0.1,0.3,0.5,0.7,0.9]
for j,(re,ls) in enumerate(((250,"-"),(40,"--"))):
    for i,o in enumerate(sorted(A.OR.unique())):
        S=A[(A.Re_label==re)&np.isclose(A.OR,o)]
        if S.empty: continue
        r=S.iloc[0]; mk=MK[i%len(MK)]
        ax[0].plot(xs,[100*r["Phi_X%d"%k] for k in range(6)],mk+ls,color="k",mfc="none" if i%2 else "k",ms=4,lw=0.7,label="OR %.1f, Re %g"%(o,re))
        ax[1].plot(xb,[r["Nu_B%d"%k] for k in range(5)],mk+ls,color="k",mfc="none" if i%2 else "k",ms=4,lw=0.7)
ax[1].axhline(7.85,color="0.5",lw=0.6,ls=":"); ax[1].text(0.12,4.6,"dotted line: Shah-London H1, 7.85",fontsize=6.5,color="0.3")
ax[0].set_xlabel(r"$x/L_{\mathrm{sink}}$"); ax[0].set_ylabel(r"clearance share of the cell flow [%]"); ax[1].set_xlabel(r"$x/L_{\mathrm{sink}}$ (bin centre)"); ax[1].set_ylabel(r"local $\mathrm{Nu}$ [-]")
for a,t in zip(ax,("(a)","(b)")): a.grid(True,ls=":",lw=0.5); a.set_title(t,fontsize=8,loc="left")
ax[0].legend(frameon=False,ncol=1,fontsize=5.5,loc="center left",bbox_to_anchor=(1.01,0.5)); ax[0].set_xlim(-0.03,1.03); save(fig,"fig_profiles")
# Fig: grid study (coarse, medium, fine at OR 0.1, Re 250)
G=L[L.partitions.astype(str).str.contains("grid_study")|(L.case_id=="C018")].sort_values("cells")
if len(G)>=2:
    fig,ax=plt.subplots(1,3,figsize=(7.0,2.4))
    for a,col,lab in zip(ax,("T_chip_max_C","dp_field","phi_field"),(r"$T_{\mathrm{chip,max}}$ [$^{\circ}$C]",r"$\Delta p_{\mathrm{sink}}$ [Pa]",r"$\Phi_{\mathrm{bypass}}$ [-]")):
        a.plot(G.cells,G[col],"o-",color="k",mfc="none"); a.set_xscale("log"); a.set_xlabel("cells"); a.set_ylabel(lab); a.grid(True,which="both",ls=":",lw=0.5)
    save(fig,"fig_grid")
print("rows",len(L),"accepted",int(L.acc.sum()),"calibration accepted",len(A))
