#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Effectively me rewriting Prompt Toolkits keybindings handlers."""
import logging
# import operator
import reprlib
import sys
from functools import total_ordering
from typing import Optional, Any, Generator

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShell

from prompt_toolkit.cache import SimpleCache
from prompt_toolkit.document import Document
from prompt_toolkit.filters import ViInsertMode
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.bindings.auto_suggest import load_auto_suggest_bindings
from prompt_toolkit.key_binding.bindings.vi import (
    load_vi_bindings,
    load_vi_search_bindings,
)
from prompt_toolkit.key_binding.key_bindings import (
    KeyBindings, ConditionalKeyBindings, _MergedKeyBindings,
    Binding, KeyBindingsBase
)
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyPressEvent
from prompt_toolkit.keys import Keys

from default_profile.startup.ptoolkit import determine_which_pt_attribute

logging.basicConfig(level=logging.WARNING)


@total_ordering
class BindingPP(Binding):
    """Fix the prompt_toolkit binding.

    Allow them to compared, called, hashed or evaluated for truthiness.
    As *none* of this is originally available.

    .. todo:: __lt__ so we can sort

    """

    def __eq__(self, other):
        if not isinstance(other, Binding):
            return False
        return self.keys == other.keys and self.handler == other.handler

    def __lt__(self, other):
        if not isinstance(other, Binding):
            raise TypeError
        return self.keys.value < other.keys.value

    def __gt__(self, other):
        if not isinstance(other, Binding):
            raise TypeError
        return self.keys.value > other.keys.value

    def __hash__(self):
        # is this right? idk but the equal was!! we may soon stop getting
        # duplicates constantly
        return hash(self.keys, self.handler)

    def __bool__(self):
        return self.filter()

    def __call__(self, event: KeyPressEvent) -> None:
        return self.call(event)


def convert_bindings(bindings: Optional[KeyBindingsBase] = None) -> Generator[BindingPP]:
    if bindings is None:
        bindings = get_ipython().pt_app.app.key_bindings.bindings
    for b in bindings:
        yield BindingPP(b.keys, b.handler, filter=b.filter, eager=b.eager, is_global=b.is_global)


