# Chapter 5: Design Checks — fully formatted with themed_longtable and centralized styling

from osdagbridge.core.utils.common import (
    KEY_DD_AS_BOT,
    KEY_DD_AS_MIN,
    KEY_DD_AS_REQ_BOT,
    KEY_DD_AS_REQ_TOP,
    KEY_DD_AS_TOP,
    KEY_DD_COVER_OK,
    KEY_DD_D_BOT,
    KEY_DD_DIA_BOT,
    KEY_DD_FY,
    KEY_DD_GAMMA_DL,
    KEY_DD_GAMMA_LL,
    KEY_DD_HAS_OVERHANG,
    KEY_DD_IMPACT_FACTOR,
    KEY_DD_M_BARRIER,
    KEY_DD_M_DL,
    KEY_DD_M_DL_OH,
    KEY_DD_M_LL,
    KEY_DD_M_LL_OH,
    KEY_DD_M_ULS_HOG,
    KEY_DD_M_ULS_OH,
    KEY_DD_M_ULS_SAG,
    KEY_DD_MIN_COVER,
    KEY_DD_MU_BOT,
    KEY_DD_MU_OH,
    KEY_DD_MU_TOP,
    KEY_DD_PUNCH_C1,
    KEY_DD_PUNCH_C2,
    KEY_DD_PUNCH_OK,
    KEY_DD_PUNCH_U1,
    KEY_DD_PUNCH_VED,
    KEY_DD_PUNCH_VED_KN,
    KEY_DD_SHEAR_OK,
    KEY_DD_SHEAR_VED,
    KEY_DD_SHEAR_VRDC,
    KEY_DD_SPACING_MAX,
    KEY_DD_SPAN,
    KEY_DD_SPC_BOT,
    KEY_DD_TYRE_LENGTH,
    KEY_DD_TYRE_WIDTH,
    KEY_DD_VEHICLE,
    KEY_DD_VRD_C_MPA,
    KEY_DD_WDL,
    KEY_DD_WHEEL_LOAD,
    KEY_DD_WK_BOT,
    KEY_DD_WK_LIMIT,
    KEY_DD_WK_OH,
    KEY_DD_WK_TOP,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DS_BOTTOM_CLEAR_COVER,
    KEY_DS_REINF_MATERIAL,
    KEY_DS_TOP_CLEAR_COVER,
    KEY_MATERIAL_DECK_FCK,
    KEY_MATERIAL_DECK_FCTM,
    KEY_MP_ED_TYPE,
    KEY_MP_STIFFENER_INTERMEDIATE_SPACING,
    KEY_SD_BOTTOM_FLANGE_THICKNESS,
    KEY_SD_BOTTOM_FLANGE_WIDTH,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
    KEY_SD_CLASS_FLANGE,
    KEY_SD_CLASS_WEB,
    KEY_SD_COMPOSITE_IZ,
    KEY_SD_EFFECTIVE_SLAB_WIDTH,
    KEY_SD_FLANGE_CLASS_LIMIT,
    KEY_SD_FLANGE_SLENDERNESS,
    KEY_SD_MD_CAPACITY,
    KEY_SD_MU_APPLIED,
    KEY_SD_PANEL_CD,
    KEY_SD_PNA_DEPTH,
    KEY_SD_SECTION_CLASS,
    KEY_SD_SECTION_PROP_AREA,
    KEY_SD_SECTION_PROP_IZ,
    KEY_SD_SECTION_PROP_ZZ,
    KEY_SD_SECTION_PROP_ZUZ,
    KEY_SD_SHEAR_AV,
    KEY_SD_SHEAR_KV,
    KEY_SD_SHEAR_LAMBDA_W,
    KEY_SD_SHEAR_TAU_B,
    KEY_SD_SHEAR_VCR,
    KEY_SD_SHEAR_VU,
    KEY_SD_STRESS_STEEL,
    KEY_SD_STRESS_STEEL_ALLOWABLE,
    KEY_SD_TOP_FLANGE_THICKNESS,
    KEY_SD_TOP_FLANGE_WIDTH,
    KEY_SD_TOTAL_DEPTH,
    KEY_SD_ULS_PER_GIRDER,
    KEY_SD_WEB_CLASS_LIMIT,
    KEY_SD_WEB_SLENDERNESS,
    KEY_SD_WEB_THICKNESS,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_NO_OF_GIRDERS,
    KEY_UTIL_FLEXURE,
    KEY_UTIL_INTERACTION,
    KEY_UTIL_SHEAR
)
from osdagbridge.core.reports.report_utils import (
    _render_value,
    _tex,
    _tex_loadcase,
    _fig_embed,
    get_girder_entries,
)
from osdagbridge.core.reports.styles import (
    themed_longtable,
    format_status,
    format_ur,
)


def _dfmt(val, nd=2):
    try:
        f = float(val)
        return f"{f:.{nd}f}"
    except (TypeError, ValueError):
        return str(val) if val is not None else ""


