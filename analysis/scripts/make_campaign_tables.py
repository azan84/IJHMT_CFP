#!/usr/bin/env python3
"""Write the LaTeX tables of the calibration campaign from the dataset ledger and the refit statistics.
Inputs: cfd/unit_cell_campaign/dataset_ledger_unitcell.csv, audit/refit_stats.csv, audit/optimum.csv,
audit/feasibility_map.csv. Outputs (manuscript/tables/): tab_campaign_counts.tex (cases run, converged,
accepted per partition and the reasons for rejection), tab_coefficients.tex (fitted coefficients with
SE and 95 % CI), tab_statistics.tex (per-partition and per-band error statistics computed here from the
ledger with the coefficients of refit_stats.csv), tab_grid.tex (three-grid study), tab_fixed_fin.tex
(fixed-fin clearance sweep), tab_calibration_ledger.tex (every accepted calibration case). Every number
in these tables traces to the ledger row or the refit_stats row named in the table caption."""
import os, sys, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LED=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,"cfd/unit_cell_campaign/dataset_ledger_unitcell.csv")
OUT=os.path.join(ROOT,"manuscript/tables"); os.makedirs(OUT,exist_ok=True)
EPS=1e-4; K_FIN=387.6
L=pd.read_csv(LED); L["acc"]=L.accepted.astype(str).str.lower().isin(["true","1","y","yes"]); L["conv"]=L.converged.astype(str).str.lower().isin(["true","1","y","yes"])
L["env"]=L.passed_validity_envelope.astype(str)=="y"; L["parts"]=L.partitions.astype(str)
def w(name,s): open(os.path.join(OUT,name),"w").write(s); print("wrote",name)
def f(x,d=3):
    try: return ("%."+str(d)+"g")%float(x)
    except Exception: return "M"
# 1. counts
PART=[("calibration","Calibration (FC-40, 700 W)"),("holdout_EFL-1","EFL-1"),("holdout_thermal_load","Thermal load"),("cross_combinations","Cross-combinations"),("fixed_fin_sweep","Fixed-fin clearance sweep"),("grid_study","Grid study")]
rows=[]
for key,lab in PART:
    S=L[L.parts.str.contains(key,regex=False)]
    if S.empty: continue
    st=S.stop_type.astype(str) if "stop_type" in S else pd.Series(["?"]*len(S),index=S.index)
    n_conv=int(S.conv.sum()); n_envstop=int((st=="envelope").sum()); n_cap=int(((st=="cap")&~S.conv).sum()); n_div=int((st=="diverged").sum()); n_env=int(S.env.sum()); n_acc=int(S.acc.sum())
    rows.append("%s & %d & %d & %d & %d & %d & %d & %d \\\\"%(lab,len(S),n_conv,n_envstop,n_cap,n_div,n_env,n_acc))
