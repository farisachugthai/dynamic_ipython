import reprlib

from IPython import get_ipython
from IPython.core.alias import AliasManager
from IPython.core.interactiveshell import InteractiveShellABC


class DynamicAliasManager(AliasManager):
    """Doesn't currently display info the way I want but it's a start."""

    shell = InteractiveShellABC()

    def __init__(self, ip=None, **kwargs):
        self.ip = ip if ip else get_ipython()
        super().__init__(shell=self.ip, **kwargs)
        self.init_aliases()

    def __repr__(self):
        return "".format(reprlib.repr(self.aliases))

    def __iter__(self):
        return iter(self.aliases)

    # def __call__(self):
    #     return self.init_aliases()


if __name__ == "__main__":
    # Forgive me for all these terrible hacks
    shell = get_ipython()
    shell.run_line_magic("alias_magic", "p pycat")
