import code
import functools
from pathlib import Path
import runpy
import sys

import pygments
from pygments.formatters.terminal256 import TerminalTrueColorFormatter

from IPython.core.getipython import get_ipython


class SubvertedInterpreter(code.InteractiveInterpreter):
    def __init__(self, shell=None, *args, **kwargs):
        self.shell = shell
        if self.shell is None:
            self.shell = get_ipython()
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}:>"

    def showsyntaxerror(self, *args, **kwargs):
        """Override the superclasses so we can ignore IPython's inconsistent way of calling this."""
        return super().showsyntaxerror()

    def showtraceback(self, *args, **kwargs):
        return super().showtraceback()

    def run(self, code_to_run=None):
        if code_to_run in sys.modules:
            runpy.run_module(code_to_run)
        elif Path(code_to_run).resolve().exists():
            runpy.run_path(code_to_run)
        else:
            self.shell.run_line_magic("run", code_to_run)

    @staticmethod
    def highlight(code):
        """Probably would work better as a standalone function but to logically follow the rest of the class we'll use it here."""

        @functools.wrap
        def wrapped(*args, **kwargs):
            return pygments.highlight(
                code,
                pygments.lexers.python.Python3Lexer(),
                TerminalTrueColorFormatter(),
                outfile=sys.stderr,
            )

        return wrapped

    def write(self, data):
        self.highlight(data)

    @property
    def last_execution_result(self):
        return self.shell.last_execution_result

    @property
    def last_execution_succeeded(self):
        return self.shell.last_execution_succeeded

    @property
    def execution_info(self):
        return self.last_execution_result.info


if __name__ == "__main__":
    interpreter = SubvertedInterpreter()

    # supposed to be used on the class not the instance
    # _ip.add_traits({"interpreter": code.InteractiveConsole(locals())})

    _ip.interpreter = interpreter
    _ip.showsyntaxerror = _ip.interpreter.showsyntaxerror
    _ip.showtraceback = _ip.interpreter.showtraceback

