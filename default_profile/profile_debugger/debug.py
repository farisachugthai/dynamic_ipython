#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a script that allows for interactive use of the `MyPdb` class.

The class generated in the `default_profile.profile_debugger.pdbrc` module,
`MyPdb` comes with a customized prompt, readline integration and fault
handlers to catch any exceptions.


"""


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
