import abc
import keyword
import re
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Tuple, Union

from IPython.core.getipython import get_ipython
from prompt_toolkit.document import Document
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    PathCompleter,
    WordCompleter,
    merge_completers,
)
from prompt_toolkit.completion.fuzzy_completer import FuzzyWordCompleter


class SimpleCompleter(abc.ABC):
    @abc.abstractproperty
    def document(self):
        # does it make sense to create these 2 as abstract properties?
        raise

    @abc.abstractproperty
    def current_text(self):
        raise

    @abc.abstractmethod
    def get_completions(self, doc=None, complete_event=None, **kwargs):
        raise

    @abc.abstractmethod
    def _initialize_completer(self, *args, **kwargs):
        raise


class SimpleCompletions:
    # Do you make super calls after subclassing ABC?
    # shit do we have to mix something else in?

    def __init__(self, shell=None):
        self.shell = shell or get_ipython()
        self._initialize_completer()

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
    """OF COURSE ITS NOT CALLABLE."""
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
    return WordCompleter(keyword.kwlist, pattern=re.compile(r"^([a-zA-Z0-9_.]+|[^a-zA-Z0-9_.\s]+)")
    )


if __name__ == "__main__":
    if get_ipython() is not None:
        merge_completers([SimpleCompletions(), get_path_completer(), get_fuzzy_keyword_completer(),
                get_word_completer()])
