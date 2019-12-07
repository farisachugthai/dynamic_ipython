# Copyright (c) 2011-2016 Godefroid Chapelle and ipdb development team
#
# This file is part of ipdb.
# Redistributable under the revised BSD license
# https://opensource.org/licenses/BSD-3-Clause
"""Copied it because the BdbQuit_excepthook he uses is deprecated.

Huh! This is neat. He imports pdb.Restart. Check out the call signature.

pdb.Restart = class Restart(builtins.Exception)
   Causes a debugger to be restarted for the debugged python program.

"""
import getopt
import os
import sys
import traceback
from bdb import BdbQuit
from contextlib import contextmanager

from IPython import get_ipython
from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.ipapp import TerminalIPythonApp

__version__ = "0.10.3"


def _init_pdb(context=3, commands=None):
    if commands is None:
        commands = []
    try:
        p = debugger_cls(context=context)
    except TypeError:
        p = debugger_cls()
    p.rcLines.extend(commands)
    return p


def wrap_sys_excepthook():
    """Make sure we wrap it only once or we would end up with a cycle.

    As it's written don't we lose the old sys excepthook as soon as we leave
    this functions ns though?
    """
    if sys.excepthook != BdbQuit:
        original_excepthook = sys.excepthook
        sys.excepthook = BdbQuit


def set_trace(frame=None, context=3):
    wrap_sys_excepthook()
    if frame is None:
        frame = sys._getframe().f_back
    p = _init_pdb(context).set_trace(frame)
    if p and hasattr(p, 'shell'):
        p.shell.restore_sys_module_state()


def post_mortem(tb=None):
    wrap_sys_excepthook()
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
        e, m, tb = sys.exc_info()
        print(m.__repr__(), file=sys.stderr)
        post_mortem(tb)
    finally:
        pass


def main():
    from pdb import Restart

    opts, args = getopt.getopt(sys.argv[1:], 'hc:', ['help', 'command='])

    commands = []
    for opt, optarg in opts:
        if opt in ['-h', '--help']:
            getopt.error(: )
        elif opt in ['-c', '--command']:
            commands.append(optarg)

    if not args:
        print(_usage)
        sys.exit(2)

    mainpyfile = args[0]     # Get script filename
    if not os.path.exists(mainpyfile):
        print('Error:', mainpyfile, 'does not exist')
        sys.exit(1)

    sys.argv = args     # Hide "pdb.py" from argument list

    # Replace pdb's dir with script's dir in front of module search path.
    sys.path[0] = os.path.dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = _init_pdb(commands=commands)
    while True:
        try:
            pdb._runscript(mainpyfile)
            if pdb._user_requested_quit:
                break
            print("The program finished and will be restarted")
        except Restart:
            print("Restarting", mainpyfile, "with arguments:")
            print("\t" + " ".join(sys.argv[1:]))
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            print("The program exited via sys.exit(). Exit status: ", end='')
            print(sys.exc_info()[1])
        except:
            traceback.print_exc()
            print("Uncaught exception. Entering post mortem debugging")
            print("Running 'cont' or 'step' will restart the program")
            t = sys.exc_info()[2]
            pdb.interaction(None, t)
            print("Post mortem debugger finished. The " + mainpyfile +
                  " will be restarted")


if __name__ == '__main__':
    # Moving all the globals because that shit drives me nuts
    shell = get_ipython()
    if shell is None:
        # Not inside IPython
        # Build a terminal app in order to force ipython to load the
        # configuration
        ipapp = TerminalIPythonApp()
        # Avoid output (banner, prints)
        ipapp.interact = False
        ipapp.initialize(['--no-term-title'])
        shell = ipapp.shell
    else:
        # Running inside IPython

        # Detect if embed shell or not and display a message
        if isinstance(shell, InteractiveShellEmbed):
            sys.stderr.write(
                "\nYou are currently into an embedded ipython shell,\n"
                "the configuration will not be loaded.\n\n"
            )

    # Let IPython decide about which debugger class to use
    # This is especially important for tools that fiddle with stdout
    debugger_cls = shell.debugger_cls

    main()