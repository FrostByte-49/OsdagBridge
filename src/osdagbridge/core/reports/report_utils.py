from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS
)
from osdagbridge.core.reports.styles import FIG_PLACEMENT, FIG_DEFAULT_WIDTH, FIG_MAX_HEIGHT


def _tex(value):
    """
    Escape a Python value for safe LaTeX embedding.

    Handles Unicode mathematical symbols (≤, ≥, ±, ≠, °, −) and comparison
    operators (> and <) safely without double escaping or text-mode corruption.
    """
    s = str(value) if value is not None else ''
    if not s:
        return r''

    # Normalise non-ASCII glyphs from section designations
    for uni, ascii_ in [('∠', 'L'), ('ⅹ', 'x'), ('×', 'x'), ('−', '-')]:
        s = s.replace(uni, ascii_)

    # Protect math symbols with unique placeholders so subsequent LaTeX escaping
    # does not destroy their backslashes or math delimiters. Use alphanumeric placeholders
    # without underscores or special chars.
    math_tokens = {
        '≤': r'$\leq$',
        '≥': r'$\geq$',
        '±': r'$\pm$',
        '≠': r'$\neq$',
        '°': r'$^\circ$',
        '>': r'$>$',
        '<': r'$<$',
    }
    placeholders = {}
    for idx, (sym, tex_math) in enumerate(math_tokens.items()):
        if sym in s:
            ph = f"XXOSDAGMATH{idx}XX"
            placeholders[ph] = tex_math
            s = s.replace(sym, ph)

    # 1. Backslash must be escaped first
    s = s.replace('\\', r'\textbackslash{}')

    # 2. Special characters (excluding backslash — already done)
    for ch, esc in [
        ('&',  r'\&'),
        ('%',  r'\%'),
        ('$',  r'\$'),
        ('#',  r'\#'),
        ('{',  r'\{'),
        ('}',  r'\}'),
        ('_',  r'\_\allowbreak{}'),
        ('~',  r'\textasciitilde{}'),
        ('^',  r'\^{}'),
    ]:
        s = s.replace(ch, esc)

    s = s.replace(':', r':\allowbreak{}')

    # 3. Restore protected math tokens
    for ph, tex_math in placeholders.items():
        s = s.replace(ph, tex_math)

    return s


def _tex_loadcase(value):
    """
    Like _tex() but replaces underscores with spaces first so load-case labels
    like 'ACCIDENTAL_1' render as 'ACCIDENTAL 1' instead of 'ACCIDENTAL\\_\\allowbreak{}1'.
    """
    s = str(value) if value is not None else ''
    s = s.replace('_', ' ')
    return _tex(s)


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    return _tex(val) + unit


def get_girder_entries(input_dict):
    """
    Retrieve all girder labels and member IDs from backend keys.

    Returns:
        List[Tuple[str, str]] — (girder_label, member_id)
    """
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))
    entries = []
    for i in range(1, n + 1):
        entries.append((
            input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", f"G{i}"),
            input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", f"G{i}M1"),
        ))
    return entries


# ---------------------------------------------------------------------------
# Figure helpers (F1/F6)
# ---------------------------------------------------------------------------

def _fig_or_placeholder(path, caption, width=None, label=""):
    """
    Embed a figure with a real \\caption{} (not \\caption*) and [!htbp] placement.
    When path is falsy or file missing: omit the figure entirely and log a warning
    (no visible PLACEHOLDER box in PDF output — per F2).

    caption: plain text — do NOT prefix 'Figure X:' (captionsetup handles numbering).
    """
    import logging, os
    logger = logging.getLogger(__name__)
    w = width or FIG_DEFAULT_WIDTH
    if path:
        p = str(path).replace('\\', '/')
        if not os.path.isfile(path):
            logger.warning("Figure file not found, omitting: %s", path)
            return f"% Figure omitted — file not found: {p}\n"
        label_tex = (r"\label{" + label + r"}") if label else ""
        return (
            r"\begin{figure}[" + FIG_PLACEMENT + r"]" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[width=" + w + r",height=" + FIG_MAX_HEIGHT + r",keepaspectratio]{" + p + r"}" + "\n"
            r"\caption{" + caption + r"}" + label_tex + "\n"
            r"\end{figure}"
        )
    logger.warning("Figure path not provided, omitting figure: %s", caption)
    return f"% Figure omitted — no path provided: {caption}\n"


def _fig_embed(path, caption, width=None, height=None, label=""):
    """
    Embed a real figure with [!htbp] and a real \\caption{}.
    Falls back to omitting (logging) rather than showing PLACEHOLDER box.
    """
    import logging, os
    logger = logging.getLogger(__name__)
    w = width or FIG_DEFAULT_WIDTH
    if path:
        p = str(path).replace('\\', '/')
        if not os.path.isfile(path):
            logger.warning("Figure file not found, omitting: %s", path)
            return f"% Figure omitted — file not found: {p}\n"
        opts = f"width={w}"
        if height:
            opts += f",height={height},keepaspectratio"
        else:
            opts += r",height=" + FIG_MAX_HEIGHT + r",keepaspectratio"
        label_tex = (r"\label{" + label + r"}") if label else ""
        return (
            r"\begin{figure}[" + FIG_PLACEMENT + r"]" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[" + opts + r"]{" + p + r"}" + "\n"
            r"\caption{" + caption + r"}" + label_tex + "\n"
            r"\end{figure}"
        )
    logger.warning("Figure path not provided, omitting: %s", caption)
    return f"% Figure omitted — no path provided: {caption}\n"


def _fig_subfigure(subfigs, caption, label=""):
    """
    Build a figure environment with subfigures for side-by-side panels.

    subfigs: list of (path, subcaption, width_frac) tuples
             width_frac: fraction of \\linewidth, e.g. 0.48
    caption: overall figure caption (plain text)
    """
    import logging, os
    logger = logging.getLogger(__name__)
    lines = [r"\begin{figure}[" + FIG_PLACEMENT + r"]", r"\centering"]
    any_valid = False
    for path, subcap, frac in subfigs:
        if not path or not os.path.isfile(str(path)):
            logger.warning("Subfigure omitted — file not found: %s", path)
            continue
        any_valid = True
        p = str(path).replace('\\', '/')
        w = f"{frac:.2f}\\linewidth"
        lines.append(r"\begin{subfigure}[b]{" + w + r"}")
        lines.append(r"  \centering")
        lines.append(r"  \includegraphics[width=\linewidth,keepaspectratio]{" + p + r"}")
        lines.append(r"  \caption{" + subcap + r"}")
        lines.append(r"\end{subfigure}")
    if not any_valid:
        logger.warning("All subfigures missing for: %s", caption)
        return f"% Figure omitted — no subfigures available: {caption}\n"
    label_tex = (r"\label{" + label + r"}") if label else ""
    lines.append(r"\caption{" + caption + r"}" + label_tex)
    lines.append(r"\end{figure}")
    return "\n".join(lines)
