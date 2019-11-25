import copy
from reprlib import Repr


class ReprAlias(Repr):
    def __init__(self, aliases=None):
        """Initialize truncated alias list.

        Parameters
        ----------
        alias : dict, optional
            Aliases in a more sensible data structure

        """
        self.aliases = aliases

    def transform_aliases_to_dict(self):
        # TODO:
        self.aliases

    def __repr__(self):
        return ''.join(self.__class__.__name__)

    def __str__(self):
        return '{}\n{}'.format(self.__class__.__name__,
                               self.repr_dict(self.aliases, 15))

    def __add__(self):
        # todo
        raise NotImplementedError

    def __copy__(self):
        return copy.copy(self.aliases)


if __name__ == "__main__":
    repr_alias = ReprAlias(get_ipython().alias_manager.user_aliases)
