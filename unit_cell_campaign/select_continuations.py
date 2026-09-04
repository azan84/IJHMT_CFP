#!/usr/bin/env python3
"""Select finished cases to continue: (a) stopped at the iteration cap (no ENVELOPE_STOP) inside the wall bound of the validity envelope (max interface temperature <= 70 C) and short of the acceptance residuals
(U, p_rgh < 1e-4; h < 1e-6), or (b) converged before 1200 iterations, so that the 500-iteration stationarity
window lies past the initial transient. Writes CONTINUE in each selected case, sets its endTime, and prints the list file."""
import sys, os, glob, re
ROOT=os.path.dirname(os.path.abspath(__file__)); END=int(sys.argv[1]) if len(sys.argv)>1 else 12000; OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,"run_list_continue.txt")
def tsort(fs): return sorted(fs,key=lambda f: float(os.path.basename(os.path.dirname(f))))
sel=[]
for d in sorted(glob.glob(os.path.join(ROOT,"cases/*/DONE"))):
    c=os.path.dirname(d)
    if os.path.exists(c+"/ENVELOPE_STOP"): continue
    fs=tsort(glob.glob(c+"/postProcessing/fluid/residuals/*/solverInfo.dat"))
    if not fs: continue
    lines=[l for l in open(fs[-1]) if l.strip()]; hdr=[h.strip() for h in [l for l in lines if l.startswith("# Time")][0].strip("# \n").split("\t")]
    row=dict(zip(hdr,[x.strip() for x in [l for l in lines if not l.startswith("#")][-1].split("\t")])); it=int(float(row["Time"]))
    r={k:float(row[k]) for k in ("Ux_initial","Uy_initial","Uz_initial","p_rgh_initial","h_initial")}
    met=max(r["Ux_initial"],r["Uy_initial"],r["Uz_initial"])<1e-4 and r["p_rgh_initial"]<1e-4 and r["h_initial"]<1e-6
    tf=tsort(glob.glob(c+"/postProcessing/fluid/ifaceTmax/*/*.dat")); tw=float([l.split() for l in open(tf[-1]) if l.strip() and not l.startswith("#")][-1][1]) if tf else float("nan")
    short=it<1200   # stopped before 1200 iterations: the 500-iteration stationarity window reaches into the transient; continue to >= 1200
    if (met and not short) or tw>273.15+70.0 or it>=END: continue
    cd=c+"/system/controlDict"; s=open(cd).read(); s=re.sub(r"endTime\s+\d+;","endTime         %d;"%END,s,count=1); s=s.replace("stopAt writeNow;","stopAt endTime;"); open(cd,"w").write(s)
    open(c+"/CONTINUE","w").write("pass1 iterations %d, wall max %.2f C, residuals %s\n"%(it,tw-273.15,r)); sel.append(c)
open(OUT,"w").write("\n".join(sel)+("\n" if sel else "")); print("selected",len(sel),"cases ->",OUT); [print(" ",os.path.basename(c)) for c in sel]
