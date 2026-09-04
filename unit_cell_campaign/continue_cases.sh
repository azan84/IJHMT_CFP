#!/bin/bash
# Continue capped cases (listed one directory per line) from their latest time to the endTime now in controlDict,
# N at a time, 8 ranks each, with the convergence/envelope watchdog. The first run's DONE file is kept as DONE_pass1
# and its log as log.chtMultiRegionSimpleFoam.pass1. Usage: continue_cases.sh <list_file> [concurrency]
source /usr/lib/openfoam/openfoam2406/etc/bashrc >/dev/null 2>&1 || true
LIST=$1; NPAR=${2:-3}; export ROOT=/mnt/e/ijhmt-cfp/Paper-5/cfd/unit_cell_campaign
cont_one() {
  C=$1; cd "$C" || return 1
  if [ -f DONE ] && [ ! -f CONTINUE ]; then echo "$(date +%T) skip $C (no CONTINUE marker)"; return 0; fi
  S=$(date +%s); N=1; while [ -f DONE_pass$N ]; do N=$((N+1)); done
  [ -f DONE ] && mv DONE DONE_pass$N; mv log.chtMultiRegionSimpleFoam log.chtMultiRegionSimpleFoam.pass$N 2>/dev/null; mv log.watchdog log.watchdog.pass$N 2>/dev/null
  for f in CONVERGED_STOP ENVELOPE_STOP; do [ -f $f ] && mv $f ${f}_pass$N; done   # a stale marker must not describe the new pass
  sed -i 's/^startFrom .*;/startFrom       latestTime;/' system/controlDict
  decomposePar -allRegions -force -latestTime -decomposeParDict system/decomposeParDict > log.decomposePar.pass$((N+1)) 2>&1 || { echo "$(date +%T) FAIL decompose $C"; return 1; }
  python3 $ROOT/converge_watchdog.py "$C" 1200 20 4000 > log.watchdog 2>&1 &
  WD=$!
  mpirun -np 8 chtMultiRegionSimpleFoam -parallel > log.chtMultiRegionSimpleFoam 2>&1; RC=$?
  kill $WD 2>/dev/null
  reconstructPar -allRegions -latestTime > log.reconstructPar.pass$((N+1)) 2>&1 && rm -rf processor*
  E=$(date +%s); echo "pass$((N+1)) rc=$RC wall_s=$((E-S)) iterations_this_pass=$(grep -c '^Time = ' log.chtMultiRegionSimpleFoam) end=$(date +%F_%T)" > DONE; rm -f CONTINUE
  echo "$(date +%T) continued $C $(cat DONE)"
}
export -f cont_one
cat "$LIST" | xargs -P "$NPAR" -I{} bash -c 'cont_one {}'
echo "CONTINUATION_LIST_COMPLETE $LIST $(date +%F_%T)"
