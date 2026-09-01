# 1. Introduction

Rack power density has outrun what moving air can carry away. Chun et al. [1] observe that
high-density artificial intelligence workloads have driven escalating heat fluxes in data
centres, and they test chip-level loads above 700 W per chip. Their survey of prior
single-phase immersion work puts it below 30 W/cm2 [1]. The experimental record in this corpus
tracks the same climb. Huang et al. [2] instrumented a blade-style demonstration server
dissipating 1.75 kW of chip power in a single immersion cabinet. Kim et al. [3] modelled a
four-server rack and found immersion holding CPU temperature 22.9 degC below a hybrid
cold-plate arrangement at matched pump and fan power. Sun et al. [4] measured a 20 kW
cabinet-scale unit and recorded a cooling PUE of 1.08 to 1.09. Across this corpus, single-phase
immersion draws the most sustained attention. The dielectric liquid wets the package directly,
and one tank carries the CPU, memory and regulator loads with no phase change to manage.

What that attention has produced falls into three groups. The first is fluid comparison.
Shrigondekar et al. [5] ran FC-40 against PAO-6 in a 1U server. Y.-D. Zhang et al. [6] compared
PAO-4 with Noah@3000A across three cold-plate designs. B. Zhang et al. [7] measured SS110
against silicone oil and, more usefully for what follows, tabulated the properties and Prandtl
number of seventeen candidate coolants. The second group optimises heat-sink geometry.
Khoshvaght-Aliabadi et al. [8] swept fin length, height, thickness and spacing through a 54-run
Box-Behnken numerical design, then traded straight fins for oblique fins to attack temperature
non-uniformity [9] and reorganised the CPU and memory layout on the board [10]. The third group
works at tank scale. Ni and Yu [11] swept the hole radius and count of a flow equalisation
plate to even out server-to-server temperature. Dong et al. [12] compared Z-shaped, S-shaped
and C-shaped inlet and outlet layouts and varied immersion depth. Each group produced useful
design guidance. None predicts where the coolant actually goes once inside the chassis.

That question matters because coolant reaching the tank is not coolant reaching the fins.
Muneeshwaran et al. [13] measured it directly: a 5 mm gap between the heat sink and the 1U tank
wall raised thermal resistance by up to 7.4% and case temperature by up to 1.5 degC. Their flow
visualisation explains why. The fluid takes the gap because its resistance is lower, and that
stream does no useful heat transfer. Shrigondekar et al. [5] repeated the gap sweep at 0, 2 and
5 mm with CFD alongside experiment, and Y.-D. Zhang et al. [6] found a cold plate improved
performance largely by cutting bypass. The air-side literature reached the same conclusion
earlier and more quantitatively. Jeng [14] modelled a square pin-fin sink with laminar side
bypass and reported Nusselt number and dimensionless pressure drop against the channel-to-sink
width ratio. Cai et al. [15] measured and simulated a top bypass duct over a plate-fin
exchanger and found it shifting the average heat transfer coefficient by tens of percent. Tip
clearance has been treated the same way in liquid. Min et al. [16] found an optimum
dimensionless clearance near 0.6 under fixed pumping power, Sastre et al. [17] resolved the
flow topology by PIV at clearances up to 200% of fin height, Mei et al. [18] fitted Nusselt and
friction correlations in the clearance ratio, and Shahsavar et al. [19] carried the same
geometry into entropy generation.

Here the transfer problem becomes sharp, and should be stated precisely. Of these six bypass
studies, two use air, with Cai et al. printing Prandtl numbers of 0.702 and 0.699 [15], and
four use water, near Pr 7. The dielectric coolants tabulated by B. Zhang et al. [7] span Pr
from 19.8 for SS110 to 905 for DC-550, with FC-40 at 45.8 and PAO-6 at 359. The
bypass-mechanism literature in this corpus therefore sits one to three orders of magnitude
below the Prandtl range where immersion cooling operates, and further below it again in
viscosity. Correlations fitted there cannot be assumed to carry across.

