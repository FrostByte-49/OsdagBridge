from osdagbridge.core.reports.styles import CODE_VERSIONS
from osdagbridge.core.reports.report_utils import _tex


def references():
    items = []
    for code, info in CODE_VERSIONS.items():
        items.append(
            r"\item " + _tex(code) + " (" + info['year'] + r") --- \textit{" + _tex(info['title']) + r".}"
        )
    
    # Textbooks and guidelines
    items.append(
        r"\item Subramanian, N. (2008). \textit{Design of Steel Structures.} Oxford University Press."
    )
    items.append(
        r"\item Steel-INSDAG Teaching Resource Materials. \url{https://www.steel-insdag.org}"
    )

    items_tex = "\n\n".join(items)

    return r"""
\chapter*{References}
\addcontentsline{toc}{chapter}{References}

\begin{enumerate}

""" + items_tex + r"""

\end{enumerate}
"""
