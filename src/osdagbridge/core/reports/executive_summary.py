# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

from osdagbridge.core.reports.report_utils import (
    _fig_or_placeholder,
    _render_value,
    _tex,
    get_girder_entries,
)
from osdagbridge.core.reports.styles import (
    themed_longtable,
    format_status,
    format_ur,
)
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_SD_SECTION_DESIGNATION,
    KEY_SPAN,
    KEY_STRUCTURE_TYPE,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_GIRDERS,
)


def _max_float(values):
    """Return the largest value coercible to float, or None if there are none."""
    out = None
    for v in values:
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if out is None or f > out:
            out = f
    return out


def _max_member_efficiency(pair_designs):
    """Maximum Osdag 'efficiency' (utilization ratio) over a cross-bracing or
    end-diaphragm result dump (nested pair -> member -> force_type -> raw).
    Reads already-computed results only; nothing is recalculated here."""
    from osdagbridge.core.bridge_types.plate_girder.results_data import _extract_osdag_summary
    if not isinstance(pair_designs, dict):
        return None
    best = None
    for members in pair_designs.values():
        if not isinstance(members, dict):
            continue
        for force_types in members.values():
            if not isinstance(force_types, dict):
                continue
            for raw in force_types.values():
                try:
                    val = _extract_osdag_summary(raw or {}).get("efficiency")
                    if val is None:
                        continue
                    f = float(val)
                except (TypeError, ValueError, AttributeError):
                    continue
                if best is None or f > best:
                    best = f
    return best


