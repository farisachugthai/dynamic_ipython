#!/usr/bin/env python
# -*- coding: utf-8 -*-
import keyword
import re
from typing import Iterable, AsyncGenerator, Optional, Dict, List, Callable, Pattern, Union

import jedi
from jedi import Script
from jedi.api import replstartup  # noqa
from jedi.api.project import get_default_project
from jedi.api.environment import (
    get_cached_default_environment,
    find_virtualenvs,
    InvalidPythonEnvironment,
)

from IPython.core.getipython import get_ipython
from IPython.terminal.ptutils import IPythonPTCompleter

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory, ThreadedAutoSuggest
from prompt_toolkit.completion import CompleteEvent, ThreadedCompleter
from prompt_toolkit.completion.filesystem import ExecutableCompleter, PathCompleter
from prompt_toolkit.completion.base import Completion, Completer
from prompt_toolkit.completion.fuzzy_completer import FuzzyWordCompleter, FuzzyCompleter
from prompt_toolkit.completion.word_completer import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.eventloop import generator_to_async_generator
from prompt_toolkit.filters import FilterOrBool


class SimpleCompleter(Completer):
    """Building up a customized Completer using the prompt_toolkit API.

    Utilizes the *min_input_len* of the PathCompleter along with adding more
    necessary dunders and functionally useful fallbacks in case of being called
    incorrectly, rather adding dozens of assert statements.
    """

    def __init__(self, shell=None, completer=None, min_input_len=0, *args, **kwargs):
        self.shell = shell or get_ipython()
        self.completer = WordCompleter(
            self.user_ns, pattern=re.compile(r"^([a-zA-Z0-9_.]+|[^a-zA-Z0-9_.\s]+)")
        ) if completer is None else completer

        self.min_input_len = min_input_len

    @property
    def user_ns(self):
        if get_ipython() is None:
            return None
        return self.shell.user_ns

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}:> {self.completer}"

    @property
    def document(self):
        """Instance of `prompt_toolkit.document.Document`."""
        return self.shell.pt_app.app.current_buffer.document

    def get_completions(self, complete_event, doc=None):
        """For now lets not worry about CompleteEvent too much.

        But we will need to add a get_async_completions method.

        .. todo::
            Possibly alias this to `complete` for readline compat.

        """
        if doc is None:
            doc = self.document
        # Complete only when we have at least the minimal input length,
        # otherwise, we can too many results and autocompletion will become too
        # heavy.
        if len(doc.text) < self.min_input_len:
            return
        if not doc.current_line.strip():
            return
        yield self.completer.get_completions(
            document=doc, complete_event=complete_event
        )

    def __call__(
        self, document: Document, complete_event: CompleteEvent
    ) -> AsyncGenerator[Completion, None]:
        return self.get_completions_async(document, complete_event=complete_event)

    async def get_completions_async(
        self, document: Document, complete_event: CompleteEvent
    ) -> AsyncGenerator[Completion, None]:
        """Asynchronous generator of completions."""
        if not document.current_line.strip():
            return
        if len(document.text) < self.min_input_len:
            return
        async for completion in generator_to_async_generator(
            lambda: self.completer.get_completions(document, complete_event)
        ):
            yield completion


class PathCallable(PathCompleter):
    r"""PathCompleter with ``__call__`` defined.

    The superclass :class:`~prompt_toolkit.completion.PathCompleter` is
    initialized with a set of parameters, and 'expanduser' defaults to False.

    The 'expanduser' attribute is set to True in contrast with the
    superclass `PathCompleter`\'s default; however, that can be overridden
    in a subclass.
    """

    expanduser = True

    def __repr__(self):
        return f"{self.__class__.__name__}>"

    def __call__(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Call but note doc is positional not keyword arg as it is in CustomCompleter."""
        return self.get_completions(document, complete_event=complete_event)


def get_path_completer():
    """Basically took this from Jon's unit tests."""
    return PathCallable(min_input_len=1, expanduser=True)


def get_fuzzy_keyword_completer():
    """Return FuzzyWordCompleter initialized with all valid Python keywords."""
    return FuzzyWordCompleter(keyword.kwlist)


def get_word_completer():
    """Return WordCompleter initialized with all valid Python keywords."""
    return WordCompleter(
        keyword.kwlist, pattern=re.compile(r"^([a-zA-Z0-9_.]+|[^a-zA-Z0-9_.\s]+)")
    )


def venvs():
    """Use `jedi.api.find_virtualenvs` and return all values."""
    return [i for i in find_virtualenvs()]


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
        """Get all completions from `completers` in a non-blocking way.

        Checks that the completer actually defined this method before calling
        it so we don't force the method definition.
        """
        for completer in self.completers:
            # Consume async generator -> item can be `AsyncGeneratorItem` or
            # `Future`.
            # note i didnt define  it every time so we gotta checl
            if hasattr(completer, "get_completions_async"):
                for item in completer.get_completions_async(document, complete_event):
                    yield item

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.completers}"

    def __call__(self, document, complete_event):
        return self.get_completions_async(document, complete_event)


