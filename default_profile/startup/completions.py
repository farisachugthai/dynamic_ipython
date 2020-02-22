"""Use both Jedi and prompt_toolkit to aide IPython out."""
import abc
import keyword
import logging
from pathlib import Path
import re
import runpy
from types import MethodType
from typing import Iterable, TYPE_CHECKING

import jedi
from jedi import Script
from jedi.api import replstartup
from jedi.api.project import get_default_project
from jedi.utils import setup_readline
from jedi.api.environment import (
    get_cached_default_environment,
    find_virtualenvs,
    InvalidPythonEnvironment,
)

from IPython.core.getipython import get_ipython

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import (
    Completer,
    CompleteEvent,
    Completion,
    PathCompleter,
    ThreadedCompleter,
    WordCompleter,
)
from prompt_toolkit.completion.base import DynamicCompleter
from prompt_toolkit.completion.filesystem import ExecutableCompleter
from prompt_toolkit.completion.fuzzy_completer import FuzzyWordCompleter, FuzzyCompleter
from prompt_toolkit.document import Document

from prompt_toolkit.key_binding import merge_key_bindings

from traitlets.traitlets import Instance
from traitlets.config import LoggingConfigurable


class SimpleCompleter(Completer, abc.ABC):
    @abc.abstractproperty
    def document(self):
        # does it make sense to create these 2 as abstract properties?
        raise

    @abc.abstractmethod
    def get_completions(self, doc=None, complete_event=None, **kwargs):
        raise

    @abc.abstractmethod
    def __call__(self, document, event):
        return self.get_completions(doc=document, complete_event=event)


class SimpleCompletions(SimpleCompleter):
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

    def __repr__(self):
        return f"{self.__class__.__name__}>"

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

    def __repr__(self):
        return f"{self.__class__.__name__}>"

    def __call__(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        self.get_completions(doc=document, complete_event=complete_event)


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

    _ip = get_ipython()
    # Here's a different way to break it
    if _ip.editing_mode == "vi":
        more_keybindings = merge_key_bindings(
            [_ip.pt_app.app.key_bindings, load_vi_bindings()]
        )
    else:
        more_keybindings = merge_key_bindings(
            [_ip.pt_app.app.key_bindings, load_key_bindings()]
        )

    _ip.pt_app.app.key_bindings = more_keybindings
    _ip.pt_app.app.key_bindings._update_cache()


def venvs():
    """Use `jedi.api.find_virtualenvs` and return all values."""
    return [i for i in find_virtualenvs()]


class CustomCompleter(Completer):
    """A completer that attempts to meet prompt_toolkits API as generically as possible."""

    def __repr__(self):
        return f"{self.__class__.__name__}>"

    def __call__(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        self.get_completions(doc=document, complete_event=complete_event)

    def get_completions(self, document, complete_event):
        global options
        method_dict = get_options()
        word = document.get_word_before_cursor()

        methods = list(method_dict.items())

        selected = document.text.split()
        if len(selected) > 0:
            selected = selected[-1]
            if not selected.startswith("--"):
                current = method_dict.get(selected)
                if current is not None:
                    has_options = method_dict.get(selected)["options"]
                    if has_options is not None:
                        options = [
                            ("--{}".format(o["flag"]), {"meta": o["meta"]})
                            for o in has_options
                        ]
                        methods = options + methods
            else:
                methods = options

        for m in methods:
            method_name, flag = m
            if method_name.startswith(word):
                meta = (
                    flag["meta"] if isinstance(flag, dict) and flag.get("meta") else ""
                )
                yield Completion(
                    method_name, start_position=-len(word), display_meta=meta,
                )


class MergedCompleter(Completer):
    """Combine several completers into one."""

    def __init__(self, completers):
        """His `_MergedCompleter` class without the asserts."""
        self.completers = completers

    def get_completions(self, document, complete_event):
        # Get all completions from the other completers in a blocking way.
        for completer in self.completers:
            for c in completer.get_completions(document, complete_event):
                yield c

    def get_completions_async(self, document, complete_event):
        # Get all completions from the other completers in a blocking way.
        for completer in self.completers:
            # Consume async generator -> item can be `AsyncGeneratorItem` or
            # `Future`.
            for item in completer.get_completions_async(document, complete_event):
                yield item


class FuzzyCallable(FuzzyCompleter):
    def __init__(self, completer=None, words=None, meta_dict=None, WORD=False):
        """The exact code for FuzzyWordCompleter...except callable."""
        # assert callable(words) or all(isinstance(w, string_types) for w in words)
        self.words = words
        if self.words is None:
            self.words = keyword.kwlist
        self.meta_dict = meta_dict or {}
        self.WORD = WORD

        self.word_completer = WordCompleter(words=lambda: self.words, WORD=self.WORD)

        self.fuzzy_completer = FuzzyCompleter(self.word_completer, WORD=self.WORD)

        self.completer = self.fuzzy_completer
        super().__init__(completer=self.completer)

    def get_completions(self, document, complete_event):
        return self.fuzzy_completer.get_completions(document, complete_event)

    def __call__(self, document, complete_event):
        return self.get_completions(document, complete_event)


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
        # alternatively to set_custom_completer, can i skip the types.methodtype part and just do:
        # _ip.Completer.matchers.append(FuzzyCompleter(CustomCompleter))
        # seems to be working
        # So let's see how far we can chain these
        fuzzy_completer = FuzzyCallable(ExecutableCompleter())
        merged_completer = MergedCompleter(fuzzy_completer)

        _ip.Completer.matchers.append(merged_completer)

        threaded = ThreadedCompleter(get_word_completer())
        _ip.set_custom_completer(get_path_completer())
        _ip.set_custom_completer(get_fuzzy_keyword_completer)
        _ip.pt_app.auto_suggest = AutoSuggestFromHistory()

        current_document = _ip.pt_app.default_buffer.document
        script = Script(current_document.text, environment=environment)