I have launched the extraction of all 133 case tarballs to verify the presence and SHA-256 checksums against `local/local_case_checksums.txt`. Waiting for completion.
I will wait for the task to finish.
I am waiting for the extraction and checksum verification task to complete.
Waiting for task-30 to finish.
I will wait for the reproducibility error analysis to finish.
# Upload Check Audit Report: Unit-Cell Campaign Public Repository

**Commit audited:** [`22a1674d967ab958a408e5d5245f017530a7549d`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone)  
**Author / Date:** azan84, Sat Sep 5 20:15:41 2026 +0800  
**Sparse-checkout directories in clone:** [`unit_cell_campaign/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign), [`analysis/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis), [`.gitignore`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/.gitignore), [`README.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/README.md), [`run_remote_share.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/run_remote_share.py)

---

## 1. Results (Case Tarballs vs. Local Case Checksums)

### Tarball Inventory
- Cases listed in [`local/finished_cases.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/local/finished_cases.txt): **133**
- Tarballs found in [`clone/unit_cell_campaign/results/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign/results): **43** (imported remote share)
- Tarballs found in [`clone/unit_cell_campaign/results_local/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign/results_local): **90** (workstation share)
- Total tarballs: **133**
- Missing cases: **0**
- Extra tarballs: **0**

### Checksum Verification against `local/local_case_checksums.txt`
All 133 tarballs were extracted into `scratch/extracted/` (11,432 files extracted across all archives). Comparing against the 7,623 SHA-256 entries in [`local/local_case_checksums.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/local/local_case_checksums.txt):

#### Missing Files in Tarballs: 82 files
The following 82 files exist locally in `local_case_checksums.txt` but are absent from the extracted tarballs:
1. **Case `C091` (23 files missing from `results/C091.tar.gz`):**
   - `C091/postProcessing/fluid/binQ_wallB0/0/surfaceFieldValue.dat` to `binQ_wallB4/0/surfaceFieldValue.dat` (5 files)
   - `C091/postProcessing/fluid/binT_wallB0/0/surfaceFieldValue.dat` to `binT_wallB4/0/surfaceFieldValue.dat` (5 files)
   - `C091/postProcessing/fluid/whf/0/wallHeatFlux.dat` (1 file)
   - `C091/postProcessing/fluid/zonePhi_clearX0/0/surfaceFieldValue.dat` to `zonePhi_clearX5/0/surfaceFieldValue.dat` (6 files)
   - `C091/postProcessing/fluid/zoneT_clearX0/0/surfaceFieldValue.dat` to `zoneT_clearX5/0/surfaceFieldValue.dat` (6 files)
2. **Case `C092` (23 files missing from `results/C092.tar.gz`):**
   - `C092/postProcessing/fluid/binQ_wallB0/0/surfaceFieldValue.dat` to `binQ_wallB4/0/surfaceFieldValue.dat` (5 files)
   - `C092/postProcessing/fluid/binT_wallB0/0/surfaceFieldValue.dat` to `binT_wallB4/0/surfaceFieldValue.dat` (5 files)
   - `C092/postProcessing/fluid/whf/0/wallHeatFlux.dat` (1 file)
   - `C092/postProcessing/fluid/zonePhi_clearX0/0/surfaceFieldValue.dat` to `zonePhi_clearX5/0/surfaceFieldValue.dat` (6 files)
   - `C092/postProcessing/fluid/zoneT_clearX0/0/surfaceFieldValue.dat` to `zoneT_clearX5/0/surfaceFieldValue.dat` (6 files)
3. **Case `X010` (36 files missing from `results/X010.tar.gz`):**
   - `X010/posthoc_zoneT.json` (absent from tarball)
   - `X010/postProcessing/fluid/binQ_wallB0..4/0/surfaceFieldValue.dat` (5 files)
   - `X010/postProcessing/fluid/binT_wallB0..4/0/surfaceFieldValue.dat` (5 files)
   - `X010/postProcessing/fluid/whf/0/wallHeatFlux.dat` (1 file)
   - `X010/postProcessing/fluid/zonePhi_chanX0..5/0/surfaceFieldValue.dat` (6 files)
   - `X010/postProcessing/fluid/zonePhi_clearX0..5/0/surfaceFieldValue.dat` (6 files)
   - `X010/postProcessing/fluid/zoneT_chanX0..5/0/surfaceFieldValue.dat` (6 files)
   - `X010/postProcessing/fluid/zoneT_clearX0..5/0/surfaceFieldValue.dat` (6 files)  
   *(Note: `X010.tar.gz` in clone contains `postProcessing` files under time directory `1875/` instead of `0/`, and they are 0-byte empty files because the case stopped at iteration 1875 due to temperature divergence).*

