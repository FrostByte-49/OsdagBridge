# =============================================================================
# OsdagBridge Report Generator - Plotting and Visualization Utilities
# Generates Demand/Capacity Utilization Ratio (UR) and Material Quantity Charts
# Colors sourced from styles.py — no hardcoded hex values here (C1/C2).
# =============================================================================

import os
import sys
import logging

logger = logging.getLogger(__name__)

# Ensure active conda environment site-packages are accessible when running under Python 3.12
if sys.version_info[:2] == (3, 12):
    _conda_sp = r"C:\Users\Pranav Khalate\miniconda3\envs\osdagbridge-env\Lib\site-packages"
    if os.path.isdir(_conda_sp) and _conda_sp not in sys.path:
        sys.path.insert(0, _conda_sp)

try:
    import matplotlib  # type: ignore
    matplotlib.use('Agg')  # Headless backend
    import matplotlib.pyplot as plt  # type: ignore
    import numpy as np  # type: ignore

    # Apply Osdag Theme styling to matplotlib
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['axes.edgecolor'] = '#CCCCCC'
    plt.rcParams['axes.linewidth'] = 0.8
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False
    plt = None
    np = None

# Import colors from styles.py — no hardcoded hex in this file (A7 / C1 / C2)
from osdagbridge.core.reports.styles import (
    MPL_COLOR_PRIMARY,
    MPL_COLOR_SECONDARY,
    MPL_COLOR_PASS,
    MPL_COLOR_FAIL,
    MPL_COLOR_THRESHOLD,
    MPL_COLOR_WARN,
    MPL_COLOR_HEADER_BG,
    MPL_COLOR_BORDER,
)


def generate_ur_summary_chart(ur_data, output_path):
    """
    Generate the Section 5.5 Utilization Ratio (Demand / Capacity) Summary Chart.

    Requirements:
    - Fixed 4 components in order: Girder, Deck Slab, Cross Bracing, End Diaphragm
    - VERTICAL bars (ax.bar, not barh)
    - Y-axis = Utilization Ratio
    - HORIZONTAL red dashed line at UR = 1.0
    - Color bands:
        * UR < 0.8         : Green (MPL_COLOR_PASS)
        * 0.8 <= UR <= 1.0 : Amber/Orange (MPL_COLOR_WARN)
        * UR > 1.0         : Red (MPL_COLOR_FAIL)
    - If a component has no data, omit its bar and label "(No result)"
    - Sourced from styles.py
    """
    if not _HAS_MPL:
        logger.error("matplotlib unavailable — UR chart cannot be generated.")
        return None

    components = ["Girder", "Deck Slab", "Cross Bracing", "End Diaphragm"]
    ur_dict = ur_data or {}

    # Extract values for the 4 components in fixed order
    comp_values = []
    has_any_data = False
    for comp in components:
        val = ur_dict.get(comp)
        if val is not None:
            try:
                f = float(val)
                comp_values.append(f)
                has_any_data = True
                continue
            except (TypeError, ValueError):
                pass
        comp_values.append(None)

    if not has_any_data:
        logger.warning("UR chart: no valid data across any of the 4 components — chart omitted.")
        return None

    try:
        fig, ax = plt.subplots(figsize=(6.5, 4.8), dpi=300)
        x_pos = np.arange(len(components))
        bar_width = 0.52

        valid_vals = [v for v in comp_values if v is not None]
        max_val = max(valid_vals) if valid_vals else 1.0
        y_max = max(max_val * 1.25, 1.35)

        for i, (comp, val) in enumerate(zip(components, comp_values)):
            if val is not None:
                if val > 1.0:
                    c = MPL_COLOR_FAIL
                elif val >= 0.8:
                    c = MPL_COLOR_WARN
                else:
                    c = MPL_COLOR_PASS

                bar = ax.bar(i, val, width=bar_width, color=c, edgecolor='none', zorder=3)
                ax.text(
                    i,
                    val + max_val * 0.025,
                    f"{val:.2f}",
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold',
                    color=c,
                )
            else:
                # Absent bar: indicate "(No result)"
                ax.text(
                    i,
                    0.05,
                    "(No result)",
                    ha='center', va='bottom', fontsize=8.5, fontstyle='italic',
                    color='#777777',
                )

        # Horizontal red dashed threshold line at UR = 1.0
        ax.axhline(1.0, color=MPL_COLOR_THRESHOLD, linestyle='--', linewidth=1.5,
                   zorder=4, label='Allowable Threshold (UR = 1.0)')

        ax.set_xticks(x_pos)
        ax.set_xticklabels(components, fontsize=9.5, fontweight='bold', ha='center')
        ax.set_ylabel("Utilization Ratio (UR = Demand / Capacity)", fontsize=10,
                      fontweight='bold', labelpad=8)
        ax.set_ylim(0, y_max)
        ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
        ax.legend(loc='upper right', frameon=True, facecolor='#FFFFFF',
                  edgecolor=MPL_COLOR_BORDER, fontsize=9)
        ax.set_title("Summary of Overall Design Utilization Ratios",
                     fontsize=11, fontweight='bold', pad=12, color=MPL_COLOR_PRIMARY)

        plt.tight_layout()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return output_path

    except Exception as exc:
        logger.error("UR chart generation failed: %s", exc, exc_info=True)
        if plt:
            try:
                plt.close('all')
            except Exception:
                pass
        return None


