# =============================================================================
# OsdagBridge Report Generator - Centralized Styling & Theme Configuration
# Single Source of Truth for LaTeX Layout, Colors, Typography, & Table Metrics
# =============================================================================

# --- Color Palette (HTML hex definitions) ---
COLOR_PRIMARY       = "003366"   # Deep Navy / Primary Brand
COLOR_SECONDARY     = "4A777A"   # Slate Teal Accent
COLOR_OSDAG_GREEN   = "91B014"   # Osdag Green Branding
COLOR_HEADER_BG     = "E6EEF4"   # Soft Blue-Grey for Table Headers
COLOR_HEADER_TEXT   = "002244"   # Dark Header Text
COLOR_ROW_ALT       = "F8FAFC"   # Alternating Row Tint
COLOR_BORDER        = "CCCCCC"   # Neutral Border Gray
COLOR_PASS          = "1B5E20"   # Dark Green for Passed Checks
COLOR_FAIL          = "B71C1C"   # Dark Red for Failed Checks
COLOR_WARNING       = "E65100"   # Orange / Warning
COLOR_THRESHOLD     = "D32F2F"   # Red dashed line for UR = 1.0
COLOR_WARN          = "E65100"   # Amber/Orange for 0.8 <= UR <= 1.0

# Matplotlib-safe hex strings (with #) — imported by plot_utils.py
MPL_COLOR_PRIMARY   = "#" + COLOR_PRIMARY
MPL_COLOR_SECONDARY = "#" + COLOR_SECONDARY
MPL_COLOR_PASS      = "#" + COLOR_PASS
MPL_COLOR_FAIL      = "#" + COLOR_FAIL
MPL_COLOR_THRESHOLD = "#" + COLOR_THRESHOLD
MPL_COLOR_WARN      = "#" + COLOR_WARN
MPL_COLOR_HEADER_BG = "#" + COLOR_HEADER_BG
MPL_COLOR_BORDER    = "#" + COLOR_BORDER

# --- Page Geometry & Spacing Settings ---
PAGE_GEOMETRY = {
    "a4paper": True,
    "top":        "2.2cm",
    "bottom":     "2.8cm",   # Generous margin preventing footer bleed
    "left":       "2.0cm",
    "right":      "2.0cm",
    "headheight": "16pt",
    "headsep":    "0.6cm",
    "footskip":   "1.3cm",   # Extra foot skip preventing text overlap
}

# --- Table Dimensions & Formatting ---
TABLE_ARRAYSTRETCH   = 1.25    # Vertical row breathing space
TABLE_TABCOLSEP      = "5pt"   # Horizontal column padding
TABLE_EXTRAROWHEIGHT = "0pt"   # Must be 0pt so colortbl does not overlap or swallow \hline
TABLE_ARRAYRULEWIDTH = "0.5pt"

# --- Standard longtable geometry ---
LT_PRE  = "0pt"
LT_POST = "6pt"

# --- Figure defaults ---
FIG_PLACEMENT     = "!htbp"
FIG_DEFAULT_WIDTH = r"0.9\textwidth"
FIG_MAX_HEIGHT    = r"0.38\textheight"

# --- Code version registry — single source for Chapters 1, 8, 9 ---
CODE_VERSIONS = {
    "IRC 5":   {"year": "2015", "title": "Standard Specifications and Code of Practice for Road Bridges, Section I --- General Features of Design"},
    "IRC 6":   {"year": "2017", "title": "Standard Specifications and Code of Practice for Road Bridges, Section II --- Loads and Load Combinations"},
    "IRC 22":  {"year": "2015", "title": "Standard Specifications and Code of Practice for Road Bridges, Section VI --- Composite Construction (Limit State Design)"},
    "IRC 24":  {"year": "2010", "title": "Standard Specifications and Code of Practice for Road Bridges, Section V --- Steel Road Bridges (Limit State Method)"},
    "IRC 112": {"year": "2020", "title": "Code of Practice for Concrete Road Bridges"},
    "IRC SP 114": {"year": "2018", "title": "Guidelines for Seismic Design of Road Bridges"},
    "IS 456":  {"year": "2000", "title": "Plain and Reinforced Concrete --- Code of Practice"},
    "IS 800":  {"year": "2007", "title": "General Construction in Steel --- Code of Practice"},
    "IS 1786": {"year": "2008", "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement"},
    "IS 1893 (Part 3)": {"year": "2014", "title": "Criteria for Earthquake Resistant Design of Structures, Part 3: Bridges and Retaining Walls"},
    "IS 2062": {"year": "2011", "title": "Hot Rolled Medium and High Tensile Structural Steel --- Specification"},
    "IS 6006": {"year": "2014", "title": "Specification for Uncoated Stress Relieved Strand for Prestressed Concrete"},
}


