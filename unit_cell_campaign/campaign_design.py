#!/usr/bin/env python3
"""Design of experiments for the unit-cell calibration campaign (manuscript Sec. 7.1, adapted to the unit cell).
Writes campaign_design.json. Decisions recorded here (see also audit/decisions.md, 'Campaign design'):
- Channel Reynolds levels (manuscript definition, Eq. re_active with Phi = 0, all flow through the fins): nine
  levels 2, 5, 10, 20, 40, 70, 100, 150, 250, spanning the base geometry's operating range (Sec. 2.1: 9 to 104
  at 1 to 3 LPM) and the anchor's split (Sec. 3.4: 1.2 to 227). The archived duct-Reynolds labels are not used.
- Recess ratios 0 to 1 in steps of 0.1 (calibration), intermediate 0.15/0.35/0.65/0.85 (cross-combinations).
- Withheld coolant EFL-1: eleven recess ratios at three levels (10, 40, 150) plus two cross cases.
  PAO-4 is not run: its properties have no source (manuscript Table 3, MISSING).
- Withheld loads: 300, 500, 850, 1000, 1200 W at OR 0, 0.25, 0.5, 0.75, 1.0 and Re 40 (25 cases).
- Cross-combinations: 12 FC-40 cases at the intermediate recess ratios and off-grid Reynolds numbers 7, 15, 30,
  55, 85, 125, 200 (three per recess ratio) plus the two EFL-1 cases (16 total, as in the manuscript's design).
- Grid study (A6): coarse and fine grids at OR 0.1, Re 250, the manuscript's most demanding case (Sec. 4.3).
- Fixed-fin clearance sweep (B1): H_fin = 20.9 mm (Table 1 base sink) with clearance 0, 5, 10, 19.05 mm at Re 40
  (chassis height varied), separating the clearance effect from the fin-height effect.
- Topology holdouts (pin fin, oblique fin) are not representable by the unit cell and are not run."""
import json, itertools, os
OR_CAL=[round(0.1*i,1) for i in range(11)]; RE_CAL=[2,5,10,20,40,70,100,150,250]
cases=[]
def add(cid,fluid,OR,Re,P,parts,grid="medium",Hfin=None,Hc=None):
    cases.append(dict(case_id=cid,fluid=fluid,OR=OR,Re_ch=Re,P_sink_W=P,partitions=parts,grid=grid,H_fin_fixed_m=Hfin,H_chassis_m=Hc))
n=0
for OR in OR_CAL:
    for Re in RE_CAL: n+=1; add("C%03d"%n,"FC-40",OR,Re,700.0,["calibration"])
n=0
for OR in OR_CAL:
    for Re in (10,40,150): n+=1; add("E%03d"%n,"EFL-1",OR,Re,700.0,["holdout_EFL-1"])
n=0
for P in (300.0,500.0,850.0,1000.0,1200.0):
    for OR in (0.0,0.25,0.5,0.75,1.0): n+=1; add("L%03d"%n,"FC-40",OR,40,P,["holdout_thermal_load"])
cross=[(0.15,7),(0.15,30),(0.15,125),(0.35,15),(0.35,55),(0.35,200),(0.65,7),(0.65,85),(0.65,125),(0.85,15),(0.85,55),(0.85,200)]
n=0
for OR,Re in cross: n+=1; add("X%03d"%n,"FC-40",OR,Re,700.0,["cross_combinations"])
add("X013","EFL-1",0.15,15,700.0,["cross_combinations","holdout_EFL-1"]); add("X014","EFL-1",0.65,125,700.0,["cross_combinations","holdout_EFL-1"])
add("G001","FC-40",0.1,250,700.0,["grid_study"],grid="coarse"); add("G002","FC-40",0.1,250,700.0,["grid_study"],grid="fine")   # manuscript Sec. 4.3: most demanding case = smallest non-zero recess ratio, highest Reynolds number (OR 0.1, Re 250); the medium grid point is C018
HB=4.5e-3; HF=20.9e-3
for i,c in enumerate((0.0,5e-3,10e-3,19.05e-3)): add("F%03d"%(i+1),"FC-40",None,40,700.0,["fixed_fin_sweep"],Hfin=HF,Hc=HB+HF+c)
design=dict(meta=dict(description="unit-cell calibration campaign, revision round 3",n_cases=len(cases),Re_levels=RE_CAL,OR_levels=OR_CAL,
            fluids=["FC-40","EFL-1"],excluded="PAO-4 (no property source); pin-fin and oblique-fin topologies (not representable)",
            gravity="none: forced convection (decision of 4 September 2026 after the buoyancy convergence investigation, audit/decisions.md); the Richardson numbers of Sec. 3.3 measure the neglected effect",
            EFL1_buoyancy="not applicable (no body force); EFL-1 density constant 1889 kg/m3 (no expansion coefficient sourced)",
            OR1_convention="OR = 1 (no fins): the bare duct receives the flow rate of the OR = 0 case with the same Re_ch label; Phi = 1 by definition; stated in manuscript Sec. 6.3",
            properties="FC-40 Chun fits tabulated at 20-60 C and clamped outside (validity band); EFL-1 Huang Table 2 points at 20/40/60 C; copper Chun Table 2",
            solver="chtMultiRegionSimpleFoam; GAMG p_rgh, smoothSolver U h; relaxation p 0.3 U 0.7 h 0.9; residual watchdog stops at U, p_rgh 1e-5 and h 1e-6 after 600 iterations (the solver does not act on residualControl); endTime 4000 cap",
            acceptance="residual targets met; monitors stationary over the last 500 iterations (0.5 %); mass split closure 0.5 %; energy balance 0.5 % of load; envelope wall <= 70 C, chip <= 165 C"),cases=cases)
os.makedirs('/mnt/e/ijhmt-cfp/Paper-5/cfd/unit_cell_campaign',exist_ok=True)
json.dump(design,open('/mnt/e/ijhmt-cfp/Paper-5/cfd/unit_cell_campaign/campaign_design.json','w'),indent=1)
import collections; print('cases',len(cases),collections.Counter(p for c in cases for p in c['partitions']))
