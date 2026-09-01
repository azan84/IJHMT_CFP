#!/bin/bash
# ==============================================================================
# Immersion Liquid Cooling Open-Ratio Bypass Parametric Campaign Launcher
# Self-Bootstrapping Standalone Runner for Any Workstation / Cluster
# Repository: https://github.com/azan84/IJHMT_CFP
# ==============================================================================

set -e

# ANSI Color Codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "=============================================================================="
echo "  IMMERSION COOLING OPEN-RATIO BYPASS PARAMETRIC SIMULATION CAMPAIGN"
echo "  Automated Design of Experiments (DOE) Multi-Scale Solver & Postprocessor"
echo "  Repository: github.com/azan84/IJHMT_CFP"
echo "=============================================================================="
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="https://github.com/azan84/IJHMT_CFP.git"
SSH_REPO_URL="git@github.com:azan84/IJHMT_CFP.git"

# 1. Self-Bootstrapping: Check if running inside full cloned repository or standalone file
if [ ! -f "$SCRIPT_DIR/run_parametric_campaign.py" ] || [ ! -f "$SCRIPT_DIR/doe_definition.json" ]; then
    echo -e "${YELLOW}[*] Standalone execution detected. Bootstrapping repository from GitHub...${NC}"
    
    if [ ! -d "$SCRIPT_DIR/IJHMT_CFP" ]; then
        echo -e "${CYAN}--> Cloning repository from ${REPO_URL}...${NC}"
        git clone "$REPO_URL" "$SCRIPT_DIR/IJHMT_CFP" || git clone "$SSH_REPO_URL" "$SCRIPT_DIR/IJHMT_CFP"
    fi
    
    CAMPAIGN_DIR="$SCRIPT_DIR/IJHMT_CFP/parametric_campaign"
    REPO_DIR="$SCRIPT_DIR/IJHMT_CFP"
else
    CAMPAIGN_DIR="$SCRIPT_DIR"
    REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# 2. Software & Environment Check (OpenFOAM v2406, MPI, Python3, Git)
echo -e "\n${BLUE}[*] Phase 1: Checking Required Software & Solvers...${NC}"

if ! command -v simpleFoam &> /dev/null; then
    echo -e "${YELLOW}[!] OpenFOAM environment is not currently active in this shell.${NC}"
    
    # Candidate bashrc paths
    OF_BASHRC_CANDIDATES=(
        "/usr/lib/openfoam/openfoam2406/etc/bashrc"
        "/usr/lib/openfoam/openfoam2312/etc/bashrc"
        "/usr/lib/openfoam/openfoam2306/etc/bashrc"
        "/usr/lib/openfoam/openfoam2212/etc/bashrc"
        "/opt/openfoam2406/etc/bashrc"
        "/opt/openfoam2312/etc/bashrc"
        "/opt/openfoam10/etc/bashrc"
        "/opt/openfoam11/etc/bashrc"
        "$HOME/OpenFOAM/OpenFOAM-v2406/etc/bashrc"
        "$HOME/OpenFOAM/OpenFOAM-10/etc/bashrc"
    )

    FOUND_BASHRC=""
    for p in "${OF_BASHRC_CANDIDATES[@]}"; do
        if [ -f "$p" ]; then
            FOUND_BASHRC="$p"
            break
        fi
    done

    if [ -n "$FOUND_BASHRC" ]; then
        echo -e "${GREEN}[OK] Detected OpenFOAM installation at: ${FOUND_BASHRC}${NC}"
        echo -e "${CYAN}--> Sourcing OpenFOAM environment...${NC}"
        source "$FOUND_BASHRC"
    else
        echo -e "${RED}[ERROR] OpenFOAM installation was not found in standard directories.${NC}"
        read -p "Please enter the absolute path to your OpenFOAM etc/bashrc: " USER_BASHRC
        if [ -f "$USER_BASHRC" ]; then
            source "$USER_BASHRC"
        else
            echo -e "${RED}[FATAL] Invalid path. Please install OpenFOAM (e.g. openfoam2406) and re-run.${NC}"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}[PASS] OpenFOAM Active: $(which simpleFoam)${NC}"
echo -e "${GREEN}[PASS] MPI Active:      $(which mpirun)${NC}"
echo -e "${GREEN}[PASS] Python3 Active:  $(which python3)${NC}"
echo -e "${GREEN}[PASS] Git Active:      $(which git)${NC}"

# 3. Synchronize with GitHub repository
echo -e "\n${BLUE}[*] Phase 2: Synchronizing with Remote GitHub Repository...${NC}"
cd "$REPO_DIR"
git pull --rebase origin main || echo -e "${YELLOW}[!] Git pull warning (continuing with local files).${NC}"

# 4. Launch Interactive Python Orchestrator
echo -e "\n${BLUE}[*] Phase 3: Launching Interactive Resource Optimizer & Solver Queue...${NC}"
cd "$CAMPAIGN_DIR"
python3 run_parametric_campaign.py "$@"

echo -e "\n${GREEN}${BOLD}=============================================================================="
echo "  PARAMETRIC SIMULATION CAMPAIGN EXECUTION FINISHED"
echo "  Results aggregated in: $CAMPAIGN_DIR/results/"
echo "=============================================================================="
echo -e "${NC}"
