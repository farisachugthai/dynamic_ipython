"""Set up matplotlib.

INFO:matplotlib.font_manager:Could not open font file /system/fonts/NotoColorEmoji.ttf: In FT2Font: Could not set the fontsize (error code 0x17)
INFO:matplotlib.font_manager:generated new fontManager
"""
import base64
import difflib
import logging
import locale
import sys
from io import BytesIO

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import set_loglevel, RcParams, rcdefaults
from matplotlib.figure import Figure
from matplotlib.font_manager import FontManager
from matplotlib.font_manager import get_fontconfig_fonts, get_font

# noinspection PyProtectedMember
from matplotlib.style.core import STYLE_BLACKLIST


def generate_figure(plot=None):
    """Generate a Figure optionally plotting values."""
    fig = Figure()
    ax = fig.subplots()
    if plot:
        ax.plot(*plot)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


def diff_rcparams(rcparam=None):
    differ = difflib.Differ()
    # TODO: Odd place to get all messed up in


def set_mpl():

    fonts = get_fontconfig_fonts()
    try:
        font = fonts.index("Roboto-Black.ttf")
    except (ValueError, IndexError):
        return
    if not font:
        pass  # todo
    else:
        return font


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")
    set_loglevel("info")
    fm = FontManager()
    roboto = set_mpl()
