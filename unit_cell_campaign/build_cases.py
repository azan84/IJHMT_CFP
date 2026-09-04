#!/usr/bin/env python3
"""Build the cases named in a list file (one case id per line) from campaign_design.json under cases/<case_id>:
blockMesh, checkMesh, splitMeshRegions, topoSet (fluid face zones), fields and dictionaries, as unit_cell.build does.
Forced convection (gravity = None) as decided for the campaign. Usage: build_cases.py <list_file> [workers]"""
import json, os, sys, concurrent.futures as cf
ROOT=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,ROOT); import unit_cell as u
design={c["case_id"]:c for c in json.load(open(os.path.join(ROOT,"campaign_design.json")))["cases"]}
ids=[l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
def one(cid):
    c=design[cid]; d=os.path.join(ROOT,"cases",cid)
    if os.path.exists(os.path.join(d,"case_meta.json")) and os.path.exists(os.path.join(d,"constant/fluid/polyMesh/faces")): return cid,"exists"
    try:
        kw=dict(fluid=c["fluid"],Re_ch=c["Re_ch"],P_W=c["P_sink_W"],grid=c["grid"])
        if c.get("H_fin_fixed_m"): kw.update(Hfin=c["H_fin_fixed_m"],Hc=c["H_chassis_m"])
        else: kw.update(OR=c["OR"])
        m=u.build(d,**kw,log=lambda *a: None,gravity=False); return cid,"ok %s cells"%m.get("cells")
    except Exception as e: return cid,"FAIL %s"%e
if __name__=="__main__":
    missing=[i for i in ids if i not in design]
    if missing: sys.exit("unknown case ids: %s"%missing)
    with cf.ThreadPoolExecutor(max_workers=int(sys.argv[2]) if len(sys.argv)>2 else 4) as ex:
        for cid,st in ex.map(one,ids): print(cid,st,flush=True)