def generate_material_takeoff_charts(material_dict, steel_chart_path, concrete_chart_path):
    """
    Generate Chapter 7 Material Take-off Summary Charts.

    C2 requirements:
    - NO fallback constants (0.92, 0.45, 145.2, 18.5 — all deleted)
    - Steel: Girders / Cross Bracing / End Diaphragms from real data only; skip missing
    - Concrete (m³) and rebar (MT) as two subplots with own units
    - Larger figure size for readability
    - Colors from styles.py

    Returns
    -------
    (steel_chart_path, concrete_chart_path) — None for a chart if data is unavailable
    """
    if not _HAS_MPL:
        logger.error("matplotlib unavailable — material charts cannot be generated.")
        return None, None

    steel_path_out   = None
    concrete_path_out = None

    # ── 1. Structural Steel Breakdown ─────────────────────────────────────────
    try:
        steel_items, steel_values = [], []

        g_wt = _safe_float(material_dict.get("steel_girders_wt_total"))
        if g_wt is not None:
            steel_items.append("Girders")
            steel_values.append(g_wt)
        else:
            logger.warning("Material chart: steel_girders_wt_total missing — bar omitted.")

        # Cross bracing: try total first, then sum of components
        cb_wt = _safe_float(material_dict.get("bracing_wt_total"))
        if cb_wt is None or cb_wt <= 0.0:
            t = _safe_float(material_dict.get("bracing_top_wt_total"))  or 0.0
            b = _safe_float(material_dict.get("bracing_bot_wt_total"))  or 0.0
            d = _safe_float(material_dict.get("bracing_diag_wt_total")) or 0.0
            cb_wt = t + b + d if (t + b + d) > 0 else None
        if cb_wt is not None:
            steel_items.append("Cross Bracing")
            steel_values.append(cb_wt)
        else:
            logger.warning("Material chart: cross-bracing weight missing — bar omitted.")

        ed_wt = _safe_float(material_dict.get("diaphragm_wt_total"))
        if ed_wt is not None and ed_wt > 0:
            steel_items.append("End Diaphragms")
            steel_values.append(ed_wt)
        else:
            logger.warning("Material chart: diaphragm_wt_total missing — bar omitted.")

        if steel_items:
            fig, ax = plt.subplots(figsize=(max(5.5, len(steel_items) * 1.6), 4.2), dpi=300)
            bars = ax.bar(steel_items, steel_values, width=0.45,
                          color=MPL_COLOR_PRIMARY, zorder=3)
            _label_bars(ax, bars, steel_values, suffix=" MT")
            ax.set_ylabel("Weight (Metric Tonnes)", fontsize=9.5, fontweight='bold')
            ax.set_title("Structural Steel Breakdown (Tonnes)", fontsize=10.5,
                         fontweight='bold', pad=10, color=MPL_COLOR_PRIMARY)
            ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
            plt.tight_layout()
            os.makedirs(os.path.dirname(os.path.abspath(steel_chart_path)), exist_ok=True)
            plt.savefig(steel_chart_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            steel_path_out = steel_chart_path
        else:
            logger.warning("Material chart: no steel data — chart not generated.")

    except Exception as exc:
        logger.error("Steel material chart failed: %s", exc, exc_info=True)
        if plt:
            try:
                plt.close('all')
            except Exception:
                pass

    # ── 2. Concrete Volume + Reinforcement Steel (two subplots) ───────────────
    try:
        conc_vol = _safe_float(material_dict.get("concrete_deck_vol_total"))
        rebar_wt = _safe_float(material_dict.get("rebar_deck_wt_total"))

        has_conc  = conc_vol is not None and conc_vol > 0
        has_rebar = rebar_wt is not None and rebar_wt > 0

        if has_conc or has_rebar:
            fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.2), dpi=300)

            if has_conc:
                bar1 = axes[0].bar(["Deck Concrete"], [conc_vol], width=0.4,
                                   color=MPL_COLOR_SECONDARY, zorder=3)
                _label_bars(axes[0], bar1, [conc_vol], suffix=" m³")
                axes[0].set_ylabel("Volume (m³)", fontsize=9.5, fontweight='bold')
                axes[0].set_title("Concrete Volume", fontsize=10, fontweight='bold',
                                  color=MPL_COLOR_PRIMARY)
                axes[0].set_ylim(0, conc_vol * 1.22)
                axes[0].grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
            else:
                axes[0].text(0.5, 0.5, "No concrete data", transform=axes[0].transAxes,
                             ha='center', va='center', color='grey', fontsize=9)
                logger.warning("Material chart: concrete volume missing.")

            if has_rebar:
                bar2 = axes[1].bar(["Deck Rebar"], [rebar_wt], width=0.4,
                                   color=MPL_COLOR_FAIL, zorder=3)
                _label_bars(axes[1], bar2, [rebar_wt], suffix=" MT")
                axes[1].set_ylabel("Weight (Metric Tonnes)", fontsize=9.5, fontweight='bold')
                axes[1].set_title("Reinforcement Steel", fontsize=10, fontweight='bold',
                                  color=MPL_COLOR_PRIMARY)
                axes[1].set_ylim(0, rebar_wt * 1.22)
                axes[1].grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
            else:
                axes[1].text(0.5, 0.5, "No rebar data", transform=axes[1].transAxes,
                             ha='center', va='center', color='grey', fontsize=9)
                logger.warning("Material chart: rebar weight missing.")

            plt.tight_layout()
            os.makedirs(os.path.dirname(os.path.abspath(concrete_chart_path)), exist_ok=True)
            plt.savefig(concrete_chart_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            concrete_path_out = concrete_chart_path
        else:
            logger.warning("Material chart: no concrete/rebar data — chart not generated.")

    except Exception as exc:
        logger.error("Concrete/rebar chart failed: %s", exc, exc_info=True)
        if plt:
            try:
                plt.close('all')
            except Exception:
                pass

    return steel_path_out, concrete_path_out


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _safe_float(val):
    """Return float or None — never raises."""
    try:
        f = float(val)
        return f if f == f else None  # reject NaN
    except (TypeError, ValueError):
        return None


def _label_bars(ax, bars, values, suffix=""):
    """Add value labels above each bar."""
    max_v = max(values) if values else 1.0
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + max_v * 0.02,
            f"{val:.2f}{suffix}",
            ha='center', va='bottom', fontsize=9, fontweight='bold',
        )
