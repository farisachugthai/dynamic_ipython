#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Few more things we might wanna work out here.

Our lack of the module :mod:`inspect` is pretty surprising.

Refer to either `IPython.core.oinspect` or `xonsh.inspectors`
for some good uses of the std lib module.

"""
from pprint import pformat

from pygments import highlight
from pygments.formatters import Terminal256Formatter  # Or TerminalFormatter

# from pygments.lexers import PythonLexer
from IPython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magic import register_line_magic, magic_escapes
from IPython.lib.lexers import IPyLexer


@magics_class
class PrettyColorfulInspector(Magics):
    """Implementation for a magic function that inspects a given python object.

    The extension then prints a syntax-highlighted and pretty-printed
    version of the provided object.
    """

    @line_magic
    def i(self, line=None):
        """Alias for the `%inspect magic defined here."""
        self.inspect(line=line)

    @line_magic
    def inspect(self, line=None):
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
        if line:
            # Use Pygments to do syntax highlighting
            lexer = IPyLexer()
            formatter = Terminal256Formatter()

            # evaluate the line to get a python object
            python_object = self.shell.ev(line)

            # Pretty Print/Format the object
            formatted_object = pformat(python_object)

            # Print the output, but don't return anything (otherwise, we'd
            # potentially get a wall of color-coded text.
            # print(highlight(formatted_object, lexer, formatter).strip())

            formatted_dict = pformat(python_object.__dict__)
            print(highlight(formatted_dict, lexer, formatter).strip())


def load_ipython_extension(shell=None):
    """Add to the list of extensions used by IPython."""
    if shell is None:
        shell = get_ipython()
    shell.register_magics(PrettyColorfulInspector)
    shell.register_line_magic(PrettyColorfulInspector.inspect)
    shell.register_line_magic(PrettyColorfulInspector.i)


if __name__ == "__main__":
    # Register with IPython
    ip = get_ipython()
    # ip.register_magics(PrettyColorfulInspector)
    # which one? load_extension or register

    register_line_magic()
    load_ipython_extension(ip)
