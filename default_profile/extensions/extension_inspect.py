#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Few more things we might wanna work out here.

Our lack of the module :mod:`inspect` is pretty surprising.

Refer to either `IPython.core.oinspect` or `xonsh.inspectors`
for some good uses of the std lib module.

"""
from pprint import pformat

from pygments import highlight
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

try:
    from gruvbox.gruvbox import GruvboxStyle
except ImportError:
    GruvboxStyle = None
    from pygments.styles.inkpot import InkPotStyle

from IPython.core.getipython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.lib.lexers import IPyLexer
from IPython.lib.pretty import pprint


@magics_class
class PrettyColorfulInspector(Magics):
    """Implementation for a magic function that inspects a given python object.

    The extension then prints a syntax-highlighted and pretty-printed
    version of the provided object.
    """

    # Use Pygments to do syntax highlighting
    lexer = IPyLexer()
    if GruvboxStyle is not None:
        style = GruvboxStyle
    else:
        style = InkPotStyle
    formatter = TerminalTrueColorFormatter(style=style)

    def shell(self):
        # why the fuck is this returning none
        return get_ipython()

    def __repr__(self):
        return f"<{self.__class__.__name__}>:"

    @line_magic
    def ins(self, line=None):
        """Alias for the `%inspect_obj magic defined here."""
        self.inspect(line=line)

    @line_magic
    def inspect_obj(self, line=None):
        """Deviate from the original implementation a bit.

        In this version, we'll use the IPython lexer used at IPython.lib
        instead of pygments.

        Parameters
        ----------
        line : str
            Line to be evaluated by the IPython shell.
            Note that this invokes the get_ipython().ev() method.
            So we might wanna wrap this in a try/except but idk what it'll raise.

        """
        if not line:
            return

        # evaluate the line to get a python object
        python_object = self.shell.ev(line)

        # Pretty Print/Format the object
        # Print the output, but don't return anything (otherwise, we'd
        # potentially get a wall of color-coded text.
        formatted_dict = pformat(python_object.__dict__)
        print(highlight(formatted_dict, lexer, formatter).strip())
        pprint(python_object)


def load_ipython_extension(shell=None):
    """Add to the list of extensions used by IPython."""
    if shell is None:
        shell = get_ipython()
    if shell is None:
        return
    shell.register_magics(PrettyColorfulInspector)
    shell.register_magic_function(PrettyColorfulInspector.inspect_obj)
    shell.register_magic_function(PrettyColorfulInspector.ins)


if __name__ == "__main__":
    load_ipython_extension(get_ipython())
