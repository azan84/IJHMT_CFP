I have launched the extraction of all 133 case tarballs to verify the presence and SHA-256 checksums against `local/local_case_checksums.txt`. Waiting for completion.
I will wait for the task to finish.
I have launched the reproducibility test in the mock environment to verify the script outputs against the repository's tables and figures. Waiting for completion.
I have started the mock reproduction test to verify that the scripts produce the repository's tables, figures, and summary when run against the data. Waiting for the task to finish.
# Upload Check Audit Report (Round 2): Unit-Cell Campaign Public Repository

**Commit Audited:** [`544e675c3dfe69b4075d9c5bf201a4622b1d9537`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone)  
**Author / Date:** azan84, Sat Sep 5 21:16:12 2026 +0800  
**Repository State:** Sparse-checkout containing [`unit_cell_campaign/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign), [`analysis/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis), [`.gitignore`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/.gitignore), [`README.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/README.md), and [`run_remote_share.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/run_remote_share.py).

---

## 1. Results: Case Tarballs vs. Local Case Checksums

### Tarball Inventory
- Cases listed in [`local/finished_cases.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/local/finished_cases.txt): **133** (90 solved on the workstation, 43 imported from the remote share).
- Tarballs in [`clone/unit_cell_campaign/results/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign/results): **43**
- Tarballs in [`clone/unit_cell_campaign/results_local/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign/results_local): **90**
- Total tarballs: **133** (0 missing, 0 extra).

### Extraction & SHA-256 Verification
All 133 archives were unpacked into `scratch/extracted/` (11,432 files total). Each extracted monitor file, JSON extraction, `DONE` marker, solver stop marker, and `case_meta.json` was verified against [`local/local_case_checksums.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/local/local_case_checksums.txt):
- **Entries in `local/local_case_checksums.txt`:** 7,541
- **Exact matching files:** **7,541**
- **Missing files:** **0**
- **Differing files:** **0**

### Verification of Round-1 Findings:
- **`C091` & `C092`:** The local cases were restored to their tarball state (`posthoc_zoneT.json` SHA-256 hashes `664b7948...` and `e791ff4a...` match the clone tarballs exactly; multi-station post-processing files that had been locally generated without field data were removed).
- **`X010`:** Restored to its tarball state (20 files present at time `0/`, all matching SHA-256).

---

## 2. Analysis: Files in `clone/analysis/` vs. Local Originals

### Byte-Identity Check
Every file under [`clone/analysis/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis) was compared against its original in `local/`:
- **Total files in `clone/analysis/`:** 46
- **Byte-identical to local original:** **44 files**
  - Ledger: [`dataset_ledger_unitcell.csv`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/dataset_ledger_unitcell.csv) == [`local/campaign/dataset_ledger_unitcell.csv`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/local/campaign/dataset_ledger_unitcell.csv)
  - Analysis results: `refit_stats.csv`, `feasibility_map.csv`, `optimum.csv`, `campaign_results_summary.md`, `sealed_dp_check.csv` all match their counterparts in `local/audit/`.
  - Figures (12 files): All 6 PNG figures and all 6 PDF figures in `clone/analysis/figures/` (`fig_dp_pump`, `fig_parity`, `fig_phi_bypass`, `fig_profiles`, `fig_rth_or`, `fig_unit_cell`) match `local/figures/`.
  - Scripts (7 files): `campaign_results_summary.py`, `fig_campaign.py`, `fig_unit_cell.py`, `make_campaign_tables.py`, `refit_closures.py`, `sealed_dp_check.py`, `solve_eq22.py` match `local/figures_src/` or `local/audit_src/`.
  - Tables (4 files): `tab_calibration_ledger.tex`, `tab_campaign_counts.tex`, `tab_coefficients.tex`, `tab_statistics.tex` match `local/tables/`.
  - Audit trail (15 files): All 15 audit logs and instruction files match `local/audit/`, including `upload_check_gemini_round1.md` (which is byte-identical to `local/audit/upload_check_gemini.md`) and `decisions.md` (which includes the 8-line addendum).
- **Differing from local original:** **0 files**
- **Repository-only files:** **2 files** (`clone/analysis/README.md` and `clone/analysis/MANIFEST_sha256.txt`).

### Check of `clone/analysis/MANIFEST_sha256.txt`
- Lists 184 files (138 under `unit_cell_campaign/`, 46 under `analysis/`).
- **183 files present and verified** with matching SHA-256.
- **0 missing files.** (The 6 vector PDFs un-ignored in commit `544e675` now pass).
- The single mismatch is `analysis/MANIFEST_sha256.txt` itself, which contains the 0-byte dummy hash `e3b0c442...` (self-referential placeholder).

### Audit of Local Files NOT in Clone
1. **`local/figures/` (2 files not in clone):**
   - `fig_sastre_dp.pdf` & `fig_sastre_dp.png`: Pre-campaign CFD tip-clearance benchmark validation against Sastre et al. (2018), not part of the unit cell campaign. *Legitimately stays out.*
2. **`local/figures_src/` (1 file not in clone):**
   - `fig_sastre_dp.py`: Generator script for the pre-campaign Sastre figure. *Legitimately stays out.*
3. **`local/campaign/` (17 files not in clone):**
   - Orchestration shell scripts (`run_campaign.sh`, `run_local_then_continue.sh`, `auto_sync.sh`, etc.), case builders (`build_all.py`), transient diagnostics (`transient_check.py`, `converge_watchdog_v1.py`), and raw run manifests (`run_list_*.txt`). *Legitimately stays out.*
4. **`local/audit/` (78 files not in clone):**
   - Pre-campaign gate review reports (`gate_0_codex*` through `gate_5_codex*`, `agy_review_*`, `verifier_*`, `open_defects.md`). *Legitimately stays out.*
   - Manuscript token provenance tracking ledgers (`provenance*.csv`, `numeric_tokens*.csv`, `consistency*.csv`, 250-case isothermal `dataset_ledger.csv`). *Legitimately stays out.*
   - Internal selftests and verification traces (`dp_trace.*`, `rth_trace.md`, `checkMesh_summary.csv`, `*_selftest.csv`). *Legitimately stays out.*
5. **`local/audit_src/` (17 files not in clone):**
   - Manuscript audit scripts (`provenance_rules*.py`, `check_source_paths.py`, `consistency_sweep.py`, etc.). *Legitimately stays out.*
6. **`local/tables/` (0 files not in clone):** All 4 tables are present in clone.

---

## 3. Consistency

- **Ledger vs Tarballs:** [`clone/analysis/dataset_ledger_unitcell.csv`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/dataset_ledger_unitcell.csv) has exactly 133 rows and 133 unique `case_id` values, corresponding 1-to-1 with the 133 tarballed cases in `results/` (43) and `results_local/` (90).
- **Summary Counts:** [`clone/unit_cell_campaign/results/summary_all.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign/results/summary_all.md) matches the ledger across every partition:
  - **Total:** 133 finished | 46 inside envelope | 41 converged | 41 accepted
  - **Calibration:** 99 finished | 34 inside envelope | 34 converged | 34 accepted
  - **Cross-combinations:** 14 finished | 5 inside envelope | 2 converged | 2 accepted
  - **Fixed-fin sweep:** 4 finished | 2 inside envelope | 2 converged | 2 accepted
  - **Holdout EFL-1:** 5 finished | 1 inside envelope | 0 converged | 0 accepted
  - **Holdout thermal load:** 13 finished | 5 inside envelope | 3 converged | 3 accepted
