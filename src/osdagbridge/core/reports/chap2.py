# Chapter 2: Input Parameters — formatted with themed_longtable and centralized styling

from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_CB_TYPE,
    KEY_CROSS_BRACING,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DESIGN_MODE,
    KEY_DO_GAMMA_C_BASIC,
    KEY_DO_GAMMA_FLT,
    KEY_DO_GAMMA_M0,
    KEY_DO_GAMMA_M1,
    KEY_DO_GAMMA_MF,
    KEY_DO_GAMMA_S,
    KEY_DO_GAMMA_V,
    KEY_END_DIAPHRAGM,
    KEY_FOOTPATH,
    KEY_GIRDER,
    KEY_INCLUDE_MEDIAN,
    KEY_MD_TYPE,
    KEY_MP_CB_BRACING_SECTION_DESIGNATION,
    KEY_MP_CB_MEMBER_ID,
    KEY_MP_CB_SELECT_GIRDERS,
    KEY_MP_CB_SPACING,
    KEY_MP_CB_TYPE,
    KEY_MP_ED_BRACING_SECTION_DESIGNATION,
    KEY_MP_ED_MEMBER_ID,
    KEY_MP_ED_SELECT_GIRDERS,
    KEY_MP_ED_TYPE,
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS,
    KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH,
    KEY_MP_GIRDER_DEPTH,
    KEY_MP_GIRDER_SYMMETRY,
    KEY_MP_GIRDER_TOP_FLANGE_THICKNESS,
    KEY_MP_GIRDER_TOP_FLANGE_WIDTH,
    KEY_MP_GIRDER_TORSIONAL_RESTRAINT,
    KEY_MP_GIRDER_TYPE,
    KEY_MP_GIRDER_WARPING_RESTRAINT,
    KEY_MP_GIRDER_WEB_THICKNESS,
    KEY_MP_GIRDER_WEB_TYPE,
    KEY_MP_STIFFENER_BEARING_THICKNESS,
    KEY_MP_STIFFENER_INTERMEDIATE,
    KEY_MP_STIFFENER_INTERMEDIATE_SPACING,
    KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS,
    KEY_MP_STIFFENER_LONGITUDINAL,
    KEY_MP_STIFFENER_NO_BEARING_STIFFENERS,
    KEY_MP_STIFFENER_SPACING,
    KEY_RL_LOAD_VALUE,
    KEY_RL_TYPE,
    KEY_SD_SHEAR_DIAMETER,
    KEY_SD_SHEAR_HEIGHT,
    KEY_SD_SHEAR_STUDS_PER_SECTION,
    KEY_SD_SHEAR_ULTIMATE_STRENGTH,
    KEY_SD_SHEAR_YIELD_STRENGTH,
    KEY_SKEW_ANGLE,
    KEY_SPAN,
    KEY_STRUCTURE_TYPE,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_OVERALL_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS
)
from osdagbridge.core.reports.report_utils import _render_value, get_girder_entries, _tex
from osdagbridge.core.reports.styles import themed_longtable


