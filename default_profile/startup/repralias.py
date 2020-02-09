"""Try to make viewing large amounts of aliases a bit more manageable.

As a product of running `%rehashx` the alias magic is unusable.

In addition, we try to add enough dunders to the new `ReprAlias` class
constructed here that it appropriately follows the ``mapping`` protocol
as specified in the Python Language Reference.

"""
import copy
import logging
import reprlib

from IPython.core.getipython import get_ipython

from default_profile.startup import STARTUP_LOGGER


def get_aliases(shell=None):
    if shell is None:
        shell = get_ipython()
    if shell is None:
        return
    return shell.alias_manager.aliases


class ReprAlias(reprlib.Repr):
    """Take user aliases and transform them to a dictionary.

    Then utilize :class:`reprlib.Repr` to print the structure.

    .. todo::
        xonsh.__amalgam__.LsColors is a subclass of :class:`abc.ABCMeta`
        that reimplements most of the dunders for `dict` so check out that
        implementation to see some good examples.

    """

    maxlevel = 5

    def __init__(self, aliases=None, shell=None):
        """Initialize truncated alias list.

        Parameters
        ----------
        alias : dict, optional
            Aliases in a more sensible data structure

        """
        self.aliases = aliases or get_aliases()
        if len(self.aliases) == 0:
            STARTUP_LOGGER.exception("Length of repralias.ReprAlias.aliases was 0")
        self.shell = shell
        if self.shell is None:
            self.shell = get_ipython()
        self.alias_manager = self.shell.alias_manager
        self.aliases_dict = self.transform_aliases_to_dict()
        self.idx = 0
        super().__init__()

    def get_alias(self, other):
        """Uses shell.alias_manager to get an alias.

        .. note::
            Not the same implementation as ``self.__getitem__``.

        Parameters
        ----------
        other : str
            Alias to check. Returns None if alias is not defined.

        """
        return self.alias_manager.get_alias(self, other)

    def __getitem__(self, other):
        try:
            return self.aliases_dict[other]
        except TypeError:
            raise

    def __index__(self, other):
        """I  think the difference is ``__getitem__`` ==> ReprAlias['ls']
        and ``__index__`` ==> ReprAlias[0]."""
        return index(self.keys(), other)

    def keys(self):
        # Well of course the above doesn't work i never defined keys
        return self.aliases_dict.keys()

    def transform_aliases_to_dict(self):
        """Ensure everythings funcional. Then.

        TODO: Check that this can be rewritten as 1 line.::

            return {flat[i[0]]: i[1] for i in self.aliases}

        Returns
        -------
        flattened_dict : dict
            Aliases in a dict.

        """
        flattened_dict = {}
        for i in self.aliases:
            flattened_dict[i[0]] = i[1]

        return flattened_dict

    def __len__(self):
        return len(self.aliases_dict)

    def __repr__(self):
        return "<{}>: {} aliases".format(self.__class__.__name__, len(self.aliases))

    @reprlib.recursive_repr
    def __str__(self, maxdict=30):
        return "<{}>\n{}".format(
            self.__class__.__name__, self.repr_dict(self.aliases_dict, maxdict)
        )

    def define_alias(self, alias):
        self.alias_manager.define_alias(alias)

    def soft_define_alias(self, alias):
        """Define a new alias and don't raise an error on an invalid alias.

        Examples
        --------
        ::

            In [54]: pkg?
            Repr: <alias pkg for 'pkg'>
            In [55]: aliases + ('pkg', 'pkg list-a')
            In [56]: pkg?
            Repr: <alias pkg for 'pkg list-a'>

        """
        self.alias_manager.soft_define_alias(*alias)

    def __add__(self, alias):
        self.soft_define_alias(alias)

    def __iadd__(self, alias):
        self.soft_define_alias(alias)

    def __copy__(self):
        return copy.copy(self.aliases)

    def __contains__(self, other):
        return other in self.aliases_dict

    def __iter__(self):
        return iter(self.aliases_dict.items())

    def __next__(self):
        max = len(self)
        if max >= self.idx:
            # Reset the loop and raise stopiteration
            self.idx = 0
            raise StopIteration
        self.idx += 1
        return self.aliases_dict[self.idx]


if __name__ == "__main__":
    aliases = ReprAlias(get_aliases())

# Vim: set et:
