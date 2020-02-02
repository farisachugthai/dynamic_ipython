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
        """Implementation is wrong.

        Traceback
        ---------
        >>> from wcwidth import wcswidth
        >>> from default_profile.startup.repralias import ReprAlias, get_aliases
        >>> aliases = ReprAlias(get_aliases)
        >>> wcswidth(aliases)
        Traceback (most recent call last):
        File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/IPython/core/interactiveshell.py", line 3319, in run_code
        exec(code_obj, self.user_global_ns, self.user_ns)
        File "<ipython-input-67-0ba317adf8d3>", line 1, in <module>
        wcswidth(aliases)
        File "/data/data/com.termux/files/home/.local/share/virtualenvs/dynamic_ipython-mVJ3Ohov/lib/python3.8/site-packages/wcwidth/wcwidth.py", line 201, in wcswidth
        for char in pwcs[idx]:
        File "/data/data/com.termux/files/home/projects/dynamic_ipython/default_profile/startup/repralias.py",
        line 63, in __getitem__
        return other in self.aliases_dict
        TypeError: unhashable type: 'slice'

        """
        return other in self.aliases_dict

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

    def __copy__(self):
        return copy.copy(self.aliases)

    def __contains__(self, other):
        return other in self.aliases_dict

    def __iter__(self):
        try:
            return iter(self.aliases)
        except TypeError:
            raise


if __name__ == "__main__":
    aliases = ReprAlias(get_aliases())
