#!/usr/bin/env python
# -*- coding: utf-8 -*-
import code
import cgitb
import faulthandler
import functools
import logging
import os
import pathlib
from reprlib import Repr
import sys
import trace
import traceback

from prompt_toolkit import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.defaults import load_key_bindings

import traitlets
from traitlets.config.loader import Config
from traitlets.config.application import Application
from IPython.core.magics.basic import BasicMagics
from IPython.core.getipython import get_ipython
from IPython.core.profiledir import ProfileDir, ProfileDirError
from IPython.extensions.storemagic import StoreMagics
from IPython.terminal.interactiveshell import TerminalInteractiveShell


logging.basicConfig(level=logging.INFO)


class TerminallyUnimpaired(TerminalInteractiveShell):
    """What do we need to implement?

    Assuming this'll crash then we can notate what was required.

    We crashed on loading magics? Weird.
    Uhh I'm just gonna add a Config to ensure that it's there.

    """
    kb = KeyBindings()
    all_kb = load_key_bindings()

    def __repr__(self):
        return f"<{Repr().repr(self.__class__.__name__)}>:"

    def begin(self):
        """The superclass already defined initialize and a few other methods.

        So let's go with begin since we don't have much room in this namespace.
        """
        if self.config is None:
            self.config = Config()
        super().initialize()

    @staticmethod
    def execfile(fname, user_global=None):
        """Apparently using global raises an error.

        Could've checked it wasn't reserved I  guess.
        """
        user_global = user_global or globals()
        with open(fname, "rb") as f:
            code_obj = compile(f.read(), "<string>", "exec")
            clean_ns = {}
            # Are you still allowed to do this?
            # return exec(code_obj in clean_ns)
            # nope
            return exec(code_obj, user_global, clean_ns)

    def init_profile_dir(self, profile_dir=None):
        """Modify this so we have a none argument for profile_dir."""
        if profile_dir is not None:
            self.profile_dir = profile_dir
            return
        try:
            self.profile_dir = ProfileDir.create_profile_dir_by_name(
                self.ipython_dir, "default"
            )
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
            lines.extend(traceback.format_exception_only(exception_type, value))
        finally:
            tblist = tb = None
        if lines:
            sys.stderr.write("".join(lines))

    def custom_toolbar(self) -> HTML:
        """TODO: I want this to return as the bottom toolbar.

        Does it go in self.extra_prompt_options?
        """
        s = "New Terminal REPL"

        @functools.wraps
        def entry(k: str, v: str) -> str:
            return f' | <b><style bg="ansiblue">{k.capitalize()}</style></b> {v}'

        s += entry("multiline", self.config.multiline)
        s += entry("directory", pathlib.Path().cwd())
        s += entry("style", self.config.highlighting_style)

        return HTML(s)


class Terminally(TerminalInteractiveShell):
    """Since a lot of these things are class attributes, can I assign to a subclass and have things automagically appear in teh super?"""

    kb = KeyBindings()

    def __init__(self, config=None, *args, **kwargs):
        """Note that initialization requires a config object.

        traitlets raises an error so let's setup a little dance around that.
        """
        super().__init__(*args, **kwargs)
        self.config = config or self._create_config()
        self.Completer = self.create_completer()

    def __call__(self):
        super().prompt_for_code()

    @staticmethod
    def _create_config():
        running_shell = get_ipython()
        if running_shell is not None:
            # Well this'll probably cause some issues because 2 of these can't
            # running at the same time
            return running_shell.config

    def create_kb(self):
        # TODO
        raise NotImplementedError

    def create_lexer(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def create_completer():
        import rlcompleter

        return rlcompleter.Completer

    def _extra_prompt_options(self, **kwargs):
        """Override the superclasses method because this feels like a solid spot to inject some configurability."""
        if kwargs is None:
            return super()._extra_prompt_options
        else:
            return {**kwargs}


class StoreAndLoadMagics(StoreMagics):
    """I keep getting an error about this."""

    # StoreMagics(get_ipython()).unobserve_all()
    def __init__(self, shell=None, *args, **kwargs):
        """TODO: Docstring for function."""
        super().__init__(self, *args, **kwargs)
        self.shell = shell or get_ipython()

    def load_ext(self):
        self.shell.register_magics(self)

    # Load the extension in IPython.
    def register_magic(self, ip):
        """Are you allowed to do this?"""
        ip.register_magics(self)


def load_ipython_extension(ip=None):
    """Load the extension in IPython."""
    if ip is None:
        ip = get_ipython()

    storemagic = StoreMagics(ip)
    ip.register_magics(storemagic)
    # ip.events.register('pre_run_cell', storemagic.pre_run_cell)
    # ip.events.register('post_execute', storemagic.post_execute_hook)


if __name__ == "__main__":
    if Application.initialized():
        config = Application.instance().config
    else:
        # If we try starting a new application or shell here, it'll raise
        # either an ApplicationError or a TraitError. Which I guess we could
        # catch but f it
        sys.exit()

    logging.info('Config was %s', config)

    try:
        unimpaired = TerminallyUnimpaired()
    except Exception as e:  # noqa
        logging.exception(e)
        shell = None
    # else:
    #     shell.extension_manager.load_extension("storeandloadmagics")