# =============================================================================
# LaTeX helper functions
# =============================================================================

def get_caption_setup():
    """Return unified caption setup for standardizing Table and Figure captions."""
    return r"""
\usepackage{caption}
\captionsetup{
    labelfont=bf,
    labelsep=colon,
    justification=centering,
    singlelinecheck=false,
    format=plain
}
\captionsetup[table]{name=Table}
\captionsetup[figure]{name=Figure}
"""


def get_geometry_latex():
    """Return LaTeX \\geometry command string."""
    return (
        f"\\usepackage[a4paper, "
        f"top={PAGE_GEOMETRY['top']}, "
        f"bottom={PAGE_GEOMETRY['bottom']}, "
        f"left={PAGE_GEOMETRY['left']}, "
        f"right={PAGE_GEOMETRY['right']}, "
        f"headheight={PAGE_GEOMETRY['headheight']}, "
        f"headsep={PAGE_GEOMETRY['headsep']}, "
        f"footskip={PAGE_GEOMETRY['footskip']}]{{geometry}}"
    )


def get_color_definitions():
    r"""Return LaTeX \definecolor statements for report colors."""
    return f"""
\\definecolor{{osdagGreen}}{{HTML}}{{{COLOR_OSDAG_GREEN}}}
\\definecolor{{OsdagPrimary}}{{HTML}}{{{COLOR_PRIMARY}}}
\\definecolor{{OsdagSecondary}}{{HTML}}{{{COLOR_SECONDARY}}}
\\definecolor{{OsdagHeaderBg}}{{HTML}}{{{COLOR_HEADER_BG}}}
\\definecolor{{OsdagRowAlt}}{{HTML}}{{{COLOR_ROW_ALT}}}
\\definecolor{{OsdagBorder}}{{HTML}}{{{COLOR_BORDER}}}
\\definecolor{{OsdagPass}}{{HTML}}{{{COLOR_PASS}}}
\\definecolor{{OsdagFail}}{{HTML}}{{{COLOR_FAIL}}}
\\definecolor{{OsdagThreshold}}{{HTML}}{{{COLOR_THRESHOLD}}}
\\definecolor{{OsdagWarn}}{{HTML}}{{{COLOR_WARN}}}
"""


def get_global_table_settings():
    """Return LaTeX global table spacing/padding setup (placed once in preamble)."""
    return (
        r"\setlength{\tabcolsep}{" + TABLE_TABCOLSEP + r"}" + "\n"
        r"\renewcommand{\arraystretch}{" + str(TABLE_ARRAYSTRETCH) + r"}" + "\n"
        r"\setlength{\LTpre}{" + LT_PRE + r"}" + "\n"
        r"\setlength{\LTpost}{" + LT_POST + r"}" + "\n"
        r"\setlength{\arrayrulewidth}{" + TABLE_ARRAYRULEWIDTH + r"}" + "\n"
        r"\setlength{\extrarowheight}{" + TABLE_EXTRAROWHEIGHT + r"}"
    )


def format_status(status_str):
    """Format status string with consistent theme colors (OsdagPass / OsdagFail / OsdagWarn)."""
    s = str(status_str).strip()
    if not s or s == "---":
        return "---"
    if "FAIL" in s.upper():
        return r"\textcolor{OsdagFail}{\textbf{FAIL}}"
    if "PASS" in s.upper():
        return r"\textcolor{OsdagPass}{\textbf{PASS}}"
    if "WARN" in s.upper():
        return r"\textcolor{OsdagWarn}{\textbf{WARN}}"
    return s


