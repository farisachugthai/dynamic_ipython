#!/usr/bin/env python3
"""Arguably the best canary in the coal mine that something's wrong with setup.

Lmao also dude check out what doctest has at the bottom.
"""
from IPython.core.getipython import get_ipython
import IPython
import doctest
import logging
import unittest
import shutil
import tempfile
import unittest


def remove_tmpdir(dirname):
    print("In remove_tmpdir()")
    shutil.rmtree(dirname)


######################################################################
# 9. Example Usage
######################################################################


class _TestClass:
    """
    A pointless class, for sanity-checking of docstring testing.

    Methods:
        square()
        get()

    >>> _TestClass(13).get() + _TestClass(-12).get()
    1
    >>> hex(_TestClass(13).square().get())
    '0xa9'
    """

    def __init__(self, val):
        """val -> _TestClass object with associated value val.

        >>> t = _TestClass(123)
        >>> print(t.get())
        123
        """

        self.val = val

    def square(self):
        """square() -> square TestClass's associated value

        >>> _TestClass(13).square().get()
        169
        """

        self.val = self.val ** 2
        return self

    def get(self):
        """get() -> return TestClass's associated value.

        >>> x = _TestClass(-42)
        >>> print(x.get())
        -42
        """

        return self.val


__test__ = {
    "_TestClass": _TestClass,
    "string": r"""
                      Example of a string object, searched as-is.
                      >>> x = 1; y = 2
                      >>> x + y, x * y
                      (3, 2)
                      """,
    "bool-int equivalence": r"""
                                    In 2.2, boolean expressions displayed
                                    0 or 1.  By default, we still accept
                                    them.  This can be disabled by passing
                                    DONT_ACCEPT_TRUE_FOR_1 to the new
                                    optionflags argument.
                                    >>> 4 == 4
                                    1
                                    >>> 4 == 4
                                    True
                                    >>> 4 > 4
                                    0
                                    >>> 4 > 4
                                    False
                                    """,
    "blank lines": r"""
                Blank lines can be marked with <BLANKLINE>:
                    >>> print('foo\n\nbar\n')
                    foo
                    <BLANKLINE>
                    bar
                    <BLANKLINE>
            """,
    "ellipsis": r"""
                If the ellipsis flag is used, then '...' can be used to
                elide substrings in the desired output:
                    >>> print(list(range(1000))) #doctest: +ELLIPSIS
                    [0, 1, 2, ..., 999]
            """,
    "whitespace normalization": r"""
                If the whitespace normalization flag is used, then
                differences in whitespace are ignored.
                    >>> print(list(range(30))) #doctest: +NORMALIZE_WHITESPACE
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                     15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                     27, 28, 29]
            """,
}


class FixturesTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(remove_tmpdir, self.tmpdir)

    def test1(self):
        print("\nIn test1()")

    def test2(self):
        print("\nIn test2()")


if __name__ == "__main__":
    unittest.main()
