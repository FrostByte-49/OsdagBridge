# Chapter 7: Material Take-off & Quantity Summary

from osdagbridge.core.reports.report_utils import _fig_subfigure, _fig_embed
from osdagbridge.core.reports.styles import themed_longtable


def ch7_quantities(input_dict, fig_paths=None):
    if fig_paths is None:
        fig_paths = {}

    def _val(k):
        v = input_dict.get(k)
        if v in (None, "", "None"):
            return "N.A."
        try:
            f = float(v)
            return f"{f:.2f}"
        except (TypeError, ValueError):
            return str(v)

    # K1: No default weights (0.22, 0.48, 0.45 deleted)
    g_wt  = _val("steel_girders_wt_total")
    cb_t  = _val("bracing_top_wt_total")
    cb_b  = _val("bracing_bot_wt_total")
    cb_d  = _val("bracing_diag_wt_total")
    ed_wt = _val("diaphragm_wt_total")
    c_wt  = _val("concrete_deck_wt_total")
    rb_wt = _val("rebar_deck_wt_total")
    ss_wt = _val("shear_studs_wt_total")
    cr_wt = _val("crash_barrier_wt_total")

    # Compute Total Steel and Total Materials if numeric
    total_steel_mt = 0.0
    has_steel = False
    for wt_str in (g_wt, cb_t, cb_b, cb_d, ed_wt, rb_wt, ss_wt):
        try:
            total_steel_mt += float(wt_str)
            has_steel = True
        except (TypeError, ValueError):
            pass
    tot_steel_str = f"{total_steel_mt:.2f}" if has_steel else "N.A."

    t71_rows = [
        f"1 & Structural Steel (IS 2062) for Girders & {_val('steel_girders_vol_formula')} & {_val('steel_girders_qty')} & {_val('steel_girders_vol_total')} m$^3$ & {_val('steel_girders_wt_single')} & {g_wt} \\\\",
        f"2(a) & Cross Bracing --- Top Chord & {_val('bracing_top_vol_formula')} & {_val('bracing_top_qty')} & {_val('bracing_top_vol_total')} m$^3$ & {_val('bracing_top_wt_single')} & {cb_t} \\\\",
        f"2(b) & Cross Bracing --- Bottom Chord & {_val('bracing_bot_vol_formula')} & {_val('bracing_bot_qty')} & {_val('bracing_bot_vol_total')} m$^3$ & {_val('bracing_bot_wt_single')} & {cb_b} \\\\",
        f"2(c) & Cross Bracing --- Diagonal Chord & {_val('bracing_diag_vol_formula')} & {_val('bracing_diag_qty')} & {_val('bracing_diag_vol_total')} m$^3$ & {_val('bracing_diag_wt_single')} & {cb_d} \\\\",
        f"2(d) & End Diaphragms & {_val('diaphragm_vol_formula')} & {_val('diaphragm_qty')} & {_val('diaphragm_vol_total')} m$^3$ & {_val('diaphragm_wt_single')} & {ed_wt} \\\\",
        f"3 & Concrete (M40) for Deck Slab & {_val('concrete_deck_vol_formula')} & {_val('concrete_deck_qty')} & {_val('concrete_deck_vol_total')} m$^3$ & {_val('concrete_deck_wt_single')} & {c_wt} \\\\",
        f"4 & Reinforcement Steel (Fe 500) & {_val('rebar_deck_vol_formula')} & {_val('rebar_deck_qty')} & {_val('rebar_deck_vol_total')} m$^3$ & {_val('rebar_deck_wt_single')} & {rb_wt} \\\\",
        f"5 & Shear Stud Connectors & {_val('shear_studs_vol_formula')} & {_val('shear_studs_qty')} & {_val('shear_studs_vol_total')} m$^3$ & {_val('shear_studs_wt_single')} & {ss_wt} \\\\",
        f"6 & Crash Barrier & {_val('crash_barrier_vol_formula')} & {_val('crash_barrier_qty')} & {_val('crash_barrier_vol_total')} m$^3$ & {_val('crash_barrier_wt_single')} & {cr_wt} \\\\",
        f"\\multicolumn{{6}}{{|r|}}{{\\textbf{{Total Structural and Reinforcement Steel (MT)}}}} & \\textbf{{{tot_steel_str}}} \\\\",
    ]

    t71 = themed_longtable(
        col_spec="|C{1.0cm}|L{4.2cm}|C{2.6cm}|C{1.6cm}|C{2.0cm}|C{1.8cm}|C{1.8cm}|",
        headers=["S.N.", "Item Description", "Volume Expression", "Qty", "Total Vol", "Unit Wt (MT)", "Total Wt (MT)"],
        body_rows=t71_rows,
        caption="Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        label="tab:bill-of-materials",
    )

    # K2: Table first, charts after
    charts_subfigs = []
    st_path = fig_paths.get('steel_tonnage')
    cr_path = fig_paths.get('concrete_rebar')
    if st_path:
        charts_subfigs.append((st_path, 'Structural Steel Breakdown (MT)', 0.48))
    if cr_path:
        charts_subfigs.append((cr_path, 'Concrete Volume and Reinforcement Weight', 0.48))

    if charts_subfigs:
        material_charts_block = _fig_subfigure(
            charts_subfigs,
            caption="Material Quantity Take-Off Summaries",
            label="fig:material-takeoff-charts"
        )
    else:
        material_charts_block = ""

    return f"""
\\chapter{{Material Take-off \\& Quantity Summary}}
\\label{{ch:material-takeoff}}

This section provides the preliminary Bill of Materials (BOM) including quantities of structural steel, concrete, reinforcement, and fixtures estimated for the superstructure.

\\vspace{{0.4cm}}
{t71}

\\vspace{{0.8cm}}
{material_charts_block}
"""