#### Differing Checksums in Tarballs: 2 files
- **`C091/posthoc_zoneT.json`:**
  - Local SHA-256: `95ea70ac93c518b378882ca86fc39f9ff2a7702578ff95f33db2d02e9e2598d7` (version 2 extraction)
  - Clone SHA-256: `664b7948855c43d31d7cb1f79884586ff37d1409be5fe3434e17026dca433a51` (stale version 1 extraction)
- **`C092/posthoc_zoneT.json`:**
  - Local SHA-256: `4609ed3cf00138977f91f115019069b07fffdec0490afcd1882c3d9b6e00031a` (version 2 extraction)
  - Clone SHA-256: `e791ff4ab297a355415adfad189bda67716bec37765bb62545c252b4a5c192f3` (stale version 1 extraction)

**Finding & Cause:** Cases `C091` and `C092` were solved on the remote machine and packaged with version-1 extraction (`zones: ["clearIn", "clearOut"]`). After being imported locally, `posthoc_zone_T.py` (version 2) was run on the workstation, producing the 23 station/bin files and updating `posthoc_zoneT.json` to version 2. However, the tarballs in the repository (`clone/unit_cell_campaign/results/C091.tar.gz` and `C092.tar.gz`) were never repacked with the local version-2 extractions.

---

## 2. Analysis Files vs. Local Originals

### Comparison of `clone/analysis/` (38 files)
- **Byte-identical to local originals:** **34 files**
  - Ledger: [`clone/analysis/dataset_ledger_unitcell.csv`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/dataset_ledger_unitcell.csv) == [`local/campaign/dataset_ledger_unitcell.csv`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/local/campaign/dataset_ledger_unitcell.csv) (`1edde21ca3871fb239eb5f6c60b0efec56de4c4c2e31bbfbeaf6ef3b7059064a`)
  - Analysis outputs: `refit_stats.csv`, `feasibility_map.csv`, `optimum.csv`, `campaign_results_summary.md`, `sealed_dp_check.csv` all match their originals in `local/audit/`.
  - Figures: 6 PNG figures in `clone/analysis/figures/` match `local/figures/`.
  - Scripts: `campaign_results_summary.py`, `fig_campaign.py`, `make_campaign_tables.py`, `refit_closures.py`, `sealed_dp_check.py`, `solve_eq22.py` in `clone/analysis/scripts/` match `local/figures_src/` or `local/audit_src/`.
  - Tables: 4 TeX tables in `clone/analysis/tables/` match `local/tables/`.
  - Audit logs: 10 audit files in `clone/analysis/audit/` match `local/audit/`.
- **Differing from local original:** **1 file**
  - [`clone/analysis/audit/decisions.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/audit/decisions.md) (`54d77728dc13daadb9aa09ecda60c019a1f8a6beec4ed9903e27b59fdaa5ddc9`)  
    != [`local/audit/decisions.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/local/audit/decisions.md) (`52b29ea029b13f7bb98faf42308dd7b9b8e5fa6bc8177157d63f5b0c6c5a3abe`)  
    *Diff:* `local/audit/decisions.md` has an 8-line Addendum added at 20:20 on 5 September 2026 documenting the import of L011, L013, L014, L017 and the 133-row ledger generation. This was not pushed to the repository.
- **Repository-only / No local original:** **3 files**
  - `clone/analysis/MANIFEST_sha256.txt` (manifest generated for repository verification)
  - `clone/analysis/README.md` (repository-level documentation of the analysis folder)
  - `clone/analysis/audit/instructions_remote_setup_audit_round3_4.md` (audit instruction file present in clone, absent from `local/audit/`)

