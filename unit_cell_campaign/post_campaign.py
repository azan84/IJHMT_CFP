#!/usr/bin/env python3
"""Post-process the unit-cell campaign into a dataset ledger (manuscript Secs. 3.5, 4.4, 5, 6.2, 7).
Per case, from the runtime monitors (postProcessing/*/<name>/<time>/*.dat, last row and the last 500 iterations):
  dp_sink_Pa      = areaAverage(inlet p) - areaAverage(outlet p)                     [static pressure, Pa]
  Phi_in, Phi_mid = |sum phi over clearance zone| / (|channel zone| + |clearance zone|) at x = 0 and x = L/2
  mass_split_closure_pct = |(chan + clear) - inlet| / inlet at x = 0                [manuscript Sec. 4.4, 0.5 %]
  energy_balance_pct     = |Q_in - (H_out - H_in)| / Q_in, Q_in = heated integral, H = sum(phi h)   [Sec. 3.5, 0.5 %]
  T_base_max/mean (heated patch), T_wall_max (fluid_to_solid max), T_out_bulk (mass-weighted)
  Nu (ledger; NaN by construction at OR = 1, where no fin channel exists): length-averaged form from five streamwise interface bins (posthoc_zone_T.py version 2): h_m = q''_mean / dT_mean,
  q''_mean = sum Q_i / sum A_i, dT_mean = area-weighted mean of (bin-mean interface T - mean channel bulk T at the bin ends,
  mass-flux weighted at the six stations); Nu = h_m D_h / k(T_film); Nu_B0..B4 local per bin; Phi_X0..X5 clearance share
  at the six stations. Also Nu_edge (leading/trailing-edge channel bulk, version 1), Nu_cell (cell-mixed bulk) and
  Nu_lmtd (isothermal-wall log-mean form, undefined at Re_ch <= 10) ; Re_ch (design) ; Re_active = Re_ch (1 - Phi_in)
  R_base = (T_base_max - T_in) / P_sink ; R_th = R_base + R_TIM (Eq. tim: 6e-3 K/W over 48 x 68 mm; R_spread MISSING)
  acceptance: residual targets met (solverInfo), stationarity of the four monitors over the last 500 iterations
  (0.5 %), mass split 0.5 %, energy 0.5 %, envelope wall <= 70 C and chip <= 165 C.
Output: dataset_ledger_unitcell.csv with the columns figures/src/refit_closures.py and solve_eq22.py expect."""
import os, sys, json, glob, math, csv, re
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import unit_cell as u
ROOT=os.path.dirname(os.path.abspath(__file__))
R_TIM=6.0e-3   # manuscript Eq. (tim): 1.9e-5 m2 K/W over the 48 x 68 mm package

def read_dat(case,region,name,col=1):
    fs=sorted(glob.glob(os.path.join(case,"postProcessing",region,name,"*","*.dat")),key=lambda f: float(os.path.basename(os.path.dirname(f))))   # numeric time order (restarts add 4000/, 12000/ ...)
    rows=[]
    for f in fs:
        for line in open(f):
            if line.startswith("#") or not line.strip(): continue
            parts=line.split()
            try: rows.append((float(parts[0]),float(parts[col])))
            except: pass
    return np.array(rows) if rows else np.zeros((0,2))
def last(a): return float(a[-1,1]) if len(a) else float("nan")
def stationary(a,window=500,tol=0.005):
    if len(a)<3: return False, float("nan")
    t=a[:,0]; sel=a[t>=t[-1]-window,1]
    ref=abs(sel).max() if abs(sel).max()>0 else 1.0
    var=(sel.max()-sel.min())/ref; return var<=tol, float(var)
def whf(case,region,name,patch):
    fs=sorted(glob.glob(os.path.join(case,"postProcessing",region,name,"*","wallHeatFlux.dat"))); val=float("nan")
    for f in fs:
        for line in open(f):
            if line.startswith("#"): continue
            p=line.split()
            if len(p)>=5 and p[1]==patch: val=float(p[4])
    return val
