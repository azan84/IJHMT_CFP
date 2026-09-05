# Remote set-up audit, round 3 (5 September 2026): launcher and runner before hand-over

Auditor: Gemini 3.7 Flash through the Antigravity CLI (`agy --model gemini-3.7-flash-high`), on an isolated copy with sandboxes that reproduce the second machine's broken clone (`instructions_round3.md`, `make_sandbox.sh`). Verdict FAIL: two blocking items (a --test run altered a case's controlDict so that the next production start failed the manifest check; OPENFOAM_BASHRC was not honoured) and six non-blocking items, all fixed in commit 64b1d72 (see the round-4 instructions). The auditor's report follows verbatim.

I have launched the remote share launcher in sandbox 1 (`python3 run_remote_share.py --test --test-push`) to test repairing the broken clone and running the 60-iteration OpenFOAM test case. Waiting for the execution to complete.
I have launched `python3 run_remote_share.py --cores 8 --no-push` in sandbox 1 to see how the full run behaves after the `--test` run. Waiting for the command to finish.
I have started `python3 run_remote_share.py --test --test-push` in sandbox 2 with the rebase in progress to observe how the launcher repairs the repository and whether results are preserved. Waiting for completion.
I have launched `python3 run_remote_share.py --test --test-push` in sandbox 2 with a pre-existing `.git/index.lock` to verify whether the launcher removes the lock and proceeds cleanly. Waiting for the execution to finish.
I have launched `remote_run.py --test --test-push` on Machine A in sandbox 3. Waiting for the execution to complete.
I have launched `remote_run.py --test --test-push` on Machine B in sandbox 3. Waiting for completion to inspect the resulting commits and origin state.
# Adversarial Audit Report: Remote Share Launcher and Runner (Round 3)

**Audited Directory**: [`package/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package)  
**Audit Specification**: [`instructions_round3.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/instructions_round3.md)  
**Prior Audits**: [`round1_FAIL.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/round1_FAIL.md), [`round2_PASS.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/round2_PASS.md)  
**Auditor**: Adversarial Auditor (Gemini 3.7 Flash; Read-Only on `package/`, sandboxed execution under `scratch/`)

---

## Part A: Exercising the System in Throwaway Sandboxes

### 1. Sandbox 1: Exercise the Launcher in the Second Machine's Broken State

Sandbox `scratch/sb1` was constructed with `bash make_sandbox.sh scratch/sb1`. This instantiated:
- A bare `origin.git` with an upstream commit on `README.md` (`db22b4c upstream commit`).
- A sparse clone `sb1/remote_pc/IJHMT_CFP` with an unpushed result commit (`results: L015 (unpushed)`) and uncommitted modifications to the legacy tracked log `unit_cell_campaign/remote_run.log`.
- `run_remote_share.py` pointing to `sb1/origin.git`.

#### Initial Execution (`python3 run_remote_share.py --test --test-push`)
The launcher was executed directly from `sb1/remote_pc`:
```text
+ git fetch -q origin main
+ git rebase -q origin/main
+ git push -q origin HEAD:main || echo 'push failed (the runner retries after every case)'
launcher updated from the repository; restarting
+ git fetch -q origin main
+ git rebase -q origin/main
+ git push -q origin HEAD:main || echo 'push failed (the runner retries after every case)'
2026-09-05 12:24:17 environment: OpenFOAM v2406; mpirun mpirun (Open MPI) 4.1.2
2026-09-05 12:24:17 resources: 16 physical cores, 32 logical, 24.8 GB available, load 16.5
2026-09-05 12:24:17 TEST MODE: C091 for 60 iterations, push exercised
2026-09-05 12:24:17 using 8 cores: 1 concurrent cases x 8 ranks
2026-09-05 12:24:19 checked 1 cases; 0 with differences; 0 numeric-equivalent
2026-09-05 12:24:19 C091 start
2026-09-05 12:24:48 C091 done rc=0 60 iterations, cap stop, 29 s
2026-09-05 12:24:48 TEST PASSED: build, verify, decompose, solve, reconstruct, zone extraction (posthoc_zoneT.json present) and packing (tar present); inspect cases/C091 and results/C091.tar.gz
```

