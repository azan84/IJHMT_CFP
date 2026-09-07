#!/usr/bin/env python3
"""Post-process the Mei et al. (2014) hc/hf=1.2 probe case: area-weighted patch averages from
foamToVTK output (floor+pins wall temperature, outlet bulk temperature, inlet pressure), then the
paper's own Nu/f definitions (Eqs. 14, 16) and comparison to its Eq. 20/23 correlations."""
import vtk
import math
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

CASE = "/mnt/e/ijhmt-cfp/Paper-5/cfd/mei2014_pinfin_validation/case_hc1.2"

def read_patch(path):
    r = vtk.vtkXMLPolyDataReader()
    r.SetFileName(path)
    r.Update()
    return r.GetOutput()

def area_weighted_avg(poly, field_name, is_point_data=True):
    """Area-weighted average of a field over a triangulated/quad patch surface."""
    tri = vtk.vtkTriangleFilter()
    tri.SetInputData(poly)
    tri.Update()
    surf = tri.GetOutput()
    if is_point_data:
        arr = vtk_to_numpy(surf.GetPointData().GetArray(field_name))
        pts = vtk_to_numpy(surf.GetPoints().GetData())
    else:
        arr = vtk_to_numpy(surf.GetCellData().GetArray(field_name))
    ncells = surf.GetNumberOfCells()
    total_area = 0.0
    total_weighted = 0.0
    for i in range(ncells):
        cell = surf.GetCell(i)
        pids = [cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())]
        p0, p1, p2 = [np.array(surf.GetPoint(pid)) for pid in pids[:3]]
        a = 0.5 * np.linalg.norm(np.cross(p1 - p0, p2 - p0))
        if is_point_data:
            val = np.mean([arr[pid] if arr.ndim == 1 else arr[pid] for pid in pids])
        else:
            val = arr[i]
        total_area += a
        total_weighted += a * val
    return total_weighted / total_area, total_area

T_floor, A_floor = area_weighted_avg(read_patch(f"{CASE}/VTK/case_hc1.2_908/boundary/floor.vtp"), "T")
T_pins, A_pins = area_weighted_avg(read_patch(f"{CASE}/VTK/case_hc1.2_908/boundary/pins.vtp"), "T")
T_outlet, A_outlet = area_weighted_avg(read_patch(f"{CASE}/VTK/case_hc1.2_908/boundary/outlet.vtp"), "T")
p_inlet, A_inlet = area_weighted_avg(read_patch(f"{CASE}/VTK/case_hc1.2_213/boundary/inlet.vtp"), "p", is_point_data=False)
p_outlet, _ = area_weighted_avg(read_patch(f"{CASE}/VTK/case_hc1.2_213/boundary/outlet.vtp"), "p", is_point_data=False)

T_wall_avg = (T_floor * A_floor + T_pins * A_pins) / (A_floor + A_pins)
T_in = 298.15
T_f_ave = (T_in + T_outlet) / 2.0

# --- fluid properties (standard water at 25 C, not printed in the source paper) ---
rho = 997.0
mu = 8.90e-4
kf = 0.606
cp = 4182.0
Pr = mu * cp / kf

# --- geometry (Mei et al. Table 1, hc/hf = 1.2) ---
Df = 1.0e-3
hf = 1.0e-3
hc = 1.2e-3
ST = 1.8e-3
SL = 1.8e-3
N_L = 15          # rows actually modelled (paper uses 50; see caveats in the writeup)
u_in = 0.05       # m/s, chosen inlet velocity

# u_max and Re exactly as defined in the paper (Eqs. 9-11): purely geometric from u_in, not from
# the CFD velocity field.
Amin_over_period = ST * hc - Df * hf       # per full pitch
Ain_over_period = ST * hc
u_max = u_in * Ain_over_period / Amin_over_period
Re = rho * u_max * Df / mu

q = 1000.0  # W/m2, the flux value used in the BC (Nu is independent of this choice, see 0/T)
h_ave = q / (T_wall_avg - T_f_ave)
Nu_ave = h_ave * Df / kf

dP = p_inlet - p_outlet  # p already kinematic (p/rho) in incompressible solver: convert
dP_static = dP * rho     # Pa
f = dP_static / (N_L * (rho * u_max**2 / 2))

# --- Mei et al. correlations (Eqs. 20, 23) -- NEGATIVE exponents on (hc/hf): confirmed by
# rendering p.714-715 of the source PDF as images, since plain-text extraction silently drops
# superscript minus signs (Nu = 0.75*(hc/hf)^-1.41*Re^0.51*Pr^1/3; f = 42.27*(hc/hf)^-1.64*Re^-0.75)
hc_hf = hc / hf
Nu_corr = 0.75 * hc_hf**(-1.41) * Re**0.51 * Pr**(1/3)
f_corr = 42.27 * hc_hf**(-1.64) * Re**(-0.75)

print(f"T_floor (area-avg)   = {T_floor:.4f} K, area = {A_floor*1e6:.4f} mm2")
print(f"T_pins  (area-avg)   = {T_pins:.4f} K, area = {A_pins*1e6:.4f} mm2")
print(f"T_wall combined      = {T_wall_avg:.4f} K")
print(f"T_outlet (bulk)      = {T_outlet:.4f} K")
print(f"T_f,ave (Eq. 29)     = {T_f_ave:.4f} K")
print(f"p_inlet (kinematic)  = {p_inlet:.6e} m2/s2   p_outlet = {p_outlet:.6e} m2/s2")
print(f"dP (static)          = {dP_static:.4f} Pa")
print()
print(f"u_in = {u_in} m/s -> u_max = {u_max:.6f} m/s -> Re (Eq. 11) = {Re:.2f}")
print(f"Pr = {Pr:.3f}")
print()
print(f"CFD  Nu_ave = {Nu_ave:.3f}   |  Eq.(20) predicted Nu = {Nu_corr:.3f}   |  diff = {100*(Nu_ave-Nu_corr)/Nu_corr:+.1f}%")
print(f"CFD  f      = {f:.2f}       |  Eq.(23) predicted f  = {f_corr:.2f}     |  diff = {100*(f-f_corr)/f_corr:+.1f}%")