def format_ur(val):
    """Format UR with color coding (< 0.8 green, 0.8-1.0 amber/warn, > 1.0 red)."""
    try:
        f = float(val)
        s = f"{f:.2f}"
        if f > 1.0:
            return r"\textcolor{OsdagFail}{\textbf{" + s + r"}}"
        elif f >= 0.8:
            return r"\textcolor{OsdagWarn}{" + s + r"}"
        else:
            return r"\textcolor{OsdagPass}{" + s + r"}"
    except (TypeError, ValueError):
        return str(val) if val is not None else "---"


def col_spec(weights: list, aligns: list = None) -> str:
    """
    Build a LaTeX column spec where column widths are relative fractions of \\usablew.
    All weights are normalized to sum to 1.0 so the table exactly fills \\linewidth.
    """
    total = sum(weights) if weights else 1.0
    if total <= 0:
        total = 1.0
    norm_w = [w / total for w in weights]
    if aligns is None:
        aligns = ['C'] * len(weights)
    elif len(aligns) < len(weights):
        aligns = list(aligns) + ['C'] * (len(weights) - len(aligns))

    parts = []
    for w, a in zip(norm_w, aligns):
        al = str(a).upper()
        if al in ('L', 'P'):
            al_char = 'L'
        elif al == 'R':
            al_char = 'R'
        else:
            al_char = 'C'
        parts.append(f"{al_char}{{\\dimexpr{w:.4f}\\usablew\\relax}}")
    return "|" + "|".join(parts) + "|"


def _count_cols(col_spec_str: str) -> int:
    """Count the number of data columns in a LaTeX column spec string."""
    if "|" in col_spec_str:
        segs = [s.strip() for s in col_spec_str.strip("|").split("|") if s.strip()]
        return max(len(segs), 1)
    import re
    return max(len(re.findall(r'(?<!\{)[clrpCLRX](?!\})', col_spec_str)), 1)


def normalize_col_spec(spec: str) -> tuple[str, int]:
    """
    Convert any LaTeX col_spec (e.g. '|C{3cm}|L{5cm}|' or '|c|c|') into relative
    \\usablew fractions and return (normalized_spec, ncols).
    """
    import re
    if r"\usablew" in spec:
        ncols = _count_cols(spec)
        return spec, ncols

    tokens = [t.strip() for t in spec.strip("|").split("|") if t.strip()]
    if not tokens:
        return "|C{\\dimexpr1.0000\\usablew\\relax}|", 1

    weights = []
    aligns = []
    for tok in tokens:
        m = re.match(r"([A-Za-z])(?:\s*\{([0-9\.]+)\s*(?:cm|mm|pt|in)?\})?", tok)
        if m:
            al = m.group(1).upper()
            if al in ('L', 'P'):
                aligns.append('L')
            elif al == 'R':
                aligns.append('R')
            else:
                aligns.append('C')
            w_str = m.group(2)
            w = float(w_str) if w_str else 1.0
            weights.append(w)
        else:
            aligns.append('C')
            weights.append(1.0)

    ncols = len(weights)
    return col_spec(weights, aligns), ncols


def header_row(headers: list) -> str:
    """Format table header cells once: bold text with title capitalization."""
    return " & ".join(
        r"\textbf{" + str(h).strip().title() + r"}" for h in headers
    )


