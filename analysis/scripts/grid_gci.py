#!/usr/bin/env python3
"""Grid convergence index (GCI) for the three-grid study (G001 coarse, C018 medium, G002 fine),
OR = 0.1, Re_ch = 250, FC-40. Procedure of Celik et al. (2008, ASME J. Fluids Eng. 130, 078001),
which generalises Roache (1997) to non-constant refinement ratios; matches the method named in
manuscript/sections/verification_validation.tex Sec. vv-grid (Eca and Hoekstra 2014; Roache 1997).
Reads cell counts and the three verification quantities (T_chip_max_C, dp_sink_Pa, phi_field)
straight from cfd/unit_cell_campaign/dataset_ledger_unitcell.csv; nothing is typed in by hand."""
import pandas as pd
from scipy.optimize import brentq

L = pd.read_csv("/mnt/e/ijhmt-cfp/Paper-5/cfd/unit_cell_campaign/dataset_ledger_unitcell.csv")
row = {c: L[L.case_id == c].iloc[0] for c in ("G001", "C018", "G002")}
N1, N2, N3 = row["G001"].cells, row["C018"].cells, row["G002"].cells   # coarse, medium, fine
r21 = (N2 / N1) ** (1 / 3)
r32 = (N3 / N2) ** (1 / 3)
print("cells: coarse=%d medium=%d fine=%d" % (N1, N2, N3))
print("refinement ratios: r21=%.4f r32=%.4f" % (r21, r32))

def gci(name, phi1, phi2, phi3):
    """phi1=fine(most refined)=G002, phi2=medium=C018, phi3=coarse=G001, Celik ordering: 1 finest."""
    e21 = phi2 - phi1   # medium - fine
    e32 = phi3 - phi2   # coarse - medium
    if e21 == 0 or e32 == 0:
        print("%-14s all-equal or zero difference; grid-independent to solver precision" % name)
        return
    s = 1 if (e32 / e21) > 0 else -1
    import math
    def q_of_p(p):
        num = r21 ** p - s
        den = r32 ** p - s
        return math.log(num / den)

    def f(p):
        return abs(math.log(abs(e32 / e21)) + q_of_p(p)) - p * math.log(r21)

    p = brentq(f, 0.05, 12.0)
    phi_ext = (r21 ** p * phi1 - phi2) / (r21 ** p - 1)
    ea21 = abs((phi1 - phi2) / phi1)
    e_ext21 = abs((phi_ext - phi1) / phi_ext)
    gci_fine = 1.25 * ea21 / (r21 ** p - 1)
    print("%-14s fine=%.6g medium=%.6g coarse=%.6g" % (name, phi1, phi2, phi3))
    print("               apparent order p=%.3f  extrapolated=%.6g" % (p, phi_ext))
    print("               approx. rel. error (fine-medium)=%.4f%%  extrapolated rel. error=%.4f%%  GCI_fine=%.4f%%" % (
        100 * ea21, 100 * e_ext21, 100 * gci_fine))

gci("T_chip_max_C", row["G002"].T_chip_max_C, row["C018"].T_chip_max_C, row["G001"].T_chip_max_C)
gci("dp_sink_Pa", row["G002"].dp_sink_Pa, row["C018"].dp_sink_Pa, row["G001"].dp_sink_Pa)
gci("Phi_bypass", row["G002"].phi_field, row["C018"].phi_field, row["G001"].phi_field)
gci("Nu", row["G002"].Nu, row["C018"].Nu, row["G001"].Nu)
