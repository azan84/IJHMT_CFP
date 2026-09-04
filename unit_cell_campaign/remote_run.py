#!/usr/bin/env python3
"""Run a share of the unit-cell calibration campaign on a second machine and push the results back to the
repository. Everything the cases need is built here from the audited design (campaign_design.json, unit_cell.py) and
verified against the checksum manifest of the local build (manifest_local_build.json) before any solve starts.

Steps: 0 environment (OpenFOAM v2406, mpirun, git), 1 resources (physical cores, RAM, load) and the number of cores
to use (asked interactively unless --cores is given), 2 build the listed cases and verify them, 3 run the cases
N at a time with 8 MPI ranks each (decomposePar, chtMultiRegionSimpleFoam with the convergence/envelope watchdog,
reconstructPar of the latest time, post-hoc zone extraction), pack each finished case's monitors and logs into
results/<case>.tar.gz and push, 4 continuation pass for cases that stopped short of the acceptance residuals or
before 1200 iterations, 5 final push. Resumable: finished cases (DONE) are skipped.

Usage: python3 remote_run.py [--list run_list_remote.txt] [--cores N] [--no-push] [--test [--test-push]]
  --test builds and runs the first listed case for 60 iterations only (pipeline check; results not pushed unless
  --test-push). Each case uses 8 MPI ranks (fixed by the audited decomposeParDict)."""
import os, sys, re, json, time, shutil, argparse, subprocess, threading, tarfile, glob
ROOT=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(ROOT)
LOG=open(os.path.join(ROOT,"remote_run.log"),"a")
def log(msg):
    line="%s %s"%(time.strftime("%F %T"),msg); print(line,flush=True); LOG.write(line+"\n"); LOG.flush()
def sh(cmd,cwd=None,logfile=None,env=None):
    if logfile:
        with open(logfile,"w") as f: return subprocess.call(["bash","-c",cmd],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,env=env)
    return subprocess.call(["bash","-c",cmd],cwd=cwd,env=env)
def out(cmd,cwd=None):
    return subprocess.run(["bash","-c",cmd],cwd=cwd,capture_output=True,text=True).stdout
# ---------- 0 environment ----------
OF_CANDIDATES=["/usr/lib/openfoam/openfoam2406/etc/bashrc","/opt/openfoam2406/etc/bashrc","/opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc",
               os.path.expanduser("~/OpenFOAM/OpenFOAM-v2406/etc/bashrc"),"/usr/lib/openfoam/openfoam2412/etc/bashrc"]
def find_openfoam():
    if shutil.which("chtMultiRegionSimpleFoam"): return ""   # already in the environment
    for b in OF_CANDIDATES:
        if os.path.exists(b) and "chtMultiRegionSimpleFoam" in out("source %s >/dev/null 2>&1; which chtMultiRegionSimpleFoam"%b): return "source %s >/dev/null 2>&1; "%b
    sys.exit("OpenFOAM v2406 not found: chtMultiRegionSimpleFoam is not in PATH and no etc/bashrc was found at %s. Source your OpenFOAM bashrc and rerun."%OF_CANDIDATES)
OF=find_openfoam(); PRE=OF
if OF: os.environ["OPENFOAM_BASHRC"]=OF.split()[1]   # the builder and the zone extraction source the same bashrc
def check_env():
    ver=out(PRE+"foamVersion 2>/dev/null || echo $WM_PROJECT_VERSION").strip()
    for tool in ("blockMesh","splitMeshRegions","topoSet","decomposePar","chtMultiRegionSimpleFoam","reconstructPar","postProcess","mpirun"):
        if not out(PRE+"which "+tool).strip(): sys.exit("missing tool: %s"%tool)
    if not shutil.which("git"): sys.exit("git is required")
    log("environment: OpenFOAM %s; mpirun %s"%(ver or "(version string unavailable)",out(PRE+"mpirun --version 2>&1 | head -1").strip()))
    if "2406" not in ver: log("WARNING: the campaign was audited on OpenFOAM v2406; this machine reports '%s'"%ver)
