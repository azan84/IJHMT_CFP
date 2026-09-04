#!/usr/bin/env python3
"""Post-hoc extraction, from the final written fields of a finished case, of the mass-flux-weighted mean temperature
and the mass flux on the fin-channel and clearance face zones at the sink leading edge (x = 0: chanIn, clearIn, built
by the campaign topoSetDict) and trailing edge (x = L: chanOut, clearOut, built here with the same z bounds as the case\'s own leading-edge boxes). Empty zones (no clearance at
OR 0, no channel at OR 1) are skipped, because surfaceFieldValue aborts on them. Result: <case>/posthoc_zoneT.json
with T_<zone>_K, phi_<zone>_kg_s and the time read. Idempotent: skipped when the json is newer than DONE.
Usage: posthoc_zone_T.py <case> [<case> ...]"""
import sys, os, re, json, glob, subprocess, shutil
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
    cmd=of_prefix()+cmd   # OpenFOAM environment: PATH, OPENFOAM_BASHRC or the usual install paths
    with open(os.path.join(cwd,log),"w") as f: return subprocess.call(["bash","-c",cmd],cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
def process(case):
    out=os.path.join(case,"posthoc_zoneT.json"); done=os.path.join(case,"DONE")
    if not os.path.exists(done): return "not finished"
    if os.path.exists(out) and os.path.getmtime(out)>os.path.getmtime(done): return "up to date"
    sy=os.path.join(case,"system/fluid"); td=open(os.path.join(sy,"topoSetDict")).read()
    # the case's own leading-edge boxes: chanIn spans z in [zlo, zsplit] (degenerate at OR = 1), clearIn spans [zsplit, ztop]
    m=re.findall(r"name (\w+)Set; type faceSet; action new; source boxToFace; box \(-1e-06 -1 ([0-9.e-]+)\) \(1e-06 1 ([0-9.e-]+)\); \}",td)   # leading-edge boxes at x = 0
    zb={name:(float(z0),float(z1)) for name,z0,z1 in m}
    if "chanIn" not in zb or "clearIn" not in zb: return "leading-edge zones not found in system/fluid/topoSetDict"
    L=0.118; acts=[]
    for name,(z0,z1) in (("chanOut",zb["chanIn"]),("clearOut",zb["clearIn"])):
        acts.append("    { name %sSet; type faceSet; action new; source boxToFace; box (%.6f -1 %s) (%.6f 1 %s); }\n    { name %s; type faceZoneSet; action new; source setToFaceZone; faceSet %sSet; }"%(name,L-1e-6,repr(z0),L+1e-6,repr(z1),name,name))
    hdr="FoamFile { version 2.0; format ascii; class dictionary; object topoSetDict; }\n"
    fz=os.path.join(case,"constant/fluid/polyMesh/faceZones")
    have_out=os.path.exists(fz) and b"clearOut" in open(fz,"rb").read()
    if not have_out:
        shutil.copy(os.path.join(sy,"topoSetDict"),os.path.join(sy,"topoSetDict.campaign"))
        open(os.path.join(sy,"topoSetDict"),"w").write(hdr+"actions\n(\n"+"\n".join(acts)+"\n);\n")
        rc=run("topoSet -region fluid",case,"log.topoSet.posthoc")
        shutil.copy(os.path.join(sy,"topoSetDict.campaign"),os.path.join(sy,"topoSetDict"))
        if rc!=0: return "topoSet failed"
    sizes=zone_sizes(os.path.join(case,"log.topoSet")); sizes.update(zone_sizes(os.path.join(case,"log.topoSet.posthoc")))
    zones=[z for z in ("chanIn","clearIn","chanOut","clearOut") if sizes.get(z,0)>0]
    fo="FoamFile { version 2.0; format ascii; class dictionary; object posthocFuncs; }\nfunctions\n{\n"
    for z in zones:
        fo+="    zoneT_%s { type surfaceFieldValue; libs (fieldFunctionObjects); region fluid; regionType faceZone; name %s; operation weightedAverage; weightField phi; fields (T); writeFields false; log false; }\n"%(z,z)
        fo+="    zonePhi_%s { type surfaceFieldValue; libs (fieldFunctionObjects); region fluid; regionType faceZone; name %s; operation sum; fields (phi); writeFields false; log false; }\n"%(z,z)
    fo+="}\n"; open(os.path.join(sy,"posthocFuncs"),"w").write(fo)
    for d in glob.glob(os.path.join(case,"postProcessing/fluid/zone*")): shutil.rmtree(d)
    rc=run('postProcess -region fluid -latestTime -fields "(T phi)" -dict system/fluid/posthocFuncs',case,"log.postProcess.posthoc")
    res={"zones":zones,"zone_sizes":{z:sizes.get(z,0) for z in ("chanIn","clearIn","chanOut","clearOut")}}
    for z in zones:
        for kind,key in (("zoneT_","T_%s_K"),("zonePhi_","phi_%s_kg_s")):
            fs=sorted(glob.glob(os.path.join(case,"postProcessing/fluid",kind+z,"*","surfaceFieldValue.dat")),key=lambda f: float(os.path.basename(os.path.dirname(f))))
            if not fs: return "postProcess incomplete (%s%s)"%(kind,z)
            rows=[l.split() for l in open(fs[-1]) if l.strip() and not l.startswith("#")]
            if not rows: return "postProcess wrote no value for %s%s (no T/phi fields in the latest time directory? see log.postProcess.posthoc)"%(kind,z)
            res[key%z]=float(rows[-1][1]); res["time"]=float(rows[-1][0])
    if rc!=0 and len(zones)>0: res["postProcess_rc"]=rc
    json.dump(res,open(out,"w"),indent=1); return "written"
if __name__=="__main__":
    for c in sys.argv[1:]: print(os.path.basename(c.rstrip("/")),process(c.rstrip("/")))