def process(case):
    meta=json.load(open(os.path.join(case,"case_meta.json"))); out=dict(case_id=os.path.basename(case),**{k:meta[k] for k in ("fluid","OR","Re_ch","P_sink_W","grid","H_fin_m","clearance_m","D_h_m","A_wetted_full_m2","u_in_m_s","Q_full_sink_LPM","cells")})
    done=os.path.join(case,"DONE"); out["run"]=open(done).read().strip() if os.path.exists(done) else "not run"
    pin=read_dat(case,"fluid","inletP",col=2); pout=read_dat(case,"fluid","outletP",col=2); phin=read_dat(case,"fluid","inletPhi")   # column 2 = areaAverage(p_rgh): static pressure without the hydrostatic column
    ch_in=read_dat(case,"fluid","chanInPhi"); cl_in=read_dat(case,"fluid","clearInPhi"); ch_mid=read_dat(case,"fluid","chanMidPhi"); cl_mid=read_dat(case,"fluid","clearMidPhi")
    Hin=read_dat(case,"fluid","inletH"); Hout=read_dat(case,"fluid","outletH"); Tout=read_dat(case,"fluid","outletTbulk")
    Tw=read_dat(case,"fluid","ifaceT"); Twmax=read_dat(case,"fluid","ifaceTmax"); Tb=read_dat(case,"solid","heatedT"); Tbmax=read_dat(case,"solid","heatedTmax")
    out["dp_sink_Pa"]=last(pin)-last(pout)
    m_in=abs(last(phin)); ch=abs(last(ch_in)) if len(ch_in) else 0.0; cl=abs(last(cl_in)) if len(cl_in) else 0.0; out["m_in_kg_s"]=m_in   # an absent zone (OR 0 clearance, OR 1 channel) carries no flow
    out["Phi_in"]=cl/(ch+cl) if (ch+cl)>0 else float("nan"); out["mass_split_closure_pct"]=100*abs((ch+cl)-m_in)/m_in if m_in>0 else float("nan")
    chm=abs(last(ch_mid)) if len(ch_mid) else 0.0; clm=abs(last(cl_mid)) if len(cl_mid) else 0.0; out["Phi_mid"]=clm/(chm+clm) if (chm+clm)>0 else float("nan")
    Qin=whf(case,"solid","whfSolid","heated"); Qw=whf(case,"fluid","whfFluid","fluid_to_solid"); dH=last(Hout)-last(Hin)   # sum(phi h): inlet phi is negative (into the domain) so H_out - H_in = enthalpy rise... phi<0 at inlet -> Hin negative
    out["Q_in_W"]=Qin; out["Q_wall_fluid_W"]=Qw; out["dH_W"]=last(Hout)+last(Hin)   # both sums carry the sign of phi: outlet +, inlet -; enthalpy rise = sum_out + sum_in
    out["energy_balance_pct"]=100*abs(Qin-out["dH_W"])/Qin if Qin else float("nan")
    T_in=u.T_IN; out["T_in_K"]=T_in; out["T_out_bulk_K"]=last(Tout); out["T_wall_mean_K"]=last(Tw); out["T_wall_max_K"]=last(Twmax); out["T_base_mean_K"]=last(Tb); out["T_base_max_K"]=last(Tbmax)
    # post-hoc face-zone bulk temperatures and fluxes at the sink leading and trailing edges (posthoc_zone_T.py)
    pz=os.path.join(case,"posthoc_zoneT.json")
    dn=os.path.join(case,"DONE")
    def _stale(pz):
        if not os.path.exists(pz): return True
        try: return json.load(open(pz)).get("version",1)<2   # version-1 extraction (edges only): the streamwise bins are needed
        except Exception: return True
    if os.path.exists(dn) and (_stale(pz) or os.path.getmtime(pz)<=os.path.getmtime(dn)):   # a case without DONE (running) keeps whatever extraction it has
        import posthoc_zone_T; posthoc_zone_T.process(case)
    Z=json.load(open(pz)) if os.path.exists(pz) else {}
    out["T_ch_in_K"]=Z.get("T_chanIn_K",float("nan")); out["T_ch_out_K"]=Z.get("T_chanOut_K",float("nan")); out["T_cl_out_K"]=Z.get("T_clearOut_K",float("nan"))
    cho=abs(Z.get("phi_chanOut_kg_s",0.0)); clo=abs(Z.get("phi_clearOut_kg_s",0.0)); out["Phi_out"]=clo/(cho+clo) if (cho+clo)>0 else float("nan")
    # wetted area of the half-pitch cell: fin faces (both sides of the half fin = one face of height H_fin, length L) + channel floor (s/2 x L) + fin tip (t_f/2 x L, if clearance > 0)
    Hf=meta["H_fin_m"]; A_cell=Hf*u.L+(u.S/2)*u.L; out["A_wetted_cell_m2"]=A_cell   # manuscript A_wetted: fin faces plus channel floor (fin tips excluded), consistent with A_wetted_full
    q=abs(Qw)/A_cell if A_cell>0 else float("nan"); dT1=out["T_wall_mean_K"]-T_in; dT2=out["T_wall_mean_K"]-out["T_out_bulk_K"]
    # Driving temperature difference. The log-mean difference (LMTD, isothermal-wall form) is undefined when the outlet bulk
    # exceeds the mean interface temperature, which occurs at Re_ch <= 10 where the wall temperature rises along the sink by
    # more than the wall-to-bulk difference (uniform-flux base). The arithmetic-mean bulk difference, T_wall,mean - (T_in + T_out)/2,
    # is the uniform-heat-flux form consistent with the Shah-London H1 asymptote and is defined for every case; it is the
    # ledger's Nu. The LMTD value is kept as Nu_lmtd (NaN where undefined). Decision: audit/decisions.md, 4 September 2026.
    dT_am=out["T_wall_mean_K"]-0.5*(T_in+out["T_out_bulk_K"])   # cell-mixed bulk (whole cell flow at the domain inlet and outlet)
    dT_ch=out["T_wall_mean_K"]-0.5*(out["T_ch_in_K"]+out["T_ch_out_K"]) if out["T_ch_in_K"]==out["T_ch_in_K"] and out["T_ch_out_K"]==out["T_ch_out_K"] else float("nan")   # channel stream at the sink leading and trailing edges
    lmtd=(dT1-dT2)/math.log(dT1/dT2) if dT1>0 and dT2>0 and abs(dT1-dT2)>1e-9 else float("nan")
    out["dT_wall_bulk_am_K"]=dT_am; out["dT_lmtd_K"]=lmtd; out["T_out_over_T_wall_mean"]=(out["T_out_bulk_K"]-T_in)/dT1 if dT1>0 else float("nan")
    Tfilm=0.5*(out["T_wall_mean_K"]+0.5*(T_in+out["T_out_bulk_K"])); pf=u.FLUIDS[meta["fluid"]](min(max(Tfilm,293.15),333.15))
    out["dT_wall_chbulk_K"]=dT_ch
    out["h_cell_W_m2K"]=q/dT_am if dT_am>0 else float("nan"); out["Nu_cell"]=out["h_cell_W_m2K"]*meta["D_h_m"]/pf["k"]
    out["h_edge_W_m2K"]=q/dT_ch if dT_ch==dT_ch and dT_ch>0 else float("nan"); out["Nu_edge"]=out["h_edge_W_m2K"]*meta["D_h_m"]/pf["k"]   # version-1 form: leading/trailing-edge channel bulk
    out["k_film"]=pf["k"]; out["Pr_film"]=pf["mu"]*pf["cp"]/pf["k"]
    # Ledger Nu (version 2): length-averaged form from five streamwise interface bins. Per bin i: wall heat flux Q_i / A_i,
    # bin-mean interface temperature Tw_i, channel bulk at the bin ends from the mass-flux-weighted station temperatures.
    # h_m = q''_mean / dT_mean with q''_mean = sum Q_i / sum A_i and dT_mean the area-weighted mean of (Tw_i - Tb_i);
    # Nu_B<i> are the local values per bin (thermal development along the sink). Decision: audit/decisions.md, 5 September 2026.
    NB=5; ok=Z.get("version",1)>=2 and all(("Tw_wallB%d_K"%i) in Z for i in range(NB)) and all(("T_chanX%d_K"%i) in Z for i in range(NB+1))
    if ok:
        A=[Z["A_wallB%d_m2"%i] for i in range(NB)]; Tw=[Z["Tw_wallB%d_K"%i] for i in range(NB)]; Qb=[abs(Z["Q_wallB%d_W"%i]) for i in range(NB)]
        Tb=[0.5*(Z["T_chanX%d_K"%i]+Z["T_chanX%d_K"%(i+1)]) for i in range(NB)]; dT=[Tw[i]-Tb[i] for i in range(NB)]
        dT_mean=sum(A[i]*dT[i] for i in range(NB))/sum(A); q_mean=sum(Qb)/sum(A)
        out["dT_wall_bulk_bins_K"]=dT_mean; out["Q_bins_sum_W"]=sum(Qb); out["A_bins_sum_m2"]=sum(A)
        out["h_W_m2K"]=q_mean/dT_mean if dT_mean>0 else float("nan"); out["Nu"]=out["h_W_m2K"]*meta["D_h_m"]/pf["k"]
        for i in range(NB):
            hi=(Qb[i]/A[i])/dT[i] if dT[i]>0 else float("nan"); out["Nu_B%d"%i]=hi*meta["D_h_m"]/pf["k"]; out["dT_B%d_K"%i]=dT[i]
        for i in range(NB+1):
            chp=abs(Z.get("phi_chanX%d_kg_s"%i,0.0)); clp=abs(Z.get("phi_clearX%d_kg_s"%i,0.0)); out["Phi_X%d"%i]=clp/(chp+clp) if (chp+clp)>0 else float("nan")
        # effective bypass fraction for the caloric term: the channel loses mass along the sink, so the bulk rise follows
        # int dx/(m_ch(x) cp); Phi_eff = 1 - 1/<1/(1-Phi(x))> with the trapezoidal mean over the six stations (Phi_eff >= Phi_X0)
        ph=[out["Phi_X%d"%i] for i in range(NB+1)]
        if all(v==v for v in ph) and all(v<1 for v in ph):
            inv=[1/(1-v) for v in ph]; mean_inv=sum(0.5*(inv[i]+inv[i+1]) for i in range(NB))/NB; out["Phi_eff"]=1-1/mean_inv
        else: out["Phi_eff"]=float("nan")
    else:
        out["h_W_m2K"]=float("nan"); out["Nu"]=float("nan"); out["dT_wall_bulk_bins_K"]=float("nan")
        for i in range(NB): out["Nu_B%d"%i]=float("nan"); out["dT_B%d_K"%i]=float("nan")
        for i in range(NB+1): out["Phi_X%d"%i]=float("nan")
        out["Phi_eff"]=float("nan")
    out["h_lmtd_W_m2K"]=q/lmtd if lmtd==lmtd and lmtd>0 else float("nan"); out["Nu_lmtd"]=out["h_lmtd_W_m2K"]*meta["D_h_m"]/pf["k"]
    pin_=u.FLUIDS[meta["fluid"]](T_in); out["Pr_inlet"]=pin_["mu"]*pin_["cp"]/pin_["k"]
    out["Re_active"]=meta["Re_ch"]*(1-out["Phi_in"]) if not math.isnan(out["Phi_in"]) else float("nan")
    P=meta["P_sink_W"]; out["R_base_K_W"]=(out["T_base_max_K"]-T_in)/P; out["R_th_K_W"]=out["R_base_K_W"]+R_TIM; out["R_TIM_K_W"]=R_TIM; out["R_spread_K_W"]="MISSING"
    out["W_pump_W"]=meta["Q_half_m3_s"]*2*u.NFIN_SPAN*out["dp_sink_Pa"]   # full 140 mm span
    out["N_fin"]=u.NFIN_SPAN; out["m_full_kg_s"]=m_in*2*u.NFIN_SPAN; out["cp_inlet"]=pin_["cp"]; out["A_fin_full_m2"]=2*Hf*u.L*u.NFIN_SPAN   # Eq. (rth_sum): caloric term and overall surface efficiency
    out["solver_rc"]=int(re.search(r"rc=(-?\d+)",out["run"]).group(1)) if re.search(r"rc=(-?\d+)",out["run"]) else -1
    # residuals: last row of solverInfo (columns: U_converged at index 11, h_converged, p_rgh_converged flags are 'true/false' strings)
    sol=sorted(glob.glob(os.path.join(case,"postProcessing/fluid/residuals/*/solverInfo.dat")),key=lambda f: float(os.path.basename(os.path.dirname(f))))
    res={}
    if sol:
        hdr=[l for l in open(sol[-1]) if l.startswith("# Time")][0].strip("# \n").split("\t"); hdr=[h.strip() for h in hdr]
        lastl=[l for l in open(sol[-1]) if not l.startswith("#") and l.strip()][-1].split("\t"); lastl=[x.strip() for x in lastl]
        for k in ("Ux_initial","Uy_initial","Uz_initial","h_initial","p_rgh_initial"):
            if k in hdr: res[k]=float(lastl[hdr.index(k)])
        out["iterations"]=int(float(lastl[0]))
    out.update({"res_"+k:v for k,v in res.items()})
    out["residuals_met"]=bool(res) and max(res.get("Ux_initial",1),res.get("Uy_initial",1),res.get("Uz_initial",1))<1e-4 and res.get("h_initial",1)<1e-6 and res.get("p_rgh_initial",1)<1e-4
    st={}
    for nm,a in (("T_base",Tbmax),("dp",pin),("Phi",cl_in if len(cl_in) else ch_in),("energy",Hout)):   # at OR 0 the clearance zone is absent (Phi = 0 by construction): the channel flux stands in
        ok,var=stationary(a); st[nm]=(ok,var)
    out["stationary"]=all(v[0] for v in st.values()); out["stationarity_max_var"]=max((v[1] for v in st.values()),default=float("nan"))
    out["passed_mass_split"]=out["mass_split_closure_pct"]<=0.5; out["passed_energy"]=out["energy_balance_pct"]<=0.5
    out["T_chip_max_C"]=out["T_base_max_K"]-273.15+P*R_TIM   # base maximum plus the TIM drop (spreading MISSING)
    out["passed_validity_envelope"]="y" if (out["T_wall_max_K"]-273.15<=70.0 and out["T_chip_max_C"]<=165.0) else "n"
    out["converged"]=bool(out["residuals_met"] and out["stationary"] and out["passed_mass_split"] and out["passed_energy"])
    # how the run ended: converged (watchdog residual stop), envelope (watchdog envelope stop), diverged (solver exit code != 0), cap (ran to endTime)
    out["stop_type"]="converged" if os.path.exists(os.path.join(case,"CONVERGED_STOP")) else ("envelope" if os.path.exists(os.path.join(case,"ENVELOPE_STOP")) else ("diverged" if out["solver_rc"]!=0 else "cap"))
    out["accepted"]=bool(out["converged"] and out["passed_validity_envelope"]=="y")   # acceptance = closure checks and the validity envelope (manuscript Secs. 3.5, 4.4, 6.2)
    return out
