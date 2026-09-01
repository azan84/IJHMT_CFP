# New citations needed for Section 4 (Verification and validation)

Written by the Stage 4 Section 4 agent, 2026-08-31. **`references.bib` was not edited** (another
process integrates file pieces). These are the entries `sections/verification_validation.tex`
cites that do not currently exist in `manuscript/references.bib`.

Keys already present in `references.bib` and reused unchanged by Section 4 (no action needed):
`chun2026`, `shrigondekar2023`, `zhang2024pao4`, `zhang2026`, `khoshvaghtaliabadi2025`,
`khoshvaghtaliabadi2026oblique`, `khoshvaghtaliabadi2026component`, `ni2024`, `dong2026`,
`jeng2008`, `cai2019`, `min2004`, `sastre2018`, `mei2014`, `shahsavar2021`, `kim2025`.

---

## 1. `kewalramani2019`

Verified against `extraction/kewalramani-hedau-saha-agrawal-pin-fin-friction-nusselt.md`
(front-matter `citation:`, transcribed from the canonical UUID PDF `f1a5677a`) and corroborated by
`validation/reconciled_T1.md`, which independently confirms the UUID PDF is the Kewalramani et al.
IJHMT 138 (2019) paper and cites journal pages 798 to 803 for its content.

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

Note: the extraction record transcribes the printed title with "In-line" capitalised mid-sentence.
Lower-cased above for bibliography consistency; restore the printed capitalisation if the
integrating process prefers verbatim titles.

---

## 2. `lee2006`

Verified against `extraction/lee-garimella-microchannel-developing-flow.md` and independently
re-confirmed in `validation/reconciled_T1.md`, which explicitly corrects a wrong bibliographic
line in `validation/agy_blind_triage.md`. The UUID PDF `b58622c0` is the "different aspect ratios"
paper at pages 3060 to 3067, **not** "arbitrary aspect ratio" at pages 1393 to 1403.

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

---

## 3. `cheng2020`

Verified against `extraction/cheng-ijhmt160-immersion-design.md` (UUID `983b608d`).

```bibtex
@article{cheng2020,
  author  = {Cheng, C.-C. and Chang, P.-C. and Li, H.-C. and Hsu, F.-I.},
  title   = {Design of a single-phase immersion cooling system through experimental and numerical analysis},
  journal = {International Journal of Heat and Mass Transfer},
  volume  = {160},
  pages   = {120203},
  year    = {2020},
  doi     = {10.1016/j.ijheatmasstransfer.2020.120203}
}
```

**Year warning.** `DECISIONS.md` D-010 records that an earlier extraction or triage pass introduced
**2023** for this paper. The correct year printed by the source is **2020**, matching the corpus
inventory table and the extraction record. Do not let a stale 2023 propagate into the bib.

---

## 4. `vagiakis2025`

Verified against `extraction/vagiakis-korres-tzivanidis-natural-convection.md` (UUID `1a92e523`).

```bibtex
@article{vagiakis2025,
  author  = {Vagiakis, A. and Korres, D. N. and Tzivanidis, C.},
  title   = {Simulation of natural convection heat transfer in dielectric liquids for single-phase immersion cooling rack server},
  journal = {Applied Thermal Engineering},
  volume  = {274},
  pages   = {126595},
  year    = {2025},
  doi     = {10.1016/j.applthermaleng.2025.126595}
}
```

Carry forward D-005: this paper states its thermal load as 883 W in the abstract and 833 W in the
body, and Codex's arithmetic check in `validation/reconciled_T4.md` confirms Table 4 sums to
832.8 W. Section 4 cites the paper only for its Geometry FAIL, so the disputed load number is not
used, but do not let any other section quote it without the caveat.

---

## 5. `huang2023ijhmt`

Verified against `extraction/huang-ijhmt207-natural-forced-convection.md` (canonical UUID
`a9bbd285`; duplicate `b8d2fd5a` retained on disk per D-002).

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

Key chosen as `huang2023ijhmt` to avoid collision with the existing `huang2024energy`
(Energy 297, 131195), which is a different paper by a different group.

---

## 6. `eca2014`

**Not a corpus paper. There is no extraction record and no PDF in `references/` for this one.**
It is the grid-convergence methodology citation required by Section 4.3.

Verification performed: web lookup on 2026-08-31, two independent sources agreeing.

1. OSTI bibliographic record 22314855 returns: Eça, L. and Hoekstra, M.; "A procedure for the
   estimation of the numerical uncertainty of CFD calculations based on grid refinement studies";
   *Journal of Computational Physics*; volume 262; 2014; DOI `10.1016/j.jcp.2014.01.006`. OSTI does
   not print a page range.
2. The page range **104--130** is corroborated by the titles of the published comment and reply
   papers in the same journal, both of which quote the parent article as "L. Eça and M. Hoekstra,
   Journal of Computational Physics 262 (2014) 104-130" verbatim in their own titles
   (*J. Comput. Phys.* 301, 484 and 301, 487).

Elsevier journal, so it satisfies the project's Elsevier-only reference constraint.

```bibtex
@article{eca2014,
  author  = {E\c{c}a, L. and Hoekstra, M.},
  title   = {A procedure for the estimation of the numerical uncertainty of {CFD} calculations based on grid refinement studies},
  journal = {Journal of Computational Physics},
  volume  = {262},
  pages   = {104--130},
  year    = {2014},
  doi     = {10.1016/j.jcp.2014.01.006}
}
```

**Honest caveat, flagged rather than buried.** Every other entry in this file was verified against a
UUID-linked PDF held by this project. This one was verified only by web lookup, and no PDF was
opened. The DOI, journal, volume and year are confirmed twice over; the page range rests on the
corroborating titles rather than on the article's own first page. If the integrating process wants
the same standard applied here as elsewhere, obtain the PDF and confirm the page range before the
manuscript is submitted. Section 4 does **not** mark this as
`[UNVERIFIED-CITATION]` because the work is real and its identifiers were independently confirmed;
this note records exactly how far that confirmation went.

---

## Markers left in Section 4 that are not citation problems

For completeness, so the integrating process does not mistake them for missing references:
Section 4 contains thirteen `[AWAITING-RESULTS: ...]` placeholders (grid convergence metrics,
whether a fourth mesh was required, closure residuals, four anchor-tier validation deviation cells,
five anchor-case deviation cells, and the sensitivity sweep outcomes). No `[UNVERIFIED-CITATION]`
markers were needed.
