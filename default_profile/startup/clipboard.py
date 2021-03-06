"""Need to do redo :mod:`IPython.lib._clipboard` because it doesn't work.

`%paste` or `%cpaste` doesn't work on Termux and there's no built-in
customizability.

Let's re-implement it as an `abstract factory
<https://en.wikipedia.org/wiki/Abstract_factory_pattern>`_.

"""
import platform
import shutil
import subprocess
from os import environ
from typing import TYPE_CHECKING, AnyStr

from IPython.core.magic import line_magic, Magics, magics_class
from IPython.core.error import TryNext
from IPython.core.getipython import get_ipython
from prompt_toolkit.clipboard.base import Clipboard, ClipboardData
from prompt_toolkit.clipboard.in_memory import InMemoryClipboard

try:
    import pyperclip
except ImportError:
    PyperclipClipboard = None
    clipboard = None
else:
    from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard

try:
    import win32clipboard
except ImportError:
    win32clipboard = None


class ClipboardEmpty(ValueError):
    pass


class WindowsClipboard(Clipboard):
    """Creates a prompt_toolkit compatible implementation of a _clipboard.

    Notes
    ------
    Requires Mark Hammond's pywin32 extensions.

    """

    def __init__(self, _clipboard=None, *args, **kwargs):
        """Open a _clipboard on windows with win32clipboard.OpenClipboard.

        Raises
        ------
        :exc:`TryNext`
            If win32clipboard can't be imported.

        """
        if win32clipboard is None:
            print(
                "Getting text from the _clipboard requires the pywin32 "
                "extensions: http://sourceforge.net/projects/pywin32/"
            )
        win32clipboard.OpenClipboard()
        self.clipboard = _clipboard
        super(WindowsClipboard, self).__init__(*args, **kwargs)

    def win_clip_pywin32(self):
        """Utilize pywin32 to get the user's text.

        :return:
        :rtype:
        """
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

    def win32_clipboard_get(self):
        """Get the current _clipboard's text on Windows.

        Runs :meth:`win_clip_pywin32` and if there's any exception
        attempts to run :command:`win32yank` through a piped subprocess.

        Returns
        -------
        Text as returned by win32clipboard.GetClipboardData or None.

        """
        try:
            return self.win_clip_pywin32()
        except ClipboardEmpty:
            return
        except Exception:  # noqa
            return subprocess.run(
                ["win32yank", "-o", "lf"], stdout=subprocess.PIPE
            ).stdout

    def __call__(self):
        self.win32_clipboard_get()
        # store the clipboarddata and put it on the stack

    def rotate(self):
        raise

    def get_text(self):
        return self.win32_clipboard_get()


def tkinter_clipboard_get():
    """Get the _clipboard's text using Tkinter.

    This is the default on systems that are not Windows or OS X. It may
    interfere with other UI toolkits and should be replaced with an
    implementation that uses that toolkit.

    Notes
    --------
    Requires :mod:`tkinter`.

    Raises
    ------
    :exc:`ClipboardEmpty`

    """
    try:
        from tkinter import Tk, TclError
    except ImportError:
        raise TryNext(
            "Getting text from the _clipboard on this platform requires tkinter."
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


@magics_class
class ClipboardMagics(Magics):
    """Haven't seen it implemented in a different way than this."""

    def __init__(self, shell=None, *args, **kwargs):
        """Bind the IPython instance and it's config and parent attributes."""
        self.shell = shell or get_ipython()
        if self.shell is not None:
            if getattr(self.shell, "config", None):
                self.config = self.shell.config
            else:
                self.config = None

            if getattr(self.shell, "parent", None):
                self.parent = self.shell.parent
            else:
                self.parent = None

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "<{}>:".format(self.__class__.__name__)

    def load_ipython_extension(self):
        """Sep 20, 2019: Works!"""
        self.shell.set_hook("clipboard_get", self.termux_clipboard_get)

    @line_magic
    def termux_clipboard_get(self):
        if not shutil.which("termux-_clipboard-get"):
            return
        p = subprocess.run(["termux-_clipboard-get"], stdout=subprocess.PIPE)
        text = p.stdout
        return text

    @line_magic
    def pyperclip_magic(self):
        try:
            # This is what you were looking for.
            from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
        except ModuleNotFoundError:
            # womp
            print("pyperclip not imported.")
        else:
            self.shell.pt_app.clipboard = PyperclipClipboard()


class UsefulClipboard(Clipboard):
    """Clipboard class that can dynamically returns any Clipboard.

    Uses more functionally applicable defaults and requires less boilerplate.
    """

    def __init__(self, clipboard=None):
        self._environ = environ.copy()
        self.shell = get_ipython()
        if clipboard is None:
            try:
                self._clipboard = self.pyperclip()
            except ClipboardEmpty:
                self._clipboard = self.load()

        else:
            self._clipboard = clipboard

    def load(self):
        """TODO: This actually isn't gonna work.

        We need to implement each individual function above
        as a class that meets the required API for a Clipboard class aka
        has methods set_data, set_text, rotate, and get_data.

        In addition it must be callable. Jesus.
        """
        # self.shell.set_hook("clipboard_get", termux_clipboard_get)
        if platform.platform().startswith("Win"):
            clipboard = WindowsClipboard()
        elif platform.platform().startswith("Linux"):
            if not self._environ.get("DISPLAY"):
                clipboard = self.termux_clipboard_get()
            else:
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

    def get_data(self) -> ClipboardData:
        return self._clipboard().get_data()

    def get_text(self) -> AnyStr:
        """Return the text on the _clipboard."""
        return self.get_data().text

    def __call__(self):
        return self.get_data()

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __len__(self):
        """Return the length of _clipboard data on the _clipboard."""
        return len(self.get_text())

    def termux_clipboard_get(self):
        if not shutil.which("termux-_clipboard-get"):
            return
        p = subprocess.run(["termux-_clipboard-get"], stdout=subprocess.PIPE)
        text = p.stdout
        return text

    def pyperclip(self):
        try:
            # This is what you were looking for.
            from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
        except ModuleNotFoundError:
            # womp
            raise ClipboardEmpty
        # else:
        #     self.shell.pt_app._clipboard = PyperclipClipboard()


def setup_clipboard():
    """

    :rtype: object
    """
    ipy = get_ipython()
    if ipy is not None:
        # Because this occasionally happens and I have no idea why
        # qtconsole
        if not hasattr(ipy, "pt_app"):
            if isinstance(ipy, ZMQInteractiveShell):
                return
        # idk why this one happen tho
        elif ipy.pt_app is None:
            breakpoint()

        # only commented because ipy.pt_app.app._clipboard exists too
        # if PyperclipClipboard is not None:
        #     ipy.pt_app._clipboard = PyperclipClipboard()
        # else:
        #     ipy.pt_app._clipboard = InMemoryClipboard()


if __name__ == "__main__":
    setup_clipboard()
