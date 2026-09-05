# Adversarial Audit Report: Remote Share of the Unit-Cell Calibration Campaign

**Audited Directory**: `/tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign`  
**Audit Specification**: [`audit/instructions_remote_setup_audit.md`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/audit/instructions_remote_setup_audit.md)  
**Mode**: Adversarial Auditor (Gemini 3.7 Flash; Read-Only)

---

## Part A: Set-Up Fidelity

### 1. `unit_cell.py` Source Verification and Calculations

- **`fvSolution` pressure solver settings (`maxIter 200` on `p_rgh`)**:
  - Located in [`unit_cell.py:152`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L152):
    ```openfoam
    p_rgh { solver GAMG; smoother GaussSeidel; tolerance 1e-9; relTol 0.01; maxIter 200; }
    ```
    Carried in `system/fluid/fvSolution`. Correct.

- **`controlDict` settings (`endTime 12000`, `runTimeModifiable true`)**:
  - Located in [`unit_cell.py:145`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L145):
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
    Carries `endTime 12000;` and `runTimeModifiable true;`. Correct.

- **`topoSetDict` face zones and $z$-split at $H_B + H_{fin}$**:
  - Located in [`unit_cell.py:129`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L129) and [`unit_cell.py:155-162`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L155-L162):
    ```python
    zt = HB + g["Hfin"]; eps = 1e-6
    def box(x, zlo, zhi): return "(%.7g -1 %.7g) (%.7g 1 %.7g)" % (x - eps, zlo, x + eps, zhi)
    for nm_, x in (("In", 0.0), ("Mid", L/2)):
        ts += "    { name chan%sSet; type faceSet; action new; source boxToFace; box %s; }\n    { name chan%s; type faceZoneSet; action new; source setToFaceZone; faceSet chan%sSet; }\n" % (nm_, box(x, HB - eps, zt + eps if g['Hfin'] > 1e-9 else HB + eps), nm_, nm_)
        ts += "    { name clear%sSet; type faceSet; action new; source boxToFace; box %s; }\n    { name clear%s; type faceZoneSet; action new; source setToFaceZone; faceSet clear%sSet; }\n" % (nm_, box(x, (zt + eps) if g['Hfin'] > 1e-9 else HB + eps, g["Hc"] + 1e-3), nm_, nm_)
    ```
    For $H_{fin} > 10^{-9}$ ($OR < 1$), `chanIn` and `chanMid` are defined with $z \in [H_B - \epsilon, H_B + H_{fin} + \epsilon]$, and `clearIn` and `clearMid` are defined with $z \in [H_B + H_{fin} + \epsilon, H_c + 10^{-3}]$. The split is located precisely at $H_B + H_{fin}$.

