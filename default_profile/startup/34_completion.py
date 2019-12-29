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


class SimpleWordCompletions:
    def __init__(self, shell=None):
        self.shell = shell or get_ipython()
        self._initialize_word_completer()

    @property
    def user_ns(self):
        return self.shell.user_ns

    def _initialize_word_completer(self, *args, **kwargs):
        if not args and not kwargs:
            self.word_completer = WordCompleter(
                self.user_ns, pattern=re.compile(r"^([a-zA-Z0-9_.]+|[^a-zA-Z0-9_.\s]+)")
            )
        # TODO: else:

    def get_document(self):
        """Is this how you do this?"""
        return self.shell.pt_app.app.current_buffer.document

    def get_completions(self, doc=None, complete_event=None, **kwargs):

        if doc is None:
            doc = self.get_document()
        yield WordCompleter.get_completions(
            document=doc, complete_event=CompleteEvent(), **kwargs
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
        get_ipython().set_custom_completer(SimpleWordCompletions)
        get_ipython().set_custom_completer(get_path_completer)
        get_ipython().set_custom_completer(get_keyword_completer)
