#!/usr/bin/env python3
"""
=======
Pager
=======

So would it be easier to do this as a magic or using Traitlets?

Original Implementation
========================

Below is the source code for how the original :ref:`pycat` was implemented.::

    from IPython import get_ipython
    from IPython.core.magics import line_magic
    from IPython.core.errors import UsageError

    self.shell = get_ipython()

    # Real src
    @line_magic
    def pycat(self, parameter_s=''):
        # Show a syntax-highlighted file through a pager.

        # This magic is similar to the cat utility, but it will assume the file
        # to be Python source and will show it with syntax highlighting.

        # This magic command can either take a local filename, an url,
        # an history range (see %history) or a macro as argument ::

        # %pycat myscript.py
        # %pycat 7-27
        # %pycat myMacro
        # %pycat http://www.example.com/myscript.py
        if not parameter_s:
            raise UsageError('Missing filename, URL, input history range, '
                             'or macro.')

        try :
            cont = self.shell.find_user_code(parameter_s, skip_encoding_cookie=False)
        except (ValueError, IOError):
            print("Error: no such file, variable, URL, history range or macro")
            return

        page.page(self.shell.pycolorize(source_to_unicode(cont)))

File:   /usr/lib/python3.7/site-packages/IPython/core/magics/osm.py


Breaking it down
================

Here's the docstring from :mod:`IPython.utils.openpy`, specifically
the function ``read_py_file``.::

    skip_encoding_cookie : bool
      If True (the default), and the encoding declaration is found in the first
      two lines, that line will be excluded from the output - compiling a
      unicode string with an encoding declaration is a SyntaxError in Python 2.


page.page
---------

What's that ``page.page`` line?

>>> from IPython.core.magics.basic import BasicMagics
>>> BasicMagics.page??

    @line_magic
    def page(self, parameter_s=''):
        # Pretty print the object and display it through a pager.

            %page [options] OBJECT

        # If no object is given, use _ (last output).
        # Options:

            -r: page str(object), don't pretty-print it.

        # After a function contributed by Olivier Aubert, slightly modified.
        # Process options/args
        opts, args = self.parse_options(parameter_s, 'r')
        raw = 'r' in opts

        oname = args and args or '_'
        info = self.shell._ofind(oname)
        if info['found']:
            txt = (raw and str or pformat)( info['obj'] )
            page.page(txt)
        else:
            print('Object `%s` not found' % oname)

Nope! *However that is a good example use of magic_arguments*.
So whats page.page?

>>> from IPython.core import page

Eh I don't know if that was it.


Rewriting the pager
===================

Found some platform specific code. I think we're in the right direction.

Aug 17, 2019:

Think I got it.

>>> from IPython.core.page import get_pager_cmd

**Note that that isn't the page.page method; however, it does
show how IPython setup the pager.

See Also
--------
:func:`numpy.info`
:func:`numpy.source`

Also worth noting is how Numpy and Scipy entirely
circumvent it with their numpy.info() and numpy.source() functions.


Implementing the rewrite
========================

It might be best if we design this using traitlets.
They have the linking functions in the utils directory
so that we can observe if sphinxify_docstring changes, or
the value of editor changes, or handful of other things that we'll
be expected to respond to.


"""
import sys

from pygments.lexers.python import PythonLexer
from IPython.lib.lexers import IPyLexer, IPython3Lexer

from IPython import get_ipython
# Might need some of the funcs from IPython.utils.{PyColorize,coloransi,colorable}
from IPython.core.error import UsageError
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring
)


def load_ipython_docstring(shell):
    """TODO: Docstring for lpad_ipython_docstring.

    Parameters
    ----------
    shell : |ip|
        Global IPython object.

    Returns
    -------
    TODO

    """
    shell.register_magics(MyMagics)


@magic_arguments
def main():
    """Rewrite the module that creates the ``%pycat`` magic.

    In it's current implementation, the pager gives Windows a dumb terminal and
    never checks for whether :command:`less` is on the :envvar:`PATH` or
    if the user has a pager they wanna implement!

    .. addendum:: Is this a real directive?

        The implementation checks the PAGER env var.

    :returns: TODO

    """
    pass


if __name__ == "__main__":
    _ip = get_ipython()
    # main()
