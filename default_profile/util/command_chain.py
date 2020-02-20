"""Redo the CommandChainDispatcher in IPython.core.hooks for more flexbility."""
from pprint import pprint
from reprlib import Repr
import sys

import IPython
from IPython.core.getipython import get_ipython
from traitlets.traitlets import Instance


class CommandChainDispatcherRepr(IPython.utils.ipstruct.Struct):
    """Subclass IPython's Struct to allow for more functionality.

    Methods
    -------
    Refer to the superclass for most methods.
    Simply, all I've done here is to remove the double underscore from most
    methods to improve visibility.

    """

    # .. todo:: collection.ChainMap?

    shell = Instance("IPython.core.interactiveshell.InteractiveshellABC")

    def __init__(self, shell=None, chain=None, level=6, *args, **kwargs):
        """Initialize the class.

        Parameters
        ----------
        shell : :class:`~IPython.core.interactiveshell.InteractiveShell`
            IPython instance.
        chain : dict
            IPython hooks.
        level : int
            Passed to `reprlib.Repr` for processing visual representation.
        """
        super().__init__(*args, **kwargs)
        self.shell = shell or get_ipython()

        # self.chain might work really well as a queue.PriorityQueue
        if self.shell is not None:
            self.chain = self.shell.hooks
        else:
            self.chain = chain or {}

        self.level = level

    def __repr__(self):
        return Repr().repr(self.chain, level=self.level)

    def add(self, other):
        self.__add__(other)

    def iadd(self, other):
        self.__iadd__(other)

    def __str__(self):
        """If someone calls print() they actually want to see the instance's hooks."""
        pprint(self.chain)
        return self.chain

    def __sizeof__(self):
        """Implement sizeof to see how much the extra methods cost us."""
        return object.__sizeof__(self) + sum(
            sys.getsizeof(v) for v in self.__dict__.values()
        )