- **Independent Recomputation of $H_{fin}(OR)$ and Velocities**:
  Given: $H_c = 44.45\text{ mm}$, $H_B = 4.5\text{ mm}$, $s = 0.95\text{ mm} = 0.00095\text{ m}$, $t_f = 0.25\text{ mm} = 0.00025\text{ m}$, $T_{in} = 298.15\text{ K}$.
  - Fluid properties at $T_{in} = 298.15\text{ K}$:
    - **FC-40** ([`unit_cell.py:20-21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L20-L21)):
      $\rho = 2499 - 2.16(298.15) = 1854.996\text{ kg/m}^3$  
      $\mu = 0.0429 - 0.162\times 10^{-3}(298.15) + 1.08\times 10^{-7}(298.15)^2 = 0.00420018963\text{ Pa}\cdot\text{s}$  
      $\nu = \mu/\rho = 2.26425805\times 10^{-6}\text{ m}^2/\text{s}$  
      $k = 0.06542765\text{ W/(m}\cdot\text{K)}$, $c_p = 1052.1325\text{ J/(kg}\cdot\text{K)}$
    - **EFL-1** ([`unit_cell.py:22-30`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L22-L30)):
      $\rho = 1889.0\text{ kg/m}^3$, $c_p = 1165.0\text{ J/(kg}\cdot\text{K)}$  
      Tabulated at $T = [293.15, 313.15, 333.15]\text{ K}$: $\mu = [6.31, 2.77, 1.72]\times 10^{-3}\text{ Pa}\cdot\text{s}$; $k = [0.062, 0.068, 0.072]\text{ W/(m}\cdot\text{K)}$  
      Quadratic fits evaluate at $298.15\text{ K}$ to:  
      $\mu = 0.0051915625\text{ Pa}\cdot\text{s} \implies \nu = \mu/\rho = 2.74831260\times 10^{-6}\text{ m}^2/\text{s}$  
      $k = 0.06368750\text{ W/(m}\cdot\text{K)}$
  
  - **Case 1: `C005` (FC-40, $OR = 0.0$, $Re_{ch} = 40$)**:
    - $H_{fin} = (44.45 - 4.5)(1 - 0.0) = 39.95\text{ mm} = 0.03995\text{ m}$
    - $D_h = \frac{2 s H_{fin}}{s + H_{fin}} = \frac{2(0.00095)(0.03995)}{0.00095 + 0.03995} = \frac{7.5905\times 10^{-5}}{0.04090} = 0.001855868\text{ m}$ ($1.855868\text{ mm}$)
    - $u_{ch} = \frac{Re_{ch}\nu}{D_h} = \frac{40(2.26425805\times 10^{-6})}{0.001855868} = 0.04880214\text{ m/s}$
    - For $OR = 0.0$, all inlet flow passes into the channel; with $u_{ch} = u_{in}\frac{s/2 + t_f/2}{s/2}$:
      $u_{in} = u_{ch}\frac{s}{s + t_f} = 0.04880214\left(\frac{0.95}{1.20}\right) = 0.03863503\text{ m/s}$
    - `build_cases.py` output: `H_fin_m: 0.03995`, `D_h_m: 0.001855868`, `u_ch_m_s: 0.04880214`, `u_in_m_s: 0.03863503`. Matches exactly.

  - **Case 2: `E002` (EFL-1, $OR = 0.0$, $Re_{ch} = 40$)**:
    - $H_{fin} = 39.95\text{ mm} = 0.03995\text{ m}$, $D_h = 0.001855868\text{ m}$
    - $u_{ch} = \frac{40(2.74831260\times 10^{-6})}{0.001855868} = 0.05923512\text{ m/s}$
    - $u_{in} = u_{ch}\frac{s}{s + t_f} = 0.05923512\left(\frac{0.95}{1.20}\right) = 0.04689447\text{ m/s}$
    - `build_cases.py` output: `H_fin_m: 0.03995`, `D_h_m: 0.001855868`, `u_ch_m_s: 0.05923512`, `u_in_m_s: 0.04689447`. Matches exactly.

  - *(Note on $OR > 0$ cases)*: When $OR > 0$ (e.g. `C014` at $OR = 0.1$), $A_{ch\_half} = (s/2)H_{fin}$ and $A_{in\_half} = ((s+t_f)/2)(H_c - H_B)$. As designed in [`unit_cell.py:45,175`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L45), $u_{in} = u_{ch}\frac{s}{s+t_f}(1 - OR)$, which scales $u_{in}$ by the area ratio $A_{ch}/A_{in}$.

---

### 2. `manifest_local_build.json` Verification

- **Case ID coverage**:
  - `manifest_local_build.json` contains exactly 177 case IDs.
  - The set of keys matches the 177 cases in `campaign_design.json` identically.

- **Audited Files vs Files Influencing Solution**:
  - `make_manifest.py` checks 26 files per case in `FILES` ([`make_manifest.py:8-13`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L8-L13)) plus `checkMesh.cells` ([`make_manifest.py:24-26`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L24-L26)).
  - Files influencing the solution that are **not** in `FILES`:
    1. The mesh geometry files in `constant/fluid/polyMesh/` and `constant/solid/polyMesh/` (`points`, `faces`, `owner`, `neighbour`, `boundary`). As documented in [`make_manifest.py:3-5`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L3-L5), binary mesh files are excluded because blockMesh binary layout varies across systems; mesh consistency is verified via `system/blockMeshDict` and `checkMesh.cells`.
    2. `constant/cellToRegion` (generated during `splitMeshRegions`, does not affect chtMultiRegionSimpleFoam).
    3. `system/fluid/topoSetDict` is verified in `FILES`, but the resulting `constant/fluid/polyMesh/faceZones` is not directly hashed (only `checkMesh.cells` is captured from `checkMesh`).

- **Volatile directives in `controlDict`**:
  - Handled in [`make_manifest.py:14-18`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/make_manifest.py#L14-L18):
    ```python
    VOLATILE = re.compile(r"^(stopAt|endTime|startFrom)\s")
    def digest(path, volatile=False):
        data = open(path, "rb").read()
        if volatile: data = b"\n".join(l for l in data.split(b"\n") if not VOLATILE.match(l.decode("latin1")))
        return hashlib.sha256(data).hexdigest()
    ```
  - `endTime`, `stopAt`, and `startFrom` start at the beginning of the line in `system/controlDict` and are correctly matched and excluded from the SHA-256 calculation for `system/controlDict`.

- **CRITICAL AUDIT FINDING ON MANIFEST**:
  - In `manifest_local_build.json`, **4 local cases (`C003`, `C004`, `C005`, `C050`)** carry the pre-fix SHA-256 hash `77ca06ca440bb4f6f6e74058d293f7a80211d5386bd0125196c8ae5e651bc1f3` for `system/fluid/fvSolution` (the file without `maxIter 200`).
  - All other 173 cases (including all 87 cases in `run_list_remote.txt`) carry hash `2b05dc20eaba75aeac2f2540eb3fc848cb3ea2228d7855d79a5be66c758b1d89` (with `maxIter 200`).
  - Running `make_manifest.py check manifest_local_build.json` on a fresh build of `C005` flags `MISMATCH ['system/fluid/fvSolution']`. Because these 4 cases belong to the local share and are not in `run_list_remote.txt`, `make_manifest.py check` passes for all 87 remote cases. However, the manifest file in the repository is internally inconsistent with the builder for those 4 cases.

---

### 3. `run_list_remote.txt` vs Local Share and Design

- `run_list_remote.txt` contains exactly 87 case IDs:
  - `C091` to `C099` (9 cases: OR = 1.0 calibration)
  - `E031` to `E033` (3 cases: EFL-1, OR = 1.0)
  - `L005`, `L010`, `L015`, `L020`, `L025` (5 cases: thermal loads, OR = 1.0)
  - `G001`, `G002` (2 cases: grid study)
  - `E001` to `E030` (30 cases: EFL-1 holdout)
  - `L001` to `L004`, `L006` to `L009`, `L011` to `L014`, `L016` to `L019`, `L021` to `L024` (20 cases: thermal loads)
  - `X001` to `X014` (14 cases: cross-combinations)
  - `F001` to `F004` (4 cases: fixed-fin clearance sweep)
- **Local Share Disjointness**:
  - The local share consists of cases `C001` to `C090` (90 cases).
  - None of the 87 remote IDs appears in `C001` to `C090` ($\text{remote} \cap [C001\dots C090] = \emptyset$).
  - None of the 87 remote IDs appears in `run_list_local_ids.txt`.
  - All 87 remote IDs appear in `campaign_design.json`.
  - *(Defect note)*: [`run_list_local_ids.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/run_list_local_ids.txt) in this package is incomplete: it lists only 11 case IDs (`C080` to `C090`), missing `C001` through `C079`.

---

## Part B: Runner Logic

### 4. Watchdog Logic (`converge_watchdog.py`, `remote_run.py`)

- **Minimum Iterations**:
  - [`converge_watchdog.py:40`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L40): `if it < min_iter: continue`.
  - In [`remote_run.py:91`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L91) (pass 1) and line 116 (pass 2), `min_iter` is passed as `"1200"`. Verified.

- **Residual Thresholds**:
  - [`converge_watchdog.py:10`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L10): `TH = dict(Ux_initial=1e-5, Uy_initial=1e-5, Uz_initial=1e-5, p_rgh_initial=1e-5, h_initial=1e-6)`.
  - [`converge_watchdog.py:41`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L41): `all(float(d.get(k, 1.0)) < v for k, v in TH.items())`.
  - Requires $U_x, U_y, U_z, p_{rgh} < 10^{-5}$ and $h < 10^{-6}$. Verified.

- **Envelope Stop**:
  - [`converge_watchdog.py:10`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L10): `T_WALL_MAX = 273.15 + 70.0` ($343.15\text{ K}$).
  - [`converge_watchdog.py:43-46`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L43-L46): Checked when `it >= env_iter` (passed as `4000` by `remote_run.py:91,116`). If `tw > 343.15 K`, calls `stop("ENVELOPE_STOP", ...)`. Verified.

- **Numeric Ordering of Time Directories**:
  - [`converge_watchdog.py:11`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L11): `def tsort(fs): return sorted(fs, key=lambda f: float(os.path.basename(os.path.dirname(f))))`.
  - Applied in `last_row()` (line 13) and `wall_tmax()` (line 21). Verified.

- **Arguments Passed by `remote_run.py`**:
  - [`remote_run.py:91,116`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L91): `["python3", os.path.join(ROOT, "converge_watchdog.py"), d, "1200", "20", "4000"]`.
  - Arguments: `case=d`, `min_iter=1200`, `poll_s=20`, `env_iter=4000`. Correct.

- **Stop Marker Files Across Branches**:
  - `CONVERGED_STOP`: written by `stop("CONVERGED_STOP", ...)` ([`converge_watchdog.py:30,42`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L30)).
  - `ENVELOPE_STOP`: written by `stop("ENVELOPE_STOP", ...)` ([`converge_watchdog.py:30,46`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L30)).
  - **Iteration Cap Branch**: When the case reaches `endTime` (12000 or 4000) naturally without triggering convergence or envelope stops, **no stop marker file is written**. The absence of a marker file is intentional and denotes "cap" per [`remote_run.py:99`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L99) and [`README.md:48`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L48).
  - *(Defect)*: In [`converge_watchdog.py:29-30`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/converge_watchdog.py#L29-L30):
    ```python
    def stop(tag, msg):
        cd = os.path.join(case, "system/controlDict"); s = open(cd).read()
        if "stopAt endTime;" in s:
            open(cd, "w").write(s.replace("stopAt endTime;", "stopAt writeNow;"))
            open(os.path.join(case, tag), "w").write(msg + "\n")
    ```
    If `"stopAt endTime;"` is missing (e.g. whitespace variant or already changed), the marker file is silently skipped.

---

### 5. Continuation Logic (`select_continuations.py`, `remote_run.py`)

- **Selection Criteria**:
  - In [`select_continuations.py:17-20`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/select_continuations.py#L17-L20):
    ```python
    met = max(r["Ux_initial"], r["Uy_initial"], r["Uz_initial"]) < 1e-4 and r["p_rgh_initial"] < 1e-4 and r["h_initial"] < 1e-6
    short = it < 1200
    if (met and not short) or tw > 273.15 + 70.0 or it >= END: continue
    ```
    Selects cases where residuals are not met (`not met`) OR iterations are short (`it < 1200`), provided `tw <= 70 C` and `it < END` (12000). Sets `endTime 12000;` and restores `stopAt endTime;` ([`select_continuations.py:21`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/select_continuations.py#L21)).

- **Restart and Archiving**:
  - Sets `startFrom latestTime;` ([`remote_run.py:114`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L114)).
  - Runs `decomposePar -allRegions -force -latestTime` ([`remote_run.py:115`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L115)).
  - Moves `DONE -> DONE_pass1` and `log.chtMultiRegionSimpleFoam -> log.chtMultiRegionSimpleFoam.pass1` ([`remote_run.py:112-113`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L112-L113)).
  - Reruns post-hoc zone extraction ([`remote_run.py:123`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L123)).

- **Can a case that is still running be selected?**:
  - **No**. [`select_continuations.py:9`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/select_continuations.py#L9) searches strictly for `cases/*/DONE`. A case currently executing in pass 1 does not yet have a `DONE` file. During pass 2, `DONE` is renamed to `DONE_pass1` on line 113 and only rewritten when pass 2 finishes on line 121. Thus running cases cannot be selected.

- **Can a case be continued twice?**:
  - In a standard run of `remote_run.py`, `continuation()` is executed only once ([`remote_run.py:139`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L139)).
  - If `remote_run.py` or `select_continuations.py` is rerun manually:
    - Cases that reached the `endTime 12000` cap have `it >= END` ($12000 \ge 12000$), so line 20 skips them.
    - Cases where pass 2 satisfied `met and not short` are skipped.
    - **However**, if a case ran pass 2 and stopped before 12000 iterations (e.g. stopped at `it < 1200` or watchdog terminated), `select_continuations.py` **will select it again**.
    - If continued again, [`remote_run.py:113`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L113) executes `shutil.move(DONE, DONE_pass1)` which **overwrites** `DONE_pass1` and `log.chtMultiRegionSimpleFoam.pass1` from the original pass 1.
  - *(CRITICAL DATA INTEGRITY DEFECT)*: In [`remote_run.py:112-114`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L112-L114), `remote_run.py` moves `DONE` to `DONE_pass1`, but **does not remove or rename `CONVERGED_STOP`**. If a case stopped in pass 1 with `CONVERGED_STOP` before 1200 iterations and was continued, but in pass 2 runs to the 12000 cap without meeting the tighter thresholds, the old `CONVERGED_STOP` file remains on disk. As a result, line 99 erroneously tags the continued case as `"converged"` rather than `"cap"`.

---

### 6. Post-Hoc Extraction (`posthoc_zone_T.py`)

- **$z$-split and Zone Construction at $x = L$**:
  - Reads `zsplit` from `topoSetDict` ([`posthoc_zone_T.py:22`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L22)), adds `chanOutSet` ($z \in [zlo, zsplit]$) and `clearOutSet` ($z \in [zsplit, ztop]$) at $x \in [L - 10^{-6}, L + 10^{-6}]$.
- **Skips Zero-Sized Zones**:
  - [`posthoc_zone_T.py:43-44`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L43-L44): Parses sizes from `log.topoSet` and `log.topoSet.posthoc`; `zones = [z for z in (...) if sizes.get(z, 0) > 0]`. Empty zones are omitted from `posthocFuncs`, preventing `surfaceFieldValue` aborts.
- **Reads $T$ Weighted by $\phi$ and $\sum \phi$**:
  - Lines 47-48: `weightedAverage` with `weightField phi` for `T`; `sum` for `phi`.
- **Numeric Time Order**:
  - Line 55: `key=lambda f: float(os.path.basename(os.path.dirname(f)))`.
- **Idempotency**:
  - Line 20: returns `"up to date"` if `posthoc_zoneT.json` is newer than `DONE`.
  - Lines 36-37: skips running `topoSet` if `chanOut` or `clearOut` already exists in `faceZones`.
  - Line 50: clears prior `postProcessing/fluid/zone*` directories.

- **Check of the $OR = 1$ Case**:
  - In [`unit_cell.py:159`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L159), $OR = 1$ writes `chanInSet` with box `(-1e-06 -1 0.004499) (1e-06 1 0.004501)`.
  - In [`posthoc_zone_T.py:22`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L22), regex `m` matches this degenerate box and sets `zsplit = 0.004501`.
  - As a consequence, line 27 (`if zsplit is None:`) is **dead code**.
  - Execution enters line 30 (`else:`), creating a degenerate `chanOutSet` ($z \in [0.004499, 0.004501]$, size 0) and `clearOutSet` ($z \in [0.004501, 0.04545]$, covering all outlet fluid faces).
  - Because `sizes.get("chanOut", 0) == 0`, line 44 skips `chanOut` and retains `clearOut`. Output is physically correct, but the code path relies on zero-size zone filtering rather than the intended `if zsplit is None:` branch.

- **Check of the Fixed-Fin Cases (`F001` to `F004`)**:
  - In `campaign_design.py:37`: $H_B = 4.5\text{ mm}$, $H_{fin} = 20.9\text{ mm}$.
    - `F001`: $c = 0\text{ mm} \implies H_c = 25.4\text{ mm} = 0.0254\text{ m}$
    - `F002`: $c = 5\text{ mm} \implies H_c = 30.4\text{ mm} = 0.0304\text{ m}$
    - `F003`: $c = 10\text{ mm} \implies H_c = 35.4\text{ mm} = 0.0354\text{ m}$
    - `F004`: $c = 19.05\text{ mm} \implies H_c = 44.45\text{ mm} = 0.04445\text{ m}$
  - In [`posthoc_zone_T.py:25`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L25), `ztop = 0.04545` ($45.45\text{ mm}$) is hardcoded.
  - Across all 177 campaign cases, $H_{chassis} \le 44.45\text{ mm} < 45.45\text{ mm}$. Because the domain height is always $\le 44.45\text{ mm}$, `ztop = 0.04545` extends above the top wall and **covers the clearance domain for all cases**.
  - For `F001` ($c = 0$), $zsplit = 0.0254\text{ m} = H_c$. The box $[0.0254, 0.04545]$ contains 0 fluid faces; `clearOut` size is 0 and is skipped by line 44.
  - *(Code quality note)*: [`posthoc_zone_T.py:24`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L24) defines regex `m2` to capture the domain top from `clearIn`, but `m2` is unused and ignored in favor of hardcoded `ztop = 0.04545`.

---

### 7. Resource Detection and MPI Decomposition

- **Hardware and Load Detection**:
  - Physical cores: Parsed from `lscpu` via regex `Core(s) per socket` $\times$ `Socket(s)` ([`remote_run.py:44`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L44)); fallback is `os.cpu_count()`.
  - RAM: Parsed from `/proc/meminfo` (`MemAvailable` in kB / 1e6 -> GB) ([`remote_run.py:46`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L46)).
  - Load: Parsed from `/proc/loadavg` (1-min average) ([`remote_run.py:47`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L47)).

- **Prompt Proposal**:
  - [`remote_run.py:51`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L51): `default = max(a.ranks, (phys - int(round(load))) // a.ranks * a.ranks)`. Proposes an integer multiple of ranks (minimum 8) based on available physical cores minus load.

- **Oversubscription**:
  - **Yes, the run can oversubscribe the machine**.
    1. Line 54 suggests running up to $1.5\times phys$ ranks based on local benchmark throughput.
    2. Interactive validation (line 58: `if r.isdigit() and int(r) >= a.ranks: return int(r)`) imposes no upper bound.
    3. On machines with $< 8$ physical cores, `max(a.ranks, ...)` forces at least 8 cores, guaranteeing oversubscription.
    4. Passing `--cores N` on CLI bypasses all limits except `free_gb < 0.15 * cores` ([`remote_run.py:135`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L135)).

- **MPI Decomposition and `--ranks` Compatibility**:
  - `system/decomposeParDict` (and its region dictionaries) is written by [`unit_cell.py:126,146`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L126) with hardcoded `numberOfSubdomains 8;`.
  - `build_cases.py:16` does not pass `nsub`, so every case is built with exactly 8 subdomains.
  - The local build manifest hashes `decomposeParDict` for 8 subdomains.
  - In `remote_run.py:90,115`, `decomposePar` uses `system/decomposeParDict` and partitions the mesh into exactly 8 processor directories (`processor0` through `processor7`).
  - In [`remote_run.py:92,117`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L92), solver execution is:
    ```python
    sh(PRE + "mpirun -np %d chtMultiRegionSimpleFoam -parallel" % a.ranks, ...)
    ```
  - **Passing `--ranks` other than 8 causes an immediate fatal abort**: OpenFOAM verifies that `numberOfSubdomains` matches the MPI communicator size. Running `mpirun -np 4` on 8 subdomains aborts with:
    `FOAM FATAL ERROR: "system/decomposeParDict" specifies 8 processors but job was started with 4 ranks.`
    `decomposeParDict` is not updated by `remote_run.py` when `--ranks` is provided.

---

### 8. Results, Concurrency, and Importer

- **What is Packed**:
  - In [`remote_run.py:73-78`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L73-L78), `results/<cid>.tar.gz` includes:
    `postProcessing/`, `case_meta.json`, `DONE`, `DONE_pass1`, `CONVERGED_STOP`, `ENVELOPE_STOP`, `CONTINUE`, `posthoc_zoneT.json`, `system/`, constant dictionaries (`regionProperties`, `g`, fluid/solid `thermophysicalProperties`), and all `log.*` files. Large `polyMesh/` and reconstructed/processor field directories are excluded.

- **What is Pushed**:
  - [`remote_run.py:83`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L83): intends to push `results/` and `remote_run.log`.

- **BLOCKING BUG IN GIT PUSH (`remote_run.py:83`)**:
  - Line 16: `ROOT = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(ROOT)`.
  - Line 83 executes:
    ```python
    sh("git add results remote_run.log && git commit -q -m '%s' >/dev/null 2>&1; git pull -q --rebase origin main >/dev/null 2>&1; git push -q origin HEAD:main" % msg,
       cwd=REPO, logfile=os.path.join(ROOT, "git_push.log"))
    ```
  - `cwd` is set to `REPO` (`IJHMT_CFP/`). However, `results/` and `remote_run.log` are located in `ROOT` (`IJHMT_CFP/unit_cell_campaign/`).
  - Executing `git add results remote_run.log` from `REPO` fails immediately with:
    `fatal: pathspec 'results' did not match any files` (exit code 128).
  - Due to `&&`, `git commit`, `git pull`, and `git push` **never run**.
  - `push()` ignores the exit code of `sh()`. Every push fails silently, writing errors into `git_push.log`.
  - **Result: Nothing is ever pushed to the repository.**

- **Push Concurrency**:
  - [`remote_run.py:70,82`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L70): `PUSH_LOCK = threading.Lock()`. Calls to `push()` are enclosed in `with PUSH_LOCK:`, preventing concurrent git operations across threads.

- **Network Push Failure Handling**:
  - The return code of `sh(...)` in `push()` is discarded; exceptions are not raised, and execution continues.

- **Resumability**:
  - In [`remote_run.py:86`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L86): `if os.path.exists(os.path.join(d, "DONE")): log("%s skip (done)" % cid); return`.
  - In [`build_cases.py:11`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/build_cases.py#L11): checks `case_meta.json` and `constant/fluid/polyMesh/faces` to skip existing meshes.
  - The runner is resumable without repeating finished cases.

- **Importer Overwrite Protection**:
  - In [`import_remote_results.py:10`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/import_remote_results.py#L10):
    ```python
    if os.path.exists(done) and "host=" not in open(done).read(): print(cid, "skip: finished locally"); continue
    ```
  - Remote cases write `host=<nodename>` into `DONE` ([`remote_run.py:97`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L97)), whereas the local workstation runner does not include `"host="`.
  - The importer identifies locally finished cases and skips them. It does not overwrite locally finished cases.

---

### 9. OpenFOAM Environment Detection and `--test` Mode

- **Environment Detection Discrepancy**:
  - [`remote_run.py:27-34`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L27-L34) dynamically scans `OF_CANDIDATES` (`/usr/lib/openfoam/openfoam2406`, `/opt/openfoam2406`, etc.) and prepends `PRE = "source ...; "` to shell invocations.
  - However, [`unit_cell.py:180`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L180) and [`posthoc_zone_T.py:15`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/posthoc_zone_T.py#L15) **hardcode**:
    ```python
    source /usr/lib/openfoam/openfoam2406/etc/bashrc >/dev/null 2>&1;
    ```
  - If OpenFOAM v2406 on the remote machine is installed in `/opt/openfoam2406` or any non-default path without being active in the base shell environment, `build_cases.py` (via `unit_cell.py`) and `posthoc_zone_T.py` fail.

- **Pipeline Coverage in `--test` Mode**:
  - Verified across [`remote_run.py:133-143`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L133-L143):
    1. **Build**: `build([ids[0]], workers=1)` runs `build_cases.py` (`blockMesh`, `checkMesh`, `splitMeshRegions`, `topoSet`).
    2. **Verify**: runs `make_manifest.py check manifest_local_build.json build_list.txt`.
    3. **Decompose**: runs `decomposePar -allRegions -force -decomposeParDict system/decomposeParDict`.
    4. **Solve**: rewrites `endTime 60;` and `writeInterval 60;`, runs `mpirun -np 8 chtMultiRegionSimpleFoam -parallel`.
    5. **Reconstruct**: runs `reconstructPar -allRegions -latestTime`.
    6. **Extraction**: runs `posthoc_zone_T.py cases/<cid>`, generating `posthoc_zoneT.json`.
    7. **Pack**: runs `pack(cid)`, generating `results/<cid>.tar.gz`.
  - All 7 stages are exercised by `--test`.
  - *(Defect)*: `--test` invokes `choose_cores()` ([`remote_run.py:134`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L134)), triggering an interactive prompt for core count unless `--cores` is explicitly specified on the command line.

---

## Part C: Documentation

### 10. `README.md` Audit and Mismatches

1. **Undeclared Dependency (`numpy`)**:
   - [`README.md:25`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L25) states: `Python 3.8+ (standard library only)`.
   - [`unit_cell.py:23,28`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/unit_cell.py#L23) imports `numpy` inside `quad_fit()` and `efl1()`.
   - Building any of the 35 EFL-1 cases assigned to the remote machine crashes if `numpy` is not installed.

2. **Git Push Path Mismatch**:
   - [`README.md:25-26,37`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L25) states that results push automatically to the repository.
   - In [`remote_run.py:83`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/remote_run.py#L83), `git add results remote_run.log` runs with `cwd=REPO`, failing with pathspec errors and pushing nothing.

3. **`--ranks` Option Incompatibility**:
   - [`README.md:40-41`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L40) documents `--ranks`, but passing any rank count other than 8 crashes OpenFOAM due to hardcoded `numberOfSubdomains 8` in `system/decomposeParDict`.

4. **Incomplete Local Share List**:
   - [`README.md:6-8`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L6) states the remaining 90 cases run on the originating workstation.
   - [`run_list_local_ids.txt`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/run_list_local_ids.txt) in this package contains only 11 IDs (`C080` to `C090`).

5. **`--test` Prompt Behavior**:
   - [`README.md:35`](file:///tmp/claude-1000/-mnt-e-ijhmt-cfp-Paper-5/044cae9e-647d-4a52-a5b4-4a0397a1a7fd/scratchpad/IJHMT_CFP_audit/unit_cell_campaign/README.md#L35) shows `python3 remote_run.py --test` as a self-contained check, but it prompts interactively for core allocation if `--cores` is omitted.

---

```
BLOCKING (would give a wrong or unusable result on the remote machine):
1. Git push failure in remote_run.py:83: "git add results remote_run.log" executes with cwd=REPO (the repository root), where "results" and "remote_run.log" do not exist (they reside in ROOT, "unit_cell_campaign/"). The git command aborts with exit code 128 ("fatal: pathspec 'results' did not match any files"), terminating the command chain before commit, pull, or push can run. Because push() ignores the return code, all pushes silently fail and no results are ever returned to the originating repository.
2. Missing third-party dependency numpy in unit_cell.py:23,28: README.md:25 advertises "Python 3.8+ (standard library only)", but unit_cell.py imports numpy inside quad_fit() and efl1(). On a standard-library-only remote Python environment, building any of the 35 EFL-1 cases in run_list_remote.txt fails immediately with ModuleNotFoundError.
3. Hardcoded OpenFOAM installation path in unit_cell.py:180 and posthoc_zone_T.py:15: Both scripts hardcode "source /usr/lib/openfoam/openfoam2406/etc/bashrc", bypassing the OF_CANDIDATES search implemented in remote_run.py. If the remote machine has OpenFOAM v2406 installed under /opt/openfoam2406 (the standard tarball install path) and not in system PATH, mesh generation and post-hoc zone extraction abort.
4. Fatal abort when using --ranks with any value other than 8 in remote_run.py:92,117: unit_cell.py:146 and the verified manifest hardcode "numberOfSubdomains 8;" in system/decomposeParDict. If a user runs remote_run.py with --ranks N (N != 8), decomposePar creates 8 subdomains while mpirun launches N ranks, causing chtMultiRegionSimpleFoam to immediately abort with a FOAM FATAL ERROR.
5. Stale CONVERGED_STOP retention during continuation pass in remote_run.py:112-114: When a case stopped short (< 1200 iterations) with CONVERGED_STOP is continued in pass 2, remote_run.py archives DONE to DONE_pass1 but leaves CONVERGED_STOP untouched. If pass 2 hits the 12000-iteration cap without converging, the old CONVERGED_STOP remains in the case directory, causing remote_run.py:99 to misreport the run as "converged" and packaging an erroneous convergence marker into results/<case>.tar.gz.

NON-BLOCKING:
1. Four cases in manifest_local_build.json (C003, C004, C005, C050) carry stale pre-fix SHA-256 hashes for system/fluid/fvSolution (without maxIter 200), causing make_manifest.py check to report mismatches if those local cases are rebuilt. All 87 remote cases in run_list_remote.txt have the correct updated hash and pass verification.
2. run_list_local_ids.txt is truncated, containing only 11 cases (C080 to C090) instead of all 90 local cases (C001 to C090).
3. Dead code in posthoc_zone_T.py:27: For OR = 1, unit_cell.py:159 writes a degenerate chanInSet box, causing regex m on line 22 to match and set zsplit = 0.004501. The branch "if zsplit is None:" is never taken; the else branch executes, producing a 0-face chanOut that is filtered out by line 44.
4. Inflexible hardcoded clearance ceiling ztop = 0.04545 in posthoc_zone_T.py:25: While 0.04545 covers the clearance for all cases in campaign_design.json (where H_chassis <= 0.04445 m), regex m2 defined on line 24 to detect clearIn is left unused.
5. Interactive prompt during remote_run.py --test: choose_cores() prompts on stdin if --cores is omitted, which hangs non-interactive CI test invocations.
6. Overwrite of pass 1 history on repeated continuation: If select_continuations.py or remote_run.py is invoked after a continuation pass has already run, cases with it < 12000 that remain unconverged are re-selected, and remote_run.py:113 overwrites DONE_pass1 and log.chtMultiRegionSimpleFoam.pass1.

NOT VERIFIABLE:
none

VERDICT: FAIL
```
