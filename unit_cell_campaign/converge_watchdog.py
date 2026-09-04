#!/usr/bin/env python3
"""Stop a running chtMultiRegionSimpleFoam case by setting stopAt writeNow in the run-time-modifiable controlDict
(a) once the fluid residual targets are met (manuscript Sec. 3.5, tightened: Ux, Uy, Uz, p_rgh < 1e-5 and h < 1e-6)
after a minimum number of iterations -> CONVERGED_STOP; or (b) once the case has passed the envelope-check
iteration (default 4000) with a maximum interface temperature above the validity-envelope wall bound (70 C,
manuscript Sec. 6.2): such a case is excluded from the dataset whatever its residuals, so it is not continued
-> ENVELOPE_STOP. Usage: converge_watchdog.py <case> <min_iter> <poll_s> [envelope_iter]"""
import sys, os, glob, time
case=sys.argv[1]; min_iter=int(sys.argv[2]); poll=float(sys.argv[3]); env_iter=int(sys.argv[4]) if len(sys.argv)>4 else 4000
TH=dict(Ux_initial=1e-5,Uy_initial=1e-5,Uz_initial=1e-5,p_rgh_initial=1e-5,h_initial=1e-6); T_WALL_MAX=273.15+70.0
def tsort(fs): return sorted(fs,key=lambda f: float(os.path.basename(os.path.dirname(f))))
def last_row():
    fs=tsort(glob.glob(os.path.join(case,"postProcessing/fluid/residuals/*/solverInfo.dat")))
    if not fs: return None
    lines=[l for l in open(fs[-1]) if l.strip()]
    hdr=[h.strip() for h in [l for l in lines if l.startswith("# Time")][0].strip("# \n").split("\t")]
    data=[l for l in lines if not l.startswith("#")]
    if not data: return None
    row=[x.strip() for x in data[-1].split("\t")]; return dict(zip(hdr,row))
def wall_tmax():
    fs=tsort(glob.glob(os.path.join(case,"postProcessing/fluid/ifaceTmax/*/*.dat")))
    if not fs: return None
    data=[l.split() for l in open(fs[-1]) if l.strip() and not l.startswith("#")]
    if not data: return None
    try: return float(data[-1][1])
    except: return None
def stop(tag,msg):
    cd=os.path.join(case,"system/controlDict"); s=open(cd).read()
    if "stopAt endTime;" in s:
        open(cd,"w").write(s.replace("stopAt endTime;","stopAt writeNow;")); open(os.path.join(case,tag),"w").write(msg+"\n")
while True:
    time.sleep(poll)
    if os.path.exists(os.path.join(case,"DONE")) or not os.path.exists(os.path.join(case,"log.chtMultiRegionSimpleFoam")): break
    log=open(os.path.join(case,"log.chtMultiRegionSimpleFoam")).read()
    if "\nEnd\n" in log[-2000:]: break
    d=last_row()
    if not d: continue
    try: it=int(float(d["Time"]))
    except: continue
    if it<min_iter: continue
    if all(float(d.get(k,1.0))<v for k,v in TH.items()):
        stop("CONVERGED_STOP","iteration %d: %s"%(it,{k:d[k] for k in TH})); break
    if it>=env_iter:
        tw=wall_tmax()
        if tw is not None and tw>T_WALL_MAX:
            stop("ENVELOPE_STOP","iteration %d: max interface temperature %.2f K above the 70 C wall bound; residuals %s"%(it,tw,{k:d[k] for k in TH})); break
