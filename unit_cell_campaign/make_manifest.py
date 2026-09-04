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
VOLATILE=re.compile(r"^(stopAt|endTime|startFrom)\s")   # controlDict lines that the watchdog or a continuation rewrites
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
    json.dump({cid:case_digests(cid) for cid in ids},open(man,"w"),indent=1); print("manifest written for",len(ids),"cases")
else:
    M=json.load(open(man)); bad=0
    for cid in ids:
        got=case_digests(cid); exp=M.get(cid)
        if exp is None: print(cid,"NOT IN MANIFEST"); bad+=1; continue
        diff=[k for k in exp if exp[k]!=got.get(k)]
        if diff: print(cid,"MISMATCH",diff); bad+=1
    print("checked",len(ids),"cases;",bad,"with differences"); sys.exit(1 if bad else 0)