def ch2_input_parameters(m, input_dict, output_dict=None):
    girder_entries = get_girder_entries(input_dict)
    n_girders = len(girder_entries)
    
    lat = input_dict.get('latitude')
    lon = input_dict.get('longitude')
    lat_lon_str = f"{lat}° N, {lon}° E" if (lat and lon) else (f"{lat}, {lon}" if (lat or lon) else "N/A")
    skew_val = input_dict.get(KEY_SKEW_ANGLE)
    skew_str = f"{skew_val}°" if skew_val not in ("", None) else "0°"
    lanes_val = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    lanes_str = str(lanes_val) if lanes_val not in ("", None) else "2"

    # Table 2.1: Project Location
    t21_rows = [
        r"\textnormal{Project Location} & " + _tex(m.project_location) + r" \\",
        r"\textnormal{Latitude / Longitude} & " + _tex(lat_lon_str) + r" \\",
        r"\textnormal{Seismic Zone (IRC 6)} & " + (_render_value(input_dict, 'seismic_zone')) + r"\sdstar{} \\",
        r"\textnormal{Basic Wind Speed (IRC 6)} & " + (_render_value(input_dict, 'wind_speed', ' m/s')) + r"\sdstar{} \\",
        r"\textnormal{Shade Temp. Max / Min (IRC 6)} & " + (_render_value(input_dict, 'shade_temp_max', '')) + r" $^\circ$C / " + (_render_value(input_dict, 'shade_temp_min', '')) + r" $^\circ$C\sdstar{} \\",
    ]
    t21 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=t21_rows,
        caption="Project Location",
        label="tab:project-location"
    )

    # Table 2.2: Bridge Geometry (D4: no duplicate units)
    t22_rows = [
        r"\textnormal{Type of Structure} & " + (_render_value(input_dict, KEY_STRUCTURE_TYPE)) + r" \\",
        r"\textnormal{Span} & " + (_render_value(input_dict, KEY_SPAN, ' m')) + r" \\",
        r"\textnormal{Carriageway Width} & " + (_render_value(input_dict, KEY_CARRIAGEWAY_WIDTH, ' m')) + r" \\",
        r"\textnormal{Include Median} & " + (_render_value(input_dict, KEY_INCLUDE_MEDIAN)) + r" \\",
        r"\textnormal{Footpath} & " + (_render_value(input_dict, KEY_FOOTPATH)) + r" \\",
        r"\textnormal{Skew Angle} & " + _tex(skew_str) + r" (IRC 24 Cl. 504.8 limit: $\pm$15°) \\",
    ]
    t22 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=t22_rows,
        caption="Bridge Geometry",
        label="tab:bridge-geometry"
    )

    # Table 2.3: Material Selection
    t23_rows = [
        r"\textnormal{Girder Steel Grade (IS 2062)} & " + (_render_value(input_dict, KEY_GIRDER)) + r" \\",
        r"\textnormal{Cross Bracing Steel Grade} & " + (_render_value(input_dict, KEY_CROSS_BRACING)) + r" \\",
        r"\textnormal{End Diaphragm Steel Grade} & " + (_render_value(input_dict, KEY_END_DIAPHRAGM)) + r" \\",
        r"\textnormal{Concrete Deck Grade (IRC 22)} & " + (_render_value(input_dict, KEY_DECK_CONCRETE_GRADE_BASIC)) + r" \\",
    ]
    t23 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=t23_rows,
        caption="Material Selection",
        label="tab:material-selection"
    )

    # Table 2.4: Typical Section Details (D4: no duplicate units)
    t24_rows = [
        r"\textnormal{Overall Bridge Width} & " + (_render_value(input_dict, KEY_TS_OVERALL_WIDTH, ' m')) + r" \\",
        r"\textnormal{No. of Girders} & " + (_render_value(input_dict, KEY_TS_NO_OF_GIRDERS)) + r" \\",
        r"\textnormal{Girder Spacing} & " + (_render_value(input_dict, KEY_TS_GIRDER_SPACING, ' m')) + r" \\",
        r"\textnormal{Deck Overhang Width} & " + (_render_value(input_dict, KEY_TS_DECK_OVERHANG, ' m')) + r" \\",
        r"\textnormal{Deck Thickness} & " + (_render_value(input_dict, KEY_TS_DECK_THICKNESS, ' mm')) + r" \\",
        r"\textnormal{Footpath Width} & " + (_render_value(input_dict, KEY_TS_FOOTPATH_WIDTH, ' m')) + r" (IRC 5 Cl. 104.3.6 min: 1.5 m) \\",
        r"\textnormal{No. of Traffic Lanes} & " + _tex(lanes_str) + r" (per IRC 5 Cl. 104.3.1) \\",
    ]
    t24 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=t24_rows,
        caption="Typical Section Details",
        label="tab:typical-section"
    )

    # Table 2.5: Components Details (D4: no duplicate units)
    t25_rows = [
        r"\textnormal{Crash Barrier Type} & " + (_render_value(input_dict, KEY_CB_TYPE)) + r" \\",
        r"\textnormal{Crash Barrier Load} & " + (_render_value(input_dict, KEY_CB_LOAD, ' kN/m')) + r" \\",
    ]
    if str(input_dict.get(KEY_INCLUDE_MEDIAN, "")).strip().lower() in ("yes", "true", "1"):
        t25_rows.append(r"\textnormal{Median Type} & " + _render_value(input_dict, KEY_MD_TYPE) + r" \\")
    t25_rows.extend([
        r"\textnormal{Railing Type} & " + (_render_value(input_dict, KEY_RL_TYPE)) + r" \\",
        r"\textnormal{Railing Load} & " + (_render_value(input_dict, KEY_RL_LOAD_VALUE, ' kN/m')) + r" \\",
        r"\textnormal{Wearing Course Material} & " + (_render_value(input_dict, KEY_WC_MATERIAL)) + r" \\",
        r"\textnormal{Wearing Course Thickness} & " + (_render_value(input_dict, KEY_WC_THICKNESS, ' mm')) + r" \\",
    ])
    t25 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=t25_rows,
        caption="Components Details",
        label="tab:components-details"
    )

    return r"""
\chapter{Input Parameters}

This section documents all inputs provided to OsdagBridge. User-provided inputs are clearly distinguished from software-assumed defaults. Where the user did not supply a value, the software has applied the IRC/IS code default or an empirical guideline; these are annotated with an asterisk (\sdstar{}).

\section{Basic Inputs (User-Defined)}
\label{sec:basic-inputs}

\noindent\textit{Note: These inputs are mandatory and were provided by the user.}

\vspace{0.4cm}
""" + t21 + r"""

\vspace{0.4cm}
""" + t22 + r"""

\vspace{0.4cm}
""" + t23 + r"""

\section{Additional Inputs}
\label{sec:additional-inputs}

Where the user has modified additional inputs, those values are reported here. Where no modification was made, the software default is shown.

\vspace{0.4cm}
""" + t24 + r"""

\vspace{0.4cm}
""" + t25 + r"""

""" + _girder_tables(input_dict, n_girders) + r"""

""" + _bracing_tables(input_dict, n_girders) + r"""

""" + _shear_connector_table(input_dict, output_dict) + r"""

""" + _safety_factors_table(input_dict)


