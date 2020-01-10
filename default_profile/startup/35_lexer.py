from traitlets.config import LoggingConfigurable
from traitlets.traitlets import Instance
from pygments.lexer import Lexer

from prompt_toolkit.lexers.pygments import PygmentsLexer

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShellABC


class IPythonConfigurableLexer(LoggingConfigurable):
    """ TODO: The IPythonPTLexer also should have a few of these attributes as well.

    And here's how you join the bridge.

    class PygmentsLexer(Lexer):

        Lexer that calls a pygments lexer.

        Example::

            from pygments.lexers.html import HtmlLexer
            lexer = PygmentsLexer(HtmlLexer)

        Note: Don't forget to also load a Pygments compatible style. E.g.::

            from prompt_toolkit.styles.from_pygments import style_from_pygments_cls
            from pygments.styles import get_style_by_name
            style = style_from_pygments_cls(get_style_by_name('monokai'))

        :param pygments_lexer_cls: A `Lexer` from Pygments.
        :param sync_from_start: Start lexing at the start of the document. This
            will always give the best results, but it will be slow for bigger
            documents. (When the last part of the document is display, then the
            whole document will be lexed by Pygments on every key stroke.) It is
            recommended to disable this for inputs that are expected to be more
            than 1,000 lines.
        :param syntax_sync: `SyntaxSync` object.
    """

    shell = Instance(InteractiveShellABC, allow_none=True)

    lexer = Instance(Lexer, help="Instance that lexs documents.", allow_none=True).tag(
        config=True
    )

    # from pygments.lexer.Lexer
    #: Name of the lexer
    name = None

    #: Shortcuts for the lexer
    aliases = []

    #: File name globs
    filenames = []

    #: Secondary file name globs
    alias_filenames = []

    #: MIME types
    mimetypes = []

    #: Priority, should multiple lexers match and no content is provided
    priority = 0

    def __init__(self, shell=None, original_lexer=None, **kwargs):
        super().__init__(**kwargs)
        self.shell = shell
        if self.shell is not None:
            self.original_lexer = self.shell.pt_app.lexer
        else:
            self.original_lexer = None


if __name__ == "__main__":
    lexer = IPythonConfigurableLexer()
    # TODO: isn't there a method like _ip.add_trait or something?
