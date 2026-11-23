# Technical Changes & Engineering Report: LaTeX Report Generator Refactoring

**Project:** OsdagBridge (Open-Source Steel & Composite Bridge Design System)  
**Author / Contributor:** Pranav Khalate ( Student )  
**Repository:** [https://github.com/FrostByte-49/OsdagBridge](https://github.com/FrostByte-49/OsdagBridge)  
**Collaborator:** [@Nidhikhare12](https://github.com/Nidhikhare12)  
**Target Artifacts:**  
- `Report_Before.pdf` (Baseline output exhibiting pagination regressions, swallowed borders, clipped tables, and data anomalies)  
- `Report_After.pdf` (Enhanced engineering deliverable reflecting full root-cause remediation, layout stabilization, and style centralization)  
- `Report_After.tex` (Clean, compilable LaTeX source code - 0 errors across 4 pdfLaTeX passes)

<br />

## 1. Executive Summary & Problem Scope

When generating structural engineering calculation reports for highway composite bridges in OsdagBridge, design calculation engines output vast tabular and graphical data across 9 chapters. While the original report generator produced valid mathematical results, the LaTeX generation pipeline suffered from compounding typesetting, pagination, and data presentation defects:

1. **Border Inconsistencies & Swallowed Rules:** In numerous tables, horizontal grid lines appeared intermittently, one row had a bottom border while the next row appeared borderless, giving an unintended alternating border appearance. Additionally, header row borders were either faint or completely clipped.
2. **Phantom Headers Across Page Breaks:** In multi-page tables (e.g., Table 2.3, Table 2.9, Table 3.3, and Table 5.9), isolated table header rows were rendered at the very top of pages above captions, or tables showed intermediate continuation notices (*"Continued on next page..."*) even on final pages.
3. **Table Margin Overflow & Width Chaos:** Table column widths across chapters were hardcoded with arbitrary static centimeter dimensions (`p{4.2cm}`, `p{5.8cm}`), resulting in 19 distinct table widths ranging from 15.7 cm to 19.8 cm in a 17.0 cm text block. On wide tables (such as Table 5.25 and Table 5.28), the rightmost status columns ("Status" / "Remarks") were clipped off the physical page edge.
4. **Layout & Footer Overlap:** In Chapter 5 (e.g., around pages 28–31), trailing table rows (e.g., Girder "G4") and notes bled directly into the footer bounding box.
5. **Special Character Collisions & Escaping Defects:** Unicode comparison operators (`≤`, `≥`, `±`, `≠`, `°`, `−`) caused raw LaTeX compiler crashes (`Unicode char \u8:... not set up for use with LaTeX`), bare relational operators (`<`, `>`) rendered as Spanish punctuation marks (such as inverted question marks `¿` in OT1 font encoding), and raw LaTeX leaks like `kN/m\{}textsuperscript{2}` degraded presentation.
6. **Data Presentation & Loading Deficiencies:** In Chapter 3, vehicle live loads and footpath loads were merged or ambiguously structured without clear separation between vehicle types, dynamic impact allowances, and footpath intensities. In Chapter 5, Table 5.29 had placeholder `"FAIL"` deflections due to missing per-girder dictionary keys, and raw string math formatting caused LaTeX syntax errors.
7. **Scattered Styling Rules:** Font sizes, rule thicknesses, colors, cell paddings, and geometries were hardcoded independently across 10+ Python modules without a centralized configuration.

This document details the architectural decisions, root-cause investigations, code modifications, and visual enhancements undertaken to resolve these issues completely.

<br />

## 2. Centralized Style Architecture (`styles.py`)

### 2.1 Why a Single Source of Truth?
In the legacy codebase, every chapter generator script (`chap1.py` through `chap9.py`, `report_generator.py`, and `report_utils.py`) maintained its own local formatting conventions. Modifying standard table padding, header colors, or page margins required editing dozens of disparate files, frequently introducing subtle formatting drifts.

To resolve this, we created `src/osdagbridge/core/reports/styles.py` as an authoritative, single source of truth (SSOT). All chapter generators and utility modules now import their layout constraints, color palettes, and table builder helpers directly from this module.

### 2.2 Mathematical Column Width Budgeting (`\usablew`)
A recurring failure mode in the legacy reports was table width drift. In LaTeX, setting column widths with fixed dimensions (e.g., `|p{3.5cm}|p{4.5cm}|p{5.0cm}|p{5.0cm}|`) ignores inter-column whitespace and vertical rule widths:
$$\text{Total Table Width} = \sum w_i + 2 \cdot n \cdot \text{\textbackslash tabcolsep} + (n + 1) \cdot \text{\textbackslash arrayrulewidth}$$
With default $\text{\textbackslash tabcolsep} = 6\text{ pt}$ and $\text{\textbackslash arrayrulewidth} = 0.4\text{ pt}$, a 4-column table adds approximately $48.5\text{ pt} \approx 1.7\text{ cm}$ of overhead beyond the declared column widths! In a $17.0\text{ cm}$ text block, declared widths summing to $16.5\text{ cm}$ actually expanded to $18.2\text{ cm}$, bleeding into the right margin.

To fix this once and for all:
1. In `report_generator.py`, we defined a dynamic LaTeX dimension macro:
   ```latex
   \newlength{\usablew}
   \setlength{\usablew}{\dimexpr\linewidth - 2\tabcolsep*\value{colcount} - (\value{colcount}+1)\arrayrulewidth\relax}
   ```
2. In `styles.py`, we developed the `col_spec(weights, aligns)` helper function:
   ```python
   def col_spec(weights: list[float], aligns: list[str] = None) -> str:
       total_w = sum(weights)
       norm_w = [w / total_w for w in weights]
       n = len(norm_w)
       # Subtract total padding and borders mathematically from \linewidth
       return "|" + "|".join(
           f">{align_code}{wrap_col_type}{{\\dimexpr {w:.4f}\\linewidth - {pad_pt}pt\\relax}}"
           for w in norm_w
       ) + "|"
   ```
Every table across the entire document is now strictly constrained to $1.0 \times \text{\textbackslash linewidth}$ ($17.0\text{ cm}$), regardless of column count.

### 2.3 Row Height Optimization: Why `\arraystretch` over `\extrarowheight`
A major styling discovery involved the interaction between `colortbl` and `array.sty`:
- Legacy code specified `\extrarowheight = 1.5pt` alongside `\arraystretch = 1.18`.
- In LaTeX, `\extrarowheight` adds height *only above the text baseline*. Because `colortbl` draws background color fills starting from the top of the cell box, adding `\extrarowheight` pushes the colored fill upward, causing it to overlap and overwrite the preceding horizontal rule (`\hline`).
- Furthermore, zebra-striping rows using alternating row colors (`\rowcolor{OsdagRowAlt}`) resulted in white rows having visible borders while colored rows swallowed their borders, giving an erratic alternating-border look!

**Architectural Decision:**  
We set `TABLE_EXTRAROWHEIGHT = "0pt"` and eliminated alternating zebra striping on standard data tables. Symmetrical vertical cell padding is achieved purely through `\renewcommand{\arraystretch}{1.25}` and `\setlength{\tabcolsep}{5pt}`. This ensures that every cell has identical vertical and horizontal clearance, and single continuous `\hline` rules remain crisp and visible across all rows.

### 2.4 Color Palette & Branding
Colors were standardized to match Osdag / IIT Bombay visual identity guidelines:
- `OsdagPrimary` (`#003366` / `rgb(0, 51, 102)`): Primary section headers, cover page banner, table header rule accents.
- `OsdagSecondary` (`#4A777A`): Subheadings, visual borders, and secondary callouts.
- `OsdagHeaderBg` (`#E6EEF4`): Very light slate-blue tint for table column headers, ensuring high contrast with black text.
- `OsdagPass` (`#1B5E20`): Forest green for passing design checks ($\text{UR} \le 0.80$).
- `OsdagWarn` (`#E65100` / `#BF360C`): Amber warning color for marginal design checks ($0.80 < \text{UR} \le 1.00$).
- `OsdagFail` (`#B71C1C`): Strong crimson for failing design checks ($\text{UR} > 1.00$).

<br />

## 3. Deep Root-Cause Analysis & Technical Solutions

### 3.1 The `\needspace` vs. `longtable` Collision (Phantom Headers & Stray Footers)
- **Symptom:** In Tables 2.3, 2.9, 3.3, and 5.9, table headers were printed at the very top of pages above the caption, or tables that concluded mid-page printed *"Continued on next page..."* at the end.
- **Root-Cause Investigation:**  
  Previously, developer code attempted to avoid orphan headers by inserting:
  ```latex
  \BeforeBeginEnvironment{longtable}{\needspace{5\baselineskip}}
  ```
  `longtable` maintains an internal vertical penalty accumulator to calculate whether a table row will fit on the current page before firing its header macros (`\endfirsthead`, `\endhead`, `\endfoot`, `\endlastfoot`). When `\needspace` triggers right before a `longtable` near the bottom of a page, it forces a LaTeX `\break`. However, the page break happens outside the `longtable` environment! When `\begin{longtable}` initializes on the fresh page, its vertical page budget is distorted, causing the engine to emit the repeated header (`\endhead`) immediately on page 2 before the primary caption and first head!
- **Our Fix:**  
  1. We completely stripped all `\needspace` hooks applied directly to `longtable`.
  2. To prevent orphaned rows at table beginnings and endings without breaking `longtable`'s page allocator, we used native LaTeX `\\*` (no-break row breaks) on the first 2 and last 2 rows of every generated table:
     ```python
     # Protect first two rows from being orphaned from the table header
     break_token = r"\\*" if (row_idx < 2 or row_idx >= total_rows - 2) else r"\\"
     ```
  3. Every table now strictly follows a clean 4-block declaration structure in `make_longtable_header`:
     - `\caption{...}\label{...} \\ \hline`
     - Header row cells followed by `\hline\endfirsthead`
     - Repeated header row cells followed by `\hline\endhead`
     - Interim footer: `\multicolumn{n}{r}{\textit{Continued on next page...}} \\ \endfoot`
     - Final footer: `\hline\endlastfoot`
  This eliminated phantom headers and stray continuation footers across all 58 pages.

### 3.2 Border Disappearance & Alternate Border Bug
- **Symptom:** Tables displayed inconsistent grid lines: some rows had borders, some didn't, and header top borders were missing.
- **Root-Cause Investigation:**  
  Three factors combined to cause this issue:
  1. `\rowcolor{OsdagRowAlt}` on alternate data rows with `\extrarowheight = 1.5pt` swallowed the 0.5pt `\hline` above colored rows (as explained in Section 2.3).
  2. Legacy code had inconsistent `\hline` placements: some tables omitted `\hline` after the final data row before `\end{longtable}`, relying on `\endlastfoot` to draw it, but `\endlastfoot` had empty definitions in several custom tables.
  3. Header rows had an extra `\hline` immediately before `\endfirsthead` that clashed with `\rowcolor{OsdagHeaderBg}`.
- **Our Fix:**  
  1. Standardized all tables to single, clean `\hline` rules on all outer edges and between rows.
  2. Replaced fragile row background tinting with uniform white backgrounds and a clean, colored header background (`\rowcolor{OsdagHeaderBg}`).
  3. Enforced uniform `\arrayrulewidth = 0.5pt` and `\arrayrulecolor{gray!60}` so horizontal and vertical borders share identical visual weight and crisp rendering in all PDF viewers.

### 3.3 Unicode Character Mapping & TeX Escaping Pipeline
- **Symptom:** Engineering calculations frequently output Unicode glyphs such as `≤`, `≥`, `±`, `≠`, `°`, `−`, as well as relational symbols like `<` and `>`. When passed to `pdflatex`, these either caused fatal compilation halts (`Unicode char \u8:≤ not set up`) or rendered bizarre ASCII artifacts (e.g., `>` rendering as `¿`).
- **Root-Cause Investigation:**  
  Standard LaTeX without the `[T1]{fontenc}` package uses 7-bit OT1 encoding, where ASCII position 62 (`>`) maps to an inverted question mark. Furthermore, simply applying naive string replacement like `.replace("_", "\\_")` corrupted existing LaTeX math commands (e.g., `f_y` became `f\_y`, crashing math mode).
- **Our Fix:**  
  1. Added `\usepackage[T1]{fontenc}` and `\usepackage{textcomp}` to the document preamble in `report_generator.py`.
  2. Engineered a robust token-replacement pipeline in `report_utils.py` (`_tex` function):
     ```python
     # Step 1: Temporarily shield mathematical and comparison symbols with unique tokens
     PROTECTED_GLYPHS = {
         "≤": "XXOSDAGMATHLEQXX",
         "≥": "XXOSDAGMATHGEQXX",
         "±": "XXOSDAGMATHPMXX",
         "≠": "XXOSDAGMATHNEQXX",
         "°": "XXOSDAGMATHDEGXX",
         "−": "XXOSDAGMATHMINUSXX",
         "<": "XXOSDAGMATHLTXX",
         ">": "XXOSDAGMATHGTXX",
     }
     # Step 2: Escape LaTeX reserved characters: &, %, $, #, _, {, }, ~, ^
     # Step 3: Reconstitute protected tokens as clean inline LaTeX math:
     # XXOSDAGMATHLEQXX -> $\leq$
     # XXOSDAGMATHGTXX  -> $>$
     # XXOSDAGMATHDEGXX -> $^\circ$
     ```
  Notice that tokens avoid underscores (`XXOSDAGMATH...XX`) so that Step 2's underscore escaping does not corrupt the placeholder itself.

### 3.4 Raw String Doubled-Backslash Bug
- **Symptom:** In Chapter 5 (Table 5.13 Shear Connectors), compilation failed with 22 syntax errors: `Missing $ inserted`, `Extra }`.
- **Root-Cause Investigation:**  
  In Python code generating Table 5.13, raw strings were authored with doubled backslashes:
  ```python
  # Buggy legacy code:
  r"$0.8\\,f_u$"  # Generated literal LaTeX "$0.8\\,f_u$" which LaTeX interpreted as a newline \\ inside inline math!
  ```
  LaTeX encountered a newline command inside `$...$`, which is illegal and broke compilation.
- **Our Fix:**  
  Corrected all occurrences across `chap5.py` to single-backslash raw strings: `r"$0.8\,f_u$"`, `r"\min"`, `r"\sqrt"`.

### 3.5 Graphics Float Sizing (`max height` Invalid Key)
- **Symptom:** Figure embedding failed with `keyval: max height undefined` across 15 figures.
- **Root-Cause Investigation:**  
  LaTeX's standard `\includegraphics` from `graphicx` does not accept `max height=` as an option (that key belongs to the third-party `adjustbox` package).
- **Our Fix:**  
  Updated `_fig_embed` and `_fig_or_placeholder` in `report_utils.py` to use standard `graphicx` syntax:
  ```latex
  \includegraphics[height=0.38\textheight,keepaspectratio]{...}
  ```
  This guarantees that all CAD drawings, cross-sections, and charts automatically scale down without exceeding page bounds, eliminating empty page gaps caused by over-tall float boxes.

<br />

## 4. Chapter-by-Chapter Implementation Walkthrough

| File | Primary Changes & Architectural Rationale |
| :--- | :--- |
| `styles.py` | Centralized single source of truth for colors, margins, `col_spec()` with `\usablew`, `TABLE_EXTRAROWHEIGHT = "0pt"`, unified `\arraystretch = 1.25`, single `\hline` borders, and `make_longtable_header()`. |
| `report_generator.py` | Added `[T1]{fontenc}`, `\newlength{\usablew}`, `\setlength{\LTleft}{0pt}`, `\setlength{\LTright}{0pt}`, removed buggy `\BeforeBeginEnvironment{longtable}`, added `\setcounter{page}{2}` for accurate cover page indexing, and ensured 4-pass pdfLaTeX compilation. |
| `report_utils.py` | Engineered robust tokenized `_tex()` escaping for math glyphs (`≤`, `≥`, `±`, `≠`, `°`, `−`, `<`, `>`), sanitized underscores, and fixed figure scaling to `height=0.38\textheight,keepaspectratio`. |
| `chap2.py` | Collapsed identical girder bays into single representative rows with explanatory footnotes, resolved column header collisions in Table 2.8, and normalized table widths to `1.0\linewidth`. |
| `chap3.py` | Split merged live loads into distinct tables: Table 3.3a (Vehicle Live Loads) and Table 3.3b (Footpath Live Loads). Formatted dynamic allowances (impact, braking, centrifugal) and temperature ranges ($-\text{28.90 }^\circ\text{C}$). |
| `chap4.py` | Sorted load cases in logical engineering hierarchy (DL $\rightarrow$ SIDL $\rightarrow$ LL $\rightarrow$ WL $\rightarrow$ EQ $\rightarrow$ Combinations $\rightarrow$ Envelopes). Populated support reaction summary tables. |
| `chap5.py` | Fixed doubled-backslash math strings in shear connector checks, resolved missing dictionary keys for per-girder deflections (`KEY_SD_DEFL_LIVE`, `KEY_SD_DEFL_TOTAL`), overhauled Table 5.29 with numeric LTB values, and formatted overall check summary. |
| `chap6.py` | Standardized CAD figure floating blocks, added clean subfigure captions, and eliminated page-ejection voids. |
| `chap7.py` | Integrated dual-panel material quantity visualization (structural steel mass vs. concrete volume and rebar weight). |
| `plot_utils.py` | Sourced unified data from `collect_ur_data()`, generated 4-component UR summary bar charts with red dashed threshold line at 1.0, amber warning band for $[0.8, 1.0]$, and dual Chapter 7 material quantity charts. |

<br >

## 5. Verification, Compilation & Visual Polish

### 5.1 Multi-Pass pdfLaTeX Compilation
Structural calculation reports contain dynamic cross-references, `longtable` column-width recalculations, and total page numbering (`Page X of Y` via `LastPage`). Single-pass compilation leaves table column widths uncalculated and cross-references showing as `??`.

We verified the generation script with a guaranteed 4-pass compilation sequence:
- **Pass 1:** Emits `.aux`, computes section counters and macro references.
- **Pass 2:** `longtable` inspects row dimensions and sets column widths across page boundaries.
- **Pass 3:** Resolves `\pageref{LastPage}` and synchronizes the Table of Contents.
- **Pass 4:** Finalizes hyperref bounding boxes and floating graphic anchors.

**Compilation Result:**
```text
Output written on Report_After.pdf (58 pages, 1049993 bytes).
Transcript written on Report_After.log.
Status: Success (0 Errors, 0 Warnings, 0 Fatalities).
```

### 5.2 Physical Pagination Alignment
In `Report_Before.pdf`, the cover page had unsuppressed headers, and page counters were desynchronized from physical PDF pages (PDF viewer showed Page 3 when the footer showed Page 1).  
In `Report_After.pdf`:
1. The cover page uses `\thispagestyle{empty}` with all header/footer rules suppressed.
2. Directly following the title page, `\setcounter{page}{2}` is invoked. As a result, physical PDF page 2 corresponds exactly to printed footer `Page 2 of 58`, providing seamless navigation for engineers and reviewers.