if __name__=="__main__":
    design=json.load(open(os.path.join(ROOT,"campaign_design.json")))
    cases=[os.path.join(ROOT,"cases",c["case_id"]) for c in design["cases"]] if len(sys.argv)<2 else sys.argv[1:]
    parts={c["case_id"]:";".join(c["partitions"]) for c in design["cases"]}
    rows=[]
    for c in cases:
        if not os.path.exists(os.path.join(c,"case_meta.json")): continue
        if len(sys.argv)<2 and not os.path.exists(os.path.join(c,"DONE")): continue   # the campaign ledger holds finished cases only
        r=process(c); r["partitions"]=parts.get(r["case_id"],"pilot"); rows.append(r)
    # ledger columns for the refit scripts
    for r in rows:
        r.update(dict(Re_recomputed_ch_Eq1_140mm=r["Re_ch"],Pr=r["Pr_inlet"],phi_field=r["Phi_in"],phi_eff_field=r.get("Phi_eff",float("nan")),Nu_field=r["Nu"],Rth_field=r["R_th_K_W"],k=r["k_film"],D_h=r["D_h_m"],A_wetted=r["A_wetted_full_m2"],t_fin=u.TF,H_fin=r["H_fin_m"],
                      D_h_over_L=r["D_h_m"]/u.L,Re_label=r["Re_ch"],geometry_label="Plate-Fin",P_TDP=r["P_sink_W"],Tchip_field=r["T_chip_max_C"],dp_field=r["dp_sink_Pa"],Q_LPM=r["Q_full_sink_LPM"],
                      thermal_data_source="chtMultiRegionSimpleFoam unit cell (this campaign)"))
    out=os.environ.get("POST_OUT") or (os.path.join(ROOT,"dataset_ledger_unitcell.csv") if len(sys.argv)<2 else os.path.join(ROOT,"pilot_results.csv"))   # POST_OUT overrides the output path
    keys=sorted({k for r in rows for k in r},key=lambda k:(k!="case_id",k))
    with open(out,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print("wrote",out,len(rows),"rows")
    for r in rows: print(r["case_id"],"OR",r["OR"],"Re",r["Re_ch"],"| dp %.4g Pa Phi_in %.4f Phi_mid %.4f | split %.3g%% energy %.3g%% | Tbase max %.2f C wall max %.2f C | Nu %.3f h %.1f | R_base %.5f | it %s res_met %s stat %s acc %s"%(r["dp_sink_Pa"],r["Phi_in"],r["Phi_mid"],r["mass_split_closure_pct"],r["energy_balance_pct"],r["T_base_max_K"]-273.15,r["T_wall_max_K"]-273.15,r["Nu"],r["h_W_m2K"],r["R_base_K_W"],r.get("iterations"),r["residuals_met"],r["stationary"],r["accepted"]))
