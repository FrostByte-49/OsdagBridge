# =============================================================================
# Chapter 3: Loads and Load Combinations
# Formatted using themed_longtable and centralized styling
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)
from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import themed_longtable
from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017


def _is_true(val):
    if val is None:
        return False
    s = str(val).strip().lower()
    return s in ("true", "1", "yes")


def ch3_loads(input_dict):
    # ── Table 3.1: Dead Load — Self Weight ────────────────────────────────────
    # E7: Density: 78.5 kN/m3 (steel), 25.0 kN/m3 (concrete) per IRC 6 Cl. 203
    steel_density = input_dict.get(KEY_MATERIAL_GIRDER_DENSITY) or "78.5"
    conc_density  = input_dict.get(KEY_MATERIAL_DECK_DENSITY) or "25.0"
    sw_factor     = input_dict.get(KEY_PL_SELF_WEIGHT_FACTOR) or "1.0"

    t31_rows = [
        f"\\textnormal{{Structural Steel Density}} & {_tex(str(steel_density))} kN/m$^3$ \\\\",
        f"\\textnormal{{Reinforced Concrete Density}} & {_tex(str(conc_density))} kN/m$^3$ \\\\",
        f"\\textnormal{{Self-Weight Multiplier}} & {_tex(str(sw_factor))} \\\\",
    ]
    t31 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Design Value"],
        body_rows=t31_rows,
        caption="Dead Load --- Self Weight",
        label="tab:dead-load-selfweight",
    )

    # ── Table 3.2: Surfacing & SIDL (DW) ──────────────────────────────────────
    wc_mat = input_dict.get(KEY_WC_MATERIAL, "Bituminous")
    try:
        wc_thk_mm = float(input_dict.get(KEY_WC_THICKNESS, 50.0) or 50.0)
    except Exception:
        wc_thk_mm = 50.0
    wc_density = 24.0 if "bitum" in str(wc_mat).lower() else 25.0
    wc_load_val = (wc_thk_mm / 1000.0) * wc_density
    wc_load_str = f"{wc_load_val:.2f} kN/m$^2$ ({wc_mat}, {wc_thk_mm:.0f} mm)"

    cb_load = input_dict.get(KEY_CB_LOAD)
    cb_load_str = f"{cb_load} kN/m per barrier" if cb_load not in (None, "") else "---"

    rl_load = input_dict.get(KEY_RL_LOAD_VALUE)
    rl_load_str = f"{rl_load} kN/m\\sdstar{{}}" if rl_load not in (None, "") else "---"

    t32_rows = [
        r"\textnormal{Wearing Course Load} & " + wc_load_str + r" \\",
        r"\textnormal{Crash Barrier SIDL} & " + _tex(cb_load_str) + r" \\",
        r"\textnormal{Railing Load} & " + rl_load_str + r" \\",
    ]
    t32 = themed_longtable(
        col_spec="|L{5.5cm}|L{9.5cm}|",
        headers=["Parameter", "Design Value"],
        body_rows=t32_rows,
        caption="Dead Load for Surfacing and SIDL (DW)",
        label="tab:sidl-loads",
    )

    # ── Table 3.3: Vehicle Live Loads (E1) ────────────────────────────────────
    # Columns: Vehicle Class | Description | Load | Unit | Axles/Tracks
    veh_defs = [
        (KEY_LL_IRC_CLASS_A,      "IRC Class A",           "Wheeled Vehicle Train", "554",  "kN", "8 axles"),
        (KEY_LL_IRC_70R_WHEELED,  "IRC Class 70R (Wheel)", "Heavy Wheeled Vehicle", "1000", "kN", "7 axles"),
        (KEY_LL_IRC_70R_TRACKED,  "IRC Class 70R (Track)", "Tracked Heavy Vehicle", "700",  "kN", "2 tracks"),
        (KEY_LL_IRC_AA_WHEELED,   "IRC Class AA (Wheel)",  "Heavy Wheeled Loading", "400",  "kN", "2 axles"),
        (KEY_LL_IRC_AA_TRACKED,   "IRC Class AA (Track)",  "Tracked Heavy Vehicle", "700",  "kN", "2 tracks"),
        (KEY_LL_IRC_CLASS_SV,     "IRC Class SV",          "Special Vehicle",       "3850", "kN", "Trailer"),
        (KEY_LL_IRC_70R_BOGIE,    "IRC Class 70R (Bogie)", "Bogie Axle Loading",   "400",  "kN", "2 axles"),
        (KEY_LL_IRC_CLASS_FATIGUE,"IRC Class Fatigue",     "Fatigue Vehicle",       "IRC 6", "Annex C", "Standard truck"),
    ]
    veh_rows = []
    for k, name, desc, load_val, unit, axles in veh_defs:
        if _is_true(input_dict.get(k)):
            veh_rows.append(
                f"{_tex(name)} & {_tex(desc)} & {_tex(load_val)} & {_tex(unit)} & {_tex(axles)} \\\\"
            )

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            cname = c.get('name') if isinstance(c, dict) else str(c)
            cload = str(c.get('load', '---')) if isinstance(c, dict) else '---'
            cax = str(c.get('axles', '---')) if isinstance(c, dict) else '---'
            if cname:
                veh_rows.append(
                    f"{_tex(cname)} & Custom Vehicle & {_tex(cload)} & kN & {_tex(cax)} \\\\"
                )

    if not veh_rows:
        veh_rows.append(r"No vehicle selected & --- & --- & --- & --- \\")

    t33 = themed_longtable(
        col_spec="|L{3.5cm}|L{4.2cm}|C{2.0cm}|C{1.8cm}|C{2.5cm}|",
        headers=["Vehicle Class", "Description", "Load", "Unit", "Axles/Tracks"],
        body_rows=veh_rows,
        caption="Vehicle Live Loads",
        label="tab:vehicle-live-loads",
    )

    # ── Table 3.4: Live Load Dynamic & Longitudinal Effects (E2) ──────────────
    span = input_dict.get(KEY_SPAN)
    span_m = float(span) if span not in (None, "") else 0.0

    impact_a_str = "---"
    impact_aa_str = "---"
    if span_m > 0:
        try:
            im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
            impact_a_str = f"{1.0 + im_a:.3f}"
        except Exception:
            impact_a_str = "---"
        try:
            im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
            impact_aa_str = f"{1.0 + im_aa:.3f}"
        except Exception:
            impact_aa_str = "---"

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    braking_force_str = "---"
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
            braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
            braking_force_kN = braking_force_t * 9.81
            braking_force_str = f"{braking_force_kN:.2f}"
        except Exception:
            braking_force_str = "---"

    t34_rows = [
        f"\\textnormal{{Impact Factor --- Class A}} & {impact_a_str} & --- & IRC 6 Cl. 208.2 \\\\",
        f"\\textnormal{{Impact Factor --- Class AA / 70R}} & {impact_aa_str} & --- & IRC 6 Cl. 208.3 \\\\",
        f"\\textnormal{{Braking Force}} & {braking_force_str} & kN & IRC 6 Cl. 211 \\\\",
        r"\textnormal{Centrifugal Force} & Not applicable (straight bridge) & --- & IRC 6 Cl. 212 \\",
    ]
    t34 = themed_longtable(
        col_spec="|L{5.0cm}|C{3.0cm}|C{2.0cm}|L{4.2cm}|",
        headers=["Parameter", "Value", "Unit", "Reference"],
        body_rows=t34_rows,
        caption="Live Load Dynamic and Longitudinal Effects",
        label="tab:live-load-effects",
    )

    # ── Table 3.5: Footpath Live Load (E3) ────────────────────────────────────
    has_fp = (
        str(input_dict.get('basic_inputs.bridge_geometry.footpath', '')).strip().lower() in ('yes', 'true', '1') or
        float(input_dict.get('typical_section.footpath_width', 0) or 0) > 0 or
        str(input_dict.get(KEY_FOOTPATH, '')).strip().lower() in ('yes', 'true', '1')
    )
    fp_mode  = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")

    if not has_fp:
        t35_rows = [r"\textnormal{Footpath Live Load Intensity} & Not applicable (no footpath) & --- & --- \\"]
    else:
        if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
            try:
                fp_intensity = f"{IRC6_2017.cl_206_1_footway_load(span_m):.3f}"
            except Exception:
                fp_intensity = "4.905"
            ref_str = "IRC 6 Cl. 206.1"
        elif fp_value not in (None, ""):
            fp_intensity = f"{float(fp_value):.3f}"
            ref_str = "User Defined"
        else:
            try:
                fp_intensity = f"{IRC6_2017.cl_206_1_footway_load(span_m):.3f}"
            except Exception:
                fp_intensity = "4.905"
            ref_str = "IRC 6 Cl. 206.1"
        t35_rows = [f"\\textnormal{{Footpath Live Load Intensity}} & {fp_intensity} & kN/m$^2$ & {ref_str} \\\\"]

    t35 = themed_longtable(
        col_spec="|L{5.0cm}|C{3.0cm}|C{2.0cm}|L{4.2cm}|",
        headers=["Parameter", "Value", "Unit", "Reference"],
        body_rows=t35_rows,
        caption="Footpath Live Load",
        label="tab:footpath-live-load",
    )

    # ── Table 3.6: Wind Load (WL) (E4) ────────────────────────────────────────
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT) or 10.0
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            if _vb:
                _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
                if not vz_val:
                    vz_val = _res.get("Vz")
                if not pz_val:
                    pz_val = _res.get("Pz")
        except Exception:
            pass

    vz_str = f"{float(vz_val):.2f}" if vz_val not in (None, "") else "---"
    pz_str = f"{float(pz_val):.2f}" if pz_val not in (None, "") else "---"

    ft_val = input_dict.get(KEY_WL_TRANSVERSE_WIND_FORCE)
    fl_val = input_dict.get(KEY_WL_LONGITUDINAL_WIND_FORCE)
    fv_val = input_dict.get(KEY_WL_VERTICAL_WIND_FORCE)

    ft_str = f"{float(ft_val):.2f}" if ft_val not in (None, "") else "---"
    fl_str = f"{float(fl_val):.2f}" if fl_val not in (None, "") else "---"
    fv_str = f"{float(fv_val):.2f}" if fv_val not in (None, "") else "---"

    vb_val = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
    vb_str = f"{float(vb_val):.1f}" if vb_val not in (None, "") else "---"
    h_val  = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT) or "---"
    ter_val = input_dict.get(KEY_WL_TERRAIN_TYPE) or "Plain Terrain"

    t36_rows = [
        f"\\textnormal{{Basic Wind Speed, $V_b$}} & {vb_str} & m/s & Project Location \\\\",
        f"\\textnormal{{Terrain Category}} & {_tex(str(ter_val))} & --- & IRC 6 Cl. 209.2 \\\\",
        f"\\textnormal{{Average Exposed Height, $H$}} & {_tex(str(h_val))} & m & Superstructure \\\\",
        f"\\textnormal{{Hourly Mean Wind Speed, $V_z$}} & {vz_str} & m/s & IRC 6 Table 12 \\\\",
        f"\\textnormal{{Hourly Wind Pressure, $P_z$}} & {pz_str} & N/m$^2$ & IRC 6 Table 12 \\\\",
        f"\\textnormal{{Transverse Wind Force, $F_T$}} & {ft_str} & kN & IRC 6 Cl. 209.3.3 \\\\",
        f"\\textnormal{{Longitudinal Wind Force, $F_L$}} & {fl_str} & kN & IRC 6 Cl. 209.3.4 \\\\",
        f"\\textnormal{{Vertical Wind Force, $F_V$}} & {fv_str} & kN & IRC 6 Cl. 209.3.5 \\\\",
    ]
    t36 = themed_longtable(
        col_spec="|L{5.5cm}|C{3.0cm}|C{2.0cm}|L{4.2cm}|",
        headers=["Parameter", "Value", "Unit", "Reference"],
        body_rows=t36_rows,
        caption="Wind Load (WL) Parameters and Forces (IRC 6)",
        label="tab:wind-loads",
    )

    # ── Table 3.7: Seismic Load (EL) (E4) ─────────────────────────────────────
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _fmt_dec(v, nd=4):
        try:
            return f"{float(v):.{nd}f}"
        except (TypeError, ValueError):
            return "---"

    t37_rows = [
        f"\\textnormal{{Seismic Zone}} & {_render_value(input_dict, 'seismic_zone')} & --- & IRC 6 Annex E \\\\",
        f"\\textnormal{{Zone Factor, $Z$}} & {_fmt_dec(sl_zone_factor, 2)} & --- & IRC 6 Cl. 218.4 \\\\",
        f"\\textnormal{{Importance Factor, $I$}} & {_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)} & --- & IRC 6 Cl. 218.5.2 \\\\",
        f"\\textnormal{{Soil Type}} & {_render_value(input_dict, KEY_SL_SOIL_TYPE)} & --- & IRC 6 Cl. 218.5.1 \\\\",
        f"\\textnormal{{Response Acceleration, $S_a/g$}} & {_fmt_dec(sl_spectral, 3)} & --- & IRC 6 Fig. 19 \\\\",
        f"\\textnormal{{Horizontal Coeff., $A_h$}} & {_fmt_dec(sl_ah, 4)} & --- & IRC 6 Cl. 218.5 \\\\",
        f"\\textnormal{{Vertical Coeff., $A_v$}} & {_fmt_dec(sl_av, 4)} & --- & IRC 6 Cl. 218.6 \\\\",
    ]
    t37 = themed_longtable(
        col_spec="|L{5.5cm}|C{3.0cm}|C{2.0cm}|L{4.2cm}|",
        headers=["Parameter", "Value", "Unit", "Reference"],
        body_rows=t37_rows,
        caption="Earthquake Load (EL) Parameters (IRC 6)",
        label="tab:seismic-loads",
    )

    # ── Table 3.8: Temperature Load (TL) (E5: sign at source) ─────────────────
    tl_temp_min = input_dict.get(KEY_TL_BRIDGE_TEMP_MIN) or "---"
    tl_temp_max = input_dict.get(KEY_TL_BRIDGE_TEMP_MAX) or "---"
    tl_rise_val = input_dict.get(KEY_TL_TEMP_RISE)
    tl_fall_val = input_dict.get(KEY_TL_TEMP_FALL)

    try:
        rise_f = float(tl_rise_val)
        rise_str = f"{rise_f:+.2f}"
    except (TypeError, ValueError):
        rise_str = "---"

    try:
        fall_f = float(tl_fall_val)
        fall_str = f"-{abs(fall_f):.2f}"
    except (TypeError, ValueError):
        fall_str = "---"

    t38_rows = [
        f"\\textnormal{{Maximum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_max')} & $^\\circ$C & Project Location \\\\",
        f"\\textnormal{{Minimum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_min')} & $^\\circ$C & Project Location \\\\",
        f"\\textnormal{{Effective Bridge Temp. Range}} & {_tex(str(tl_temp_min))} to {_tex(str(tl_temp_max))} & $^\\circ$C & IRC 6 Cl. 215.2 \\\\",
        f"\\textnormal{{Design Temp. Rise / Fall}} & {rise_str} / {fall_str} & $^\\circ$C & IRC 6 Cl. 215.3 \\\\",
    ]
    t38 = themed_longtable(
        col_spec="|L{5.5cm}|C{3.0cm}|C{2.0cm}|L{4.2cm}|",
        headers=["Parameter", "Value", "Unit", "Reference"],
        body_rows=t38_rows,
        caption="Temperature Load (TL) Parameters (IRC 6)",
        label="tab:temperature-loads",
    )

    # ── Table 3.9: Load Combinations (E5: header/endhead structure) ───────────
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"ULS-{i:02d} & {_tex(cases)} \\\\")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"SLS-{i:02d} & {_tex(cases)} \\\\")

    t39 = themed_longtable(
        col_spec="|C{3.0cm}|p{12.0cm}|",
        headers=["Combination ID", "Load Cases and Factors"],
        body_rows=lc_rows,
        caption="Design Load Combinations (IRC 6)",
        label="tab:load-combinations",
    )

    return f"""
\\chapter{{Loads and Load Combinations}}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\\vspace{{0.4cm}}
{t31}

\\vspace{{0.4cm}}
{t32}

\\vspace{{0.4cm}}
{t33}

\\vspace{{0.4cm}}
{t34}

\\vspace{{0.4cm}}
{t35}

\\vspace{{0.4cm}}
{t36}

\\vspace{{0.4cm}}
{t37}

\\vspace{{0.4cm}}
{t38}

\\vspace{{0.4cm}}
{t39}

\\noindent\\textit{{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}}
"""
