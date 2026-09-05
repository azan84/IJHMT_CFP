#!/usr/bin/env python3
"""Verification: pressure drop of the sealed unit-cell cases (OR = 0) against the fully developed laminar value of
Shah and London for a rectangular duct of aspect ratio alpha = s/H_fin, f_D Re = 96 (1 - 1.3553 a + 1.9467 a^2 - 1.7012 a^3
+ 0.9564 a^4 - 0.2537 a^5), dp = f_D Re mu u_ch L / (2 D_h^2), with the viscosity of Table 3 at the inlet temperature, at the
mean channel bulk temperature and at the film temperature. Input: cfd/unit_cell_campaign/dataset_ledger_unitcell.csv and
the case metadata; output audit/sealed_dp_check.csv."""
import os, sys, json, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); C=os.path.join(ROOT,"cfd/unit_cell_campaign"); sys.path.insert(0,C); import unit_cell as u
d=pd.read_csv(os.path.join(C,"dataset_ledger_unitcell.csv")); s=d[(d.OR==0)&(d.fluid=="FC-40")&(d.partitions.str.contains("calibration"))].sort_values("Re_ch")
rows=[]
for r in s.itertuples():
    m=json.load(open(os.path.join(C,"cases",r.case_id,"case_meta.json"))); Hf=m["H_fin_m"]; Dh=m["D_h_m"]; uch=m["u_in_m_s"]*(u.S/2+u.TF/2)/(u.S/2)
    a=u.S/Hf; fReD=96*(1-1.3553*a+1.9467*a**2-1.7012*a**3+0.9564*a**4-0.2537*a**5)
    def dp_sl(T): p=u.FLUIDS["FC-40"](min(max(T,293.15),333.15)); return fReD*p["mu"]*uch*u.L/(2*Dh**2)
    Tb=0.5*(r.T_ch_in_K+r.T_ch_out_K); Tf=0.5*(r.T_wall_mean_K+Tb)
    rows.append(dict(case_id=r.case_id,Re_ch=r.Re_ch,u_ch_m_s=uch,alpha=a,fD_Re=fReD,dp_cfd_Pa=r.dp_sink_Pa,dp_SL_Tin_Pa=dp_sl(u.T_IN),ratio_Tin=r.dp_sink_Pa/dp_sl(u.T_IN),
                     T_bulk_mean_K=Tb,dp_SL_Tbulk_Pa=dp_sl(Tb),ratio_Tbulk=r.dp_sink_Pa/dp_sl(Tb),T_film_K=Tf,dp_SL_Tfilm_Pa=dp_sl(Tf),ratio_Tfilm=r.dp_sink_Pa/dp_sl(Tf),accepted=r.accepted))
o=pd.DataFrame(rows); o.to_csv(os.path.join(ROOT,"audit/sealed_dp_check.csv"),index=False); print(o[["case_id","Re_ch","dp_cfd_Pa","dp_SL_Tin_Pa","ratio_Tin","ratio_Tbulk","ratio_Tfilm"]].to_string(index=False,float_format=lambda x:"%.4g"%x))