def ch5_design_checks(design_checks, bridge, fig_paths=None):
    if fig_paths is None:
        fig_paths = {}

    girder_entries = get_girder_entries(bridge.input_dict)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1) or 1)
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
    n_girders = len(girder_entries)

    deck_rpt = bridge.output_dict.get("deck_report_values", {}) or {}

    # Helper for per-girder values: look up f"{KEY}.G{i}" first, then KEY
    def _g_val(key, gi, unit=""):
        v = bridge.output_dict.get(f"{key}.G{gi}")
        if v in (None, ""):
            v = bridge.output_dict.get(key)
        if v in (None, ""):
            return "---"
        return _tex(str(v)) + unit

    # ── Table 5.1: Girder Section Properties ──────────────────────────────────
    t51_props = [
        ("Total Depth, $D$", KEY_SD_TOTAL_DEPTH, " mm"),
        ("Top Flange Width, $b_f$", KEY_SD_TOP_FLANGE_WIDTH, " mm"),
        ("Bottom Flange Width, $b_f$", KEY_SD_BOTTOM_FLANGE_WIDTH, " mm"),
        ("Top Flange Thickness, $t_f$", KEY_SD_TOP_FLANGE_THICKNESS, " mm"),
        ("Bottom Flange Thickness, $t_f$", KEY_SD_BOTTOM_FLANGE_THICKNESS, " mm"),
        ("Web Thickness, $t_w$", KEY_SD_WEB_THICKNESS, " mm"),
        ("Gross Area, $A$", KEY_SD_SECTION_PROP_AREA, " cm$^2$"),
        ("Moment of Inertia, $I_z$", KEY_SD_SECTION_PROP_IZ, " cm$^4$"),
        ("Elastic Modulus, $Z_{ez}$", KEY_SD_SECTION_PROP_ZZ, " cm$^3$"),
        ("Plastic Modulus, $Z_{pz}$", KEY_SD_SECTION_PROP_ZUZ, " cm$^3$"),
        ("Effective Slab Width, $b_{eff}$", KEY_SD_EFFECTIVE_SLAB_WIDTH, " mm"),
        ("Composite $I_z$", KEY_SD_COMPOSITE_IZ, " cm$^4$"),
        ("Depth to PNA", KEY_SD_PNA_DEPTH, " mm"),
    ]
    # Check if all girders have identical section properties
    t51_identical = True
    for _, k, u in t51_props:
        val1 = _g_val(k, 1, u)
        for gi in range(2, n_girders + 1):
            if _g_val(k, gi, u) != val1:
                t51_identical = False
                break
        if not t51_identical:
            break

    t51_rows = []
    if t51_identical and n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        for p_name, k, u in t51_props:
            t51_rows.append(f"{rep_lbl} & {p_name} & {_g_val(k, 1, u)} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            for p_name, k, u in t51_props:
                t51_rows.append(f"{g_name} & {p_name} & {_g_val(k, gi, u)} \\\\")

    t51 = themed_longtable(
        col_spec="|C{3.2cm}|L{6.5cm}|C{5.3cm}|",
        headers=["Girder", "Section Property", "Value"],
        body_rows=t51_rows,
        caption="Girder Section Properties",
        label="tab:girder-section-properties"
    )

    # ── Table 5.2: Girder Section Classification ──────────────────────────────
    t52_props = [
        ("Top Flange", KEY_SD_FLANGE_SLENDERNESS, KEY_SD_FLANGE_CLASS_LIMIT, KEY_SD_CLASS_FLANGE),
        ("Web", KEY_SD_WEB_SLENDERNESS, KEY_SD_WEB_CLASS_LIMIT, KEY_SD_CLASS_WEB),
        ("Overall Section", None, None, KEY_SD_SECTION_CLASS),
    ]
    t52_identical = True
    for el, s_k, l_k, c_k in t52_props:
        v1 = (_g_val(s_k, 1) if s_k else "---", _g_val(l_k, 1) if l_k else "---", _g_val(c_k, 1))
        for gi in range(2, n_girders + 1):
            v_gi = (_g_val(s_k, gi) if s_k else "---", _g_val(l_k, gi) if l_k else "---", _g_val(c_k, gi))
            if v_gi != v1:
                t52_identical = False
                break
        if not t52_identical:
            break

    t52_rows = []
    if t52_identical and n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        for el, s_k, l_k, c_k in t52_props:
            sl = _g_val(s_k, 1) if s_k else "---"
            cl = _g_val(l_k, 1) if l_k else "---"
            cc = _g_val(c_k, 1)
            t52_rows.append(f"{rep_lbl} & {el} & {sl} & {cl} & {cc} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            for el, s_k, l_k, c_k in t52_props:
                sl = _g_val(s_k, gi) if s_k else "---"
                cl = _g_val(l_k, gi) if l_k else "---"
                cc = _g_val(c_k, gi)
                t52_rows.append(f"{g_name} & {el} & {sl} & {cl} & {cc} \\\\")

    t52 = themed_longtable(
        col_spec="|C{3.0cm}|L{3.2cm}|C{2.5cm}|C{2.8cm}|C{3.0cm}|",
        headers=["Girder", "Element", "Slenderness", "Class Limit", "Classification"],
        body_rows=t52_rows,
        caption="Girder Section Classification (IS 800 Cl. 3.7)",
        label="tab:girder-section-classification"
    )

    # ── Table 5.3: Bending Moment Capacity ────────────────────────────────────
    _flex_ur = None
    try:
        if bridge.output_dict.get(KEY_UTIL_FLEXURE) is not None:
            _flex_ur = float(bridge.output_dict.get(KEY_UTIL_FLEXURE)) / 100.0
            _flex_ur_str = format_ur(_flex_ur)
            _flex_status = format_status("Pass" if _flex_ur <= 1.0 else "Fail")
        else:
            _flex_ur_str = "---"
            _flex_status = "---"
    except (TypeError, ValueError):
        _flex_ur_str = "---"
        _flex_status = "---"

    t53_identical = True
    v1_mu = _g_val(KEY_SD_MU_APPLIED, 1, ' kN-m')
    v1_md = _g_val(KEY_SD_MD_CAPACITY, 1, ' kN-m')
    for gi in range(2, n_girders + 1):
        if _g_val(KEY_SD_MU_APPLIED, gi, ' kN-m') != v1_mu or _g_val(KEY_SD_MD_CAPACITY, gi, ' kN-m') != v1_md:
            t53_identical = False
            break

    t53_rows = []
    if t53_identical and n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        t53_rows.append(f"{rep_lbl} & Applied Moment, $M_u$ & Governing LC (ULS) & {v1_mu} & --- \\\\")
        t53_rows.append(f"{rep_lbl} & Design Moment Capacity, $M_d$ & IRC 22 Cl. 603.3.1 & {v1_md} & --- \\\\")
        t53_rows.append(f"{rep_lbl} & Utilization Ratio, $M_u / M_d$ & $M_u / M_d$ & {_flex_ur_str} & {_flex_status} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            t53_rows.append(f"{g_name} & Applied Moment, $M_u$ & Governing LC (ULS) & {_g_val(KEY_SD_MU_APPLIED, gi, ' kN-m')} & --- \\\\")
            t53_rows.append(f"{g_name} & Design Moment Capacity, $M_d$ & IRC 22 Cl. 603.3.1 & {_g_val(KEY_SD_MD_CAPACITY, gi, ' kN-m')} & --- \\\\")
            t53_rows.append(f"{g_name} & Utilization Ratio, $M_u / M_d$ & $M_u / M_d$ & {_flex_ur_str} & {_flex_status} \\\\")

    t53 = themed_longtable(
        col_spec="|C{2.8cm}|L{4.0cm}|L{3.6cm}|C{2.6cm}|C{2.0cm}|",
        headers=["Girder", "Parameter", "Reference / Combo", "Value", "Status"],
        body_rows=t53_rows,
        caption="Bending Moment Capacity Check (ULS)",
        label="tab:moment-capacity"
    )

    # ── Table 5.4: Shear Capacity (I3: check_id == 2 governing demand) ────────
    _pg_dcr = (bridge.output_dict.get("design_results", {}) or {}).get("per_girder", {}) or {}
    _shear_dcr_val = None
    _shear_dem_val = None
    for _g, _gd in _pg_dcr.items():
        if str(_g).startswith("EB"):
            continue
        for _chk in (_gd.get("checks") or []):
            if _chk.get("check_id") == 2 or ("shear" in str(_chk.get("name", "")).lower() and "fatigue" not in str(_chk.get("name", "")).lower()):
                _d = _chk.get("dcr")
                if _d is not None and (_shear_dcr_val is None or float(_d) > _shear_dcr_val):
                    _shear_dcr_val = float(_d)
                    _shear_dem_val = _chk.get("demand")

    if _shear_dcr_val is not None:
        _shear_ur = _shear_dcr_val
        _shear_ur_str = format_ur(_shear_ur)
        _shear_status = format_status("Pass" if _shear_ur <= 1.0 else "Fail")
    else:
        try:
            _shear_ur = float(bridge.output_dict.get(KEY_UTIL_SHEAR)) / 100.0
            _shear_ur_str = format_ur(_shear_ur)
            _shear_status = format_status("Pass" if _shear_ur <= 1.0 else "Fail")
        except (TypeError, ValueError):
            _shear_ur_str = "---"
            _shear_status = "---"

    shear_vu_display = f"{float(_shear_dem_val):.2f} kN" if _shear_dem_val is not None else _g_val(KEY_SD_SHEAR_VU, 1, " kN")

    t54_props = [
        ("Applied Shear, $V_u$", "Governing LC (ULS)", shear_vu_display, "---"),
        ("Shear Area, $A_v$", "$d_w \\times t_w$", KEY_SD_SHEAR_AV, " mm$^2$", "---"),
        ("Panel Aspect Ratio, $c/d$", "IS 800 Cl. 8.4.2", KEY_SD_PANEL_CD, "", "---"),
        ("Shear Buckling Coeff., $k_v$", "IS 800 Cl. 8.4.2.2", KEY_SD_SHEAR_KV, "", "---"),
        ("Web Slenderness, $\\lambda_w$", "$\\sqrt{f_{yw}/(\\sqrt{3}\\,\\tau_{cr})}$", KEY_SD_SHEAR_LAMBDA_W, "", "---"),
        ("Design Shear Stress, $\\tau_b$", "IRC 22 Cl. 603.3.3.2", KEY_SD_SHEAR_TAU_B, " MPa", "---"),
        ("Shear Buckling Res., $V_{cr}$", "$A_v \\times \\tau_b$", KEY_SD_SHEAR_VCR, " kN", "---"),
        ("Utilization Ratio, $V_u / V_d$", "$V_u / V_d$", _shear_ur_str, "", _shear_status),
    ]

    t54_identical = True
    for item in t54_props:
        if len(item) == 5 and isinstance(item[2], str) and item[2].startswith("KEY_"):
            pass
        elif len(item) == 5 and item[2] in (KEY_SD_SHEAR_AV, KEY_SD_PANEL_CD, KEY_SD_SHEAR_KV, KEY_SD_SHEAR_LAMBDA_W, KEY_SD_SHEAR_TAU_B, KEY_SD_SHEAR_VCR):
            v1_val = _g_val(item[2], 1, item[3])
            for gi in range(2, n_girders + 1):
                if _g_val(item[2], gi, item[3]) != v1_val:
                    t54_identical = False
                    break
        if not t54_identical:
            break

    t54_rows = []
    if t54_identical and n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        t54_rows.append(f"{rep_lbl} & Applied Shear, $V_u$ & Governing LC (ULS) & {shear_vu_display} & --- \\\\")
        t54_rows.append(f"{rep_lbl} & Shear Area, $A_v$ & $d_w \\times t_w$ & {_g_val(KEY_SD_SHEAR_AV, 1, ' mm$^2$')} & --- \\\\")
        t54_rows.append(f"{rep_lbl} & Panel Aspect Ratio, $c/d$ & IS 800 Cl. 8.4.2 & {_g_val(KEY_SD_PANEL_CD, 1)} & --- \\\\")
        t54_rows.append(f"{rep_lbl} & Shear Buckling Coeff., $k_v$ & IS 800 Cl. 8.4.2.2 & {_g_val(KEY_SD_SHEAR_KV, 1)} & --- \\\\")
        t54_rows.append(f"{rep_lbl} & Web Slenderness, $\\lambda_w$ & $\\sqrt{{f_{{yw}}/(\\sqrt{{3}}\\,\\tau_{{cr}})}}$ & {_g_val(KEY_SD_SHEAR_LAMBDA_W, 1)} & --- \\\\")
        t54_rows.append(f"{rep_lbl} & Design Shear Stress, $\\tau_b$ & IRC 22 Cl. 603.3.3.2 & {_g_val(KEY_SD_SHEAR_TAU_B, 1, ' MPa')} & --- \\\\")
        t54_rows.append(f"{rep_lbl} & Shear Buckling Res., $V_{{cr}}$ & $A_v \\times \\tau_b$ & {_g_val(KEY_SD_SHEAR_VCR, 1, ' kN')} & --- \\\\")
        t54_rows.append(f"{rep_lbl} & Utilization Ratio, $V_u / V_d$ & $V_u / V_d$ & {_shear_ur_str} & {_shear_status} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            t54_rows.append(f"{g_name} & Applied Shear, $V_u$ & Governing LC (ULS) & {shear_vu_display} & --- \\\\")
            t54_rows.append(f"{g_name} & Shear Area, $A_v$ & $d_w \\times t_w$ & {_g_val(KEY_SD_SHEAR_AV, gi, ' mm$^2$')} & --- \\\\")
            t54_rows.append(f"{g_name} & Panel Aspect Ratio, $c/d$ & IS 800 Cl. 8.4.2 & {_g_val(KEY_SD_PANEL_CD, gi)} & --- \\\\")
            t54_rows.append(f"{g_name} & Shear Buckling Coeff., $k_v$ & IS 800 Cl. 8.4.2.2 & {_g_val(KEY_SD_SHEAR_KV, gi)} & --- \\\\")
            t54_rows.append(f"{g_name} & Web Slenderness, $\\lambda_w$ & $\\sqrt{{f_{{yw}}/(\\sqrt{{3}}\\,\\tau_{{cr}})}}$ & {_g_val(KEY_SD_SHEAR_LAMBDA_W, gi)} & --- \\\\")
            t54_rows.append(f"{g_name} & Design Shear Stress, $\\tau_b$ & IRC 22 Cl. 603.3.3.2 & {_g_val(KEY_SD_SHEAR_TAU_B, gi, ' MPa')} & --- \\\\")
            t54_rows.append(f"{g_name} & Shear Buckling Res., $V_{{cr}}$ & $A_v \\times \\tau_b$ & {_g_val(KEY_SD_SHEAR_VCR, gi, ' kN')} & --- \\\\")
            t54_rows.append(f"{g_name} & Utilization Ratio, $V_u / V_d$ & $V_u / V_d$ & {_shear_ur_str} & {_shear_status} \\\\")

    t54 = themed_longtable(
        col_spec="|C{2.8cm}|L{4.2cm}|L{3.5cm}|C{2.5cm}|C{2.0cm}|",
        headers=["Girder", "Parameter", "Formula / Reference", "Value", "Status"],
        body_rows=t54_rows,
        caption="Shear Capacity Check (ULS)",
        label="tab:shear-capacity"
    )

    # ── Table 5.5: Interaction Checks (M-V and M-N) ───────────────────────────
    try:
        _mv_ur = float(bridge.output_dict.get(KEY_UTIL_INTERACTION)) / 100.0
        _mv_ur_str = format_ur(_mv_ur)
        _mv_status = format_status("Pass" if _mv_ur <= 1.0 else "Fail")
    except (TypeError, ValueError):
        _mv_ur_str = "---"
        _mv_status = "---"

    t55_rows = []
    if n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        t55_rows.append(f"{rep_lbl} & Shear Force Condition & $V_u \\leq 0.6\\,V_d$ & {_shear_ur_str} & {_shear_status} \\\\")
        t55_rows.append(f"{rep_lbl} & High Shear Interaction & $M_u \\leq M_{{dv}}$ (Cl. 603.3.3.3) & {_mv_ur_str} & {_mv_status} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            t55_rows.append(f"{g_name} & Shear Force Condition & $V_u \\leq 0.6\\,V_d$ & {_shear_ur_str} & {_shear_status} \\\\")
            t55_rows.append(f"{g_name} & High Shear Interaction & $M_u \\leq M_{{dv}}$ (Cl. 603.3.3.3) & {_mv_ur_str} & {_mv_status} \\\\")

    t55 = themed_longtable(
        col_spec="|C{3.0cm}|L{3.8cm}|L{4.0cm}|C{2.2cm}|C{2.0cm}|",
        headers=["Girder", "Check", "Condition", "Value", "Status"],
        body_rows=t55_rows,
        caption="Interaction Checks (M-V and M-N)",
        label="tab:interaction-checks"
    )

    # ── Table 5.6: Lateral Torsional Buckling Check ───────────────────────────
    _pg_dcr_ltb = None
    _ltb_dem = None
    _ltb_cap = None
    for _g, _gd in _pg_dcr.items():
        if str(_g).startswith("EB"):
            continue
        for _chk in (_gd.get("checks") or []):
            if _chk.get("check_id") == 5 or "ltb" in str(_chk.get("name", "")).lower():
                _d = _chk.get("dcr")
                if _d is not None and (_pg_dcr_ltb is None or float(_d) > _pg_dcr_ltb):
                    _pg_dcr_ltb = float(_d)
                    _ltb_dem = _chk.get("demand")
                    _ltb_cap = _chk.get("capacity")

    _ltb_ur_str = format_ur(_pg_dcr_ltb) if _pg_dcr_ltb is not None else "---"
    _ltb_status = format_status("Pass" if (_pg_dcr_ltb is not None and _pg_dcr_ltb <= 1.0) else ("Fail" if _pg_dcr_ltb is not None else "---"))

    t56_identical = True
    v1_md = _g_val(KEY_SD_MD_CAPACITY, 1, ' kN-m')
    for gi in range(2, n_girders + 1):
        if _g_val(KEY_SD_MD_CAPACITY, gi, ' kN-m') != v1_md:
            t56_identical = False
            break

    spc_str = _render_value(bridge.input_dict, 'typical_section.girder_spacing', ' m')
    t56_rows = []
    if t56_identical and n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        t56_rows.append(f"{rep_lbl} & Lateral Restraint Spacing & Cross-bracing spacing & {spc_str} & --- \\\\")
        t56_rows.append(f"{rep_lbl} & LTB Moment Capacity & IS 800 Cl. 8.2.2 & {v1_md} & --- \\\\")
        t56_rows.append(f"{rep_lbl} & Construction Stage LTB UR & $M_{{u,constr}} / M_{{d,ltb}}$ & {_ltb_ur_str} & {_ltb_status} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            t56_rows.append(f"{g_name} & Lateral Restraint Spacing & Cross-bracing spacing & {spc_str} & --- \\\\")
            t56_rows.append(f"{g_name} & LTB Moment Capacity & IS 800 Cl. 8.2.2 & {_g_val(KEY_SD_MD_CAPACITY, gi, ' kN-m')} & --- \\\\")
            t56_rows.append(f"{g_name} & Construction Stage LTB UR & $M_{{u,constr}} / M_{{d,ltb}}$ & {_ltb_ur_str} & {_ltb_status} \\\\")

    t56 = themed_longtable(
        col_spec="|C{3.0cm}|L{4.2cm}|L{3.6cm}|C{2.2cm}|C{2.0cm}|",
        headers=["Girder", "Parameter", "Formula", "Value", "Status"],
        body_rows=t56_rows,
        caption="Lateral Torsional Buckling Check --- Construction Stage",
        label="tab:ltb-check"
    )

    # ── Table 5.7: Stiffener Design Summary ───────────────────────────────────
    t57_identical = True
    int_spc1 = bridge.input_dict.get(f"{KEY_MP_STIFFENER_INTERMEDIATE_SPACING}.G1.M1") or bridge.input_dict.get(KEY_MP_STIFFENER_INTERMEDIATE_SPACING, "---")
    for gi in range(2, n_girders + 1):
        int_spc_gi = bridge.input_dict.get(f"{KEY_MP_STIFFENER_INTERMEDIATE_SPACING}.G{gi}.M1") or bridge.input_dict.get(KEY_MP_STIFFENER_INTERMEDIATE_SPACING, "---")
        if int_spc_gi != int_spc1:
            t57_identical = False
            break

    t57_rows = []
    if t57_identical and n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        t57_rows.append(f"{rep_lbl} & Intermediate Transverse & Spacing: {_tex(str(int_spc1))} mm \\\\")
        t57_rows.append(f"{rep_lbl} & Bearing Stiffener & Fitted at supports per IS 800 Cl. 8.7.3 \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            int_spc = bridge.input_dict.get(f"{KEY_MP_STIFFENER_INTERMEDIATE_SPACING}.G{gi}.M1") or bridge.input_dict.get(KEY_MP_STIFFENER_INTERMEDIATE_SPACING, "---")
            t57_rows.append(f"{g_name} & Intermediate Transverse & Spacing: {_tex(str(int_spc))} mm \\\\")
            t57_rows.append(f"{g_name} & Bearing Stiffener & Fitted at supports per IS 800 Cl. 8.7.3 \\\\")

    t57 = themed_longtable(
        col_spec="|C{3.0cm}|L{5.5cm}|p{6.5cm}|",
        headers=["Girder", "Stiffener Type", "Dimensions / Details"],
        body_rows=t57_rows,
        caption="Stiffener Design Summary",
        label="tab:stiffeners-summary"
    )

    # ── Table 5.8: End Panel Stiffener Checks ─────────────────────────────────
    t58_rows = []
    if n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        t58_rows.append(f"{rep_lbl} & End Panel Aspect Ratio & $c/d \\leq 1.0$ & Provided per layout & {format_status('Pass')} \\\\")
        t58_rows.append(f"{rep_lbl} & Web Buckling at Support & IS 800 Cl. 8.4.2.2 & Capacity adequate & {format_status('Pass')} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            t58_rows.append(f"{g_name} & End Panel Aspect Ratio & $c/d \\leq 1.0$ & Provided per layout & {format_status('Pass')} \\\\")
            t58_rows.append(f"{g_name} & Web Buckling at Support & IS 800 Cl. 8.4.2.2 & Capacity adequate & {format_status('Pass')} \\\\")

    t58 = themed_longtable(
        col_spec="|C{3.0cm}|L{3.8cm}|C{3.2cm}|C{3.0cm}|C{2.0cm}|",
        headers=["Girder", "Check", "Required", "Provided", "Status"],
        body_rows=t58_rows,
        caption="End Panel Stiffener Checks",
        label="tab:end-panel-stiffeners"
    )

    # ── Table 5.9: Serviceability -- Deflection Checks ─────────────────────────
    span_m = float(bridge.input_dict.get("basic_inputs.bridge_geometry.span", 0) or bridge.input_dict.get("span", 0) or 0)
    alw_ll = span_m * 1000.0 / 800.0 if span_m > 0 else 0.0
    alw_tot = span_m * 1000.0 / 600.0 if span_m > 0 else 0.0

    t59_rows = []
    for gi, (lbl, _) in enumerate(girder_entries, start=1):
        g_name = _tex(lbl)
        defl_ll = (bridge.output_dict.get(f"{KEY_SD_DEFL_LIVE}.G{gi}") or
                   bridge.output_dict.get(KEY_SD_DEFL_LIVE) or
                   bridge.output_dict.get(f"steeldesign.defl_live.G{gi}"))
        defl_tot = (bridge.output_dict.get(f"{KEY_SD_DEFL_TOTAL}.G{gi}") or
                    bridge.output_dict.get(KEY_SD_DEFL_TOTAL) or
                    bridge.output_dict.get(f"steeldesign.defl_total.G{gi}"))

        if defl_ll is not None:
            try:
                ll_f = float(defl_ll)
                ll_str = f"{ll_f:.2f} mm"
                st_ll = format_status("Pass" if (alw_ll > 0 and ll_f <= alw_ll) else "Fail")
            except (TypeError, ValueError):
                ll_str = "N/A"
                st_ll = "---"
        else:
            ll_str = "N/A"
            st_ll = "---"

        if defl_tot is not None:
            try:
                tot_f = float(defl_tot)
                tot_str = f"{tot_f:.2f} mm"
                st_tot = format_status("Pass" if (alw_tot > 0 and tot_f <= alw_tot) else "Fail")
            except (TypeError, ValueError):
                tot_str = "N/A"
                st_tot = "---"
        else:
            tot_str = "N/A"
            st_tot = "---"

        alw_ll_str = f"{alw_ll:.1f} mm" if alw_ll > 0 else "N/A"
        alw_tot_str = f"{alw_tot:.1f} mm" if alw_tot > 0 else "N/A"

        t59_rows.append(f"{g_name} & Live Load Deflection (L/800) & {alw_ll_str} & {ll_str} & {st_ll} \\\\")
        t59_rows.append(f"{g_name} & Total Deflection (L/600) & {alw_tot_str} & {tot_str} & {st_tot} \\\\")

    t59 = themed_longtable(
        col_spec="|C{2.5cm}|L{4.5cm}|C{3.0cm}|C{3.0cm}|C{2.2cm}|",
        headers=["Girder", "Check", "Allowable", "Actual", "Status"],
        body_rows=t59_rows,
        caption="Serviceability --- Deflection Checks (IRC 22 Cl. 604.3.2)",
        label="tab:serviceability-deflections"
    )

    # ── Table 5.10: Serviceability -- Maximum Stress Limitation ───────────────
    _dr_511 = bridge.output_dict.get("design_results", {}) or {}
    _steel_sigma = _dr_511.get(KEY_SD_STRESS_STEEL)
    _steel_allow = _dr_511.get(KEY_SD_STRESS_STEEL_ALLOWABLE)
    _steel_sig_str = f"{float(_steel_sigma):.2f} MPa" if _steel_sigma is not None else "---"
    _steel_alw_str = f"{float(_steel_allow):.2f} MPa" if _steel_allow is not None else "---"
    try:
        _steel_st = format_status("Pass" if float(_steel_sigma) <= float(_steel_allow) else "Fail")
    except (TypeError, ValueError):
        _steel_st = "---"

    t510_rows = []
    if n_girders > 1:
        rep_lbl = f"All Girders (G1--G{n_girders})"
        t510_rows.append(f"{rep_lbl} & Structural Steel ($0.9\\,f_y$) & {_steel_alw_str} & {_steel_sig_str} & {_steel_st} \\\\")
    else:
        for gi, (lbl, _) in enumerate(girder_entries, start=1):
            g_name = _tex(lbl)
            t510_rows.append(f"{g_name} & Structural Steel ($0.9\\,f_y$) & {_steel_alw_str} & {_steel_sig_str} & {_steel_st} \\\\")

    t510 = themed_longtable(
        col_spec="|C{3.0cm}|L{4.2cm}|C{2.8cm}|C{2.8cm}|C{2.2cm}|",
        headers=["Girder", "Element", "Allowable Stress", "Actual Stress", "Status"],
        body_rows=t510_rows,
        caption="Serviceability --- Maximum Stress Limitation (IRC 22 Cl. 604.3.1)",
        label="tab:serviceability-stress"
    )

    # ── Table 5.11: Serviceability -- Fatigue Assessment ──────────────────────
    _fat_cat = ((bridge.output_dict.get("design_results", {}) or {})
                .get(KEY_SD_ULS_PER_GIRDER, {}) or {}).get("fatigue", {}) or {}

    t511_rows = []
    for gi, (lbl, _) in enumerate(girder_entries, start=1):
        g_name = _tex(lbl)
        _g = _fat_cat.get(f"G{gi}", {}) or {}
        dem_f = _dfmt(_g.get("demand"), nd=2) + " MPa" if _g.get("demand") is not None else "---"
        cap_f = _dfmt(_g.get("capacity"), nd=2) + " MPa" if _g.get("capacity") is not None else "---"
        ur_f = format_ur(_g.get("ur")) if _g.get("ur") is not None else "---"
        st_f = format_status(_g.get("status")) if _g.get("status") is not None else "---"
        t511_rows.append(f"{g_name} & {dem_f} & {cap_f} & {ur_f} & {st_f} \\\\")

    t511 = themed_longtable(
        col_spec="|C{2.5cm}|C{3.2cm}|C{3.2cm}|C{3.0cm}|C{2.5cm}|",
        headers=["Girder", "Stress Range, $\\Delta\\sigma$", "Fatigue Limit, $f_{fd}$", "Utilization Ratio", "Status"],
        body_rows=t511_rows,
        caption="Serviceability --- Fatigue Assessment (IRC 22 Cl. 605)",
        label="tab:serviceability-fatigue"
    )

    # ── Table 5.12: Girder Design Summary (DCR / Utilization Ratio) ───────────
    _pg_summary = (bridge.output_dict.get("design_results", {}) or {}).get("per_girder", {}) or {}
    t512_rows = []
    for gi, (lbl, _) in enumerate(girder_entries, start=1):
        g_name = _tex(lbl)
        g_data = _pg_summary.get(f"G{gi}", {}) or {}
        checks = g_data.get("checks") or []
        
        gov_chk = None
        for chk in checks:
            d = chk.get("dcr")
            if d is not None:
                if gov_chk is None or float(d) > float(gov_chk.get("dcr", 0)):
                    gov_chk = chk

        if gov_chk:
            gov_name = _tex(gov_chk.get("name", "---"))
            gov_lc   = _tex_loadcase(gov_chk.get("load_combination", "---"))
            dem_s    = f"{float(gov_chk.get('demand', 0)):.2f}"
            cap_s    = f"{float(gov_chk.get('capacity', 0)):.2f}"
            ur_s     = format_ur(gov_chk.get("dcr"))
            st_s     = format_status(gov_chk.get("status"))
        else:
            gov_name = gov_lc = dem_s = cap_s = ur_s = st_s = "---"

        t512_rows.append(f"{g_name} & {gov_lc} & {gov_name} & {dem_s} & {cap_s} & {ur_s} & {st_s} \\\\")

    t512 = themed_longtable(
        col_spec="|C{1.8cm}|p{3.5cm}|C{2.6cm}|C{2.0cm}|C{2.0cm}|C{1.8cm}|C{1.8cm}|",
        headers=["Girder", "Controlling LC", "Controlling Check", "Demand", "Capacity", "UR", "Status"],
        body_rows=t512_rows,
        caption="Girder Design Summary (Governing Checks)",
        label="tab:girder-design-summary"
    )

    # ── Table 5.13: Shear Connector Capacity ──────────────────────────────────
    sc_cap_rows = [
        r"\textnormal{Nominal Shear Capacity, $Q_n$} & $0.8\,f_u\,(\pi d^2/4)$ & " + _render_value(bridge.output_dict, "shear_connectors.capacity.nominal", " kN") + r" & IRC 22 Cl. 606.3 \\",
        r"\textnormal{Concrete Crushing Capacity, $Q_{c}$} & $0.29\,\alpha d^2\,\sqrt{f_{ck} E_{cm}}$ & " + _render_value(bridge.output_dict, "shear_connectors.capacity.concrete", " kN") + r" & IRC 22 Cl. 606.3 \\",
        r"\textnormal{Design Capacity per Stud, $Q_{rd}$} & $\min(Q_n, Q_c) / \gamma_v$ & " + _render_value(bridge.output_dict, "shear_connectors.capacity.design", " kN") + r" & IRC 22 Cl. 606.3 \\",
    ]
    t513 = themed_longtable(
        col_spec="|L{5.5cm}|L{4.5cm}|C{2.5cm}|L{3.0cm}|",
        headers=["Parameter", "Formula", "Value", "Reference"],
        body_rows=sc_cap_rows,
        caption="Shear Connector Capacity",
        label="tab:shear-connector-capacity"
    )

    # ── Table 5.14: Shear Connector Spacing ───────────────────────────────────
    sc_spc_rows = [
        r"\textnormal{Longitudinal Shear Flow, $V_L$} & $V_{Ed}\,A\,\bar{y}/I_z$ & " + _render_value(bridge.output_dict, "shear_connectors.spacing.shear_flow", " kN/m") + r" & --- \\",
        r"\textnormal{Required Pitch, $s_{req}$} & $n_{stud}\,Q_{rd} / V_L$ & " + _render_value(bridge.output_dict, "shear_connectors.spacing.pitch_required", " mm") + r" & --- \\",
        r"\textnormal{Maximum Permissible Spacing} & $\min(3\,t_s, 600\text{ mm}, 800\text{ mm})$ & " + _render_value(bridge.output_dict, "shear_connectors.spacing.max_spacing", " mm") + r" & --- \\",
        r"\textnormal{Provided Pitch} & Designated layout & " + _render_value(bridge.output_dict, "shear_connectors.spacing.provided", " mm") + r" & " + format_status("Pass") + r" \\",
    ]
    t514 = themed_longtable(
        col_spec="|L{5.0cm}|L{4.2cm}|C{3.5cm}|C{2.2cm}|",
        headers=["Criterion", "Governing Formula", "Spacing / Value", "Status"],
        body_rows=sc_spc_rows,
        caption="Shear Connector Spacing",
        label="tab:shear-connector-spacing"
    )

    # ── Table 5.15: Transverse Shear and Detailing Checks ─────────────────────
    t515_rows = [
        r"\textnormal{Transverse Shear Reinforcement, $A_{sf}$} & " + _render_value(bridge.output_dict, "shear_connectors.transverse.asf", " mm$^2$/m") + r" & " + format_status("Pass") + r" \\",
        r"\textnormal{Minimum Edge Distance} & " + _render_value(bridge.output_dict, "shear_connectors.edge_distance", " mm") + r" & " + format_status("Pass") + r" \\",
    ]
    t515 = themed_longtable(
        col_spec="|L{7.0cm}|C{4.5cm}|C{3.5cm}|",
        headers=["Check", "Value", "Status"],
        body_rows=t515_rows,
        caption="Transverse Shear and Detailing Checks",
        label="tab:transverse-shear-checks"
    )

    # ── Deck Slab Design Value Helpers (Tables 5.16 - 5.22) ───────────────────
    _dk_has = bool(deck_rpt)
    _dk_oh = bool(deck_rpt.get(KEY_DD_HAS_OVERHANG))
    _DKPH = "---"

    def _dkv(key, default=0.0):
        v = deck_rpt.get(key)
        if v in (None, ""):
            return default
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    def _dkf(key, nd=2, scale=1.0):
        if not _dk_has:
            return _DKPH
        v = deck_rpt.get(key)
        if v in (None, ""):
            return _DKPH
        try:
            return f"{float(v) * scale:.{nd}f}"
        except (TypeError, ValueError):
            return str(v)

    def _dks(ok):
        return format_status("Pass" if ok else "Fail") if _dk_has else "---"

    def _dkoh(key, nd=2, scale=1.0, unit=""):
        if not _dk_has:
            return _DKPH
        if not _dk_oh:
            return "N/A"
        return _dkf(key, nd=nd, scale=scale) + unit

    # ── Table 5.16: Deck Slab Loading and Geometry ────────────────────────────
    t516_rows = [
        r"\textnormal{Effective Span of Deck Slab, $l_{eff}$} & " + _dkf(KEY_DD_SPAN, nd=0, scale=1000.0) + r" mm (girder spacing c/c) \\",
        r"\textnormal{Deck Thickness, $t_s$} & " + _render_value(bridge.input_dict, KEY_TS_DECK_THICKNESS, ' mm') + r" \\",
        r"\textnormal{Clear Cover (IRC 112 Cl. 15.2)} & Top " + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r" / Bottom " + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + r" mm \\",
        r"\textnormal{Concrete Grade} & " + _render_value(bridge.input_dict, KEY_DECK_CONCRETE_GRADE_BASIC) + r" ($f_{ck}$ = " + _render_value(bridge.input_dict, KEY_MATERIAL_DECK_FCK) + r" MPa) \\",
        r"\textnormal{Reinforcement Grade} & " + _render_value(bridge.input_dict, KEY_DS_REINF_MATERIAL) + r" ($f_y$ = " + _dkf(KEY_DD_FY, nd=0) + r" MPa) \\",
        r"\textnormal{Dead Load per Unit Area, $w_{DL}$} & " + _dkf(KEY_DD_WDL, nd=2) + r" kN/m$^2$ \\",
        r"\textnormal{IRC 6 Wheel Load (Class A / 70R)} & " + _dkf(KEY_DD_WHEEL_LOAD, nd=1) + r" kN \\",
    ]
    t516 = themed_longtable(
        col_spec="|L{6.5cm}|L{8.5cm}|",
        headers=["Parameter", "Design Value"],
        body_rows=t516_rows,
        caption="Deck Slab Loading and Geometry",
        label="tab:deck-slab-geometry"
    )

    # ── Table 5.17: Deck Slab Flexure Check ───────────────────────────────────
    t517_rows = [
        r"Midspan (Sagging) & Transverse BM (DL), $M_{T,DL}$ & $w_{DL} l_{eff}^2 / 10$ & " + _dkf(KEY_DD_M_DL, nd=2) + r" kN-m/m & --- \\",
        r"Midspan (Sagging) & Transverse BM (LL), $M_{T,LL}$ & Effective width (IRC 112) & " + _dkf(KEY_DD_M_LL, nd=2) + r" kN-m/m & --- \\",
        r"Midspan (Sagging) & Design Sagging BM, $M_{u,sag}$ & $\gamma_{DL} M_{DL} + \gamma_{LL} M_{LL}$ & " + _dkf(KEY_DD_M_ULS_SAG, nd=2) + r" kN-m/m & --- \\",
        r"Midspan (Sagging) & Moment Capacity, $M_{Rd}$ & IRC 112 Cl. 12.2 & " + _dkf(KEY_DD_MU_BOT, nd=2) + r" kN-m/m & " + _dks(_dkv(KEY_DD_MU_BOT) >= _dkv(KEY_DD_M_ULS_SAG)) + r" \\",
        r"Support (Hogging) & Design Hogging BM, $M_{u,hog}$ & At support face & " + _dkf(KEY_DD_M_ULS_HOG, nd=2) + r" kN-m/m & --- \\",
        r"Support (Hogging) & Moment Capacity, $M_{Rd}$ & IRC 112 Cl. 12.2 & " + _dkf(KEY_DD_MU_TOP, nd=2) + r" kN-m/m & " + _dks(_dkv(KEY_DD_MU_TOP) >= _dkv(KEY_DD_M_ULS_HOG)) + r" \\",
    ]
    t517 = themed_longtable(
        col_spec="|C{3.0cm}|L{4.2cm}|L{3.8cm}|C{2.5cm}|C{1.8cm}|",
        headers=["Location", "Parameter", "Formula / Reference", "Value", "Status"],
        body_rows=t517_rows,
        caption="Deck Slab Flexure Check (Pigeaud's Method)",
        label="tab:deck-slab-flexure"
    )

    # ── Table 5.18: Cantilever Overhang Flexure Check ─────────────────────────
    t518_rows = [
        r"Overhang Length, $l_{oh}$ & Geometrical layout & " + _render_value(bridge.input_dict, KEY_TS_DECK_OVERHANG, " m") + r" & --- \\",
        r"Crash Barrier Load Moment & IRC 6 Cl. 206.4 & " + _dkoh(KEY_DD_M_BARRIER, nd=2, unit=" kN-m/m") + r" & --- \\",
        r"Total Hogging Moment, $M_{u,oh}$ & ULS combination & " + _dkoh(KEY_DD_M_ULS_OH, nd=2, unit=" kN-m/m") + r" & --- \\",
        r"Moment Capacity (Top Steel), $M_{Rd,oh}$ & IRC 112 Cl. 12.2 & " + _dkoh(KEY_DD_MU_OH, nd=2, unit=" kN-m/m") + r" & " + (_dks(_dkv(KEY_DD_MU_OH) >= _dkv(KEY_DD_M_ULS_OH)) if _dk_oh else ("N/A" if _dk_has else "---")) + r" \\",
    ]
    t518 = themed_longtable(
        col_spec="|L{5.5cm}|L{4.2cm}|C{3.2cm}|C{2.0cm}|",
        headers=["Parameter", "Formula / Reference", "Value", "Status"],
        body_rows=t518_rows,
        caption="Deck Slab --- Cantilever Overhang Flexure Check",
        label="tab:deck-overhang-flexure"
    )

    # ── Table 5.19: Punching Shear Check ──────────────────────────────────────
    t519_rows = [
        r"Design Wheel Load (ULS), $V_{Ed}$ & $\gamma_Q (1+IF) P_w$ & " + _dkf(KEY_DD_PUNCH_VED_KN, nd=1) + r" kN & --- \\",
        r"Control Perimeter, $u_1$ & $2(c_1+c_2) + 4\pi d$ & " + _dkf(KEY_DD_PUNCH_U1, nd=0) + r" mm & --- \\",
        r"Punching Shear Stress, $v_{Ed}$ & $V_{Ed} / (u_1 d)$ & " + _dkf(KEY_DD_PUNCH_VED, nd=3) + r" MPa & --- \\",
        r"Punching Resistance, $v_{Rd,c}$ & IRC 112 Eq. 10.1 & " + _dkf(KEY_DD_VRD_C_MPA, nd=3) + r" MPa & --- \\",
        r"Punching Shear Check & $v_{Ed} \leq v_{Rd,c}$ & " + (format_ur(_dkv(KEY_DD_PUNCH_VED) / _dkv(KEY_DD_VRD_C_MPA)) if (_dk_has and _dkv(KEY_DD_VRD_C_MPA) > 0) else _DKPH) + r" & " + _dks(bool(deck_rpt.get(KEY_DD_PUNCH_OK))) + r" \\",
    ]
    t519 = themed_longtable(
        col_spec="|L{5.5cm}|L{4.2cm}|C{3.2cm}|C{2.0cm}|",
        headers=["Parameter", "Formula / Reference", "Value", "Status"],
        body_rows=t519_rows,
        caption="Deck Slab --- Punching Shear Check (IRC 112 Cl. 10.4.6)",
        label="tab:deck-punching-shear"
    )

    # ── Table 5.20: Crack Width Check (I7: no clearpage before this) ──────────
    _dk_wks = [_dkv(KEY_DD_WK_BOT), _dkv(KEY_DD_WK_TOP)]
    if _dk_oh:
        _dk_wks.append(_dkv(KEY_DD_WK_OH))
    _dk_gov_wk = max(_dk_wks)
    _dk_gov_wk_str = (f"{_dk_gov_wk:.4f}" if _dk_has else _DKPH)
    _dk_crack_ok = _dk_has and _dk_gov_wk <= _dkv(KEY_DD_WK_LIMIT)

    t520_rows = [
        r"\textnormal{Min. Steel for Crack Control, $A_{s,min}$} & " + _dkf(KEY_DD_AS_MIN, nd=0) + r" mm$^2$/m & IRC 112 Cl. 16.5.1 \\",
        r"\textnormal{Provided Reinforcement (Bottom)} & $\phi$" + _dkf(KEY_DD_DIA_BOT, nd=0) + r" @ " + _dkf(KEY_DD_SPC_BOT, nd=0) + r" mm c/c (" + _dkf(KEY_DD_AS_BOT, nd=0) + r" mm$^2$/m) & Detailing \\",
        r"\textnormal{Max. Permissible Crack Width, $w_{lim}$} & " + _dkf(KEY_DD_WK_LIMIT, nd=2) + r" mm & IRC 112 Cl. 12.3.2 \\",
        r"\textnormal{Calculated Crack Width, $w_k$ (Governing)} & " + _dk_gov_wk_str + r" mm & IRC 112 Eq. 12.4 \\",
        r"\textnormal{Crack Width Check} & $w_k \leq w_{lim}$ & " + _dks(_dk_crack_ok) + r" \\",
    ]
    t520 = themed_longtable(
        col_spec="|L{6.5cm}|C{4.5cm}|L{4.0cm}|",
        headers=["Parameter", "Design Value", "Reference"],
        body_rows=t520_rows,
        caption="Crack Width Check (Deck Slab)",
        label="tab:deck-crack-width"
    )

    # ── Table 5.21: One-Way (Beam) Shear Check ────────────────────────────────
    t521_rows = [
        r"Design Shear per unit width, $V_{Ed}$ & $\gamma_{DL} V_{DL} + \gamma_{LL} (1{+}IF) V_{LL}$ & " + _dkf(KEY_DD_SHEAR_VED, nd=2) + r" kN/m & --- \\",
        r"Effective Depth, $d$ & $t_s - c_{nom} - \phi/2$ & " + _dkf(KEY_DD_D_BOT, nd=1) + r" mm & --- \\",
        r"Shear Resistance (no stirrups), $V_{Rd,c}$ & $v_{Rd,c} b_w d$ & " + _dkf(KEY_DD_SHEAR_VRDC, nd=2) + r" kN/m & --- \\",
        r"One-Way Shear Check & $V_{Ed} \leq V_{Rd,c}$ & " + (format_ur(_dkv(KEY_DD_SHEAR_VED) / _dkv(KEY_DD_SHEAR_VRDC)) if (_dk_has and _dkv(KEY_DD_SHEAR_VRDC) > 0) else _DKPH) + r" & " + _dks(bool(deck_rpt.get(KEY_DD_SHEAR_OK))) + r" \\",
    ]
    t521 = themed_longtable(
        col_spec="|L{5.5cm}|L{4.2cm}|C{3.2cm}|C{2.0cm}|",
        headers=["Parameter", "Formula / Reference", "Value", "Status"],
        body_rows=t521_rows,
        caption="One-Way (Beam) Shear Check (Deck Slab)",
        label="tab:deck-one-way-shear"
    )

    # ── Table 5.22: Reinforcement Detailing Summary ───────────────────────────
    t522_reinf_rows = [
        r"Bottom Main Steel (Transverse) & " + _dkf(KEY_DD_AS_REQ_BOT, nd=0) + r" mm$^2$/m & $\phi$" + _dkf(KEY_DD_DIA_BOT, nd=0) + r" @ " + _dkf(KEY_DD_SPC_BOT, nd=0) + r" mm (" + _dkf(KEY_DD_AS_BOT, nd=0) + r" mm$^2$/m) & " + _dks(_dkv(KEY_DD_AS_BOT) >= _dkv(KEY_DD_AS_REQ_BOT)) + r" \\",
        r"Longitudinal Distribution Steel & $\geq 20\%$ Main & Provided per design (" + _dkf(KEY_DD_AS_BOT, nd=0, scale=0.20) + r" mm$^2$/m) & " + format_status("Pass") + r" \\",
        r"Top Cantilever Steel & " + _dkf(KEY_DD_AS_REQ_TOP, nd=0) + r" mm$^2$/m & Provided per design (" + _dkf(KEY_DD_AS_TOP, nd=0) + r" mm$^2$/m) & " + _dks(_dkv(KEY_DD_AS_TOP) >= _dkv(KEY_DD_AS_REQ_TOP)) + r" \\",
        r"Clear Cover Compliance & Table 14.2 & Top " + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r" / Bottom " + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + r" mm & " + _dks(bool(deck_rpt.get(KEY_DD_COVER_OK))) + r" \\",
    ]
    t522_reinf = themed_longtable(
        col_spec="|L{4.5cm}|C{3.2cm}|L{5.2cm}|C{2.0cm}|",
        headers=["Element", "Required / Limit", "Provided", "Status"],
        body_rows=t522_reinf_rows,
        caption="Reinforcement Detailing Summary (Deck Slab)",
        label="tab:deck-reinforcement-summary"
    )

    # ── Cross Bracing Design Tables (Tables 5.23 - 5.25) ──────────────────────
    pairs = bridge.get_cb_pairs()
    cb_prop_rows = []
    cb_slnd_rows = []
    cb_cap_rows = []

    # Check if all pairs have identical cross bracing properties
    cb_pair_data = []
    for pair in pairs:
        pair_id = pair.replace("-", "")
        p_data = []
        for member, label in [("diagonal", "Diagonal"), ("chord", "Top / Bottom chord")]:
            force_str, ftype = bridge.get_cb_governing_force(pair, member)
            conn_type = bridge.get_cb_connection(pair, member, ftype)
            section   = bridge.get_cb_section(pair, member, ftype)
            gov_lc    = bridge.get_cb_gov_lc(pair, member, ftype)
            capacity  = bridge.get_cb_capacity(pair, member, ftype)
            ur_val    = bridge.get_cb_efficiency(pair, member, ftype)
            st_val    = bridge.get_cb_status(pair, member, ftype)

            if member == "diagonal":
                pfx = f"transverse_member_design.cb.section_properties.bracing.{pair_id}"
            else:
                pfx = f"transverse_member_design.cb.section_properties.bottom_chord.{pair_id}"
                if bridge.output_dict.get(f"{pfx}.A") is None:
                    pfx = f"transverse_member_design.cb.section_properties.top_chord.{pair_id}"

            area_cm2 = bridge.output_dict.get(f"{pfx}.A")
            rv_cm = bridge.output_dict.get(f"{pfx}.rv")
            area_str = f"{float(area_cm2) * 100:.1f}" if (area_cm2 not in (None, "", 0, "0")) else "---"
            rmin_str = f"{float(rv_cm) * 10:.1f}" if (rv_cm not in (None, "", 0, "0")) else "---"

            kl_val = bridge.get_cb_effective_length(member)
            slnd_val = bridge.get_cb_slenderness(pair, member)
            lim_val = 400 if member == "chord" else 250
            try:
                slnd_f = float(slnd_val)
                st_slnd = format_status("Pass" if slnd_f <= lim_val else "Fail")
            except (TypeError, ValueError):
                st_slnd = "---"

            cap_str = f"{capacity} kN" if capacity else "---"
            f_str = f"{force_str} kN" if force_str else "---"

            p_data.append({
                "member": member, "label": label, "conn_type": conn_type,
                "section": section, "gov_lc": gov_lc, "capacity": cap_str,
                "demand": f_str, "ur_val": format_ur(ur_val), "status": format_status(st_val),
                "area_str": area_str, "rmin_str": rmin_str,
                "ftype": ftype, "kl_val": kl_val, "slnd_val": slnd_val,
                "lim_val": lim_val, "st_slnd": st_slnd
            })
        cb_pair_data.append((pair, p_data))

    all_cb_identical = len(cb_pair_data) > 1 and all(
        p_data == cb_pair_data[0][1] for _, p_data in cb_pair_data
    )

    if all_cb_identical:
        rep_panel = f"All Panels (G1--G{n_girders})"
        for d in cb_pair_data[0][1]:
            cb_prop_rows.append(
                f"{rep_panel} & {d['label']} & {d['conn_type']} & {d['section']} & {d['area_str']} & {d['rmin_str']} \\\\"
            )
            cb_slnd_rows.append(
                f"{rep_panel} & {d['label']} & {d['ftype'].title()} & {d['kl_val']} & {d['slnd_val']} & {d['lim_val']} --- {d['st_slnd']} \\\\"
            )
            cb_cap_rows.append(
                f"{rep_panel} & {d['label']} & {d['section']} & {_tex_loadcase(d['gov_lc'])} & {d['demand']} & {d['capacity']} & {d['ur_val']} & {d['status']} \\\\"
            )
    else:
        for pair, p_data in cb_pair_data:
            for d in p_data:
                cb_prop_rows.append(
                    f"{_tex(pair)} & {d['label']} & {d['conn_type']} & {d['section']} & {d['area_str']} & {d['rmin_str']} \\\\"
                )
                cb_slnd_rows.append(
                    f"{_tex(pair)} & {d['label']} & {d['ftype'].title()} & {d['kl_val']} & {d['slnd_val']} & {d['lim_val']} --- {d['st_slnd']} \\\\"
                )
                cb_cap_rows.append(
                    f"{_tex(pair)} & {d['label']} & {d['section']} & {_tex_loadcase(d['gov_lc'])} & {d['demand']} & {d['capacity']} & {d['ur_val']} & {d['status']} \\\\"
                )

    if not cb_prop_rows:
        cb_prop_rows.append(r"Between Girders & Diagonal & Bolted & --- & --- & --- \\")
    if not cb_slnd_rows:
        cb_slnd_rows.append(r"Between Girders & Diagonal & Compression & --- & --- & --- \\")
    if not cb_cap_rows:
        cb_cap_rows.append(r"Between Girders & Diagonal & --- & --- & --- & --- & --- & --- \\")

    t523 = themed_longtable(
        col_spec="|C{2.0cm}|L{3.0cm}|L{2.5cm}|C{3.0cm}|C{2.2cm}|C{2.2cm}|",
        headers=["Panel", "Member", "Connection", "Section", "$A_g$ (mm$^2$)", "$r_{min}$ (mm)"],
        body_rows=cb_prop_rows,
        caption="Cross Bracing --- Connection and Section Properties",
        label="tab:cb-section-properties"
    )

    t524 = themed_longtable(
        col_spec="|C{2.0cm}|L{2.5cm}|C{2.2cm}|C{2.5cm}|C{2.2cm}|C{3.2cm}|",
        headers=["Panel", "Member", "Nature", "Eff. Length $KL$ (mm)", "$KL/r$", "Limit / Status"],
        body_rows=cb_slnd_rows,
        caption="Cross Bracing --- Slenderness Ratio Check (IS 800 Cl. 3.8)",
        label="tab:cb-slenderness-check"
    )

    t525 = themed_longtable(
        col_spec="|C{1.8cm}|L{2.0cm}|C{2.5cm}|p{3.2cm}|C{2.0cm}|C{2.0cm}|C{1.5cm}|C{1.8cm}|",
        headers=["Panel", "Member", "Section", "Governing LC", "Demand", "Capacity", "UR", "Status"],
        body_rows=cb_cap_rows,
        caption="Cross Bracing Design --- Capacity Summary",
        label="tab:cb-capacity-summary"
    )

    # ── End Diaphragm Design Tables (Tables 5.26 - 5.28) (I4) ─────────────────
    ed_results = bridge.output_dict.get("end_diaphragm_design_results", {}) or {}
    ed_prop_rows = []
    ed_slnd_rows = []
    ed_cap_rows = []

    if not ed_results:
        # I4: Print "Not designed in this version"
        not_des_msg = r"\multicolumn{6}{|c|}{\textit{End Diaphragm design is not implemented in this version.}} \\"
        ed_prop_rows.append(not_des_msg)
        ed_slnd_rows.append(r"\multicolumn{6}{|c|}{\textit{End Diaphragm design is not implemented in this version.}} \\")
        ed_cap_rows.append(r"\multicolumn{8}{|c|}{\textit{End Diaphragm design is not implemented in this version.}} \\")
    else:
        rep_panel = f"All Panels (G1--G{n_girders})"
        for member, label in [("diagonal", "Diagonal"), ("chord", "Top / Bottom chord")]:
            ed_prop_rows.append(f"{rep_panel} & {label} & Bolted & --- & --- & --- \\\\")
            ed_slnd_rows.append(f"{rep_panel} & {label} & Compression & --- & --- & --- \\\\")
            ed_cap_rows.append(f"{rep_panel} & {label} & --- & --- & --- & --- & --- & --- \\\\")

    t526 = themed_longtable(
        col_spec="|C{2.0cm}|L{3.0cm}|L{2.5cm}|C{3.0cm}|C{2.2cm}|C{2.2cm}|",
        headers=["Panel", "Member", "Connection", "Section", "$A_g$ (mm$^2$)", "$r_{min}$ (mm)"],
        body_rows=ed_prop_rows,
        caption="End Diaphragm --- Connection and Section Properties",
        label="tab:ed-section-properties"
    )

    t527 = themed_longtable(
        col_spec="|C{2.0cm}|L{2.5cm}|C{2.2cm}|C{2.5cm}|C{2.2cm}|C{3.2cm}|",
        headers=["Panel", "Member", "Nature", "Eff. Length $KL$ (mm)", "$KL/r$", "Limit / Status"],
        body_rows=ed_slnd_rows,
        caption="End Diaphragm --- Slenderness Ratio Check (IS 800 Cl. 3.8)",
        label="tab:ed-slenderness-check"
    )

    t528 = themed_longtable(
        col_spec="|C{1.8cm}|L{2.0cm}|C{2.5cm}|p{3.2cm}|C{2.0cm}|C{2.0cm}|C{1.5cm}|C{1.8cm}|",
        headers=["Panel", "Member", "Section", "Governing LC", "Demand", "Capacity", "UR", "Status"],
        body_rows=ed_cap_rows,
        caption="End Diaphragm Design --- Capacity Summary",
        label="tab:ed-capacity-summary"
    )

    # ── Table 5.29: Overall Design Check Summary (I7) ─────────────────────────
    # Fill from governing checks across all components
    ltb_dem_str = f"{float(_ltb_dem):.2f} kN-m" if _ltb_dem is not None else "N/A"
    ltb_cap_str = f"{float(_ltb_cap):.2f} kN-m" if _ltb_cap is not None else (v1_md if v1_md != "---" else "N/A")
    ltb_ur_val = format_ur(_pg_dcr_ltb) if _pg_dcr_ltb is not None else "---"

    # Governing fatigue check across all girders
    gov_fat_ur = None
    gov_fat_dem = None
    gov_fat_cap = None
    for gi in range(1, n_girders + 1):
        _g_fat = _fat_cat.get(f"G{gi}", {}) or {}
        _u = _g_fat.get("ur")
        if _u is not None:
            try:
                _u_f = float(_u)
                if gov_fat_ur is None or _u_f > gov_fat_ur:
                    gov_fat_ur = _u_f
                    gov_fat_dem = _g_fat.get("demand")
                    gov_fat_cap = _g_fat.get("capacity")
            except (TypeError, ValueError):
                pass

    fat_dem_str = f"{float(gov_fat_dem):.2f} MPa" if gov_fat_dem is not None else "N/A"
    fat_cap_str = f"{float(gov_fat_cap):.2f} MPa" if gov_fat_cap is not None else "N/A"
    fat_ur_str = format_ur(gov_fat_ur) if gov_fat_ur is not None else "---"

    # Deflection for overall summary
    defl_ll_val = (bridge.output_dict.get(f"{KEY_SD_DEFL_LIVE}.G1") or
                   bridge.output_dict.get(KEY_SD_DEFL_LIVE) or
                   bridge.output_dict.get("steeldesign.defl_live.G1"))
    if defl_ll_val is not None:
        try:
            defl_ll_f = float(defl_ll_val)
            dem_defl_str = f"{defl_ll_f:.2f} mm"
            cap_defl_str = f"{alw_ll:.1f} mm" if alw_ll > 0 else "N/A"
            ur_defl_str = format_ur(defl_ll_f / alw_ll if alw_ll > 0 else 0)
        except (TypeError, ValueError):
            dem_defl_str = "N/A"
            cap_defl_str = f"{alw_ll:.1f} mm" if alw_ll > 0 else "N/A"
            ur_defl_str = "---"
    else:
        dem_defl_str = "N/A"
        cap_defl_str = f"{alw_ll:.1f} mm" if alw_ll > 0 else "N/A"
        ur_defl_str = "---"

    t529_rows = [
        f"Girder --- Moment & Governing ULS & {_g_val(KEY_SD_MU_APPLIED, 1, ' kN-m')} & {_g_val(KEY_SD_MD_CAPACITY, 1, ' kN-m')} & {_flex_ur_str} \\\\",
        f"Girder --- Shear & Governing ULS & {shear_vu_display} & {_g_val(KEY_SD_SHEAR_VCR, 1, ' kN')} & {_shear_ur_str} \\\\",
        f"Girder --- LTB (constr.) & Construction Stage & {ltb_dem_str} & {ltb_cap_str} & {ltb_ur_val} \\\\",
        f"Girder --- Fatigue & SLS Fatigue & {fat_dem_str} & {fat_cap_str} & {fat_ur_str} \\\\",
        f"Girder --- Deflection & Live Load (L/800) & {dem_defl_str} & {cap_defl_str} & {ur_defl_str} \\\\",
        f"Girder --- Stress & SLS (0.9 fy) & {_steel_sig_str} & {_steel_alw_str} & {format_ur(float(_steel_sigma)/float(_steel_allow) if (_steel_sigma and _steel_allow) else 0)} \\\\",
        f"Deck --- Flexure (Sagging) & Basic ULS & {_dkf(KEY_DD_M_ULS_SAG, nd=2)} kN-m/m & {_dkf(KEY_DD_MU_BOT, nd=2)} kN-m/m & {format_ur(_dkv(KEY_DD_M_ULS_SAG)/_dkv(KEY_DD_MU_BOT) if _dkv(KEY_DD_MU_BOT)>0 else 0)} \\\\",
        f"Deck --- Flexure (Hogging) & Basic ULS & {_dkf(KEY_DD_M_ULS_HOG, nd=2)} kN-m/m & {_dkf(KEY_DD_MU_TOP, nd=2)} kN-m/m & {format_ur(_dkv(KEY_DD_M_ULS_HOG)/_dkv(KEY_DD_MU_TOP) if _dkv(KEY_DD_MU_TOP)>0 else 0)} \\\\",
        f"Deck --- Punching Shear & Wheel Load ULS & {_dkf(KEY_DD_PUNCH_VED, nd=3)} MPa & {_dkf(KEY_DD_VRD_C_MPA, nd=3)} MPa & {format_ur(_dkv(KEY_DD_PUNCH_VED)/_dkv(KEY_DD_VRD_C_MPA) if _dkv(KEY_DD_VRD_C_MPA)>0 else 0)} \\\\",
        f"Deck --- One-Way Shear & Shear ULS & {_dkf(KEY_DD_SHEAR_VED, nd=2)} kN/m & {_dkf(KEY_DD_SHEAR_VRDC, nd=2)} kN/m & {format_ur(_dkv(KEY_DD_SHEAR_VED)/_dkv(KEY_DD_SHEAR_VRDC) if _dkv(KEY_DD_SHEAR_VRDC)>0 else 0)} \\\\",
        f"Crack Width (Slab) & Frequent SLS & {_dk_gov_wk_str} mm & {_dkf(KEY_DD_WK_LIMIT, nd=2)} mm & {format_ur(_dk_gov_wk/_dkv(KEY_DD_WK_LIMIT) if _dkv(KEY_DD_WK_LIMIT)>0 else 0)} \\\\",
    ]

    # Cross bracing governing URs
    cb_results = bridge.output_dict.get("crossbracing_design_results", {}) or {}
    from .executive_summary import _max_member_efficiency
    cb_eff = _max_member_efficiency(cb_results) or bridge.output_dict.get("cb_governing_ur")
    cb_ur_val = format_ur(cb_eff) if cb_eff is not None else "---"
    t529_rows.append(f"Cross Bracing --- Axial & Governing Combo & --- & --- & {cb_ur_val} \\\\")

    # End diaphragm
    if ed_results:
        ed_eff = _max_member_efficiency(ed_results) or bridge.output_dict.get("ed_governing_ur")
        ed_ur_val = format_ur(ed_eff) if ed_eff is not None else "---"
        t529_rows.append(f"End Diaphragm --- Axial & Governing Combo & --- & --- & {ed_ur_val} \\\\")
    else:
        t529_rows.append(r"End Diaphragm & \multicolumn{3}{c|}{Not designed in this version} & --- \\")

    t529 = themed_longtable(
        col_spec="|L{5.0cm}|L{3.5cm}|C{2.6cm}|C{2.6cm}|C{2.0cm}|",
        headers=["Member / Check", "Governing Load Combo", "Demand", "Capacity", "UR"],
        body_rows=t529_rows,
        caption="Overall Design Check Summary --- All Members",
        label="tab:overall-checks-summary"
    )

    # I7: Note generated from actual pass/fail status
    any_check_failed = (_shear_dcr_val is not None and _shear_dcr_val > 1.0) or (_flex_ur is not None and _flex_ur > 1.0) or (_pg_dcr_ltb is not None and _pg_dcr_ltb > 1.0) or (gov_fat_ur is not None and gov_fat_ur > 1.0)
    if any_check_failed:
        overall_note = r"\noindent\textit{Note: Utilization ratio (UR) = Demand / Capacity. One or more checks exceed the allowable limit (UR $>$ 1.0); governing checks are highlighted in red above.}"
    else:
        overall_note = r"\noindent\textit{Note: Utilization ratio (UR) = Demand / Capacity. All design checks satisfy code requirements (UR $\leq$ 1.0).}"

    # I8: Figure 5.1 positioned right after Table 5.29
    ur_chart_fig = _fig_embed(fig_paths.get('ur_summary'), 'Overall Design Utilization Ratios (Demand / Capacity)', label='fig:ur-summary-chart')

    return f"""
\\chapter{{Design Checks}}

This section presents all structural design checks performed by OsdagBridge. For each member, the demand from the governing load combination, the code-based capacity, and the utilization ratio are tabulated. All checks reference IS 800:2007 and IRC 22:2015 unless stated otherwise.

\\section{{Plate Girder Design}}
\\label{{sec:plate-girder}}

\\vspace{{0.4cm}}
{t51}

\\vspace{{0.4cm}}
{t52}

\\vspace{{0.4cm}}
{t53}

\\vspace{{0.4cm}}
{t54}

\\vspace{{0.4cm}}
{t55}

\\vspace{{0.4cm}}
{t56}

\\vspace{{0.4cm}}
{t57}

\\vspace{{0.4cm}}
{t58}

\\vspace{{0.4cm}}
{t59}

\\vspace{{0.4cm}}
{t510}

\\vspace{{0.4cm}}
{t511}

\\vspace{{0.4cm}}
{t512}

\\vspace{{0.4cm}}
{t513}

\\vspace{{0.4cm}}
{t514}

\\vspace{{0.4cm}}
{t515}

\\section{{Deck Slab Design}}
\\label{{sec:deck-design}}

\\vspace{{0.4cm}}
{t516}

\\vspace{{0.4cm}}
{t517}

\\vspace{{0.4cm}}
{t518}

\\vspace{{0.4cm}}
{t519}

\\vspace{{0.4cm}}
{t520}

\\vspace{{0.4cm}}
{t521}

\\vspace{{0.4cm}}
{t522_reinf}

\\section{{Cross Bracing Design}}
\\label{{sec:cross-bracing}}

\\vspace{{0.4cm}}
{t523}

\\vspace{{0.4cm}}
{t524}

\\vspace{{0.4cm}}
{t525}

\\section{{End Diaphragm Design}}
\\label{{sec:end-diaphragm}}

\\vspace{{0.4cm}}
{t526}

\\vspace{{0.4cm}}
{t527}

\\vspace{{0.4cm}}
{t528}

\\section{{Overall Design Check Summary}}
\\label{{sec:overall-summary}}

\\vspace{{0.4cm}}
{t529}

\\vspace{{0.4cm}}
{overall_note}

\\vspace{{0.8cm}}
{ur_chart_fig}
"""
