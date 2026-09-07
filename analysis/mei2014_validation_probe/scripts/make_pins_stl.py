#!/usr/bin/env python3
"""Write an ASCII STL of N_ROWS identical cylindrical pins (Mei et al. 2014, IJHMT 70, Table 1
geometry: Df = 1 mm pin diameter, SL = 1.8 mm row pitch, hf = 1 mm pin height), one pin per row,
centred on the y = 0 symmetry plane (half-pitch domain, ST/2 = 0.9 mm). Each pin is closed
(side wall + top cap + a bottom cap set below the domain floor) so it is a watertight surface
for snappyHexMesh to use as a solid obstacle protruding from the channel floor."""
import math, sys

DF = 1.0e-3          # pin diameter [m]
R = DF / 2
HF = 1.0e-3           # pin height [m]
SL = 1.8e-3           # row pitch [m]
N_ROWS = 15
Z_BOTTOM = -0.2e-3    # extend below the domain floor (z=0) so the side wall fully penetrates it
Z_TOP = HF            # pin tip, flush with the exposed clearance region
N_SEG = 48            # circumferential resolution

def circle_pts(xc, r, n):
    return [(xc + r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]

facets = []
def tri(p1, p2, p3):
    facets.append((p1, p2, p3))

for row in range(N_ROWS):
    xc = SL / 2 + row * SL
    ring = circle_pts(xc, R, N_SEG)
    top_centre = (xc, 0.0, Z_TOP)
    bot_centre = (xc, 0.0, Z_BOTTOM)
    for i in range(N_SEG):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % N_SEG]
        p0b, p1b = (x0, y0, Z_BOTTOM), (x1, y1, Z_BOTTOM)
        p0t, p1t = (x0, y0, Z_TOP), (x1, y1, Z_TOP)
        # side wall: two triangles per segment, outward normal
        tri(p0b, p1b, p1t)
        tri(p0b, p1t, p0t)
        # top cap (outward normal = +z)
        tri(top_centre, (x0, y0, Z_TOP), (x1, y1, Z_TOP))
        # bottom cap (outward normal = -z)
        tri(bot_centre, (x1, y1, Z_BOTTOM), (x0, y0, Z_BOTTOM))

out = sys.argv[1] if len(sys.argv) > 1 else "pins.stl"
with open(out, "w") as f:
    f.write("solid pins\n")
    for p1, p2, p3 in facets:
        # normal not needed to be exact for snappyHexMesh (it recomputes), write a placeholder
        f.write(" facet normal 0 0 0\n  outer loop\n")
        for p in (p1, p2, p3):
            f.write("   vertex %.9e %.9e %.9e\n" % p)
        f.write("  endloop\n endfacet\n")
    f.write("endsolid pins\n")
print("wrote", len(facets), "facets to", out, "for", N_ROWS, "pins")
