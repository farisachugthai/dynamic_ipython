import logging
import reprlib
from typing import Callable, Optional

from prompt_toolkit.application.dummy import DummyApplication
from prompt_toolkit.enums import DEFAULT_BUFFER, SEARCH_BUFFER
from prompt_toolkit.application.current import get_app

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

    def __init__(self, kb=None, shell=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