class KeyBindingsManager(KeyBindingsBase):
    """An object to make working with keybindings easier.

    Subclasses UserList with a list of Keys and their handlers.
    By defining dunders, the collection of keybindings are much
    easier to work with.
    """

    _get_bindings_for_keys_cache: SimpleCache[Any, Any]

    def __init__(
        self,
        kb: Optional[KeyBindings] = None,
        shell: Optional[InteractiveShell] = None,
        **kwargs,
    ):
        """Initialize the class.

        Parameters
        ----------
        kb  : `KeyBindings`, optional
            KeyBindings to initialize with.

        """
        self.shell = shell or get_ipython()
        self.init_kb(kb)
        # idk what this is but pt requires it
        self._get_bindings_for_keys_cache = SimpleCache(maxsize=10000)
        self._get_bindings_starting_with_keys_cache = SimpleCache(maxsize=1000)
        self.__version = 0  # For cache invalidation.
        self.data = self.kb
        if hasattr(self, 'pt_app'):
            self.pt_app = self.shell.pt_app
        elif hasattr(self, 'pt_cli'):
            self.pt_app = self.shell.pt_cli
        else:
            self.pt_app = None
        super().__init__()

    def __repr__(self):
        return f"<{self.__class__.__name__}>: Bindings {len(self.bindings)} KB: {len(self.kb.bindings)} "

    def __add__(self, another_one, *args):
        if isinstance(another_one, Binding):
            maybe_key = BindingPP(another_one)

            # Dont add duplicate keys!!
            if maybe_key in self:
                return
            elif another_one in self:
                return
            return self.bindings.append(maybe_key)
        return self.kb.add_binding(another_one)

    def __iadd__(self, another_one, *args):
        return self.__add__(another_one, *args)

    def __mul__(self):
        raise TypeError

    def add(self, another_one, *args):
        """Add another binding.

        Takes same parameters as `Binding` ``__init__``
        and **not** the same bindings as `KeyBindings.add`.
        """
        return self.__add__(another_one, *args)

    @property
    def kb(self):
        return self._kb

    @property
    def bindings(self):
        """Make the *kb* attributes bindings visible at the top level."""
        return self.kb.bindings

    @bindings.setter
    def bindings_setter(self, value):
        self.kb.bindings = value

    @bindings.deleter
    def bindings_deleter(self):
        del self.kb.bindings

    # @bindings.setter
    # def call_iadd(self, other):
    #     self.__iadd__(other)

    add_binding = add
    insert = add

    def __iter__(self):
        return iter(self.bindings)

    def __len__(self):
        return len(self.bindings)

    def len(self):
        return self.__len__()

    def __repr_pretty(self, p, cycle):
        # I don't know why it has that call signature
        return (
            f"<{self.__class__.__name__}:> - {reprlib.recursive_repr(self.kb.bindings)}"
        )

    def __getitem__(self, index):
        return self.bindings[index]

    # def __getslice__(self, index, step=1):
    #     return slice(self.bindings, index, step)

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise TypeError
        if isinstance(value, Binding):
            b = value
            value = BindingPP(b.keys, b.handler, filter=b.filter, eager=b.eager, is_global=b.is_global)
        self.bindings[index] = value

    def __delitem__(self, index):
        del self.bindings[index]

    def __slice__(self, index, stop=None, step=1):
        return slice(self.bindings, index, step)

    @property
    def _version(self):
        """I think a tally that gets cleared when the list of handlers needs updating?"""
        return self.__version

    @_version.setter
    def _set_cache(self, value=None):
        self._version = value if value is not None else self._version + 1
        self._get_bindings_for_keys_cache.clear()
        self._get_bindings_starting_with_keys_cache.clear()

    @_version.deleter
    def _clear_cache(self):
        self._get_bindings_for_keys_cache.clear()
        self._get_bindings_starting_with_keys_cache.clear()

    def get_keys(self, keys):
        """Return handlers for 'keys'.

        :param keys:
        :type keys:
        :return:
        :rtype:
        """
        try:
            len(keys)
        except AttributeError:
            return

        result = []
        # Dude don't define the vars inside the for loop
        # It's easier to segregate them at the top and then work with them
        any_count = 0
        for binding in self.bindings:
            if len(keys) == len(binding.keys):
                match = True
                for i, j in zip(binding.keys, keys):
                    if i != j and i != Keys.Any:
                        match = False
                        break

                    if i == Keys.Any:
                        any_count += 1

                if match:
                    result.append((any_count, binding))

        # Place bindings that have more 'Any' occurrences in them at the end.
        result = sorted(result, key=lambda item: -item[0])

        return [item[1] for item in result]

    def get_bindings_for_keys(self, keys):
        """Return a list of key bindings that can handle this key.

        (This return also inactive bindings, so the `filter` still has to be
        called, for checking it.)

        :param keys: tuple of keys.

        """
        return self._get_bindings_for_keys_cache.get(keys)

    def get_bindings_starting_with_keys(self, keys):
        """Return a list of key bindings that handle a sequence starting with `keys`.

        (It does only return bindings for which the sequences are
        longer than `keys`. And like `get_bindings_for_keys`, it also includes
        inactive bindings.)

        :param keys: tuple of keys.

        """

        def get():
            result = []
            for b in self.bindings:
                if len(keys) < len(b.keys):
                    match = True
                    for i, j in zip(b.keys, keys):
                        if i != j and i != Keys.Any:
                            match = False
                            break
                    if match:
                        result.append(b)
            return result

        return self._get_bindings_starting_with_keys_cache.get(keys, get)

    def __sizeof__(self):
        # Unfortunately I've added so much to this class that it might be necessary to check
        # how big ano object is now
        return object.__sizeof__(self) + sum(
            sys.getsizeof(v) for v in self.__dict__.values()
        )

    def get(self, keys):
        # TODO:
        pass

    def __dir__(self):  # wtf did i do that this isnt sorted anymore
        return sorted(dir(self))

    def __str__(self, level=500):
        return reprlib.Repr().repr_list(self.bindings, level)

    def init_kb(self, kb=None):
        if kb is None:
            if self.shell is not None:
                if hasattr(self.shell, "pt_app"):
                    self._kb = self.shell.pt_app.app.key_bindings
                elif hasattr(self.shell, "pt_cli"):
                    self._kb = self.shell.pt_cli.application.key_bindings_registry
                else:
                    self._kb = None
        else:
            if not isinstance(kb, "KeyBindingsBase"):
                raise TypeError
            self._kb = kb

        # So this should cover both IPython and pt aps that don't have self.shell set!
        if self.kb is None:
            self.kb = load_key_bindings()


