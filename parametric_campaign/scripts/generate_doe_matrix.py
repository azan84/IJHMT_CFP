#!/usr/bin/env python3
"""
Generate Expanded 250-Case Design of Experiments (DOE) Matrix for Immersion Cooling.
Tiers:
1. Baseline Full-Factorial Grid (11 Open Ratios x 9 Reynolds Numbers = 99 Cases in FC-40 Plate-Fin).
2. Fluid Sensitivity Matrix (PAO-4 & EFL-1 across 11 Open Ratios x 3 Re = 66 Cases).
3. Topology Sensitivity Matrix (Micro-Pin-Fin & Oblique-Fin across 11 Open Ratios x 2 Re = 44 Cases).
4. TDP Heat Load Sensitivity (300 W, 500 W, 850 W, 1000 W, 1200 W = 25 Cases).
5. Out-of-Sample Validation Grid (16 Cases).
Total: 250 Cases.
"""

import json
import os

FLUID_DATABASE = {
    "FC-40": {
        "description": "3M Fluorinert FC-40 Dielectric Liquid",
        "rho": 1855.0,        # kg/m^3 at 25 C
        "cp": 1052.0,         # J/(kg K)
        "k": 0.0654,          # W/(m K)
        "mu": 3.50e-3,        # Pa s
        "nu": 3.50e-3 / 1855.0, # 1.887e-6 m^2/s
        "Pr": (1052.0 * 3.50e-3) / 0.0654 # 56.3
    },
    "PAO-4": {
        "description": "Polyalphaolefin PAO-4 Synthetic Hydrocarbon Oil",
        "rho": 795.0,         # kg/m^3 at 25 C
        "cp": 2210.0,         # J/(kg K)
        "k": 0.1430,          # W/(m K)
        "mu": 1.42e-2,        # Pa s
        "nu": 1.42e-2 / 795.0, # 1.786e-5 m^2/s
        "Pr": (2210.0 * 1.42e-2) / 0.1430 # 219.5
    },
    "EFL-1": {
        "description": "Dielectric Fluorinated Liquid EFL-1",
        "rho": 1889.0,        # kg/m^3 at 25 C
        "cp": 1165.0,         # J/(kg K)
        "k": 0.0680,          # W/(m K)
        "mu": 2.77e-3,        # Pa s
        "nu": 2.77e-3 / 1889.0, # 1.466e-6 m^2/s
        "Pr": (1165.0 * 2.77e-3) / 0.0680 # 47.46
    }
}

CHASSIS = {
    "height_m": 0.04445,      # 1U height (44.45 mm)
    "width_m": 0.140,         # Core channel width (140 mm)
    "length_m": 0.400,        # Chassis length (400 mm)
    "hydraulic_diameter_m": (2 * 0.04445 * 0.140) / (0.04445 + 0.140), # 0.0675 m
    "cross_section_area_m2": 0.04445 * 0.140                            # 0.006223 m^2
}

def compute_inlet_velocity(re_ch, nu, dh):
    return (re_ch * nu) / dh

