#!/usr/bin/env python3
"""Spanwise-periodic conjugate unit-cell case builder for the calibration campaign (revision round 3).
Geometry: manuscript Sec. 2.3 and Table 1b (s = 0.95 mm, t_f = 0.25 mm, H_base = 4.5 mm, H_chassis = 44.45 mm,
H_fin(OR) = (H_chassis - H_base)(1 - OR), L_sink = 118 mm; plena 60 mm / 80 mm). Half-pitch slice between two
symmetry planes: half channel (s/2) + half fin (t_f/2). Regions: fluid (channel + clearance + plena) and solid
(base + fin). Heat flux on the base underside over the sink footprint: P_sink / (0.140 x 0.118) W/m2.
Fluids: manuscript Table 3 (FC-40: Chun et al. fits, temperature dependent; EFL-1: Huang et al. Table 2 values).
Solver settings: manuscript Sec. 3.5 "calibration campaign as specified". This file only writes cases; running is
done by run_campaign.sh. Every number written here is traceable to the manuscript tables or to this file."""
import os, math, json, subprocess, shutil

# --- fixed geometry (manuscript Table 1b / Sec. 2.3) ---
S=0.95e-3; TF=0.25e-3; HB=4.5e-3; HC=44.45e-3; L=0.118; LIN=0.060; LOUT=0.080
W_SPAN=0.140; NFIN_SPAN=117   # 140 mm span at 1.2 mm pitch (Table 1b): 117 fins, 116 channels
GRIDS={"coarse":dict(ny_ch=3,ny_fin=1,nz_base=4,nz_fin=24,nz_cl=8,nx_in=20,nx_sink=60,nx_out=25),
       "medium":dict(ny_ch=5,ny_fin=2,nz_base=6,nz_fin=40,nz_cl=12,nx_in=30,nx_sink=100,nx_out=40),
       "fine":dict(ny_ch=8,ny_fin=3,nz_base=9,nz_fin=64,nz_cl=18,nx_in=45,nx_sink=160,nx_out=60)}

# --- fluids (manuscript Table 3; T in kelvin) ---
def fc40(T):   # Chun et al. 2026, Table 3, p. 7 (fits); rho, mu, k, cp
    return dict(rho=2499-2.16*T, mu=0.0429-0.162e-3*T+1.08e-7*T**2, k=0.086-6.90e-5*T, cp=590+1.55*T)
def quad_fit(xs,ys):   # exact quadratic through three points (for the EFL-1 tabulated k and mu at 20, 40, 60 C): Lagrange form,
    # plain IEEE-double arithmetic in a fixed order so that every machine produces the same bits (numpy.polyfit did not)
    (x0,x1,x2),(y0,y1,y2)=xs,ys
    return lambda T: y0*((T-x1)*(T-x2))/((x0-x1)*(x0-x2))+y1*((T-x0)*(T-x2))/((x1-x0)*(x1-x2))+y2*((T-x0)*(T-x1))/((x2-x0)*(x2-x1))
EFL1_T=[293.15,313.15,333.15]; EFL1_MU=[6.31e-3,2.77e-3,1.72e-3]; EFL1_K=[0.062,0.068,0.072]   # Huang et al. 2024, Table 2
EFL1_RHO=1889.0; EFL1_CP=1165.0                                                                # Huang et al. 2024, Table 2 (single values)
def efl1(T):
    mu=quad_fit(EFL1_T,EFL1_MU)(T); k=quad_fit(EFL1_T,EFL1_K)(T)
    return dict(rho=EFL1_RHO,mu=float(mu),k=float(k),cp=EFL1_CP)
FLUIDS={"FC-40":fc40,"EFL-1":efl1}
SOLID=dict(rho=8978.0,cp=381.0,k=387.6)   # copper, Chun et al. Table 2, p. 6 (manuscript solid-property table)
T_IN=298.15; G=(-9.81,0.0,0.0)   # inlet 25 C (manuscript Table 1b); gravity along -x with the flow vertical upward (T-configuration, Sec. 3.3); an assumption recorded in campaign_design.json

