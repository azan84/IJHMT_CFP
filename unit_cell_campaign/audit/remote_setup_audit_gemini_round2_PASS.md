# Adversarial Audit Report: Remote Share of the Unit-Cell Calibration Campaign (Round 2)

**Audited Directory**: `/tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign`  
**Audit Specification**: [`audit/instructions_remote_setup_audit.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/audit/instructions_remote_setup_audit.md)  
**Prior Round Report**: [`audit/round1_report.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/audit/round1_report.md)  
**Mode**: Adversarial Auditor (Gemini 3.7 Flash; Read-Only)

---

## Part A: Set-Up Fidelity

### 1. `unit_cell.py` Source Verification and Calculations

- **`fvSolution` pressure solver settings (`maxIter 200` on `p_rgh`)**:
  - Located in [`unit_cell.py:162`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L162):
    ```openfoam
    p_rgh { solver GAMG; smoother GaussSeidel; tolerance 1e-9; relTol 0.01; maxIter 200; }
    ```
    Carried in `system/fluid/fvSolution`. Verified.

- **`controlDict` settings (`endTime 12000`, `runTimeModifiable true`)**:
  - Located in [`unit_cell.py:155`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L155):
    ```openfoam
    application chtMultiRegionSimpleFoam;
    startFrom latestTime;
    startTime 0;
    stopAt endTime;
    endTime 12000;
    deltaT 1;
    writeControl timeStep;
    writeInterval 1000;
    purgeWrite 1;
    writeFormat binary;
    writePrecision 8;
    runTimeModifiable true;
    ```
    Carries `endTime 12000;` and `runTimeModifiable true;`. Verified.

- **`topoSetDict` face zones and $z$-split at $H_B + H_{fin}$**:
  - Located in [`unit_cell.py:139,168-171`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L139):
    ```python
    zt = HB + g["Hfin"]; eps = 1e-6
    def box(x, zlo, zhi): return "(%.7g -1 %.7g) (%.7g 1 %.7g)" % (x - eps, zlo, x + eps, zhi)
    for nm_, x in (("In", 0.0), ("Mid", L / 2)):
        ts += "    { name chan%sSet; type faceSet; action new; source boxToFace; box %s; }\n    { name chan%s; type faceZoneSet; action new; source setToFaceZone; faceSet chan%sSet; }\n" % (nm_, box(x, HB - eps, zt + eps if g['Hfin'] > 1e-9 else HB + eps), nm_, nm_)
        ts += "    { name clear%sSet; type faceSet; action new; source boxToFace; box %s; }\n    { name clear%s; type faceZoneSet; action new; source setToFaceZone; faceSet clear%sSet; }\n" % (nm_, box(x, (zt + eps) if g['Hfin'] > 1e-9 else HB + eps, g["Hc"] + 1e-3), nm_, nm_)
    ```
    For $H_{fin} > 10^{-9}$ ($OR < 1$), `chanIn` and `chanMid` are bounded by $z \in [H_B - \epsilon, H_B + H_{fin} + \epsilon]$, and `clearIn` and `clearMid` are bounded by $z \in [H_B + H_{fin} + \epsilon, H_c + 10^{-3}]$. The split is located precisely at $H_B + H_{fin}$. For $OR = 1$ ($H_{fin} \le 10^{-9}$), `chanIn` and `chanMid` collapse to a zero-thickness box $[H_B - \epsilon, H_B + \epsilon]$ (containing 0 faces), while `clearIn` and `clearMid` span $[H_B + \epsilon, H_c + 10^{-3}]$, capturing the entire fluid channel. Verified.

