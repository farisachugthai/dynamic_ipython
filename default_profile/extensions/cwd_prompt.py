#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is an example that shows how to create new prompts for IPython.

See Also
--------
Powerline has some cool stuff for configuring the prompt and they have
stuff for IPython<=0.11, 0.11<=IPython<=5.5 AND 5.5<=IPython!


"""
import os

from IPython import get_ipython
from IPython.core.magic import magics_class
from IPython.terminal.prompts import Prompts, Token


@magics_class
class MyPrompt(Prompts):
    """Create a customized instance of an IPython prompt.

    Specifically, include the current working directory.

    Unsure of whether I need that decorator though.
    """
    def in_prompt_tokens(self, cli=None):
        return [(Token, os.getcwd()), (Token.Prompt, '>>>')]


def load_ipython_extension(shell):
    """Set the prompt to MyPrompt and save the old prompt in the variable new_prompts.old_prompts."""
    new_prompts = MyPrompt(shell)
    new_prompts.old_prompts = shell.prompts
    shell.prompts = new_prompts


def unload_ipython_extension(shell):
    """Recover the old prompt."""
    if not hasattr(shell.prompts, 'old_prompts'):
        print("cannot unload")
    else:
        shell.prompts = shell.prompts.old_prompts


if __name__ == "__main__":
    _ip = get_ipython()
    if _ip is not None:
        load_ipython_extension(_ip)