#### Verification in `sb1/origin.git` and the Clone
- **Origin commit history**:
  ```text
  * 5730d67 (HEAD -> main) results: C091 (cap, 60 iterations)
  * 15154a5 results: L015 (unpushed)
  * db22b4c upstream commit
  * 398e672 base
  ```
  The clone's history rebased linearly on top of `origin/main`.
- **Result tarballs in bare origin**:
  Both `unit_cell_campaign/results/L015.tar.gz` and `unit_cell_campaign/results/C091.tar.gz` arrived cleanly, along with `ledger_Azan.csv`, `post_campaign_Azan.log`, `remote_run_Azan.log`, and `summary_Azan.md`.
- **Clone working tree**:
  `git -C sb1/remote_pc/IJHMT_CFP status` reported:
  `nothing to commit, working tree clean`.
- **Launcher self-update**:
  `diff -u sb1/remote_pc/run_remote_share.py sb1/remote_pc/IJHMT_CFP/run_remote_share.py` returned exit code 0 with zero diff. The launcher successfully overwritten itself with the repository version and re-executed.

#### Second Execution: Failure of Idempotence
Running `python3 run_remote_share.py --test --test-push` a second time in `sb1/remote_pc` resulted in an immediate fatal crash:
```text
+ git fetch -q origin main
+ git rebase -q origin/main
+ git push -q origin HEAD:main || echo 'push failed (the runner retries after every case)'
2026-09-05 12:25:10 environment: OpenFOAM v2406; mpirun mpirun (Open MPI) 4.1.2
2026-09-05 12:25:10 resources: 16 physical cores, 32 logical, 24.8 GB available, load 18.8
2026-09-05 12:25:10 TEST MODE: C091 for 60 iterations, push exercised
2026-09-05 12:25:10 using 8 cores: 1 concurrent cases x 8 ranks
2026-09-05 12:25:10 checked 1 cases; 1 with differences; 0 numeric-equivalent
the freshly built cases differ from the audited local build (verify_build.log); not running
```
Inspection of `sb1/remote_pc/IJHMT_CFP/unit_cell_campaign/verify_build.log`:
```text
C091 MISMATCH ['system/controlDict']
checked 1 cases; 1 with differences; 0 numeric-equivalent
```
Running the actual campaign `python3 run_remote_share.py --cores 8 --no-push` immediately afterward failed with the exact same error:
```text
checked 87 cases; 1 with differences; 0 numeric-equivalent
the freshly built cases differ from the audited local build (verify_build.log); not running
```
**Root Cause**:
In [`remote_run.py:133`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L133):
```python
if endtime:
    cd=os.path.join(d,"system/controlDict"); s=open(cd).read(); s=re.sub(r"endTime\s+\d+;","endTime %d;"%endtime,s,count=1); s=re.sub(r"writeInterval\s+\d+;","writeInterval %d;"%endtime,s,count=1); open(cd,"w").write(s)
```
The `--test` mode rewrites `writeInterval 1000;` to `writeInterval 60;` in `cases/C091/system/controlDict`.  
In [`make_manifest.py:14`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/make_manifest.py#L14):
```python
VOLATILE=re.compile(r"^(stopAt|endTime|startFrom)\s")
```
`VOLATILE` strips `stopAt`, `endTime`, and `startFrom`, but **fails to strip `writeInterval`**.  
On any rerun, [`build_cases.py:11`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/build_cases.py#L11) detects that `cases/C091` exists and skips rebuilding it. When `make_manifest.py check` runs before any solves start ([`remote_run.py:69`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L69)), `system/controlDict` has SHA-256 mismatch against `manifest_local_build.json`. The runner halts.  
**Severity**: **BLOCKING**. Rerunning `--test` or running the actual campaign after `--test` is blocked.

---

### 2. Sandbox 2: Breaking the Environment Further

In `scratch/sb2`, three failure modes were evaluated:

#### 2a. Rebase in Progress (Merge Conflict)
An upstream commit modified `unit_cell_campaign/README.md`. A conflicting edit was committed locally in the clone, and `git fetch origin main && git rebase origin/main` was invoked to put git into an unresolved rebase state (`interactive rebase in progress; onto fd3b66e`, `both modified: unit_cell_campaign/README.md`).
- **Launcher Execution**:
  [`run_remote_share.py:21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L21) executed `git rebase --abort >/dev/null 2>&1`.
  Next, during update, `git rebase -q origin/main` failed due to the local conflicting commit.
  Line 28 triggered the fallback replay:
  ```text
  rebase could not apply; replaying the local result files on top of origin/main
  + git rebase --abort >/dev/null 2>&1; git reset -q --soft origin/main && git add -A unit_cell_campaign/results && (git diff --cached --quiet || git commit -q -m 'results: replayed on origin by the launcher')
  ```
- **Result Preservation**:
  `origin.git` received commit `31ec918 results: replayed on origin by the launcher`, which contained `unit_cell_campaign/results/L015.tar.gz`. The unpushed result file was preserved and pushed. No result file was lost.

#### 2b. Lingering `.git/index.lock`
A lock file was created via `touch .git/index.lock`.
- **Launcher Execution**:
  [`run_remote_share.py:21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L21) (`rm -f .git/index.lock`) deleted the stale lock. The launcher completed fetch, rebase, build, OpenFOAM solve, and push without error (exit code 0). No result files were lost.

#### 2c. Unreachable Origin
The clone's remote was pointed to a non-existent path:
`git remote set-url origin /nonexistent/path.git`.
- **Launcher Execution**:
  `git fetch -q origin main` failed with exit code 128 (`fatal: '/nonexistent/path.git' does not appear to be a git repository`).
  [`run_remote_share.py:25`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L25) caught this:
  `fetch failed (network?); continuing with the local copy`.
  The runner proceeded with the local build and solved C091.
  During `push()`, [`remote_run.py:101`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L101) reported:
  `PUSH FAILED at 'fetch' (rc 128, see git_push.log); results stay in unit_cell_campaign/results and are pushed with the next case`.
- **Result Preservation**:
  All local result files (`C091.tar.gz`, `L015.tar.gz`, `ledger_Azan.csv`, `remote_run_Azan.log`) remained intact under `unit_cell_campaign/results/`. No result file was lost.

---

### 3. Sandbox 3: Multi-Machine Sharing Simulation

In `scratch/sb3`, two clones (`machine_A` and `machine_B`) were configured against `origin.git`.

#### 3a. Running `--test --test-push` in A then B
1. Machine A solved C091 (60 iterations) and pushed commit `c52d7eb results: C091 (cap, 60 iterations)`.
2. Machine B was executed with the same command. In [`remote_run.py:131`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L131):
   ```python
   if not a.test and done_elsewhere(cid,a): ...
   ```
   Because `not a.test` is `False`, Machine B **did not skip C091**, rebuilt it, solved 60 iterations, and called `push()`.
3. During Machine B's push, `git rebase -q origin/main` encountered a conflict on the binary tarball `results/C091.tar.gz`.
4. Fallback line 97 executed:
   `git reset -q --soft origin/main && git add -A ... && git commit -q -m 'results: C091 (cap, 60 iterations) (replayed on origin)'`
   Machine B created commit `ee23bfb` and pushed it to `origin.git`, **overwriting Machine A's tarball on origin**.

#### 3b. Sequence of Events Where Both Machines Solve the Same Case (Production Mode)
In production (without `--test`), both machines will solve the same case under the following sequences:
1. **Meeting in the Middle**:
   Machine 1 iterates forward from `ids[0]`; Machine 2 iterates backward (`--reverse`) from `ids[-1]`.
   When Machine 1 reaches case $K$, it executes `done_elsewhere(K, a)`. At that moment, Machine 2 is currently running case $K$ (cases take 1 to 45 minutes). Because Machine 2 has not yet called `push()`, `results/K.tar.gz` does not exist on origin. Machine 1 starts solving case $K$. Both machines are now solving case $K$ simultaneously.
2. **Concurrent Workers Race**:
   When `conc > 1` (e.g. `--cores 16` giving `conc = 2`), multiple threads pop cases from the queue. If Machine 1 pops cases $K$ and $K+1$ simultaneously before either is committed to origin, Machine 2 (advancing from the other side) can pop case $K$ concurrently.
3. **Transient Push / Network Failure**:
   If Machine 1 finishes case $K$ and `push()` fails due to temporary network unavailability or a non-fast-forward push rejection, `results/K.tar.gz` remains only in Machine 1's local results directory. Machine 2 runs `git fetch`, does not find `K.tar.gz` on origin, and proceeds to solve case $K$.

#### 3c. Behavior of `import_remote_results.py` with Duplicate Tarballs
In [`import_remote_results.py:8-18`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/import_remote_results.py#L8-L18):
- **Local Origin Priority**:
  Line 10: `if os.path.exists(done) and "host=" not in open(done).read(): print(cid,"skip: finished locally"); continue`.
  If the case was solved on the originating workstation (whose `DONE` file lacks `"host="`), remote tarballs are ignored.
- **Remote Collision Handling**:
  Because all tarballs share the filename `results/<case>.tar.gz`, git cannot hold two separate files for the same case. Whichever machine pushed last overwrites the tarball in `origin/main`.
  When `import_remote_results.py` pulls:
  Line 11: `if os.path.exists(done) and os.path.getmtime(done)>=os.path.getmtime(tgz): continue`.
  `git pull` updates the mtime of `results/<case>.tar.gz`. The importer detects `mtime(tgz) > mtime(done)` and unpacks the newer tarball, overwriting the previously imported case files in `cases/<case>/`.

---

## Part B: Code Audit

### 4. `remote_run.py` Audit

- **Git Commands**:
  - `git_repair()` ([`remote_run.py:83-85`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L83-L85)): executes `git rebase --abort; git merge --abort; git checkout -q -- unit_cell_campaign/remote_run.log`. Note that unlike `run_remote_share.py:21`, it does not remove `.git/index.lock`.
  - `push()` ([`remote_run.py:86-102`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L86-L102)): synchronized with `PUSH_LOCK`. Copies live log to `results/LOGNAME`, stages `results/`, commits, fetches, rebases on `origin/main` with soft-reset replay fallback, and pushes.
  - `done_elsewhere()` ([`remote_run.py:103-109`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L103-L109)): guarded by `PUSH_LOCK`. Fetches `origin/main` and attempts a rebase (aborting on conflict). Returns `True` if `results/<cid>.tar.gz` exists and `cases/<cid>/DONE` does not.
- **Per-Host File Names**:
  - `LOGNAME = "remote_run_%s.log" % os.uname().nodename.split(".")[0]` ([line 18](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L18))
  - `ledger_%s.csv` ([line 115](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L115))
  - `post_campaign_%s.log` ([line 116](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L116))
  - `summary_%s.md` ([line 126](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L126))
  Per-host naming isolates each machine's logs and tables, preventing merge conflicts in git.
- **What Happens When `results/` Does Not Exist Yet**:
  `results/` is created on demand by `pack()` ([line 75](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L75)) and `running_ledger()` ([line 114](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L114)).
  **Defect**: If `push()` is invoked directly when `results/` does not exist (e.g. at line 206 after skipping all cases on a fresh clone), line 94 (`shutil.copy(..., os.path.join(ROOT, "results", LOGNAME))`) crashes with `FileNotFoundError`.
- **Continuation Pass on a Machine That Skipped Most Cases**:
  In [`select_continuations.py:9`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/select_continuations.py#L9), cases are found via `glob.glob("cases/*/DONE")`. Cases that were skipped by `done_elsewhere()` do not have `DONE` on disk. Thus, a machine only selects and continues cases that finished locally. If a machine skipped all cases, 0 cases are selected, and the pass completes harmlessly.
- **`refresh_extraction()`**:
  Scans finished cases ([line 151](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L151)), checks if `posthoc_zoneT.json` version is `< 2`, re-executes `posthoc_zone_T.py`, repacks tarballs, updates the running ledger, and pushes.
- **`running_ledger()` Scope and Name Definitions**:
  All names used in `running_ledger(a)` (`ROOT`, `LOGNAME`, `PRE`, `sh`, `log`, `time`, `os`, `csv`, `open`, `float`, `sum`, `dict`, `list`) are fully defined. Note: `ids_all` at line 120 is defined globally at line 195 when run as `__main__`.
- **`check_env()` When OpenFOAM Is Reachable ONLY via `OPENFOAM_BASHRC`**:
  **Defect**: [`remote_run.py:29-35`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L29-L35) checks `shutil.which("chtMultiRegionSimpleFoam")` and then iterates strictly through `OF_CANDIDATES`. It **does not check `os.environ.get("OPENFOAM_BASHRC")`** at all (unlike `unit_cell.py:40` and `posthoc_zone_T.py:20`).
  If OpenFOAM is in a non-standard path exported via `OPENFOAM_BASHRC`, `find_openfoam()` exits with fatal error `sys.exit("OpenFOAM v2406 not found...")`.
- **Subprocess Environment**:
  All subprocess calls either inherit `os.environ` implicitly or pass `env=env` explicitly ([line 116](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L116) passing `POST_OUT`). OpenFOAM commands prepend `PRE`, ensuring the bashrc environment is loaded.

---

### 5. `run_remote_share.py` Audit

- **Clone vs Repair Path**:
  - Fresh clone (`not os.path.isdir(CLONE/.git)`): executes `git clone --filter=blob:none --sparse` over SSH (or HTTPS fallback), sets sparse-checkout, configures `user.name` and `user.email`.
  - Existing clone: executes `git_repair_and_update()` ([lines 19-29](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L19-L29)), aborting rebases/merges, clearing `index.lock`, dropping edits to `remote_run.log`, staging and committing uncommitted `results/`, fetching and rebasing on `origin/main`.
- **HTTPS Fallback**:
  If SSH clone returns non-zero, it prints an advisory that results will only push with a personal access token (or `--no-push`), then clones via `HTTPS`. If HTTPS also fails, it exits cleanly.
- **Git Identity**:
  Line 38 runs:
  `git config user.name >/dev/null || git config user.name 'remote runner'; git config user.email >/dev/null || git config user.email 'remote-runner@localhost'`.
  Ensures commits will never fail due to unset git author/committer identity.
- **Self-Update Loop Guard**:
  Line 42 guards the restart with `os.environ.get("RUN_REMOTE_SHARE_UPDATED") != "1"`.
  Before `os.execvp`, line 43 sets `os.environ["RUN_REMOTE_SHARE_UPDATED"] = "1"`.
  The restarted process sees this environment variable and skips self-updating, avoiding infinite restart loops.
- **Runner Execution with Operator Arguments**:
  Line 46 executes:
  `os.execvp(sys.executable, [sys.executable, script] + sys.argv[1:])`.
  Directly replaces the process image and forwards all operator flags (`--cores 16`, `--test`, etc.).
- **Windows CRLF Line Endings**:
  - Running `python3 run_remote_share.py` on a file with CRLF works natively (Python standard grammar handles `\r\n`).
  - Line 42 compares the file against the repo copy via `filecmp.cmp(me, repo_copy, shallow=False)`.
    Because binary comparison of `\r\n` vs `\n` returns `False`, line 43 copies `repo_copy` over `me` and restarts.
    The launcher **automatically repairs its own line endings to Linux `\n` on first launch**.

---

### 6. Extraction, Post-Processing, and Solver Logic Audit

- **`posthoc_zone_T.py` (Version 2)**:
  - Six streamwise stations ($x = 0, L/5, \dots, L$) and five interface bins ($wallB0 \dots wallB4$).
  - Correctly re-runs `topoSet` to generate faceZones, executes `chtMultiRegionSimpleFoam -postProcess -latestTime -dict system/fluid/posthocFuncs`, reads `surfaceFieldValue.dat`, and outputs `posthoc_zoneT.json` with `"version": 2`.
  - Skips empty face zones (e.g. `chanX` at OR 1, `clearX` at OR 0) so `surfaceFieldValue` does not abort.
- **`post_campaign.py`**:
  - `stop_type` ([line 141](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/post_campaign.py#L141)): classifies stop mechanism into `"converged"`, `"envelope"`, `"diverged"`, or `"cap"`. Verified.
  - `POST_OUT` ([line 158](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/post_campaign.py#L158)): environment variable overrides output path. Verified.
  - **Nusselt Definition on OR = 1 Cases**:
    In [`post_campaign.py:92-93`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/post_campaign.py#L92-L93):
    `ok = Z.get("version",1)>=2 and all(("Tw_wallB%d_K"%i) in Z for i in range(NB)) and all(("T_chanX%d_K"%i) in Z for i in range(NB+1))`
    For OR = 1 cases, `T_chanX%d_K` does not exist (the station temperatures are in `T_clearX%d_K`). Thus `ok` evaluates to `False`, and `Nu`, `Nu_field`, and `Phi_eff` evaluate to `NaN` in `ledger_<host>.csv`.
  - **Version 1 JSON Fallback**:
    If a JSON has version 1, `ok` is `False`, setting `out["Nu"] = NaN`. However, `Nu_edge` and `Nu_cell` remain populated. Line 66 only invokes `posthoc_zone_T.process(case)` if `mtime(json) <= mtime(done)`.
- **`select_continuations.py`**:
  Checks residuals ($Ux, Uy, Uz, p_{rgh} < 10^{-4}, h < 10^{-6}$), minimum iterations ($1200$), envelope temperature ($\le 70^\circ\text{C}$), and iteration cap ($12000$). Verified.
- **`converge_watchdog.py`**:
  Polls solver log and monitors every 20 s. Stops solver via `stopAt writeNow;` upon convergence or upon violating the $70^\circ\text{C}$ validity envelope after iteration 4000. Verified.
- **`make_manifest.py`**:
  Uses SHA-256 for dictionaries and `NUMTOL = 1e-9` relative tolerance on floating-point tokens in `case_meta.json` and `constant/fluid/thermophysicalProperties`.
  **Defect**: As discovered in Part A, `VOLATILE` ignores `stopAt`, `endTime`, and `startFrom`, but does not ignore `writeInterval`.
- **`unit_cell.py`**:
  - `quad_fit` ([lines 22-25](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/unit_cell.py#L22-L25)): evaluates an exact 3-point Lagrange polynomial using pure IEEE double arithmetic in a fixed operation sequence, eliminating platform-dependent differences seen with `numpy.polyfit`.
  - `of_prefix()` ([lines 35-43](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/unit_cell.py#L35-L43)): correctly inspects `os.environ.get("OPENFOAM_BASHRC")`.

---

### 7. `.gitignore` and `README.md` Alignment

- **Tracked vs Pushed Files in Git**:
  - Live runner logs in `unit_cell_campaign/*.log` are ignored by line 23 of `.gitignore`.
  - Snapshot logs and ledgers copied into `unit_cell_campaign/results/` (`results/remote_run_<node>.log`, `results/ledger_<node>.csv`, etc.) are pushed because `unit_cell_campaign/*.log` does not match subdirectories.
  - Built meshes and runtime case directories `unit_cell_campaign/cases/` are ignored by line 20.
  - Result archives `unit_cell_campaign/results/*.tar.gz` are tracked and pushed.
- **Discrepancies**:
  1. `.gitignore` line 24 contains `!unit_cell_campaign/remote_run.log`. The file `remote_run.log` remains tracked in the git repository blob index from historical commits.
  2. `unit_cell_campaign/README.md` lines 58-60 refers to `results/ledger_remote.csv` and `results/summary_remote.md`, whereas the runner writes `results/ledger_<node>.csv` and `results/summary_<node>.md`.
  3. `unit_cell_campaign/README.md` line 72 states that OpenFOAM is found via `OPENFOAM_BASHRC`, but `remote_run.py:find_openfoam()` does not read this variable.

---

## Verdict

```
BLOCKING (would lose results, stop the run, or produce a wrong number on the second machine):
1. `remote_run.py:133` modifies `writeInterval` in `cases/C091/system/controlDict` during `--test` mode, but `make_manifest.py:14` does not include `writeInterval` in `VOLATILE`. On any subsequent run (`--test` rerun or the production run `python3 run_remote_share.py`), `build_cases.py` skips rebuilding C091, `make_manifest.py check` flags `C091 MISMATCH ['system/controlDict']`, and `remote_run.py:71` aborts with exit code 1 (`the freshly built cases differ from the audited local build; not running`), completely halting the campaign.
2. `remote_run.py:31-35` (`find_openfoam()`) fails to inspect `os.environ.get("OPENFOAM_BASHRC")`. If OpenFOAM is installed in a non-standard path reachable only through `OPENFOAM_BASHRC` (as documented in `README.md:72`), `find_openfoam()` halts with fatal error `sys.exit("OpenFOAM v2406 not found...")`.

NON-BLOCKING:
1. In `remote_run.py:94`, `push()` attempts `shutil.copy(..., "results/LOGNAME")` without checking or creating `results/` via `os.makedirs(..., exist_ok=True)`. If `push()` is called before any case completes (e.g. line 206 after skipping all cases on a fresh clone), it raises `FileNotFoundError`.
2. In `remote_run.py:131`, `done_elsewhere()` is bypassed when `a.test` is active (`if not a.test and done_elsewhere(...)`), causing two machines running `--test` to solve the same case and overwrite each other's test tarball on origin via git replay fallback.
3. In `post_campaign.py:92`, `ok` checks `all(("T_chanX%d_K"%i) in Z for i in range(NB+1))`. For OR = 1 cases (which have no fin channel), station temperatures are stored under `clearX`, causing `ok` to evaluate to `False` and writing `Nu = NaN` and `Nu_field = NaN` into `ledger_<host>.csv`.
4. In `post_campaign.py:66`, `posthoc_zone_T.process(case)` is skipped if `mtime(json) > mtime(done)`. When executed standalone on finished cases with version 1 JSONs whose timestamps are newer than `DONE`, it does not re-extract and leaves `Nu = NaN`.
5. Documentation discrepancy: `README.md` lines 58-60 states output is written to `ledger_remote.csv` and `summary_remote.md`, but `remote_run.py` writes per-host files `ledger_<node>.csv` and `summary_<node>.md`.
6. Legacy repository artifact: `!unit_cell_campaign/remote_run.log` remains in `.gitignore` and `unit_cell_campaign/remote_run.log` remains tracked in the repository tree.

NOT VERIFIABLE:
1. Full 87-case solution convergence and physical accuracy across all cases beyond the single 60-iteration test case executed on this machine.
2. Production SSH authentication to GitHub on the physical remote machine (tested in sandboxes against bare local git repositories).

VERDICT: FAIL
```
