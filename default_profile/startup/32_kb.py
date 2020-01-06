"""Make prompt_toolkit's keybindings more extensible.

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


"""
import logging
import reprlib
from typing import Callable, Optional

from prompt_toolkit.application.dummy import DummyApplication
from prompt_toolkit.cache import SimpleCache
from prompt_toolkit.enums import DEFAULT_BUFFER, SEARCH_BUFFER
from prompt_toolkit.filters import Condition

from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_vi_bindings, load_key_bindings
from prompt_toolkit.key_binding.key_bindings import _MergedKeyBindings, KeyBindings, KeyBindingsBase

from prompt_toolkit.key_binding.bindings.vi import (
    load_vi_bindings,
    load_vi_search_bindings
)

# Dude these are all the vi modes prompt_toolkit has...lol
# So I just checked. Wanna know what it does? They're basically enums that get compared to editing_mode.input_mode. lol kinda dumb right.
# from prompt_toolkit.filters.app import (
#     vi_selection_mode,
#     vi_recording_macro,
#     vi_register_names,
#     vi_mode,
#     vi_replace_mode,
#     vi_waiting_for_text_object_mode,
#     vi_insert_mode,
#     vi_search_direction_reversed,
#     vi_navigation_mode,
#     vi_digraph_mode,
#     vi_insert_multiple_mode,
# )

from IPython.core.getipython import get_ipython

kb_logger = logging.getLogger(name=__name__)


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

    def __init__(self, kb=None, shell=None):
        self.shell = shell or get_ipython()
        if self.shell is not None:
            self.kb = kb or self.shell.pt_app.app.key_bindings
            if self.kb is None:
                self.kb = load_key_bindings()
        # idk what this is but pt requires it
        self._get_bindings_for_keys_cache = SimpleCache(maxsize=10000)
        self._get_bindings_starting_with_keys_cache = SimpleCache(maxsize=1000)
        self.__version = 0  # For cache invalidation.
        super().__init__()

    def __repr__(self):
        return "<{}>: {}".format(self.__class__.__name__,
                                 len(self.kb.bindings))

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

    @property
    def len(self):
        return self.__len__()

    def __str__(self, level=6):
        return reprlib.Repr().repr_list(self.kb.bindings, level)

    def __call__(self):
        """Doesn't do anything important."""
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
        self._version = 0

    @_version.setter
    def _clear_cache(self):
        self._version += 1
        self._get_bindings_for_keys_cache.clear()
        self._get_bindings_starting_with_keys_cache.clear()

    def get_bindings_for_keys(self, keys):
        """
        Return a list of key bindings that can handle this key.
        (This return also inactive bindings, so the `filter` still has to be
        called, for checking it.)
        :param keys: tuple of keys.
        """
        def get():
            result = []
            for b in self.bindings:
                if len(keys) == len(b.keys):
                    match = True
                    any_count = 0

                    for i, j in zip(b.keys, keys):
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

    def __init__(self, kb=None, shell=None, *args, **kwargs):
        self.shell = shell or get_ipython()
        if self.shell is not None:
            self.kb = kb or self.shell.pt_app.key_bindings
            if self.kb is None:
                self.kb = load_key_bindings()
        super().__init__(kb=self.kb, shell=self.shell, *args, **kwargs)


def unpack(i):
    # raise NotImplementedError
    pass


class HandlesMergedKB(KeyBindingsManager):
    """It might be easier to handle the insufferable discrepencies in implementation
    between _MergedKeyBindings and ConditionalKeyBindings through class attributes.

    .. todo:: Unpacking the KeyBindings registry attribute.
    """

    shell = get_ipython()
    if shell is not None:
        kb = shell.pt_app.app.key_bindings
        if kb is None:
            kb = load_key_bindings()
        else:
            if isinstance(kb, _MergedKeyBindings):
                for i in kb.registries:
                    unpack(i)

    def __init__(self, kb=None, shell=None, *args, **kwargs):
        """Honestly can't say I have a great grasp on proper initialization
        of subclasses with both class attributes and __init__'s.
        """
        super().__init__(kb=kb, shell=shell, *args, **kwargs)


if __name__ == "__main__":

    _ip = get_ipython()
    if _ip is not None:
        container_kb = KeyBindingsManager(shell=_ip,
                                          kb=_ip.pt_app.key_bindings.bindings)
        # Dude holy shit does this give you a lot
        if _ip.editing_mode == "vi":
            more_keybindings = merge_key_bindings(
                [_ip.pt_app.app.key_bindings,
                 load_vi_bindings()])
        else:
            more_keybindings = merge_key_bindings(
                [_ip.pt_app.app.key_bindings,
            container_kb ])

        _ip.pt_app.app.key_bindings = container_kb