def of_prefix():
    """Shell prefix that provides the OpenFOAM environment: none when the tools are already in PATH, otherwise
    'source <bashrc>; ' from OPENFOAM_BASHRC (exported by remote_run.py after detection) or the usual install paths."""
    import shutil as _sh
    if _sh.which("chtMultiRegionSimpleFoam"): return ""
    cands=[os.environ.get("OPENFOAM_BASHRC","")]+["/usr/lib/openfoam/openfoam2406/etc/bashrc","/opt/openfoam2406/etc/bashrc","/opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc",os.path.expanduser("~/OpenFOAM/OpenFOAM-v2406/etc/bashrc")]
    for b in cands:
        if b and os.path.exists(b): return "source %s >/dev/null 2>&1; "%b
    raise RuntimeError("OpenFOAM v2406 not found: put its tools in PATH or set OPENFOAM_BASHRC to its etc/bashrc")

def geometry(OR=None,Hfin=None,Hc=HC):
    if Hfin is None: Hfin=(Hc-HB)*(1-OR)
    c=Hc-HB-Hfin
    if Hfin>1e-9: Dh=2*S*Hfin/(S+Hfin); Ach_half=(S/2)*Hfin
    else: Dh=2*S*(Hc-HB)/(S+Hc-HB); Ach_half=(S/2)*(Hc-HB)   # OR = 1 convention (manuscript Sec. 6.3): no channel exists, so the bare duct receives the flow rate of the sealed (OR = 0) case with the same Re_ch label; D_h and A_ch of that sealed case index the case
    return dict(Hfin=Hfin,c=c,Dh=Dh,Ach_half=Ach_half,Ain_half=((S+TF)/2)*(Hc-HB),Hc=Hc,
                A_wetted_full=2*NFIN_SPAN*Hfin*L+(W_SPAN-NFIN_SPAN*TF)*L)   # manuscript Eq. (A_wetted)

def inlet_velocity(Re_ch,fluid,g):
    p=FLUIDS[fluid](T_IN); nu=p["mu"]/p["rho"]
    u_ch=Re_ch*nu/g["Dh"]; Q_half=u_ch*g["Ach_half"]; u_in=Q_half/g["Ain_half"]
    return dict(nu_in=nu,u_ch=u_ch,Q_half=Q_half,u_in=u_in,Q_full_sink_LPM=Q_half*2*NFIN_SPAN*60000)