def _girder_tables(input_dict, n_girders):
    n = n_girders if n_girders >= 1 else 1
    girder_entries = get_girder_entries(input_dict)
    if not girder_entries:
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
    
    entries_for_table = [
        (lbl, mid, i)
        for i, (lbl, mid) in enumerate(girder_entries, start=1)
    ]

    def _dim_vals(i):
        def _to_mm(val_key):
            val = input_dict.get(val_key)
            if val in ("", None):
                return "---"
            try:
                f = float(val)
                if f < 20.0:  # meters to mm
                    f = f * 1000.0
                return f"{f:.1f} mm"
            except (ValueError, TypeError):
                return _render_value(input_dict, val_key, ' mm')

        return (
            _to_mm(f"{KEY_MP_GIRDER_DEPTH}.G{i}.M1"),
            _to_mm(f"{KEY_MP_GIRDER_WEB_THICKNESS}.G{i}.M1"),
            _to_mm(f"{KEY_MP_GIRDER_TOP_FLANGE_WIDTH}.G{i}.M1") + ", " + _to_mm(f"{KEY_MP_GIRDER_TOP_FLANGE_THICKNESS}.G{i}.M1"),
            _to_mm(f"{KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH}.G{i}.M1") + ", " + _to_mm(f"{KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS}.G{i}.M1"),
        )

    def _gen_vals(i):
        return (
            _render_value(input_dict, KEY_DESIGN_MODE),
            _render_value(input_dict, f"{KEY_MP_GIRDER_TYPE}.G{i}.M1"),
            _render_value(input_dict, f"{KEY_MP_GIRDER_SYMMETRY}.G{i}.M1"),
        )

    def _rst_vals(i):
        return (
            _render_value(input_dict, f"{KEY_MP_GIRDER_TORSIONAL_RESTRAINT}.G{i}.M1") + ", " + _render_value(input_dict, f"{KEY_MP_GIRDER_WARPING_RESTRAINT}.G{i}.M1"),
            _render_value(input_dict, f"{KEY_MP_GIRDER_WEB_TYPE}.G{i}.M1"),
            _render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE}.G{i}.M1") + "; Spc: " + _render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE_SPACING}.G{i}.M1", ' mm') + "; Thk: " + _render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS}.G{i}.M1", ' mm'),
            _render_value(input_dict, f"{KEY_MP_STIFFENER_LONGITUDINAL}.G{i}.M1"),
            "No: " + _render_value(input_dict, f"{KEY_MP_STIFFENER_NO_BEARING_STIFFENERS}.G{i}.M1") + "; Spc: " + _render_value(input_dict, f"{KEY_MP_STIFFENER_SPACING}.G{i}.M1", ' mm') + "; Thk: " + _render_value(input_dict, f"{KEY_MP_STIFFENER_BEARING_THICKNESS}.G{i}.M1", ' mm'),
        )

    # D2: Compare row content WITHOUT the girder label
    all_identical = False
    if len(entries_for_table) > 1:
        first_gen = _gen_vals(1)
        first_dim = _dim_vals(1)
        first_rst = _rst_vals(1)
        all_identical = all(
            _gen_vals(i) == first_gen and _dim_vals(i) == first_dim and _rst_vals(i) == first_rst
            for _, _, i in entries_for_table
        )

    gen_rows, dim_rows, rst_rows = [], [], []

    if all_identical:
        g_lbl = f"G1--G{len(entries_for_table)}"
        m_id = "M1"
        gv = _gen_vals(1)
        dv = _dim_vals(1)
        rv = _rst_vals(1)
        gen_rows.append(f"{g_lbl} & {m_id} & {gv[0]} & {gv[1]} & {gv[2]} \\\\")
        dim_rows.append(f"{g_lbl} & {dv[0]} & {dv[1]} & {dv[2]} & {dv[3]} \\\\")
        rst_rows.append(f"{g_lbl} & {rv[0]} & {rv[1]} & {rv[2]} & {rv[3]} & {rv[4]} \\\\")
        identical_note = f"\\noindent\\textit{{Note: Girders G1 to G{len(entries_for_table)} are structurally identical; single representative row displayed.}}\n\\vspace{{0.4em}}\n"
    else:
        for g_lbl, m_id, i in entries_for_table:
            gv = _gen_vals(i)
            dv = _dim_vals(i)
            rv = _rst_vals(i)
            gen_rows.append(f"{g_lbl} & {m_id} & {gv[0]} & {gv[1]} & {gv[2]} \\\\")
            dim_rows.append(f"{g_lbl} & {dv[0]} & {dv[1]} & {dv[2]} & {dv[3]} \\\\")
            rst_rows.append(f"{g_lbl} & {rv[0]} & {rv[1]} & {rv[2]} & {rv[3]} & {rv[4]} \\\\")
        identical_note = ""

    t26 = themed_longtable(
        col_spec="|L{2.2cm}|L{1.8cm}|p{3.8cm}|p{3.8cm}|p{3.8cm}|",
        headers=["Girder", "Member ID", "Design Mode", "Girder Type", "Girder Symmetry"],
        body_rows=gen_rows,
        caption="Girder General Information",
        label="tab:girder-gen-info"
    )

    t27 = themed_longtable(
        col_spec="|L{1.8cm}|L{2.5cm}|L{2.2cm}|p{4.5cm}|p{4.5cm}|",
        headers=["Girder", "Total Depth, D (mm)", "Web, $t_w$ (mm)", "Top Flange ($b_{tf}, t_{tf}$)", "Bottom Flange ($b_{bf}, t_{bf}$)"],
        body_rows=dim_rows,
        caption="Girder Section Dimensions",
        label="tab:girder-dimensions"
    )

    # D3: Table 2.8 widened columns and no header collision
    t28 = themed_longtable(
        col_spec="|L{1.8cm}|p{2.6cm}|p{2.4cm}|p{2.8cm}|p{2.4cm}|p{2.5cm}|",
        headers=["Girder", "Torsional / Warping Restraint", "Web Philosophy", "Intermediate Stiffeners", "Longitudinal Stiffeners", "Bearing Stiffener"],
        body_rows=rst_rows,
        caption="Girder Restraint and Stiffener Details",
        label="tab:girder-restraints"
    )

    return f"""
{identical_note}
{t26}

\\vspace{{0.4cm}}
{t27}

\\vspace{{0.4cm}}
{t28}
"""


