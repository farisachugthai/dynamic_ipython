"""Basically a no-op because IPython keeps raising errors."""
from IPython.core.getipython import get_ipython
from IPython.extensions.storemagic import StoreMagics


class StoreAndLoadMagics(StoreMagics):
    """I keep getting an error about this."""
    def __init__(self, shell=None, *args, **kwargs):
        """TODO: Docstring for function."""
        super().__init__(self, *args, **kwargs)
        self.shell = shell or get_ipython()

    def load_ext(self):
        self.shell.register_magics(self)

    # Load the extension in IPython.
    def register_magic(self, ip):
        """Are you allowed to do this?"""
        ip.register_magics(self)