def write_blockmesh(case,g,grid):
    N=dict(GRIDS[grid]); Hfin=g["Hfin"]; Hc=g["Hc"]
    # (OR = 1: the HB..Hc layer takes the fin-layer resolution; see the layer classifier below)
    xs=[-LIN,0.0,L,L+LOUT]; ys=[0.0,S/2,(S+TF)/2]
    zs=sorted(set([0.0,HB]+([HB+Hfin] if Hfin>1e-9 else [])+[Hc]))
    V=[];idx={}
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            for k,z in enumerate(zs): idx[(i,j,k)]=len(V); V.append((x,y,z))
    nx=[N["nx_in"],N["nx_sink"],N["nx_out"]]; ny=[N["ny_ch"],N["ny_fin"]]
    zl=[]
    for k in range(len(zs)-1):
        lo=zs[k]
        if abs(lo)<1e-12: zl.append(("base",N["nz_base"]))
        elif Hfin>1e-9 and abs(lo-HB)<1e-12: zl.append(("fin",N["nz_fin"]))
        elif Hfin<=1e-9 and abs(lo-HB)<1e-12: zl.append(("clear",N["nz_fin"]))   # OR = 1: the full channel height is resolved like the fin layer (set-up audit, blocking item 2)
        else: zl.append(("clear",N["nz_cl"]))
    blocks=[]
    for i in range(3):
        for j in range(2):
            for k,(zn,nz) in enumerate(zl):
                ins=(i==1)
                if zn=="base": zone="solid" if ins else None
                elif zn=="fin": zone="solid" if (j==1 and ins) else "fluid"
                else: zone="fluid"
                if zone is None: continue
                v=[idx[(i,j,k)],idx[(i+1,j,k)],idx[(i+1,j+1,k)],idx[(i,j+1,k)],idx[(i,j,k+1)],idx[(i+1,j,k+1)],idx[(i+1,j+1,k+1)],idx[(i,j+1,k+1)]]
                blocks.append("    hex (%s) %s (%d %d %d) simpleGrading (1 1 1)"%(" ".join(map(str,v)),zone,nx[i],ny[j],nz))
    def face(a,b,c,d): return "(%d %d %d %d)"%(idx[a],idx[b],idx[c],idx[d])
    kb=[k for k,(zn,_) in enumerate(zl) if zn=="base"][0]; kfl=[k for k,(zn,_) in enumerate(zl) if zn!="base"]; nzl=len(zl); nzs=len(zs)
    inlet=[face((0,j,k),(0,j+1,k),(0,j+1,k+1),(0,j,k+1)) for j in range(2) for k in kfl]
    outlet=[face((3,j,k),(3,j+1,k),(3,j+1,k+1),(3,j,k+1)) for j in range(2) for k in kfl]
    top=[face((i,j,nzs-1),(i+1,j,nzs-1),(i+1,j+1,nzs-1),(i,j+1,nzs-1)) for i in range(3) for j in range(2)]
    symA=[face((i,0,k),(i+1,0,k),(i+1,0,k+1),(i,0,k+1)) for i in range(3) for k in range(nzl) if not (zl[k][0]=="base" and i!=1)]
    symB=[face((i,2,k),(i+1,2,k),(i+1,2,k+1),(i,2,k+1)) for i in range(3) for k in range(nzl) if not (zl[k][0]=="base" and i!=1)]
    floor=[face((i,j,kb+1),(i+1,j,kb+1),(i+1,j+1,kb+1),(i,j+1,kb+1)) for i in (0,2) for j in range(2)]
    heated=[face((1,j,0),(2,j,0),(2,j+1,0),(1,j+1,0)) for j in range(2)]
    sides=[]
    for j in range(2):
        sides.append(face((1,j,kb),(1,j+1,kb),(1,j+1,kb+1),(1,j,kb+1))); sides.append(face((2,j,kb),(2,j+1,kb),(2,j+1,kb+1),(2,j,kb+1)))
    def patch(n,t,fs): return "    %s { type %s; faces ( %s ); }\n"%(n,t,"\n        ".join(fs))
    s="FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }\nscale 1;\nvertices\n(\n"+"\n".join("    (%.7e %.7e %.7e)"%v for v in V)+"\n);\nblocks\n(\n"+"\n".join(blocks)+"\n);\nedges ();\nboundary\n(\n"
    s+=patch("inlet","patch",inlet)+patch("outlet","patch",outlet)+patch("topWall","wall",top)+patch("symChannel","symmetryPlane",symA)+patch("symFin","symmetryPlane",symB)+patch("floor","wall",floor)+patch("heated","wall",heated)+patch("baseSides","wall",sides)+");\nmergePatchPairs ();\n"
    open(os.path.join(case,"system/blockMeshDict"),"w").write(s)

H='FoamFile { version 2.0; format ascii; class dictionary; object %s; }\n'
def coeffs8(c): c=list(c)+[0.0]*(8-len(c)); return "("+" ".join("%.10g"%x for x in c)+")"
def fluid_tables(fluid):
    """Property tables (T, value) over the validity band of the source: FC-40 = Chun fits sampled at 20 to 60 C
    (Table 3: viscosity fit valid 20-60 C); EFL-1 = Huang Table 2 printed points at 20, 40, 60 C. OpenFOAM's
    tabulated thermo interpolates linearly and clamps outside the table, which is the manuscript's 'restricted
    to its validity band' (Sec. 3.3)."""
    if fluid=="FC-40":
        Ts=[293.15+10*i for i in range(5)]; P=[fc40(T) for T in Ts]
        return dict(T=Ts,rho=[q["rho"] for q in P],cp=[q["cp"] for q in P],mu=[q["mu"] for q in P],k=[q["k"] for q in P])
    return dict(T=EFL1_T,rho=[EFL1_RHO]*3,cp=[EFL1_CP]*3,mu=EFL1_MU,k=EFL1_K)