# ---------- 1 resources ----------
def resources():
    lscpu=out("lscpu"); m=re.search(r"Core\(s\) per socket:\s+(\d+)",lscpu); s=re.search(r"Socket\(s\):\s+(\d+)",lscpu)
    phys=int(m.group(1))*int(s.group(1)) if m and s else os.cpu_count(); logical=os.cpu_count()
    mem=dict(re.findall(r"^(\w+):\s+(\d+)",open("/proc/meminfo").read(),re.M)); free_gb=int(mem.get("MemAvailable",0))/1e6
    load=float(open("/proc/loadavg").read().split()[0])
    return phys,logical,free_gb,load
def choose_cores(a,phys,logical,free_gb,load):
    if a.cores: return a.cores
    default=max(a.ranks,(phys-int(round(load)))//a.ranks*a.ranks)
    print("\nThis machine: %d physical cores (%d logical), %.1f GB RAM available, 1-min load %.1f."%(phys,logical,free_gb,load))
    print("Each case runs on %d MPI ranks (about 0.1 GB RAM per rank); the measured throughput optimum on the local"%a.ranks)
    print("16-core workstation was 1.5 ranks per physical core, so up to about %d cores' worth of ranks is reasonable here."%int(phys*1.5))
    while True:
        r=input("How many cores may this run use? [%d]: "%default).strip()
        if not r: return default
        if r.isdigit() and int(r)>=a.ranks: return int(r)
        print("enter an integer >= %d"%a.ranks)
# ---------- 2 build and verify ----------
def build(ids,workers):
    lst=os.path.join(ROOT,"build_list.txt"); open(lst,"w").write("\n".join(ids)+"\n")
    rc=sh(PRE+"python3 build_cases.py %s %d"%(lst,workers),cwd=ROOT,logfile=os.path.join(ROOT,"build_cases.log"))
    res=open(os.path.join(ROOT,"build_cases.log")).read(); fails=[l for l in res.splitlines() if "FAIL" in l]
    if rc!=0 or fails: sys.exit("build failed:\n"+"\n".join(fails or [res[-2000:]]))
    rc=sh("python3 make_manifest.py check manifest_local_build.json %s"%lst,cwd=ROOT,logfile=os.path.join(ROOT,"verify_build.log"))
    log(open(os.path.join(ROOT,"verify_build.log")).read().strip().splitlines()[-1])
    if rc!=0: sys.exit("the freshly built cases differ from the audited local build (verify_build.log); not running")
# ---------- 3 run ----------
PUSH_LOCK=threading.Lock()
def pack(cid):
    d=os.path.join(ROOT,"cases",cid); os.makedirs(os.path.join(ROOT,"results"),exist_ok=True); tgz=os.path.join(ROOT,"results",cid+".tar.gz")
    keep=["postProcessing","case_meta.json","DONE","CONVERGED_STOP","ENVELOPE_STOP","CONTINUE","posthoc_zoneT.json","system","constant/regionProperties","constant/g",
          "constant/fluid/thermophysicalProperties","constant/solid/thermophysicalProperties"]+glob.glob(os.path.join(d,"log.*"))+glob.glob(os.path.join(d,"*_pass*"))
    with tarfile.open(tgz,"w:gz") as t:
        for k in keep:
            p=k if os.path.isabs(k) else os.path.join(d,k)
            if os.path.exists(p): t.add(p,arcname=os.path.join(cid,os.path.relpath(p,d)))
    return tgz
def push(msg,nopush):
    """Commit results/ and the run log and push to origin main; failures are logged and retried with the next case."""
    if nopush: return
    rel=os.path.relpath(ROOT,REPO)
    with PUSH_LOCK:
        steps=["git add -A %s/results %s/remote_run.log"%(rel,rel),"git diff --cached --quiet || git commit -q -m '%s'"%msg.replace("'",""),"git pull -q --rebase origin main","git push -q origin HEAD:main"]
        for st in steps:
            rc=sh(st,cwd=REPO,logfile=os.path.join(ROOT,"git_push.log"))
            if rc!=0: log("PUSH FAILED at '%s' (rc %d, see git_push.log); results stay in %s/results and are pushed with the next case"%(st.split()[1],rc,rel)); return False
    return True
def running_ledger(a):
    """Post-process every finished remote case into results/ledger_remote.csv and a short summary (pushed with the case)."""
    done=[os.path.join(ROOT,"cases",c) for c in sorted(os.listdir(os.path.join(ROOT,"cases"))) if os.path.exists(os.path.join(ROOT,"cases",c,"DONE"))]
    if not done: return
    env=dict(os.environ,POST_OUT=os.path.join(ROOT,"results","ledger_remote.csv"))
    rc=sh(PRE+"python3 post_campaign.py "+" ".join(done),cwd=ROOT,logfile=os.path.join(ROOT,"results","post_campaign_remote.log"),env=env)
    try:
        import csv; rows=list(csv.DictReader(open(os.path.join(ROOT,"results","ledger_remote.csv"))))
        acc=sum(r.get("accepted")=="True" for r in rows); conv=sum(r.get("converged")=="True" for r in rows); env_=sum(r.get("passed_validity_envelope")=="y" for r in rows)
        lines=["# Remote share: running summary (%s)"%time.strftime("%F %T"),"","cases finished %d of %d | inside envelope %d | converged %d | accepted %d"%(len(rows),len(ids_all),env_,conv,acc),"",
               "| case | fluid | OR | Re_ch | P [W] | it. | stop | wall max [C] | Phi_in | Phi_out | Nu | R_th [K/W] | dp [Pa] | energy [%] | accepted |","|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            c=os.path.join(ROOT,"cases",r["case_id"]); stop="conv" if os.path.exists(c+"/CONVERGED_STOP") else ("envelope" if os.path.exists(c+"/ENVELOPE_STOP") else "cap")
            f=lambda k,d=3: ("%%.%dg"%d)%float(r[k]) if r.get(k) not in (None,"","nan","MISSING") else "n/a"
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"%(r["case_id"],r["fluid"],r["OR"],r["Re_ch"],r["P_sink_W"],r["iterations"],stop,"%.1f"%(float(r["T_wall_max_K"])-273.15),f("Phi_in"),f("Phi_out"),f("Nu"),f("R_th_K_W"),f("dp_field",4),f("energy_balance_pct",2),r["accepted"]))
        open(os.path.join(ROOT,"results","summary_remote.md"),"w").write("\n".join(lines)+"\n")
    except Exception as e: log("running summary failed: %s"%e)
def done_elsewhere(cid,a):
    """True when another machine has already pushed results/<cid>.tar.gz (the list can be shared between machines running
    it in opposite orders); a quick fetch keeps the check current. Never true in --test mode or with --no-push."""
    if a.no_push: return False
    with PUSH_LOCK: sh("git pull -q --rebase origin main >/dev/null 2>&1 || git fetch -q origin main >/dev/null 2>&1",cwd=REPO)
    return os.path.exists(os.path.join(ROOT,"results",cid+".tar.gz")) and not os.path.exists(os.path.join(ROOT,"cases",cid,"DONE"))
def run_case(cid,a,endtime=None):
    d=os.path.join(ROOT,"cases",cid)
    if os.path.exists(os.path.join(d,"DONE")): log("%s skip (done)"%cid); return
    if done_elsewhere(cid,a): log("%s skip (results already in the repository from another machine)"%cid); return
    if endtime:
        cd=os.path.join(d,"system/controlDict"); s=open(cd).read(); s=re.sub(r"endTime\s+\d+;","endTime %d;"%endtime,s,count=1); s=re.sub(r"writeInterval\s+\d+;","writeInterval %d;"%endtime,s,count=1); open(cd,"w").write(s)   # test mode: write the fields at the (short) end time
    t0=time.time(); log("%s start"%cid)
    if sh(PRE+"decomposePar -allRegions -force -decomposeParDict system/decomposeParDict",cwd=d,logfile=os.path.join(d,"log.decomposePar"))!=0: log("%s FAIL decomposePar"%cid); return
    wd=subprocess.Popen(["python3",os.path.join(ROOT,"converge_watchdog.py"),d,"1200","20","4000"],stdout=open(os.path.join(d,"log.watchdog"),"w"),stderr=subprocess.STDOUT)
    rc=sh(PRE+"mpirun -np %d chtMultiRegionSimpleFoam -parallel"%a.ranks,cwd=d,logfile=os.path.join(d,"log.chtMultiRegionSimpleFoam"))
    wd.kill()
    sh(PRE+"reconstructPar -allRegions -latestTime",cwd=d,logfile=os.path.join(d,"log.reconstructPar"))
    for p in glob.glob(os.path.join(d,"processor*")): shutil.rmtree(p,ignore_errors=True)
    its=out("grep -c '^Time = ' log.chtMultiRegionSimpleFoam",cwd=d).strip()
    open(os.path.join(d,"DONE"),"w").write("rc=%s wall_s=%d iterations=%s end=%s host=%s\n"%(rc,time.time()-t0,its,time.strftime("%F_%T"),os.uname().nodename))
    sh(PRE+"python3 posthoc_zone_T.py %s"%d,cwd=ROOT,logfile=os.path.join(d,"log.posthoc"))
    stop="converged" if os.path.exists(os.path.join(d,"CONVERGED_STOP")) else ("envelope" if os.path.exists(os.path.join(d,"ENVELOPE_STOP")) else "cap")
    log("%s done rc=%s %s iterations, %s stop, %.0f s"%(cid,rc,its,stop,time.time()-t0))
    pack(cid); running_ledger(a); push("results: %s (%s, %s iterations)"%(cid,stop,its),a.no_push)
def refresh_extraction(a):
    """Re-run the zone extraction for finished cases whose posthoc_zoneT.json predates the current extraction version, repack and push."""
    import json
    stale=[]
    for c in sorted(os.listdir(os.path.join(ROOT,"cases"))):
        d=os.path.join(ROOT,"cases",c); pz=os.path.join(d,"posthoc_zoneT.json")
        if not os.path.exists(os.path.join(d,"DONE")): continue
        try: v=json.load(open(pz)).get("version",1) if os.path.exists(pz) else 0
        except Exception: v=0
        if v<2: stale.append(d)
    if not stale: return
    log("re-extracting %d finished cases with the version-2 stations and bins"%len(stale))
    for d in stale:
        sh(PRE+"python3 posthoc_zone_T.py %s"%d,cwd=ROOT,logfile=os.path.join(d,"log.posthoc")); pack(os.path.basename(d))
    running_ledger(a); push("results: extraction refreshed for %d cases"%len(stale),a.no_push)
def run_all(ids,a,conc,endtime=None):
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=conc) as ex: list(ex.map(lambda c: run_case(c,a,endtime),ids))
# ---------- 4 continuation ----------
def continuation(a,conc):
    lst=os.path.join(ROOT,"run_list_continue.txt")
    rc=sh("python3 select_continuations.py 12000 %s"%lst,cwd=ROOT,logfile=os.path.join(ROOT,"select_continuations.log"))
    sel=[os.path.basename(l.strip()) for l in open(lst) if l.strip()]; log("continuation pass: %d cases selected"%len(sel))
    def cont(cid):
        d=os.path.join(ROOT,"cases",cid); t0=time.time()
        n=1
        while os.path.exists(os.path.join(d,"DONE_pass%d"%n)): n+=1   # keep every earlier pass: DONE_pass1, DONE_pass2, ...
        for f in ("DONE","log.chtMultiRegionSimpleFoam","CONVERGED_STOP","ENVELOPE_STOP","log.watchdog"):
            if os.path.exists(os.path.join(d,f)): shutil.move(os.path.join(d,f),os.path.join(d,"%s_pass%d"%(f,n) if not f.startswith("log.") else "%s.pass%d"%(f,n)))
        cd=os.path.join(d,"system/controlDict"); s=open(cd).read(); open(cd,"w").write(re.sub(r"startFrom\s+\w+;","startFrom latestTime;",s,count=1))
        if sh(PRE+"decomposePar -allRegions -force -latestTime -decomposeParDict system/decomposeParDict",cwd=d,logfile=os.path.join(d,"log.decomposePar.pass%d"%(n+1)))!=0: log("%s FAIL decomposePar (pass %d)"%(cid,n+1)); return
        wd=subprocess.Popen(["python3",os.path.join(ROOT,"converge_watchdog.py"),d,"1200","20","4000"],stdout=open(os.path.join(d,"log.watchdog"),"w"),stderr=subprocess.STDOUT)
        rc=sh(PRE+"mpirun -np %d chtMultiRegionSimpleFoam -parallel"%a.ranks,cwd=d,logfile=os.path.join(d,"log.chtMultiRegionSimpleFoam")); wd.kill()
        sh(PRE+"reconstructPar -allRegions -latestTime",cwd=d,logfile=os.path.join(d,"log.reconstructPar.pass%d"%(n+1)))
        for p in glob.glob(os.path.join(d,"processor*")): shutil.rmtree(p,ignore_errors=True)
        its=out("grep -c '^Time = ' log.chtMultiRegionSimpleFoam",cwd=d).strip()
        open(os.path.join(d,"DONE"),"w").write("pass%d rc=%s wall_s=%d iterations_this_pass=%s end=%s host=%s\n"%(n+1,rc,time.time()-t0,its,time.strftime("%F_%T"),os.uname().nodename))
        if os.path.exists(os.path.join(d,"CONTINUE")): os.remove(os.path.join(d,"CONTINUE"))
        sh(PRE+"python3 posthoc_zone_T.py %s"%d,cwd=ROOT,logfile=os.path.join(d,"log.posthoc"))
        stop="converged" if os.path.exists(os.path.join(d,"CONVERGED_STOP")) else "cap"
        log("%s continued (pass %d): %s more iterations, %s stop, %.0f s"%(cid,n+1,its,stop,time.time()-t0)); pack(cid); running_ledger(a); push("results: %s continued pass %d (%s iterations, %s)"%(cid,n+1,its,stop),a.no_push)
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=conc) as ex: list(ex.map(cont,sel))
# ---------- main ----------
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--list",default=os.path.join(ROOT,"run_list_remote.txt")); ap.add_argument("--cores",type=int); ap.add_argument("--test-push",action="store_true",help="in --test mode also exercise the commit/push to origin"); ap.add_argument("--reverse",action="store_true",help="run the list in reverse order (a second machine sharing the same list runs it forward; each skips cases the other has pushed)")
    ap.add_argument("--no-push",action="store_true"); ap.add_argument("--test",action="store_true"); a=ap.parse_args()
    check_env(); phys,logical,free_gb,load=resources(); log("resources: %d physical cores, %d logical, %.1f GB available, load %.1f"%(phys,logical,free_gb,load))
    ids=[l.strip() for l in open(a.list) if l.strip() and not l.startswith("#")]; ids_all=list(ids)
    if a.reverse: ids=ids[::-1]
    if a.test: ids=ids[:1]; a.no_push=not a.test_push; log("TEST MODE: %s for 60 iterations, %s"%(ids[0],"push exercised" if a.test_push else "no push"))
    a.ranks=8   # fixed: system/decomposeParDict of every audited case has numberOfSubdomains 8
    if a.test and not a.cores: a.cores=8
    cores=choose_cores(a,phys,logical,free_gb,load); conc=max(1,cores//a.ranks)
    if free_gb<0.15*cores: sys.exit("not enough RAM: %.1f GB available for %d ranks"%(free_gb,cores))
    log("using %d cores: %d concurrent cases x %d ranks"%(cores,conc,a.ranks))
    build(ids,workers=min(8,max(1,conc)))
    if not a.test: refresh_extraction(a)
    run_all(ids,a,conc,endtime=60 if a.test else None)
    if not a.test: continuation(a,conc); refresh_extraction(a); push("results: continuation pass complete",a.no_push); log("REMOTE_LIST_COMPLETE")
    else:
        d=os.path.join(ROOT,"cases",ids[0]); ok=os.path.exists(os.path.join(d,"posthoc_zoneT.json")) and os.path.exists(os.path.join(ROOT,"results",ids[0]+".tar.gz"))
        log("TEST %s: build, verify, decompose, solve, reconstruct, zone extraction (%s) and packing (%s); inspect cases/%s and results/%s.tar.gz"%("PASSED" if ok else "FAILED","posthoc_zoneT.json present" if os.path.exists(os.path.join(d,"posthoc_zoneT.json")) else "posthoc_zoneT.json MISSING: see cases/%s/log.posthoc"%ids[0],"tar present" if os.path.exists(os.path.join(ROOT,"results",ids[0]+".tar.gz")) else "tar missing",ids[0],ids[0]))
        sys.exit(0 if ok else 1)
