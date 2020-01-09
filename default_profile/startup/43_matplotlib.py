"""Set up matplotlib.

INFO:matplotlib.font_manager:Could not open font file /system/fonts/NotoColorEmoji.ttf: In FT2Font: Could not set the fontsize (error code 0x17)
INFO:matplotlib.font_manager:generated new fontManager
"""
import difflib
import logging
import locale
import sys


def diff_rcparams(rcparam=None):
    differ = difflib.Differ()
    # TODO: Odd place to get all messed up in


def set_mpl():
    global get_font, get_fontconfig_fonts
    from matplotlib.font_manager import get_font, get_fontconfig_fonts

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
    locale.setlocale(locale.LC_ALL, '')

    try:
        import matplotlib as mpl
    except (ImportError, ModuleNotFoundError):
        pass
    else:
        import matplotlib.pyplot as plt
        from matplotlib.font_manager import FontManager
        from matplotlib.font_manager import get_fontconfig_fonts
        from matplotlib import set_loglevel, RcParams, rcdefaults

        from matplotlib.style.core import STYLE_BLACKLIST
        set_loglevel("info")

        fm = FontManager()
        roboto = set_mpl()