def tab(Ts,vals): return "( "+" ".join("(%.6g %.8g)"%(T,v) for T,v in zip(Ts,vals))+" )"
def write_thermo(case,fluid):
    tb=fluid_tables(fluid)
    trans="transport { mu %s; kappa %s; }"%(tab(tb["T"],tb["mu"]),tab(tb["T"],tb["k"]))
    thermo="thermodynamics { Hf 0; Sf 0; Cp %s; }"%tab(tb["T"],tb["cp"]); eos="equationOfState { rho %s; }"%tab(tb["T"],tb["rho"])
    open(os.path.join(case,"constant/fluid/thermophysicalProperties"),"w").write(H%"thermophysicalProperties"+"thermoType { type heRhoThermo; mixture pureMixture; transport tabulated; thermo hTabulated; equationOfState icoTabulated; specie specie; energy sensibleEnthalpy; }\nmixture\n{\n    specie { molWeight 650; }\n    %s\n    %s\n    %s\n}\n"%(eos,thermo,trans))
    open(os.path.join(case,"constant/fluid/turbulenceProperties"),"w").write(H%"turbulenceProperties"+"simulationType laminar;\n")
    for r in ("fluid","solid"): open(os.path.join(case,"constant/%s/radiationProperties"%r),"w").write(H%"radiationProperties"+"radiationModel none;\n")
    open(os.path.join(case,"constant/solid/thermophysicalProperties"),"w").write(H%"thermophysicalProperties"+"thermoType { type heSolidThermo; mixture pureMixture; transport constIso; thermo hConst; equationOfState rhoConst; specie specie; energy sensibleEnthalpy; }\nmixture\n{\n    specie { molWeight 63.546; }\n    equationOfState { rho %g; }\n    thermodynamics { Cp %g; Hf 0; }\n    transport { kappa %g; }\n}\n"%(SOLID["rho"],SOLID["cp"],SOLID["k"]))
    open(os.path.join(case,"constant/regionProperties"),"w").write(H%"regionProperties"+"regions ( fluid ( fluid ) solid ( solid ) );\n")
    open(os.path.join(case,"constant/g"),"w").write("FoamFile { version 2.0; format ascii; class uniformDimensionedVectorField; object g; }\ndimensions [0 1 -2 0 0 0 0];\nvalue (%g %g %g);\n"%G)

def write_fields(case,u_in,q):
    fl=os.path.join(case,"0/fluid"); so=os.path.join(case,"0/solid"); os.makedirs(fl,exist_ok=True); os.makedirs(so,exist_ok=True)
    F='FoamFile { version 2.0; format ascii; class %s; object %s; }\n'
    open(fl+"/T","w").write(F%("volScalarField","T")+"dimensions [0 0 0 1 0 0 0];\ninternalField uniform %g;\nboundaryField\n{\n    #includeEtc \"caseDicts/setConstraintTypes\"\n    inlet { type fixedValue; value uniform %g; }\n    outlet { type inletOutlet; inletValue uniform %g; value uniform %g; }\n    \"(topWall|floor)\" { type zeroGradient; }\n    fluid_to_solid { type compressible::turbulentTemperatureCoupledBaffleMixed; Tnbr T; kappaMethod fluidThermo; value uniform %g; }\n}\n"%((T_IN,)*5))
    open(fl+"/U","w").write(F%("volVectorField","U")+"dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (%g 0 0);\nboundaryField\n{\n    #includeEtc \"caseDicts/setConstraintTypes\"\n    inlet { type fixedValue; value uniform (%g 0 0); }\n    outlet { type inletOutlet; inletValue uniform (0 0 0); value uniform (%g 0 0); }\n    \"(topWall|floor|fluid_to_solid)\" { type noSlip; }\n}\n"%((u_in,)*3))
    open(fl+"/p","w").write(F%("volScalarField","p")+"dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 1e5;\nboundaryField\n{\n    #includeEtc \"caseDicts/setConstraintTypes\"\n    \"(inlet|outlet|topWall|floor|fluid_to_solid)\" { type calculated; value uniform 1e5; }\n}\n")
    open(fl+"/p_rgh","w").write(F%("volScalarField","p_rgh")+"dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 1e5;\nboundaryField\n{\n    #includeEtc \"caseDicts/setConstraintTypes\"\n    outlet { type fixedValue; value uniform 1e5; }\n    \"(inlet|topWall|floor|fluid_to_solid)\" { type fixedFluxPressure; value uniform 1e5; }\n}\n")
    open(so+"/T","w").write(F%("volScalarField","T")+"dimensions [0 0 0 1 0 0 0];\ninternalField uniform %g;\nboundaryField\n{\n    #includeEtc \"caseDicts/setConstraintTypes\"\n    heated { type externalWallHeatFluxTemperature; kappaMethod solidThermo; mode flux; q uniform %.6g; value uniform %g; }\n    \"(topWall|baseSides)\" { type zeroGradient; }\n    solid_to_fluid { type compressible::turbulentTemperatureCoupledBaffleMixed; Tnbr T; kappaMethod solidThermo; value uniform %g; }\n}\n"%(T_IN,q,T_IN,T_IN))
    open(so+"/p","w").write(F%("volScalarField","p")+"dimensions [1 -1 -2 0 0 0 0];\ninternalField uniform 1e5;\nboundaryField\n{\n    #includeEtc \"caseDicts/setConstraintTypes\"\n    \"(heated|topWall|baseSides|solid_to_fluid)\" { type calculated; value uniform 1e5; }\n}\n")

