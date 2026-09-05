#!/usr/bin/env python3
"""Refit Eq. (23) (bypass fraction) and Eq. (24) (Nusselt number) on a genuine, envelope-filtered
dataset ledger, as specified for revision round 3 (items B2, B3, B8, C2).

Input ledger (audit/dataset_ledger.csv schema): OR, Re column (--re-col), Pr, phi_field
(fraction 0-1), Nu_field, Rth_field, k, D_h, A_wetted, t_fin, H_fin (per case), D_h_over_L
(or --dh-over-l), passed_validity_envelope (y/n), partitions (semicolon-separated names
containing 'calibration' and the holdout names; a holdout row is not a calibration row),
thermal_data_source (must not start with 'none' for the rows used).
R_th is predicted by Eq. (rth_sum), R_fixed + 1/(eta_o h A_wetted) + 1/(m_active cp) with h = Nu_pred k / D_h,
eta_o = 1 - (A_fin/A_wetted)(1 - eta_fin), eta_fin = tanh(mL)/mL, m_active = m_total (1 - Phi_pred);
R_fixed (= R_TIM + R_spread) is the only fitted constant and is fitted on the calibration rows only.
No evaluation row's Rth_field or Nu_field enters its own prediction.
Model: Eq. (23) Phi = 1/(1 + C1 ((1-OR)/(OR+eps))^m (Re/100)^n); Eq. (24)
Nu = (Nu_fd^3 + (C2 Gz^p)^3)^(1/3), Gz = Re_active Pr D_h/L, Re_active = Re (1 - Phi).
Nu_fd is fixed at the Shah-London H1 value for the case aspect ratio (--nu-fd), not fitted.
Output: audit/refit_stats.csv (one row per partition: N, coefficients, SE, 95 % CI, objective,
bounds, Phi MAE [pp], Phi MAPE (OR >= 0.10), R_th MAPE, RMSE, max error, R^2, status, reason).
Refuses (exit 2) when no row carries solver-derived data. --selftest fits synthetic data generated
from the model with known coefficients and checks recovery (a software test, not a result)."""
import sys, os, argparse, numpy as np, pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import t as student_t
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EPS=1e-4
DEFAULT_OUT=os.path.join(ROOT,"audit/refit_stats.csv")
def phi_model(X,C1,m,n):
    o,r=X; return 1/(1+C1*((1-o)/(o+EPS))**m*(r/100)**n)
def nu_model(X,C2,p,nu_fd):
    gz=X; return (nu_fd**3+(C2*gz**p)**3)**(1/3)
def fit(f,X,y,p0,bounds):
    popt,pcov=curve_fit(f,X,y,p0=p0,bounds=bounds,maxfev=20000)
    res=y-f(X,*popt); N=len(y); k=len(popt); se=np.sqrt(np.diag(pcov)); tcrit=student_t.ppf(0.975,max(1,N-k))
    return popt,se,tcrit*se,float(np.sum(res**2))
def eta_fin(nu,S,a):
    h=nu*S.k.values/S.D_h.values; mL=np.sqrt(2*h/(a.k_fin*S.t_fin.values))*S.H_fin.values   # straight fin of height H_fin, base at the root, adiabatic tip
    return np.where(mL>0,np.tanh(mL)/np.maximum(mL,1e-12),1.0)
def eta_o(nu,S,a):
    """Overall surface efficiency, Eq. (eta_o): 1 - (A_fin/A_wetted)(1 - eta_fin); A_fin from the ledger (A_fin_full_m2), else all of A_wetted is fin."""
    frac=(S.A_fin_full_m2.values/S.A_wetted.values) if "A_fin_full_m2" in S else 1.0
    return 1-frac*(1-eta_fin(nu,S,a))
def rth_network(S,nu_p,phi_p,R_fixed,a):
    """Eq. (rth_sum): R_fixed (= R_TIM + R_spread, fitted on the calibration rows) + 1/(eta_o h A_wetted) + 1/(m_active cp),
    h = Nu_pred k / D_h, m_active = m_total (1 - Phi); the Phi passed here is the effective (streamwise-averaged) bypass
    fraction predicted by the second Eq. (23) fit; m_total and cp from the ledger (m_full_kg_s, cp_inlet)."""
    h=nu_p*S.k.values/S.D_h.values; conv=1/(eta_o(nu_p,S,a)*h*S.A_wetted.values)
    if "m_full_kg_s" in S and "cp_inlet" in S: cal=1/(S.m_full_kg_s.values*np.clip(1-phi_p,1e-6,None)*S.cp_inlet.values)
    else: cal=np.zeros_like(conv)
    return R_fixed+conv+cal
def rth_terms(S,nu_p,phi_p,a):
    h=nu_p*S.k.values/S.D_h.values; conv=1/(eta_o(nu_p,S,a)*h*S.A_wetted.values)
    cal=1/(S.m_full_kg_s.values*np.clip(1-phi_p,1e-6,None)*S.cp_inlet.values) if "m_full_kg_s" in S and "cp_inlet" in S else np.zeros_like(conv)
    return conv,cal
