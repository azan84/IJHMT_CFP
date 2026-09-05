#!/usr/bin/env python3
"""Solve the constrained design problem of Eq. (22) on a genuine dataset (items B5, B6):
minimise W_pump(OR, Re) subject to R_th(OR, Re) <= (1 + tol) R_th,sealed(Re) and
T_chip,max <= T_max at the stated load, on one basis (fluid, topology, P_TDP).
Input ledger columns: OR, Re_label, fluid, geometry_label (topology), P_TDP, Rth_field,
Tchip_field, dp_field, Q_LPM, passed_validity_envelope, thermal_data_source.
Output: audit/optimum.csv (the optimum or 'no feasible point') and audit/feasibility_map.csv
(every (OR, Re) of the basis with its constraint values and feasibility flag; the data of the
former Fig. 7(b)). Refuses (exit 2) when no row carries solver-derived data. --selftest runs on a
synthetic ledger with a known optimum."""
import sys, os, argparse, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT=os.path.join(ROOT,"audit/optimum.csv"); DEFAULT_MAP=os.path.join(ROOT,"audit/feasibility_map.csv")
def run(L,a):
    src=L.get("thermal_data_source",pd.Series(["none"]*len(L))).astype(str); usable=~src.str.lower().str.startswith("none")
    if not usable.any(): print("BLOCKED: no solver-derived thermal data in the ledger (thermal_data_source = %s)."%sorted(src.unique())); return 2
    need=["OR","Re_label","fluid","geometry_label","P_TDP","Rth_field","Tchip_field","dp_field","Q_LPM","passed_validity_envelope"]; miss=[c for c in need if c not in L]
    if miss: print("BLOCKED: ledger lacks",miss); return 2
    D=L[usable&(L.fluid==a.fluid)&(L.geometry_label==a.topology)&(np.isclose(L.P_TDP.astype(float),a.p_tdp))].copy()
    if D.empty: print("BLOCKED: no rows on the basis fluid=%s topology=%s P_TDP=%g W"%(a.fluid,a.topology,a.p_tdp)); return 2
    D["Wpump_W"]=D.Q_LPM.astype(float)/60000*D.dp_field.astype(float)
    sealed=D[np.isclose(D.OR.astype(float),0.0)]
    dup=sealed.Re_label.duplicated(); 
    if dup.any(): print("BLOCKED: more than one sealed row for Re_label",sealed.Re_label[dup].tolist()); return 2
    D["Rth_sealed"]=D.Re_label.map(sealed.set_index("Re_label").Rth_field)
    if D.Rth_sealed.isna().any(): print("BLOCKED: rows without a sealed reference at the same Re_label:",D[D.Rth_sealed.isna()].Re_label.unique().tolist()); return 2
    D["c_rth"]=D.Rth_field.astype(float)/D.Rth_sealed.astype(float); D["c_T"]=D.Tchip_field.astype(float)
    acc=D.accepted.astype(str).str.lower().isin(["true","1","y","yes"]) if "accepted" in D else (D.passed_validity_envelope=="y")   # closure checks and envelope
    D["feasible"]=(D.c_rth<=1+a.tol)&(D.c_T<=a.t_max)&(D.passed_validity_envelope=="y")&acc
    D[["OR","Re_label","Q_LPM","Rth_field","Rth_sealed","c_rth","c_T","dp_field","Wpump_W","passed_validity_envelope","feasible"]].to_csv(a.map_out,index=False)
    feas=D[D.feasible]
    cols=["OR_opt","Re_opt","P_TDP_W","Q_LPM","Rth_KW","Tchip_C","Wpump_W","feasible","status","reason"]
    if feas.empty:
        pd.DataFrame([dict(OR_opt="",Re_opt="",P_TDP_W=a.p_tdp,Q_LPM="",Rth_KW="",Tchip_C="",Wpump_W="",feasible="n",status="NO_FEASIBLE_POINT",reason="no (OR, Re) of the basis satisfies R_th <= %.2f R_th,sealed and T_chip <= %g C; relax the load or the constraint (B5)"%(1+a.tol,a.t_max))],columns=cols).to_csv(a.out,index=False)
        print("No feasible point on the basis at %g W; written to %s"%(a.p_tdp,a.out)); return 0
    o=feas.sort_values("Wpump_W").iloc[0]
    pd.DataFrame([dict(OR_opt=o.OR,Re_opt=o.Re_label,P_TDP_W=a.p_tdp,Q_LPM=o.Q_LPM,Rth_KW=o.Rth_field,Tchip_C=o.Tchip_field,Wpump_W=o.Wpump_W,feasible="y",status="SOLVED",reason="minimum W_pump among %d feasible of %d basis rows (fluid %s, %s, tol %.2f, T_max %g C)"%(len(feas),len(D),a.fluid,a.topology,a.tol,a.t_max))],columns=cols).to_csv(a.out,index=False)
    print("optimum: OR %.2f Re %s W_pump %.4g W (T %.1f C, R_th/R_sealed %.3f); %d feasible rows; written to %s and %s"%(o.OR,o.Re_label,o.Wpump_W,o.Tchip_field,o.c_rth,len(feas),a.out,a.map_out)); return 0