def executive_summary(input_dict, output_dict, fig_paths) -> str:
    # Real captions without hand-typed "Figure X --" prefixes (F5)
    plan_fig = _fig_or_placeholder(fig_paths.get('girder_top'), 'Overall Bridge Plan', label='fig:es-plan')
    cs_fig = _fig_or_placeholder(fig_paths.get('cross_section'), 'Typical Cross-Section', label='fig:es-cs')
    geom_fig = _fig_or_placeholder(fig_paths.get('final_geometry'), '3D View of Bridge Superstructure', label='fig:es-3d')

    default_sec = _render_value(output_dict, KEY_SD_SECTION_DESIGNATION)

    # ── Pull stored results ──────────────────────────────────────────────────
    design_results = output_dict.get("design_results", {}) or {}
    per_girder     = design_results.get("per_girder", {}) or {}
    deck_results   = output_dict.get("deck_design_results", {}) or {}
    cb_results     = output_dict.get("crossbracing_design_results", {}) or {}
    ed_results     = output_dict.get("end_diaphragm_design_results", {}) or {}

    # Overall Design Status & per-girder governing checks
    failing = []
    gov_name, gov_dcr = "", None
    girder_max_ur = None

    for g, gd in per_girder.items():
        if str(g).startswith("EB"):
            continue
        for chk in (gd.get("checks") or []):
            try:
                _val = chk.get("dcr")
                dcr = float(_val) if _val is not None else None
            except (TypeError, ValueError):
                dcr = None
            name = str(chk.get("name", "")).strip()
            is_fail = ("FAIL" in str(chk.get("status", "")).upper()) or (dcr is not None and dcr > 1.0)
            if is_fail and name and name not in failing:
                failing.append(name)
            if dcr is not None:
                if gov_dcr is None or dcr > gov_dcr:
                    gov_dcr, gov_name = dcr, name
                if girder_max_ur is None or dcr > girder_max_ur:
                    girder_max_ur = dcr

    if not per_girder:
        overall_design_status = "---"
    elif failing:
        overall_design_status = format_status("Fail") + f" ({', '.join(failing)})"
    else:
        overall_design_status = format_status("Pass")

    # Overall Utilization Ratio
    component_urs = []
    if girder_max_ur is not None:
        component_urs.append((girder_max_ur, "Girder"))
    deck_max = _max_float([v for k, v in deck_results.items() if str(k).startswith("ur_") or k in ("utilization_flexure", "utilization_shear")])
    if deck_max is not None:
        component_urs.append((deck_max, "Deck slab"))
    for results, label in ((cb_results, "Cross bracing"), (ed_results, "End diaphragm")):
        m = _max_member_efficiency(results)
        if m is not None:
            component_urs.append((m, label))

    if component_urs:
        max_ur, max_label = max(component_urs, key=lambda t: t[0])
        overall_utilization_ratio = f"{format_ur(max_ur)} ({max_label})"
    else:
        overall_utilization_ratio = "---"

    gov = _tex(gov_name) if gov_name not in (None, '', 'None') else '---'

    # ── Table ES.1: Project Overview (G3) ────────────────────────────────────
    ovw_rows = [
        r"\textnormal{Bridge Type} & " + (_render_value(input_dict, KEY_STRUCTURE_TYPE)) + r" \\",
        r"\textnormal{Design Standard} & IRC 5, IRC 6, IRC 22, IRC 24, IS 800 \\",
        r"\textnormal{Span} & " + (_render_value(input_dict, KEY_SPAN, ' m')) + r" \\",
        r"\textnormal{Carriageway Width} & " + (_render_value(input_dict, KEY_CARRIAGEWAY_WIDTH, ' m')) + r" \\",
        r"\textnormal{No. of Girders} & " + (_render_value(input_dict, KEY_TS_NO_OF_GIRDERS)) + r" \\",
        r"\textnormal{Girder Spacing} & " + (_render_value(input_dict, KEY_TS_GIRDER_SPACING, ' m')) + r" \\",
        r"\textnormal{Deck Thickness} & " + (_render_value(input_dict, KEY_TS_DECK_THICKNESS, ' mm')) + r" \\",
        r"\textnormal{Overall Design Status} & " + overall_design_status + r" \\",
        r"\textnormal{Governing Check} & " + gov + r" \\",
        r"\textnormal{Overall Utilization Ratio (max)} & " + overall_utilization_ratio + r" \\",
    ]
    overview_table = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Design Value"],
        body_rows=ovw_rows,
        caption="Project Overview",
        label="tab:es-project-overview"
    )

    # ── Table ES.2: Final Girder Geometry & Utilization (G1 - rows layout) ──
    girder_entries = get_girder_entries(input_dict)
    if not girder_entries:
        girder_entries = [("G1", "G1M1")]

    g_table_rows = []
    for gi, (lbl, mid) in enumerate(girder_entries, start=1):
        g_key = f"G{gi}"
        gd = per_girder.get(g_key, {}) or {}
        g_sec = gd.get("section") or default_sec or "---"
        
        # Determine each girder's governing check and max DCR
        g_gov_name = "---"
        g_max_dcr = None
        for chk in (gd.get("checks") or []):
            try:
                d = float(chk.get("dcr")) if chk.get("dcr") is not None else None
            except (TypeError, ValueError):
                d = None
            if d is not None:
                if g_max_dcr is None or d > g_max_dcr:
                    g_max_dcr = d
                    g_gov_name = str(chk.get("name", "---"))

        ur_str = format_ur(g_max_dcr) if g_max_dcr is not None else "---"
        g_table_rows.append(
            f"{_tex(lbl)} & {_tex(mid)} & {_tex(g_sec)} & {_tex(g_gov_name)} & {ur_str} \\\\"
        )

    girder_summary_table = themed_longtable(
        col_spec="|C{1.8cm}|C{2.0cm}|L{4.2cm}|L{4.5cm}|C{2.0cm}|",
        headers=["Girder", "Member ID", "Section", "Governing Check", "UR"],
        body_rows=g_table_rows,
        caption="Final Girder Geometry and Utilization (after optimization)",
        label="tab:es-girder-geometry"
    )

    # ── Key Design Outcomes Summary (G4: N/A when missing) ───────────────────
    girder_outcome = format_status("Fail" if failing else "Pass") if per_girder else "N/A"
    deck_outcome = format_status("Fail" if deck_max > 1.0 else "Pass") if deck_max is not None else "N/A"
    
    cb_max = _max_member_efficiency(cb_results)
    cb_outcome = format_status("Fail" if cb_max > 1.0 else "Pass") if cb_max is not None else "N/A"
    
    ed_max = _max_member_efficiency(ed_results)
    ed_outcome = format_status("Fail" if ed_max > 1.0 else "Pass") if ed_max is not None else "N/A"

    return r"""
\chapter*{Executive Summary}
\addcontentsline{toc}{chapter}{Executive Summary}

This section provides a concise summary of the bridge design, key inputs, governing loads, and final design outcomes.

\section*{Project Overview}
\addcontentsline{toc}{section}{Project Overview}
\label{sec:project-overview}

""" + overview_table + r"""

""" + plan_fig + r"""

""" + cs_fig + r"""

""" + geom_fig + r"""

\vspace{0.8em}
""" + girder_summary_table + r"""

\vspace{0.4em}
\noindent\textit{Note: Utilization ratio (UR) = demand / capacity. A value $\leq 1.0$ indicates a passing check.}

\vspace{1em}

\section*{Key Design Outcomes Summary}
\addcontentsline{toc}{section}{Key Design Outcomes Summary}
\label{sec:key-outcomes}

\noindent\begin{itemize}[leftmargin=1.5em]
\item Girder Design: """ + girder_outcome + r"""
\item Cross Bracing Design: """ + cb_outcome + r"""
\item End Diaphragm Design: """ + ed_outcome + r"""
\item Deck Design: """ + deck_outcome + r"""
\end{itemize}

\section*{Design Assumptions and Limitations}
\addcontentsline{toc}{section}{Design Assumptions and Limitations}
\label{sec:exec-assumptions}

\begin{itemize}
\item Additional inputs not provided by the user were assumed by software per IRC/IS code defaults or practical consideration.
\item Grillage analysis was performed using OSPGrillage assuming simply supported I-girders.
\item Substructure and foundation design are not included in this report.
\item Splice connections and bearings are not designed in this version.
\end{itemize}
"""
