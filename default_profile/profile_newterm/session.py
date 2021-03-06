"""Here's what we're designing for.

c.TerminalInteractiveShell.prompts_class = 'IPython.terminal.prompts.Prompts'

"""
import logging

from IPython.core.getipython import get_ipython
from IPython.terminal.prompts import Prompts, RichPromptDisplayHook

from prompt_toolkit.application.current import get_app
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.layout import Window
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.shortcuts.prompt import PromptSession

from traitlets.config import get_config, SingletonConfigurable
from traitlets.config import Bool, Enum


class RightPrompt(Window):
    """This isn't in ``__all__`` so let's redefine it."""

    def __init__(self, get_formatted_text):
        super().__init__(
            FormattedTextControl(get_formatted_text),
            align=WindowAlign.RIGHT,
            style="class:rprompt",
        )


class SessionPrompt(Prompts):
    """Let's build our own prompt session."""

    def __init__(self, *args, **kwargs):
        """What does this look like with an init and all the traits?"""
        super().__init__(self)
        self.vi_mode = Bool(False, help="Enabled vi mode").tag(config=True)

        self.editing_mode = Enum(
            klass=EditingMode, default_value=EditingMode.Emacs
        ).tag(config=True)


if __name__ == "__main__":
    current_configurable = get_config()
    if getattr(current_configurable, "Prompts", None):
        current_configurable.Prompts = SessionPrompt
    else:
        logging.error(
            "New PromptSession did not work. Prompt attr: %s",
            getattr(current_configurable, "Prompts", None),
        )

    shell = get_ipython()
    if getattr(shell, "prompts_class", None):
        shell.prompts_class = SessionPrompt
