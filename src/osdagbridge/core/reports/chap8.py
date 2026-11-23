from typing import List
from osdagbridge.core.reports.styles import themed_longtable, CODE_VERSIONS
from osdagbridge.core.reports.report_utils import _tex


def ch8_design_log(log_entries: List[str], input_dict: dict) -> str:
    """Render Chapter 8 Standards and Assumptions."""
    return _ch8_assumptions(input_dict)


def _ch8_assumptions(input_dict: dict) -> str:
    # Build Table 8.1 (IRC Codes) from CODE_VERSIONS
    irc_rows = []
    is_rows = []
    for code, info in CODE_VERSIONS.items():
        row = f"{_tex(code)} & {info['year']} & \\textit{{{_tex(info['title'])}}} \\\\"
        if code.startswith("IRC") or code.startswith("SP"):
            irc_rows.append(row)
        else:
            is_rows.append(row)

    t81 = themed_longtable(
        col_spec="|C{2.5cm}|C{1.8cm}|p{10.5cm}|",
        headers=["Code", "Year", "Title / Scope"],
        body_rows=irc_rows,
        caption="Indian Roads Congress (IRC) Design Standards",
        label="tab:irc-standards",
    )

    t82 = themed_longtable(
        col_spec="|C{2.5cm}|C{1.8cm}|p{10.5cm}|",
        headers=["Code", "Year", "Title / Scope"],
        body_rows=is_rows,
        caption="Bureau of Indian Standards (IS) Design Codes",
        label="tab:is-standards",
    )

    irc22_yr = CODE_VERSIONS.get("IRC 22", {}).get("year", "2015")
    irc6_yr  = CODE_VERSIONS.get("IRC 6", {}).get("year", "2017")
    irc112_yr = CODE_VERSIONS.get("IRC 112", {}).get("year", "2020")
    irc24_yr = CODE_VERSIONS.get("IRC 24", {}).get("year", "2010")
    is800_yr = CODE_VERSIONS.get("IS 800", {}).get("year", "2007")

    return r"""
\chapter{Standards \& Assumptions}
\label{ch:design-standards}

This section provides references to standards used to calibrate the OsdagBridge
design modules, and notes the limitations of the current software version.

\section{Design Standards}
\label{sec:design_standards}

The following Indian Road Congress (IRC) codes and Indian Standards (IS) 
form the basis of all design calculations in this software.

\vspace{0.4cm}
""" + t81 + r"""

\vspace{0.4cm}
""" + t82 + r"""

\section{Analysis and Design Assumptions of This Version}
\label{sec:design-assumptions}

\textbf{Structural Analysis}

\begin{itemize}
    \item All girders are modelled as simply supported; continuous spans are not currently supported.
    \item A 3D grillage model (OSPGrillage) is used for load distribution. Grillage members carry composite section properties after the construction stage.
    \item The transverse member forces are computed using an approximate 2D frame analogy. For irregular or skewed geometries, a 3D FEM is recommended.
    \item Fixed bearing stiffness is modelled as $k = 1{,}000{,}000 \,\text{kN/m}$ (virtually rigid); free/expansion bearing as $k = 100 \, \text{kN/m}$.
    \item Construction stage sequence analysis is approximate. Detailed staged analysis should be performed for long-term deflection checks.
\end{itemize}

\textbf{Composite Action}

\begin{itemize}
    \item Full shear connection is assumed at ULS with headed stud connectors designed per IRC """ + irc22_yr + r""" Cl.606.
    \item Short-term composite section properties (modular ratio $n = E_s/E_{cm}$) are used for ULS checks.
    \item Long-term composite section properties (with creep-adjusted modular ratio) are used for SLS deflection and crack-width checks.
    \item Pre-composite stage: the steel girder alone resists all construction loads prior to concrete gaining strength.
\end{itemize}

\textbf{Material Properties (IRC """ + irc22_yr + r""" Annex III)}

\begin{itemize}
\item Steel: $E_s = 200{,}000 \, \text{MPa}, \ G_s = 80{,}000 \, \text{MPa}, \ \nu = 0.30, \ \alpha = 11.7 \times 10^{-6}/^\circ\mathrm{C}$ (grade-independent).
\item Minimum structural concrete grade: M25.
\item Default reinforcement grade: Fe500.
\end{itemize}

\textbf{Partial Safety Factors (IRC """ + irc22_yr + r""" Cl.601.4)}

\begin{itemize}
\item $\gamma_{m0}$ (steel yield, ULS) = 1.10
\item $\gamma_{m1}$ (steel ultimate, ULS) = 1.25
\item Reinforcement (ULS) = 1.15
\item Welds --- shop: 1.25; field: 1.50
\item Fatigue ($\gamma_{mft}$) = 1.35
\end{itemize}

\textbf{Loading}

\begin{itemize}
\item Dead load densities per IRC """ + irc6_yr + r""" Cl.203: structural steel $78.5 \ \text{kN/m}^3$, concrete $25.0 \ \text{kN/m}^3$, bituminous wearing course $24.0 \ \text{kN/m}^3$.
\item Multi-lane live load reduction factors per IRC """ + irc6_yr + r""" Cl.204.4 Table 6A: 1st lane = 1.0, 2nd lane = 0.8, 3rd lane onwards = 0.4.
\item Impact factor (dynamic load allowance) computed from span per IRC """ + irc6_yr + r""" Cl.208.2/208.3.
\item Wind load applied as transverse, longitudinal, and vertical components per IRC """ + irc6_yr + r""" Cl.209.3.3--209.3.5.
\end{itemize}

\textbf{Serviceability Limits}

\begin{itemize}
\item Deflection limits (IRC """ + irc22_yr + r""" Cl.604.3.2): live load + impact $\leq L/800$; total $\leq L/600$.
\item SLS stress limits: concrete $\sigma_c \leq 0.48 f_{ck}$; rebar $\sigma_s \leq 0.80 f_{yk}$; steel $f_e \leq 0.9 f_y$.
\item Permissible crack width: $w_k \leq 0.3 \ \text{mm}$ (bridge deck, exposure class XS2/XD2 per IRC """ + irc112_yr + r""" Cl.12.3.2).
\end{itemize}

\textbf{Fatigue}

\begin{itemize}
\item Reference fatigue life: $N_{sc} = 2 \times 10^6$ cycles (IRC """ + irc22_yr + r""" Cl.605).
\item Constant stress range is assumed. A thickness correction factor $\mu_r$ is applied for plate thickness $> 25 \ \text{mm}$.
\end{itemize}

\textbf{Stiffener Design}

\begin{itemize}
\item Intermediate transverse stiffener and bearing stiffener design follows IS """ + is800_yr + r""" Cl.8.7.2/8.7.3 and IRC """ + irc24_yr + r""" Cl.509.7.2/509.7.3.
\end{itemize}

\section{Known Limitations of This Version}
\label{sec:limitations}

\begin{itemize}
\item Substructure (piers, pile caps, foundations) and bearing design are not included.
\item Splice connection design is not implemented.
\item Skew angle $>$ 15 degrees requires independent manual analysis (IRC """ + irc24_yr + r""" Cl. 504.8).
\item Construction stage sequence analysis is approximate; detailed staged analysis
  should be performed for long-term deflection checks.
\item The grillage analysis assumes simply supported boundary conditions;
  continuous spans are not currently supported.
\end{itemize}
"""