- **README Documentation:** [`clone/README.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/README.md) and [`clone/analysis/README.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/README.md) accurately describe the 133 finished cases, the split between 90 local and 43 remote cases, the deliberate exclusion of ~10 MB/case 3D volume fields, the reason why holdout statistics were held back, and the command-line flags required by scripts when run outside the originating project hierarchy.

---

## 4. Reproducibility

### Closure Refit Reproduction
Running:
```bash
python3 clone/analysis/scripts/refit_closures.py \
  --ledger clone/analysis/dataset_ledger_unitcell.csv \
  --out scratch/refit.csv
```
Exits with status 0. The calibration partition row reproduces `clone/analysis/refit_stats.csv` **identically to full floating-point precision** across all parameters ($C_1 = 0.2365466550186977$, $m = 1.3580465641242803$, $n = 0.4439926592074118$, $C_2 = 0.8751010063577392$, $p = 0.46505606026960405$, $R_{\mathrm{fixed}} = 0.0077661060173028025$, $R^2 = 0.9137$).

### Constrained Optimization Reproduction
Running:
```bash
python3 clone/analysis/scripts/solve_eq22.py \
  --ledger clone/analysis/dataset_ledger_unitcell.csv \
  --out scratch/optimum.csv \
  --map-out scratch/feasibility_map.csv
```
Exits with status 0. The script now filters the sealed baseline using the calibration partition and ignores off-grid Reynolds numbers without aborting. `scratch/optimum.csv` and `scratch/feasibility_map.csv` are **byte- and value-identical** to `clone/analysis/optimum.csv` and `clone/analysis/feasibility_map.csv`.

### Figure and Table Scripts
- In their default invocations without flags, `fig_campaign.py`, `fig_unit_cell.py`, `make_campaign_tables.py`, `campaign_results_summary.py`, and `sealed_dp_check.py` expect paths relative to the originating project structure (`figures/`, `audit/`, `cfd/unit_cell_campaign/`, `manuscript/tables/`). This behavior is documented in [`clone/analysis/README.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/README.md#L25-L30).
- When mapped or executed against those paths, all figure, table, and summary scripts run to completion and regenerate the figures, tables, and numerical summaries.

---

```
MISSING OR DIFFERENT (results or analysis that exist locally but are not, or not identically, in the repository): none
NON-BLOCKING:
1. Script execution paths in clone/analysis/scripts/ (fig_campaign.py, fig_unit_cell.py, make_campaign_tables.py, campaign_results_summary.py, sealed_dp_check.py) default to the originating project tree directory layout (cfd/unit_cell_campaign/, audit/, figures/, manuscript/tables/) rather than the sparse-checkout repository layout; command-line flags or path mapping are required as documented in clone/analysis/README.md.
2. clone/analysis/MANIFEST_sha256.txt lists an empty file hash (e3b0c442...) for its own entry analysis/MANIFEST_sha256.txt.
NOT VERIFIABLE: none
VERDICT: COMPLETE
```
