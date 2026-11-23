import re
from typing import TYPE_CHECKING
from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_TS_NO_OF_GIRDERS,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
)
from osdagbridge.core.reports.report_utils import _tex, _fig_embed
from osdagbridge.core.reports.styles import themed_longtable, format_status

if TYPE_CHECKING:
    from .report_generator import ReportDataBridge


def _natural_keys(text):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(text))]


def ch4_analysis(asum, fig_paths, bridge: "ReportDataBridge", span_m: float):
    lc_summary  = (asum or {}).get('load_cases', {})
    rxn_summary = (asum or {}).get('reactions',  {})

    def _is_moving(lc_name: str) -> bool:
        n = lc_name.lower()
        return "moving" in n or " pos_" in n

    lc_summary  = {k: v for k, v in lc_summary.items()  if not _is_moving(k)}
    rxn_summary = {k: v for k, v in rxn_summary.items() if not _is_moving(k)}

    def _fmt(val, nd=3):
        try:
            f = float(val)
            if abs(f) < 1e-6:
                f = 0.0
            return f"{f:.{nd}f}"
        except (TypeError, ValueError):
            return r"---"

    def _fmt_rxn(val, nd=3):
        """Normalise gravity reaction to upward positive (H4)."""
        try:
            f = float(val)
            # Normalise negative gravity reactions to upward positive
            f_norm = abs(f) if abs(f) >= 1e-6 else 0.0
            return f"{f_norm:.{nd}f}"
        except (TypeError, ValueError):
            return r"---"

    # H2: Logical ordering (DL, SIDL, LL, Wind, EQ, Combos, Envelopes) with natural sort
    def _lc_sort_key(name):
        n = str(name).lower()
        if n.startswith('envelope') or 'envelope' in n:
            cat = 6
        elif 'comb' in n or '+' in n or 'uls' in n or 'sls' in n:
            cat = 5
        elif 'eq' in n or 'seismic' in n or 'earthquake' in n:
            cat = 4
        elif 'wind' in n or 'wl' in n:
            cat = 3
        elif 'live' in n or 'll' in n or 'class' in n or '70r' in n:
            cat = 2
        elif 'sidl' in n or 'surfacing' in n or 'dw' in n:
            cat = 1
        elif 'dead' in n or 'dl' in n or 'self' in n:
            cat = 0
        else:
            cat = 5
        return (cat, _natural_keys(name))

    all_lcs = list(set(list(lc_summary.keys()) + list(rxn_summary.keys())))
    all_lcs.sort(key=_lc_sort_key)

    # H3: Table 4.1 — remove reaction columns (duplicate Table 4.2), standard columns
    t41_rows = []
    for lc in all_lcs:
        bm_d = lc_summary.get(lc) or {}
        max_bm = _fmt(bm_d.get('max_bm'))
        bm_g = _tex(bm_d.get('bm_girder', '---'))
        bm_loc = _fmt(bm_d.get('bm_location'), nd=2)
        max_sf = _fmt(bm_d.get('max_sf'))
        sf_g = _tex(bm_d.get('sf_girder', '---'))
        sf_loc = _fmt(bm_d.get('sf_location'), nd=2)

        t41_rows.append(
            f"{_tex(lc)} & {max_bm} & {bm_g} & {bm_loc} & {max_sf} & {sf_g} & {sf_loc} \\\\"
        )

    if not t41_rows:
        t41_rows.append(r"--- & --- & --- & --- & --- & --- & --- \\")

    t41 = themed_longtable(
        col_spec="|L{4.2cm}|C{2.0cm}|C{1.5cm}|C{1.6cm}|C{2.0cm}|C{1.5cm}|C{1.6cm}|",
        headers=["Load Case / Comb.", "Max BM (kNm)", "Girder", "Loc. (m)", "Max SF (kN)", "Girder", "Loc. (m)"],
        body_rows=t41_rows,
        caption="Summary of Maximum Demands (Bending Moment and Shear Force)",
        label="tab:analysis-demands",
    )

    # Table 4.2: Reactions at Supports (H4: upward positive)
    rxn_rows = []
    for lc in all_lcs:
        rx = rxn_summary.get(lc)
        if rx:
            l_val = _fmt_rxn(rx.get('left_kN'))
            r_val = _fmt_rxn(rx.get('right_kN'))
            if l_val != "---" or r_val != "---":
                rxn_rows.append(f"{_tex(lc)} & {l_val} & {r_val} \\\\")
    if not rxn_rows:
        rxn_rows.append(r"Envelope ULS & --- & --- \\")

    t42 = themed_longtable(
        col_spec="|L{6.0cm}|C{4.5cm}|C{4.5cm}|",
        headers=["Load Case / Combination", "Left Support Reaction (kN)", "Right Support Reaction (kN)"],
        body_rows=rxn_rows,
        caption="Reactions at Supports (Upward Positive)",
        label="tab:reactions-summary",
    )

    # Table 4.3: Serviceability Deflection Checks
    _span_m         = float(bridge.input_dict.get(KEY_SPAN, 0) or 0)
    _allow_live_mm  = _span_m * 1000.0 / 800.0
    _allow_total_mm = _span_m * 1000.0 / 600.0

    try:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1) or 1)
    except (TypeError, ValueError):
        n = 1

    _live_mm  = None
    _total_mm = None
    for _gi in range(1, n + 1):
        _l = bridge.output_dict.get(f"{KEY_SD_DEFL_LIVE}.G{_gi}")
        _t = bridge.output_dict.get(f"{KEY_SD_DEFL_TOTAL}.G{_gi}")
        if _l is not None:
            _live_mm  = max(_live_mm, float(_l))  if _live_mm  is not None else float(_l)
        if _t is not None:
            _total_mm = max(_total_mm, float(_t)) if _total_mm is not None else float(_t)

    _live_str        = f"{_live_mm:.3f} mm"  if _live_mm  is not None else "---"
    _total_str       = f"{_total_mm:.3f} mm" if _total_mm is not None else "---"
    _allow_live_str  = f"L/800 = {_allow_live_mm:.1f} mm"
    _allow_total_str = f"L/600 = {_allow_total_mm:.1f} mm"
    _live_status     = format_status("Pass" if (_live_mm is not None and _live_mm <= _allow_live_mm) else ("Fail" if _live_mm is not None else "---"))
    _total_status    = format_status("Pass" if (_total_mm is not None and _total_mm <= _allow_total_mm) else ("Fail" if _total_mm is not None else "---"))

    t43_rows = [
        f"\\textnormal{{Deflection due to Live Load, $\\delta_{{LL}}$}} & {_live_str} & {_allow_live_str} & {_live_status} \\\\",
        f"\\textnormal{{Deflection due to Total Load, $\\delta_{{total}}$}} & {_total_str} & {_allow_total_str} & {_total_status} \\\\",
    ]
    t43 = themed_longtable(
        col_spec="|L{6.0cm}|C{3.0cm}|C{3.5cm}|C{2.5cm}|",
        headers=["Parameter", "Calculated Deflection", "Allowable Limit", "Status"],
        body_rows=t43_rows,
        caption="Deflection Summary (IRC 22 Cl. 604.3.2)",
        label="tab:deflection-summary",
    )

    bm_fig = _fig_embed(fig_paths.get('bm_envelope'), 'Bending Moment Envelope (Envelope ULS) along span (kN-m)', width=r'0.78\textwidth')
    sf_fig = _fig_embed(fig_paths.get('sf_envelope'), 'Shear Force Envelope (Envelope ULS) along span (kN)', width=r'0.78\textwidth')
    defl_fig = _fig_embed(fig_paths.get('defl_ll'), 'Vertical Deflection $D_y$ (1.0 LL) along span', width=r'0.78\textwidth')

    return f"""
\\chapter{{Analysis Results}}

A grillage model was used for structural analysis. The deck is idealized as a grid of elastic beam elements --- longitudinal members represent the composite steel girders with effective slab, and transverse members represent the slab or cross frames. This section summarizes the critical output from that analysis.

\\vspace{{0.4cm}}
{t41}

\\vspace{{0.4cm}}
{t42}

\\vspace{{0.4cm}}
{t43}

\\vspace{{0.6cm}}
\\noindent
{bm_fig}
{sf_fig}
{defl_fig}
"""
