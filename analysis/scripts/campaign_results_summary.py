#!/usr/bin/env python3
"""Numbers for the manuscript's results text, each with its source, from the dataset ledger, the refit statistics, the
feasibility map and the temperature budget. Output: audit/campaign_results_summary.md (also printed)."""
import os, pandas as pd, numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); C=os.path.join(ROOT,"cfd/unit_cell_campaign")
d=pd.read_csv(os.path.join(C,"dataset_ledger_unitcell.csv")); d["acc"]=d.accepted.astype(str)=="True"; d["conv"]=d.converged.astype(str)=="True"; d["env"]=d.passed_validity_envelope=="y"
cal=d[d.partitions.str.contains("calibration")]; A=cal[cal.acc]; L=[]
def p(x): L.append(x)
p("# Campaign results summary (%d finished cases in the ledger)\n"%len(d)); p("Source: cfd/unit_cell_campaign/dataset_ledger_unitcell.csv unless stated.\n")
p("## Calibration partition (FC-40, 700 W)")
p("finished %d | inside envelope %d | converged %d | accepted %d | at cap (12000 or more iterations, not converged) %d | solver exit code != 0 %d"%(len(cal),cal.env.sum(),cal.conv.sum(),cal.acc.sum(),((cal.iterations>=12000)&~cal.conv).sum(),(cal.solver_rc!=0).sum()))
p("iterations of accepted cases: min %d, median %d, max %d"%(A.iterations.min(),A.iterations.median(),A.iterations.max()))
p("closures of accepted cases: mass split max %.2e %%, energy balance max %.3f %%, stationarity max %.2e"%(A.mass_split_closure_pct.max(),A.energy_balance_pct.max(),A.stationarity_max_var.max()))
p("wall temperature of accepted cases: %.1f to %.1f C; chip (base max + TIM): %.1f to %.1f C"%(A.T_wall_max_K.min()-273.15,A.T_wall_max_K.max()-273.15,A.T_chip_max_C.min(),A.T_chip_max_C.max()))
for o in sorted(cal.OR.unique()):
    s=cal[np.isclose(cal.OR,o)].sort_values("Re_ch"); acc=s[s.acc].Re_ch.tolist(); hot=s[~s.env].Re_ch.tolist()
    p("OR %.1f: accepted at Re_ch %s; outside the wall bound at %s"%(o,acc,hot))
p("\n## Bypass split (accepted cases)")
for o in sorted(A.OR.unique()):
    s=A[np.isclose(A.OR,o)].sort_values("Re_ch"); p("OR %.1f: Phi leading edge %s; mid %s; trailing edge %s; Phi_eff %s (Re_ch %s)"%(o,[round(x,3) for x in s.Phi_in],[round(x,3) for x in s.Phi_mid],[round(x,3) for x in s.Phi_X5],[round(x,3) for x in s.Phi_eff],s.Re_ch.tolist()))
p("\n## Nusselt number (accepted cases; length-averaged, and local in the first and last fifth)")
for o in sorted(A.OR.unique()):
    s=A[np.isclose(A.OR,o)].sort_values("Re_ch"); p("OR %.1f: Nu %s; Nu_B0 %s; Nu_B4 %s; Re_active %s"%(o,[round(x,2) for x in s.Nu],[round(x,1) for x in s.Nu_B0],[round(x,2) for x in s.Nu_B4],[round(x,1) for x in s.Re_active]))
p("\n## Temperature budget of the base maximum (accepted cases) [K]: base drop | interface span | mean film | bulk rise | P/(m(1-Phi_in)cp) | P/(m(1-Phi_eff)cp)")
for r in A.sort_values(["OR","Re_ch"]).itertuples():
    P=r.P_sink_W; p("%s OR %.1f Re %d: total %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f"%(r.case_id,r.OR,r.Re_ch,r.T_base_max_K-r.T_in_K,r.T_base_max_K-r.T_wall_max_K,r.T_wall_max_K-r.T_wall_mean_K,r.dT_wall_bulk_bins_K,r.T_ch_out_K-r.T_in_K,P/(r.m_full_kg_s*(1-r.Phi_in)*r.cp_inlet),P/(r.m_full_kg_s*(1-r.Phi_eff)*r.cp_inlet)))
p("\n## Thermal resistance, pressure drop, pumping power (accepted cases)")
for r in A.sort_values(["OR","Re_ch"]).itertuples(): p("%s OR %.1f Re %d: R_th %.4f K/W (R_base %.4f + R_TIM %.3f); dp %.4g Pa; Q_full %.3f LPM; W_pump %.4g W; T_chip %.1f C"%(r.case_id,r.OR,r.Re_ch,r.R_th_K_W,r.R_base_K_W,r.R_TIM_K_W,r.dp_sink_Pa,r.Q_full_sink_LPM,r.W_pump_W,r.T_chip_max_C))
s0=A[np.isclose(A.OR,0)].set_index("Re_ch")
p("\n## Ratios to the sealed case at the same Re_ch (accepted cases): R_th/R_th,sealed; W_pump/W_pump,sealed")
for r in A[A.OR>0].sort_values(["OR","Re_ch"]).itertuples():
    if r.Re_ch in s0.index: p("%s OR %.1f Re %d: %.3f; %.3f"%(r.case_id,r.OR,r.Re_ch,r.R_th_K_W/s0.loc[r.Re_ch,"R_th_K_W"],r.W_pump_W/s0.loc[r.Re_ch,"W_pump_W"]))
