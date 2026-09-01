# Immersion Liquid Cooling Open-Ratio Bypass Parametric Campaign

This directory contains the automated Design of Experiments (DOE) parametric study and multi-core CFD execution framework for the research paper on **single-phase immersion liquid cooling bypass dynamics in data-center chassis architectures**.

---

## 1. Scientific Overview & Design of Experiments (DOE)

The parametric campaign systematically explores the multi-dimensional design space governing fluid bypass diversion, core fluid starvation, and electronic component thermal resistance in single-phase immersion cooling systems.

### A. Controlled Parameters & Factor Levels
1. **Open Ratio ($\mathrm{OR}$)**:
   - Levels: $\mathrm{OR} \in [0.00, 0.25, 0.50, 0.75, 1.00]$ (Fully sealed shroud $\to$ fully open unconfined chassis).
2. **Channel Reynolds Number ($\mathrm{Re}_{\mathrm{ch}}$)**:
   - Levels: $\mathrm{Re}_{\mathrm{ch}} \in [50, 100, 250, 500, 1000]$ (Creeping laminar $\to$ transitional regime).
3. **Working Coolant Fluids**:
   - **3M Fluorinert FC-40**: $\rho = 1855\text{ kg/m}^3, c_p = 1052\text{ J/kg}\cdot\text{K}, k = 0.0654\text{ W/m}\cdot\text{K}, \mu = 3.50\text{ mPa}\cdot\text{s}, \mathrm{Pr} \approx 56.3$
   - **Polyalphaolefin PAO-4**: $\rho = 795\text{ kg/m}^3, c_p = 2210\text{ J/kg}\cdot\text{K}, k = 0.1430\text{ W/m}\cdot\text{K}, \mu = 14.20\text{ mPa}\cdot\text{s}, \mathrm{Pr} \approx 219.5$
   - **Engineered Fluid EFL-1**: $\rho = 1889\text{ kg/m}^3, c_p = 1165\text{ J/kg}\cdot\text{K}, k = 0.0680\text{ W/m}\cdot\text{K}, \mu = 2.77\text{ mPa}\cdot\text{s}, \mathrm{Pr} \approx 47.5$
4. **Heat Sink Topologies**:
   - **Plate-Fin (PF)**: Longitudinal parallel copper plate-fin arrays.
   - **Micro-Pin-Fin (MPF)**: Staggered elliptical pin arrays with transverse permeability.
   - **Oblique-Fin (OF)**: Converging-diverging secondary vortex channels.
5. **Thermal Load ($P_{\mathrm{TDP}}$)**:
   - Levels: $300\text{ W}, 500\text{ W}, 700\text{ W}, 1000\text{ W}$ per chip (dual-CPU socket configuration, $600\text{--}2000\text{ W}$ total).

### B. Total Design Points (50 Cases)
- **Baseline Full-Factorial Grid (25 Cases)**: Open Ratio $\times$ Reynolds Number in FC-40 plate-fin.
- **Fluid Sensitivity Matrix (12 Cases)**: Cross-comparison of PAO-4 and EFL-1.
- **Topology Sensitivity Matrix (6 Cases)**: Oblique-fin and pin-fin comparative response.
- **Thermal Load Sensitivity (3 Cases)**: High-density TDP power scaling.
- **Out-of-Sample Validation Points (4 Cases)**: Blind verification test cases withheld for model validation.

---

## 2. Directory Structure

```text
parametric_campaign/
├── README.md                      # Campaign documentation, physics, and user guide
├── launch_campaign.sh             # Master executable bash launcher (interactive TUI)
├── run_parametric_campaign.py     # Python multi-threaded orchestrator & scheduler
├── doe_definition.json            # Complete 50-case Design of Experiments database
├── template_case/                 # Standardized OpenFOAM v2406 case template
│   ├── 0/                         # Boundary condition templates (U, p, T, k, epsilon, alphat)
│   ├── constant/                  # Transport & thermophysical property templates
│   └── system/                    # FVM schemes, linear solvers, parallel decomposition
├── scripts/
│   ├── env_check.py               # Software & workstation hardware audit utility
│   ├── generate_doe_matrix.py     # Script to generate / update DOE parameter matrix
│   ├── mesh_generator.py          # Dynamic blockMesh generator for arbitrary OR & topology
│   ├── postprocess_case.py        # Case-level CHT postprocessor
│   ├── aggregate_results.py       # Campaign database aggregator (JSON, CSV, MD report)
│   └── git_sync.py                # Automated GitHub synchronizer
└── results/                       # Live updated campaign results
    ├── parametric_results.json    # Machine-readable output database
    ├── parametric_results.csv     # Tabular CSV spreadsheet
    ├── PARAMETRIC_STUDY_REPORT.md # Auto-generated markdown technical summary
    └── logs/                      # Execution logs and residual convergence histories
```

---

## 3. Quick Start & Execution

### Option A: Interactive Mode (Recommended for Workstations)
Launch the interactive shell script:
```bash
./parametric_campaign/launch_campaign.sh
```
The script will:
1. Audit the host software environment (OpenFOAM v2406, MPI, Python 3, Git).
2. Scan total CPU logical cores and RAM.
3. Prompt you interactively for how many CPU threads and memory to dedicate to the simulations.
4. Pull the latest case setup from GitHub (`azan84/IJHMT_CFP`).
5. Execute the simulation matrix with warm-start initial condition optimization.
6. Automatically postprocess each case and push live results back to GitHub.

### Option B: Non-Interactive / Batch Mode (For Cluster / Slurm / Background Tasks)
Run directly with specified resource allocation:
```bash
./parametric_campaign/launch_campaign.sh --non-interactive --threads 24 --ram 20
```

### Option C: Run a Specific Test Case
To run a single DOE design point (e.g., `DOE_Case_01`):
```bash
python3 parametric_campaign/run_parametric_campaign.py --case-id DOE_Case_01 --non-interactive --threads 16
```

---

## 4. Calculated Thermohydraulic Outputs

For every completed simulation, the automated postprocessing engine calculates:
* **Bypass Mass Flow Rate & Fraction**: $\dot{m}_{\mathrm{bypass}}$ [kg/s] and $\Phi_{\mathrm{bypass}} = \dot{m}_{\mathrm{bypass}} / \dot{m}_{\mathrm{total}} \times 100\%$
* **Component & Chassis Pressure Drop**: $\Delta p_{\mathrm{HS}}$ and $\Delta p_{\mathrm{total}}$ [Pa]
* **Maximum & Base Chip Temperatures**: $T_{\mathrm{chip,max}}$ and $\bar{T}_{\mathrm{base}}$ [°C]
* **Component Thermal Resistance**: $R_{\mathrm{th}} = (\bar{T}_{\mathrm{base}} - T_{\mathrm{in}}) / P_{\mathrm{TDP}}$ [K/W]
* **Convective Heat Transfer Coefficient & Nusselt Number**: $h_{\mathrm{conv}}$ [W/m$^2$·K] and $\mathrm{Nu}$ [-]
* **Hydraulic Pumping Power**: $W_{\mathrm{pump}} = Q_{\mathrm{vol}} \Delta p$ [W]
* **Thermal-Hydraulic Figure of Merit**: $\mathrm{FOM} = 1 / (R_{\mathrm{th}} W_{\mathrm{pump}})$ [K$^{-1}$]

All outputs are automatically formatted into `results/parametric_results.json`, `results/parametric_results.csv`, and `results/PARAMETRIC_STUDY_REPORT.md`.