def generate_matrix():
    cases = []
    case_idx = 1

    # 11 Open Ratio Levels: 0% to 100% in 10% steps
    open_ratios_11 = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
    # 9 Reynolds Numbers: 25 to 1000
    reynolds_9 = [25, 50, 100, 150, 250, 350, 500, 750, 1000]

    # Tier 1: Baseline Full Factorial Grid (FC-40, Plate-Fin, 700 W TDP) -> 11 x 9 = 99 Cases
    for or_val in open_ratios_11:
        for re_val in reynolds_9:
            fluid = "FC-40"
            nu = FLUID_DATABASE[fluid]["nu"]
            u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
            q_lpm = (u_in * CHASSIS["cross_section_area_m2"]) * 60000.0

            cases.append({
                "case_id": f"DOE_Case_{case_idx:03d}",
                "campaign_group": "Baseline_OpenRatio_Reynolds",
                "open_ratio": round(or_val, 2),
                "reynolds_number": re_val,
                "fluid": fluid,
                "topology": "Plate-Fin",
                "tdp_per_chip_W": 700.0,
                "num_chips": 2,
                "total_heat_W": 1400.0,
                "inlet_temp_C": 25.0,
                "inlet_velocity_m_s": round(u_in, 6),
                "flow_rate_LPM": round(q_lpm, 3),
                "is_out_of_sample": False
            })
            case_idx += 1

    # Tier 2: Fluid Sensitivity Matrix (PAO-4 & EFL-1 across 11 ORs x 3 Re [50, 250, 750]) -> 2 x 33 = 66 Cases
    for fluid in ["PAO-4", "EFL-1"]:
        for or_val in open_ratios_11:
            for re_val in [50, 250, 750]:
                nu = FLUID_DATABASE[fluid]["nu"]
                u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
                q_lpm = (u_in * CHASSIS["cross_section_area_m2"]) * 60000.0

                cases.append({
                    "case_id": f"DOE_Case_{case_idx:03d}",
                    "campaign_group": "Fluid_Sensitivity",
                    "open_ratio": round(or_val, 2),
                    "reynolds_number": re_val,
                    "fluid": fluid,
                    "topology": "Plate-Fin",
                    "tdp_per_chip_W": 700.0,
                    "num_chips": 2,
                    "total_heat_W": 1400.0,
                    "inlet_temp_C": 25.0,
                    "inlet_velocity_m_s": round(u_in, 6),
                    "flow_rate_LPM": round(q_lpm, 3),
                    "is_out_of_sample": False
                })
                case_idx += 1

    # Tier 3: Topology Sensitivity (Micro-Pin-Fin & Oblique-Fin across 11 ORs x 2 Re [100, 500]) -> 2 x 22 = 44 Cases
    for topo in ["Micro-Pin-Fin", "Oblique-Fin"]:
        for or_val in open_ratios_11:
            for re_val in [100, 500]:
                fluid = "FC-40"
                nu = FLUID_DATABASE[fluid]["nu"]
                u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
                q_lpm = (u_in * CHASSIS["cross_section_area_m2"]) * 60000.0

                cases.append({
                    "case_id": f"DOE_Case_{case_idx:03d}",
                    "campaign_group": "Topology_Sensitivity",
                    "open_ratio": round(or_val, 2),
                    "reynolds_number": re_val,
                    "fluid": fluid,
                    "topology": topo,
                    "tdp_per_chip_W": 700.0,
                    "num_chips": 2,
                    "total_heat_W": 1400.0,
                    "inlet_temp_C": 25.0,
                    "inlet_velocity_m_s": round(u_in, 6),
                    "flow_rate_LPM": round(q_lpm, 3),
                    "is_out_of_sample": False
                })
                case_idx += 1

    # Tier 4: TDP Thermal Load Scaling (300 W, 500 W, 850 W, 1000 W, 1200 W across OR = [0.0, 0.25, 0.50, 0.75, 1.0]) -> 25 Cases
    for tdp in [300.0, 500.0, 850.0, 1000.0, 1200.0]:
        for or_val in [0.00, 0.25, 0.50, 0.75, 1.00]:
            fluid = "FC-40"
            re_val = 250
            nu = FLUID_DATABASE[fluid]["nu"]
            u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
            q_lpm = (u_in * CHASSIS["cross_section_area_m2"]) * 60000.0

            cases.append({
                "case_id": f"DOE_Case_{case_idx:03d}",
                "campaign_group": "ThermalLoad_Sensitivity",
                "open_ratio": round(or_val, 2),
                "reynolds_number": re_val,
                "fluid": fluid,
                "topology": "Plate-Fin",
                "tdp_per_chip_W": tdp,
                "num_chips": 2,
                "total_heat_W": 2.0 * tdp,
                "inlet_temp_C": 25.0,
                "inlet_velocity_m_s": round(u_in, 6),
                "flow_rate_LPM": round(q_lpm, 3),
                "is_out_of_sample": False
            })
            case_idx += 1

    # Tier 5: Blind Out-of-Sample Validation Grid -> 16 Cases
    out_of_sample_points = [
        {"or": 0.15, "re": 75,  "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.35, "re": 175, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.65, "re": 350, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.85, "re": 600, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.25, "re": 125, "fluid": "PAO-4", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.75, "re": 400, "fluid": "PAO-4", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.15, "re": 150, "fluid": "EFL-1", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.65, "re": 500, "fluid": "EFL-1", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.35, "re": 200, "fluid": "FC-40", "topo": "Micro-Pin-Fin", "tdp": 700.0},
        {"or": 0.75, "re": 350, "fluid": "FC-40", "topo": "Micro-Pin-Fin", "tdp": 700.0},
        {"or": 0.25, "re": 200, "fluid": "FC-40", "topo": "Oblique-Fin", "tdp": 700.0},
        {"or": 0.85, "re": 450, "fluid": "FC-40", "topo": "Oblique-Fin", "tdp": 700.0},
        {"or": 0.50, "re": 300, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 400.0},
        {"or": 0.50, "re": 300, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 600.0},
        {"or": 0.50, "re": 300, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 800.0},
        {"or": 0.50, "re": 300, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 950.0},
    ]

    for pt in out_of_sample_points:
        fluid = pt["fluid"]
        nu = FLUID_DATABASE[fluid]["nu"]
        u_in = compute_inlet_velocity(pt["re"], nu, CHASSIS["hydraulic_diameter_m"])
        q_lpm = (u_in * CHASSIS["cross_section_area_m2"]) * 60000.0

        cases.append({
            "case_id": f"DOE_Case_{case_idx:03d}",
            "campaign_group": "OutOfSample_Validation",
            "open_ratio": pt["or"],
            "reynolds_number": pt["re"],
            "fluid": fluid,
            "topology": pt["topo"],
            "tdp_per_chip_W": pt["tdp"],
            "num_chips": 2,
            "total_heat_W": 2.0 * pt["tdp"],
            "inlet_temp_C": 25.0,
            "inlet_velocity_m_s": round(u_in, 6),
            "flow_rate_LPM": round(q_lpm, 3),
            "is_out_of_sample": True
        })
        case_idx += 1

    doe_payload = {
        "metadata": {
            "title": "Immersion Cooling Open-Ratio Bypass Parametric Campaign DOE (Expanded 250 Cases)",
            "total_cases": len(cases),
            "grid_resolution": "1.2 Million Cells",
            "chassis": CHASSIS,
            "fluid_database": FLUID_DATABASE
        },
        "cases": cases
    }

    out_json = os.path.join(os.path.dirname(__file__), "..", "doe_definition.json")
    with open(out_json, "w") as f:
        json.dump(doe_payload, f, indent=2)

    print(f"[SUCCESS] Generated expanded DOE matrix with {len(cases)} design points -> {out_json}")
    return doe_payload

if __name__ == "__main__":
    generate_matrix()
