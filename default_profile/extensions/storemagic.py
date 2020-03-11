"""Basically a no-op because IPython keeps raising errors."""
import logging

from traitlets import Bool

from IPython.core.getipython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.extensions.storemagic import (
    StoreMagics,
    restore_data,
    restore_dhist,
    restore_aliases,
    refresh_variables,
)


@magics_class
class StoreAndLoadMagics(StoreMagics):
    """I keep getting an error about this."""

    # because you never registered this class

    autorestore = Bool(
        False,
        help="""If True, any %store-d variables will be automatically restored
        when IPython starts.
        """,
    ).tag(config=True)

    def __init__(self, shell=None):
        """TODO: Docstring for function."""
        self.shell = shell or get_ipython()
        if self.shell is None:
            logging.error("StoreAndLoadMagics: shell is None")
        super().__init__(self.shell)
        self.shell.configurables.append(self)
        if self.autorestore:
            restore_data(self.shell)

    def load_ext(self):
        self.shell.register_magics(self)

    @line_magic
    def store(self, *args):
        """Lightweight persistence for python variables.

        Example::

          In [1]: l = ['hello',10,'world']
          In [2]: %store l
          In [3]: exit

          (IPython session is closed and started again...)

          ville@badger:~$ ipython
          In [1]: l
          NameError: name 'l' is not defined
          In [2]: %store -r
          In [3]: l
          Out[3]: ['hello', 10, 'world']

        Usage:

        * ``%store``          - Show list of all variables and their current
                                values
        * ``%store spam bar`` - Store the *current* value of the variables spam
                                and bar to disk
        * ``%store -d spam``  - Remove the variable and its value from storage
        * ``%store -z``       - Remove all variables from storage
        * ``%store -r``       - Refresh all variables, aliases and directory history
                                from store (overwrite current vals)
        * ``%store -r spam bar`` - Refresh specified variables and aliases from store
                                   (delete current val)
        * ``%store foo >a.txt``  - Store value of foo to new file a.txt
        * ``%store foo >>a.txt`` - Append value of foo to file a.txt

        It should be noted that if you change the value of a variable, you
        need to %store it again if you want to persist the new value.

        Note also that the variables will need to be pickleable; most basic
        python types can be safely %store'd.

        Also aliases can be %store'd across sessions.
        To remove an alias from the storage, use the %unalias magic.
        """
        super().store(*args)


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(StoreMagics)
