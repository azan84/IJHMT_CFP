#!/usr/bin/env python3
"""Local side: pull the repository and unpack results/<case>.tar.gz into the local campaign's cases/<case>/ for every
case that has no local DONE (or whose local copy is older). Usage: import_remote_results.py <repo_clone_dir> <local_campaign_dir>"""
import sys, os, tarfile, glob, subprocess, shutil, re
repo,local=sys.argv[1],sys.argv[2]
subprocess.call(["git","-C",repo,"pull","-q","--rebase","origin","main"])
n=0
for tgz in sorted(glob.glob(os.path.join(repo,"unit_cell_campaign/results/*.tar.gz"))):
    cid=os.path.basename(tgz)[:-7]; dest=os.path.join(local,"cases",cid); done=os.path.join(dest,"DONE")
    if os.path.exists(done) and "host=" not in open(done).read(): print(cid,"skip: finished locally"); continue
    if os.path.exists(done) and os.path.getmtime(done)>=os.path.getmtime(tgz): continue
    with tarfile.open(tgz) as t:
        members=[m for m in t.getmembers() if m.name.startswith(cid+"/") and ".." not in m.name]
        for m in members:
            target=os.path.join(dest,os.path.relpath(m.name,cid))
            if m.isdir(): os.makedirs(target,exist_ok=True); continue
            if os.path.exists(target) and "system/" in m.name and "controlDict" not in m.name: continue   # keep the local (audited, identical) dictionaries
            os.makedirs(os.path.dirname(target),exist_ok=True); f=t.extractfile(m); open(target,"wb").write(f.read())
    n+=1; print(cid,"imported",open(done).read().strip()[:80])
print(n,"cases imported")
