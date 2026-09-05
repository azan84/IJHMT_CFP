# Audit instructions, round 3: launcher and runner before hand-over to the second machine

You are the sceptical auditor (Gemini 3.7 Flash through Antigravity, by the operator's instruction) of the package
in `package/` (a disposable copy of the repository's `unit_cell_campaign/` directory plus the one-file launcher
`run_remote_share.py`, the repository's `.gitignore` and `README.md`). It will be copied to a second Linux machine
(8 physical cores, OpenFOAM v2406 installed, git with an SSH key for the repository) whose clone of the repository is
in the broken state described below. The operator will copy `run_remote_share.py` there and run
`python3 run_remote_share.py --cores 16`. Nothing else will be done by hand. Your job: find every way this can go
wrong. Read-only on `package/`; write anything you need under a scratch directory of your own.

What went wrong before (all fixed, allegedly): round 1 (`round1_FAIL.md`) found the result push run from the wrong
directory, numpy undeclared, a hard-coded OpenFOAM path, a rank-count mismatch and a stale convergence marker; round
2 (`round2_PASS.md`) passed. Since then: (a) the runner version on the second machine tracked its own live run log
in git, so once a push failed (non-fast-forward), every later `git pull --rebase` failed and 20 cases of results
stayed unpushed; (b) two machines now share one list (`run_list_remote.txt`), one running it forward, the other
(`--reverse`) backward, each skipping cases whose `results/<case>.tar.gz` another machine has already pushed;
(c) the extraction is version 2 (streamwise stations and bins) and finished cases extracted with version 1 are
refreshed at start and after the list; (d) `post_campaign.py` writes a `stop_type` column; (e) per-machine ledger,
summary and log files under `results/`; (f) the launcher repairs the clone (aborts a stuck rebase, drops edits to the
legacy tracked log, commits and pushes pending result files, replays them on top of origin if a rebase cannot apply)
and replaces itself with the repository's copy when that is newer.

## Part A: exercise it
1. `bash make_sandbox.sh <your scratch dir>` builds a throwaway "origin" and a clone in the second machine's broken
   state (legacy log modified, one unpushed result commit, origin moved ahead). Run the launcher there exactly as the
   operator will (`python3 run_remote_share.py --test --test-push`; OpenFOAM is available on this machine, the test
   builds and solves one case for 60 iterations, about 30 s to 8 min depending on the machine load). Verify in the bare
   origin that `L015.tar.gz` and the test case's tarball arrived, that the clone's history is linear on top of origin,
   that the working tree is clean apart from ignored files, and that the launcher replaced itself with the repository
   copy (compare the files). Then run the same command a second time: it must be idempotent (skip the finished case,
   push nothing new or only the refreshed ledger).
2. Break it further in a second sandbox and run the launcher again: leave a rebase in progress (start a conflicting
   rebase and do not finish it), or put an `index.lock` file in `.git`, or make origin unreachable (point SSH= at a
   non-existent path). State what happens in each case and whether any result file can be lost.
3. Two machines: in a third sandbox, clone the origin twice (A and B), run `remote_run.py --test --test-push` in A
   and then in B for the same first case; then, with `--no-push` removed and `--test` removed, simulate the sharing
   logic without solving: read `done_elsewhere()` and `run_case()` and state under which sequence of events both
   machines solve the same case, and what the importer on the originating machine (`import_remote_results.py`) does
   with two tarballs of the same case.

## Part B: read it
4. `remote_run.py`: every git command (`push()`, `done_elsewhere()`, `git_repair()`); the per-host file names; what
   happens when `results/` does not exist yet; the continuation pass after the list on a machine that skipped most
   cases; `refresh_extraction()`; `running_ledger()` (it was accidentally deleted in one version and restored: check
   every name it uses is defined); the `--test` path; `check_env()` on a machine where OpenFOAM is only reachable
   through `OPENFOAM_BASHRC`; the environment passed to subprocesses.
5. `run_remote_share.py`: clone versus repair path, the HTTPS fallback, the git identity, the self-update loop guard,
   the exec of the runner with the operator's arguments; what if the operator's copy has Windows line endings.
6. `posthoc_zone_T.py` (version 2), `post_campaign.py` (`stop_type`, `POST_OUT`, the version-2 Nusselt definition and
   the fallbacks when a json is version 1), `select_continuations.py`, `converge_watchdog.py`, `make_manifest.py`
   (numeric-tolerant check), `build_cases.py`, `unit_cell.py` (`of_prefix`, the machine-independent EFL-1 fit):
   anything that differs between the two machines by construction, and anything that can silently produce a wrong
   number rather than an error.
7. `.gitignore` and `README.md`: do they match what the scripts do (which files are pushed, which stay local)?

## Verdict
End your reply with exactly this block:
```
BLOCKING (would lose results, stop the run, or produce a wrong number on the second machine): numbered list or "none"
NON-BLOCKING: numbered list or "none"
NOT VERIFIABLE: numbered list or "none"
VERDICT: PASS | FAIL
```

## Round 4 (after the round-3 FAIL)
Round 3 (`round3_FAIL.md`) found two blocking items and six non-blocking ones. Changes since: `--test` now works on a
copy of the first case under `cases_test/` and packs into `results_test/` (the audited case files and the manifest
check are untouched; a test never enters `results/`); `find_openfoam()` honours `OPENFOAM_BASHRC` first; `push()`
creates `results/` before the log snapshot; `make_manifest.py` treats `writeInterval` as volatile and the manifest
was regenerated; `post_campaign.py` re-extracts a case whose json is version 1 whatever its timestamp, and states
that Nu is undefined at OR = 1 by construction; the README describes the per-host files and `results_test/`; the
legacy tracked `remote_run.log` stays tracked on purpose (deleting it upstream would conflict with the second
machine's unpushed commits) and is documented. Re-check every round-3 item against `package/`, exercise Part A
items 1 and 2 again (`bash make_sandbox.sh <dir>`; use `--test --test-push` only), and give the verdict block.
IMPORTANT: do not start the production run (`python3 run_remote_share.py` without `--test`) in any sandbox: it builds
87 cases and solves them, which this machine cannot spare now; the production start was verified separately
(build, manifest check and first case start) and its log is in `prod_start_check.txt` here.
