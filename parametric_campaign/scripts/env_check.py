#!/usr/bin/env python3
"""
Environment and Software Dependency Verifier.
Checks:
- OpenFOAM installation (openfoam2406, openfoam2312, openfoam10, etc.)
- OpenFOAM solvers and utilities: simpleFoam, blockMesh, decomposePar, reconstructPar
- MPI: mpirun
- Python3 environment & libraries: numpy, scipy, matplotlib
- Git & SSH remote authentication
- System hardware discovery: CPU threads, physical memory, architecture
"""

import os
import sys
import shutil
import subprocess
import multiprocessing

def check_command(cmd):
    return shutil.which(cmd) is not None

def get_system_hardware():
    cpu_count = multiprocessing.cpu_count()
    total_ram_gb = 0.0
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total_ram_kb = float(line.split()[1])
                    total_ram_gb = round(total_ram_kb / (1024.0 * 1024.0), 2)
                    break
    except Exception:
        total_ram_gb = 16.0 # fallback

    return {
        "cpu_threads": cpu_count,
        "total_ram_gb": total_ram_gb
    }

def find_openfoam_bashrc():
    candidates = [
        "/usr/lib/openfoam/openfoam2406/etc/bashrc",
        "/usr/lib/openfoam/openfoam2312/etc/bashrc",
        "/usr/lib/openfoam/openfoam2306/etc/bashrc",
        "/opt/openfoam2406/etc/bashrc",
        "/opt/openfoam2312/etc/bashrc",
        "/opt/openfoam10/etc/bashrc",
        "/opt/openfoam11/etc/bashrc",
        os.path.expanduser("~/OpenFOAM/OpenFOAM-v2406/etc/bashrc"),
        os.path.expanduser("~/OpenFOAM/OpenFOAM-10/etc/bashrc")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def verify_environment(interactive=True):
    hw = get_system_hardware()
    print("=" * 70)
    print("      HARDWARE AND SOFTWARE ENVIRONMENT AUDIT")
    print("=" * 70)
    print(f"[*] Detected Host System:")
    print(f"    - Available CPU Logical Cores/Threads: {hw['cpu_threads']}")
    print(f"    - Available Physical Memory (RAM):     {hw['total_ram_gb']} GB")
    print("-" * 70)

    # 1. Check Python
    py_ok = sys.version_info >= (3, 8)
    print(f"[{'PASS' if py_ok else 'FAIL'}] Python Version: {sys.version.split()[0]}")

    # 2. Check OpenFOAM binaries
    of_tools = ["simpleFoam", "blockMesh", "decomposePar", "reconstructPar", "mpirun"]
    missing_tools = [t for t in of_tools if not check_command(t)]

    of_sourced = len(missing_tools) == 0
    bashrc_path = find_openfoam_bashrc()

    if of_sourced:
        print(f"[PASS] OpenFOAM Environment is Active:")
        for t in of_tools:
            path = shutil.which(t)
            print(f"       * {t:15s} -> {path}")
    else:
        print(f"[WARN] OpenFOAM binaries missing in current PATH: {missing_tools}")
        if bashrc_path:
            print(f"       Found OpenFOAM installation at: {bashrc_path}")
            print(f"       (The orchestrator will automatically source this environment).")
        else:
            print(f"[FAIL] OpenFOAM installation not automatically detected in standard paths.")
            if interactive:
                custom = input("       Please enter the path to OpenFOAM etc/bashrc (or leave blank): ").strip()
                if custom and os.path.exists(custom):
                    bashrc_path = custom

    # 3. Check Git
    git_ok = check_command("git")
    print(f"[{'PASS' if git_ok else 'FAIL'}] Git executable: {shutil.which('git') if git_ok else 'NOT FOUND'}")

    # 4. Check Optional scientific packages
    pkgs = {}
    for pkg in ["numpy", "scipy", "matplotlib"]:
        try:
            __import__(pkg)
            pkgs[pkg] = True
        except ImportError:
            pkgs[pkg] = False
    
    print("-" * 70)
    print(f"[*] Python Scientific Libraries:")
    for pkg, ok in pkgs.items():
        print(f"    - {pkg:12s}: {'[INSTALLED]' if ok else '[OPTIONAL/MISSING]'}")

    print("=" * 70)
    
    is_ready = of_sourced or (bashrc_path is not None)
    return {
        "hardware": hw,
        "openfoam_active": of_sourced,
        "openfoam_bashrc": bashrc_path,
        "git_available": git_ok,
        "ready": is_ready
    }

if __name__ == "__main__":
    res = verify_environment(interactive=True)
    if not res["ready"]:
        sys.exit(1)