Open ratio does not cool anything. It redistributes coolant between the fin channels and the
bypass passages, and the split is set by two parallel hydraulic resistances whose dependence on
viscosity and density differs. The anchor data shows the consequence. At an open ratio of 100%,
Chun et al. [1] compute a bypass mass fraction of 48.41% for FC-40 but 89.69% for GC-5X;
closing the bypass to an open ratio of 0% drives both below 0.8%. Because GC-5X loses far more
flow to the bypass when the path is open, it runs roughly 23.0 K hotter than FC-40 despite its
higher specific heat and thermal conductivity. Block the bypass and the ranking inverts, with
GC-5X becoming the cooler fluid. Closing the open ratio cuts thermal resistance by 45.6% for
GC-5X against 6.1% for FC-40 [1]. The same sensitivity reaches the Reynolds number any Nusselt
correlation would need. Shrigondekar et al. [5] report fin-spacing Reynolds numbers of roughly
10 to 70 for FC-40 and only 0.2 to 1 for PAO-6 in the same hardware. Two orders of magnitude,
with the geometry unchanged.

Nothing in this corpus predicts that split. Chun et al. [1] introduce open ratio as a
quantitative bypass metric but call the definition geometry-specific, and their future work
names experimental validation and system-level metrics, not a predictive correlation. Mei et
al. [18] do embed a clearance ratio in their Nusselt and friction exponents, but that fit
absorbs the bypass effect for deionised water in one micro-scale array rather than predicting
how the flow divides. Dong et al. [12] list the derivation of a dimensionless Nu-Re-Pr
correlation from their own dataset as work still to be done. Every bypass-mechanism study here
is air-side or water-side, and every immersion study reports a case-by-case campaign. A
designer facing a new fluid or fin pitch has no closure to reach for and must run the CFD
again.

This paper supplies that closure as a chain. Open ratio sets the ratio of hydraulic resistance
between the fin passages and the bypass passages. That ratio fixes the bypass fraction, which
fixes the heat-sink Reynolds number, the flow the fins actually see rather than the flow the
pump delivers. With the fluid Prandtl number it sets the Nusselt number, and Nusselt number and
bypass fraction together give thermal resistance and the pumping penalty that buys it. Each
link is dimensionless, so a fluid enters only through its property group and a heat sink only
through its geometric ratios. The framework is fitted on part of the corpus, then tested on a
fluid and a heat-sink geometry withheld from the fitting [AWAITING-RESULTS: out-of-sample fluid
and geometry validation, from the parametric campaign this pipeline has not yet run]. Accuracy
along the chain is reported as [AWAITING-RESULTS: fitted and out-of-sample errors for bypass
fraction, Nusselt number and thermal resistance].

Section 2 sets out the geometry, the fluid property treatment, the numerical method and the
validation ladder behind the solver. Section 3 develops the framework link by link with the
parametric campaign behind each closure. Section 4 tests it out-of-sample and examines where it
breaks down, and Section 5 draws out the design consequences.

---

## References

*Provisional numbering. These citations are numbered in order of first appearance within this
section only, because the methodology and results sections do not yet exist. The whole list will
be renumbered at final manuscript assembly. Every entry below has been checked against the
source PDF in `references/`, with title, authors, journal, volume, year and DOI confirmed as
printed. Where a printed title uses a dash as a subtitle separator, it is rendered here as a
colon to comply with this manuscript's no-dash convention; no words have been changed.*

[1] Chun, I., Choi, H., Jun, Y., Lee, S., Lee, H. (2026). High heat flux immersion cooling in
data centers: Quantitative bypass control and fluid-structure compatibility across dielectric
fluids and heat sink designs. Energy, 361, 141967.
https://doi.org/10.1016/j.energy.2026.141967

[2] Huang, Y., Liu, B., Xu, S., Bao, C., Zhong, Y., Zhang, C. (2024). Experimental study on the
immersion liquid cooling performance of high-power data center servers. Energy, 297, 131195.
https://doi.org/10.1016/j.energy.2024.131195

[3] Kim, J., Choi, H., Lee, S., Lee, H. (2025). Computational study of single-phase immersion
cooling for high-energy density server rack for data centers. Applied Thermal Engineering, 264,
125476. https://doi.org/10.1016/j.applthermaleng.2025.125476

[4] Sun, X., Liu, Z., Ji, S., Yuan, K. (2025). Experimental study on thermal performance of a
single-phase immersion cooling unit for high-density computing power data center. International
Journal of Heat and Fluid Flow, 112, 109735.
https://doi.org/10.1016/j.ijheatfluidflow.2024.109735

[5] Shrigondekar, H., Lin, Y.-C., Wang, C.-C. (2023). Investigations on performance of
single-phase immersion cooling system. International Journal of Heat and Mass Transfer, 206,
123961. https://doi.org/10.1016/j.ijheatmasstransfer.2023.123961