def metrics(phi_t,phi_p,rth_t,rth_p,OR):
    out={}
    out["phi_MAE_pp"]=100*float(np.mean(np.abs(phi_p-phi_t)))
    mask=OR>=0.10; out["phi_MAPE"]=100*float(np.mean(np.abs(phi_p[mask]-phi_t[mask])/phi_t[mask])) if mask.any() else float("nan")
    if rth_t is not None:
        e=rth_p-rth_t; out["Rth_MAPE"]=100*float(np.mean(np.abs(e)/rth_t)); out["Rth_RMSE"]=float(np.sqrt(np.mean(e**2))); out["Rth_maxerr"]=float(np.max(np.abs(e)))
        ss=np.sum((rth_t-rth_t.mean())**2); out["R2"]=1-float(np.sum(e**2))/ss if ss>0 else float("nan")
    return out
def run(L,a):
    src=L.get("thermal_data_source",pd.Series(["none"]*len(L))).astype(str)
    usable=~src.str.lower().str.startswith("none")
    if not usable.any():
        print("BLOCKED: no row of the ledger carries solver-derived thermal data (thermal_data_source = %s); refusing to fit formula outputs."%sorted(src.unique())); return 2
    need=["OR",a.re_col,"Pr","phi_field","Nu_field","Rth_field","passed_validity_envelope","partitions","k","D_h","A_wetted","t_fin","H_fin"]; miss=[c for c in need if c not in L]
    if miss: print("BLOCKED: ledger lacks columns",miss); return 2
    keep=usable&(L.passed_validity_envelope=="y")
    if "accepted" in L:   # closure checks (residuals, stationarity, mass split, energy balance) and the envelope, Secs. 4.4 and 6.2
        keep&=L.accepted.astype(str).str.lower().isin(["true","1","y","yes"])
    D=L[keep].copy()
    if "D_h_over_L" not in D: D["D_h_over_L"]=a.dh_over_l
    cal=D[D.partitions.str.contains("calibration")]
    if len(cal)<8: print("BLOCKED: fewer than 8 calibration rows inside the envelope"); return 2
    X=(cal.OR.values.astype(float),pd.to_numeric(cal[a.re_col]).values); bph=([0.01,0.05,-1],[20,4,1])
    pph,seph,ciph,objph=fit(phi_model,X,cal.phi_field.values.astype(float),[1.4,0.4,-0.2],bph)
    # second fit of the same form to the effective (streamwise-averaged) bypass fraction, used in the caloric term of Eq. (rth_sum)
    has_eff="phi_eff_field" in cal and cal.phi_eff_field.notna().all()
    if has_eff: ppe,sepe,cipe,obje=fit(phi_model,X,cal.phi_eff_field.values.astype(float),[1.4,0.4,-0.2],bph)
    else: ppe,sepe,cipe,obje=pph,seph,ciph,objph
    phi_cal=phi_model(X,*pph); phie_cal=phi_model(X,*ppe); gz=pd.to_numeric(cal[a.re_col]).values*np.clip(1-phi_cal,0,None)*cal.Pr.values*cal.D_h_over_L.values
    f24=lambda g,C2,p: nu_model(g,C2,p,a.nu_fd); bnu=([0.05,0.05],[10,1.0])
    pnu,senu,cinu,objnu=fit(f24,gz,cal.Nu_field.values.astype(float),[1.0,0.33],bnu)
    # R_th network: R_th = R_fixed + 1/(eta_fin h A_wetted), h = Nu_pred k / D_h. R_fixed (TIM plus spreading) is the
    # only fitted constant and is fitted on the calibration rows alone; holdout rows never enter it.
    nu_cal=f24(gz,*pnu); conv_cal,cal_cal=rth_terms(cal,nu_cal,phie_cal,a)
    R_fixed=float(np.clip(np.mean(cal.Rth_field.values.astype(float)-conv_cal-cal_cal),0,None))   # R_TIM + R_spread, the only fitted constant of Eq. (rth_sum)
    rows=[]
    names=["calibration"]+sorted({p.strip() for ps in D.partitions for p in ps.split(";") if p.strip() and "calibration" not in p})
    for name in names:
        S=D[D.partitions.str.contains(name,regex=False)]
        if S.empty: continue
        Xs=(S.OR.values.astype(float),pd.to_numeric(S[a.re_col]).values); phi_p=phi_model(Xs,*pph); phie_p=phi_model(Xs,*ppe)
        gzs=Xs[1]*np.clip(1-phi_p,0,None)*S.Pr.values*S.D_h_over_L.values; nu_p=f24(gzs,*pnu)
        rth_p=rth_network(S,nu_p,phie_p,R_fixed,a)   # Eq. (rth_sum) with R_fixed from the calibration rows only
        mt=metrics(S.phi_field.values.astype(float),phi_p,S.Rth_field.values.astype(float),rth_p,Xs[0])
        if has_eff: e=S.phi_eff_field.values.astype(float); mt["phi_eff_MAE_pp"]=100*float(np.mean(np.abs(phie_p-e)))
        nt=S.Nu_field.values.astype(float); mt["Nu_MAPE"]=100*float(np.mean(np.abs(nu_p-nt)/nt))
        rows.append(dict(partition=name,N=len(S),C1=pph[0],m=pph[1],n=pph[2],k="dropped (B3)",C1_eff=ppe[0],m_eff=ppe[1],n_eff=ppe[2],Nu_fd=a.nu_fd,C2=pnu[0],p=pnu[1],R_fixed=R_fixed,
            SE="C1 %.4g; m %.4g; n %.4g; C1_eff %.4g; m_eff %.4g; n_eff %.4g; C2 %.4g; p %.4g"%(*seph,*sepe,*senu),CI95="C1 +-%.4g; m +-%.4g; n +-%.4g; C1_eff +-%.4g; m_eff +-%.4g; n_eff +-%.4g; C2 +-%.4g; p +-%.4g"%(*ciph,*cipe,*cinu),
            objective="SSR phi %.4g; SSR phi_eff %.4g; SSR Nu %.4g"%(objph,obje,objnu),bounds="phi %s; Nu %s"%(bph,bnu),**{k:round(v,4) for k,v in mt.items()},status="FITTED",reason="fit on rows inside the envelope with thermal_data_source = %s"%sorted(set(src[usable]))))
    out=pd.DataFrame(rows); out.to_csv(a.out,index=False); print(out.to_string()); return 0