### Verification of `clone/analysis/MANIFEST_sha256.txt`
`MANIFEST_sha256.txt` lists 182 files with their expected SHA-256 hashes:
- **176 files present and verified** with exact matching checksums.
- **6 files MISSING from the clone repository:**
  1. `analysis/figures/fig_dp_pump.pdf` (SHA-256: `89b002dd9bbf38ab05929da2621bf24af8cf5ae045821e42ea09a7d27513c649`)
  2. `analysis/figures/fig_parity.pdf` (SHA-256: `7c1affc1191ad37781d8bb343bce68970bebc95a31041c5e5d42e8daf1aa57ad`)
  3. `analysis/figures/fig_phi_bypass.pdf` (SHA-256: `9ac83da734c64c43406875962ac1641bd32823d7ecd952bb0808fd057999bb64`)
  4. `analysis/figures/fig_profiles.pdf` (SHA-256: `0dbca450b907e79d54512d887ce9bdf74786d3c786cc164e71dbbb1725f6cc2d`)
  5. `analysis/figures/fig_rth_or.pdf` (SHA-256: `5bbfbc4ada00e3cfbac4fe887a672e48ba50b9e39cfdd70a18d8d5d2e091e9ba`)
  6. `analysis/figures/fig_unit_cell.pdf` (SHA-256: `b150efbeec68d4aad5799e5b030772a21193bb8de4843ca72d57ab31da06603e`)

**Root Cause:** Line 2 of [`clone/.gitignore`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/.gitignore) contains `*.pdf`. Git ignored all PDF figures during `git add`, so despite existing in `local/figures/` and being checksummed into `MANIFEST_sha256.txt`, none of the 6 vector PDF figures were committed to the repository.

### Local Files NOT in Clone and Their Legitimacy
1. **`local/figures/` (8 files not in clone):**
   - 6 PDF figures (`fig_dp_pump.pdf`, `fig_parity.pdf`, `fig_phi_bypass.pdf`, `fig_profiles.pdf`, `fig_rth_or.pdf`, `fig_unit_cell.pdf`): **Carries campaign figure results.** Expected by `MANIFEST_sha256.txt`; excluded by `.gitignore`.
   - `fig_sastre_dp.pdf` & `fig_sastre_dp.png`: Pre-campaign CFD tip-clearance benchmark validation against Sastre et al. (2018), not part of the unit cell campaign. *Legitimately stays out.*
2. **`local/figures_src/` (2 files not in clone):**
   - `fig_unit_cell.py`: **Carries campaign analysis.** This script generates `fig_unit_cell.png` and `fig_unit_cell.pdf`. Its omission from `clone/analysis/scripts/` leaves `fig_unit_cell.png` without reproduction source in the repository.
   - `fig_sastre_dp.py`: Script for pre-campaign Sastre validation figure. *Legitimately stays out.*
3. **`local/campaign/` (17 files not in clone):**
   - `all_cases.txt`, `pilot_cases.txt`, `run_list_1.txt`, `run_list_2.txt`, `run_list_local.txt`, `run_list_continue.txt`, `run_list_continue3.txt`, `run_list_remote_abs.txt`, `build_all.py`, `run_campaign.sh`, `run_local_then_continue.sh`, `run_batch2_then_post.sh`, `continue_cases.sh`, `auto_sync.sh`, `converge_watchdog_v1.py`, `transient_check.py`, `rebuilt_after_audit.txt`, `pilot_results.csv`: Internal workstation execution manifests, shell orchestrators, and diagnostic logs. *Legitimately stays out.*
4. **`local/audit/` (78 files not in clone):**
   - Pre-campaign gate audit reports: `gate_0_codex*` through `gate_5_codex*` (rounds 1–5), `campaign_setup_audit.md`, `final_audit.md`, `open_defects.md`, `phase4_edit_plan.md`, `agy_review_*`, `auditor_change.md`, `verifier_*`, `superseded_files.md`, `e8_references.md`, `table1b_geometry_as_run.csv`, `upload_check_gemini.md`. *Legitimately stays out.*
   - Manuscript-level provenance ledgers: `provenance.csv`, `provenance_before_campaign_results.csv`, `provenance_frozen_text.csv`, `provenance_staging.csv`, `dataset_ledger.csv` (earlier 250-case isothermal sweep), `case_inventory.csv`, `consistency.csv`, `consistency_staging.csv`, `numeric_tokens*.csv`. *Legitimately stays out.*
   - Internal traces & selftests: `dp_trace.csv`, `dp_trace.md`, `rth_trace.md`, `re_recompute.csv`, `formula_reproduction.csv`, `checkMesh_summary.csv`, `feasibility_probe.md`, `feasibility_probe_residuals.csv`, `refit_stats_selftest.csv`, `optimum_selftest.csv`, `feasibility_map_selftest.csv`. *Legitimately stays out.*