[6] Zhang, Y.-D., Lin, Y.-C., Wang, C.-C. (2024). Investigation of the single-phase immersion
cold plate amid PAO-4 and Noah@3000A: An experimental approach and its numerical verification.
International Communications in Heat and Mass Transfer, 155, 107509.
https://doi.org/10.1016/j.icheatmasstransfer.2024.107509

[7] Zhang, B., Li, H., Xu, T., Wang, L., Chen, L., Li, Z. (2026). Integrated CFD modeling and
experimental validation of single-phase immersion cooling for data center thermal management.
Energy, 347, 140315. https://doi.org/10.1016/j.energy.2026.140315

[8] Khoshvaght-Aliabadi, M., Ghodrati, P., Nasrolahzadeh, A., Kang, Y.T. (2025). Optimization of
heat sinks for data center server CPUs cooled via single-phase immersion cooling. Applied
Thermal Engineering, 280, 127790. https://doi.org/10.1016/j.applthermaleng.2025.127790

[9] Khoshvaght-Aliabadi, M., Nasrolahzadeh, A., Ghodrati, P., Kang, Y.T. (2026). Oblique-fin
heat sink design for uniform CPU cooling in immersion-cooled servers. Applied Thermal
Engineering, 288, 129628. https://doi.org/10.1016/j.applthermaleng.2025.129628

[10] Khoshvaght-Aliabadi, M., Hojjati, F., Hassani, S. (2026). Influence of component
arrangement on thermal management in immersion-cooled server boards. Energy, 347, 140323.
https://doi.org/10.1016/j.energy.2026.140323

[11] Ni, D., Yu, F. (2024). CFD simulation study of flow equalisation plate model in
single-phase immersion liquid cooling for servers. Thermal Science and Engineering Progress,
47, 102268. https://doi.org/10.1016/j.tsep.2023.102268

[12] Dong, Q., Xu, S., Wu, S., Zhang, C., Wang, Q. (2026). Thermal management architecture
optimization for single-phase immersion liquid cooling. Applied Thermal Engineering, 298,
130997. https://doi.org/10.1016/j.applthermaleng.2026.130997

[13] Muneeshwaran, M., Lin, Y.-C., Wang, C.-C. (2023). Performance analysis of single-phase
immersion cooling system of data center using FC-40 dielectric fluid. International
Communications in Heat and Mass Transfer, 145, 106843.
https://doi.org/10.1016/j.icheatmasstransfer.2023.106843

[14] Jeng, T.-M. (2008). A porous model for the square pin-fin heat sink situated in a
rectangular channel with laminar side-bypass flow. International Journal of Heat and Mass
Transfer, 51, 2214-2226. https://doi.org/10.1016/j.ijheatmasstransfer.2007.11.018

[15] Cai, H., Su, L., Liao, Y., Weng, Z. (2019). Numerical and experimental study on the
influence of top bypass flow on the performance of plate fin heat exchanger. Applied Thermal
Engineering, 146, 356-363. https://doi.org/10.1016/j.applthermaleng.2018.10.007
*(Note: the running header on every page prints volume 146 (2019); the embedded PDF metadata
prints 2018, and the acceptance date is October 2018. The printed running header is used here.)*

[16] Min, J.Y., Jang, S.P., Kim, S.J. (2004). Effect of tip clearance on the cooling performance
of a microchannel heat sink. International Journal of Heat and Mass Transfer, 47, 1099-1103.
https://doi.org/10.1016/j.ijheatmasstransfer.2003.08.020

[17] Sastre, F., Valeije, A., Martin, E., Velazquez, A. (2018). Experimental and numerical study
on the flow topology of finned heat sinks with tip clearance. International Journal of Thermal
Sciences, 132, 146-160. https://doi.org/10.1016/j.ijthermalsci.2018.05.036

[18] Mei, D., Lou, X., Qian, M., Yao, Z., Liang, L., Chen, Z. (2014). Effect of tip clearance on
the heat transfer and pressure drop performance in the micro-reactor with micro-pin-fin arrays
at low Reynolds number. International Journal of Heat and Mass Transfer, 70, 709-718.
https://doi.org/10.1016/j.ijheatmasstransfer.2013.11.060

