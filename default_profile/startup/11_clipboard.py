"""Need to do redo :mod:`IPython.lib.clipboard` because it doesn't work.

`%paste` or `%cpaste` doesn't work on Termux and there's no built-in
customizability.

Let's re-implement it as an `abstract factory
<https://en.wikipedia.org/wiki/Abstract_factory_pattern>`_.

"""
import platform
import subprocess

from IPython.core.error import TryNext
from IPython.core.getipython import get_ipython
from prompt_toolkit.clipboard.base import ClipboardData, Clipboard
from prompt_toolkit.clipboard.in_memory import InMemoryClipboard

try:
    import pyperclip
except ImportError:
    PyperclipClipboard = None
    clipboard = None
else:
    from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard

    # from pyperclip import determine_clipboard

    # copy, paste = determine_clipboard()


# TODO: this isn't used so commenting it out but it should be used
# try:
#     from default_profile.extensions import termux_clipboard
# except (ImportError, ModuleNotFoundError):
#     termux_clipboard = None


class ClipboardEmpty(ValueError):
    pass


def win_clip_pywin32():
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


def win32_clipboard_get():
    """Get the current clipboard's text on Windows.

    Returns
    -------
    todo

    Notes
    ------
    Requires Mark Hammond's pywin32 extensions.


    """
    try:
        return win_clip_pywin32()
    except Exception:  # noqa
        try:
            # or something
            return subprocess.run(
                ["win32yank", "-o", "lf"], stdout=subprocess.PIPE
            ).stdout
            # "-i", "crlf", 
        except subprocess.CalledProcessError:
            raise


def tkinter_clipboard_get():
    """Get the clipboard's text using Tkinter.

    This is the default on systems that are not Windows or OS X. It may
    interfere with other UI toolkits and should be replaced with an
    implementation that uses that toolkit.

    Requires
    --------
    :mod:`tkinter`

    Raises
    ------
    :exc:`ClipboardEmpty`

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


class UsefulClipboard(Clipboard):
    """Clipboard class that can dynamically returns any Clipboard.

    Uses more functionally applicable defaults and requires less boilerplate.
    """

    def __init__(self, clipboard=None):
        super().__init__()
        if clipboard is None:
            self.clipboard = self._clipboard
        else:
            self.clipboard = clipboard

    def _clipboard(self):
        """TODO: This actually isn't gonna work.

        We need to implement each individual function above
        as a class that meets the required API for a Clipboard class aka
        has methods set_data, set_text, rotate, and get_data.

        In addition it must be callable. Jesus.
        """
        if platform.platform().startswith("Win"):
            clipboard = win32_clipboard_get()
        elif platform.platform().startswith("Linux"):
            clipboard = tkinter_clipboard_get()
        else:
            clipboard = InMemoryClipboard()
        return clipboard

    def set_data(self, data):
        self._clipboard().set_data(data)

    def set_text(self, text):
        self._clipboard().set_text(text)

    def rotate(self):
        self._clipboard().rotate()

    def get_data(self):
        return self._clipboard().get_data()

    def __call__(self):
        return self.get_data()

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __len__(self):
        """The length of clipboard data on the clipboard."""
        return len(self.get_data())


if __name__ == "__main__":
    ipy = get_ipython()
    if ipy is not None:
        # Because this occasionally happens and I have no idea why
        if not hasattr(ipy, "pt_app"):
            breakpoint()
        elif ipy.pt_app is None:
            breakpoint()

        if PyperclipClipboard is not None:
            ipy.pt_app.clipboard = PyperclipClipboard()
        else:
            ipy.pt_app.clipboard = InMemoryClipboard()
