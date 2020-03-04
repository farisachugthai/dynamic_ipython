#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is an example that shows how to create new prompts for IPython.

Adds use of format strings and f strings to the example given in the docs.

In addition, uses the original definition of the prompt in order to appear similar.

See Also
--------

Powerline has some cool stuff for configuring the prompt and they have
stuff for IPython<=0.11, 0.11<=IPython<=5.5 AND 5.5<=IPython!

"""
import time
from os import getcwd

from pygments.token import Token

from IPython.core.getipython import get_ipython
from IPython.core.magic import  magics_class
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

    def __repr__(self):
        return "{!r}".format(self.in_prompt_tokens())

    def __len__(self):
        """Implement length with the superclasses ``_width``."""
        return self._width()

    def in_prompt_tokens(self):
        return [
            (Token.Generic.Heading, getcwd()),
            (Token.Generic.SubHeading, "\nTime: "),
            (Token.Keyword.Namespace, f"{time.ctime()}:\n"),
            (Token.Name.Tag, super().vi_mode()),
            (Token.Prompt, "In ["),
            (Token.PromptNum, f"{self.shell.execution_count:d}"),
            (Token.Prompt, "]: "),
        ]

    def __call__(self):
        return self.in_prompt_tokens()


def load_ipython_extension(shell, *args, **kwargs):
    """Set the prompt to CwdPrompt.

    Save the old prompt in the variable new_prompts.old_prompts.

    Parameters
    ----------
    shell : |ip|
        Note it's not optional. IPython call it with a pos arg

    """
    new_prompts = CwdPrompt(get_ipython())
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


if __name__ == "__main__":
    # So here's a more direct way of loading these suckers
    # without setting off the deprecation warning
    get_ipython().extension_manager._call_load_ipython_extension('cwd_prompt')
    # or i guess
    get_ipython().extension_manager._call_unload_ipython_extension('cwd_prompt')
