import abc
import keyword
import logging
from pathlib import Path
import re
import runpy
from typing import Iterable, TYPE_CHECKING

import jedi
from jedi.api import replstartup
from jedi.api.project import get_default_project
from jedi.utils import setup_readline
from jedi.api.environment import get_cached_default_environment, InvalidPythonEnvironment

from IPython.core.getipython import get_ipython

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    PathCompleter,
    ThreadedCompleter,
    WordCompleter,
    merge_completers,
)
from prompt_toolkit.completion.fuzzy_completer import FuzzyWordCompleter
from prompt_toolkit.document import Document

from traitlets.traitlets import Instance
from traitlets.config import LoggingConfigurable


class ConfigurableCompleter(LoggingConfigurable):
    shell = Instance("IPython.core.interactiveshell.InteractiveShellABC")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SimpleCompleter(Completer, abc.ABC):
    @abc.abstractproperty
    def document(self):
        # does it make sense to create these 2 as abstract properties?
        raise

    # @abc.abstractproperty
    # def current_text(self):
    #     raise

    @abc.abstractmethod
    def get_completions(self, doc=None, complete_event=None, **kwargs):
        raise

    # @abc.abstractmethod
    # def _initialize_completer(self, *args, **kwargs):
    #     raise

    @abc.abstractmethod
    def __call__(self, document, event):
        return self.get_completions(doc=document, complete_event=event)


class SimpleCompletions(Completer):
    # Do you make super calls after subclassing ABC?
    # shit do we have to mix something else in?

    def __init__(self, shell=None, *args, **kwargs):
        self.shell = shell or get_ipython()
        self._initialize_completer()
        super().__init__(*args, **kwargs)

    @property
    def user_ns(self):
        return self.shell.user_ns

    def _initialize_completer(self, *args, **kwargs):
        if not args and not kwargs:
            self.completer = WordCompleter(
                self.user_ns, pattern=re.compile(r"^([a-zA-Z0-9_.]+|[^a-zA-Z0-9_.\s]+)")
            )
        # TODO: else:

    @property
    def document(self):
        return self.shell.pt_app.app.current_buffer.document

    def get_completions(self, doc=None, complete_event=None, **kwargs):
        """For now lets not worry about CompleteEvent too much. But we will need to add a
        get_async_completions method."""
        if doc is None:
            doc = self.document
        if complete_event is None:
            complete_event = CompleteEvent()
        yield self.completer.get_completions(
            document=doc, complete_event=complete_event, **kwargs
        )

    def __call__(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        self.get_completions(doc=document, complete_event=complete_event)


class PathCallable(PathCompleter):
    """OF COURSE ITS NOT CALLABLE.

    Also why is get_paths even a method? If someones looking for a relative
    directory, why wouldn't you assume that it's relative **to their current
    working directory??**

    """

    get_paths = Path()

    def __call__(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        super().get_completions(doc=document, complete_event=complete_event)


def get_path_completer():
    """Basically took this from Jon's unit tests."""
    return PathCallable(min_input_len=1, expanduser=True)


def get_fuzzy_keyword_completer():
    """Return all valid Python keywords."""
    return FuzzyWordCompleter(keyword.kwlist)


def get_word_completer():
    return WordCompleter(
        keyword.kwlist, pattern=re.compile(r"^([a-zA-Z0-9_.]+|[^a-zA-Z0-9_.\s]+)")
    )


def will_break_pt_app():
    # ergh
    merged_completers = merge_completers(
        [
            get_ipython().pt_app.completer,
            SimpleCompletions(),
            get_path_completer(),
            get_fuzzy_keyword_completer(),
            get_word_completer(),
        ]
    )
    get_ipython().pt_app.completer = merged_completers


if __name__ == "__main__":
    setup_readline()
    # To set up Script or Interpreter later
    project = get_default_project()
    try:
        environment = get_cached_default_environment()
    except InvalidPythonEnvironment:
        logging.warning("Jedi couldn't get the default project.")

    jedi.settings.add_bracket_after_function = False

    if get_ipython() is not None:
        _ip = get_ipython()
        threaded = ThreadedCompleter(get_word_completer)
        _ip.set_custom_completer(get_path_completer())
        _ip.set_custom_completer(get_fuzzy_keyword_completer)
        _ip.pt_app.auto_suggest = AutoSuggestFromHistory()

        if _ip.editing_mode == "vi":
            more_keybindings = merge_key_bindings(
                [_ip.pt_app.app.key_bindings, load_vi_bindings()]
            )
        else:
            more_keybindings = merge_key_bindings(
                [_ip.pt_app.app.key_bindings, load_key_bindings()]
            )

    # _ip.pt_app.app.key_bindings = more_keybindings
    # _ip.pt_app.app.key_bindings._update_cache()
