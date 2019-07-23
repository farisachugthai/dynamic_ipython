#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Set some print options for :mod:`numpy`.

==========
Numpy Init
==========

.. module:: 41_numpy_init
    :synopsis: Configure and modify numpy's print options.

This could be a starting point for practicing module configuration with
traits.

Help on function :func:`numpy.set_printoptions()` in numpy::

    numpy.set_printoptions = set_printoptions(
        precision=None, threshold=None, edgeitems=None, linewidth=None,
        suppress=None, nanstr=None, infstr=None, formatter=None, sign=None,
        floatmode=None, **kwarg
    )

Set printing options.

These options determine the way floating point numbers, arrays and
other NumPy objects are displayed.

Parameters
----------
precision : int or None, optional
    Number of digits of precision for floating point output (default 8).
    May be `None` if `floatmode` is not `fixed`, to print as many digits as
    necessary to uniquely specify the value.
threshold : int, optional
    Total number of array elements which trigger summarization
    rather than full repr (default 1000).
edgeitems : int, optional
    Number of array items in summary at beginning and end of
    each dimension (default 3).
linewidth : int, optional
    The number of characters per line for the purpose of inserting
    line breaks (default 75).
suppress : bool, optional
    If True, always print floating point numbers using fixed point
    notation, in which case numbers equal to zero in the current precision
    will print as zero.  If False, then scientific notation is used when
    absolute value of the smallest number is < 1e-4 or the ratio of the
    maximum absolute value to the minimum is > 1e3. The default is False.
nanstr : str, optional
    String representation of floating point not-a-number (default nan).
infstr : str, optional
    String representation of floating point infinity (default inf).
sign : string, either '-', '+', or ' ', optional
    Controls printing of the sign of floating-point types. If '+', always
    print the sign of positive values. If ' ', always prints a space
    (whitespace character) in the sign position of positive values.  If
    '-', omit the sign character of positive values. (default '-')
formatter : dict of callables, optional
    If not None, the keys should indicate the type(s) that the respective
    formatting function applies to.  Callables should return a string.
    Types that are not specified (by their corresponding keys) are handled
    by the default formatters.  Individual types for which a formatter
    can be set are:

    - 'bool'
    - 'int'
    - 'timedelta' : a `numpy.timedelta64`
    - 'datetime' : a `numpy.datetime64`
    - 'float'
    - 'longfloat' : 128-bit floats
    - 'complexfloat'
    - 'longcomplexfloat' : composed of two 128-bit floats
    - 'numpystr' : types `numpy.string_` and `numpy.unicode_`
    - 'object' : `np.object_` arrays
    - 'str' : all other strings

    Other keys that can be used to set a group of types at once are:

    - 'all' : sets all types
    - 'int_kind' : sets 'int'
    - 'float_kind' : sets 'float' and 'longfloat'
    - 'complex_kind' : sets 'complexfloat' and 'longcomplexfloat'
    - 'str_kind' : sets 'str' and 'numpystr'
floatmode : str, optional
    Controls the interpretation of the `precision` option for
    floating-point types. Can take the following values:

    * 'fixed': Always print exactly `precision` fractional digits,
            even if this would print more or fewer digits than
            necessary to specify the value uniquely.
    * 'unique': Print the minimum number of fractional digits necessary
            to represent each value uniquely. Different elements may
            have a different number of digits. The value of the
            `precision` option is ignored.
    * 'maxprec': Print at most `precision` fractional digits, but if
            an element can be uniquely represented with fewer digits
            only print it with that many.
    * 'maxprec_equal': Print at most `precision` fractional digits,
            but if every element in the array can be uniquely
            represented with an equal number of fewer digits, use that
            many digits for all elements.
legacy : string or `False`, optional
    If set to the string `'1.13'` enables 1.13 legacy printing mode. This
    approximates numpy 1.13 print output by including a space in the sign
    position of floats and different behavior for 0d arrays. If set to
    `False`, disables legacy mode. Unrecognized strings will be ignored
    with a warning for forward compatibility.

    .. versionadded:: 1.14.0

See Also
--------
get_printoptions, set_string_function, array2string

Notes
-----
`formatter` is always reset with a call to `set_printoptions`.

Examples
--------
Floating point precision can be set:

>>> np.set_printoptions(precision=4)
>>> print(np.array([1.123456789]))
[1.1235]

Long arrays can be summarised:

>>> np.set_printoptions(threshold=5)
>>> print(np.arange(10))
[0 1 2 ... 7 8 9]

This doctest fails with the exact numbers it's supposed to have.
How do you fix a whitespace issue?

Small results can be suppressed:

>>> eps = np.finfo(float).eps
>>> x = np.arange(4.)
>>> x**2 - (x + eps)**2
array([-4.9304e-32, -4.4409e-16,  0.0000e+00,  0.0000e+00])
>>> np.set_printoptions(suppress=True)
>>> x**2 - (x + eps)**2
array([-0., -0.,  0.,  0.])

A custom formatter can be used to display array elements as desired:

>>> np.set_printoptions(formatter={'all':lambda x: 'int: '+str(-x)})
>>> x = np.arange(3)
>>> x
array([int: 0, int: -1, int: -2])
>>> np.set_printoptions()  # formatter gets reset
>>> x
array([0, 1, 2])

To put back the default options, you can use:

>>> np.set_printoptions(edgeitems=3,infstr='inf',
... linewidth=75, nanstr='nan', precision=8,
... suppress=False, threshold=1000, formatter=None)


"""
import doctest

try:
    import numpy as np
except (ImportError, ModuleNotFoundError):
    pass
else:
    def set_numpy_printoptions(**kwargs):
        """Define this function only if numpy can be imported.

        But don't end the script with sys.exit() because anything that imports
        this module will exit too. As the :ref:`__init__.py` imports this module
        the whole package breaks due to a simple installation issue.

        Parameters
        ----------
        overrides : dict
            Any options that should be overridden.

        """
        np.set_printoptions(threshold=20)


if __name__ == "__main__":
    set_numpy_printoptions()
    doctest.testmod()  # why not?
