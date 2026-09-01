# New citations needed for Sections 2 and 3

Written by the Stage 4 agent drafting `sections/problem_formulation.tex` (Section 2) and
`sections/numerical_method.tex` (Section 3). `references.bib` was **not** edited, per the brief.

Sections 2 and 3 use 20 distinct `\cite{}` keys. Seventeen already exist in
`manuscript/references.bib` and are used unchanged:

`cai2019`, `chun2026`, `dong2026`, `jeng2008`, `khoshvaghtaliabadi2025`,
`khoshvaghtaliabadi2026component`, `khoshvaghtaliabadi2026oblique`, `kim2025`, `mei2014`,
`min2004`, `muneeshwaran2023`, `ni2024`, `sastre2018`, `shahsavar2021`, `shrigondekar2023`,
`zhang2024pao4`, `zhang2026`.

Three keys are new. **All three are already requested, with identical keys and identical
bibliographic data, in the sibling file `new_citations_needed_s4.md`** written by the agent
drafting Section 4. There is no key collision and no conflicting entry; this file records the
independent verification path taken here so the integrating process can see that two agents
arrived at the same entries by different routes.

Every field below was read directly out of the canonical UUID-linked PDF in `references/` by this
agent, not copied from an extraction record.

---

## 1. `huang2023ijhmt`

**Used in:** `numerical_method.tex`, Section 3.2 (adiabatic outer-wall condition for an immersion
tank) and Section 3.3 (the only paper in the surveyed set that writes a Boussinesq-form buoyancy
body force in its momentum equation, and the source of an expansion coefficient that is
deliberately *not* adopted here).

**Verified against:** `references/a9bbd285-53c5-419f-a583-7366211c5c7a.pdf`. Title, authors and
affiliations read from p.1; the load-bearing content read from rendered/extracted pp.4 and 5,
namely Table 1 (thermal expansion coefficient 0.0014 1/degC for the Fluorinert, 0.0018 1/degC for
water; density rho = 1878 minus 2.455T; boiling point 128 degC), assumption 5 on p.4 ("the
Boussinesq hypothesis is used to relate the Reynolds stresses to the mean velocity gradients",
i.e. the eddy-viscosity sense, not buoyancy), the momentum equation Eq. (9) on p.5 carrying the
buoyancy term `rho g theta xi` with xi defined in the text as the coefficient of thermal
expansion, and the outer-wall condition Eq. (12) on p.5.

```bibtex
@article{huang2023ijhmt,
  author  = {Huang, Yongping and Ge, Junlei and Chen, Yongping and Zhang, Chengbin},
  title   = {Natural and forced convection heat transfer characteristics of single-phase immersion cooling systems for data centers},
  journal = {International Journal of Heat and Mass Transfer},
  volume  = {207},
  pages   = {124023},
  year    = {2023},
  doi     = {10.1016/j.ijheatmasstransfer.2023.124023}
}
```

**Key choice:** `huang2023ijhmt` rather than a bare `huang2023`, because `references.bib` already
carries `huang2024energy` (Energy 297, 131195), a different paper by a different group.

**Caveat carried into the text:** the fluid in this paper is named only as a "fluorinert
electronic liquid" with no grade. Its printed boiling point of 128 degC rules out FC-40, whose
boiling point is 165 degC in three other sources, so its 0.0014 1/degC expansion coefficient is
recorded in Section 3.3 as checked and rejected, not adopted.

---

## 2. `lee2006`

**Used in:** `numerical_method.tex`, Section 3.4 (the thermally-developing-flow benchmark that
sets the lowest rung of the verification ladder) and in the survey of discretisation practice.

**Verified against:** `references/b58622c0-a9bc-4a55-a965-fbf974a82502.pdf`. Title, authors and
affiliation (Cooling Technologies Research Center, Purdue University) read from p.1. Journal,
volume, year and page range read from the running header printed on every page:
"International Journal of Heat and Mass Transfer 49 (2006) 3060-3067". DOI read from the
front-matter line on p.1: "doi:10.1016/j.ijheatmasstransfer.2006.02.011".

```bibtex
@article{lee2006,
  author  = {Lee, P.-S. and Garimella, S. V.},
  title   = {Thermally developing flow and heat transfer in rectangular microchannels of different aspect ratios},
  journal = {International Journal of Heat and Mass Transfer},
  volume  = {49},
  pages   = {3060--3067},
  year    = {2006},
  doi     = {10.1016/j.ijheatmasstransfer.2006.02.011}
}
```

**Disambiguation:** this is the "different aspect ratios" paper at pages 3060 to 3067, not the
frequently confused "arbitrary aspect ratio" paper at pages 1393 to 1403.

---

## 3. `kewalramani2019`

**Used in:** `numerical_method.tex`, Section 3.4. It is the strongest laminar determination in the
surveyed set, and it is the model this paper's own regime determination follows: the authors cite
a published laminar-to-unsteady transition near a pin Reynolds number of 640, note that their own
maximum is 275, and then run a steady against unsteady comparison at that maximum. Also cited in
Section 3.3 as the counter-case that neglects gravity outright on a micro-scale argument.

**Verified against:** `references/f1a5677a-9400-4d90-a683-8d0a048b1eb8.pdf`. Title, authors and
affiliation (Department of Mechanical Engineering, IIT Bombay) read from p.1. Journal, volume,
year and page range read from the printed header on p.1 and the running header on p.2:
"International Journal of Heat and Mass Transfer 138 (2019) 796-808". DOI read from the
front-matter line on p.1: "https://doi.org/10.1016/j.ijheatmasstransfer.2019.04.118".

```bibtex
@article{kewalramani2019,
  author  = {Kewalramani, G. V. and Hedau, G. and Saha, S. K. and Agrawal, A.},
  title   = {Study of laminar single phase frictional factor and {Nusselt} number in in-line micro pin-fin heat sink for electronic cooling applications},
  journal = {International Journal of Heat and Mass Transfer},
  volume  = {138},
  pages   = {796--808},
  year    = {2019},
  doi     = {10.1016/j.ijheatmasstransfer.2019.04.118}
}
```

**Note:** the printed title capitalises "In-line" mid-sentence. Lower-cased above for
bibliography consistency; restore the printed form if the integrating process prefers verbatim
titles. This matches the choice already made in `new_citations_needed_s4.md`.

---

## Preamble change also required

Both `problem_formulation.tex` and `numerical_method.tex` use booktabs rules (`\toprule`,
`\midrule`, `\bottomrule`) for five tables. `manuscript/main.tex` currently loads only `amsmath`,
`amssymb`, `textcomp` and `lmodern`, so the integrating process must add:

```latex
\usepackage{booktabs}
```

A header comment to that effect is at the top of each `.tex` fragment.
