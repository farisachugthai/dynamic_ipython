"""Simply gonna jot this down fast.

Sorry for the sloppiness
"""
import sys
from inspect import getdoc

from pyfzf.pyfzf import FzfPrompt

from prompt_toolkit.shortcuts import print_formatted_text as print
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.keys import Keys

from IPython import get_ipython
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.terminal.shortcuts import create_ipython_shortcuts


class TestInter(TerminalInteractiveShell):

    shell = get_ipython()

    config = shell.config

    def __init__(self, *args, **kwargs):
        """Does this work if they didnt define an init?"""
        self.shell = shell
        self.config = config
        super().__init__(self, *args, **kwargs)


def new_shortcuts(shell):
    kb = create_ipython_shortcuts()
    fzf_keys = (Keys.ControlT, HasFocus=DEFAULT_BUFFER)

    fzf_prompt = FzfPrompt()
    # fzf_prompt.prompt()
    # launch with
    # todo:
    # kb.add_binding()

if __name__ == "__main__":
    _, *args = sys.argv[:]
    if len(args) > 0:
        print(getdoc(*args))
    else:
        sys.exit('Need to provide an argument.')
