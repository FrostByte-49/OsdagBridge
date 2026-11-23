from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports.styles import themed_longtable, CODE_VERSIONS


def ch1_project_info(m):
    proj_rows = [
        r"\textnormal{Project Name} & " + _tex(m.project_name) + r" \\",
        r"\textnormal{Project Location} & " + _tex(m.project_location) + r" \\",
        r"\textnormal{Designer} & " + _tex(m.designer) + r" \\",
        r"\textnormal{Reviewer} & " + _tex(m.reviewer) + r" \\",
        r"\textnormal{Organization} & " + _tex(m.company) + r" \\",
        r"\textnormal{Client} & " + _tex(m.client) + r" \\",
        r"\textnormal{Software Version} & OsdagBridge v1.0.0 \\",
    ]
    t11 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=proj_rows,
        caption="Project and Design Team Details",
        label="tab:project-details",
    )

    # Render standards list directly from CODE_VERSIONS (A6 / L3)
    code_items = []
    for code, info in CODE_VERSIONS.items():
        code_items.append(
            r"\item " + _tex(code) + " (" + info['year'] + r"): \textit{" + _tex(info['title']) + r"}"
        )
    codes_tex = "\n".join(code_items)

    return r"""
\chapter{Project Information}

This section records all project metadata as entered by the designer.

\section{Project and Design Team Details}
\label{sec:project-details}

""" + t11 + r"""

\section{Applicable Codes and Standards}
\label{sec:codes}

\begin{itemize}
""" + codes_tex + r"""
\end{itemize}
"""