def _bracing_tables(input_dict, n_girders):
    n = n_girders if n_girders >= 2 else 2
    panels = [
        (
            _render_value(input_dict, f"{KEY_MP_CB_SELECT_GIRDERS}.G{i}G{i+1}.B{i}M1"),
            _render_value(input_dict, f"{KEY_MP_CB_MEMBER_ID}.G{i}G{i+1}.B{i}M1"),
            _render_value(input_dict, f"{KEY_MP_ED_SELECT_GIRDERS}.G{i}G{i+1}.E{i}M1"),
            _render_value(input_dict, f"{KEY_MP_ED_MEMBER_ID}.G{i}G{i+1}.E{i}M1"),
            i
        )
        for i in range(1, n)
    ]

    # Check if all cross bracing panels are identical
    cb_first = (
        _render_value(input_dict, f'{KEY_MP_CB_TYPE}.G1G2.B1M1'),
        _render_value(input_dict, f'{KEY_MP_CB_BRACING_SECTION_DESIGNATION}.G1G2.B1M1'),
        _render_value(input_dict, f'{KEY_MP_CB_SPACING}.G1G2.B1M1', ' m')
    )
    cb_identical = len(panels) > 1 and all(
        (
            _render_value(input_dict, f'{KEY_MP_CB_TYPE}.G{i}G{i+1}.B{i}M1'),
            _render_value(input_dict, f'{KEY_MP_CB_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.B{i}M1'),
            _render_value(input_dict, f'{KEY_MP_CB_SPACING}.G{i}G{i+1}.B{i}M1', ' m')
        ) == cb_first
        for _, _, _, _, i in panels
    )

    if cb_identical:
        cb_rows = [
            f"All Panels (G1--G{n}) & B1M1--B{n-1}M1 & {cb_first[0]} & {cb_first[1]} & {cb_first[2]} \\\\"
        ]
    else:
        cb_rows = [
            f"{cb_loc} & {cb_ids} & {_render_value(input_dict, f'{KEY_MP_CB_TYPE}.G{i}G{i+1}.B{i}M1')} & {_render_value(input_dict, f'{KEY_MP_CB_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.B{i}M1')} & {_render_value(input_dict, f'{KEY_MP_CB_SPACING}.G{i}G{i+1}.B{i}M1', ' m')} \\\\"
            for cb_loc, cb_ids, _, _, i in panels
        ]

    # Check if all end diaphragm panels are identical
    ed_first = (
        _render_value(input_dict, f'{KEY_MP_ED_TYPE}.G1G2.E1M1'),
        _render_value(input_dict, f'{KEY_MP_ED_BRACING_SECTION_DESIGNATION}.G1G2.E1M1')
    )
    ed_identical = len(panels) > 1 and all(
        (
            _render_value(input_dict, f'{KEY_MP_ED_TYPE}.G{i}G{i+1}.E{i}M1'),
            _render_value(input_dict, f'{KEY_MP_ED_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.E{i}M1')
        ) == ed_first
        for _, _, _, _, i in panels
    )

    if ed_identical:
        ed_rows = [
            f"All Panels (G1--G{n}) & E1M1--E{n-1}M1 & {ed_first[0]} & {ed_first[1]} \\\\"
        ]
    else:
        ed_rows = [
            f"{ed_loc} & {ed_ids} & {_render_value(input_dict, f'{KEY_MP_ED_TYPE}.G{i}G{i+1}.E{i}M1')} & {_render_value(input_dict, f'{KEY_MP_ED_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.E{i}M1')} \\\\"
            for _, _, ed_loc, ed_ids, i in panels
        ]

    t29 = themed_longtable(
        col_spec="|L{3.2cm}|L{3.0cm}|L{3.2cm}|L{3.5cm}|C{2.1cm}|",
        headers=["Location", "Member IDs", "Type of Bracing", "Bracing Section", "Spacing"],
        body_rows=cb_rows,
        caption="Member Properties: Cross Bracing Details",
        label="tab:cross-bracing-details"
    )

    t210 = themed_longtable(
        col_spec="|L{3.2cm}|L{3.0cm}|L{4.2cm}|L{4.6cm}|",
        headers=["Location", "Member IDs", "Type of Bracing", "Bracing Section"],
        body_rows=ed_rows,
        caption="Member Properties: End Diaphragm Details",
        label="tab:end-diaphragm-details"
    )

    return f"""
\\vspace{{0.4cm}}
{t29}

\\vspace{{0.4cm}}
{t210}
"""


