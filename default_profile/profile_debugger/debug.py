#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a script that allows for interactive use of the `MyPdb` class.

The class generated in the `default_profile.profile_debugger.pdbrc` module,
`MyPdb` comes with a customized prompt, readline integration and fault
handlers to catch any exceptions.


"""
import argparse

import logging
import os
import sys
import traceback
from bdb import BdbQuit
from contextlib import contextmanager
from pathlib import Path
from pdb import Restart, Pdb
from textwrap import dedent

try:
    from pdbrc import MyPdb
except:  # noqa
    MyPdb = None

from jedi.api import replstartup
from IPython.core.getipython import get_ipython
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.ipapp import TerminalIPythonApp


logger = logging.getLogger()


def _init_pdb(context=3, commands=None, debugger_kls=None):
    """Needed to add a debugger_cls param to this."""
    if debugger_kls is None:
        if MyPdb is not None:
            debugger_kls = MyPdb
        elif ipdb is not None:
            debugger_kls = ipdb
        else:
            debugger_kls = Pdb
    if commands is None:
        commands = []
    try:
        p = debugger_kls(context=context)
    except TypeError:
        p = debugger_kls()
    p.rcLines.extend(commands)
    return p


def wrap_sys_excepthook():
    """Make sure we wrap it only once or we would end up with a cycle.

    As it's written don't we lose the old sys excepthook as soon as we leave
    this functions ns though?

    Also how do you compare Exceptions and whatever excepthook is?
    """
    if sys.excepthook != BdbQuit:
        original_excepthook = sys.excepthook
        sys.excepthook = BdbQuit


def set_trace(frame=None, context=3):
    # wrap_sys_excepthook()
    if frame is None:
        frame = sys._getframe().f_back
    p = _init_pdb(context).set_trace(frame)
    if p and hasattr(p, "shell"):
        p.shell.restore_sys_module_state()


def post_mortem(tb=None):
    # wrap_sys_excepthook()
    p = _init_pdb()
    p.reset()
    if tb is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        tb = sys.exc_info()[2]
    if tb:
        p.interaction(None, tb)


def pm():
    post_mortem(sys.last_traceback)


def run(statement, globals=None, locals=None):
    _init_pdb().run(statement, globals, locals)


def runcall(*args, **kwargs):
    return _init_pdb().runcall(*args, **kwargs)


def runeval(expression, globals=None, locals=None):
    return _init_pdb().runeval(expression, globals, locals)


@contextmanager
def launch_ipdb_on_exception():
    try:
        yield
    except Exception:
        if hasattr(sys, "exc_info"):
            print(sys.exc_info()[2])
        post_mortem(tb)
    finally:
        pass


def get_parser():
    """Factored out of main. Well sweet this now rasies an error."""
    parser = argparse.ArgumentParser(
        prog="ipdb+",
        description=(
            "\nAn IPython flavored version of pdb with even more useful features."
            "\nWhy?\nYou're debugging code you don't want to figure out if you"
            " imported something or not.\n\n"
        ),
    )

    # i hate positionals but hang on to it for a little
    # parser.add_argument(
    #     "mainpyfile",
    #     metavar="File to execute",
    #     action="store",
    # type=argparse.Filetype  this doesnt work?
    # also can we add nargs and have more than one?
    # help="File to run under the debugger."
    # )
    parser.add_argument(
        "-f",
        "--file",
        action="store",
        dest="mainpyfile",
        help="File to run under the debugger.",
    )

    parser.add_argument(
        "-c",
        "--commands",
        nargs="*",
        type=list,
        help="List of commands to run before starting.",
        default=[],
        action="append",
    )

    parser.add_argument(
        "-m",
        "--module",
        nargs="?",
        help=dedent(
            "Module to debug. Note that the provided module will be subject"
            " to all the standard rules that any imported module would be"
            " as per the import rules specified in the language/library"
            " references."
        ),
        dest="mod",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        help="Force interactivity if pdb would otherwise exit.",
        const=True,
        nargs="?",
        default=False,
    )

    parser.add_argument("-v", "--version", action="version")

    return parser


def debug_script(script=None):
    if script is None:
        return
    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = _init_pdb(commands=namespace.commands)

    try:
        pdb._runscript(script)
        if pdb._user_requested_quit:
            return
        logger.warning("The program finished and will be restarted")
    except Restart:
        logger.info(f"Restarting {script} with arguments:\t{str(sys.argv[1:])}")
    except BdbQuit:
        logger.critical("Quit signal received.  Goodbye!")

    except SystemExit:
        # In most cases SystemExit does not warrant a post-mortem session.
        print("The program exited via sys.exit(). Exit status: ", end="")
        print(sys.exc_info()[1])
    except:
        traceback.print_exc()
        print("Uncaught exception. Entering post mortem debugging")
        print("Running 'cont' or 'step' will restart the program")
        t = sys.exc_info()[2]
        pdb.interaction(None, t)
        print("Post mortem debugger finished. The " + script + " will be restarted")


def main():
    """Parses users argument and dispatches based on responses."""
    program_name, *args = sys.argv
    parser = get_parser()
    if not args:
        # Print some help, then don't do the other junk here
        parser.print_help()
        return

    try:
        namespace = parser.parse_args(args)
    except SystemExit:
        # can't believe i'm catching sysexit but fuck you argparse
        namespace = None

    if hasattr(namespace, "mainpyfile"):
        if namespace.mainpyfile is not None:
            if not Path(namespace.mainpyfile).exists():
                raise FileNotFoundError
    else:
        _init_pdb().set_trace()

    mainpyfile = namespace.mainpyfile
    # Replace pdb's dir with script's dir in front of module search path.
    if mainpyfile is not None:
        sys.path.insert(0, os.path.dirname(mainpyfile))
        debug_script(mainpyfile)


def get_or_start_ipython():
    """Returns the global IPython instance.

    Summary
    -------

    Extended Summary
    ----------------
    In contrast to `IPython.core.getipython.get_ipython`, this will start
    IPython if `get_ipython` returns None.

    Builds a terminal app in order to force IPython to load the
    user's configuration.
    `IPython.terminal.TerminalIPythonApp.interact` is set to False to
    avoid output (banner, prints) and then the TerminalIPythonApp is
    initialized with '--no-term-title'.
    """
    shell = get_ipython()
    if shell is None:
        ipapp = TerminalIPythonApp()
        ipapp.interact = False
        ipapp.initialize(["--no-term-title"])
        shell = ipapp.shell
    else:
        # Detect if embed shell or not and display a message
        if isinstance(shell, InteractiveShellEmbed):
            sys.stderr.write(
                "\nYou are currently into an embedded ipython shell,\n"
                "the configuration will not be loaded.\n\n"
            )


if __name__ == "__main__":
    main()