def themed_longtable(col_spec: str, headers: list, body_rows: list,
                     caption: str = "", label: str = "",
                     needspace_lines: int = 0) -> str:
    """
    Build a fully-compliant themed longtable LaTeX block.

    Guarantees:
    - Exactly \\linewidth wide (flush to left/right margins) via relative \\usablew.
    - Zero \\needspace before longtable (eliminating phantom headers & stray footers).
    - Header formatted once via header_row(), bold text, OsdagHeaderBg shading.
    - Heavier rule under header (\\hline\\hline).
    - First 2 rows and last 2 rows end with \\\\* (no page break) to avoid orphan rows.
    - Clean \\hline between rows, no duplicate trailing \\hline (closed by \\endlastfoot).
    - "Continued on next page..." footer with no side borders, only when continued.
    """
    # Auto-convert column spec to relative fractions of \usablew
    norm_spec, ncols = normalize_col_spec(col_spec)
    hdr_cells = header_row(headers)

    lines = []
    # Tables with more than 6 columns get tighter padding and footnotesize to stay within \linewidth
    is_wide = ncols > 6
    if is_wide:
        lines.append(r"{\begingroup\footnotesize\setlength{\tabcolsep}{3pt}")
        lines.append(f"\\setlength{{\\usablew}}{{\\dimexpr\\linewidth - 6pt * {ncols} - \\arrayrulewidth * {ncols + 1}\\relax}}")
    else:
        lines.append(f"\\setlength{{\\usablew}}{{\\dimexpr\\linewidth - \\tabcolsep * {2 * ncols} - \\arrayrulewidth * {ncols + 1}\\relax}}")

    lines.append(r"\begin{longtable}{" + norm_spec + r"}")

    # Caption on first page
    if caption:
        cap = r"\caption{" + caption.strip() + r"}"
        if label:
            cap += r"\label{" + label + r"}"
        lines.append(cap + r" \\")

    # First-page header
    lines.append(r"\hline")
    lines.append(r"\rowcolor{OsdagHeaderBg} " + hdr_cells + r" \\")
    lines.append(r"\hline")
    lines.append(r"\endfirsthead")

    # Continuation header (no duplicate caption)
    lines.append(r"\hline")
    lines.append(r"\rowcolor{OsdagHeaderBg} " + hdr_cells + r" \\")
    lines.append(r"\hline")
    lines.append(r"\endhead")

    # Interim footer — "Continued on next page..." only when not last page
    lines.append(r"\hline")
    lines.append(
        r"\multicolumn{" + str(ncols) + r"}{r}{\textit{\footnotesize Continued on next page...}} \\"
    )
    lines.append(r"\endfoot")

    # Final footer — single closing rule, no continuation text
    lines.append(r"\hline")
    lines.append(r"\endlastfoot")

    # Body rows — clean trailing \hline and \\, apply \\* to first/last 2 rows
    cleaned_rows = []
    for row in body_rows:
        r_ = row.strip()
        while r_.endswith(r"\hline"):
            r_ = r_[:-6].strip()
        if r_.endswith(r"\\*"):
            r_ = r_[:-3].strip()
        elif r_.endswith(r"\\"):
            r_ = r_[:-2].strip()
        if r_:
            cleaned_rows.append(r_)

    total_rows = len(cleaned_rows)
    for idx, r_ in enumerate(cleaned_rows):
        # Keep first 2 and last 2 rows from breaking across pages
        break_cmd = r"\\*" if (idx < 2 or idx >= total_rows - 2) else r"\\"
        lines.append(f"{r_} {break_cmd}")

        # Add \hline between rows, but NOT after the final row (closed by \endlastfoot)
        if idx < total_rows - 1:
            lines.append(r"\hline")

    lines.append(r"\end{longtable}")
    if is_wide:
        lines.append(r"\endgroup}")

    return "\n".join(lines)


def make_longtable_header(header_row_text, col_spec_str, caption=None, label=None):
    """
    Legacy helper — kept for backward compatibility.
    Prefer themed_longtable() for new code.
    """
    norm_spec, col_count = normalize_col_spec(col_spec_str)

    lines = []
    lines.append(f"\\setlength{{\\usablew}}{{\\dimexpr\\linewidth - \\tabcolsep * {2 * col_count} - \\arrayrulewidth * {col_count + 1}\\relax}}")
    lines.append(r"\begin{longtable}{" + norm_spec + r"}")
    if caption:
        cap = r"\caption{" + caption + r"}"
        if label:
            cap += r"\label{" + label + r"}"
        lines.append(cap + r" \\")

    lines.append(r"\hline")
    lines.append(r"\rowcolor{OsdagHeaderBg} " + header_row_text + r" \\")
    lines.append(r"\hline")
    lines.append(r"\endfirsthead")

    # Header on continued pages
    lines.append(r"\hline")
    lines.append(r"\rowcolor{OsdagHeaderBg} " + header_row_text + r" \\")
    lines.append(r"\hline")
    lines.append(r"\endhead")

    # Interim footer
    lines.append(r"\hline")
    lines.append(r"\multicolumn{" + str(col_count) + r"}{r}{\textit{\footnotesize Continued on next page...}} \\")
    lines.append(r"\endfoot")

    # Final footer
    lines.append(r"\hline")
    lines.append(r"\endlastfoot")

    return "\n".join(lines)
