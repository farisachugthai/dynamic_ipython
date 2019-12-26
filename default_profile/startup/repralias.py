import copy
import logging
from reprlib import Repr

from IPython.core.getipython import get_ipython

from default_profile.startup import STARTUP_LOGGER


def get_aliases(shell=None):
    if shell is None:
        shell = get_ipython()
    if shell is None:
        return
    return shell.alias_manager.aliases


class ReprAlias(Repr):
    """Take user aliases and transform them to a dictionary.

    Then utilize :class:`reprlib.Repr` to print the structure.
    """
    maxdict = 6
    maxlevel = 5

    def __init__(self, aliases=None):
        """Initialize truncated alias list.

        Parameters
        ----------
        alias : dict, optional
            Aliases in a more sensible data structure

        """
        self.aliases = aliases or get_aliases()
        if len(self.aliases) == 0:
            STARTUP_LOGGER.exception("Length of repralias.ReprAlias.aliases was 0")

    def transform_aliases_to_dict(self):
        """Ensure everythings funcional. Then.

        TODO: Check that this can be rewritten as 1 line.::

            return {flat[i[0]]: i[1] for i in self.aliases}

        """
        flattened_dict = {}
        for i in self.aliases:
            flattened_dict[i[0]] = i[1]

        return flattened_dict

    def __repr__(self):
        return "{}: {} aliases".format(self.__class__.__name__, len(self.aliases))

    def __str__(self):
        return "{}\n{}".format(
            self.__class__.__name__, self.repr_dict(self.aliases, 15)
        )

    def __add__(self):
        # todo
        raise NotImplementedError

    def __copy__(self):
        return copy.copy(self.aliases)


if __name__ == "__main__":
    aliases = ReprAlias(get_ipython().alias_manager.user_aliases)
