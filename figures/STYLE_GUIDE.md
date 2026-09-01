# Manuscript Figure Style Guide & Visual Conventions (Elsevier Journal Standard)
**Paper-5: Bypass-Controlled Single-Phase Immersion Cooling of Server Heat Sinks**  
*Target Journal: International Journal of Heat and Mass Transfer / Energy*  
*Author / Lead: agy (Independent Screener and Figure Lead)*  
*Stage: 5 (Figure Visual Overhaul & Journal Idiom Alignment)*

---

## 1. Core Visual Principles & Journal Idiom

All figures across the manuscript (Figures 1–12) strictly follow the authentic visual conventions established in primary reference literature (Muneeshwaran et al., IJHMT 2023; Chun et al., IJHMT 2026; Jeng, IJHMT 2008):

1. **Source of Record:** Vector SVG format is the definitive master file. High-resolution raster previews (600 DPI PNG) are generated directly from vector SVGs via PyMuPDF.
2. **Greyscale First:** Figures must be 100% interpretable in monochrome/greyscale without loss of clarity. Line styles (solid, dashed, dash-dot, dotted), high-contrast hatch patterns, and distinct geometric markers ($\circ, \bullet, \square, \blacksquare, \vartriangle, \blacktriangle, \blacklozenge$) are the primary discriminators; colour is strictly secondary.
3. **No UI / Dashboard Aesthetics:** Zero rounded "card" containers (`rx=0`), zero drop-shadows, zero decorative gradients, zero pastel card background fills. Panel boundaries and coordinate frames are plain thin black rectangles (`stroke="#000000"`).
4. **No Colored Badge Pills:** Categorical labels, tiers, and provenance tags are rendered in plain text or monospace notation (`[adopted]`, `[derived]`, `[assumed]`), never as colored UI pill badges.
5. **Plain Panel Captions:** Panel labels ("(a)", "(b)", "(c)", ...) are set as plain bold black text directly above or beside panels, never inside colored/shaded header bars.
6. **Dimensional CAD Conventions:** Schematics (Figs. 1, 2, 6) employ thin black extension/dimension lines with crisp arrowheads, dimension text along the line, and clean geometric linework (Muneeshwaran Fig. 2 style).
7. **Scientific Uncertainty:** Data plots (Figs. 5, 7–12) use discrete data markers with standard I-beam error bars or explicit stated $\pm X\%$ uncertainty text, not fuzzy shaded polygon bands.
8. **Plain Discipline Watermarks:** `[AWAITING-RESULTS]` and `PLACEHOLDER — MOCK DATA` markers use a plain black-bordered rectangular box with bold black text (Chun Fig. 3(b) inset style), ensuring unmistakable segregation without decorative watermarks.
9. **Strict Typographic Bounds:** All figure text is strictly bounded between **$5.5\text{ pt}$ (typographic floor)** and **$9.0\text{ pt}$ (typographic ceiling)**.
10. **Canonical Sizing:** Fixed canvas width of **$390.0\text{ pt} = 137.06\text{ mm}$** matching the single-column manuscript text width (`\textwidth`) at 1:1 scale.

---

## 2. Managed Semantic Palette & Grayscale Discrimination

| Entity | Stroke / Fill | Line Style | Marker / Hatch | Greyscale Semantic Meaning |
|---|---|---|---|---|
| **Active Core Flow ($q_{\text{active}}$)** | `#0072B2` (Active Blue) | Solid ($1.2 - 1.8\text{ pt}$) | Solid arrow / Filled diamond ($\blacklozenge$) | Primary coolant heat removal stream |
| **Lateral Bypass Flow ($q_{\text{bypass}}$)** | `#D55E00` (Vermilion) | Dashed ($4, 2$) | Open chevron / Open circle ($\circ$) | Unheated bypass diversion stream |
| **Solid Copper Heat Sink** | `#E69F00` (Amber) | Solid ($0.8\text{ pt}$) | Open square ($\square$) / Solid base | Base plate, fin array, TTV heat source |
| **Flow Control Blocks** | `#009E73` (Teal) | Solid ($0.6\text{ pt}$) | Dense cross-hatch (`#hatch-block`) | Baffles, flow blockage hardware |
| **Structural Frame / Ink** | `#000000` (Black) | Solid ($0.6 - 1.0\text{ pt}$) | Black arrows / Hard frame | Domain outlines, coordinate axes, primary text |
| **Gridlines / Sub-rules** | `#CBD5E1` (Light Grey) | Dashed ($2, 2$, $0.5\text{ pt}$) | None | Coordinate grid reference |

---

## 3. Manuscript Figure Inventory (Stage 5 Overhaul)

| Figure | Source Script | Master SVG | 600 DPI PNG | Description | Canvas ($\text{W}\times\text{H}$) | Verified Font Range | Status |
|---|---|---|---|---|---|---|---|
| **Fig. 1** | `scratch/gen_fig1.py` | `figures/fig1_domain.svg` | `figures/fig1_domain.png` | Computational Domain & Bypass Architecture | $390.0 \times 440.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 2** | `scratch/gen_fig2.py` | `figures/fig2_dimension_ledger.svg` | `figures/fig2_dimension_ledger.png` | Dimension Ledger & Parameter Provenance | $390.0 \times 395.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 5** | `scratch/gen_fig5.py` | `figures/fig5_validation_ladder.svg` | `figures/fig5_validation_ladder.png` | Experimental Validation Ladder (6 Panels) | $390.0 \times 335.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 6** | `scratch/gen_fig6.py` | `figures/fig6_flowpath_concept.svg` | `figures/fig6_flowpath_concept.png` | Schematic Flowpath Topology Across OR | $390.0 \times 205.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 7** | `scratch/gen_fig7.py` | `figures/fig7_bypass_fraction.svg` | `figures/fig7_bypass_fraction.png` | Bypass Fraction ($\Phi_{\text{bypass}}$) Sensitivity | $390.0 \times 255.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 8** | `scratch/gen_fig8_9.py` | `figures/fig8_rth_vs_reglobal.svg` | `figures/fig8_rth_vs_reglobal.png` | Thermal Resistance vs. Global Domain Re | $390.0 \times 245.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 9** | `scratch/gen_fig8_9.py` | `figures/fig9_rth_vs_rehs.svg` | `figures/fig9_rth_vs_rehs.png` | Thermal Resistance vs. Core $\mathrm{Re}_{\text{hs}}$ (Data Collapse) | $390.0 \times 245.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 10** | `scratch/gen_fig10.py` | `figures/fig10_dp_pumping_vs_openratio.svg` | `figures/fig10_dp_pumping_vs_openratio.png` | Pressure Drop & Pumping Power vs. OR | $390.0 \times 245.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 11** | `scratch/gen_fig11.py` | `figures/fig11_parity_plot.svg` | `figures/fig11_parity_plot.png` | Model Parity vs. Experimental Benchmarks | $390.0 \times 270.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |
| **Fig. 12** | `scratch/gen_fig12.py` | `figures/fig12_outofsample.svg` | `figures/fig12_outofsample.png` | Out-of-Sample Fluid & Topology Validation | $390.0 \times 245.0\text{ pt}$ | $5.5 - 8.2\text{ pt}$ | **PASS** |

