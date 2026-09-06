#!/usr/bin/env python3
"""Additional statistics the campaign_results_summary.py general sweep does not compute: the coolant
comparison of Sec. 8.2 (Table bases) on three matched bases at OR = 0.1, and the T_chip,max RMSE and
maximum error of the withheld-load partition at OR = 0 (Sec. 7.1 item 3), predicted with the same
resistance network and coefficients as refit_closures.py (imported, not re-derived). Writes
audit/coolant_comparison.csv and appends both results to audit/campaign_results_summary.md."""
import os, sys, importlib.util, numpy as np, pandas as pd
ROOT="/mnt/e/ijhmt-cfp/Paper-5"; LED=os.path.join(ROOT,"cfd/unit_cell_campaign/dataset_ledger_unitcell.csv")
spec=importlib.util.spec_from_file_location("refit_closures",os.path.join(ROOT,"figures/src/refit_closures.py"))
rc=importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
d=pd.read_csv(LED); d["acc"]=d.accepted.astype(str)=="True"
t=pd.read_csv(os.path.join(ROOT,"audit/refit_stats.csv")).set_index("partition"); c=t.loc["calibration"]
import types; A_=types.SimpleNamespace(k_fin=387.6,nu_fd=float(c.Nu_fd))

L=[]
def p(s): L.append(s); print(s)

# ---------- coolant comparison, OR = 0.1 ----------
p("\n## Coolant comparison, OR = 0.1 (Sec. 8.2, Table bases; FC-40 calibration curve vs EFL-1 holdout)")
fc=d[(d.partitions.str.contains("calibration"))&(np.isclose(d.OR,0.1))].sort_values("Re_ch").reset_index(drop=True)
efl=d[(d.case_id.isin(["E005","E006"]))].sort_values("Re_ch").reset_index(drop=True)
cols=["Q_full_sink_LPM","m_full_kg_s","Re_ch","Pr_inlet","Phi_in","R_th_K_W","dp_sink_Pa","W_pump_W"]
def loglog_interp(x,y,xt):
    lx=np.log(x); ly=np.log(y); return float(np.exp(np.interp(np.log(xt),lx,ly)))
for _,e in efl.iterrows():
    p("\n--- anchor: %s (EFL-1, Re_ch label %g, accepted %s) ---"%(e.case_id,e.Re_ch,e.acc))
    p("matched Re_ch (Re_ch = %g both fluids): FC-40 %s vs EFL-1 %s"%(e.Re_ch,
        fc[np.isclose(fc.Re_ch,e.Re_ch)].case_id.iloc[0] if (np.isclose(fc.Re_ch,e.Re_ch)).any() else "none",e.case_id))
    if (np.isclose(fc.Re_ch,e.Re_ch)).any():
        f=fc[np.isclose(fc.Re_ch,e.Re_ch)].iloc[0]
        for k in cols: p("  %s: FC-40 %.5g | EFL-1 %.5g"%(k,f[k],e[k]))
    for basis,key in (("matched Q [[LPM]]","Q_full_sink_LPM"),("matched W_pump [[W]]","W_pump_W")):
        target=e[key]
        if target<fc[key].min() or target>fc[key].max(): p("  %s: EFL-1 value %.5g outside the FC-40 curve's range [%.5g, %.5g] at OR = 0.1; not interpolated"%(basis,target,fc[key].min(),fc[key].max())); continue
        row={}
        for k in cols: row[k]=loglog_interp(fc[key].values,fc[k].values,target) if k!=key else target
        p("  %s: FC-40 (interpolated) Q %.5g LPM, Re_ch %.4g, Phi %.4f, R_th %.5f K/W, dp %.5g Pa, W_pump %.5g W | EFL-1 Q %.5g LPM, Re_ch %.4g, Phi %.4f, R_th %.5f K/W, dp %.5g Pa, W_pump %.5g W"%(
            basis,row["Q_full_sink_LPM"],row["Re_ch"],row["Phi_in"],row["R_th_K_W"],row["dp_sink_Pa"],row["W_pump_W"],
            e.Q_full_sink_LPM,e.Re_ch,e.Phi_in,e.R_th_K_W,e.dp_sink_Pa,e.W_pump_W))