def write_system(case,g,nsub=8):
    sy=os.path.join(case,"system")
    for r in ("fluid","solid"): os.makedirs(os.path.join(sy,r),exist_ok=True)
    zt=HB+g["Hfin"]; eps=1e-6
    # monitors: manuscript Sec. 3.5 (base temperature, pressure drop, bypass fraction, energy balance) and Sec. 4.4 (mass split)
    def sfv(name,reg,rtype,nm,op,fields,extra=""):
        return "    %s { type surfaceFieldValue; libs (fieldFunctionObjects); region %s; regionType %s; name %s; operation %s; fields (%s); %s writeFields false; log false; writeControl timeStep; writeInterval 25; }\n"%(name,reg,rtype,nm,op,fields,extra)
    fo="functions\n{\n"
    fo+=sfv("inletP","fluid","patch","inlet","areaAverage","p p_rgh")+sfv("outletP","fluid","patch","outlet","areaAverage","p p_rgh")   # p_rgh = p minus the hydrostatic column: the pressure drop uses p_rgh
    fo+=sfv("inletPhi","fluid","patch","inlet","sum","phi")+sfv("outletPhi","fluid","patch","outlet","sum","phi")
    fo+=sfv("inletH","fluid","patch","inlet","weightedSum","h","weightField phi;")+sfv("outletH","fluid","patch","outlet","weightedSum","h","weightField phi;")
    fo+=sfv("outletTbulk","fluid","patch","outlet","weightedAverage","T","weightField phi;")
    zones=[z for z in ("chanIn","clearIn","chanMid","clearMid") if not ((z.startswith("clear") and g["c"]<=1e-9) or (z.startswith("chan") and g["Hfin"]<=1e-9))]   # a zone with no faces (OR = 0 clearance, OR = 1 channel) cannot be monitored
    for z in zones: fo+=sfv(z+"Phi","fluid","faceZone",z,"sum","phi")
    fo+=sfv("ifaceT","fluid","patch","fluid_to_solid","areaAverage","T")+sfv("ifaceTmax","fluid","patch","fluid_to_solid","max","T")
    fo+=sfv("heatedT","solid","patch","heated","areaAverage","T")+sfv("heatedTmax","solid","patch","heated","max","T")
    fo+="    whfFluid { type wallHeatFlux; libs (fieldFunctionObjects); region fluid; patches (fluid_to_solid); writeFields false; log false; writeControl timeStep; writeInterval 25; }\n"
    fo+="    whfSolid { type wallHeatFlux; libs (fieldFunctionObjects); region solid; patches (heated solid_to_fluid); writeFields false; log false; writeControl timeStep; writeInterval 25; }\n"
    fo+="    residuals { type solverInfo; libs (utilityFunctionObjects); region fluid; fields (p_rgh U h); writeControl timeStep; writeInterval 25; }\n}\n"   # convergence stop: run_campaign.sh watchdog (reads this monitor; stops via stopAt writeNow)
    open(sy+"/controlDict","w").write(H%"controlDict"+"application chtMultiRegionSimpleFoam;\nstartFrom latestTime;\nstartTime 0;\nstopAt endTime;\nendTime 12000;\ndeltaT 1;\nwriteControl timeStep;\nwriteInterval 1000;\npurgeWrite 1;\nwriteFormat binary;\nwritePrecision 8;\nrunTimeModifiable true;\n"+fo)
    dp=H%"decomposeParDict"+"numberOfSubdomains %d;\nmethod scotch;\n"%nsub
    for r in ("","fluid/","solid/"): open(sy+"/"+r+"decomposeParDict","w").write(dp)
    open(sy+"/fvSolution","w").write(H%"fvSolution"+"PIMPLE { nOuterCorrectors 1; }\n")
    open(sy+"/fvSchemes","w").write(H%"fvSchemes"+"ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; }\ndivSchemes { default none; }\nlaplacianSchemes { default Gauss linear corrected; }\ninterpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n")
    open(sy+"/fluid/fvSchemes","w").write(H%"fvSchemes"+"ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; limited cellLimited Gauss linear 1; }\ndivSchemes\n{\n    default none;\n    div(phi,U) bounded Gauss linearUpwind grad(U);\n    div(phi,h) bounded Gauss linearUpwind limited;\n    div(phi,K) bounded Gauss linear;\n    div(phi,e) bounded Gauss linearUpwind limited;\n    div(phi,Ekp) bounded Gauss linear;\n    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;\n}\nlaplacianSchemes { default Gauss linear corrected; }\ninterpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n")
    # manuscript Sec. 3.5: GAMG on pressure, smooth solvers on momentum and energy, relaxation p 0.3 / U 0.7 / h 0.9, residual targets below 1e-4 (continuity, momentum) and 1e-6 (energy); tighter targets here so that the integral monitors are stationary
    open(sy+"/fluid/fvSolution","w").write(H%"fvSolution"+"solvers\n{\n    rho { solver PCG; preconditioner DIC; tolerance 1e-8; relTol 0; }\n    p_rgh { solver GAMG; smoother GaussSeidel; tolerance 1e-9; relTol 0.01; maxIter 200; }\n    \"(U|h)\" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-9; relTol 0.1; nSweeps 2; }\n}\nSIMPLE\n{\n    momentumPredictor yes;\n    nNonOrthogonalCorrectors 0;\n    residualControl { p_rgh 1e-5; U 1e-5; h 1e-6; }\n}\nrelaxationFactors\n{\n    fields { rho 1; p_rgh 0.3; }\n    equations { U 0.7; h 0.9; }\n}\n")
    open(sy+"/solid/fvSchemes","w").write(H%"fvSchemes"+"ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; }\ndivSchemes { default none; }\nlaplacianSchemes { default Gauss linear corrected; }\ninterpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n")
    open(sy+"/solid/fvSolution","w").write(H%"fvSolution"+"solvers { h { solver PCG; preconditioner DIC; tolerance 1e-9; relTol 0.1; } }\nSIMPLE { nNonOrthogonalCorrectors 0; residualControl { h 1e-6; } }\nrelaxationFactors { equations { h 1; } }\n")
    # face zones for the mass split (manuscript Sec. 4.4): sink leading edge x = 0 and mid-sink x = L/2, below (channel) and above (clearance) the fin-tip plane
    def box(x,zlo,zhi): return "(%.7g -1 %.7g) (%.7g 1 %.7g)"%(x-eps,zlo,x+eps,zhi)
    ts="actions\n(\n"
    for nm_,x in (("In",0.0),("Mid",L/2)):
        ts+="    { name chan%sSet; type faceSet; action new; source boxToFace; box %s; }\n    { name chan%s; type faceZoneSet; action new; source setToFaceZone; faceSet chan%sSet; }\n"%(nm_,box(x,HB-eps,zt+eps if g['Hfin']>1e-9 else HB+eps),nm_,nm_)
        ts+="    { name clear%sSet; type faceSet; action new; source boxToFace; box %s; }\n    { name clear%s; type faceZoneSet; action new; source setToFaceZone; faceSet clear%sSet; }\n"%(nm_,box(x,(zt+eps) if g['Hfin']>1e-9 else HB+eps,g["Hc"]+1e-3),nm_,nm_)
    ts+=");\n"
    open(sy+"/fluid/topoSetDict","w").write(H%"topoSetDict"+ts)

