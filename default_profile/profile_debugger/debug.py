# Copyright (c) 2011-2016 Godefroid Chapelle and ipdb development team
#
# This file is part of ipdb.
# Redistributable under the revised BSD license
# https://opensource.org/licenses/BSD-3-Clause
"""Copied it because the BdbQuit_excepthook he uses is deprecated.

Huh! This is neat. He imports pdb.Restart. Check out the call signature.

.. class:: pdb.Restart

   class Restart(builtins.Exception)
   Causes a debugger to be restarted for the debugged python program.

.. todo:: ipdb doesnt take a -m option. pdb started taking it in 3.7.

"""
import argparse
import logging
import os
import sys
import traceback
from bdb import BdbQuit
from contextlib import contextmanager
from pathlib import Path
from pdb import Restart
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
        debugger_kls = debugger_kls
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
            "-f", "--file",
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


# def debug_forever():


def main():
    program_name, *args = sys.argv
    parser = get_parser()
    if not args:
        sys.exit(parser.print_help())

    namespace = parser.parse_args(args)

    if hasattr(namespace, "mainpyfile"):
        if not Path(namespace.mainpyfile).exists():
            raise FileNotFoundError

        mainpyfile = namespace.mainpyfile
        # Replace pdb's dir with script's dir in front of module search path.
        sys.path.insert(0, os.path.dirname(mainpyfile))
    # should probably make an else. 

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = _init_pdb(commands=namespace.commands)

    # ????
    # while True:
    #     debug_forever()
    try:
        pdb._runscript(mainpyfile)
        if pdb._user_requested_quit:
            return
        logger.warning("The program finished and will be restarted")
    except Restart:
        logger.info(f"Restarting {mainpyfile} with arguments:\t{str(sys.argv[1:])}")
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
        print("Post mortem debugger finished. The " + mainpyfile + " will be restarted")


if __name__ == "__main__":
    # Moving all the globals because that shit drives me nuts
    shell = get_ipython()
    if shell is None:
        # Not inside IPython
        # Build a terminal app in order to force ipython to load the
        # configuration
        ipapp = TerminalIPythonApp()
        # Avoid output (banner, prints)
        ipapp.interact = False
        ipapp.initialize(["--no-term-title"])
        shell = ipapp.shell
    else:
        # Running inside IPython

        # Detect if embed shell or not and display a message
        if isinstance(shell, InteractiveShellEmbed):
            sys.stderr.write(
                "\nYou are currently into an embedded ipython shell,\n"
                "the configuration will not be loaded.\n\n"
            )

    # todo: so the actual implementation of this in ipython is shell.debugger()
    # a method to run IPython.core.ultratb.AutoformattedTB.debugger()
    # AutoFormattedTB is bound to the shell as InteractiveTB.
    # It also doesnt have a debugger method but subclasses VerboseTB which does.
    # So if we bind this debugger class to the `debugger` attribute
    # A) things becone a little less interconnected and fucky and
    # B) itll probably run faster since it wont need to resolve mixins on  subclasses on subclasses

    # Also of note.:
    # :attr:`debugger_history`
    # In [43]: _ip.debugger_history
    # Out[43]: <prompt_toolkit.history.InMemoryHistory at 0x7e42910490>
    # add an arg for log file and switch this to a FileHistory
    global debugger_cls
    debugger_cls = MyPdb
    main()
