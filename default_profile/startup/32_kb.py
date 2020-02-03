#!/usr/bin/env python3
"""Effectively me rewriting Prompt Toolkits keybindings handlers.

Summary
-------
Make prompt_toolkit's keybindings more extensible.

Reminder of where you left off:

Bottom toolbar works but isn't bound to a key idk why it isn't working.
The seemingly recommended interface is to merge with merge_key_bindings
Difficult to add key_bindings after the merge though.
Mostly everything's behaving as it should however.

I'm just gonna note how much this bugs me though.::

    In [30]: p = PromptSessionKB()
    Out[30]: <PromptSessionKB>: 13

    In [31]: a = ApplicationKB()
    Out[31]: <ApplicationKB>: 24

Alright now I need to start keeping track because this is rough.::

    In [1]: _ip.pt_app.app  # Application. _ip.pt_app is the PromptSession.
    Out[1]: <prompt_toolkit.application.application.Application at 0x7f2710ac7d90>


    In [9]: _ip.pt_app.current_buffer
    AttributeError: 'PromptSession' object has no attribute 'current_buffer'

    In [2]: _ip.pt_app.app.current_buffer
    Out[2]: <Buffer(name='DEFAULT_BUFFER', text='_ip.pt_app.a...') at 139805760009696>

    In [3]: _ip.pt_app.validator

    In [4]: _ip.pt_app.app.validator
    AttributeError: 'Application' object has no attribute 'validator'

Alright so they're not the similar after all right?
From the docs.:

    Dynamically switch between Emacs and Vi mode

    The Application has an editing_mode attribute.
    We can change the key bindings by changing this attribute from
    EditingMode.VI to EditingMode.EMACS.

Guess what else has an editing_mode attribute.::

    In [5]: _ip.pt_app.editing_mode
    Out[5]: <EditingMode.VI: 'VI'>

    In [6]: _ip.pt_app.app.editing_mode
    Out[6]: <EditingMode.VI: 'VI'>


Dude mergedkeybindings are horrible.::

    In [30]: _ip.pt_app.app.key_bindings
    Out[30]: <prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f271047f340>

    In [31]: _ip.pt_app.app.key_bindings.registries
    Out[31]:
    [<prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac7b50>,
    <prompt_toolkit.key_binding.key_bindings.ConditionalKeyBindings at 0x7f2710447430>]

    In [32]: _ip.pt_app.app.key_bindings.registries[0]
    Out[32]: <prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac7b50>

    In [33]: _ip.pt_app.app.key_bindings.registries[0].registries
    Out[33]:
    [<prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac77f0>,
    <prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings at 0x7f2710ac79a0>]

    In [34]: _ip.pt_app.app.key_bindings.registries[0].registries[0]
    Out[34]: <prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac77f0>

    In [35]: _ip.pt_app.app.key_bindings.registries[0].registries[0].registries[0]
    Out[35]: <prompt_toolkit.key_binding.key_bindings.KeyBindings at 0x7f2710ac3160>

    In [36]: _ip.pt_app.app.key_bindings.registries[0].registries[0].registries[0].bindings
    Out[36]:
    [Binding(keys=(<Keys.Right: 'right'>,), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadd30>),
    Binding(keys=(<Keys.ControlE: 'c-e'>,), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadd30>),
    Binding(keys=(<Keys.ControlF: 'c-f'>,), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadd30>),
    Binding(keys=(<Keys.Escape: 'escape'>, 'f'), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadc10>)]

And you kinda can't do anything about it.::

    In [39]: did_we_make_it_better = DynamicKeyBindings(_ip.pt_app.app.key_bindings)
    Out[39]: <prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings at 0x7f26f7d9ba30>

    In [40]: did_we_make_it_better.bindings
    TypeError: '_MergedKeyBindings' object is not callable

Can't extract anything from them.::

    In [42]: for i in load_key_bindings().registries[0].bindings:
        ...:     _ip.pt_app.key_bindings.add(i.keys)(i.handler)
        ...: ValueError: Invalid key: (<Keys.ControlX: 'c-x'>, 'r', 'y')

Gotta be honest I felt very creative workibg ny way up to that one.
If we can't do that, lets keep working at the individual bindings.::

    In [43]: i.keys
    Out[43]: (<Keys.ControlX: 'c-x'>, 'r', 'y')
    In [44]: type(i.keys)
    Out[44]: tuple
    In [45]: i.keys[0]
    Out[45]: <Keys.ControlX: 'c-x'>

So far so good?::

    In [57]: c = ""
    ...: for j in i.keys:
    ...:     c += Keys(j)
    ...: ValueError: 'r' is not a valid Keys
        During handling of the above exception, another exception occurred:
        ValueError: 'r' is not a valid Keys

Yup. We have to redefine what a key is.


Fun with Vim
------------

Dude these are all the vi modes prompt_toolkit has...lol
So I just checked. Wanna know what it does?
They're basically enums that get compared to editing_mode.input_mode. lol kinda dumb right.::

    from prompt_toolkit.filters.app import (
        vi_selection_mode,
        vi_recording_macro,
        vi_register_names,
        vi_mode,
        vi_replace_mode,
        vi_waiting_for_text_object_mode,
        vi_insert_mode,
        vi_search_direction_reversed,
        vi_navigation_mode,
        vi_digraph_mode,
        vi_insert_multiple_mode,
    )


"""
import logging
import reprlib
from typing import Callable, Optional
import warnings

