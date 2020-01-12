#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is an example that shows how to create new prompts for IPython.

See Also
--------
Powerline has some cool stuff for configuring the prompt and they have
stuff for IPython<=0.11, 0.11<=IPython<=5.5 AND 5.5<=IPython!


"""
from os import getcwd

from pygments.token import Token

from IPython.core.getipython import get_ipython
from IPython.core.magic import magics_class
from IPython.terminal.prompts import Prompts


@magics_class
class CwdPrompt(Prompts):
    """Create a customized instance of an IPython prompt.

    Specifically, include the current working directory.

    Unsure of whether I need that decorator though.
    """

    def __init__(self, shell=None, *args, **kwargs):
        """I think we need to define old_prompts.

        In the unload_ipython_extension part of this it checks the shells
        current prompt for an old_prompts attr. So we need to define it here
        for it to unload right?
        """
        self.shell = shell or get_ipython()
        if self.shell is not None:
            self.old_prompt = self.shell.prompts
            super().__init__(self.shell, *args, **kwargs)

    # this returns a list
    # def __repr__(self):
    #     return self.in_prompt_tokens(cli=self.shell)

    def __repr__(self):
        return "{!r}".format(self.in_prompt_tokens(cli=self.shell))

    def in_prompt_tokens(self, cli=None):
        """Uh what was cli supposed to be?"""
        return [(Token, getcwd()), (Token.Prompt, " >>> ")]

    def __call__(self):
        # ?
        return self.in_prompt_tokens()


def load_ipython_extension(shell):
    """Set the prompt to CwdPrompt.

    Save the old prompt in the variable new_prompts.old_prompts.

    Parameters
    ----------
    shell : |ip|, optional

    """
    new_prompts = CwdPrompt(shell)
    new_prompts.old_prompts = shell.prompts
    shell.prompts = new_prompts


def unload_ipython_extension(shell):
    """Recover the old prompt.

    Parameters
    ----------
    shell : |ip|, optional

    """
    if not hasattr(shell.prompts, "old_prompts"):
        print("cannot unload")
    else:
        shell.prompts = shell.prompts.old_prompts
