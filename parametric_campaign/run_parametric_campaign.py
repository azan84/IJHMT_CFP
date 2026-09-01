#!/usr/bin/env python3
"""
Master Orchestrator for Immersion Cooling DOE Parametric Campaign.
Features:
- Automated Software & Environment Check (OpenFOAM v2406, mpirun, python3, git)
- Hardware Discovery (CPU threads, RAM) & Interactive Allocation
- Multi-fidelity Mesh Resolution (high: 1.1M, medium: 350k, fast: 85k cells)
- Resume & State-Preservation (Automatically skips completed cases upon restart)
- Parallel MPI Solver Execution & Dynamic blockMesh Parameterization
- Live Post-Processing (Bypass Fraction, Thermal Resistance, Pressure Drop, FOM)
- Automated 2D/3D Temperature and Streamline Contour Generation
- Safe GitHub Synchronization with Auto-Identity Configuration
"""

import os
import sys
import shutil
import subprocess
import json
import time
import argparse

CAMPAIGN_ROOT = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CAMPAIGN_ROOT, ".."))
SCRIPTS_DIR = os.path.join(CAMPAIGN_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from env_check import verify_environment, get_system_hardware
from mesh_generator import generate_blockmesh_dict
from postprocess_case import postprocess_case
from aggregate_results import aggregate_campaign_results
from git_sync import git_pull, git_push_results

def parse_args():
    parser = argparse.ArgumentParser(description="Immersion Cooling DOE Parametric Orchestrator")
    parser.add_argument("--non-interactive", "-y", action="store_true", help="Run in non-interactive batch mode with defaults")
    parser.add_argument("--threads", type=int, default=None, help="Number of CPU threads to allocate")
    parser.add_argument("--ram", type=float, default=None, help="Maximum RAM in GB to allocate")
    parser.add_argument("--mesh-res", type=str, choices=["high", "medium", "fast"], default="medium", help="Mesh resolution fidelity")
    parser.add_argument("--auto-push", action="store_true", default=True, help="Automatically push results to GitHub after each completed case")
    parser.add_argument("--force-rerun", action="store_true", default=False, help="Force rerun of already completed cases")
    parser.add_argument("--max-cases", type=int, default=None, help="Limit number of cases to run in this execution")
    parser.add_argument("--case-id", type=str, default=None, help="Run a single specific case by ID (e.g. DOE_Case_001)")
    return parser.parse_args()

def interactive_setup(hw, args):
    if args.non_interactive:
        threads = args.threads or hw["cpu_threads"]
        ram = args.ram or max(4.0, round(hw["total_ram_gb"] * 0.90, 1))
        mesh_res = args.mesh_res
        auto_push = args.auto_push
        return threads, ram, mesh_res, auto_push

    print("\n" + "=" * 70)
    print("      INTERACTIVE WORKSTATION RESOURCE ALLOCATION")
    print("=" * 70)
    print(f"[*] Detected Hardware Platform:")
    print(f"    - Available CPU Logical Cores / Threads: {hw['cpu_threads']}")
    print(f"    - Total Physical Memory (RAM):           {hw['total_ram_gb']} GB")
    print("-" * 70)

    # 1. CPU Allocation
    default_threads = hw["cpu_threads"]
    try:
        th_input = input(f"--> Enter CPU threads to allocate [1-{hw['cpu_threads']}, Default: {default_threads} (100%)]: ").strip()
        threads = int(th_input) if th_input else default_threads
        threads = max(1, min(hw["cpu_threads"], threads))
    except ValueError:
        threads = default_threads

    # 2. RAM Allocation
    default_ram = max(4.0, round(hw["total_ram_gb"] * 0.90, 1))
    try:
        ram_input = input(f"--> Enter RAM limit in GB [Default: {default_ram} GB]: ").strip()
        ram = float(ram_input) if ram_input else default_ram
        ram = max(2.0, min(hw["total_ram_gb"], ram))
    except ValueError:
        ram = default_ram

    # 3. Mesh Resolution Fidelity
    print("\n[*] Mesh Resolution Fidelity:")
    print("    [1] Medium Grid (~350k cells, ~1.5 min/case) [RECOMMENDED FOR 250 CASES]")
    print("    [2] High Grid   (~1.1M cells, ~6.0 min/case) [MAXIMUM RESOLUTION]")
    print("    [3] Fast Grid   (~85k cells,  ~15 sec/case)  [RAPID SCREENING]")
    res_input = input("--> Select Mesh Fidelity [1/2/3, Default: 1]: ").strip()
    res_map = {"1": "medium", "2": "high", "3": "fast"}
    mesh_res = res_map.get(res_input, "medium")

    # 4. GitHub Auto-Push
    push_input = input("--> Automatically push updated results to GitHub after each case? [Y/n, Default: Y]: ").strip().lower()
    auto_push = push_input != "n"

    print("-" * 70)
    print(f"[OK] Configuration Locked: {threads} Threads | {ram} GB RAM | Mesh: {mesh_res.upper()} | Auto-Push: {auto_push}")
    print("=" * 70 + "\n")
    return threads, ram, mesh_res, auto_push

def setup_case_directory(case_dir, case_meta, fluid_props, num_procs, mesh_res):
    template_dir = os.path.join(CAMPAIGN_ROOT, "template_case")
    shutil.rmtree(case_dir, ignore_errors=True)
    os.makedirs(case_dir, exist_ok=True)

    # Copy template folders
    for fldr in ["0", "constant", "system"]:
        shutil.copytree(os.path.join(template_dir, fldr), os.path.join(case_dir, fldr))

    # 1. Substitute 0/U
    u_in = case_meta["inlet_velocity_m_s"]
    with open(os.path.join(case_dir, "0", "U.template"), "r") as f:
        u_content = f.read().replace("__U_INLET__", f"{u_in:.6e}")
    with open(os.path.join(case_dir, "0", "U"), "w") as f:
        f.write(u_content)
    os.remove(os.path.join(case_dir, "0", "U.template"))

    # 2. Substitute 0/T
    t_in_k = case_meta["inlet_temp_C"] + 273.15
    q_flux = case_meta["tdp_per_chip_W"] / 0.0112 # Active patch area 80x140 mm
    with open(os.path.join(case_dir, "0", "T.template"), "r") as f:
        t_content = f.read().replace("__T_INLET_K__", f"{t_in_k:.2f}").replace("__HEAT_FLUX_W_M2__", f"{q_flux:.2f}")
    with open(os.path.join(case_dir, "0", "T"), "w") as f:
        f.write(t_content)
    os.remove(os.path.join(case_dir, "0", "T.template"))

    # 3. Substitute constant/transportProperties
    with open(os.path.join(case_dir, "constant", "transportProperties.template"), "r") as f:
        tp_content = f.read().replace("__NU__", f"{fluid_props['nu']:.6e}") \
                             .replace("__RHO__", f"{fluid_props['rho']:.1f}") \
                             .replace("__CP__", f"{fluid_props['cp']:.1f}") \
                             .replace("__K__", f"{fluid_props['k']:.4f}") \
                             .replace("__PR__", f"{fluid_props['Pr']:.2f}")
    with open(os.path.join(case_dir, "constant", "transportProperties"), "w") as f:
        f.write(tp_content)
    os.remove(os.path.join(case_dir, "constant", "transportProperties.template"))

    # 4. Generate blockMeshDict for Open Ratio & Topology
    generate_blockmesh_dict(case_dir, open_ratio=case_meta["open_ratio"], topology=case_meta["topology"], resolution=mesh_res)

    # 5. Substitute system/controlDict & decomposeParDict
    with open(os.path.join(case_dir, "system", "controlDict.template"), "r") as f:
        cd_content = f.read()
    with open(os.path.join(case_dir, "system", "controlDict"), "w") as f:
        f.write(cd_content)
    os.remove(os.path.join(case_dir, "system", "controlDict.template"))

    with open(os.path.join(case_dir, "system", "decomposeParDict.template"), "r") as f:
        dp_content = f.read().replace("__N_PROCS__", str(num_procs))
    with open(os.path.join(case_dir, "system", "decomposeParDict"), "w") as f:
        f.write(dp_content)
    os.remove(os.path.join(case_dir, "system", "decomposeParDict.template"))

def run_single_simulation(case_dir, case_meta, fluid_db, num_procs, mesh_res):
    cid = case_meta["case_id"]
    log_file = os.path.join(case_dir, "log.simpleFoam")

    # 1. Mesh generation
    subprocess.run(["blockMesh"], cwd=case_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["checkMesh"], cwd=case_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 2. Parallel decomposition & solve
    if num_procs > 1:
        subprocess.run(["decomposePar", "-force"], cwd=case_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        # Check mpirun arguments support
        mpi_cmd = f"mpirun -np {num_procs} simpleFoam -parallel > {log_file} 2>&1"
        try:
            subprocess.run(f"mpirun --use-hwthread-cpus -np {num_procs} simpleFoam -parallel > {log_file} 2>&1", shell=True, cwd=case_dir, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(mpi_cmd, shell=True, cwd=case_dir, check=True)
            
        subprocess.run(["reconstructPar", "-latestTime"], cwd=case_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        with open(log_file, "w") as lf:
            subprocess.run(["simpleFoam"], cwd=case_dir, stdout=lf, stderr=subprocess.STDOUT, check=True)

    # 3. Postprocess outputs
    res = postprocess_case(case_dir, case_meta, fluid_db)
    return res

def main():
    args = parse_args()

    # Step 1: Environment & software verification
    env = verify_environment(interactive=not args.non_interactive)
    if not env["ready"]:
        print("[FATAL] Environment audit failed. OpenFOAM is required to run simulations.")
        sys.exit(1)

    # Step 2: Interactive or automated hardware allocation
    hw = env["hardware"]
    threads, ram, mesh_res, auto_push = interactive_setup(hw, args)

    # Step 3: Pull latest from GitHub
    print("\n[*] Synchronizing with GitHub repository (azan84/IJHMT_CFP)...")
    git_pull(REPO_ROOT)

    # Step 4: Load DOE definition
    doe_file = os.path.join(CAMPAIGN_ROOT, "doe_definition.json")
    with open(doe_file, "r") as f:
        doe = json.load(f)

    cases_to_run = doe["cases"]
    if args.case_id:
        cases_to_run = [c for c in cases_to_run if c["case_id"] == args.case_id]
    if args.max_cases:
        cases_to_run = cases_to_run[:args.max_cases]

    total_cases = len(cases_to_run)
    fluid_db = doe["metadata"]["fluid_database"]

    cases_root = os.path.join(CAMPAIGN_ROOT, "cases")
    os.makedirs(cases_root, exist_ok=True)

    print("\n" + "=" * 70)
    print(f"      STARTING DOE PARAMETRIC CAMPAIGN ({total_cases} CASES)")
    print(f"      Threads: {threads} | Memory Limit: {ram} GB | Mesh: {mesh_res.upper()} | Auto-Push: {auto_push}")
    print("=" * 70)

    completed_cases = 0
    t_start_all = time.time()

    for idx, case_meta in enumerate(cases_to_run, 1):
        cid = case_meta["case_id"]
        group = case_meta["campaign_group"]
        fluid = case_meta["fluid"]
        or_val = case_meta["open_ratio"]
        re_val = case_meta["reynolds_number"]
        tdp = case_meta["tdp_per_chip_W"]
        case_dir = os.path.join(cases_root, cid)
        res_file = os.path.join(case_dir, "case_results.json")

        # RESUME CHECK: Skip already completed cases
        if os.path.exists(res_file) and not args.force_rerun:
            try:
                with open(res_file, "r") as rf:
                    cdata = json.load(rf)
                if cdata.get("status") == "COMPLETED_CONVERGED":
                    print(f"\n[Case {idx:03d}/{total_cases:03d}] {cid} already completed. SKIPPING.")
                    completed_cases += 1
                    continue
            except Exception:
                pass

        print(f"\n[Case {idx:03d}/{total_cases:03d}] Launching {cid} ({group}):")
        print(f"   * Fluid: {fluid} | Topology: {case_meta['topology']} | TDP: {tdp:.0f} W")
        print(f"   * Open Ratio: {or_val:.2f} | Reynolds Re_ch: {re_val} | Flow Rate: {case_meta['flow_rate_LPM']:.2f} LPM")

        t_start_case = time.time()
        setup_case_directory(case_dir, case_meta, fluid_db[fluid], num_procs=threads, mesh_res=mesh_res)
        
        try:
            res = run_single_simulation(case_dir, case_meta, fluid_db, num_procs=threads, mesh_res=mesh_res)
            t_elapsed = time.time() - t_start_case
            completed_cases += 1

            print(f"   [DONE in {t_elapsed:.1f}s] Output Metrics:")
            print(f"      - Bypass Fraction (Phi_bypass): {res['bypass_fraction_pct']:.1f}%")
            print(f"      - Thermal Resistance (R_th):    {res['thermal_resistance_K_W']:.4f} K/W")
            print(f"      - Peak Chip Temperature:        {res['T_chip_max_C']:.1f} °C")
            print(f"      - Chassis Pressure Drop:        {res['pressure_drop_total_Pa']:.1f} Pa")
            print(f"      - Figure of Merit (FOM):        {res['figure_of_merit_K_inv']:.1f} K^-1")

            # Update aggregated campaign database
            aggregate_campaign_results(CAMPAIGN_ROOT)

            # Auto-push to GitHub
            if auto_push:
                git_push_results(REPO_ROOT, completed_cases, total_cases)

        except Exception as e:
            print(f"   [ERROR] Failed solving {cid}: {e}")

    t_total_elapsed = time.time() - t_start_all
    print("\n" + "=" * 70)
    print(f"      CAMPAIGN FINISHED: {completed_cases}/{total_cases} CASES COMPLETED")
    print(f"      Total Execution Time: {t_total_elapsed/60.0:.2f} minutes")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
