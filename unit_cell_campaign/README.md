# Unit-cell calibration campaign: remote share

Spanwise-periodic conjugate unit-cell cases (OpenFOAM v2406, `chtMultiRegionSimpleFoam`, forced convection,
temperature-dependent FC-40 and EFL-1 properties) for the calibration of the bypass framework of the IJHMT
manuscript "Dimensionless framework for bypass-controlled single-phase immersion cooling of server heat sinks".
The design (177 cases) is `campaign_design.json`; this directory carries the share listed in `run_list_remote.txt`
(87 cases: the OR = 1 and grid-study cases, the EFL-1, thermal-load, cross-combination and fixed-fin cases).
The remaining 90 cases run on the originating workstation.

## What is baked in (the corrections made during the first day of the campaign)

| Item | Setting | Where |
|---|---|---|
| Pressure solver | GAMG, relTol 0.01, at most 200 inner iterations (the low-Re cases stalled at the 1000 default) | `unit_cell.py` (fvSolution) |
| Iteration cap | 12,000 | `unit_cell.py` (controlDict) |
| Convergence stop | initial residuals p_rgh, U < 1e-5 and h < 1e-6 after at least 1200 iterations | `converge_watchdog.py`, called by `remote_run.py` |
| Envelope stop | at or after 4000 iterations when the maximum interface temperature exceeds 70 C (such a case cannot enter the dataset) | `converge_watchdog.py` |
| Continuation pass | cases short of the acceptance residuals (U, p_rgh < 1e-4; h < 1e-6) or stopped before 1200 iterations are continued from their latest time to 12,000 | `select_continuations.py`, `remote_run.py` |
| Post-hoc extraction (version 2) | six streamwise stations (channel and clearance mass flux and mass-flux-weighted temperature) and five interface bins (area, mean temperature, integrated wall heat flux recomputed from the fields through the solver's -postProcess mode); the length-averaged Nusselt number and the local bin values come from them; cases extracted with version 1 are refreshed at the next start | `posthoc_zone_T.py` |
| Build verification | every dictionary and field file of each built case is compared by SHA-256 with the audited local build before any solve; floating-point text (case_meta.json, property tables) may differ within 1e-9 relative between machines and is then reported as numeric-equivalent (`manifest_local_build.json`) | `make_manifest.py` |

## Requirements on the remote machine

- Linux, OpenFOAM v2406 (ESI; `chtMultiRegionSimpleFoam`, `blockMesh`, `splitMeshRegions`, `topoSet`, `decomposePar`,
  `reconstructPar`, `postProcess`), MPI (`mpirun`), Python 3.8+ (standard library only), git with push access to
  this repository (SSH key or token) so that results return automatically.
- About 0.1 GB RAM per MPI rank and about 30 MB of disk per case (the final fields stay on the remote machine;
  only monitors, logs and the zone extraction are pushed, about 1 MB per case).

## Run

One file: copy `run_remote_share.py` (repository root) to the machine and run

```bash
python3 run_remote_share.py --test    # clones the repository, builds the cases and runs the first one for 60 iterations on a copy
python3 run_remote_share.py           # asks how many cores to use, builds and verifies the 87 cases, runs them,
                                      # pushes results/<case>.tar.gz after every case, then the continuation pass
```

or by hand:

```bash
git clone git@github.com:azan84/IJHMT_CFP.git
cd IJHMT_CFP/unit_cell_campaign
python3 remote_run.py --test
python3 remote_run.py
```

Two machines may share the list: each checks the repository before every case and skips cases whose results
another machine has already pushed; run one of them with `--reverse` so that they meet in the middle.
`remote_run.py` detects physical cores, available RAM and the current load and proposes a default; each case uses
8 MPI ranks (fixed by the audited `decomposeParDict`), so the number of concurrent cases is cores / 8. On the originating 16-core workstation the
throughput optimum was three concurrent cases (1.5 ranks per physical core). Pass `--cores N` to skip the prompt,
`--no-push` to keep results local. The run is resumable: rerun the same command after an interruption.

## Results

After every case the runner also rewrites `results/ledger_<host>.csv` (one post-processed row per case finished on
that machine: bypass fractions, Nusselt number, thermal resistance, pressure drop, closures, acceptance),
`results/summary_<host>.md` (a table of the same, readable on GitHub) and a snapshot of its run log
`results/remote_run_<host>.log`, and pushes them with the case. `--test` works on a copy of the first case under
`cases_test/` and packs into `results_test/`, so a test never enters `results/`. The file `remote_run.log` at the
campaign root is a legacy of the first runner version and is kept tracked but no longer written.
`results/<case>.tar.gz` holds `postProcessing/` (all monitors), the solver, mesh and watchdog logs, `DONE`
(return code, wall time, iterations, host), the stop marker (`CONVERGED_STOP`, `ENVELOPE_STOP` or none = cap),
`posthoc_zoneT.json`, `case_meta.json` and the dictionaries as run. On the originating machine
`import_remote_results.py` unpacks them into the campaign directory for the dataset ledger (`post_campaign.py`).

## Provenance

`campaign_design.json` and `unit_cell.py` are the audited set-up (campaign set-up audit, round 2, 4 September 2026);
`manifest_local_build.json` lists the SHA-256 of every dictionary of the 177 locally built cases as they stand on the
originating machine; four local cases that had finished before the pressure-solver cap was added (C003, C004,
C005, C050) are recorded without `maxIter 200`, as run. A remote build that does not match the manifest is refused.
OpenFOAM is found through PATH, the `OPENFOAM_BASHRC` environment variable, or the usual install paths.
