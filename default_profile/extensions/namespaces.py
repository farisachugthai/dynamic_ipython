"""Simply gonna jot this down fast.

Sorry for the sloppiness.
"""
import sys
from inspect import getdoc

from pyfzf.pyfzf import FzfPrompt

from prompt_toolkit.application.current import get_app
from prompt_toolkit.application.run_in_terminal import run_in_terminal
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import print_formatted_text as print
from prompt_toolkit.utils import Event

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


def new_shortcuts():
    """Let's overlay a few shortcuts with the default ones."""
    app = get_app()
    shell = get_ipython()
    kb = create_ipython_shortcuts(shell)
    fzf_keys = (Keys.ControlT, HasFocus=DEFAULT_BUFFER)

    # not sure how pt wants us to do this part
    # with run_in_terminal(FzfPrompt(), render_cli_done=True, in_executor=True):
    # fzf_prompt = FzfPrompt()
    # launch with
    # fzf_prompt.prompt()
    # todo:
    # kb.add_binding()


if __name__ == "__main__":
    _, *args = sys.argv[:]
    if len(args) > 0:
        print(getdoc(*args))
    else:
        sys.exit('Need to provide an argument.')