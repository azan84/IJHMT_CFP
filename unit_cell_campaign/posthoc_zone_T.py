#!/usr/bin/env python3
"""Post-hoc extraction (version 2) from the final written fields of a finished case, run through the solver's
-postProcess mode so that the wall heat flux is recomputed from the fields:
  * six streamwise stations x = i L/5 (i = 0..5; station 0 = sink leading edge, 5 = trailing edge): mass-flux-weighted
    mean temperature and mass flux on the fin-channel face zone (chanX_i) and on the clearance zone (clearX_i);
  * five streamwise bins of the fluid-solid interface (wallB_i, x in [i L/5, (i+1) L/5]): area, area-averaged
    temperature and integrated wall heat flux.
The station and bin edges lie on mesh faces for the three grids (nx_sink = 60, 100, 160 are multiples of 5).
Empty zones (no clearance at OR 0, no channel at OR 1) are skipped because surfaceFieldValue aborts on them.
Result: <case>/posthoc_zoneT.json (version 2; the version-1 keys T_chanIn_K, T_chanOut_K, phi_*In/Out are kept
as aliases of stations 0 and 5). Idempotent: skipped when a version-2 json is newer than DONE.
Usage: posthoc_zone_T.py <case> [<case> ...]"""
import sys, os, re, json, glob, subprocess, shutil
VERSION=2; NB=5; L=0.118
def of_prefix():
    """Shell prefix that provides the OpenFOAM environment: none when the tools are already in PATH, otherwise
    'source <bashrc>; ' from OPENFOAM_BASHRC (exported by remote_run.py after detection) or the usual install paths."""
    import shutil as _sh
    if _sh.which("chtMultiRegionSimpleFoam"): return ""
    cands=[os.environ.get("OPENFOAM_BASHRC","")]+["/usr/lib/openfoam/openfoam2406/etc/bashrc","/opt/openfoam2406/etc/bashrc","/opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc",os.path.expanduser("~/OpenFOAM/OpenFOAM-v2406/etc/bashrc")]
    for b in cands:
        if b and os.path.exists(b): return "source %s >/dev/null 2>&1; "%b
    raise RuntimeError("OpenFOAM v2406 not found: put its tools in PATH or set OPENFOAM_BASHRC to its etc/bashrc")
def zone_sizes(logf):
    d={}
    if os.path.exists(logf):
        for m in re.finditer(r"faceZoneSet (\w+) now size (\d+)",open(logf).read()): d[m.group(1)]=int(m.group(2))
    return d
