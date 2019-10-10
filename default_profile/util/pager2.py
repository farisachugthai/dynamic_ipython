#!/usr/bin/env python
# -*- coding: utf-8 -*-

from IPython import get_ipython
# Might need some of the funcs from IPython.utils.{PyColorize,coloransi,colorable}

try:
    import pynvim
except (ImportError, ModuleNotFoundError):
    pynvim = None


def connect_to_neovim():
    """Gonna meander a bit in this module."""
    if os.environ.get('NVIM_LISTEN_ADDRESS'):
        try:
            nvim = pynvim.attach('socket', path=os.environ.get('NVIM_LISTEN_ADDRESS'))
        except RuntimeError:
            # I realize that this is probably an insane exception to catch
            # However, if you run this code inside of a Neovim session it'll crash as it doesn't want to run a
            # new asynchronous loop on top of another.
            # So catch that exception and just keep moving.
            # We never connected to the user so we actually
            # can't notify them of anything so we'll let them know
            # we're dead in the water elsewhere...
            return
        return nvim


def page_in_neovim():
    """I just did this in neovim and thought it was cool.

    Well I did it a little differently than this. The mental model of how
    nvim connects to python and how they communicate is really confusing to me.
    """
    vim = connect_to_neovim()
    vim.command('py3 import pydoc; pydoc.ttypager(<cword>)')


def load_ipython_docstring(shell):
    """TODO: Docstring for load_ipython_docstring.

    Parameters
    ----------
    shell : |ip|
        Global IPython object.

    """
    pass


def main():
    """Rewrite the module that creates the ``%pycat`` magic.

    In it's current implementation, the pager gives Windows a dumb terminal and
    never checks for whether :command:`less` is on the :envvar:`PATH` or
    if the user has a pager they wanna implement!

    """
    pass


if __name__ == "__main__":
    _ip = get_ipython()
    # main()