# CSV export at the Re=150 anchor (best-converged, farthest from the envelope edge)
e=efl[efl.Re_ch==150].iloc[0]; f=fc[fc.Re_ch==150].iloc[0]
rows=[dict(basis="matched Re_ch",fluid="FC-40",**{k:f[k] for k in cols}),dict(basis="matched Re_ch",fluid="EFL-1",**{k:e[k] for k in cols})]
for key in ("Q_full_sink_LPM","W_pump_W"):
    target=e[key]; row={k:(loglog_interp(fc[key].values,fc[k].values,target) if k!=key else target) for k in cols}
    rows.append(dict(basis="matched %s"%key,fluid="FC-40 (interpolated)",**row)); rows.append(dict(basis="matched %s"%key,fluid="EFL-1",**{k:e[k] for k in cols}))
pd.DataFrame(rows).to_csv(os.path.join(ROOT,"audit/coolant_comparison.csv"),index=False)

# ---------- T_chip,max prediction error, withheld-load partition, OR = 0 ----------
p("\n## Withheld-load partition, OR = 0 (Sec. 7.1 item 3): T_chip,max RMSE and maximum error")
tl=d[(d.partitions.str.contains("holdout_thermal_load"))&(d.acc)&(np.isclose(d.OR,0))].sort_values("P_sink_W").reset_index(drop=True)
X=(tl.OR.values.astype(float),tl.Re_recomputed_ch_Eq1_140mm.values.astype(float))
phi_p=rc.phi_model(X,c.C1,c.m,c.n); phie=rc.phi_model(X,c.C1_eff,c.m_eff,c.n_eff)
gz=X[1]*np.clip(1-phi_p,0,None)*tl.Pr.values*tl.D_h_over_L.values; nu_p=rc.nu_model(gz,c.C2,c.p,c.Nu_fd)
rth_p=rc.rth_network(tl,nu_p,phie,c.R_fixed,A_)
Tchip_p=tl.T_in_K.values-273.15+tl.P_sink_W.values*rth_p+tl.R_TIM_K_W.values*tl.P_sink_W.values*0   # R_TIM already inside R_th via rth_network's R_fixed; T_chip = T_in + P*R_th
Tchip_p=(tl.T_in_K.values-273.15)+tl.P_sink_W.values*rth_p
err=Tchip_p-tl.T_chip_max_C.values
p("cases: %s (P = %s W)"%(tl.case_id.tolist(),tl.P_sink_W.tolist()))
p("T_chip,max field [C]: %s"%[round(x,2) for x in tl.T_chip_max_C])
p("T_chip,max predicted [C] (T_in + P x R_th_predicted): %s"%[round(x,2) for x in Tchip_p])
p("RMSE %.3f C | maximum error %.3f C | mean error %+.3f C"%(np.sqrt(np.mean(err**2)),np.max(np.abs(err)),np.mean(err)))

open(os.path.join(ROOT,"audit/campaign_results_summary.md"),"a").write("\n".join(L)+"\n")
print("\nappended to audit/campaign_results_summary.md; coolant table in audit/coolant_comparison.csv")

# ---------- fixed-fin sweep: closure prediction vs field, row by row ----------
L2=["\n## Fixed-fin clearance sweep: closure prediction vs field (Sec. 8.1)"]
ff=d[d.partitions.str.contains("fixed_fin_sweep")].sort_values("clearance_m").reset_index(drop=True)
X=(ff.OR.values.astype(float),ff.Re_recomputed_ch_Eq1_140mm.values.astype(float))
phi_p=rc.phi_model(X,c.C1,c.m,c.n); phie=rc.phi_model(X,c.C1_eff,c.m_eff,c.n_eff)
gz=X[1]*np.clip(1-phi_p,0,None)*ff.Pr.values*ff.D_h_over_L.values; nu_p=rc.nu_model(gz,c.C2,c.p,c.Nu_fd)
rth_p=rc.rth_network(ff,nu_p,phie,c.R_fixed,A_)
for i,r in ff.iterrows():
    L2.append("%s: clearance %.2f mm, OR(equivalent) %.4f, Re_ch %g, accepted %s | Phi field %.4f vs closure %.4f (%+.1f pp) | R_th field %.5f vs closure %.5f K/W (%+.1f %%)"%(
        r.case_id,r.clearance_m*1e3,r.OR,r.Re_ch,r.acc,r.Phi_in,phi_p[i],100*(phi_p[i]-r.Phi_in),r.R_th_K_W,rth_p[i],100*(rth_p[i]-r.R_th_K_W)/r.R_th_K_W))
L2.append("(F003, F004 lie outside the validity envelope; their closure comparison is shown for context only, not part of the accepted-case statistic.)")
open(os.path.join(ROOT,"audit/campaign_results_summary.md"),"a").write("\n".join(L2)+"\n")
print("\n".join(L2))
