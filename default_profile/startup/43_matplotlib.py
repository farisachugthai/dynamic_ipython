"""Set up matplotlib.

INFO:matplotlib.font_manager:Could not open font file /system/fonts/NotoColorEmoji.ttf: In FT2Font: Could not set the fontsize (error code 0x17)
INFO:matplotlib.font_manager:generated new fontManager
"""
import sys


def set_mpl():
    global get_font, get_fontconfig_fonts
    from matplotlib.font_manager import get_font, get_fontconfig_fonts
    fonts = get_fontconfig_fonts()
    try:
        font = fonts.index('Roboto-Black.ttf')
    except (ValueError, IndexError):
        return
    if not font:
        pass  # todo
    else:
        return font


if __name__ == "__main__":
    try:
        import matplotlib as mpl
    except (ImportError, ModuleNotFoundError):
        pass
    else:
        import matplotlib.pyplot as mpl
        from matplotlib.font_manager import FontManager
        from matplotlib.font_manager import get_fontconfig_fonts

        fm = FontManager()
        roboto = set_mpl()
