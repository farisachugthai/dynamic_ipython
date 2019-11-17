"""Need to do redo :mod:`IPython.lib.clipboard` because it doesn't work.

`%paste` or `%cpaste` doesn't work on Termux and there's no built-in
customizability.

Let's re-implement it as an `abstract factory
<https://en.wikipedia.org/wiki/Abstract_factory_pattern>`_.

"""
import subprocess

from IPython.core.error import TryNext

try:
    import pyperclip
except ImportError:
    # from prompt_toolkit.contrib I think?
    pass

from default_profile.extensions import termux_clipboard


class ClipboardEmpty(ValueError):
    pass


def win32_clipboard_get():
    """Get the current clipboard's text on Windows.

    Admittedly difficult to explain why it's not listed in the dependencies
    though.

    Note
    ----
    Requires Mark Hammond's pywin32 extensions.
    """
    try:
        import win32clipboard
    except ImportError:
        raise TryNext(
            "Getting text from the clipboard requires the pywin32 "
            "extensions: http://sourceforge.net/projects/pywin32/"
        )
    win32clipboard.OpenClipboard()
    try:
        text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except (TypeError, win32clipboard.error):
        try:
            text = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
        except (TypeError, win32clipboard.error):
            raise ClipboardEmpty
    finally:
        win32clipboard.CloseClipboard()
    return text


def tkinter_clipboard_get():
    """Get the clipboard's text using Tkinter.

    This is the default on systems that are not Windows or OS X. It may
    interfere with other UI toolkits and should be replaced with an
    implementation that uses that toolkit.
    """
    try:
        from tkinter import Tk, TclError
    except ImportError:
        raise TryNext(
            "Getting text from the clipboard on this platform requires tkinter."
        )

    root = Tk()
    root.withdraw()
    try:
        text = root.clipboard_get()
    except TclError:
        raise ClipboardEmpty
    finally:
        root.destroy()
    return text