B=A[A.OR>0].copy(); B["rise"]=B.T_ch_out_K-B.T_in_K; B["pred_in"]=B.P_sink_W/(B.m_full_kg_s*(1-B.Phi_in)*B.cp_inlet); B["pred_eff"]=B.P_sink_W/(B.m_full_kg_s*(1-B.Phi_eff)*B.cp_inlet)
B["err_K"]=B.pred_eff-B.rise; B["err_pct"]=100*B.err_K/B.rise; B["under"]=B.rise/B.pred_in
p("\n## Caloric term against the measured channel exit rise (accepted cases with OR > 0): underestimation factor with the leading-edge Phi min %.2f max %.1f; with Phi_eff: within 1 K in %d of %d cases; error range %.1f%% to %.1f%% at OR <= 0.2 (excluding the lowest accepted Re of each OR: %s), %.0f%% to %.0f%% at OR >= 0.3"%(B.under.min(),B.under.max(),int((B.err_K.abs()<=1).sum()),len(B),
  B[(B.OR<=0.2)&~B.case_id.isin(["C011","C022"])].err_pct.min(),B[(B.OR<=0.2)&~B.case_id.isin(["C011","C022"])].err_pct.max(),"C011, C022",B[B.OR>=0.3].err_pct.min(),B[B.OR>=0.3].err_pct.max()))
for r in B.sort_values(["OR","Re_ch"]).itertuples(): p("%s OR %.1f Re %d: rise %.2f K | P/(m(1-Phi_in)cp) %.2f | P/(m(1-Phi_eff)cp) %.2f | error %+.2f K (%+.1f %%) | underestimation %.2f"%(r.case_id,r.OR,r.Re_ch,r.rise,r.pred_in,r.pred_eff,r.err_K,r.err_pct,r.under))
fm=pd.read_csv(os.path.join(ROOT,"audit/feasibility_map.csv")); ff=fm[fm.feasible.astype(str).isin(["True","y"])]
p("\n## Feasible operating map (audit/feasibility_map.csv; R_th <= 1.10 R_sealed(Re) and T_chip <= 85 C): %d feasible of %d rows"%(len(ff),len(fm)))
for re_ in sorted(ff.Re_label.unique()):
    s=ff[ff.Re_label==re_].sort_values("OR"); best=s.loc[s.Wpump_W.idxmin()]; p("Re %g: feasible OR %s; minimum W_pump at OR %.1f: %.4g W (sealed %.4g W, ratio %.3f), R_th ratio %.3f, T_chip %.1f C"%(re_,s.OR.tolist(),best.OR,best.Wpump_W,s[s.OR==0].Wpump_W.iloc[0] if (s.OR==0).any() else float("nan"),best.Wpump_W/(s[s.OR==0].Wpump_W.iloc[0] if (s.OR==0).any() else float("nan")),best.c_rth,best.c_T))
t=pd.read_csv(os.path.join(ROOT,"audit/refit_stats.csv")).set_index("partition"); c=t.loc["calibration"]
import importlib.util, types
spec=importlib.util.spec_from_file_location("refit_closures",os.path.join(ROOT,"figures/src/refit_closures.py")); rc=importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
A_=types.SimpleNamespace(k_fin=387.6,nu_fd=float(c.Nu_fd)); S=A.sort_values(["OR","Re_ch"]).reset_index(drop=True)
X=(S.OR.values.astype(float),S.Re_recomputed_ch_Eq1_140mm.values.astype(float)); phi_p=rc.phi_model(X,c.C1,c.m,c.n); phie=rc.phi_model(X,c.C1_eff,c.m_eff,c.n_eff)
gz=X[1]*np.clip(1-phi_p,0,None)*S.Pr.values*S.D_h_over_L.values; nu_p=rc.nu_model(gz,c.C2,c.p,c.Nu_fd); conv,calo=rc.rth_terms(S,nu_p,phie,A_); eo=rc.eta_o(nu_p,S,A_); ef=rc.eta_fin(nu_p,S,A_)
p("\n## Network terms of Eq. (rth_sum) with the fitted coefficients (accepted cases) [K/W]: R_fixed %.4f | convective 1/(eta_o h A) | caloric 1/(m(1-Phi_eff)cp) | predicted | field | error %%; eta_fin, eta_o"%c.R_fixed)
p("convective term min %.4f max %.4f (ratio %.2f); caloric term min %.4f max %.4f (ratio %.0f); R_TIM %.4f; implied R_spread = R_fixed - R_TIM = %.4f"%(conv.min(),conv.max(),conv.max()/conv.min(),calo.min(),calo.max(),calo.max()/calo.min(),0.006,c.R_fixed-0.006))
for i,r in S.iterrows():
    pred=c.R_fixed+conv[i]+calo[i]; p("%s OR %.1f Re %d: conv %.4f | cal %.4f | pred %.4f | field %.4f | %+.1f %% | eta_fin %.3f eta_o %.3f | Phi_pred %.3f Phi_eff_pred %.3f Nu_pred %.2f"%(r.case_id,r.OR,r.Re_ch,conv[i],calo[i],pred,r.Rth_field,100*(pred-r.Rth_field)/r.Rth_field,ef[i],eo[i],phi_p[i],phie[i],nu_p[i]))
p("\n## Fit (audit/refit_stats.csv, calibration row)"); p(c.to_string())
sd=pd.read_csv(os.path.join(ROOT,"audit/sealed_dp_check.csv")); p("\n## Sealed pressure drop against Shah-London (audit/sealed_dp_check.csv): ratio at film viscosity %s; at inlet viscosity %s"%([round(x,3) for x in sd.ratio_Tfilm],[round(x,3) for x in sd.ratio_Tin]))
open(os.path.join(ROOT,"audit/campaign_results_summary.md"),"w").write("\n".join(L)+"\n"); print("\n".join(L))