class Documented(Document):
    """I'll admit this subclass doesn't exist for much of a reason.

    However, it's a LOT easier to work with classes with their dunders defined.

    Implement the basics for a class to be considered a sequence IE len and iter.
    """

    def __len__(self):
        return self.cursor_position

    def __iter__(self):
        return iter(self.text)


def create_vi_insert_keybindings() -> ConditionalKeyBindings:
    kb = KeyBindings()
    handle = kb.add

    # Add custom key binding for PDB.
    # holy hell this is genius. py3.7 just got breakpoint but this wouldve been a great addition to my ipy conf
    @handle(Keys.ControlB)
    def pdb_snippet(event):
        """Pressing Control-B will insert `pdb.set_trace`."""
        event.cli.current_buffer.insert_text("\nimport pdb; pdb.set_trace()\n")

    @handle(Keys.ControlE, Keys.ControlE)
    def exec_line(event):
        """Typing ControlE twice should also execute the current command. (Alternative for Meta-Enter.)"""
        b = event.current_buffer
        if b.accept_action.is_returnable:
            b.accept_action.validate_and_handle(event.cli, b)

    @handle("j", "j")
    def normal_mode(event):
        """Map 'jj' to Escape."""
        event.cli.input_processor.feed(KeyPress(Keys.Escape))

    # Custom key binding for some simple autocorrection while typing.
    # TODO: Observe how much this slows stuff down because if its a quick lookup then you could add your autocorrect.vim
    corrections = {
        "impotr": "import",
        "pritn": "print",
    }

    @handle(" ")
    def autocorrection(event):
        """When a space is pressed. Check & correct word before cursor."""
        b = event.cli.current_buffer
        w = b.document.get_word_before_cursor()

        if w is not None:
            if w in corrections:
                b.delete_before_cursor(count=len(w))
                b.insert_text(corrections[w])

        b.insert_text(" ")

    return ConditionalKeyBindings(kb, filter=ViInsertMode())


def create_kb() -> Optional[KeyBindings]:
    # Honestly I'm wary to do this but let's go for it
    if get_ipython() is None:
        return
    pre_existing_keys = determine_which_pt_attribute()
    if len(pre_existing_keys) == 0:
        print('pre_existing_keys is 0')
        return
    _all_kb = pre_existing_keys.extend([*load_vi_bindings().bindings,
                                        *load_vi_search_bindings().bindings,
                                        *load_auto_suggest_bindings().bindings,  # these stopped getting added when i did this
                                        # create_searching_keybindings().bindings,
                                        *create_vi_insert_keybindings().bindings,
                                        ])
    all_kb = KeyBindings()
    # we cant assign to bindings as its a property
    all_kb._bindings = _all_kb
    return all_kb


def flatten_kb():
    if hasattr(get_ipython().pt_app.app.key_bindings, '_bindings2'):
        # fucking _MergedKeyBindings
        get_ipython().pt_app.app.key_bindings = get_ipython().pt_app.app.key_bindings._bindings2
        logging.warning(len(get_ipython().pt_app.app.key_bindings.bindings))


if __name__ == "__main__":
    merged_kb = create_kb()

    if merged_kb is not None:

        # get_ipython().pt_app.app.key_bindings = merged_kb
        # _MergedKeyBindings doesnt have it holy fuck
        # get_ipython().pt_app.app.key_bindings._clear_cache()
        flatten_kb()
        # print(type(merged_kb))
        # print(dir(merged_kb))
    else:
        print('fuck')