def _shear_connector_table(input_dict, output_dict=None):
    od = output_dict or {}
    sc_rows = [
        r"\textnormal{Stud Diameter} & " + (_render_value(od, KEY_SD_SHEAR_DIAMETER, ' mm')) + r" \\",
        r"\textnormal{Stud Height} & " + (_render_value(od, KEY_SD_SHEAR_HEIGHT, ' mm')) + r" \\",
        r"\textnormal{Stud $f_y$} & " + (_render_value(od, KEY_SD_SHEAR_YIELD_STRENGTH, ' MPa')) + r" \\",
        r"\textnormal{Stud $f_u$} & " + (_render_value(od, KEY_SD_SHEAR_ULTIMATE_STRENGTH, ' MPa')) + r" \\",
        r"\textnormal{No. of Studs per Section} & " + (_render_value(od, KEY_SD_SHEAR_STUDS_PER_SECTION)) + r" \\",
    ]
    t211 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=sc_rows,
        caption="Shear Connector Details",
        label="tab:shear-connector-details"
    )
    return f"""
\\vspace{{0.4cm}}
{t211}
"""


def _safety_factors_table(input_dict):
    sf_rows = [
        r"\textnormal{$\gamma_{M0}$ (Yielding / Buckling)} & " + (_render_value(input_dict, KEY_DO_GAMMA_M0)) + r" \\",
        r"\textnormal{$\gamma_{M1}$ (Ultimate Stress)} & " + (_render_value(input_dict, KEY_DO_GAMMA_M1)) + r" \\",
        r"\textnormal{$\gamma_C$ (Concrete, Basic)} & " + (_render_value(input_dict, KEY_DO_GAMMA_C_BASIC)) + r" \\",
        r"\textnormal{$\gamma_s$ (Reinforcement)} & " + (_render_value(input_dict, KEY_DO_GAMMA_S)) + r" \\",
        r"\textnormal{$\gamma_v$ (Shear Connectors)} & " + (_render_value(input_dict, KEY_DO_GAMMA_V)) + r" \\",
        r"\textnormal{$\gamma_{fft}$ (Fatigue Load)} & " + (_render_value(input_dict, KEY_DO_GAMMA_FLT)) + r" \\",
        r"\textnormal{$\gamma_{Mft}$ (Fatigue Strength)} & " + (_render_value(input_dict, KEY_DO_GAMMA_MF)) + r" \\",
    ]
    t212 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Value"],
        body_rows=sf_rows,
        caption="Partial Safety Factors",
        label="tab:partial-safety-factors"
    )
    return f"""
\\vspace{{0.4cm}}
\\noindent\\textit{{Note: All values are per IRC 22 Table 1 unless user-modified.}}

{t212}
"""