def build(case,fluid,OR=None,Hfin=None,Hc=HC,Re_ch=40.0,P_W=700.0,grid="medium",run_mesh=True,log=print,gravity=True):
    global G
    G=(-9.81,0.0,0.0) if gravity else (0.0,0.0,0.0)   # gravity switch: the campaign decision on buoyancy is recorded in audit/decisions.md
    os.makedirs(case,exist_ok=True)
    for d in ("system","constant","constant/fluid","constant/solid","0"): os.makedirs(os.path.join(case,d),exist_ok=True)
    g=geometry(OR=OR,Hfin=Hfin,Hc=Hc); v=inlet_velocity(Re_ch,fluid,g); q=P_W/(W_SPAN*L)
    ORv=OR if OR is not None else 1-g["Hfin"]/(Hc-HB)
    write_blockmesh(case,g,grid); write_thermo(case,fluid); write_system(case,g); write_fields(case,v["u_in"],q)
    meta=dict(fluid=fluid,OR=ORv,Re_ch=Re_ch,P_sink_W=P_W,grid=grid,H_fin_m=g["Hfin"],clearance_m=g["c"],H_chassis_m=Hc,D_h_m=g["Dh"],A_ch_half_m2=g["Ach_half"],A_in_half_m2=g["Ain_half"],
              A_wetted_full_m2=g["A_wetted_full"],u_ch_m_s=v["u_ch"],u_in_m_s=v["u_in"],Q_half_m3_s=v["Q_half"],Q_full_sink_LPM=v["Q_full_sink_LPM"],nu_inlet_m2_s=v["nu_in"],
              q_base_W_m2=q,T_in_K=T_IN,g=G,props_inlet=FLUIDS[fluid](T_IN),solid=SOLID,
              notes="half-pitch slice (s/2 + t_f/2) with symmetry planes; Re_ch = u_ch D_h/nu(T_in) with all flow through the channel (u_in scaled by A_ch/A_in); A_wetted per manuscript Eq. for the 140 mm span")
    json.dump(meta,open(os.path.join(case,"case_meta.json"),"w"),indent=1)
    if run_mesh:
        env=dict(os.environ); 
        def run(cmd,logname):
            with open(os.path.join(case,logname),"w") as f: r=subprocess.run(of_prefix()+"cd %s && %s"%(case,cmd),shell=True,executable="/bin/bash",stdout=f,stderr=subprocess.STDOUT)
            if r.returncode!=0: raise RuntimeError("%s failed in %s (see %s)"%(cmd,case,logname))
        run("blockMesh","log.blockMesh"); run("checkMesh -allGeometry -allTopology","log.checkMesh")
        run("splitMeshRegions -cellZones -overwrite","log.splitMeshRegions"); run("topoSet -region fluid","log.topoSet")
        for f in ("0/cellToRegion","0/fluid/cellToRegion","0/solid/cellToRegion"):
            p=os.path.join(case,f); 
            if os.path.exists(p): os.remove(p)
        n=[l for l in open(os.path.join(case,"log.checkMesh")) if "cells:" in l]; meta["cells"]=int(n[0].split(":")[1]) if n else None
        zs=[l.strip() for l in open(os.path.join(case,"log.topoSet")) if "faceZone" in l and "Added" in l or "faces" in l.lower() and "Set" in l][:8]; meta["topoSet"]=zs
        json.dump(meta,open(os.path.join(case,"case_meta.json"),"w"),indent=1)
    return meta
