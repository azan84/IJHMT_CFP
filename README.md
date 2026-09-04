# IJHMT_CFP

Simulation set-up of the manuscript "Dimensionless framework for bypass-controlled single-phase immersion
cooling of server heat sinks" (International Journal of Heat and Mass Transfer, special issue, revision round 3).

| Directory | Content | Status |
|---|---|---|
| `unit_cell_campaign/` | Spanwise-periodic conjugate unit-cell calibration campaign (OpenFOAM v2406, `chtMultiRegionSimpleFoam`): builder, design (177 cases), runner for a second machine, results of the remote share | active (September 2026) |
| `parametric_campaign/` | Earlier 250-case sweep on the empty duct (`simpleFoam`, isothermal, no fins, no energy equation) | superseded: its runs carry no thermal or bypass information (manuscript Section 6.1); kept as the archive of what was run |

See `unit_cell_campaign/README.md` for how to run the remote share. One-file start on a fresh machine: copy
`run_remote_share.py` there and run `python3 run_remote_share.py` (it clones this repository and starts the run).