from IPython.core.getipython import get_ipython

import prompt_toolkit
from prompt_toolkit.application.current import get_app
from prompt_toolkit.cache import SimpleCache
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding.defaults import load_key_bindings, load_vi_bindings
from prompt_toolkit.key_binding.key_bindings import (
    KeyBindings,
    KeyBindingsBase,
    _MergedKeyBindings,
    merge_key_bindings,
)

# from prompt_toolkit.key_binding.key_processor import KeyPress
from prompt_toolkit.keys import Keys


class KeyBindingsManager(KeyBindingsBase):
    """Bind an interface with IPython's keybindings and define dunders so this behaves properly.

    I think that I'm going to continue this by making a subclass that validates the bindings it's being given
    because you can add the same keybinding over and over and that's probably
    never what the user wants to have happen.

    In order to properly take over the keybindings class we're given,
    I'm assuming wed need to implement the methods provided by the class
    KeyBindingsBase.

    *Fun fact:* This used to be a class in prompt_toolkit!

    Copy pasted it below.

    .. todo::
        ``__getitem__`` so we have a properly constructed sequence.
        Jan 03, 2020: Done! Just ensure everything works upon usage.

    """

    def __init__(self, kb=None, shell=None, **kwargs):
        """Initialize the class.

        Parameters
        ----------
        kb : KeyBindings
            Any KeyBindings you wanna throw us right off the bat.
            Handling this is gonna be hard unfortunately.
        """
        self.shell = shell or get_ipython()
        if self.shell is not None:
            if kb is None:
                if hasattr(self.shell, "pt_app"):
                    self.kb = self.shell.pt_app.app.key_bindings
                elif hasattr(ip, "pt_cli"):
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
        """
        .. admonition:: From pydoc.help('SPECIALMETHODS')

            object.__bool__(self)
                Called to implement truth value testing and the built-in operation
                "bool()"; should return "False" or "True".  When this method is not
                defined, "__len__()" is called, if it is defined, and the object is
                considered true if its result is nonzero.  If a class defines
                neither "__len__()" nor "__bool__()", all its instances are
                considered true.

        """
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

    # def __index__(self):

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
        return self.kb.bindings[index]

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

    .. todo:: Unpacking the KeyBindings registry attribute.
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

    def __init__(self, kb=None, shell=None, *args, **kwargs):
        """Honestly can't say I have a great grasp on proper initialization
        of subclasses with both class attributes and __init__'s.
        """
        super().__init__(kb=kb, shell=shell, *args, **kwargs)


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


def safely_get_registry(_ip):
    if _ip is not None:
        if hasattr(_ip, "pt_app"):
            registry = _ip.pt_app.app.key_bindings
            # todo
            # if type(registry) == _MergedKeyBindings:
            #     unnest_merged_kb(registry)


def kb_main(_ip=None):


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