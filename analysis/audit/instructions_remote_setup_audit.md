# Audit instructions: remote share of the unit-cell calibration campaign

You are the adversarial auditor (Gemini 3.7 Flash, by the operator's instruction) of the package in this
directory (`unit_cell_campaign/` of the repository IJHMT_CFP), which will be cloned on a second Linux machine
(OpenFOAM v2406 installed) to run 87 of the 177 cases of the calibration campaign of the IJHMT manuscript
"Dimensionless framework for bypass-controlled single-phase immersion cooling of server heat sinks". The other
90 cases run on the originating workstation with the same builder. You have no knowledge of how the package
was produced; check the files themselves. Read-only: create, modify or delete nothing.

The operator's instruction is that the errors met during the first day of the campaign must not recur. They were:
(1) the pressure solver (GAMG on p_rgh) stalled at its 1000-iteration inner limit in low-Reynolds cases, so each
SIMPLE step took eight times longer; (2) cases stopped at a 4000-iteration cap with residuals still falling;
(3) a case that met the residual stop at 676 iterations failed the 500-iteration stationarity test because the
window reached into the initial transient; (4) the Nusselt number was defined with a log-mean temperature
difference that is undefined at Re_ch <= 10 and with the cell-mixed bulk temperature, which carries the bypass
split; (5) monitor files of a restarted case were read in lexicographic instead of numeric time order; (6) an
empty face zone (no clearance at OR = 0, no channel at OR = 1) aborts `surfaceFieldValue`.

## Part A: set-up fidelity
1. `unit_cell.py` is the builder audited on the originating machine. Verify in its source that the fvSolution it
   writes carries `maxIter 200` on p_rgh (item 1), the controlDict `endTime 12000` (item 2), `runTimeModifiable true`,
   and that the topoSetDict it writes defines the face zones chanIn, clearIn, chanMid, clearMid with the z split
   at H_B + H_fin for the case; recompute H_fin(OR) = (44.45 - 4.5)(1 - OR) mm and the inlet velocity from
   Re_ch = u_ch D_h / nu(T_in) with u_ch = u_in (s/2 + t_f/2)/(s/2) for two cases of `campaign_design.json`
   (one FC-40, one EFL-1) and compare with what `build_cases.py` would produce (you may run
   `python3 build_cases.py <list> 1` into a temporary copy of this directory outside the repository, then
   `python3 make_manifest.py check manifest_local_build.json <list>`; OpenFOAM utilities that only build meshes
   are allowed, the solver is not).
2. `manifest_local_build.json`: confirm it covers all 177 case ids and that `make_manifest.py check` compares
   every dictionary and field file that matters (list any file that influences the solution but is not in
   FILES). State whether `endTime`, `stopAt` and `startFrom` are correctly excluded as volatile.
3. `run_list_remote.txt`: 87 ids; confirm none of them appears in the local share (the ids C001 to C090 are
   local) and that all appear in the design.

## Part B: runner logic (`remote_run.py`, `converge_watchdog.py`, `select_continuations.py`, `posthoc_zone_T.py`)
4. Watchdog: minimum 1200 iterations before a convergence stop (item 3); thresholds p_rgh, U < 1e-5, h < 1e-6;
   envelope stop at or after 4000 iterations when the maximum interface temperature exceeds 343.15 K; numeric
   ordering of time directories (item 5). Is the watchdog started with the right arguments by `remote_run.py`,
   and does a stop marker file get written in every branch?
5. Continuation: `select_continuations.py` continues cases that are short of the acceptance residuals
   (U, p_rgh < 1e-4; h < 1e-6) or stopped before 1200 iterations, inside the 70 C wall bound, and sets endTime
   12000; `remote_run.py` restarts them from the latest time (startFrom latestTime, decomposePar -latestTime),
   keeps the first-pass DONE and log, and reruns the zone extraction. Can a case be continued twice? Can a case
   that is still running be selected?
6. Post-hoc extraction: `posthoc_zone_T.py` adds chanOut/clearOut at x = L with the same z split as the case's
   own topoSetDict, skips zones of size 0 (item 6), reads T weighted by phi and the phi sum, orders time
   directories numerically, and is idempotent. Check the OR = 1 case (degenerate chanIn box) and the fixed-fin
   cases (H_fin = 20.9 mm, chassis height varies: does the top of the clearance box, 0.04545, still cover the
   domain when H_chassis differs from 44.45 mm? see F001 to F004 in the design).
7. Resources: how are physical cores, RAM and load detected; what does the prompt propose; can the run
   oversubscribe the machine; is 8 ranks per case fixed by `system/decomposeParDict` (numberOfSubdomains) and
   does `--ranks` other than 8 break decomposePar?
8. Results: what is packed, what is pushed, can two threads push at the same time, what happens if the push
   fails (network), and is the run resumable without re-solving finished cases? Does the importer on the
   originating machine overwrite a locally finished case?
9. OpenFOAM environment detection and the `--test` mode: does the test exercise every stage (build, verify,
   decompose, solve, reconstruct, extraction, pack)?

## Part C: documentation
10. `README.md`: every claim in it must match the scripts (settings table, requirements, commands, result
    contents). List any mismatch.

## Verdict
End your reply with exactly this block:
```
BLOCKING (would give a wrong or unusable result on the remote machine): numbered list or "none"
NON-BLOCKING: numbered list or "none"
NOT VERIFIABLE: numbered list or "none"
VERDICT: PASS | FAIL
```
FAIL if any blocking item stands.
