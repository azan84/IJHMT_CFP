#!/usr/bin/env python3
"""Write (or check) the manifest of SHA-256 checksums of every dictionary and field file of the built cases, so that a
build on another machine can be verified bit for bit against the audited local build. Binary mesh files are excluded
(blockMesh output is deterministic but its binary layout is not part of the audit); the mesh is checked through
checkMesh's cell count instead. Usage: make_manifest.py write <manifest.json> <list_file>   |   make_manifest.py check <manifest.json> <list_file>"""
import sys, os, json, hashlib, re
ROOT=os.path.dirname(os.path.abspath(__file__))
FILES=["case_meta.json","system/controlDict","system/blockMeshDict","system/decomposeParDict","system/fvSchemes","system/fvSolution",
       "system/fluid/decomposeParDict","system/fluid/fvSchemes","system/fluid/fvSolution","system/fluid/topoSetDict",
       "system/solid/decomposeParDict","system/solid/fvSchemes","system/solid/fvSolution",
       "constant/regionProperties","constant/g","constant/fluid/thermophysicalProperties","constant/fluid/turbulenceProperties",
       "constant/fluid/radiationProperties","constant/solid/thermophysicalProperties","constant/solid/radiationProperties",
       "0/fluid/U","0/fluid/T","0/fluid/p","0/fluid/p_rgh","0/solid/T","0/solid/p"]
VOLATILE=re.compile(r"^(stopAt|endTime|startFrom|writeInterval)\s")   # controlDict lines that the watchdog or a continuation rewrites
def digest(path,volatile=False):
    data=open(path,"rb").read()
    if volatile: data=b"\n".join(l for l in data.split(b"\n") if not VOLATILE.match(l.decode("latin1")))
    return hashlib.sha256(data).hexdigest()
def case_digests(cid):
    d=os.path.join(ROOT,"cases",cid); out={}
    for f in FILES:
        p=os.path.join(d,f)
        if os.path.exists(p): out[f]=digest(p,volatile=f.endswith("controlDict"))
    lc=os.path.join(d,"log.checkMesh")
    if os.path.exists(lc):
        m=re.search(r"cells:\s+(\d+)",open(lc).read()); out["checkMesh.cells"]=int(m.group(1)) if m else None
    return out
mode,man,lst=sys.argv[1],sys.argv[2],sys.argv[3]; ids=[l.strip() for l in open(lst) if l.strip()]
if mode=="write":
    man_d={cid:case_digests(cid) for cid in ids}
    man_d["_text"]={cid:{f:open(os.path.join(ROOT,"cases",cid,f)).read() for f in ("case_meta.json","constant/fluid/thermophysicalProperties") if os.path.exists(os.path.join(ROOT,"cases",cid,f))} for cid in ids}   # kept for the numeric-equivalence check
    json.dump(man_d,open(man,"w"),indent=1); print("manifest written for",len(ids),"cases")
else:
    M=json.load(open(man)); bad=0; numeq=0
    NUMTOL=1e-9   # numeric tolerance (relative) for files whose text carries floating-point values that another machine may round differently in the last bits
    def numeric_equivalent(cid,f):
        """Text equal apart from floating-point numbers that agree to NUMTOL: the two files describe the same case."""
        a=open(os.path.join(ROOT,"cases",cid,f)).read(); b=M.get("_text",{}).get(cid,{}).get(f)
        if b is None: return False
        ta=re.split(r"(-?\d+\.?\d*(?:[eE][-+]?\d+)?)",a); tb=re.split(r"(-?\d+\.?\d*(?:[eE][-+]?\d+)?)",b)
        if len(ta)!=len(tb): return False
        for x,y in zip(ta,tb):
            if x==y: continue
            try: fx,fy=float(x),float(y)
            except ValueError: return False
            if abs(fx-fy)>NUMTOL*max(abs(fx),abs(fy),1e-300): return False
        return True
    for cid in ids:
        got=case_digests(cid); exp=M.get(cid)
        if exp is None: print(cid,"NOT IN MANIFEST"); bad+=1; continue
        diff=[k for k in exp if exp[k]!=got.get(k)]
        hard=[k for k in diff if not (k in ("case_meta.json","constant/fluid/thermophysicalProperties") and numeric_equivalent(cid,k))]
        if hard: print(cid,"MISMATCH",hard); bad+=1
        elif diff: numeq+=1; print(cid,"numeric-equivalent (floating-point text differs within %g relative):"%NUMTOL,diff)
    print("checked",len(ids),"cases;",bad,"with differences;",numeq,"numeric-equivalent"); sys.exit(1 if bad else 0)
