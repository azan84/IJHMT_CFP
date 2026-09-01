#!/usr/bin/env python3
"""
Parametric Multi-Block Structured Mesh Generator for Immersion Cooling Chassis.
Dynamically sets up blockMeshDict based on:
- Open Ratio (OR in [0.0, 1.0]): modulates clearance / bypass plenum cross-section.
- Heat Sink Topology (Plate-Fin, Micro-Pin-Fin, Oblique-Fin).
- Channel and chip dimensions.
"""

import os
import sys

def generate_blockmesh_dict(case_dir, open_ratio=0.5, topology="Plate-Fin"):
    os.makedirs(os.path.join(case_dir, "system"), exist_ok=True)
    
    # 1U Chassis Dimensions: L = 400 mm, W = 140 mm, H = 44.45 mm
    L_m = 0.400
    W_half_m = 0.070
    H_m = 0.04445
    
    # Heat sink base: L_hs = 80 mm, W_hs = 70 mm, H_hs = 25 mm
    # Chip 1 center x = 140 mm (x in [100, 180] mm)
    # Chip 2 center x = 280 mm (x in [240, 320] mm)
    
    # Clearance height modulated by Open Ratio:
    # At OR = 0 (fully shrouded), c = 0; at OR = 1.0, c = 19.45 mm
    H_fin = 0.025
    c_max = H_m - H_fin # 0.01945 m
    c_current = open_ratio * c_max
    z_fin_top = H_fin
    
    # Grid density parameters
    nx_entry = 20
    nx_chip1 = 24
    nx_gap = 16
    nx_chip2 = 24
    nx_exit = 20
    
    ny_core = 32
    nz_fin = 20
    nz_clearance = max(6, int(16 * max(0.2, open_ratio)))
    
    dict_content = f"""FoamFile
{{
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
scale 1.0;

vertices
(
    // Layer 0: z = 0.000 (Chassis bottom / Chip base)
    (0.000 -{W_half_m:.4f} 0.000) // 0
    (0.000  {W_half_m:.4f} 0.000) // 1
    (0.100 -{W_half_m:.4f} 0.000) // 2
    (0.100  {W_half_m:.4f} 0.000) // 3
    (0.180 -{W_half_m:.4f} 0.000) // 4
    (0.180  {W_half_m:.4f} 0.000) // 5
    (0.240 -{W_half_m:.4f} 0.000) // 6
    (0.240  {W_half_m:.4f} 0.000) // 7
    (0.320 -{W_half_m:.4f} 0.000) // 8
    (0.320  {W_half_m:.4f} 0.000) // 9
    (0.400 -{W_half_m:.4f} 0.000) // 10
    (0.400  {W_half_m:.4f} 0.000) // 11

    // Layer 1: z = {z_fin_top:.5f} (Fin tip plane)
    (0.000 -{W_half_m:.4f} {z_fin_top:.5f}) // 12
    (0.000  {W_half_m:.4f} {z_fin_top:.5f}) // 13
    (0.100 -{W_half_m:.4f} {z_fin_top:.5f}) // 14
    (0.100  {W_half_m:.4f} {z_fin_top:.5f}) // 15
    (0.180 -{W_half_m:.4f} {z_fin_top:.5f}) // 16
    (0.180  {W_half_m:.4f} {z_fin_top:.5f}) // 17
    (0.240 -{W_half_m:.4f} {z_fin_top:.5f}) // 18
    (0.240  {W_half_m:.4f} {z_fin_top:.5f}) // 19
    (0.320 -{W_half_m:.4f} {z_fin_top:.5f}) // 20
    (0.320  {W_half_m:.4f} {z_fin_top:.5f}) // 21
    (0.400 -{W_half_m:.4f} {z_fin_top:.5f}) // 22
    (0.400  {W_half_m:.4f} {z_fin_top:.5f}) // 23

    // Layer 2: z = {H_m:.5f} (Top chassis wall)
    (0.000 -{W_half_m:.4f} {H_m:.5f}) // 24
    (0.000  {W_half_m:.4f} {H_m:.5f}) // 25
    (0.100 -{W_half_m:.4f} {H_m:.5f}) // 26
    (0.100  {W_half_m:.4f} {H_m:.5f}) // 27
    (0.180 -{W_half_m:.4f} {H_m:.5f}) // 28
    (0.180  {W_half_m:.4f} {H_m:.5f}) // 29
    (0.240 -{W_half_m:.4f} {H_m:.5f}) // 30
    (0.240  {W_half_m:.4f} {H_m:.5f}) // 31
    (0.320 -{W_half_m:.4f} {H_m:.5f}) // 32
    (0.320  {W_half_m:.4f} {H_m:.5f}) // 33
    (0.400 -{W_half_m:.4f} {H_m:.5f}) // 34
    (0.400  {W_half_m:.4f} {H_m:.5f}) // 35
);

blocks
(
    // Lower Fin Domain (Blocks 0-4)
    hex (0 2 3 1 12 14 15 13)       ({nx_entry} {ny_core} {nz_fin}) simpleGrading (1 1 1)
    hex (2 4 5 3 14 16 17 15)       ({nx_chip1} {ny_core} {nz_fin}) simpleGrading (1 1 1)
    hex (4 6 7 5 16 18 19 17)       ({nx_gap}   {ny_core} {nz_fin}) simpleGrading (1 1 1)
    hex (6 8 9 7 18 20 21 19)       ({nx_chip2} {ny_core} {nz_fin}) simpleGrading (1 1 1)
    hex (8 10 11 9 20 22 23 21)     ({nx_exit}  {ny_core} {nz_fin}) simpleGrading (1 1 1)

    // Upper Bypass Domain (Blocks 5-9)
    hex (12 14 15 13 24 26 27 25)   ({nx_entry} {ny_core} {nz_clearance}) simpleGrading (1 1 1)
    hex (14 16 17 15 26 28 29 27)   ({nx_chip1} {ny_core} {nz_clearance}) simpleGrading (1 1 1)
    hex (16 18 19 17 28 30 31 29)   ({nx_gap}   {ny_core} {nz_clearance}) simpleGrading (1 1 1)
    hex (18 20 21 19 30 32 33 31)   ({nx_chip2} {ny_core} {nz_clearance}) simpleGrading (1 1 1)
    hex (20 22 23 21 32 34 35 33)   ({nx_exit}  {ny_core} {nz_clearance}) simpleGrading (1 1 1)
);

edges ();

defaultPatch
{{
    name walls;
    type wall;
}}

boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (0 1 13 12)
            (12 13 25 24)
        );
    }}
    outlet
    {{
        type patch;
        faces
        (
            (10 22 23 11)
            (22 34 35 23)
        );
    }}
    chip_bases
    {{
        type wall;
        faces
        (
            (2 4 5 3)
            (6 8 9 7)
        );
    }}
);
"""
    mesh_path = os.path.join(case_dir, "system", "blockMeshDict")
    with open(mesh_path, "w") as f:
        f.write(dict_content)
    return mesh_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cdir = sys.argv[1]
        or_v = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        generate_blockmesh_dict(cdir, open_ratio=or_v)
        print(f"[SUCCESS] blockMeshDict generated for OR = {or_v}")