def selftest(a):
    OR=np.tile(np.linspace(0,1,11),5); Re=np.repeat([100,250,500,750,1000],11)
    rth=0.05+0.02*OR**2+10/Re; T=25+700*rth; dp=(1-0.5*OR)*Re*0.2; Q=Re*0.01
    L=pd.DataFrame(dict(OR=OR,Re_label=Re,fluid="FC-40",geometry_label="Plate-Fin",P_TDP=700.0,Rth_field=rth,Tchip_field=T,dp_field=dp,Q_LPM=Q,passed_validity_envelope="y",thermal_data_source="selftest synthetic (not solver-derived; software check only)"))
    if a.out==DEFAULT_OUT: a.out=os.path.join(ROOT,"audit/optimum_selftest.csv")          # honour user-supplied --out / --map-out (e.g. /tmp)
    if a.map_out==DEFAULT_MAP: a.map_out=os.path.join(ROOT,"audit/feasibility_map_selftest.csv")
    rc=run(L,a); r=pd.read_csv(a.out).iloc[0]
    # expected: feasible needs T<=85 -> rth<=0.0857 -> Re>=... ; minimum pump among feasible is the lowest Re with largest OR satisfying the 10 % tolerance
    # known argmin: T <= 85 needs 10/Re <= 0.0357 - 0.02 OR^2 (Re >= 280 at OR 0, so Re = 500 on this grid); the 10 % tolerance allows OR^2 <= 0.25 + 50/Re,
    # i.e. OR <= 0.59 at Re = 500; W_pump grows with Re^2 and falls with OR, so the optimum is (OR 0.5, Re 500), W = 0.01*500/60000 * 0.75 * 100 = 0.00625 W
    ok=(r.status=="SOLVED") and np.isclose(r.OR_opt,0.5) and int(r.Re_opt)==500 and np.isclose(r.Wpump_W,0.00625) and (r.Tchip_C<=85)
    print("SELFTEST known argmin (OR 0.5, Re 500, 0.00625 W) recovered:",ok); return 0 if ok else 1
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--ledger",default=os.path.join(ROOT,"audit/dataset_ledger.csv")); ap.add_argument("--fluid",default="FC-40"); ap.add_argument("--topology",default="Plate-Fin")
    ap.add_argument("--p-tdp",type=float,default=700.0); ap.add_argument("--t-max",type=float,default=85.0); ap.add_argument("--tol",type=float,default=0.10)
    ap.add_argument("--out",default=DEFAULT_OUT); ap.add_argument("--map-out",default=DEFAULT_MAP); ap.add_argument("--selftest",action="store_true"); a=ap.parse_args()
    sys.exit(selftest(a) if a.selftest else run(pd.read_csv(a.ledger),a))