w("tab_campaign_counts.tex","""\\begin{table}[htbp]
\\centering
\\caption{Calibration campaign: cases finished at the time of this build, converged (residual targets, stationarity, mass-split and energy closures of Section~\\ref{sec:vv-closure}), stopped by the envelope rule (maximum interface temperature above 70~$^{\\circ}$C at 4000 iterations or later), stopped at the iteration cap without converging, diverged (solver exit code other than zero), inside the validity envelope, and accepted (converged and inside the envelope). Source: \\texttt{cfd/unit\\_cell\\_campaign/dataset\\_ledger\\_unitcell.csv}, column \\texttt{stop\\_type}. Partitions overlap as stated in Section~\\ref{sec:partitions}.}
\\label{tab:campaign_counts}
\\scriptsize
\\begin{tabular}{@{}lccccccc@{}}
\\hline
Partition & finished & converged & envelope stop & at cap & diverged & in envelope & accepted \\\\
\\hline
"""+"\\n".join(rows)+"""
\\hline
\\end{tabular}
\\end{table}
""")
# 2. coefficients
ST=os.path.join(ROOT,"audit/refit_stats.csv")
T=pd.read_csv(ST).set_index("partition") if os.path.exists(ST) else None
if T is not None and "calibration" in T.index and str(T.loc["calibration","status"])=="FITTED":
    c=T.loc["calibration"]
    import re as _re
    se=dict(_re.findall(r"(\w+) ([-0-9.e+]+)",str(c.SE))); ci=dict(_re.findall(r"(\w+) \+-([-0-9.e+]+)",str(c.CI95)))
    rows=["\\multicolumn{5}{@{}l}{Eq.~(\\ref{eq:phi_bypass_closure}), leading-edge bypass fraction $\\Phi_{\\mathrm{bypass}}$} \\\\"]
    for nm,val,lab,bnd in (("C1",c.C1,"$C_1$","[0.01, 20]"),("m",c.m,"$m$","[0.05, 4]"),("n",c.n,"$n$","[$-1$, 1]")):
        rows.append("%s & %s & %s & $\\pm$%s & %s \\\\"%(lab,f(val,4),f(se[nm],3),f(ci[nm],3),bnd))
    if "C1_eff" in c and c.C1_eff==c.C1_eff:
        rows.append("\\multicolumn{5}{@{}l}{Same form fitted to the effective bypass fraction $\\Phi_{\\mathrm{eff}}$ of the caloric term} \\\\")
        for nm,val,lab,bnd in (("C1_eff",c.C1_eff,"$C_1^{\\mathrm{eff}}$","[0.01, 20]"),("m_eff",c.m_eff,"$m^{\\mathrm{eff}}$","[0.05, 4]"),("n_eff",c.n_eff,"$n^{\\mathrm{eff}}$","[$-1$, 1]")):
            rows.append("%s & %s & %s & $\\pm$%s & %s \\\\"%(lab,f(val,4),f(se[nm],3),f(ci[nm],3),bnd))
    rows.append("\\multicolumn{5}{@{}l}{Eq.~(\\ref{eq:nu_composite}), Nusselt number} \\\\")
    for nm,val,lab,bnd in (("C2",c.C2,"$C_2$","[0.05, 10]"),("p",c.p,"$p$","[0.05, 1]")):
        rows.append("%s & %s & %s & $\\pm$%s & %s \\\\"%(lab,f(val,4),f(se[nm],3),f(ci[nm],3),bnd))
    rows.append("$\\mathrm{Nu}_{\\mathrm{fd}}$ & %s & fixed & fixed & Shah-London H1, aspect ratio 0.024 \\\\"%f(c.Nu_fd,4))
    rows.append("$R_{\\mathrm{fixed}} = R_{\\mathrm{TIM}} + R_{\\mathrm{spread}}$ [K W$^{-1}$] & %s & mean residual & & $\\ge 0$ \\\\"%f(c.R_fixed,4))
    w("tab_coefficients.tex","""\\begin{table}[htbp]
\\centering
\\caption{Coefficients of Eqs.~(\\ref{eq:phi_bypass_closure}) and (\\ref{eq:nu_composite}) fitted on the %d accepted calibration cases by bounded non-linear least squares (objective: %s; the Prandtl exponent $k$ was not included, Section~\\ref{sec:fitting}). Standard errors and 95\\%% confidence intervals from the covariance of the fit. Source: \\texttt{audit/refit\\_stats.csv}, row \\texttt{calibration}.}
\\label{tab:coefficients}
\\scriptsize
\\begin{tabular}{@{}lcccl@{}}
\\hline
Coefficient & Value & SE & 95\\%% CI & Bounds \\\\
\\hline
"""%(int(c.N),str(c.objective).replace("SSR","SSR ").replace("phi_eff","$\\Phi_{\\mathrm{eff}}$").replace("phi","$\\Phi$").replace("Nu","Nu"))+"\n".join(rows)+"""
\\hline
\\end{tabular}
\\end{table}
""")
    # 3. statistics per partition and band, recomputed here from the ledger with the fitted coefficients
    import importlib.util, types
    spec=importlib.util.spec_from_file_location("refit_closures",os.path.join(ROOT,"figures/src/refit_closures.py")); rc=importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
    A_=types.SimpleNamespace(k_fin=K_FIN,nu_fd=float(c.Nu_fd))
    def predict(S):
        phi_p=rc.phi_model((S.OR.values.astype(float),S.Re_recomputed_ch_Eq1_140mm.values.astype(float)),c.C1,c.m,c.n)
        gz=S.Re_recomputed_ch_Eq1_140mm.values.astype(float)*np.clip(1-phi_p,0,None)*S.Pr.values*S.D_h_over_L.values
        phie=rc.phi_model((S.OR.values.astype(float),S.Re_recomputed_ch_Eq1_140mm.values.astype(float)),c.C1_eff,c.m_eff,c.n_eff) if "C1_eff" in c and c.C1_eff==c.C1_eff else phi_p
        nu_p=rc.nu_model(gz,c.C2,c.p,c.Nu_fd); rth_p=rc.rth_network(S,nu_p,phie,c.R_fixed,A_)   # caloric term with the effective bypass fraction
        return phi_p,nu_p,rth_p
    def stats(S):
        if S.empty: return None
        pp,nn,rr=predict(S); pt=S.phi_field.values.astype(float); nt=S.Nu_field.values.astype(float); rt=S.Rth_field.values.astype(float); o=S.OR.values.astype(float)
        mae=100*np.mean(np.abs(pp-pt)); m=o>=0.1; mape=100*np.mean(np.abs(pp[m]-pt[m])/pt[m]) if m.any() else np.nan
        numape=100*np.mean(np.abs(nn-nt)/nt); e=rr-rt; rmape=100*np.mean(np.abs(e)/rt); rrmse=np.sqrt(np.mean(e**2)); rmax=np.max(np.abs(e)); ss=np.sum((rt-rt.mean())**2); r2=1-np.sum(e**2)/ss if ss>0 else np.nan
        return len(S),mae,mape,numape,rmape,rrmse,rmax,r2
    def row(lab,S):
        s=stats(S)
        if s is None: return "%s & 0 & M & M & M & M & M & M & M \\\\"%lab
        N,mae,mape,numape,rmape,rrmse,rmax,r2=s
        return "%s & %d & %s & %s & %s & %s & %s & %s & %s \\\\"%(lab,N,f(mae,3),f(mape,3) if not np.isnan(mape) else "n/a",f(numape,3),f(rmape,3),f(rrmse,3),f(rmax,3),f(r2,3) if not np.isnan(r2) else "n/a")
    A=L[L.acc]; rows=[]
    for key,lab in PART[:4]: rows.append(row(lab,A[A.parts.str.contains(key,regex=False)]))
    rows.append("\\hline")
    cal=A[A.parts.str.contains("calibration")]
    for lo,hi,lab in ((0,0,"OR = 0"),(0.05,0.3,"0 $<$ OR $\\le$ 0.3"),(0.3,0.7,"0.3 $<$ OR $\\le$ 0.7"),(0.7,1.0,"0.7 $<$ OR $\\le$ 1")):
        S=cal[np.isclose(cal.OR,0)] if hi==0 else cal[(cal.OR>lo+1e-9)&(cal.OR<=hi+1e-9)]
        rows.append(row("calibration, "+lab,S))
    for lo,hi,lab in ((0,10,"$\\mathrm{Re}_{ch} \\le 10$"),(10,50,"10 $<$ $\\mathrm{Re}_{ch} \\le$ 50"),(50,300,"$\\mathrm{Re}_{ch} >$ 50")):
        rows.append(row("calibration, "+lab,cal[(cal.Re_label>lo)&(cal.Re_label<=hi)]))
    w("tab_statistics.tex","""\\begin{table}[htbp]
\\centering
\\caption{Error statistics of the calibrated closure on the accepted cases of each partition and of the calibration subgroups (Section~\\ref{sec:accuracy_evaluation}). $\\Phi$ MAE in percentage points; $\\Phi$ MAPE over $\\mathrm{OR} \\ge 0.1$; Nu MAPE; $R_{\\mathrm{th}}$ MAPE, RMSE [K W$^{-1}$], maximum absolute error [K W$^{-1}$] and $R^2$ from the independent resistance network of Section~\\ref{sec:fitting} with $R_{\\mathrm{fixed}}$ fitted on the calibration set only. Computed by \\texttt{figures/src/make\\_campaign\\_tables.py} from \\texttt{dataset\\_ledger\\_unitcell.csv} with the coefficients of Table~\\ref{tab:coefficients}. n/a: subgroup without $\\mathrm{OR} \\ge 0.1$ rows or without variance.}
\\label{tab:statistics}
\\scriptsize
\\setlength{\\tabcolsep}{2.5pt}
\\begin{tabular}{@{}lcccccccc@{}}
\\hline
Set & $N$ & $\\Phi$ MAE & $\\Phi$ MAPE & Nu MAPE & $R_{\\mathrm{th}}$ MAPE & $R_{\\mathrm{th}}$ RMSE & $R_{\\mathrm{th}}$ max. & $R^2$ \\\\
\\hline
"""+"\n".join(rows)+"""
\\hline
\\end{tabular}
\\end{table}
""")
# 4. grid study
G=L[L.parts.str.contains("grid_study")|(L.case_id=="C018")].sort_values("cells")
if len(G)>=2:
    rows=["%s & %s & %d & %s & %s & %s & %s & %s & %s \\\\"%(r.case_id,r.grid,int(r.cells),f(r.T_chip_max_C,4),f(r.dp_field,4),f(100*r.phi_field,3),f(r.Nu_field,3),f(r.energy_balance_pct,2),"yes" if r.acc else "no") for r in G.itertuples()]
    w("tab_grid.tex","""\\begin{table}[htbp]
\\centering
\\caption{Three-grid study at $\\mathrm{OR} = 0.1$, $\\mathrm{Re}_{ch} = 250$, FC-40, 700~W (the smallest non-zero recess ratio at the highest Reynolds level). Source: rows G001, C018 and G002 of \\texttt{dataset\\_ledger\\_unitcell.csv}.}
\\label{tab:grid}
\\scriptsize
\\begin{tabular}{@{}llccccccc@{}}
\\hline
Case & Grid & Cells & $T_{\\mathrm{chip,max}}$ [$^{\\circ}$C] & $\\Delta p_{\\mathrm{sink}}$ [Pa] & $\\Phi_{\\mathrm{bypass}}$ [\\%] & Nu & Energy closure [\\%] & Accepted \\\\
\\hline
"""+"\n".join(rows)+"""
\\hline
\\end{tabular}
\\end{table}
""")
# 5. fixed-fin sweep
F=L[L.parts.str.contains("fixed_fin_sweep")].sort_values("clearance_m")
if len(F)>=2:
    rows=["%s & %s & %s & %s & %s & %s & %s & %s \\\\"%(r.case_id,f(1000*r.clearance_m,3),f(100*r.phi_field,3),f(r.T_chip_max_C,4),f(r.Rth_field,3),f(r.dp_field,4),f(r.Nu_field,3),"yes" if r.acc else "no") for r in F.itertuples()]
    w("tab_fixed_fin.tex","""\\begin{table}[htbp]
\\centering
\\caption{Fixed-fin clearance sweep: $H_{\\mathrm{fin}} = 20.9$~mm, clearance varied by the chassis height, $\\mathrm{Re}_{ch} = 40$, FC-40, 700~W. Source: rows F001 to F004 of \\texttt{dataset\\_ledger\\_unitcell.csv}.}
\\label{tab:fixed_fin}
\\scriptsize
\\begin{tabular}{@{}lccccccc@{}}
\\hline
Case & $c$ [mm] & $\\Phi_{\\mathrm{bypass}}$ [\\%] & $T_{\\mathrm{chip,max}}$ [$^{\\circ}$C] & $R_{\\mathrm{th}}$ [K W$^{-1}$] & $\\Delta p_{\\mathrm{sink}}$ [Pa] & Nu & Accepted \\\\
\\hline
"""+"\n".join(rows)+"""
\\hline
\\end{tabular}
\\end{table}
""")
# 6. the accepted calibration ledger (supplementary)
C=L[L.parts.str.contains("calibration")].sort_values(["Re_label","OR"])
rows=["%s & %s & %g & %s & %s & %s & %s & %s & %s & %s & %s \\\\"%(r.case_id,f(r.OR,2),r.Re_label,f(100*r.phi_field,3),f(r.Nu_field,3),f(r.T_chip_max_C,4),f(r.Rth_field,3),f(r.dp_field,4),f(r.energy_balance_pct,2),(int(r.iterations) if pd.notna(r.iterations) else "M"),"yes" if r.acc else "no") for r in C.itertuples()]
w("tab_calibration_ledger.tex","""\\begin{longtable}{@{}lcccccccccc@{}}
\\caption{Calibration partition of the unit-cell campaign (FC-40, 700~W): every case, its bypass fraction, Nusselt number, maximum chip temperature, thermal resistance, sink pressure drop, energy closure, iterations and acceptance. Source: \\texttt{cfd/unit\\_cell\\_campaign/dataset\\_ledger\\_unitcell.csv}.}\\label{tab:calibration_ledger}\\\\
\\hline
Case & OR & $\\mathrm{Re}_{ch}$ & $\\Phi$ [\\%] & Nu & $T_{\\mathrm{chip,max}}$ [$^{\\circ}$C] & $R_{\\mathrm{th}}$ [K/W] & $\\Delta p$ [Pa] & energy [\\%] & it. & acc. \\\\
\\hline
\\endfirsthead
\\hline
Case & OR & $\\mathrm{Re}_{ch}$ & $\\Phi$ [\\%] & Nu & $T_{\\mathrm{chip,max}}$ [$^{\\circ}$C] & $R_{\\mathrm{th}}$ [K/W] & $\\Delta p$ [Pa] & energy [\\%] & it. & acc. \\\\
\\hline
\\endhead
"""+"\n".join(rows)+"""
\\hline
\\end{longtable}
""")
print("rows",len(L),"accepted",int(L.acc.sum()))
