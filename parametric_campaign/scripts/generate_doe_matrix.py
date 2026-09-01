#!/usr/bin/env python3
"""
Generate Design of Experiments (DOE) Matrix for Immersion Cooling Bypass Parametric Study.
Covers:
1. Baseline Full-Factorial Grid (Open Ratio x Reynolds Number for FC-40 Plate-Fin).
2. Fluid Sensitivity Matrix (PAO-4 and EFL-1 across Open Ratios and Reynolds Numbers).
3. Topology Sensitivity Matrix (Micro-Pin-Fin and Oblique-Fin across Open Ratios).
4. TDP Heat Load Sensitivity Matrix (300 W, 500 W, 700 W, 1000 W).
5. Out-of-sample verification test cases for predictive model validation.
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

# 1U Chassis Dimensions
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

    # Tier 1: Baseline Full Factorial Grid (FC-40, Plate-Fin, 700 W TDP)
    open_ratios = [0.0, 0.25, 0.50, 0.75, 1.00]
    reynolds_numbers = [50, 100, 250, 500, 1000]

    for or_val in open_ratios:
        for re_val in reynolds_numbers:
            fluid = "FC-40"
            nu = FLUID_DATABASE[fluid]["nu"]
            u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
            q_vol_m3_s = u_in * CHASSIS["cross_section_area_m2"]
            q_lpm = q_vol_m3_s * 60000.0

            cases.append({
                "case_id": f"DOE_Case_{case_idx:02d}",
                "campaign_group": "Baseline_OpenRatio_Reynolds",
                "open_ratio": or_val,
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

    # Tier 2: Fluid Sensitivity Matrix (PAO-4 and EFL-1 across OR = [0.0, 0.5, 1.0] and Re = [100, 500])
    for fluid in ["PAO-4", "EFL-1"]:
        for or_val in [0.0, 0.50, 1.00]:
            for re_val in [100, 500]:
                nu = FLUID_DATABASE[fluid]["nu"]
                u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
                q_vol_m3_s = u_in * CHASSIS["cross_section_area_m2"]
                q_lpm = q_vol_m3_s * 60000.0

                cases.append({
                    "case_id": f"DOE_Case_{case_idx:02d}",
                    "campaign_group": "Fluid_Sensitivity",
                    "open_ratio": or_val,
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

    # Tier 3: Topology Sensitivity Matrix (Micro-Pin-Fin and Oblique-Fin across OR = [0.0, 0.5, 1.0] at Re = 250)
    for topo in ["Micro-Pin-Fin", "Oblique-Fin"]:
        for or_val in [0.0, 0.50, 1.00]:
            fluid = "FC-40"
            re_val = 250
            nu = FLUID_DATABASE[fluid]["nu"]
            u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
            q_vol_m3_s = u_in * CHASSIS["cross_section_area_m2"]
            q_lpm = q_vol_m3_s * 60000.0

            cases.append({
                "case_id": f"DOE_Case_{case_idx:02d}",
                "campaign_group": "Topology_Sensitivity",
                "open_ratio": or_val,
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

    # Tier 4: TDP Thermal Load Sensitivity (300 W, 500 W, 1000 W at OR = 0.5, Re = 250 in FC-40)
    for tdp in [300.0, 500.0, 1000.0]:
        fluid = "FC-40"
        or_val = 0.50
        re_val = 250
        nu = FLUID_DATABASE[fluid]["nu"]
        u_in = compute_inlet_velocity(re_val, nu, CHASSIS["hydraulic_diameter_m"])
        q_vol_m3_s = u_in * CHASSIS["cross_section_area_m2"]
        q_lpm = q_vol_m3_s * 60000.0

        cases.append({
            "case_id": f"DOE_Case_{case_idx:02d}",
            "campaign_group": "ThermalLoad_Sensitivity",
            "open_ratio": or_val,
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

    # Tier 5: Blind Out-of-Sample Verification Test Points (4 cases withheld for model validation)
    out_of_sample_points = [
        {"or": 0.35, "re": 175, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.65, "re": 350, "fluid": "FC-40", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.50, "re": 200, "fluid": "PAO-4", "topo": "Plate-Fin", "tdp": 700.0},
        {"or": 0.25, "re": 400, "fluid": "EFL-1", "topo": "Oblique-Fin", "tdp": 700.0},
    ]

    for pt in out_of_sample_points:
        fluid = pt["fluid"]
        nu = FLUID_DATABASE[fluid]["nu"]
        u_in = compute_inlet_velocity(pt["re"], nu, CHASSIS["hydraulic_diameter_m"])
        q_vol_m3_s = u_in * CHASSIS["cross_section_area_m2"]
        q_lpm = q_vol_m3_s * 60000.0

        cases.append({
            "case_id": f"DOE_Case_{case_idx:02d}",
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
            "title": "Immersion Cooling Open-Ratio Bypass Parametric Campaign DOE",
            "total_cases": len(cases),
            "chassis": CHASSIS,
            "fluid_database": FLUID_DATABASE
        },
        "cases": cases
    }

    out_json = os.path.join(os.path.dirname(__file__), "..", "doe_definition.json")
    with open(out_json, "w") as f:
        json.dump(doe_payload, f, indent=2)

    print(f"[SUCCESS] Generated DOE matrix with {len(cases)} design points -> {out_json}")
    return doe_payload

if __name__ == "__main__":
    generate_matrix()