[19] Shahsavar, A., Shahmohammadi, M., Askari, I.B. (2021). CFD simulation of the impact of tip
clearance on the hydrothermal performance and entropy generation of a water-cooled pin-fin heat
sink. International Communications in Heat and Mass Transfer, 126, 105400.
https://doi.org/10.1016/j.icheatmasstransfer.2021.105400

---

## Drafting notes (not part of the manuscript text)

Recorded here so the next agent does not have to re-derive them.

1. **Correction to the task brief's framing of the bypass papers.** The Stage 4 task
   specification described all six bypass/tip-clearance papers as air-side, developed near
   Pr 0.7. That is not what the sources say. Only `jeng-porous-pin-fin-bypass` (air, Pr not
   printed) and `cai-su-liao-weng-top-bypass-plate-fin` (air, Pr 0.702 and 0.699 printed in its
   Table 1) are air-side. `min-jang-kim-tip-clearance` (water, silicon sink),
   `sastre-valeije-martin-velazquez-tip-clearance` (water),
   `mei-lou-qian-yao-liang-chen-micro-pin-fin-tip-clearance` (deionized water) and
   `shahsavar-shahmohammadi-askari-tip-clearance-entropy` (pure water, properties printed:
   rho 998.1, k 0.6, cp 4162, mu 0.001003, giving Pr about 6.96) all use water. The text above
   states this accurately and makes the stronger, still-true argument: this corpus's
   bypass literature spans Pr from about 0.7 to about 7, while its dielectric coolants span
   Pr from 19.8 to 905.

2. **Prandtl and viscosity ranges are quoted from a printed table, not derived here.** Pr 19.76
   (SS110) to 905.31 (DC-550), with FC-40 at 45.755 and PAO-6 at 358.67, are read directly from
   Table 2 of `zhang-b-cfd-immersion-validation` (Energy 347, 140315). This avoids relying on any
   property value evaluated by this pipeline. The dynamic-viscosity span is the same table's
   mu column (FC-40 0.00273 Pa s, DC-550 0.07846 Pa s) against the air viscosity printed in
   Cai et al.'s Table 1 (1.89e-5 Pa s), giving ratios of roughly 145 and 4150.

3. **Disputed figures avoided.** Per D-005, `vagiakis-korres-tzivanidis-natural-convection` and
   its 883 W / 833 W internal inconsistency are not cited at all. Per D-008, the FC-40 property
   correlation shared between `khoshvaght-aliabadi-heatsink-optimisation` and
   `khoshvaght-aliabadi-oblique-fin` is not cited, and neither paper is cited for property
   provenance; they are cited only for their geometry-optimisation contributions. Per D-006,
   `khoshvaght-aliabadi-heatsink-optimisation` is described as a numerical design of
   experiments and is not claimed to be experimentally validated.

4. **Anchor numbers verified against the PDF, not only the extraction record.** The GC-5X versus
   FC-40 inversion is not present in `extraction/chun-immersion-bypass-anchor.md`; it was
   verified directly against the anchor PDF. Bypass fractions of 48.41% / 89.69% at OR 100%,
   36.65% / 67.20% at OR 50% and 0.78% / 0.79% at OR 0% are Table 6 of the anchor. The 45.6%
   versus 6.1% thermal resistance reductions, the roughly 23.0 K penalty at OR 100%, and the
   inversion sentence ("at OR 0% where the bypass path is completely blocked, GC-5X achieves a
   lower chip temperature than FC-40, resulting in a performance inversion") are on the two
   pages that follow.

5. **Basis for the "no predictive framework" claim.** Verified by reading every N, N+E and N+E'
   immersion extraction record plus targeted PDF checks: the anchor calls its own open-ratio
   definition geometry-specific and its future-work list contains no correlation;
   `dong-xu-wu-zhang-wang-architecture-optimisation` lists a dimensionless Nu-Re-Pr correlation
   as future work in its own conclusions; `mei-lou-qian-yao-liang-chen` has clearance-ratio
   correlations but for deionized water and without predicting the flow split. No corpus paper
   predicts the bypass split.

6. **Not cited, and why.** `cheng-ijhmt160-immersion-design`, `huang-ijhmt207-natural-forced-
   convection`, `kewalramani-hedau-saha-agrawal-pin-fin-friction-nusselt`,
   `lee-garimella-microchannel-developing-flow` and `zhang-b`'s fin-optimisation sub-study are
   all legitimate corpus papers but did not carry an argument this section needed. The last two
   are validation-ladder rungs and belong in Section 2, not here.
