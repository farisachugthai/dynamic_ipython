"""Configure prompt_toolkit effectively within a running IPython instance.

Summary
-------
Provides utilities functions and classes to work with both prompt_toolkit
and IPython.

The `Helpers` class gives a useful reference as to the relationship between
a number of the intertwined classes in a running `PromptSession`.

Notes
-----
Of use might be.:

    get_ipython().pt_app.layout

An object that contains the default_buffer, `DEFAULT_BUFFER`, a reference
to a container `HSplit` and a few other things possibly worth exploring.

"""
from prompt_toolkit import search
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.keys import Keys

from IPython.core.getipython import get_ipython

DEDENT_TOKENS = frozenset(["raise", "return", "pass", "break", "continue"])


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app


class Helpers:

    def __init__(self):
        self.shell = get_ipython()
        self.app()

    @property
    def is_running(self):
        pass

    def __repr__(self):
        return f"{self.pt_app}"

    def app(self):
        self._app = get_app()

    @property
    def pt_app(self):
        return self.shell.pt_app.app

    @property
    def session(self):
        return self.shell.pt_app

    @property
    def pt_app_kb(self):
        """Application instance keybindings.

        NOT the same as 'session_kb'.

        In [103]: pt.pt_app_kb == pt.session_kb
        Out[103]: False
        """
        return self.pt_app.key_bindings

    @property
    def session_kb(self):
        return self.session.key_bindings

    @property
    def app_layout(self):
        """The same as session_layout *thank god*.

        In [102]: pt.app_layout == pt.session_layout
        Out[102]: True
        """
        return self.pt_app.layout

    @property
    def session_layout(self):
        return self.pt_app.layout

    @property
    def layout(self):
        self.app_layout

    @property
    def pt_app_style(self):
        """Of course it's not the same as the session_style.

        In [108]: pt.pt_app.style
        Out[108]: <prompt_toolkit.styles.base.DynamicStyle at 0x7f164da54f40>

        In [109]: pt.session.style
        Out[109]: <prompt_toolkit.styles.base.DynamicStyle at 0x7f1658a90a30>
        """
        return self.pt_app.style

    @property
    def session_style(self):
        return self.session.style

    @property
    def buffer(self):
        return self.layout.current_buffer

    @property
    def document(self):
        return self.buffer.document


if __name__ == "__main__":
    pt = Helpers()
