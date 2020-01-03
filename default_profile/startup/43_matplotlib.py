"""Set up matplotlib.

INFO:matplotlib.font_manager:Could not open font file /system/fonts/NotoColorEmoji.ttf: In FT2Font: Could not set the fontsize (error code 0x17)
INFO:matplotlib.font_manager:generated new fontManager
"""
import sys


def get_mpl_font(font='Roboto-Black.ttf'):
    if font in get_fontconfig_fonts():
        return True


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
        if get_mpl_font():
            font = 'Roboto-Black'  # todo this is not well done
        get_mpl_font()
