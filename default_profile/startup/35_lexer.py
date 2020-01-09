from traitlets.config import LoggingConfigurable
from traitlets.traitlets import Instance
from pygments.lexer import Lexer

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShellABC


class IPythonConfigurableLexer(LoggingConfigurable):
    """ TODO: The IPythonPTLexer also should have a few of these attributes as well."""
    shell = Instance(InteractiveShellABC, allow_none=True)

    lexer = Instance(Lexer, help="Instance that lexs documents." allow_none=True).tag(config=True)

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

    def __init__(self, shell, original_lexer=None, **kwargs):
        super().__init__(**kwargs)
        self.shell = shell
        if self.shell is not None:
            self.original_lexer = self.shell.pt_app.lexer
        else:
            self.original_lexer = None


_ip = get_ipython()