- **Independent Recomputation of $H_{fin}(OR)$ and Velocities**:
  Given: $H_c = 44.45\text{ mm}$, $H_B = 4.5\text{ mm}$, $s = 0.95\text{ mm} = 0.00095\text{ m}$, $t_f = 0.25\text{ mm} = 0.00025\text{ m}$, $T_{in} = 298.15\text{ K}$.
  - Fluid properties at $T_{in} = 298.15\text{ K}$:
    - **FC-40** ([`unit_cell.py:20-21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L20-L21)):
      $$\rho = 2499 - 2.16(298.15) = 1854.996\text{ kg/m}^3$$
      $$\mu = 0.0429 - 0.162\times 10^{-3}(298.15) + 1.08\times 10^{-7}(298.15)^2 = 0.00420018963\text{ Pa}\cdot\text{s}$$
      $$\nu = \mu/\rho = 2.26425805\times 10^{-6}\text{ m}^2/\text{s}$$
      $$k = 0.06542765\text{ W/(m}\cdot\text{K)}, \quad c_p = 1052.1325\text{ J/(kg}\cdot\text{K)}$$
    - **EFL-1** ([`unit_cell.py:22-30`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L22-L30)):
      $$\rho = 1889.0\text{ kg/m}^3, \quad c_p = 1165.0\text{ J/(kg}\cdot\text{K)}$$
      Tabulated at $T = [293.15, 313.15, 333.15]\text{ K}$: $\mu = [6.31, 2.77, 1.72]\times 10^{-3}\text{ Pa}\cdot\text{s}$; $k = [0.062, 0.068, 0.072]\text{ W/(m}\cdot\text{K)}$.
      Quadratic fit polynomial evaluated at $298.15\text{ K}$:
      $$\mu = 0.0051915625\text{ Pa}\cdot\text{s} \implies \nu = \mu/\rho = 2.74831260\times 10^{-6}\text{ m}^2/\text{s}$$
      $$k = 0.06368750\text{ W/(m}\cdot\text{K)}$$
  
  - **Case 1: `C005` (FC-40, $OR = 0.0$, $Re_{ch} = 40$)**:
    - $H_{fin} = (44.45 - 4.5)(1 - 0.0) = 39.95\text{ mm} = 0.03995\text{ m}$
    - $D_h = \frac{2 s H_{fin}}{s + H_{fin}} = \frac{2(0.00095)(0.03995)}{0.00095 + 0.03995} = \frac{7.5905\times 10^{-5}}{0.04090} = 0.001855868\text{ m}$ ($1.855868\text{ mm}$)
    - $u_{ch} = \frac{Re_{ch}\nu}{D_h} = \frac{40(2.26425805\times 10^{-6})}{0.001855868} = 0.04880214\text{ m/s}$
    - With $u_{ch} = u_{in}\frac{s/2 + t_f/2}{s/2}$:
      $$u_{in} = u_{ch}\frac{s}{s + t_f} = 0.04880214\left(\frac{0.95}{1.20}\right) = 0.03863502\text{ m/s}$$
    - `build_cases.py` output: `H_fin_m: 0.03995`, `D_h_m: 0.001855868`, `u_ch_m_s: 0.04880214`, `u_in_m_s: 0.03863502`. Matches exactly.

  - **Case 2: `E002` (EFL-1, $OR = 0.0$, $Re_{ch} = 40$)**:
    - $H_{fin} = 39.95\text{ mm} = 0.03995\text{ m}$, $D_h = 0.001855868\text{ m}$
    - $u_{ch} = \frac{40(2.74831260\times 10^{-6})}{0.001855868} = 0.05923509\text{ m/s}$
    - $u_{in} = u_{ch}\frac{s}{s + t_f} = 0.05923509\left(\frac{0.95}{1.20}\right) = 0.04689445\text{ m/s}$
    - `build_cases.py` output: `H_fin_m: 0.03995`, `D_h_m: 0.001855868`, `u_ch_m_s: 0.05923509`, `u_in_m_s: 0.04689445`. Matches exactly.

- **Mesh Build and Manifest Comparison in Temporary Directory**:
  - A clean build of `C091` (FC-40, $OR = 1.0$), `E002` (EFL-1, $OR = 0.0$), `F001` ($c = 0$), and `F004` ($c = 19.05\text{ mm}$) was executed in an isolated workspace using `python3 build_cases.py <list> 1`.
  - All OpenFOAM utilities (`blockMesh`, `checkMesh`, `splitMeshRegions`, `topoSet`) succeeded without error.
  - Manifest verification via `python3 make_manifest.py check manifest_local_build.json <list>` passed with `0 with differences`.

---

### 2. `manifest_local_build.json` Verification

- **Case ID Coverage**:
  - `manifest_local_build.json` contains exactly 177 case IDs.
  - The key set maps 1-to-1 to the 177 cases defined in [`campaign_design.json`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/campaign_design.json) with zero missing or extra keys.

- **Audited Files vs Files Influencing the Solution**:
  - `make_manifest.py` checks 26 dictionaries and initial field files in `FILES` ([`make_manifest.py:8-13`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L8-L13)) and validates the grid topology through `checkMesh.cells` ([`make_manifest.py:24-26`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L24-L26)).
  - Files that influence the solution but are **not** explicitly listed in `FILES`:
    1. Binary mesh geometry files in `constant/fluid/polyMesh/` and `constant/solid/polyMesh/` (`points`, `faces`, `owner`, `neighbour`, `boundary`). As documented in [`make_manifest.py:3-5`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L3-L5), binary layouts vary between OpenFOAM binary distributions; determinism is guaranteed by hashing `system/blockMeshDict` and matching `checkMesh.cells`.
    2. `constant/cellToRegion` (created temporarily by `splitMeshRegions`, removed by [`unit_cell.py:194-196`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L194-L196)).
    3. `constant/fluid/polyMesh/faceZones` (generated by `topoSet`; its source dictionary `system/fluid/topoSetDict` is verified in `FILES`, and generated face zones are logged in `case_meta.json`).

- **Volatile Directives in `controlDict`**:
  - Evaluated in [`make_manifest.py:14-18`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L14-L18):
    ```python
    VOLATILE = re.compile(r"^(stopAt|endTime|startFrom)\s")
    def digest(path, volatile=False):
        data = open(path, "rb").read()
        if volatile: data = b"\n".join(l for l in data.split(b"\n") if not VOLATILE.match(l.decode("latin1")))
        return hashlib.sha256(data).hexdigest()
    ```
  - Directives `endTime`, `stopAt`, and `startFrom` occur at the line start in `system/controlDict` and are correctly matched and stripped when computing the SHA-256 digest of `system/controlDict`.

- **Documentation of the 4 Local Cases (`C003`, `C004`, `C005`, `C050`)**:
  - In `manifest_local_build.json`, exactly 4 cases (`C003`, `C004`, `C005`, `C050`) carry the pre-fix SHA-256 hash `77ca06ca440bb4f6f6e74058d293f7a80211d5386bd0125196c8ae5e651bc1f3` for `system/fluid/fvSolution` (without `maxIter 200`).
  - All other 173 cases (including all 87 remote cases in `run_list_remote.txt`) carry hash `2b05dc20eaba75aeac2f2540eb3fc848cb3ea2228d7855d79a5be66c758b1d89` (with `maxIter 200`).
  - In Round 2, this is explicitly explained in [`README.md:55-57`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L55-L57):
    > *"four local cases that had finished before the pressure-solver cap was added (C003, C004, C005, C050) are recorded without `maxIter 200`, as run. A remote build that does not match the manifest is refused."*
  - None of these 4 cases is in `run_list_remote.txt`; all remote cases match the builder.

---

### 3. `run_list_remote.txt` Disjointness and Completeness

- [`run_list_remote.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/run_list_remote.txt) contains exactly 87 unique case IDs:
  - $OR = 1.0$ calibration cases: `C091` to `C099` (9 cases)
  - EFL-1 $OR = 1.0$ cases: `E031` to `E033` (3 cases)
  - Thermal load $OR = 1.0$ cases: `L005`, `L010`, `L015`, `L020`, `L025` (5 cases)
  - Grid independence cases: `G001`, `G002` (2 cases)
  - EFL-1 holdout cases: `E001` to `E030` (30 cases)
  - Thermal load cases: `L001` to `L004`, `L006` to `L009`, `L011` to `L014`, `L016` to `L019`, `L021` to `L024` (20 cases)
  - Cross-combination cases: `X001` to `X014` (14 cases)
  - Fixed-fin clearance sweep: `F001` to `F004` (4 cases)
- **Local Share Disjointness**:
  - The local share consists of cases `C001` through `C090` (90 cases).
  - In Round 2, [`run_list_local_ids.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/run_list_local_ids.txt) was fixed and now lists all 90 cases (`C001` through `C090`).
  - Disjointness test: $\text{remote} \cap \text{local} = \emptyset$.
  - Completeness test: $\text{remote} \cup \text{local} = 177$ cases, covering `campaign_design.json` identically. Verified.

---

## Part B: Runner Logic

### 4. Watchdog Logic (`converge_watchdog.py`, `remote_run.py`)

- **Minimum Iterations**:
  - [`converge_watchdog.py:40`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L40): `if it < min_iter: continue`.
  - In [`remote_run.py:101,128`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L101), `min_iter` is passed as `"1200"` for both pass 1 and the continuation pass. Verified.

- **Residual Thresholds**:
  - [`converge_watchdog.py:10,41`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L10):
    ```python
    TH = dict(Ux_initial=1e-5, Uy_initial=1e-5, Uz_initial=1e-5, p_rgh_initial=1e-5, h_initial=1e-6)
    if all(float(d.get(k, 1.0)) < v for k, v in TH.items()):
        stop("CONVERGED_STOP", ...)
    ```
    Requires $U_x, U_y, U_z, p_{rgh} < 10^{-5}$ and $h < 10^{-6}$. Verified.

- **Envelope Stop**:
  - [`converge_watchdog.py:10,43-46`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L10): `T_WALL_MAX = 273.15 + 70.0` ($343.15\text{ K}$).
  - Evaluated at or after `env_iter` (passed as `"4000"` in [`remote_run.py:101,128`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L101)). If $T_{wall,max} > 343.15\text{ K}$, triggers `stop("ENVELOPE_STOP", ...)`. Verified.

- **Numeric Time Ordering**:
  - [`converge_watchdog.py:11`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L11): `def tsort(fs): return sorted(fs, key=lambda f: float(os.path.basename(os.path.dirname(f))))`. Used for reading `solverInfo.dat` and `ifaceTmax`. Verified.

- **Arguments Passed**:
  - [`remote_run.py:101,128`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L101): `["python3", os.path.join(ROOT, "converge_watchdog.py"), d, "1200", "20", "4000"]`. Matches the specification.

- **Stop Marker Files Across Branches**:
  - `CONVERGED_STOP`: written by `stop("CONVERGED_STOP", ...)` on line 42.
  - `ENVELOPE_STOP`: written by `stop("ENVELOPE_STOP", ...)` on line 46.
  - `Iteration Cap`: cases reaching `endTime 12000` terminate through OpenFOAM's normal exit (`\nEnd\n` in log detected by line 35). As intended by the design ([`remote_run.py:109`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L109), [`README.md:48`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L48)), no marker file is written; the absence of a marker file signifies "cap".

---

### 5. Continuation Logic (`select_continuations.py`, `remote_run.py`)

- **Selection Criteria**:
  - Located in [`select_continuations.py:17-20`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/select_continuations.py#L17-L20):
    ```python
    met = max(r["Ux_initial"], r["Uy_initial"], r["Uz_initial"]) < 1e-4 and r["p_rgh_initial"] < 1e-4 and r["h_initial"] < 1e-6
    short = it < 1200
    if (met and not short) or tw > 273.15 + 70.0 or it >= END: continue
    ```
    Correctly continues cases that fail acceptance residuals (`not met`) or stopped short (`it < 1200`), provided $T_{wall,max} \le 70^\circ\text{C}$ and $it < 12000$. Sets `endTime 12000;` and restores `stopAt endTime;` ([`select_continuations.py:21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/select_continuations.py#L21)).

- **Restart and Pass Archiving (Round-1 Blocking Issue 5 Fix)**:
  - In [`remote_run.py:122-125`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L122-L125):
    ```python
    n = 1
    while os.path.exists(os.path.join(d, "DONE_pass%d" % n)): n += 1
    for f in ("DONE", "log.chtMultiRegionSimpleFoam", "CONVERGED_STOP", "ENVELOPE_STOP", "log.watchdog"):
        if os.path.exists(os.path.join(d, f)):
            shutil.move(os.path.join(d, f), os.path.join(d, "%s_pass%d" % (f, n) if not f.startswith("log.") else "%s.pass%d" % (f, n)))
    ```
    All previous files, including `CONVERGED_STOP` and `ENVELOPE_STOP`, are renamed to `${f}_pass${n}` before starting the continuation pass. No stale stop markers persist to contaminate pass 2 status reporting or tarball packaging.
  - Restarts from latest time (`startFrom latestTime;`, `decomposePar -latestTime`), runs solver, reconstructs latest time, removes processor directories, and reruns `posthoc_zone_T.py` ([`remote_run.py:126-135`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L126-L135)).

- **Can a case be continued twice?**:
  - Yes, safely. If `remote_run.py` or continuation is rerun, the `while os.path.exists(os.path.join(d, "DONE_pass%d" % n)): n += 1` loop detects existing passes and increments $n$ (e.g. archiving to `DONE_pass2`, `log.chtMultiRegionSimpleFoam.pass2`, etc.).
  - [`remote_run.py:78`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L78) includes `glob.glob(os.path.join(d, "*_pass*"))` in `pack()`, ensuring full historical provenance is preserved in the tarball. Cases reaching 12000 iterations satisfy `it >= END` and are not continued again.

- **Can a case that is still running be selected?**:
  - No. [`select_continuations.py:9`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/select_continuations.py#L9) searches strictly for `cases/*/DONE`. A running case in pass 1 has no `DONE` file; during continuation, `DONE` is renamed to `DONE_pass${n}` and only rewritten upon pass completion ([`remote_run.py:133`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L133)).

---

### 6. Post-Hoc Extraction (`posthoc_zone_T.py`)

- **Leading-Edge Box Cloning for Trailing Edge (Round-1 Non-Blocking Issues 3 & 4 Fix)**:
  - Located in [`posthoc_zone_T.py:32-37`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L32-L37):
    ```python
    m = re.findall(r"name (\w+)Set; type faceSet; action new; source boxToFace; box \(-1e-06 -1 ([0-9.e-]+)\) \(1e-06 1 ([0-9.e-]+)\); \}", td)
    zb = {name: (float(z0), float(z1)) for name, z0, z1 in m}
    if "chanIn" not in zb or "clearIn" not in zb: return "leading-edge zones not found in system/fluid/topoSetDict"
    L = 0.118; acts = []
    for name, (z0, z1) in (("chanOut", zb["chanIn"]), ("clearOut", zb["clearIn"])):
        acts.append("    { name %sSet; type faceSet; action new; source boxToFace; box (%.6f -1 %s) (%.6f 1 %s); }\n    { name %s; type faceZoneSet; action new; source setToFaceZone; faceSet %sSet; }" % (name, L - 1e-6, repr(z0), L + 1e-6, repr(z1), name, name))
    ```
  - Directly extracts the case's own $z$-bounds `(z0, z1)` for `chanIn` and `clearIn`. The dead branch `if zsplit is None:` and unused regex `m2` from Round 1 have been completely eliminated.
- **Fixed-Fin Cases (`F001` to `F004`)**:
  - The hardcoded ceiling `ztop = 0.04545` was removed. `clearIn` in [`unit_cell.py:170`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L170) is bounded at $z_{hi} = H_c + 10^{-3}$. Consequently, `zb["clearIn"]` automatically uses $H_c + 10^{-3}$ for each chassis height ($25.4\text{ mm}, 30.4\text{ mm}, 35.4\text{ mm}, 44.45\text{ mm}$), matching the exact domain height across all fixed-fin cases.
- **$OR = 1.0$ Cases**:
  - `chanIn` spans $[H_B - \epsilon, H_B + \epsilon]$ (0 faces). `chanOut` receives the same bounds (0 faces).
  - [`posthoc_zone_T.py:48`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L48) filters zones: `zones = [z for z in ("chanIn","clearIn","chanOut","clearOut") if sizes.get(z,0)>0]`. `chanIn` and `chanOut` are skipped, leaving only `clearIn` and `clearOut`. Confirmed on test case `C091` where `posthoc_zoneT.json` generated cleanly with sizes 0 for channel zones and 280 for clearance zones.
- **Weighted Average and Idempotency**:
  - Uses `operation weightedAverage; weightField phi; fields (T);` and `operation sum; fields (phi);` ([`posthoc_zone_T.py:51-52`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L51-L52)).
  - Sorts time directories numerically ([`posthoc_zone_T.py:59`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L59)).
  - Idempotent: checks if JSON is newer than `DONE` ([`posthoc_zone_T.py:29`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L29)); reuses existing `clearOut` in `faceZones` ([`posthoc_zone_T.py:40-41`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L40-L41)); cleans prior zone directories before post-processing ([`posthoc_zone_T.py:54`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L54)).

---

### 7. Resource Detection and MPI Decomposition

- **Hardware and Load Detection**:
  - Physical cores: `lscpu` regex `Core(s) per socket` $\times$ `Socket(s)` ([`remote_run.py:48-49`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L48-L49)), fallback `os.cpu_count()`.
  - RAM: `/proc/meminfo` -> `MemAvailable` in kB / 1e6 -> `free_gb` ([`remote_run.py:50`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L50)).
  - Load: `/proc/loadavg` 1-minute load average ([`remote_run.py:51`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L51)).
- **Prompt Proposal**:
  - [`remote_run.py:55`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L55): `default = max(a.ranks, (phys - int(round(load))) // a.ranks * a.ranks)`. Proposes an integer multiple of 8 ranks based on unloaded physical cores.
- **Oversubscription**:
  - The run can oversubscribe the machine if requested: the prompt mentions running up to $1.5\times phys$ ranks based on workstation benchmarking; the user can enter any integer $\ge 8$; and CLI `--cores N` overrides the prompt.
- **MPI Ranks Fixed at 8 (Round-1 Blocking Issue 4 Fix)**:
  - `system/decomposeParDict` in all cases specifies `numberOfSubdomains 8;` ([`unit_cell.py:156`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L156)).
  - In Round 2, the `--ranks` CLI parameter was **removed from `argparse`** ([`remote_run.py:142`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L142)), and [`remote_run.py:147`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L147) hardcodes:
    ```python
    a.ranks = 8   # fixed: system/decomposeParDict of every audited case has numberOfSubdomains 8
    ```
    This completely eliminates the possibility of rank/subdomain mismatches causing FOAM FATAL ERROR crashes.

---

### 8. Results, Concurrency, and Importer

- **What is Packed**:
  - [`remote_run.py:75-83`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L75-L83): `results/<cid>.tar.gz` packs `postProcessing/`, `case_meta.json`, `DONE`, `CONVERGED_STOP`, `ENVELOPE_STOP`, `CONTINUE`, `posthoc_zoneT.json`, `system/`, constant dictionaries (`regionProperties`, `g`, `fluid/thermophysicalProperties`, `solid/thermophysicalProperties`), all `log.*` files, and all historical `*_pass*` files. Bulky mesh topology and volumetric time fields are excluded.
- **Git Push Implementation (Round-1 Blocking Issue 1 Fix)**:
  - Located in [`remote_run.py:84-93`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L84-L93):
    ```python
    def push(msg, nopush):
        if nopush: return
        rel = os.path.relpath(ROOT, REPO)
        with PUSH_LOCK:
            steps = ["git add -A %s/results %s/remote_run.log"%(rel, rel),
                     "git diff --cached --quiet || git commit -q -m '%s'"%msg.replace("'", ""),
                     "git pull -q --rebase origin main",
                     "git push -q origin HEAD:main"]
            for st in steps:
                rc = sh(st, cwd=REPO, logfile=os.path.join(ROOT, "git_push.log"))
                if rc != 0:
                    log("PUSH FAILED at '%s' (rc %d, see git_push.log); results stay in %s/results and are pushed with the next case"%(st.split()[1], rc, rel))
                    return False
        return True
    ```
  - `rel` resolves to `unit_cell_campaign`. Pathspec `unit_cell_campaign/results` and `unit_cell_campaign/remote_run.log` matches valid paths from `cwd=REPO`.
  - Every step checks return code `rc`. Failures log the failing subcommand and return code, abort cleanly without throwing unhandled exceptions, and leave results queued locally in `results/` to be committed and pushed on the next case.
- **Push Concurrency**:
  - Synchronized via `PUSH_LOCK = threading.Lock()` ([`remote_run.py:74,88`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L74)); threads cannot run git operations simultaneously.
- **Resumability**:
  - Handled by [`remote_run.py:96`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L96): `if os.path.exists(os.path.join(d, "DONE")): log("%s skip (done)" % cid); return`.
  - In [`build_cases.py:11`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/build_cases.py#L11): checks `case_meta.json` and `faces` file to skip already built meshes.
- **Importer Protection Against Overwriting Local Cases**:
  - In [`import_remote_results.py:10`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/import_remote_results.py#L10):
    ```python
    if os.path.exists(done) and "host=" not in open(done).read(): print(cid, "skip: finished locally"); continue
    ```
  - Remote cases write `host=<nodename>` into `DONE` ([`remote_run.py:107,133`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L107)), while workstation cases do not include `host=`. Locally solved cases are skipped and never overwritten. In addition, line 17 preserves local audited `system/` dictionaries.

---

### 9. OpenFOAM Environment Detection and `--test` Mode

- **Universal Environment Detection (Round-1 Blocking Issue 3 Fix)**:
  - In [`unit_cell.py:35-43`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L35-L43) and [`posthoc_zone_T.py:9-17`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L9-L17), `of_prefix()` dynamically locates OpenFOAM:
    1. Checks if `chtMultiRegionSimpleFoam` is already in PATH.
    2. Checks `$OPENFOAM_BASHRC` (exported by [`remote_run.py:36`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L36)).
    3. Searches `OF_CANDIDATES` (`/usr/lib/openfoam/openfoam2406/etc/bashrc`, `/opt/openfoam2406/etc/bashrc`, `/opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc`, `~/OpenFOAM/...`).
  - Hardcoded paths in `unit_cell.py` and `posthoc_zone_T.py` were replaced with `of_prefix()`.
- **Pipeline Coverage in `--test` Mode**:
  - Exercises all 7 stages:
    1. Build: `build([ids[0]], workers=1)` -> `build_cases.py` (`blockMesh`, `checkMesh`, `splitMeshRegions`, `topoSet`).
    2. Verify: `make_manifest.py check manifest_local_build.json build_list.txt`.
    3. Decompose: `decomposePar -allRegions -force -decomposeParDict system/decomposeParDict`.
    4. Solve: rewrites `endTime 60;` and `writeInterval 60;`, runs `mpirun -np 8 chtMultiRegionSimpleFoam -parallel` with watchdog.
    5. Reconstruct: `reconstructPar -allRegions -latestTime`.
    6. Post-hoc zone extraction: `posthoc_zone_T.py` -> writes `posthoc_zoneT.json`.
    7. Pack: `pack(cid)` -> writes `results/<cid>.tar.gz`.
  - Non-interactive prompt handling ([`remote_run.py:148`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L148)):
    ```python
    if a.test and not a.cores: a.cores = 8
    ```
    Skips `choose_cores()` interactive prompt automatically during `--test` mode.

---

## Part C: Documentation

### 10. `README.md` Audit

- **Requirements and Dependencies (Round-1 Blocking Issue 2 Fix)**:
  - [`README.md:25`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L25) states: `Python 3.8+ with numpy (the builder's property fits)`.
  - [`remote_run.py:42-43`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L42-L43) checks `import numpy` on startup. Dependency is declared and checked.
- **Settings Table Alignment**:
  - Pressure solver: GAMG, relTol 0.01, maxIter 200 $\implies$ matches `unit_cell.py:162`.
  - Iteration cap: 12,000 $\implies$ matches `unit_cell.py:155`.
  - Convergence stop: $p_{rgh}, U < 10^{-5}$, $h < 10^{-6}$, $\ge 1200$ iters $\implies$ matches `converge_watchdog.py:10,40,41`.
  - Envelope stop: $\ge 4000$ iters, $T_{wall,max} > 70^\circ\text{C}$ $\implies$ matches `converge_watchdog.py:10,43-46`.
  - Continuation pass: $U, p_{rgh} < 10^{-4}$, $h < 10^{-6}$ or $it < 1200$ continued to 12,000 $\implies$ matches `select_continuations.py:17-21`.
  - Post-hoc zone extraction: mass-weighted $T$ and flux sum $\implies$ matches `posthoc_zone_T.py`.
  - Build verification: SHA-256 compared with `manifest_local_build.json` $\implies$ matches `make_manifest.py`.
- **Git Ignore Consistency**:
  - In `../gitignore_of_repo.txt`: lines 20-24 ignore `unit_cell_campaign/cases/`, `*.log`, but whitelist `!unit_cell_campaign/remote_run.log`. `results/` is not ignored. Matches `remote_run.py:89` which stages `unit_cell_campaign/results` and `unit_cell_campaign/remote_run.log`.

---

## Status of Prior Audit Findings (Round 1 $\to$ Round 2)

| Issue | Severity | Status in Round 2 | Verification Evidence |
|---|---|---|---|
| 1. Git push failure (bad cwd / pathspec) | BLOCKING | **RESOLVED** | `remote_run.py:87,89` uses `rel = os.path.relpath(ROOT, REPO)` and checks `rc != 0` on every step. |
| 2. Missing `numpy` dependency | BLOCKING | **RESOLVED** | Declared in `README.md:25` and validated at startup in `remote_run.py:42-43`. |
| 3. Hardcoded `/usr/lib/openfoam/openfoam2406` | BLOCKING | **RESOLVED** | `of_prefix()` in `unit_cell.py:35` and `posthoc_zone_T.py:9` searches PATH, `$OPENFOAM_BASHRC`, and standard candidate directories. |
| 4. Fatal crash if `--ranks != 8` | BLOCKING | **RESOLVED** | `--ranks` removed from CLI; `a.ranks = 8` fixed in `remote_run.py:147` and documented in `README.md:40-41`. |
| 5. Stale `CONVERGED_STOP` retention in continuation | BLOCKING | **RESOLVED** | `remote_run.py:124-125` renames `CONVERGED_STOP` and `ENVELOPE_STOP` to `${f}_pass${n}` before starting pass 2. |
| 6. Pre-fix hashes for local cases in manifest | NON-BLOCKING | **RESOLVED** | Documented in `README.md:55-57` as historical run state on originating workstation. All remote cases have updated hashes. |
| 7. Truncated `run_list_local_ids.txt` | NON-BLOCKING | **RESOLVED** | `run_list_local_ids.txt` expanded to all 90 local cases (`C001` to `C090`). |
| 8. Dead code in `posthoc_zone_T.py:27` | NON-BLOCKING | **RESOLVED** | Dead branch `if zsplit is None:` eliminated; boxes cloned directly from leading-edge definitions. |
| 9. Hardcoded `ztop = 0.04545` | NON-BLOCKING | **RESOLVED** | Hardcoded ceiling removed; bounds parsed dynamically from each case's `topoSetDict`. |
| 10. Interactive prompt in `--test` mode | NON-BLOCKING | **RESOLVED** | `remote_run.py:148` sets `a.cores = 8` when `--test` is active, bypassing interactive stdin prompt. |
| 11. Overwrite of pass 1 history on re-continuation | NON-BLOCKING | **RESOLVED** | `remote_run.py:122-123` dynamically discovers latest pass index $n$ and archives sequentially (`DONE_pass1`, `DONE_pass2`, etc.). |

---

```
BLOCKING (would give a wrong or unusable result on the remote machine): none
NON-BLOCKING: none
NOT VERIFIABLE: none
VERDICT: PASS
```