def run(cmd,cwd,log):
    cmd=of_prefix()+cmd
    with open(os.path.join(cwd,log),"w") as f: return subprocess.call(["bash","-c",cmd],cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
def tsort(fs): return sorted(fs,key=lambda f: float(os.path.basename(os.path.dirname(f))))
def last_value(case,fo,col=1):
    fs=tsort(glob.glob(os.path.join(case,"postProcessing/fluid",fo,"*","surfaceFieldValue.dat")))
    if not fs: return None
    rows=[l.split() for l in open(fs[-1]) if l.strip() and not l.startswith("#")]
    if not rows or len(rows[-1])<=col: return None
    return float(rows[-1][col])
def process(case):
    out=os.path.join(case,"posthoc_zoneT.json"); done=os.path.join(case,"DONE")
    if not os.path.exists(done): return "not finished"
    if os.path.exists(out) and os.path.getmtime(out)>os.path.getmtime(done):
        try:
            if json.load(open(out)).get("version",1)>=VERSION: return "up to date"
        except Exception: pass
    sy=os.path.join(case,"system/fluid"); td=open(os.path.join(sy,"topoSetDict")).read()
    m=re.findall(r"name (\w+)Set; type faceSet; action new; source boxToFace; box \(-1e-06 -1 ([0-9.e-]+)\) \(1e-06 1 ([0-9.e-]+)\); \}",td)   # leading-edge boxes at x = 0
    zb={name:(float(z0),float(z1)) for name,z0,z1 in m}
    if "chanIn" not in zb or "clearIn" not in zb: return "leading-edge zones not found in system/fluid/topoSetDict"
    acts=[]
    for i in range(1,NB+1):
        x=L*i/NB
        for name,(z0,z1) in (("chanX%d"%i,zb["chanIn"]),("clearX%d"%i,zb["clearIn"])):
            acts.append("    { name %sSet; type faceSet; action new; source boxToFace; box (%.7f -1 %r) (%.7f 1 %r); }\n    { name %s; type faceZoneSet; action new; source setToFaceZone; faceSet %sSet; }"%(name,x-1e-6,z0,x+1e-6,z1,name,name))
    for i in range(NB):
        x0,x1=L*i/NB,L*(i+1)/NB
        acts.append("    { name wallB%dSet; type faceSet; action new; source patchToFace; patch fluid_to_solid; }\n    { name wallB%dSet; type faceSet; action subset; source boxToFace; box (%.7f -1 -1) (%.7f 1 1); }\n    { name wallB%d; type faceZoneSet; action new; source setToFaceZone; faceSet wallB%dSet; }"%(i,i,x0-1e-7,x1-1e-7,i,i))
    hdr="FoamFile { version 2.0; format ascii; class dictionary; object topoSetDict; }\n"
    if True:   # always rebuild the post-hoc zones (a few seconds; 'action new' replaces any earlier definition)
        shutil.copy(os.path.join(sy,"topoSetDict"),os.path.join(sy,"topoSetDict.campaign"))
        open(os.path.join(sy,"topoSetDict"),"w").write(hdr+"actions\n(\n"+"\n".join(acts)+"\n);\n")
        rc=run("topoSet -region fluid",case,"log.topoSet.posthoc")
        shutil.copy(os.path.join(sy,"topoSetDict.campaign"),os.path.join(sy,"topoSetDict"))
        if rc!=0: return "topoSet failed"
    sizes=zone_sizes(os.path.join(case,"log.topoSet")); sizes.update(zone_sizes(os.path.join(case,"log.topoSet.posthoc")))
    sizes["chanX0"]=sizes.get("chanIn",0); sizes["clearX0"]=sizes.get("clearIn",0)
    zname=lambda z: {"chanX0":"chanIn","clearX0":"clearIn"}.get(z,z)
    zones=[z for i in range(NB+1) for z in ("chanX%d"%i,"clearX%d"%i) if sizes.get(z,0)>0]
    bins=["wallB%d"%i for i in range(NB) if sizes.get("wallB%d"%i,0)>0]
    fo="FoamFile { version 2.0; format ascii; class dictionary; object posthocFuncs; }\nfunctions\n{\n"
    fo+="    whf { type wallHeatFlux; libs (fieldFunctionObjects); region fluid; patches (fluid_to_solid); writeFields true; log false; }\n"
    for z in zones:
        fo+="    zoneT_%s { type surfaceFieldValue; libs (fieldFunctionObjects); region fluid; regionType faceZone; name %s; operation weightedAverage; weightField phi; fields (T); writeFields false; log false; }\n"%(z,zname(z))
        fo+="    zonePhi_%s { type surfaceFieldValue; libs (fieldFunctionObjects); region fluid; regionType faceZone; name %s; operation sum; fields (phi); writeFields false; log false; }\n"%(z,zname(z))
    for b in bins:
        fo+="    binT_%s { type surfaceFieldValue; libs (fieldFunctionObjects); region fluid; regionType faceZone; name %s; operation areaAverage; fields (T); writeArea true; writeFields false; log false; }\n"%(b,b)
        fo+="    binQ_%s { type surfaceFieldValue; libs (fieldFunctionObjects); region fluid; regionType faceZone; name %s; operation areaIntegrate; fields (wallHeatFlux); writeArea true; writeFields false; log false; }\n"%(b,b)
    fo+="}\n"; open(os.path.join(sy,"posthocFuncs"),"w").write(fo)
    for d in glob.glob(os.path.join(case,"postProcessing/fluid/zone*"))+glob.glob(os.path.join(case,"postProcessing/fluid/bin*"))+glob.glob(os.path.join(case,"postProcessing/fluid/whf")): shutil.rmtree(d)
    rc=run("chtMultiRegionSimpleFoam -postProcess -latestTime -dict system/fluid/posthocFuncs",case,"log.postProcess.posthoc")
    res={"version":VERSION,"stations_x_m":[L*i/NB for i in range(NB+1)],"zones":zones,"bins":bins,"zone_sizes":{z:sizes.get(z,0) for z in ["chanX%d"%i for i in range(NB+1)]+["clearX%d"%i for i in range(NB+1)]+["wallB%d"%i for i in range(NB)]}}
    for z in zones:
        t=last_value(case,"zoneT_"+z,1); p=last_value(case,"zonePhi_"+z,1)
        if t is None or p is None: return "postProcess wrote no value for %s (see log.postProcess.posthoc)"%z
        res["T_%s_K"%z]=t; res["phi_%s_kg_s"%z]=p
    for b in bins:
        A=last_value(case,"binT_"+b,1); t=last_value(case,"binT_"+b,2); q=last_value(case,"binQ_"+b,2)
        if A is None or t is None or q is None: return "postProcess wrote no value for %s (see log.postProcess.posthoc)"%b
        res["A_%s_m2"%b]=A; res["Tw_%s_K"%b]=t; res["Q_%s_W"%b]=q
    fs=tsort(glob.glob(os.path.join(case,"postProcessing/fluid/zoneT_%s/*/surfaceFieldValue.dat"%zones[0]))); res["time"]=float([l.split() for l in open(fs[-1]) if l.strip() and not l.startswith("#")][-1][0])
    for old,new in (("chanIn","chanX0"),("clearIn","clearX0"),("chanOut","chanX%d"%NB),("clearOut","clearX%d"%NB)):   # version-1 aliases
        if "T_%s_K"%new in res: res["T_%s_K"%old]=res["T_%s_K"%new]; res["phi_%s_kg_s"%old]=res["phi_%s_kg_s"%new]
    if rc!=0: res["postProcess_rc"]=rc
    json.dump(res,open(out,"w"),indent=1); return "written"
if __name__=="__main__":
    for c in sys.argv[1:]: print(os.path.basename(c.rstrip("/")),process(c.rstrip("/")),flush=True)
