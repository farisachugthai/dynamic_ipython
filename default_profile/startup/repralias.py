import copy
import gc
import logging
import reprlib
from IPython.core.alias import Alias
from IPython.core.getipython import get_ipython


def user_aliases(shell=None):
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
        self.shell = shell if shell is not None else get_ipython()
        self.alias_manager = self.shell.alias_manager
        self.aliases_dict = self.transform_aliases_to_dict(self.aliases)
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
        # I think the difference is ``__getitem__`` ==> ReprAlias['ls']
        # and ``__index__`` ==> ReprAlias[0].
        return index(self.keys(), other)

    def keys(self):
        # Well of course the above doesn't work i never defined keys
        return self.aliases_dict.keys()

    def transform_aliases_to_dict(self, list_of_tuples=None):
        """Ensure everythings funcional. Then.

        TODO: Check that this can be rewritten as 1 line.::

            return {flat[i[0]]: i[1] for i in self.aliases}

        Returns
        -------
        flattened_dict : dict
            Aliases in a dict.

        """
        if len(list_of_tuples) <= 0:
            list_of_tuples = self.aliases
        return {i[0]: i[1] for i in list_of_tuples}

    def __len__(self):
        """Length of 'aliases_dict'."""
        return len(self.aliases_dict)

    def define_alias(self, alias):
        """Dispatch to the running IPython's AliasManager to define an alias."""
        self.alias_manager.define_alias(alias)


if __name__ == "__main__":
    aliases = ReprAlias(user_aliases())
