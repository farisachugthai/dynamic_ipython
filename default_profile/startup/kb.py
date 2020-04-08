#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Effectively me rewriting Prompt Toolkits keybindings handlers."""
import logging
import operator
import reprlib
from collections import UserList
import sys
from typing import Callable, Optional, Dict, TYPE_CHECKING, Any

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShell

from prompt_toolkit.cache import SimpleCache
from prompt_toolkit.document import Document
from prompt_toolkit.filters import ViInsertMode
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding import merge_key_bindings
from prompt_toolkit.key_binding.bindings.auto_suggest import load_auto_suggest_bindings
from prompt_toolkit.key_binding.bindings.vi import (
    load_vi_bindings,
    load_vi_search_bindings,
)
from prompt_toolkit.key_binding.key_bindings import KeyBindings, ConditionalKeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.keys import Keys

from default_profile.startup.ptoolkit import create_searching_keybindings, determine_which_pt_attribute

logging.basicConfig(level=logging.WARNING)


class KeyBindingsManager(UserList):
    """An object to make working with keybindings easier.

    Subclasses UserList with a list of Keys and their handlers.
    By defining dunders, the collection of keybindings are much
    easier to work with.
    """

    _get_bindings_for_keys_cache: SimpleCache[Any, Any]

    def __init__(
        self, kb: KeyBindings = None, shell: InteractiveShell = None, **kwargs
    ) -> Optional:
        """Initialize the class.

        Parameters
        ----------
        kb : `KeyBindings`
            Any KeyBindings you wanna throw us right off the bat.
            Handling this is gonna be hard unfortunately.
        kwargs : dict
            kwargs passed to UserList

        """
        super().__init__(**kwargs)
        self.shell = shell or get_ipython()
        if self.shell is not None:
            if kb is None:
                if hasattr(self.shell, "pt_app"):
                    self.kb = self.shell.pt_app.app.key_bindings
                elif hasattr(shell, "pt_cli"):
                    self.kb = self.shell.pt_cli.application.key_bindings_registry
                else:
                    self.kb = None
            else:
                self.kb = kb

        # So this should cover both IPython and pt aps that don't have self.shell set!
        if self.kb is None:
            self.kb = load_key_bindings()
        # idk what this is but pt requires it
        self._get_bindings_for_keys_cache = SimpleCache(maxsize=10000)
        self._get_bindings_starting_with_keys_cache = SimpleCache(maxsize=1000)
        self.__version = 0  # For cache invalidation.
        self.data = self.kb

    def __repr__(self):
        return "<{}>: {}".format(self.__class__.__name__, len(self.kb.bindings))

    def __add__(self, another_one):
        """Honestly not sure if this returns anything."""
        return self.kb.add_binding(another_one)

    def __iadd__(self, another_one):
        return self.__add__(another_one)

    def add(self, another_one):
        """Add another binding."""
        return self.__add__(another_one)

    def __len__(self):
        return len(self.kb.bindings)

    def len(self):
        return self.__len__()

    def __repr_pretty(self, p, cycle):
        # I don't know why it has that call signature
        return (
            f"<{self.__class__.__name__}:> - {reprlib.recursive_repr(self.kb.bindings)}"
        )

    def __getitem__(self, index):
        return operator.getitem(self.kb.bindings, index)

    @property
    def bindings(self):
        """Make the *kb* attributes bindings visible at the top level."""
        return self.kb.bindings

    @bindings.setter
    def call_iadd(self, other):
        self.__iadd__(other)

    @property
    def _version(self):
        """I think a tally that gets cleared when the list of handlers needs updating?"""
        return self.__version

    @_version.setter
    def _clear_cache(self):
        self._version += 1
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

    @_version.setter
    def _version(self, value):
        self.__version = value


class ApplicationKB(KeyBindingsManager):
    """Functionally the exact same thing except now we're bound to _ip.pt_app."""

    def __init__(self, kb=None, shell=None, **kwargs):
        self.shell = shell or get_ipython()
        if self.shell is not None:
            self.kb = kb or self.shell.pt_app.key_bindings
            if self.kb is None:
                self.kb = load_key_bindings()
        super().__init__(kb=self.kb, shell=self.shell)


class HandlesMergedKB(KeyBindingsManager):
    """It might be easier to handle the insufferable discrepencies in implementation
    between _MergedKeyBindings and ConditionalKeyBindings through class attributes.

    .. todo::
        Unpacking the KeyBindings registry attribute.

    """

    def __init__(
        self, kb: KeyBindings = None, shell: InteractiveShell = None, **kwargs
    ):
        if shell is None:
            shell = get_ipython()
        if shell is None:
            raise

        if hasattr(shell, "pt_app"):
            kb = shell.pt_app.app.key_bindings
            if kb is None:
                kb = load_key_bindings()
            else:
                pass  # todo
                # if isinstance(kb, _MergedKeyBindings):
                #     for i in kb.registries:
                #         unpack(i)


class Documented(Document):
    """I'll admit this subclass doesn't exist for much of a reason.

    However, it's a LOT easier to work with classes with their dunders defined.

    Implement the basics for a class to be considered a sequence IE len and iter.
    """

    def __len__(self):
        return self.cursor_position

    def __iter__(self):
        return iter(self.text)


def custom_keybindings() -> ConditionalKeyBindings:
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


def create_kb():
    # Honestly I'm wary to do this but let's go for it
    if get_ipython() is None:
        return
    pre_existing_keys = determine_which_pt_attribute()
    if pre_existing_keys is None:
        return
    all_kb = merge_key_bindings(
        [
            pre_existing_keys,
            load_vi_bindings(),
            load_vi_search_bindings(),
            load_auto_suggest_bindings(),  # these stopped getting added when i did this
            create_searching_keybindings(),
            custom_keybindings(),
        ]
    )
    return all_kb


def flatten_kb(merge):
    # noinspection PyProtectedMember
    logging.debug(merge._bindings2.bindings)
    # noinspection PyProtectedMember
    return merge._bindings2.bindings


if __name__ == "__main__":
    merged_kb = create_kb()
    if merged_kb is not None:
        kb_we_want = flatten_kb(merged_kb)
        current_kb = kb_we_want