class FuzzyCallable(FuzzyWordCompleter):
    """A FuzzyCompleter with ``__call__`` defined."""

    def __init__(self,
                 WORD: Optional[bool] = False,
                 pattern: Optional[Pattern[str]] = None,
                 enable_fuzzy: Optional[FilterOrBool] = True,
                 meta_dict: Optional[Dict[str, str]] = None,
                 words: Optional[Union[List[str], Callable[[], List[str]]]] = None,
                 ignore_case: Optional[bool] = False,
                 sentence: Optional[bool] = False,
                 match_middle: Optional[bool] = False):
        """Mostly FuzzyWordCompleter...except callable.

        And the superclasses are initialized a little better.

        Parameters
        ----------
        :param completer: A :class:`~.Completer` instance.
        :param WORD: When True, use WORD characters.
        :param pattern: Regex pattern which selects the characters before the
            cursor that are considered for the fuzzy matching.
        :param enable_fuzzy: (bool or `Filter`) Enabled the fuzzy behavior. For
            easily turning fuzzyness on or off according to a certain condition.
        :param words: List of words or callable that returns a list of words.
        :param ignore_case: If True, case-insensitive completion.
        :param meta_dict: Optional dict mapping words to their meta-text. (This
            should map strings to strings or formatted text.)
        :param WORD: When True, use WORD characters.

        :param sentence: When True, don't complete by comparing the word before the
            cursor, but by comparing all the text before the cursor. In this case,
            the list of words is just a list of strings, where each string can
            contain spaces. (Can not be used together with the WORD option.)

        :param match_middle: When True, match not only the start, but also in the
            middle of the word.

        """
        self.words = keyword.kwlist if words is None else words
        self.WORD = WORD
        self.pattern = pattern
        self.enable_fuzzy = enable_fuzzy
        self.meta_dict = meta_dict if meta_dict is None else meta_dict
        # i dont get the lambda
        self.word_completer = WordCompleter(
            words=lambda: self.words,
            ignore_case=ignore_case,
            meta_dict=self.meta_dict,
            WORD=self.WORD,
            sentence=sentence,
            match_middle=match_middle,
            pattern=pattern,
        )
        self.fuzzy_completer = FuzzyCompleter(
            self.word_completer,
            pattern=pattern,
            WORD=self.WORD,
            enable_fuzzy=self.enable_fuzzy
        )
        self.completer = ThreadedCompleter(self.fuzzy_completer)
        super().__init__(self.completer)

    def get_completions(self, document, complete_event):
        return self.completer.get_completions(document, complete_event)

    def __call__(self, document, complete_event):
        return self.get_completions(document, complete_event)

    def __repr__(self):
        return f"<{self.__class__.__name__}>:"


def create_jedi_script():
    """Initialize a jedi.Script with the prompt_toolkit.default_buffer.document."""
    # TODO:
    _ip = get_ipython()
    # To set up Script or Interpreter later
    try:
        environment = get_cached_default_environment()
    except InvalidPythonEnvironment:
        print("Jedi couldn't get the default project.")
        return
    current_document = _ip.pt_app.default_buffer.document
    script = Script(current_document.text, environment=environment)
    return script


def create_pt_completers():
    """Return a combination of all the completers in this module.

    Still needs to factor in magic completions before its officially
    integrated into the rest of the app.
    """
    # No longer utilizes the set_custom_completer  method of IPython as that
    # requires the name of the completer's complete method.
    # Actually thats a great thing to allow to be specified. It allows for
    # readlines `complete` method and pt's get_completions to work togethwr!
    # Need to review their api tho.
    # alternatively to set_custom_completer, can i skip the types.methodtype part and just do:
    # _ip.Completer.matchers.append(FuzzyCompleter(CustomCompleter))
    # seems to be working
    # So let's see how far we can chain these
    fuzzy_completer = FuzzyCallable(ExecutableCompleter())
    list_of_completers = [
        fuzzy_completer,
        get_path_completer(),
        get_word_completer(),
        get_fuzzy_keyword_completer(),
        SimpleCompleter(),
    ]
    if get_ipython() is not None:
        list_of_completers.append(IPythonPTCompleter(get_ipython()))

    merged_completer = MergedCompleter(list_of_completers)
    threaded = ThreadedCompleter(merged_completer)
    return threaded


if __name__ == "__main__":
    jedi.settings.add_bracket_after_function = False
    jedi.settings.case_insensitive_completion = True
    default_project = get_default_project()
    combined_completers = create_pt_completers()

    session = get_ipython().pt_app if get_ipython() is not None else None
    if session is not None:
        # when using tmux or windows this is super helpful
        # yeah but otherwise destroys your ability to scroll backwards
        # session.refresh_interval = 0.5
        session.auto_suggest = ThreadedAutoSuggest(AutoSuggestFromHistory())
        # not there because no event loop but  we're so close
        # session.completer = combined_completers