5. **`local/audit_src/` (17 files not in clone):**
   - Manuscript audit verification scripts: `apply_verifier_disagreements.py`, `build_case_inventory.py`, `check_source_paths.py`, `checkmesh_summary.py`, `consistency_sweep.py`, `dataset_ledger.py`, `dp_trace.py`, `extract_numeric_tokens.py`, `foam_flux_split.py`, `formula_reproduction.py`, `physics_checks.py`, `provenance_pdf_check.py`, `provenance_quantity_relabel*.py`, `provenance_rules*.py`, `re_recompute.py`. *Legitimately stays out.*
6. **`local/tables/` (0 files not in clone):** All 4 tables are present in clone.

---

## 3. Consistency

- **Ledger vs Tarballs:** [`clone/analysis/dataset_ledger_unitcell.csv`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/dataset_ledger_unitcell.csv) has exactly **133** rows and 133 unique `case_id` values, corresponding 1-to-1 with the 133 tarballed cases (43 in `results/`, 90 in `results_local/`). 0 missing, 0 extra.
- **Summary Counts:** [`clone/unit_cell_campaign/results/summary_all.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/unit_cell_campaign/results/summary_all.md) reports:
  - Total: finished 133 of 177 | inside envelope 46 | converged 41 | accepted 41
  - Partitions:
    - `calibration`: 99 finished, 34 inside envelope, 34 converged, 34 accepted
    - `cross_combinations`: 14 finished, 5 inside envelope, 2 converged, 2 accepted
    - `fixed_fin_sweep`: 4 finished, 2 inside envelope, 2 converged, 2 accepted
    - `holdout_EFL-1`: 5 finished, 1 inside envelope, 0 converged, 0 accepted
    - `holdout_thermal_load`: 13 finished, 5 inside envelope, 3 converged, 3 accepted
  - Full 99-case calibration acceptance map ($11 \times 9$) matches the ledger flags exactly.
- **README Documentation:**
  - [`clone/README.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/README.md) and [`clone/analysis/README.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/README.md) accurately describe the 133 rows, the split between 90 local cases and 43 remote cases, the pause status (44 cases unrun on common list, 3 cross-combination cases awaiting continuation pass), and the deliberate absence of large volume field files (~10 MB/case).
  - Discrepancy: `clone/analysis/README.md` states that `MANIFEST_sha256.txt` lists the SHA-256 of every file under `analysis/` and `results/`, but 6 PDF files listed in that manifest are missing from `clone/analysis/figures/`.

---

## 4. Reproducibility

### Test of `refit_closures.py`
Running:
```bash
python3 clone/analysis/scripts/refit_closures.py \
  --ledger clone/analysis/dataset_ledger_unitcell.csv \
  --out scratch/refit.csv
```
- **Exit status:** 0 (success).
- **Comparison:**
  - The `calibration` row in `scratch/refit.csv` matches `clone/analysis/refit_stats.csv` **to full machine precision across every parameter and metric** ($C_1 = 0.2365466550186977$, $m = 1.3580465641242803$, $n = 0.4439926592074118$, $C_2 = 0.8751010063577392$, $p = 0.46505606026960405$, $R_{\mathrm{fixed}} = 0.0077661060173028025$, $R^2 = 0.9137$, etc.).
  - `clone/analysis/refit_stats.csv` has only the `calibration` row, whereas `scratch/refit.csv` outputs 4 rows (`calibration`, `cross_combinations`, `fixed_fin_sweep`, `holdout_thermal_load`). This is consistent with `clone/analysis/README.md` which notes that holdout statistics were held back until the full campaign resumes.

### Failures when Regenerating from Clone Alone
Every script under [`clone/analysis/scripts/`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts) fails when invoked from the repository root with default arguments:
1. **Broken Default Paths in All Scripts:**
   - [`campaign_results_summary.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/campaign_results_summary.py), [`fig_campaign.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/fig_campaign.py), and [`make_campaign_tables.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/make_campaign_tables.py) look for `ROOT/cfd/unit_cell_campaign/dataset_ledger_unitcell.csv`. In the clone, the path is `ROOT/analysis/dataset_ledger_unitcell.csv`.
   - [`refit_closures.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/refit_closures.py) and [`solve_eq22.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/solve_eq22.py) default `--ledger` to `ROOT/audit/dataset_ledger.csv`, which does not exist in the clone.
   - [`fig_campaign.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/fig_campaign.py), [`make_campaign_tables.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/make_campaign_tables.py), and [`campaign_results_summary.py`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/upload_check/clone/analysis/scripts/campaign_results_summary.py) hardcode internal import `ROOT/figures/src/refit_closures.py`, output directories `ROOT/figures/` and `ROOT/manuscript/tables/`, and input paths `ROOT/audit/refit_stats.csv`, none of which exist in the clone.
