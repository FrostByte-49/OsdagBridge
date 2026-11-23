# Chapter 6 – Drawings and Visualizations

from osdagbridge.core.reports.report_utils import _fig_embed, _fig_subfigure


def ch6_drawings(fig_paths):
    """
    Chapter 6 – Drawings and Visualizations.
    CAD-generated 3D and 2D engineering views rendered using pythonOCC.
    Uses \\FloatBarrier after each section to prevent figures drifting across headings.
    """
    sup3d = _fig_embed(fig_paths.get('final_geometry'), 'Overall 3D Bridge Superstructure', label='fig:bridge-3d')
    cs    = _fig_embed(fig_paths.get('cross_section'), 'Typical Cross Section', label='fig:cross-section')
    gtop  = _fig_embed(fig_paths.get('girder_top'), 'Top View', label='fig:top-view')

    g3d   = _fig_embed(fig_paths.get('girder_3d'), '3D View of Plate Girders', label='fig:girder-3d')
    gxsec = _fig_embed(fig_paths.get('section_preview'), 'Cross Section of Plate Girder', label='fig:girder-xsec')
    gside = _fig_embed(fig_paths.get('stiffener_preview'), 'Side View of Girder', label='fig:girder-side')

    cbdia = _fig_embed(fig_paths.get('cb_diagram'), 'Cross Bracing Layout', label='fig:cb-layout')

    # J2 / J3: Subfigures for Cross Bracing components
    cb_p1 = fig_paths.get('cb_bracing')
    cb_p2 = fig_paths.get('cb_top_chord')
    cb_p3 = fig_paths.get('cb_bottom_chord')

    cb_subfigs = [
        (cb_p1, 'Bracing Section', 0.31),
        (cb_p2, 'Top Chord', 0.31),
        (cb_p3, 'Bottom Chord', 0.31),
    ]
    cb_sections_block = _fig_subfigure(
        cb_subfigs,
        caption='Cross Bracing Component Sections',
        label='fig:cb-sections'
    )

    eddia = _fig_embed(fig_paths.get('ed_diagram'), 'End Diaphragm Layout', label='fig:ed-layout')

    # J2 / J3: Subfigures for End Diaphragm components
    ed_p1 = fig_paths.get('ed_bracing')
    ed_p2 = fig_paths.get('ed_top_chord')
    ed_p3 = fig_paths.get('ed_bottom_chord')

    ed_subfigs = [
        (ed_p1, 'Bracing Section', 0.31),
        (ed_p2, 'Top Chord', 0.31),
        (ed_p3, 'Bottom Chord', 0.31),
    ]
    ed_sections_block = _fig_subfigure(
        ed_subfigs,
        caption='End Diaphragm Component Sections',
        label='fig:ed-sections'
    )

    return f"""
\\chapter{{Drawings and Visualizations}}
\\label{{ch:drawings}}

This section presents CAD-generated views of the designed bridge and its components. All views are generated automatically by OsdagBridge using pythonOCC.

\\section{{Bridge Configuration and Layout}}
\\label{{sec:bridge-layout}}

{sup3d}

{cs}

{gtop}

\\FloatBarrier

\\section{{Plate Girder --- Detailed Views}}
\\label{{sec:girder-views}}

{g3d}

{gxsec}

{gside}

\\FloatBarrier

\\section{{Cross Bracing Detail}}
\\label{{sec:bracing-detail}}

{cbdia}

{cb_sections_block}

\\FloatBarrier

\\section{{End Diaphragm Detail}}
\\label{{sec:diaphragm-detail}}

{eddia}

{ed_sections_block}

\\FloatBarrier
"""
