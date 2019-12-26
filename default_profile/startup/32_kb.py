import logging
import reprlib
from typing import Callable, Optional

from prompt_toolkit.application.dummy import DummyApplication
from prompt_toolkit.enums import DEFAULT_BUFFER, SEARCH_BUFFER
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_vi_bindings

# Dude these are all the vi modes prompt_toolkit has...lol
from prompt_toolkit.key_binding.bindings.vi import(
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

from IPython.core.getipython import get_ipython
from IPython.terminal.shortcuts import create_ipython_shortcuts
from IPython.utils.text import SList

kb_logger = logging.getLogger(name=__name__)


class VerbosePrompt:
    """Because I can't ever remember how these classes resolve."""

    def __init__(self) -> None:
        self.shell = get_ipython()
        if getattr(self.shell, "pt_app", None):
            self.app = self.shell.pt_app
            self.buffer = self.shell.pt_app.buffer
            self.document = self.shell.pt_app.buffer.document
        else:  # well let's check at least
            self.app = get_app()
            if self.app is not None:
                # ah shit what if it's a dummy app
                if isinstance(self.app, DummyApplication):
                    self.app = None
            else:
                kb_logger.error("IPython was none but prompt toolkit returned an app.")

    def __repr__(self):
        return "{}".format(i for i in dir(self) if not i.startswith("_"))


class ContainerKeyBindings:
    """Originally this was gonna subclass SList but I wrote like 6 dunders
    in one shot so I realized it wouldn't be a good idea."""

    def __init__(self, kb=None, shell=None):
        self.shell = shell or get_ipython()
        if self.shell is not None:
            self.kb = kb or self.shell.pt_app.app.key_binding
            if self.kb is None:
                self.kb = create_ipython_shortcuts()

    def __repr__(self):
        return "<{}>: {}".format(self.__class__.__name__, len(self.kb.bindings))

    def __add__(self, another_one):
        self.kb.add_binding(another_one)

    def __iadd__(self, another_one):
        return self.__add__(another_one)

    def __len__(self):
        return len(self.kb.bindings)

    def __str__(self):
        return reprlib.Repr().repr_list(self.kb.bindings)

    def __call__(self):
        """Doesn't do anything important."""
        return self.__str__()

    # def __index__(self):


if __name__ == "__main__":

    _ip = get_ipython()
    if _ip is not None:
        # Does this do anything? Need to revisit how these work and what the
        # difference between _ip.pt_app and _ip.pt_app.app are
        # _ip.pt_app.key_bindings.bindings.extend(load_basic_bindings().bindings)
        # Sweet i might have just broken how pt handles keypresses

        # Also let's make an instance of this class
        container_kb = ContainerKeyBindings(shell=_ip, kb=_ip.pt_app.key_bindings.bindings)
        # Dude holy shit does this give you a lot
        if _ip.editing_mode == 'vi':
            more_keybindings = merge_key_bindings([_ip.pt_app.app.key_bindings, load_vi_bindings()])
            _ip.pt_app.app.key_bindings = more_keybindings
