"""Configure prompt_toolkit effectively within a running IPython instance.

Summary
-------
Provides utilities functions and classes to work with both `prompt_toolkit`
and `IPython`. The APIs of both libraries can be individually quite
overwhelming, and the combination and interaction of the 2 can prove difficult
to stay on top of.

The `Helpers` class defined here gives a useful reference as to the
relationship between a number of the intertwined classes in a running
`PromptSession`.

Notes
-----
Of use might be.:

    get_ipython().pt_app.layout

An object that contains the default_buffer, `DEFAULT_BUFFER`, a reference
to a container `HSplit` and a few other things possibly worth exploring.

"""
from reprlib import repr
from prompt_toolkit.keys import Keys

from IPython.core.getipython import get_ipython

DEDENT_TOKENS = frozenset(["raise", "return", "pass", "break", "continue"])


def get_app():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app.app


def get_session():
    """A patch to cover up the fact that get_app() returns a DummyApplication."""
    if get_ipython() is not None:
        return get_ipython().pt_app


class Helpers:
    def __init__(self):
        self.shell = get_ipython()
        self.pt_app = get_app()
        self.session = get_session()

    def __repr__(self):
        return f"{self.__class__.__name__} with app at {self.pt_app}"

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
        return self.session.layout

    @property
    def layout(self):
        return self.app_layout

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
    def current_buffer(self):
        return self.layout.current_buffer

    @property
    def current_container(self):
        """Return the HSplit defining the layout of the app."""
        return self.layout.container

    @property
    def current_container_children(self):
        """Return a list of the current container children.

        I genuinely don't think I expected it to be so big.
        """
        return self.current_container.children

    @property
    def current_control(self):
        """Return IPython's buffer control."""
        return self.layout.current_control

    @property
    def current_document(self):
        return self.current_buffer.document

    @property
    def current_buffer_texts(self):
        """Return the 'text' attr of the current buffer as a string."""
        return self.current_buffer.text

    @property
    def current_document_text(self):
        """Return the 'lines' attr of the current document as a list."""
        return self.current_document.lines

    @property
    def current_window(self):
        return self.layout.current_window

    @property
    def current_content(self):
        """The 'content' attribute of a `Window` returns a UIControl instance.

        In this specific case, it returns a BufferControl.
        """
        return self.current_window.content

    @property
    def content_is_control(self):
        """Is the `Window` content the control returned by the layout?"""
        return self.current_content is self.current_control

    def session_validator(self):
        return self.session.validator

    def app_validator(self):
        return self.pt_app

    def validate_validators(self):
        # who watches the watchmen?
        print(isinstance(session_validator, prompt_toolkit.validator.Validator))
        return self.app_validator is self.session_validator


if __name__ == "__main__":
    pt = Helpers()
