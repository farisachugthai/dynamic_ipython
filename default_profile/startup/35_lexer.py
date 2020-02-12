#!/usr/bin/env python
# -*- coding: utf-8 -*-
from traitlets.config import LoggingConfigurable
from traitlets.traitlets import Instance
from pygments.lexer import Lexer
from pygments.lexers.python import PythonLexer

from pygments.formatters.terminal256 import TerminalTrueColorFormatter

from prompt_toolkit.lexers.pygments import PygmentsLexer
from prompt_toolkit.lexers.base import DynamicLexer, SimpleLexer

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShellABC
from IPython.lib.lexers import IPyLexer, IPythonTracebackLexer


def get_lexer():
    _ = PygmentsLexer(PythonLexer)
    return _


class IPythonConfigurableLexer(LoggingConfigurable):
    shell = Instance(InteractiveShellABC, allow_none=True)

    lexer = Instance(Lexer, help="Instance that lexs documents.", allow_none=True).tag(
        config=True
    )

    # from pygments.lexer.Lexer
    #: Name of the lexer
    name = None

    #: Shortcuts for the lexer
    aliases = []

    #: File name globs
    filenames = []

    #: Secondary file name globs
    alias_filenames = []

    #: MIME types
    mimetypes = []

    #: Priority, should multiple lexers match and no content is provided
    priority = 0

    def __init__(self, shell=None, original_lexer=None, **kwargs):
        super().__init__(**kwargs)
        self.shell = shell
        if self.shell is None:
            self.shell = get_ipython()

        if self.shell is not None:
            self.original_lexer = self.shell.pt_app.lexer
            self.shell.configurables.append("DynamicAliasManager")
        else:
            self.original_lexer = None


class Colorizer:
    """Make the pygments function 'highlight' even easier to work with.

    Additionally utilize ``__slots__`` to conserve memory.
    """

    __slots__ = {
            # The original docstring for pylexer was raising an error in sphinx...
        "pylexer": "A PythonLexer from Pygments",
        "formatter": TerminalTrueColorFormatter.__doc__,
        # 'highlight': pygments.highlight.__doc__
    }

    def __init__(self, pylexer=None, formatter=None):
        if pylexer is None:
            self.pylexer = PythonLexer()
        if formatter is None:
            self.formatter = TerminalTrueColorFormatter()

    def __call__(self, code):
        return self.highlight(code)

    def highlight(self, code):
        return pygments.highlight(code, self.pylexer, self.formatter)

    def __repr__(self):
        return f"{self.__class__.__name__}"


if __name__ == "__main__":
    lexer = IPythonConfigurableLexer()
    # TODO: isn't there a method like _ip.add_trait or something?
    colorizer = Colorizer()
    pt_lexer = get_lexer()
