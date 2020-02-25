#!/usr/bin/env python3
"""Effectively me rewriting Prompt Toolkits keybindings handlers."""
import logging
import operator
import reprlib
import warnings
from collections import UserList
from typing import Callable, Optional

from IPython.core.getipython import get_ipython

from prompt_toolkit.cache import SimpleCache
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import (
    # KeyBindingsBase,
    _MergedKeyBindings,
)

from prompt_toolkit.keys import Keys


class KeyBindingsManager(UserList):
    def __init__(self, kb=None, shell=None, **kwargs):
        """Initialize the class.

        Parameters
        ----------
        kb : `KeyBindings`
            Any KeyBindings you wanna throw us right off the bat.
            Handling this is gonna be hard unfortunately.

        """
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
        return self.__add__(another_one)

    def __len__(self):
        return len(self.kb.bindings)

    def len(self):
        return self.__len__()

    def __str__(self, level=6):
        return reprlib.Repr().repr_list(self.kb.bindings, level)

    def __repr_pretty(self, p, cycle):
        # I don't know why it has that call signature
        return (
            f"<{self.__class__.__name__}:> - {reprlib.recursive_repr(self.kb.bindings)}"
        )

    def __call__(self):
        """Simply calls the str method until we figure something out."""
        return self.__str__()

    def __iter__(self):
        """This file in general is gonna suck to test isn't it?"""
        try:
            for i in iter(self.kb.bindings):
                yield i
        except TypeError:
            raise  # uhm idk
        except StopIteration:
            pass

    def __getitem__(self, index):
        return operator.getitem(self.kb.bindings, index)

    @property
    def bindings(self):
        return self.kb.bindings

    @bindings.setter
    def call_iadd(self, other):
        self.__iadd__(other)

    @property
    def _version(self):
        return self.__version

    @_version.setter
    def _clear_cache(self):
        self._version += 1
        self._get_bindings_for_keys_cache.clear()
        self._get_bindings_starting_with_keys_cache.clear()

    def get_keys(self, keys):
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
                    result.append((any_count, b))

        # Place bindings that have more 'Any' occurrences in them at the end.
        result = sorted(result, key=lambda item: -item[0])

        return [item[1] for item in result]

    def get_bindings_for_keys(self, keys):
        """Return a list of key bindings that can handle this key.

        (This return also inactive bindings, so the `filter` still has to be
        called, for checking it.)
        :param keys: tuple of keys.
        """
        self.get(keys)
        return self._get_bindings_for_keys_cache.get(keys, get)

    def get_bindings_starting_with_keys(self, keys):
        """
        Return a list of key bindings that handle a key sequence starting with
        `keys`. (It does only return bindings for which the sequences are
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


class ApplicationKB(KeyBindingsManager):
    """Functionally the exact same thing except now we're bound to _ip.pt_app."""

    def __init__(self, kb=None, shell=None, **kwargs):
        self.shell = shell or get_ipython()
        if self.shell is not None:
            self.kb = kb or self.shell.pt_app.key_bindings
            if self.kb is None:
                self.kb = load_key_bindings()
        super().__init__(kb=self.kb, shell=self.shell, *args, **kwargs)


class HandlesMergedKB(KeyBindingsManager):
    """It might be easier to handle the insufferable discrepencies in implementation
    between _MergedKeyBindings and ConditionalKeyBindings through class attributes.

    .. todo::
        Unpacking the KeyBindings registry attribute.

    """

    shell = get_ipython()
    if shell is not None:
        if hasattr(shell, "pt_app"):
            kb = shell.pt_app.app.key_bindings
            if kb is None:
                kb = load_key_bindings()
            else:
                pass  # todo
                # if isinstance(kb, _MergedKeyBindings):
                #     for i in kb.registries:
                #         unpack(i)


def unnest_merged_kb(kb, pre_existing_list=None):
    if pre_existing_list:
        ret = pre_existing_list
    else:
        ret = []
    if type(kb) == _MergedKeyBindings:
        for i in kb.registries:
            ret.append(i)
        for i in ret:
            unnest_merged_kb(kb, pre_existing_list=ret)
    else:
        if ret:
            return ret
        else:
            return


def _rewritten_add(registry, _binding):
    key = _binding.keys
    filter = _binding.filter
    handler = _binding.handler
    registry.add(key, filter=filter)(handler)
    return registry


class Documented(Document):
    """I'll admit this subclass doesn't exist for much of a reason.

    However, it's a LOT easier to work with classes with their dunders defined.
    """

    def __len__(self):
        return self.cursor_position

    def __iter__(self):
        return iter(self.text)