def selftest(a):
    rng=np.random.default_rng(1); OR=np.tile(np.linspace(0,0.9,10),9); Re=np.repeat([25,50,100,150,250,350,500,750,1000],10).astype(float)
    C1,m,n,C2,p=1.5,0.4,-0.2,0.9,0.4; Pr=np.full(OR.shape,67.5); dhl=np.full(OR.shape,0.016)
    phi=np.clip(phi_model((OR,Re),C1,m,n)*(1+0.01*rng.standard_normal(OR.shape)),0,0.999); nu=nu_model(Re*(1-phi)*Pr*dhl,C2,p,a.nu_fd)*(1+0.01*rng.standard_normal(OR.shape))
    k=np.full(OR.shape,0.0654); Dh=np.full(OR.shape,1.856e-3); Aw=np.full(OR.shape,0.61); tf=np.full(OR.shape,0.25e-3); Hf=np.full(OR.shape,39.95e-3); R_fixed_true=0.012
    mf=np.full(OR.shape,0.05)*Re/100; cp=np.full(OR.shape,1052.0); Af=np.full(OR.shape,0.60)
    S=pd.DataFrame(dict(k=k,D_h=Dh,A_wetted=Aw,t_fin=tf,H_fin=Hf,m_full_kg_s=mf,cp_inlet=cp,A_fin_full_m2=Af)); rth=rth_network(S,nu,phi,R_fixed_true,a)*(1+0.01*rng.standard_normal(OR.shape))
    L=pd.DataFrame(dict(OR=OR,Re_recomputed_ch_Eq1_140mm=Re,Pr=Pr,D_h_over_L=dhl,phi_field=phi,phi_eff_field=phi,Nu_field=nu,Rth_field=rth,k=k,D_h=Dh,A_wetted=Aw,t_fin=tf,H_fin=Hf,m_full_kg_s=mf,cp_inlet=cp,A_fin_full_m2=Af,passed_validity_envelope="y",partitions="calibration",thermal_data_source="selftest synthetic (not solver-derived; software check only)"))
    L.loc[::7,"partitions"]="holdout-synthetic"   # exclusive holdout: these rows are not in the calibration set
    if a.out==DEFAULT_OUT: a.out=os.path.join(ROOT,"audit/refit_stats_selftest.csv")   # honour a user-supplied --out (e.g. /tmp) in read-only sandboxes
    rc=run(L,a); T=pd.read_csv(a.out).set_index("partition"); r=T.loc["calibration"]
    ok=all(abs(r[kk]-v)/abs(v)<0.05 for kk,v in dict(C1=C1,m=m,n=n,C2=C2,p=p,R_fixed=R_fixed_true).items()) and T.loc["holdout-synthetic","Rth_MAPE"]<3 and T.loc["holdout-synthetic","N"]==13
    print("SELFTEST recovery within 5 %% (C1, m, n, C2, p, R_fixed) and holdout R_th MAPE < 3 %%: %s"%ok); return 0 if ok else 1
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--ledger",default=os.path.join(ROOT,"audit/dataset_ledger.csv")); ap.add_argument("--re-col",default="Re_recomputed_ch_Eq1_140mm")
    ap.add_argument("--nu-fd",type=float,default=7.85,help="Shah-London H1 asymptote for the case aspect ratio (7.85 at alpha 0.024)"); ap.add_argument("--dh-over-l",type=float,default=1.856e-3/0.118)
    ap.add_argument("--out",default=DEFAULT_OUT); ap.add_argument("--k-fin",type=float,default=387.6,help="fin conductivity [W/m K]"); ap.add_argument("--selftest",action="store_true"); a=ap.parse_args()
    sys.exit(selftest(a) if a.selftest else run(pd.read_csv(a.ledger),a))
