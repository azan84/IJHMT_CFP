#!/usr/bin/env python3
"""One-file launcher for the remote share of the unit-cell calibration campaign.
Copy this file to the machine, then:   python3 run_remote_share.py            (asks how many cores to use)
                                       python3 run_remote_share.py --test     (one case, 60 iterations, no push)
                                       python3 run_remote_share.py --cores 40 (no prompt)
It clones (or updates) github.com/azan84/IJHMT_CFP into ./IJHMT_CFP (sparse: only unit_cell_campaign/, no history
blobs of the old campaign) and runs unit_cell_campaign/remote_run.py there with the arguments you pass. Results are
pushed back to the repository after every case, so the clone needs push access (an SSH key registered on GitHub);
without it, add --no-push and copy IJHMT_CFP/unit_cell_campaign/results/ back by hand."""
import os, sys, subprocess, shutil
SSH="git@github.com:azan84/IJHMT_CFP.git"; HTTPS="https://github.com/azan84/IJHMT_CFP.git"
HERE=os.path.dirname(os.path.abspath(__file__)); CLONE=os.path.join(HERE,"IJHMT_CFP")
def run(cmd,cwd=None): print("+",cmd,flush=True); return subprocess.call(["bash","-c",cmd],cwd=cwd)
if not shutil.which("git"): sys.exit("git is required (apt install git)")
if not os.path.isdir(os.path.join(CLONE,".git")):
    rc=run("git clone --filter=blob:none --sparse %s %s"%(SSH,CLONE))
    if rc!=0:
        print("SSH clone failed (no key for GitHub on this machine?); cloning over HTTPS. Results can then be pushed only with a token; use --no-push otherwise.")
        if run("git clone --filter=blob:none --sparse %s %s"%(HTTPS,CLONE))!=0: sys.exit("clone failed")
    run("git sparse-checkout set unit_cell_campaign",cwd=CLONE)
else:
    run("git rebase --abort >/dev/null 2>&1; git merge --abort >/dev/null 2>&1; git checkout -q -- unit_cell_campaign/remote_run.log >/dev/null 2>&1; true",cwd=CLONE)   # repair a half-done rebase or a dirty legacy log
    if run("git pull -q --rebase origin main",cwd=CLONE)!=0:
        print("pull --rebase failed; replaying local result commits on top of origin")
        run("git rebase --abort >/dev/null 2>&1; git fetch -q origin main && git reset -q --soft origin/main && git add -A unit_cell_campaign/results && (git diff --cached --quiet || git commit -q -m 'results: replayed on origin') && git push -q origin HEAD:main",cwd=CLONE)
run("git config user.name >/dev/null || git config user.name 'remote runner'; git config user.email >/dev/null || git config user.email 'remote-runner@localhost'",cwd=CLONE)
script=os.path.join(CLONE,"unit_cell_campaign","remote_run.py")
if not os.path.exists(script): sys.exit("unit_cell_campaign/remote_run.py not found after the clone")
os.execvp(sys.executable,[sys.executable,script]+sys.argv[1:])
