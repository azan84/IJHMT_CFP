#!/usr/bin/env python3
"""One-file launcher for the remote share of the unit-cell calibration campaign.
Copy this file to the machine, then:   python3 run_remote_share.py            (asks how many cores to use)
                                       python3 run_remote_share.py --test     (one case, 60 iterations, no push)
                                       python3 run_remote_share.py --cores 16 (no prompt)
It clones (or repairs and updates) github.com/azan84/IJHMT_CFP in ./IJHMT_CFP (sparse: only unit_cell_campaign/) and
runs unit_cell_campaign/remote_run.py there with the arguments you pass. Before updating it repairs the clone on its
own: an interrupted rebase or merge is aborted, edits to the legacy tracked run log are dropped, result files that were
never committed or never pushed are committed and pushed (replayed on top of the repository if a rebase cannot apply).
It also replaces itself with the repository's copy when that is newer, so later fixes arrive without copying the file
again. Results are pushed back after every case, so the clone needs push access (an SSH key registered on GitHub);
without it, add --no-push and copy IJHMT_CFP/unit_cell_campaign/results/ back by hand."""
import os, sys, subprocess, shutil, filecmp
SSH="git@github.com:azan84/IJHMT_CFP.git"; HTTPS="https://github.com/azan84/IJHMT_CFP.git"
HERE=os.path.dirname(os.path.abspath(__file__)); CLONE=os.path.join(HERE,"IJHMT_CFP"); RES="unit_cell_campaign/results"
def run(cmd,cwd=None,quiet=False):
    if not quiet: print("+",cmd,flush=True)
    return subprocess.call(["bash","-c",cmd],cwd=cwd)
def git_repair_and_update():
    """Bring the clone to a clean state on top of origin/main without losing any result file."""
    run("git rebase --abort >/dev/null 2>&1; git merge --abort >/dev/null 2>&1; git cherry-pick --abort >/dev/null 2>&1; rm -f .git/index.lock; true",cwd=CLONE,quiet=True)
    run("git checkout -q -- unit_cell_campaign/remote_run.log >/dev/null 2>&1; true",cwd=CLONE,quiet=True)   # legacy tracked live log of earlier runner versions
    run("git add -A %s >/dev/null 2>&1; git diff --cached --quiet || git commit -q -m 'results: pending results committed by the launcher'"%RES,cwd=CLONE,quiet=True)
    run("git sparse-checkout set unit_cell_campaign /run_remote_share.py /.gitignore /README.md >/dev/null 2>&1; true",cwd=CLONE,quiet=True)   # older clones lack the root files
    if run("git fetch -q origin main",cwd=CLONE)!=0: print("fetch failed (network?); continuing with the local copy"); return
    if run("git rebase -q origin/main",cwd=CLONE)!=0:
        print("rebase could not apply; replaying the local result files on top of origin/main")
        run("git rebase --abort >/dev/null 2>&1; git reset -q --soft origin/main && git add -A %s && (git diff --cached --quiet || git commit -q -m 'results: replayed on origin by the launcher')"%RES,cwd=CLONE)
    run("git push -q origin HEAD:main || echo 'push failed (the runner retries after every case)'",cwd=CLONE)
if not shutil.which("git"): sys.exit("git is required (apt install git)")
FRESH=not os.path.isdir(os.path.join(CLONE,".git"))
if FRESH:
    rc=run("git clone --filter=blob:none --sparse %s %s"%(SSH,CLONE))
    if rc!=0:
        print("SSH clone failed (no key for GitHub on this machine?); cloning over HTTPS. Results can then be pushed only with a token; use --no-push otherwise.")
        if run("git clone --filter=blob:none --sparse %s %s"%(HTTPS,CLONE))!=0: sys.exit("clone failed")
    run("git sparse-checkout set unit_cell_campaign /run_remote_share.py /.gitignore /README.md",cwd=CLONE)   # the campaign directory plus the root files (this launcher, the ignore rules)
run("git config user.name >/dev/null || git config user.name 'remote runner'; git config user.email >/dev/null || git config user.email 'remote-runner@localhost'",cwd=CLONE,quiet=True)
if os.path.isdir(os.path.join(CLONE,".git")) and not FRESH: git_repair_and_update()
# self-update: the repository's launcher replaces this file when it differs (once per start; the re-executed copy skips this step)
me=os.path.abspath(__file__); repo_copy=os.path.join(CLONE,"run_remote_share.py")
if os.path.exists(repo_copy) and not filecmp.cmp(me,repo_copy,shallow=False) and os.environ.get("RUN_REMOTE_SHARE_UPDATED")!="1":
    shutil.copy(repo_copy,me); print("launcher updated from the repository; restarting"); os.environ["RUN_REMOTE_SHARE_UPDATED"]="1"; os.execvp(sys.executable,[sys.executable,me]+sys.argv[1:])
script=os.path.join(CLONE,"unit_cell_campaign","remote_run.py")
if not os.path.exists(script): sys.exit("unit_cell_campaign/remote_run.py not found after the clone")
os.execvp(sys.executable,[sys.executable,script]+sys.argv[1:])
