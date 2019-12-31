import abc
import keyword
import re

from IPython.core.getipython import get_ipython
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    PathCompleter,
    WordCompleter,
)

class SimpleCompleter(metaclass=abc.ABC):

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


class SimpleCompletions(SimpleCompleter):
    # Do you make super calls after subclassing ABC?

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
        yield WordCompleter.get_completions(
            document=doc, complete_event=complete_event, **kwargs
        )


def get_path_completer():
    """Basically took this from Jon's unit tests."""
    return PathCompleter(min_input_len=1, expanduser=True)


def get_keyword_completer():
    """Return all valid Python keywords."""
    return WordCompleter(
        keyword.kwlist, pattern=re.compile(r"^([a-zA-Z0-9_.]+|[^a-zA-Z0-9_.\s]+)")
    )


if __name__ == "__main__":
    if get_ipython() is not None:
        get_ipython().set_custom_completer(SimpleCompletions())
        get_ipython().set_custom_completer(get_path_completer())
        get_ipython().set_custom_completer(get_keyword_completer())
