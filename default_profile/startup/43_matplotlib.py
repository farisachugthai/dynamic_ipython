"""Set up matplotlib.

INFO:matplotlib.font_manager:Could not open font file /system/fonts/NotoColorEmoji.ttf: In FT2Font: Could not set the fontsize (error code 0x17)
INFO:matplotlib.font_manager:generated new fontManager
"""
import sys


def set_mpl():
    # TODO
    pass


if __name__ == "__main__":
    try:
        import matplotlib as mpl
    except (ImportError, ModuleNotFoundError):
        pass
    else:
        import matplotlib.pyplot as mpl
        from matplotlib.font_manager import FontManager

        fm = FontManager()
        set_mpl()
