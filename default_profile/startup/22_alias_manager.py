import reprlib

from traitlets import List, Instance

from IPython.core.getipython import get_ipython
from IPython.core.alias import AliasManager, default_aliases, AliasError
from IPython.core.interactiveshell import InteractiveShellABC


class DynamicAliasManager(AliasManager):
    """Doesn't currently display info the way I want but it's a start."""

    # shell = InteractiveShellABC()

    def __init__(self, ip=None, user_aliases=None, **kwargs):
        self.ip = ip if ip else get_ipython()
        super().__init__(shell=self.ip, **kwargs)
        self.linemagics = self.shell.magics_manager.magics['line']
        self.user_aliases = user_aliases
        # yes thank god they defined teh defaults in 1 function.
        self.default_aliases = default_aliases()
        self.init_aliases()

    def init_aliases(self):
        """Override the superclasses init_aliases by not making weird edge cases for ls."""
        # Load default & user aliases
        for name, cmd in self.default_aliases + self.user_aliases:
            self.soft_define_alias(name, cmd)

    def __repr__(self):
        return "".format(reprlib.repr(self.aliases))

    def __iter__(self):
        try:
            return iter(self.aliases)
        except TypeError:
            raise

    def __add__(self, name=None, cmd=None, *args):
        """Allow name or cmd to not be specified. But if you pass non-kwargs please keep it in a tuple."""
        # I think i made this as flexible as possible. Cross your fingers.
        if name is None and cmd is None:
            if len(args) != 2:
                raise AliasError
            else:
                name, cmd = args
        self.define_alias(name, cmd)

    def undefine_alias(self, name):
        """Override to raise AliasError not ValueError."""
        if self.is_alias(name):
            del self.linemagics[name]
        else:
            raise AliasError('%s is not an alias' % name)


if __name__ == "__main__":
    # Forgive me for all these terrible hacks
    shell = get_ipython()
    shell.run_line_magic("alias_magic", "p pycat")
