# Remote set-up audit, round 4 (5 September 2026): launcher and runner before hand-over

Auditor: Gemini 3.7 Flash through the Antigravity CLI, on the corrected package (commit 64b1d72) with the sandboxes of round 3. Verdict PASS; the two non-blocking items (a stale index.lock in the runner's repair; the case where both machines solve the same case) were taken in the next commit. The auditor's report follows verbatim.

I have launched `python3 run_remote_share.py --test --test-push` in sandbox `scratch4/sb1/remote_pc` to test clone repair and the single-case test solve. Waiting for the command to finish.
Waiting for task-46 to finish.
I have launched `python3 run_remote_share.py --test --test-push` in `scratch4/sb2/remote_pc` with a conflicting rebase in progress. Waiting for the command to finish.
I have launched `python3 run_remote_share.py --test --test-push` in `scratch4/sb3/remote_pc` (Machine A). Waiting for it to complete.
Waiting for task-84 to finish.
I have launched `python3 remote_run.py --test --test-push` on Machine B in `scratch4/sb3`. Waiting for completion.
# Adversarial Audit Report: Remote Share Launcher and Runner (Round 4)

**Audited Directory**: [`package/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package)  
**Audit Specification**: [`instructions_round3.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/instructions_round3.md) (including the **Round 4** section)  
**Prior Audits**: [`round1_FAIL.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/round1_FAIL.md), [`round2_PASS.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/round2_PASS.md), [`round3_FAIL.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/round3_FAIL.md)  
**Production Start Reference**: [`prod_start_check.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/prod_start_check.txt)  
**Auditor**: Adversarial Auditor (Gemini 3.7 Flash; Read-Only on `package/`, sandboxed execution exclusively under `scratch4/`)

---

## Part A: Exercising the System in Throwaway Sandboxes

All executions were performed exclusively using the `--test --test-push` path in throwaway sandboxes under `scratch4/`. The production run was never started.

---

### 1. Sandbox 1: Exercise the Launcher in the Second Machine's Broken State

Sandbox `scratch4/sb1` was constructed with:
```bash
bash make_sandbox.sh /tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/scratch4/sb1
```
This instantiated:
- A bare `origin.git` with an upstream commit (`1972994 upstream commit`) modifying `README.md`.
- A sparse clone `sb1/remote_pc/IJHMT_CFP` containing:
  - An unpushed result commit: `015fc1a results: L015 (unpushed)` with `unit_cell_campaign/results/L015.tar.gz`.
  - Uncommitted modifications to the legacy tracked log `unit_cell_campaign/remote_run.log`.
- A launcher copy `sb1/remote_pc/run_remote_share.py` pointing to `sb1/origin.git`.

#### 1a. First Run (`python3 run_remote_share.py --test --test-push`)
Executed directly from `sb1/remote_pc`:
```text
+ git fetch -q origin main
+ git rebase -q origin/main
+ git push -q origin HEAD:main || echo 'push failed (the runner retries after every case)'
launcher updated from the repository; restarting
+ git fetch -q origin main
+ git rebase -q origin/main
+ git push -q origin HEAD:main || echo 'push failed (the runner retries after every case)'
2026-09-05 13:27:15 environment: OpenFOAM v2406; mpirun mpirun (Open MPI) 4.1.2
2026-09-05 13:27:15 resources: 16 physical cores, 32 logical, 24.8 GB available, load 16.3
2026-09-05 13:27:15 TEST MODE: C091 for 60 iterations, push exercised
2026-09-05 13:27:15 using 8 cores: 1 concurrent cases x 8 ranks
2026-09-05 13:27:16 checked 1 cases; 0 with differences; 0 numeric-equivalent
2026-09-05 13:27:16 C091 start
2026-09-05 13:27:41 C091 done rc=0 60 iterations, cap stop, 25 s
2026-09-05 13:27:42 TEST PASSED: build, verify, decompose, solve, reconstruct, zone extraction (posthoc_zoneT.json present) and packing (tar present); inspect cases_test/C091 and results_test/C091.tar.gz
```

#### 1b. Verification in `sb1/origin.git` and Clone
- **Origin Git Log**:
  ```text
  * a4b9e8d (HEAD -> main) results: C091 (cap, 60 iterations)
  * 015fc1a results: L015 (unpushed)
  * 1972994 upstream commit
  * 3fd0672 base
  ```
  The clone's commit history rebased linearly on top of `origin/main`.
- **Result Tarballs in Bare Origin**:
  `git -C sb1/origin.git ls-tree -r --name-only HEAD` confirmed that both tarballs arrived:
  - `unit_cell_campaign/results/L015.tar.gz` (unpushed commit preserved and delivered)
  - `unit_cell_campaign/results_test/C091.tar.gz` (test tarball isolated under `results_test/`, keeping `results/` pristine)
- **Clone Working Tree**:
  `git -C sb1/remote_pc/IJHMT_CFP status` returned:
  `nothing to commit, working tree clean`.
- **Launcher Self-Update**:
  `diff -u sb1/remote_pc/run_remote_share.py sb1/remote_pc/IJHMT_CFP/run_remote_share.py` returned exit code 0 with zero difference.

#### 1c. Second Run: Verification of Idempotence
In Round 3, running a second time immediately halted with:
`C091 MISMATCH ['system/controlDict']` (exit code 1).

In Round 4, executing `python3 run_remote_share.py --test --test-push` a second time produced:
```text
+ git fetch -q origin main
+ git rebase -q origin/main
+ git push -q origin HEAD:main || echo 'push failed (the runner retries after every case)'
2026-09-05 13:27:48 environment: OpenFOAM v2406; mpirun mpirun (Open MPI) 4.1.2
2026-09-05 13:27:48 resources: 16 physical cores, 32 logical, 24.8 GB available, load 18.1
2026-09-05 13:27:48 TEST MODE: C091 for 60 iterations, push exercised
2026-09-05 13:27:48 using 8 cores: 1 concurrent cases x 8 ranks
2026-09-05 13:27:48 checked 1 cases; 0 with differences; 0 numeric-equivalent
2026-09-05 13:27:48 C091 skip (done)
2026-09-05 13:27:48 TEST PASSED: build, verify, decompose, solve, reconstruct, zone extraction (posthoc_zoneT.json present) and packing (tar present); inspect cases_test/C091 and results_test/C091.tar.gz
```
- The manifest check passed bit for bit (`0 with differences; 0 numeric-equivalent`).
- The finished test case was cleanly recognized and skipped (`C091 skip (done)`).
- The origin commit tip remained unchanged at `a4b9e8d`.
- The clone working tree remained clean.
**Idempotence is fully verified.**

---

### 2. Sandbox 2: Fault Tolerance and Result Preservation

Sandbox `scratch4/sb2` was built using `make_sandbox.sh` and subjected to three destructive failure modes:

#### 2a. Unresolved Rebase in Progress (Merge Conflict)
An upstream commit modified `unit_cell_campaign/README.md`. A conflicting edit was committed locally, and a rebase was initiated to produce a merge conflict:
`CONFLICT (content): Merge conflict in unit_cell_campaign/README.md`
`interactive rebase in progress; onto d3a58b6`.

When the launcher was executed (`python3 run_remote_share.py --test --test-push`):
1. [`run_remote_share.py:21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L21) executed `git rebase --abort >/dev/null 2>&1`.
2. Standard rebase failed due to the uncommitted local conflict; lines 26-28 triggered the fallback replay:
   `rebase could not apply; replaying the local result files on top of origin/main`
   `git rebase --abort >/dev/null 2>&1; git reset -q --soft origin/main && git add -A unit_cell_campaign/results && (git diff --cached --quiet || git commit -q -m 'results: replayed on origin by the launcher')`
3. Origin received:
   - Commit `f204a9f results: replayed on origin by the launcher` (preserving `results/L015.tar.gz`)
   - Commit `28ea0da results: C091 (cap, 60 iterations) (replayed on origin)` (delivering `results_test/C091.tar.gz`)
**Result Preservation**: Both `L015.tar.gz` and `C091.tar.gz` were delivered to origin. No result file was lost.

#### 2b. Lingering `.git/index.lock`
A lock file was placed in `.git/index.lock`.
1. [`run_remote_share.py:21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L21) executed `rm -f .git/index.lock`.
2. The launcher completed fetch, rebase, manifest verification, and execution without error (exit code 0).
**Result Preservation**: No interruption, zero lost results.

#### 2c. Unreachable Origin (Network / Authentication Failure)
The clone's remote was pointed to a non-existent path (`/tmp/nonexistent/origin.git`).
1. `git fetch -q origin main` failed with exit code 128.
2. [`run_remote_share.py:25`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L25) logged `fetch failed (network?); continuing with the local copy` and proceeded.
3. The runner built and executed C091 locally.
4. During `push()`, [`remote_run.py:102`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L102) logged:
   `PUSH FAILED at 'fetch' (rc 128, see git_push.log); results stay in unit_cell_campaign/results and are pushed with the next case`.
5. Inspection of the clone directory confirmed that `results_test/C091.tar.gz` (22.7 KB), `results/L015.tar.gz`, and `results/remote_run_Azan.log` remained intact on disk.
**Result Preservation**: All local result files were preserved on disk pending future pushes. No result file was lost.

---

### 3. Sandbox 3: Multi-Machine Sharing Simulation

In `scratch4/sb3`, two separate clones (Machine A and Machine B) were configured against `origin.git`.
- Machine A executed `python3 run_remote_share.py --test --test-push` and pushed commit `b62c5fb results: C091 (cap, 60 iterations)`.
- Machine B executed `python3 remote_run.py --test --test-push` and pushed commit `5c8573d results: C091 (cap, 60 iterations)`.
Origin cleanly recorded both commits in linear succession.

#### 3a. Sequence of Events Where Both Machines Solve the Same Case (Production Run)
In production (running without `--test`), both machines can solve the same case under the following specific sequences:
1. **Meeting in the Middle**:
   Machine 1 processes `run_list_remote.txt` forward from index 0; Machine 2 processes with `--reverse` backward from the end. When Machine 1 finishes case $K-1$, it inspects case $K$ via `done_elsewhere(K, a)`. At that moment, Machine 2 is actively solving case $K$ (cases take 1 to 45 minutes). Because Machine 2 has not finished, `results/K.tar.gz` is not yet on origin. Machine 1 finds no result and starts solving case $K$. Both machines solve case $K$ concurrently.
2. **Concurrent Worker Slots (`conc > 1`)**:
   When `--cores 16` is used, `conc = 2` concurrent cases are solved in parallel. Machine 1 pops cases $K$ and $K+1$ simultaneously before either is committed to origin. Machine 2 (advancing from the other side) checks case $K$, finds it unpushed, and begins solving case $K$.
3. **Transient Push / Remote Outage**:
   If Machine 1 finishes case $K$ and `push()` fails due to transient network rejection or SSH timeout, `results/K.tar.gz` remains only on Machine 1's local disk. When Machine 2 checks case $K$, `done_elsewhere()` fetches from origin, does not find `K.tar.gz`, and Machine 2 solves case $K$.
4. **Flag `--no-push`**:
   If either machine runs with `--no-push`, `done_elsewhere()` unconditionally returns `False` ([`remote_run.py:107`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L107)), preventing either from skipping cases finished on the other.

#### 3b. Behavior of `import_remote_results.py` with Duplicate Tarballs
In [`import_remote_results.py:8-19`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/import_remote_results.py#L8-L19):
- **Local Origin Priority**:
  Line 10: `if os.path.exists(done) and "host=" not in open(done).read(): print(cid,"skip: finished locally"); continue`.
  Cases finished locally on the originating workstation lack `"host="` in their `DONE` file and are never overwritten by remote results.
- **Remote Collisions**:
  In git, all archives share the pathname `results/<case>.tar.gz`. When two machines push the same case, the second push replays on origin, making its tarball the tip of `origin/main`.
  When `import_remote_results.py` executes:
  - Line 6 runs `git pull -q --rebase origin main`, updating the file modification timestamp (`mtime`) of `results/<case>.tar.gz` to the pull time.
  - Line 11 checks `if os.path.exists(done) and os.path.getmtime(done)>=os.path.getmtime(tgz): continue`. Because `mtime(tgz) > mtime(done)`, this check evaluates to `False`.
  - Lines 12-18 unpack the newer tarball, overwriting the previously imported case files in `cases/<case>/` while preserving local dictionaries (line 17: `if os.path.exists(target) and "system/" in m.name and "controlDict" not in m.name: continue`).
  - Archives under `results_test/` are ignored because line 8 matches only `unit_cell_campaign/results/*.tar.gz`.

---

## Part B: Comprehensive Code and Configuration Audit

### 4. `remote_run.py` Audit

- **Git Commands**:
  - `git_repair()` ([lines 84-86](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L84-L86)): Aborts pending rebase/merge operations and reverts modifications to `unit_cell_campaign/remote_run.log`.
  - `push()` ([lines 87-103](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L87-L103)): Synchronized with `PUSH_LOCK`. Line 95 now explicitly ensures `results/` exists:
    ```python
    os.makedirs(os.path.join(ROOT,"results"),exist_ok=True); shutil.copy(os.path.join(ROOT,LOGNAME),os.path.join(ROOT,"results",LOGNAME))
    ```
    This completely eliminates the Round 3 `FileNotFoundError` (Non-Blocking 1).
    Line 96 conditionally stages `results_test` if present without polluting production `results/`. Rebase failure triggers soft-reset replay on origin.
  - `done_elsewhere()` ([lines 104-110](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L104-L110)): Guarded by `PUSH_LOCK`. Fetches and rebases; returns `True` only if `results/<cid>.tar.gz` exists and `cases/<cid>/DONE` does not.
- **Per-Host File Names**:
  - `LOGNAME = "remote_run_%s.log" % os.uname().nodename.split(".")[0]` ([line 18](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L18))
  - `ledger_%s.csv` ([line 116](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L116))
  - `post_campaign_%s.log` ([line 117](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L117))
  - `summary_%s.md` ([line 127](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L127))
  Prevents git merge conflicts between concurrent machines.
- **Continuation Pass on a Machine That Skipped Most Cases**:
  [`select_continuations.py:9`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/select_continuations.py#L9) inspects only cases with `cases/*/DONE`. Skipped cases lack `DONE` and are ignored. If all cases were skipped, 0 cases are selected, and the pass terminates cleanly.
- **`refresh_extraction()`**:
  Lines 157-171 re-extract cases whose `posthoc_zoneT.json` version is `< 2`.
- **`running_ledger()` Scope and Name Definitions**:
  All referenced symbols (`ROOT`, `LOGNAME`, `PRE`, `sh`, `log`, `time`, `os`, `csv`, `ids_all`) are defined. `ids_all` is initialized globally at line 205 prior to any invocation.
- **OpenFOAM Environment (`OPENFOAM_BASHRC`)**:
  Lines 29-35 now check `os.environ.get("OPENFOAM_BASHRC","")` as the very first candidate in `OF_CANDIDATES`:
  ```python
  OF_CANDIDATES=[os.environ.get("OPENFOAM_BASHRC",""),"/usr/lib/openfoam/openfoam2406/etc/bashrc", ...]
  ```
  Line 37 exports `os.environ["OPENFOAM_BASHRC"]=OF.split()[1]`. Subprocesses inherit this environment.
- **The `--test` Path Isolation**:
  [`remote_run.py:130-135`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L130-L135) directs `--test` to work on a cloned directory under `cases_test/<cid>`:
  ```python
  def case_dir(cid,a):
      if not a.test: return os.path.join(ROOT,"cases",cid)
      d=os.path.join(ROOT,"cases_test",cid)
      if not os.path.exists(os.path.join(d,"case_meta.json")): shutil.copytree(os.path.join(ROOT,"cases",cid),d)
      return d
  ```
  The canonical `cases/` directory and its dictionaries are completely untouched. Pack outputs go to `results_test/<cid>.tar.gz` ([line 75](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/remote_run.py#L75)).

---

### 5. `run_remote_share.py` Audit

- **Clone vs. Repair Path**:
  - Fresh clone ([lines 31-37](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L31-L37)): Sparse clone containing `unit_cell_campaign/`, `/run_remote_share.py`, `/.gitignore`, `/README.md`.
  - Existing clone ([lines 19-29](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/run_remote_share.py#L19-L29)): Clears rebase/merge/cherry-pick, clears `.git/index.lock`, restores legacy log, commits pending results, fetches, and rebases on `origin/main` with soft-reset replay fallback.
- **HTTPS Fallback**:
  Line 34 catches non-zero exit from SSH clone and falls back to HTTPS.
- **Git Identity**:
  Line 38 sets fallback `user.name 'remote runner'` and `user.email 'remote-runner@localhost'`.
- **Self-Update Loop Guard**:
  Line 42 checks `filecmp.cmp(me, repo_copy, shallow=False)` and guards re-exec with `RUN_REMOTE_SHARE_UPDATED != "1"`. Line 43 sets `RUN_REMOTE_SHARE_UPDATED = "1"` before calling `os.execvp`.
- **Runner Execution**:
  Line 46 calls `os.execvp(sys.executable, [sys.executable, script] + sys.argv[1:])`, forwarding all operator arguments (`--cores 16`, `--test`, etc.).
- **Windows CRLF Handling**:
  Python handles CRLF syntax natively. When compared with the repository's LF file via `filecmp.cmp(me, repo_copy, shallow=False)`, the byte difference evaluates to `False`. Line 43 replaces `me` with `repo_copy` and restarts, automatically normalizing CRLF to Unix LF on first launch.

---

### 6. Extraction, Post-Processing, and Solver Logic Audit

- **`posthoc_zone_T.py` (Version 2)**:
  - Six streamwise stations ($x = 0, L/5, \dots, L$) and five interface bins ($wallB0 \dots wallB4$).
  - Correctly ignores empty face zones at OR 0 and OR 1 to prevent `surfaceFieldValue` crashes.
  - `of_prefix()` ([lines 15-23](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/posthoc_zone_T.py#L15-L23)) respects `OPENFOAM_BASHRC`.
- **`post_campaign.py`**:
  - `stop_type` ([line 145](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/post_campaign.py#L145)): Correctly flags `"converged"`, `"envelope"`, `"diverged"`, or `"cap"`.
  - `POST_OUT` ([line 116](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/post_campaign.py#L116)): Honoured via environment variable.
  - **Version 1 JSON Fallback**: Lines 66-70 now re-extract any case where `version < 2` regardless of file mtime:
    ```python
    def _stale(pz):
        if not os.path.exists(pz): return True
        try: return json.load(open(pz)).get("version",1)<2
        except Exception: return True
    if os.path.exists(dn) and (_stale(pz) or os.path.getmtime(pz)<=os.path.getmtime(dn)):
        import posthoc_zone_T; posthoc_zone_T.process(case)
    ```
    Verified: eliminates Round 3 Non-Blocking 4.
  - **OR = 1 Nusselt Definition**: Line 9 explicitly documents that Nu is NaN by construction at OR = 1 because no fin channel exists ($H_{\text{fin}} = 0$).
- **`make_manifest.py`**:
  - Line 14 updated to:
    ```python
    VOLATILE=re.compile(r"^(stopAt|endTime|startFrom|writeInterval)\s")
    ```
    Verified: eliminates Round 3 Blocking 1.
  - Relative tolerance `NUMTOL = 1e-9` prevents false mismatches from platform-dependent float stringification.
- **`select_continuations.py`**:
  Checks residuals, 1200 iteration minimum, $70^\circ\text{C}$ validity envelope, and iteration cap.
- **`converge_watchdog.py`**:
  Stops solver on residual convergence after 1200 iterations or on exceeding $70^\circ\text{C}$ after 4000 iterations.
- **`build_cases.py` & `unit_cell.py`**:
  - `quad_fit()` ([lines 22-25](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/unit_cell.py#L22-L25)) uses exact 3-point Lagrange polynomial in fixed evaluation order to eliminate floating-point non-determinism across compilers.
  - `of_prefix()` ([lines 35-43](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/unit_cell.py#L35-L43)) honours `OPENFOAM_BASHRC`.

---

### 7. `.gitignore` and `README.md` Alignment

- **Tracked vs Ignored Files in Git**:
  - [`package/.gitignore:20-21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/.gitignore#L20-L21) ignores both `unit_cell_campaign/cases/` and `unit_cell_campaign/cases_test/`.
  - Line 24 ignores `unit_cell_campaign/*.log` (top-level live logs stay local).
  - Line 25 explicitly un-ignores the legacy tracked file: `!unit_cell_campaign/remote_run.log`.
  - Directory `unit_cell_campaign/results/` is tracked, pushing `.tar.gz`, `ledger_<host>.csv`, `summary_<host>.md`, and `remote_run_<host>.log`.
  - Directory `unit_cell_campaign/results_test/` is staged only during `--test-push`.
- **Documentation Alignment**:
  [`unit_cell_campaign/README.md:58-63`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit3/package/unit_cell_campaign/README.md#L58-L63) precisely documents:
  - Per-host outputs (`ledger_<host>.csv`, `summary_<host>.md`, `remote_run_<host>.log`).
  - `--test` execution under `cases_test/` and packing into `results_test/`.
  - The historical purpose and tracking of `remote_run.log`.
  - OpenFOAM lookup precedence via PATH, `OPENFOAM_BASHRC`, or default install directories.

---

## Verdict

```
BLOCKING (would lose results, stop the run, or produce a wrong number on the second machine): none
NON-BLOCKING:
1. In `remote_run.py:84-86`, `git_repair()` runs `git rebase --abort; git merge --abort; git checkout -q -- unit_cell_campaign/remote_run.log`, but does not remove `.git/index.lock` (unlike `run_remote_share.py:21`). If an operating system crash or SIGKILL interrupts git in the middle of a multi-case solve loop, the next case's push could encounter a stale `.git/index.lock` until the launcher is restarted.
2. In production mode without a distributed lock manager, if two machines meet in the middle of `run_list_remote.txt` or have concurrent worker slots (`conc > 1`), both machines can solve the same case concurrently before either pushes. The second machine's tarball overwrites the first on origin, and `import_remote_results.py` imports whichever tarball was pushed last.
NOT VERIFIABLE:
1. Full 87-case physical convergence and accuracy across the entire parameter space (production run was not started per instruction; verified via `prod_start_check.txt` and single 60-iteration test solves).
2. Remote SSH authentication to GitHub on the physical remote machine (tested in sandboxes against bare local git repositories).
VERDICT: PASS
```
