#!/usr/bin/env python3
"""
Parametric Structured Mesh Generator for Open-Ratio Immersion Cooling.
Dynamically computes:
- Physics-based geometric scaling: Fin height H_fin(OR) = H_chassis * (1 - OR)
- Clearance gap C(OR) = H_chassis - H_fin
- Dynamic 1-layer (sealed) or 2-layer (bypass) blockMesh topology
- Multi-resolution grid density: high (~1.1M cells), medium (~350k cells), fast (~85k cells)
"""

import os
import sys

def generate_blockmesh_dict(case_dir, open_ratio=0.5, topology="Plate-Fin", resolution="high"):
    os.makedirs(os.path.join(case_dir, "system"), exist_ok=True)
    
    # 1U Chassis Envelope: L = 400 mm, W = 140 mm, H = 44.45 mm
    W_half_m = 0.070    # -70 mm to +70 mm (Width = 140 mm)
    H_chassis = 0.04445 # 44.45 mm total height
    
    # Physical fin height scaling with Open Ratio (OR in [0.0, 1.0])
    # OR = 0.0 -> Fully shrouded (H_fin = 44.45 mm, Clearance = 0 mm)
    # OR = 0.5 -> 50% clearance bypass (H_fin = 22.23 mm, Clearance = 22.22 mm)
    # OR = 1.0 -> Bare open channel (H_fin = 2.2 mm baseline base, Clearance = 42.25 mm)
    clamped_or = min(0.95, max(0.0, float(open_ratio)))
    H_fin = max(0.0022, H_chassis * (1.0 - clamped_or))
    z_fin_top = round(H_fin, 6)
    clearance_gap = round(H_chassis - z_fin_top, 6)
    
    # Grid Discretization based on resolution mode
    if resolution == "high":
        nx_entry = 60; nx_chip1 = 80; nx_gap = 50; nx_chip2 = 80; nx_exit = 60
        ny_core = 100
        nz_total = 40
        nz_fin = max(10, int(nz_total * (H_fin / H_chassis)))
        nz_clearance = max(0, nz_total - nz_fin)
    elif resolution == "medium":
        nx_entry = 35; nx_chip1 = 45; nx_gap = 30; nx_chip2 = 45; nx_exit = 35
        ny_core = 55
        nz_total = 26
        nz_fin = max(6, int(nz_total * (H_fin / H_chassis)))
        nz_clearance = max(0, nz_total - nz_fin)
    else: # fast
        nx_entry = 20; nx_chip1 = 24; nx_gap = 16; nx_chip2 = 24; nx_exit = 20
        ny_core = 32
        nz_total = 18
        nz_fin = max(5, int(nz_total * (H_fin / H_chassis)))
        nz_clearance = max(0, nz_total - nz_fin)
        
    has_clearance = (clamped_or > 0.02) and (clearance_gap > 0.001) and (nz_clearance >= 4)
    
    if not has_clearance:
        # 1-Layer Mesh (Fully Shrouded: z = 0 to H_chassis)
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

    // Layer 1: z = {H_chassis:.5f} (Top chassis shroud wall)
    (0.000 -{W_half_m:.4f} {H_chassis:.5f}) // 12
    (0.000  {W_half_m:.4f} {H_chassis:.5f}) // 13
    (0.100 -{W_half_m:.4f} {H_chassis:.5f}) // 14
    (0.100  {W_half_m:.4f} {H_chassis:.5f}) // 15
    (0.180 -{W_half_m:.4f} {H_chassis:.5f}) // 16
    (0.180  {W_half_m:.4f} {H_chassis:.5f}) // 17
    (0.240 -{W_half_m:.4f} {H_chassis:.5f}) // 18
    (0.240  {W_half_m:.4f} {H_chassis:.5f}) // 19
    (0.320 -{W_half_m:.4f} {H_chassis:.5f}) // 20
    (0.320  {W_half_m:.4f} {H_chassis:.5f}) // 21
    (0.400 -{W_half_m:.4f} {H_chassis:.5f}) // 22
    (0.400  {W_half_m:.4f} {H_chassis:.5f}) // 23
);

blocks
(
    hex (0 2 3 1 12 14 15 13)       ({nx_entry} {ny_core} {nz_total}) simpleGrading (1 1 1)
    hex (2 4 5 3 14 16 17 15)       ({nx_chip1} {ny_core} {nz_total}) simpleGrading (1 1 1)
    hex (4 6 7 5 16 18 19 17)       ({nx_gap}   {ny_core} {nz_total}) simpleGrading (1 1 1)
    hex (6 8 9 7 18 20 21 19)       ({nx_chip2} {ny_core} {nz_total}) simpleGrading (1 1 1)
    hex (8 10 11 9 20 22 23 21)     ({nx_exit}  {ny_core} {nz_total}) simpleGrading (1 1 1)
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
        );
    }}
    outlet
    {{
        type patch;
        faces
        (
            (10 22 23 11)
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
    else:
        # 2-Layer Mesh (Fin Region + Bypass Clearance Region)
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

    // Layer 1: z = {z_fin_top:.5f} (Fin tip interface plane)
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

    // Layer 2: z = {H_chassis:.5f} (Top chassis wall)
    (0.000 -{W_half_m:.4f} {H_chassis:.5f}) // 24
    (0.000  {W_half_m:.4f} {H_chassis:.5f}) // 25
    (0.100 -{W_half_m:.4f} {H_chassis:.5f}) // 26
    (0.100  {W_half_m:.4f} {H_chassis:.5f}) // 27
    (0.180 -{W_half_m:.4f} {H_chassis:.5f}) // 28
    (0.180  {W_half_m:.4f} {H_chassis:.5f}) // 29
    (0.240 -{W_half_m:.4f} {H_chassis:.5f}) // 30
    (0.240  {W_half_m:.4f} {H_chassis:.5f}) // 31
    (0.320 -{W_half_m:.4f} {H_chassis:.5f}) // 32
    (0.320  {W_half_m:.4f} {H_chassis:.5f}) // 33
    (0.400 -{W_half_m:.4f} {H_chassis:.5f}) // 34
    (0.400  {W_half_m:.4f} {H_chassis:.5f}) // 35
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
        generate_blockmesh_dict(cdir, open_ratio=or_v, resolution="high")
        print(f"[SUCCESS] BlockMesh generated for OR = {or_v}")
