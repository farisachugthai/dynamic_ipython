#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.core.magics.basic import BasicMagics
from IPython.core.getipython import get_ipython
from IPython.core.profiledir import ProfileDir, ProfileDirError
from traitlets.config.loader import Config
import traitlets
import logging
import os
from reprlib import Repr
import sys

from . import storeandloadmagics
from .storeandloadmagics import StoreAndLoadMagics

logging.basicConfig(level=logging.INFO)


class TerminallyUnimpaired(TerminalInteractiveShell):
    """What do we need to implement?

    Assuming this'll crash then we can notate what was required.

    We crashed on loading magics? Weird.
    Uhh I'm just gonna add a Config to ensure that it's there.

    """

    def __repr__(self):
        truncated = Repr().repr(self.__class__.__name__)
        return "".format(truncated)

    def begin(self):
        """The superclass already defined initialize and a few other methods.

        So let's go with begin since we don't have much room in this namespace.
        """
        super().initialize()
        if self.config is None:
            self.config = Config()

    @staticmethod
    def execfile(fname, user_global=None, local=None):
        """Apparently using global raises an error.

        Could've checked it wasn't reserved I  guess.
        """
        local = local if local is not None else user_global
        with open(fname, "rb") as f:
            code_obj = compile(f.read(), "<string>", "exec")
            clean_ns = {}
            # Are you still allowed to do this?
            # return exec(code_obj in clean_ns)
            # nope
            return exec(code_obj, user_global, local)

    def init_profile_dir(self, profile_dir=None):
        """Modify this so we have a none argument for profile_dir."""
        if profile_dir is not None:
            self.profile_dir = profile_dir
            return
        try:
            self.profile_dir = ProfileDir.create_profile_dir_by_name(
                self.ipython_dir, "default")
        except ProfileDirError:
            self.log.error("Profiledirerror")
        except Exception as e:
            self.log.warning(e)

    def showsyntaxerror(self, filename=None, **kwargs):
        """Display the syntax error that just occurred.

        How refreshing is it to not have tracebacks intertwined with
        every other aspect of your application :D

        Parameters
        ----------
        filename :
        **kwargs :

        """
        # Override for avoid using sys.excepthook PY-12600
        exception_type, value, tb = sys.exc_info()
        sys.last_type = exception_type
        sys.last_value = value
        sys.last_traceback = tb
        if filename and exception_type is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, line) = value.args
            except ValueError:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        _ = traceback.format_exception_only(exception_type, value)
        sys.stderr.write("".join(_))

    def showtraceback(self, *args, **kwargs):
        """Display the exception that just occurred."""
        # Override for avoid using sys.excepthook PY-12600
        try:
            exception_type, value, tb = sys.exc_info()
            sys.last_type = exception_type
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            lines = traceback.format_list(tblist)
            if lines:
                lines.insert(0, "Traceback (most recent call last):\n")
            lines.extend(traceback.format_exception_only(
                exception_type, value))
        finally:
            tblist = tb = None
        sys.stderr.write("".join(lines))


shell = TerminallyUnimpaired()
shell.extension_manager.load_extension('storeandloadmagics')
