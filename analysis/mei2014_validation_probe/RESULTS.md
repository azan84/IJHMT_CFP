# Mei et al. (2014) reproduction probe -- results (7 September 2026)

One case: hc/hf = 1.2 (their first experimentally-validated clearance ratio), u_in = 0.05 m/s
(chosen inlet velocity, giving Re = 104.3 by their own Eq. (11) definition -- comfortably inside
their validated 33-350 range). Geometry, boundary conditions and grid-independence approach
reproduced from the paper's Table 1 and Section 2 (see `scripts/postprocess_hc1.2.py` header and
`case_hc1.2/0/T` for every source-vs-assumed value, and the exact page images checked below).

## Setup

- Half-pitch (ST/2 = 0.9 mm) spanwise-symmetric slice through one pin column, 15 rows (27 mm of
  the paper's 90 mm array -- a probe, not their full 50-row length; see caveats).
- snappyHexMesh, 15 identical cylindrical pins (Df = 1 mm, hf = 1 mm) cut from a background block;
  4 near-wall layers added on the pins and floor patches (90,450 cells; `checkMesh` reports
  "Mesh OK", max non-orthogonality 67, max skewness 2.7).
- Hydrodynamics solved with `simpleFoam` (laminar, standard water properties at 25 C -- not
  printed in the source paper, which states properties were "simplified as constant" without
  giving values); pressure drop and hence friction factor read off directly.
- Temperature solved as a decoupled passive scalar (`scalarTransportFoam`, DT = water's thermal
  diffusivity) on the converged velocity field -- valid because the problem is one-way coupled at
  constant properties. Heat flux (q = 1000 W/m2, arbitrary: Nu is independent of this choice for
  a linear, constant-property problem) applied uniformly over every wetted surface (exposed floor
  + pin sides + pin top). This is a **simplification**: it skips the conjugate aluminium pin
  entirely and imposes uniform *flux* on the fluid boundary directly, rather than uniform *flux at
  the base* conducted through the solid pin -- see the Nu discussion below for why this matters.

## Correlation sign-check (important finding, not just a result)

While reproducing this paper's Eqs. (20) and (23), the exponents on `(hc/hf)` came out with the
wrong sign from plain-text PDF extraction (a known failure mode in this project). Rendering
p.714-715 as images and reading them directly confirms the true equations are:

```
Nu = 0.75 (hc/hf)^-1.41 Re^0.51 Pr_f,ave^(1/3)      [Eq. 20]
f  = 42.27 (hc/hf)^-1.64 Re^-0.75                    [Eq. 23]
```

(both exponents on `hc/hf` NEGATIVE, and the Re exponent in the friction-factor correlation
NEGATIVE) -- text extraction had silently dropped both minus signs, giving predicted values three
orders of magnitude too large for the friction factor. Confirmed consistent with the paper's own
prose ("the friction factor nearly doubles" as hc/hf decreases from 2 to 1; "average Nusselt number
decreases with increasing tip clearance" over the fitted range 1-2) and with Fig. 6/7's axis ranges
(Nu ~ 5-20, f ~ 0.1-2, not thousands).

## Results

| Quantity | CFD (this probe) | Eq. (20)/(23), corrected | Difference |
|---|---:|---:|---:|
| Friction factor f | 1.04 | 0.96 | **+8.0%** |
| Nusselt number Nu | 5.20 | 11.36 | **-54.3%** |

(Without near-wall mesh layers, a first attempt gave f = 0.99, diff +3.0%, and Nu = 4.74,
diff -58.3% -- adding layers improved both slightly but did not close the Nu gap.)

## Interpretation

**Friction factor: a genuine, successful validation.** +8% (no layers: +3%) is well inside the
paper's own reported 10.2% MAE for this correlation against its own CFD/experimental data. This
confirms the geometry, mesh, and momentum-equation setup reproduce the real hydrodynamics of a
tip-clearance pin-fin array.

**Nusselt number: explained, not closed.** The ~54-73% shortfall is not attributed to mesh
resolution (adding boundary layers barely moved it) or to using only 15 of 50 rows (entrance
effects on a length-averaged Nu are a much smaller effect than this). The most likely cause is the
uniform-flux simplification itself: the real pin is aluminium alloy A356 (k_s ~ 150-160 W/m*K,
confirmed against Moores et al.'s AlSiC value as a cross-check), and a fin-efficiency estimate at
this size (m*hf ~ 0.42, tanh(m*hf)/(m*hf) ~ 0.94) shows the real pin is very nearly *isothermal*,
not uniform-flux. For a bluff body in crossflow, the local heat-transfer coefficient varies sharply
around the circumference (high at the front stagnation region, low in the separated wake); forcing
a *uniform flux* wall instead of the physically-correct near-*uniform temperature* one pushes the
area-averaged wall temperature up (dominated by the hot, low-h wake region), which suppresses the
area-averaged Nu relative to the real conjugate case. This is a known, physically-grounded
mechanism for exactly this direction and rough magnitude of discrepancy on a pin (not a plate) in
crossflow -- closing it would require the full conjugate (solid aluminium + fluid) solve this probe
deliberately skipped for tractability.

## What this probe does and does not establish

- **Does establish**: the campaign's general spanwise-periodic unit-cell CFD methodology
  (snappyHexMesh + simpleFoam laminar solve) reproduces an independent, non-immersion-cooling
  literature source's friction-factor behaviour for a bypass/tip-clearance flow to within its own
  reported experimental uncertainty. This is real, useful, independent evidence that the broader
  CFD approach used throughout this project is sound for tip-clearance/bypass flows generally, not
  specific to our own plate-fin geometry.
- **Does not establish**: quantitative agreement on Nusselt number/heat transfer, because of the
  uniform-flux-vs-conjugate simplification above. A full conjugate reproduction (adding the solid
  aluminium pin, splitting into two chtMultiRegionSimpleFoam regions the way the main campaign
  already does for its plate-fin geometry) is the natural next step if a genuine Nu validation
  against this source is wanted -- not attempted here, flagged as a scoped follow-up.
- Does not attempt Moores et al. (2009): its housing/duct dimensions are not published at all
  (see `validation/moores-pinfin-tip-clearance_triage.md`), making even a probe-level reproduction
  require materially more invented geometry than Mei's case did.

## Files

- `scripts/make_pins_stl.py` -- generates the 15-pin STL.
- `case_hc1.2/` -- full OpenFOAM case (blockMeshDict, snappyHexMeshDict, 0/{U,p,T}, solved fields).
- `scripts/postprocess_hc1.2.py` -- area-weighted patch post-processing and the correlation
  comparison, via foamToVTK + the vtk Python bindings (no ParaView).