2. **`solve_eq22.py` Duplicate Sealed Row Block:**
   Running `solve_eq22.py` against `clone/analysis/dataset_ledger_unitcell.csv` fails with:
   `BLOCKED: more than one sealed row for Re_label [40]` (exit code 2).  
   Because both `C005` (`calibration`) and `F001` (`fixed_fin_sweep`) have $\mathrm{OR} = 0.0$ and $\mathrm{Re} = 40$ with `fluid=FC-40, Plate-Fin, 700 W`, and `solve_eq22.py` does not filter by partition, it detects duplicate sealed baseline references and refuses to run.
3. **`sealed_dp_check.py` Case Tarball Path Error:**
   Requires unpacked case directories at `cases/<case_id>/case_meta.json` and module `unit_cell.py` under `cfd/unit_cell_campaign`. In the repository, case metadata is packed inside `<case_id>.tar.gz` and the campaign directory is `unit_cell_campaign/`.
4. **Missing Figure Generation Script:**
   `fig_unit_cell.png` exists in `clone/analysis/figures/`, but its generator `fig_unit_cell.py` was not committed to `clone/analysis/scripts/`.

---

```
MISSING OR DIFFERENT (results or analysis that exist locally but are not, or not identically, in the repository):
1. 82 post-processing and extraction files for cases C091, C092, and X010 present locally in local/local_case_checksums.txt are missing from clone/unit_cell_campaign/results/C091.tar.gz (23 files: binQ_wallB0..4, binT_wallB0..4, whf, zonePhi_clearX0..5, zoneT_clearX0..5), C092.tar.gz (23 files: identical set to C091), and X010.tar.gz (36 files: posthoc_zoneT.json and 35 monitor/flux dat files at time 0).
2. Two zone extraction json files differ between local and clone: C091/posthoc_zoneT.json (local SHA-256 95ea70ac... vs clone 664b7948...) and C092/posthoc_zoneT.json (local SHA-256 4609ed3c... vs clone e791ff4a...). Clone contains stale version-1 extractions; local contains version-2 multi-station extractions.
3. Six vector PDF figures present in local/figures/ and listed in clone/analysis/MANIFEST_sha256.txt are absent from clone/analysis/figures/ due to *.pdf in clone/.gitignore: fig_dp_pump.pdf (SHA-256 89b002dd...), fig_parity.pdf (SHA-256 7c1affc1...), fig_phi_bypass.pdf (SHA-256 9ac83da7...), fig_profiles.pdf (SHA-256 0dbca450...), fig_rth_or.pdf (SHA-256 5bbfbc4a...), and fig_unit_cell.pdf (SHA-256 b150efbe...).
4. Script local/figures_src/fig_unit_cell.py, which generates fig_unit_cell.png and fig_unit_cell.pdf, is present locally but absent from clone/analysis/scripts/.
5. local/audit/decisions.md differs from clone/analysis/audit/decisions.md (local SHA-256 52b29ea0... vs clone 54d77728...): the local copy contains an 8-line addendum dated 5 September 2026, 20:20 documenting the import of cases L011, L013, L014, and L017 and the 133-row ledger push.
NON-BLOCKING:
1. Script execution paths in clone/analysis/scripts/ (fig_campaign.py, make_campaign_tables.py, campaign_results_summary.py, sealed_dp_check.py, solve_eq22.py, refit_closures.py) reference internal project directories (cfd/unit_cell_campaign/, audit/, figures/src/, manuscript/tables/) rather than analysis/ or results tarballs.
2. solve_eq22.py blocks on the 133-row ledger because case F001 introduces a second sealed case at Re 40; it succeeds only when filtered to the calibration partition.
3. clone/analysis/audit/instructions_remote_setup_audit_round3_4.md exists in the clone but is absent from local/audit/.
NOT VERIFIABLE: none
VERDICT: INCOMPLETE
```
