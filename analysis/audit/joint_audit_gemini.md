# Joint audit of the hands-off remote package (6 September 2026): Gemini 3.7 Flash

Auditor: Gemini 3.7 Flash through the Antigravity CLI, on an isolated copy of the package (commit 9790621) with sandboxes reproducing the second machine's history. Verdict PASS, four non-blocking items, all fixed (sandbox script absolute paths, .gitignore for cases_all/, manifest excludes Python bytecode, replay path includes results_test). The auditor's report follows verbatim.

### Joint Audit Report: Campaign Set-Up and Remote Runner Verification

**Auditor:** Gemini 3.7 Flash  
**Audited Package Commit:** `97906210a129ce4501ea3ec527a2abf8876ad445` (`package/COMMIT.txt`)  
**Working Trees Examined:** `package/` (read-only), sandboxes under `scratch/`  

---

### 1. Sandbox Execution and Origin Inspection (`instructions_joint_audit.md` § 1 & 3)

The sandbox was initialized in `scratch/sb1` reproducing the state of the remote machine (modified legacy log `unit_cell_campaign/remote_run.log`, unpushed commit `results: L015 (unpushed)`, and upstream commit advancing `origin.git`). *(Note: `package/make_sandbox.sh` path resolution was corrected in `scratch/make_sandbox_fixed.sh` as detailed in Non-Blocking issue #1).*

#### Run 1: `python3 run_remote_share.py --test --test-push`
- **Execution & Self-Update:** The launcher started, detected a local difference against the repo's copy (`run_remote_share.py:43`), updated itself via `shutil.copy`, set `RUN_REMOTE_SHARE_UPDATED=1`, and restarted.
- **Git Repair & Replay:** Repaired the interrupted state, checked out legacy `remote_run.log`, rebased the unpushed commit onto `origin/main` (`80c6b75 upstream commit`), and pushed `results/L015.tar.gz`.
- **Case Execution:** Built `C091` under `cases/`, verified bit-for-bit against `manifest_local_build.json` (0 differences), executed 60 iterations under `cases_test/C091` on 8 MPI ranks (`chtMultiRegionSimpleFoam`, wall time 63 s), ran `reconstructPar -latestTime`, extracted version-2 stations/bins into `posthoc_zoneT.json`, packed `results_test/C091.tar.gz`, and pushed.
- **Bare Origin Tree (`git -C scratch/sb1/origin.git ls-tree -r --name-only HEAD`):** Contains `unit_cell_campaign/results/L015.tar.gz` and `unit_cell_campaign/results_test/C091.tar.gz`.
- **History & Tree State:** Linear (`* 06c52e1 results: C091 (cap, 60 iterations)` $\rightarrow$ `* 494c235 results: L015 (unpushed)` $\rightarrow$ `* 80c6b75 upstream commit` $\rightarrow$ `* 7e1430a base`). Working tree clean.

#### Run 2: `python3 run_remote_share.py --analyse`
- **Tarball Extraction:** Unpacked all valid result tarballs from `results/` (71 valid + 1 corrupted dummy `L015.tar.gz` which was safely skipped) and `results_local/` (90 tarballs), yielding 161 case directories in `unit_cell_campaign/cases_all/`.
- **Pipeline Execution:** 
  1. `post_campaign.py` generated `analysis/dataset_ledger_unitcell.csv` (161 rows).
  2. `refit_closures.py` fitted Eq. 23 (leading edge & effective) and Eq. 24, writing `analysis/refit_stats.csv`.
  3. `solve_eq22.py` solved the constrained design optimization, writing `analysis/optimum.csv` and `analysis/feasibility_map.csv`.
  4. `sealed_dp_check.py` verified the sealed channel laminar pressure drop against Shah-London, writing `analysis/sealed_dp_check.csv`.
  5. `campaign_results_summary.py` produced `analysis/campaign_results_summary.md`.
  6. `fig_campaign.py` generated 5 publication figures (`.png` and `.pdf`) into `analysis/figures/`.
  7. `make_campaign_tables.py` generated 5 LaTeX tables into `analysis/tables/`.
  8. Wrote `analysis/MANIFEST_sha256.txt` and pushed `analysis/` to origin.
- **Origin State:** Bare origin now contains all files under `analysis/`. History remains strictly linear (`* 553cbb9 analysis: regenerated on Azan ...`).

#### Run 3: `python3 run_remote_share.py --test --test-push` (second run)
- Verified idempotency: `C091` recognized as already solved (`C091 skip (done)`), exiting with code 0 in under 1 second. Tree clean.

#### Comparison of Sandbox Analysis Outputs vs `package/analysis/`
- **Ledger Verification:** For the 133 cases present in `package/analysis/dataset_ledger_unitcell.csv`, the newly regenerated ledger matches **100% bit-for-bit across all 115 columns**.
- **File Differences:**
  - `dataset_ledger_unitcell.csv`: 161 rows in sandbox vs 133 rows in package. The 28 additional rows correspond to completed cases already present in `package/unit_cell_campaign/results/` (`E004`–`E030` and `L001`) that had not yet been unpacked into `package/analysis/` when the manuscript was frozen on 5 September 2026 (`package/analysis/README.md:20-23`).
  - `refit_stats.csv`: Contains holdout partitions (`holdout_EFL-1`, `cross_combinations`, `fixed_fin_sweep`, `holdout_thermal_load`) made possible by the newly imported cases; the `calibration` row is **100% identical** in all parameters, errors, and objective SSRs.
  - `tables/tab_fixed_fin.tex`: Generated in the sandbox because fixed-fin cases were unpacked (predicted by `package/analysis/README.md:13`).
  - `figures/fig_parity.(png|pdf)`: Updated with holdout data points for EFL-1; other figures re-rendered with identical curves and layout.
  - `campaign_results_summary.md` and counts tables: Updated to reflect 161 completed cases.
  - `optimum.csv`, `feasibility_map.csv`, `sealed_dp_check.csv`, and `tables/tab_coefficients.tex`: **100% identical**.

---

### 2. Fault Injection & Resilience Tests (`instructions_joint_audit.md` § 2)

| Fault Injected | Observed Behavior | Run Outcome | Silent Wrong Numbers? |
|---|---|---|---|
| **Rebase left in progress** (`.git/rebase-merge` present) | `git_repair_and_update()` detects rebase collision, executes `git rebase --abort`, resets soft onto `origin/main`, stages results, and commits `results: replayed on origin by the launcher`. | Succeeded (code 0) | No |
| **`index.lock` present** (`.git/index.lock` present) | `run_remote_share.py:22` removes `.git/index.lock` before git operations. | Succeeded (code 0) | No |
| **Origin unreachable** (invalid remote URL `/nonexistent/origin.git`) | `git fetch` reports error; caught by `run_remote_share.py:26` (`fetch failed (network?); continuing with the local copy`). Solves proceed locally; push failure caught at `remote_run.py:115` (`PUSH FAILED... results stay in unit_cell_campaign/results and are pushed with the next case`). | Continued locally (code 0) | No |
| **`analysis/scripts` missing** (`analysis/scripts` removed) | `remote_run.py:221` checks `os.path.isdir(SC)`: logs `analysis/scripts not found in the repository; skipping the analysis stage` and returns `False`. | Skipped stage, exited 1 | No |
| **Matplotlib missing** (simulated via `PYTHONPATH` wrapper raising `ImportError`) | `fig_campaign.py` fails with rc 1; caught at `remote_run.py:241`: logs `analysis: fig_campaign.py failed (rc 1; matplotlib missing?); figures skipped, see analysis/analysis_fig_campaign.log`. Tables, manifest, and push continue. | Figures skipped, analysis pushed (code 0) | No |
| **Unpackable tarball** (dummy corrupted `L015.tar.gz`) | Caught at `remote_run.py:228`: logs `could not unpack L015.tar.gz: file could not be opened successfully: ReadError('not a gzip file')`. Skipping corrupted file; proceeds with all other tarballs. | Skipped corrupted case, completed stage (code 0) | No |
| **Case tarball without `posthoc_zoneT.json`** (`C001` stripped of `posthoc_zoneT.json`) | `post_campaign.py` records `Nu = NaN` and `Nu_field = NaN`. When `refit_closures.py` runs, `scipy.optimize.curve_fit` raises `ValueError: array must not contain infs or NaNs`. Caught at `remote_run.py:242`; halts analysis pipeline with exit code 1. | Stopped with error (code 1) | No |

---

### 3. Detailed Codebase Audit

1. **`unit_cell_campaign/remote_run.py`**:
   - Environment detection (§0) correctly probes `chtMultiRegionSimpleFoam` in PATH, `OPENFOAM_BASHRC`, and standard system directories (`/usr/lib/openfoam/openfoam2406`, `/opt/openfoam2406`).
   - Decompositions strictly locked to 8 MPI ranks per case (`decomposeParDict: numberOfSubdomains 8`).
   - Convergence watchdog (`converge_watchdog.py`) enforces $U, p_{rgh} < 10^{-5}$ and $h < 10^{-6}$ after $\ge 1200$ iterations; envelope watchdog stops cases exceeding $T_{\mathrm{wall,max}} > 70\,^\circ\text{C}$ at $\ge 4000$ iterations (`ENVELOPE_STOP`).
   - Duplicate protection (`other_hosts_result()` lines 76–85) safeguards existing tarballs if two machines solve the same case, routing the duplicate to `results_duplicate/`.
   - `analyse()` (§5) unpacks tarballs cleanly (with `..` path-traversal guards), sets unified environment variables (`ANALYSIS_DIR`, `CASES_DIR`, `UNIT_CELL_DIR`, `POST_OUT`), runs the 7 scripts sequentially, and updates `MANIFEST_sha256.txt`.

2. **`analysis/scripts/`**:
   - `refit_closures.py`: Eq. 23 bypass fit ($\Phi = 1/[1 + C_1 ((1-\mathrm{OR})/(\mathrm{OR}+\varepsilon))^m (\mathrm{Re}/100)^n]$) and Eq. 24 composite Nusselt fit ($\mathrm{Nu} = [\mathrm{Nu}_{\mathrm{fd}}^3 + (C_2 \mathrm{Gz}^p)^3]^{1/3}$ with fixed Shah-London $\mathrm{Nu}_{\mathrm{fd}} = 7.85$) are correctly fitted strictly on envelope-accepted calibration cases. Resistance network properly accounts for fin efficiency $\eta_{\mathrm{fin}} = \tanh(mL)/mL$, surface efficiency $\eta_o = 1 - (A_{\mathrm{fin}}/A_{\mathrm{wetted}})(1-\eta_{\mathrm{fin}})$, and caloric rise using $\Phi_{\mathrm{eff}}$. Holdouts are strictly out-of-sample evaluations. `--selftest` passed with full recovery.
   - `solve_eq22.py`: Constrained design optimization strictly isolates the sealed baseline to `partitions.str.contains("calibration")` (lines 22–27), avoiding conflicts with the fixed-fin sweep sealed case `F001`. `--selftest` passed.
   - `sealed_dp_check.py`: Correctly calculates Shah-London aspect ratio $\alpha = s/H_{\mathrm{fin}}$ friction factor polynomial against OpenFOAM static pressure drop.

3. **`post_campaign.py` & Support Tools**:
   - Computes static pressure drop $p_{\mathrm{in}} - p_{\mathrm{out}}$ using areaAverage `p_rgh`.
   - Length-averaged Nusselt number (v2) correctly derives from 5 streamwise interface bins ($q''_{\mathrm{mean}} / \Delta T_{\mathrm{mean}}$). At $\mathrm{OR} = 1.0$ (no fin channel), `Nu` is NaN by construction and all $\mathrm{OR} = 1.0$ cases are rejected by the validity envelope ($T_{\mathrm{wall}} > 70\,^\circ\text{C}$).
   - Stationarity check over 500-iteration window ($0.5\%$ tolerance), mass split ($0.5\%$), and energy balance ($0.5\%$) closures verified.
   - `select_continuations.py` correctly targets cases capped short of residuals or stopped prior to 1200 iterations.
   - `make_manifest.py` verifies SHA-256 digests of all dictionaries and 0/ fields, with $10^{-9}$ floating-point equivalence tolerance for cross-machine runtime differences.

4. **`run_remote_share.py`**:
   - Self-updates cleanly when repository copy differs.
   - Automatically fixes older sparse-checkout layouts by adding `analysis`, `/run_remote_share.py`, `/.gitignore`, `/README.md`.
   - Passes all arguments (`sys.argv[1:]`) through to `remote_run.py`.
   - Windows CRLF line endings in `run_remote_share.py` are transparently handled by Python on Linux and automatically replaced with LF on first self-update.

5. **README Documentation**:
   - Claims in `package/README.md`, `package/unit_cell_campaign/README.md`, and `package/analysis/README.md` match the implementation.

---

### Verdict Block

BLOCKING (would stop the hands-off run, lose or corrupt results, push a wrong analysis, or leave the workstation unable to pull the complete analysis): none
NON-BLOCKING:
1. `package/make_sandbox.sh:5,7,13`: Path resolution bug when invoked from the repository root as `bash package/make_sandbox.sh <dir>`. `HERE` resolves to `.../package`, causing line 7 `cp -r $HERE/package $D/seed` to fail with `cp: cannot stat '.../package/package': No such file or directory`. In addition, line 5 does not convert `$1` to an absolute path (`D=$(readlink -f "$1")`), breaking subsequent commands after line 7 `cd $D/seed`. (Affects only test sandbox generation; not executed by the production runner).
2. `.gitignore`: `unit_cell_campaign/cases_all/` is not listed in `.gitignore` (which only lists `cases/`, `cases_test/`, and `results_duplicate/`). After `run_remote_share.py --analyse` runs, `cases_all/` remains as an untracked directory in the clone's working tree. It is not staged by `push()` because `git add` specifies explicit paths, but adding it to `.gitignore` would ensure `git status` remains completely clean.
3. `analysis/MANIFEST_sha256.txt`: In `remote_run.py:246-252`, `os.walk(AN)` hashes all files under `analysis/`. When `campaign_results_summary.py` or `make_campaign_tables.py` imports `refit_closures.py` via `importlib`, Python generates `analysis/scripts/__pycache__/refit_closures.cpython-310.pyc`. This bytecode file is included in `MANIFEST_sha256.txt` but ignored by git (`.gitignore: *.py[cod]`), so it is not committed. Running `sha256sum -c MANIFEST_sha256.txt` on a freshly pulled clone on another machine warns that the `.pyc` file is missing.
4. `remote_run.py:255`: In `analyse()`, the fallback soft-reset replay command `git add -A analysis %s/results` omits `results_test` in the event of an upstream rebase collision during test mode.
NOT VERIFIABLE:
1. Full 87-case production solve (~80 CPU-hours) across all cases of `run_list_remote.txt` (prohibited by prompt instruction 3; the production startup sequence, environment check, build, manifest verification of all 87 cases, and case start were separately verified and documented in `package/prod_start_check.txt`).
2. Production SSH authentication to `git@github.com:azan84/IJHMT_CFP.git` (this machine exercised pushes to local bare repositories).
VERDICT: PASS
