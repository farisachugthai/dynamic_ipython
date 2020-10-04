.. _ipython-sphinx-directive:

========================
IPython Sphinx Directive
========================

.. module:: sphinx_directive
   :synopsis: An enhanced extension for Sphinx and rst use.

.. |rst| replace:: reStructured text

The :rst:dir:`ipython` directive is a stateful shell that can be used
in |rst| files.

The Sphinx project, for those who are unfamiliar, is used
to create documentation from valid Python source in order to generate HTML.

The generated HTML can then be uploaded online and be served as the official
documentation for software projects in the varying languages that Sphinx
supports.

The IPython directive builds on this functionality by creating an
:rst:dir:`ipython` directive. This allows for a user to, for example,
copy and paste their interactive session into an |rst| file.

While generating the HTML, the IPython Sphinx shell can also parse
and validate IPython code, syntax highlight source code that's been included
literally, and embed plots based on the live embedded data.

Specifically, the IPython Sphinx extension correctly parses standard
IPython prompts, and extracts the input and output lines to generate HTML.


.. note::

   This tutorial should be read side-by-side with the
   `Sphinx source <../_sources/sphinxext.rst.txt>`_ that generated this
   document. With the exception of the example given above, the literal
   ReStructured Text will not be displayed alongside the rendered output.

.. admonition:: Warning is Error

   All warnings are treated as errors in the default configuration which
   will lead to frequent crashes while building documentation.
   The option where this behavior can be modified, ``ipython_warning_is_error``
   is displayed in the IPython Sphinx directive module section at the
   bottom of the page.


Directive and options
=====================

The IPython directive takes a number of options detailed here.

.. rst:directive:: ipython

   Create an IPython directive.

   .. rst:directive:option:: doctest

      Run a doctest on IPython code blocks in rst.

   .. rst:directive:option:: python

      Used to indicate that the relevant code block does not have IPython prompts.

   .. rst:directive:option:: okexcept

      Allow the code block to raise an exception.

   .. rst:directive:option:: okwarning

      Allow the code block to emit an warning.

   .. rst:directive:option:: suppress

      Silence any warnings or expected errors.

   .. rst:directive:option:: verbatim

      A noop that allows for any text to be syntax highlighted as valid IPython code.

   .. rst:directive:option:: savefig: OUTFILE [IMAGE_OPTIONS]

      Save output from matplotlib to *outfile*.

It's important to note that all of these options can be used for the entire
directive block or they can decorate individual lines of code as explained
in :ref:`pseudo-decorators`.

.. todo:: Hmmmm should we document those decorators using the above syntax?

   We emit warnings when we document both directives and pseudo-decorators.


.. _ipython-directive-usage:

Usage
=====

These prompts will be renumbered starting at ``1`` regardless of the actual
number displayed in the source code.

For example, code blocks like the following::

  .. ipython::

     In [136]: x = 2

     In [137]: x**3
     Out[137]: 8

Will be rendered as:

.. ipython::

   In [136]: x = 2

   In [137]: x**3
   Out[137]: 8


.. seealso::

   :ref:`configuration-values`
      Check towards the bottom of this document to view all IPython
      configuration options.

Persisting the session across blocks
====================================

The state from previous code-blocks is stored and carries over from section
to section. The IPython shell will maintain and continue to execute in the same
namespace so long as it remains in the same document.

This can be useful for documentation that may need to build on a few
lengthier examples rather than a handful of shorter snippets.

In addition, IPython's output and :data:`sys.stderr` will be
inserted at doc build time, and the prompts will be renumbered starting
from ``1``. For example, the prompt below is renumbered so as to follow
the code block from above.

.. code-block:: py3tb

   In [138]: z = x*3   # x is recalled from previous block

   In [139]: z
   Out[139]: 6

   In [142]: print(z)
   6

   In [141]: q = z[)
   # this is a syntax error -- we trap ipy exceptions
   ------------------------------------------------------------
     File "<ipython console>", line 1
       q = z[)   # this is a syntax error -- we trap ipy exceptions
             ^
   SyntaxError: invalid syntax


Multi-line input
================

Multi-line input is supported, and particularly lengthy blocks of text can be
parsed correctly.

.. **TODO**
.. is this parsed correctly because the last character is the continuation
   character or because of a property intrinsic to IPython's sphinx extension??

.. ipython::
   :verbatim:

   In [130]: url = 'http://ichart.finance.yahoo.com/table.csv?s=CROX\
      .....: &d=9&e=22&f=2009&g=d&a=1&br=8&c=2006&ignore=.csv'

   In [131]: print(url.split('&'))
   ['http://ichart.finance.yahoo.com/table.csv?s=CROX', 'd=9', 'e=22',


Writing Pure Python Code
------------------------

Pure python code is supported by the optional argument `:python:`.
In this pure python syntax you do not include the output from the
python interpreter. The following markup::

   .. ipython:: python

      foo = 'bar'
      print(foo)
      foo = 2
      foo**2

Renders as

.. ipython:: python

   foo = 'bar'
   print(foo)
   foo = 2
   foo**2

We can even plot from python, using the :rst:dir:`savefig` option to the directive,
as well as :rst:dir:`suppress` output with a semicolon.

These options can both be expressed with their decorator counterparts like so:

.. code-block:: rst

   .. ipython:: python

      @savefig plot_simple_python.png width=4in
      plot([1, 2, 3])

.. ipython:: python

   @savefig plot_simple_python.png width=4in
   plot([1, 2, 3])

For more information on the `@savefig` decorator, please refer to the end of
this page in Pseudo-Decorators section.

Similarly, :data:`sys.stderr` is inserted.:

.. code-block:: rst

   .. ipython:: python
      :okexcept:

      foo = 'bar'
      foo[)


.. ipython:: python
   :okexcept:

   foo = 'bar'
   foo[)


Handling Comments
==================

Comments are handled and state is preserved.:

.. ipython:: python

   # comments are handled
   print(foo)

The following section attempts to execute faulty code, namely calling
the :mod:`matplotlib.pyplot` functions ``matplotlib.pyplot.ioff``
and ``matplotlib.pyplot.ion`` which haven't been defined in this session.

.. code-block:: rst

   .. ipython:: python
      :suppress:

      ioff()
      ion()

As we observe, there is no code-block below, and the directive appropriately
suppresses the error during doc-builds.

.. ipython:: python
   :suppress:

   ioff()
   ion()


Splitting Python statements across lines
========================================

Multi-line input is handled.:

.. ipython:: python

   line = 'Multi\
           line &\
           support &\
           works'
   print(line.split('&'))

.. why is this function definition in here twice?

Functions definitions are correctly parsed.:

.. ipython:: python

   def square(x):
       """
       An overcomplicated square function as an example.
       """
       if x < 0:
           x = abs(x)
       y = x * x
       return y

And persist across sessions.:

.. ipython:: python

   print(square(3))
   print(square(-2))

.. I want to put this in the docstrings of those functions with the `env`
   parameter that kept tripping me up. (ref)

.. glossary::

   environment
      A structure where information about all documents under the root is saved,
      and used for cross-referencing.  The environment is pickled after the
      parsing stage, so that successive runs only need to read and parse new and
      changed documents.


.. _pseudo-decorators:

Pseudo-Decorators
=================

Here are the supported decorators, and any optional arguments they
take.  Some of the decorators can be used as options to the entire
block (e.g. `@verbatim` and `@suppress`), and some only apply to the
line just below them (eg `@savefig`).:

.. decorator:: suppress

   Execute the ipython input block, but suppress the input and output
   block from the rendered output.  Also, can be applied to the entire
   ``..ipython`` block as a directive option with :rst:dir:`:suppress:`.


.. decorator:: verbatim

   Insert the input and output block in exactly as they were inputted, but
   prepend an IPython prompt if necessary. Auto-increment the prompt as
   appropriate for the state of the document. Internally, the interpreter will
   be fed an empty string, so it is a no-op that keeps line numbering
   consistent. Also, can be applied to the entire ``.. ipython`` block as a
   directive option with :rst:dir:`verbatim`.

.. decorator:: savefig

   Save the target of the directive to :dfn:`outfile`.
   *I think I'm just gonna rewrite this entire paragraph.*
   Save the figure to the static directory and insert it into the
   document, possibly binding it into a mini-page and/or putting
   code/figure label/references to associate the code and the figure.
   Takes args to pass to the image directive (*scale*,
   *width*, etc can be ``**kwargs``)

.. decorator:: doctest

   Compare the pasted in output in the IPython block with the output
   generated at doc build time, and raise errors if they don't
   match. Also, can be applied to the entire ``.. ipython`` block as a
   directive option with ``:doctest:``.

.. decorator:: okexcept

.. decorator:: okwarning

.. decorator:: python


.. todo:: Document the magics.py sphinx extension!!

   The ``.. magic::`` directive doesn't appear to be documented at all.
   Actually wait. Does it ship with the IPython wheel?


.. _configuration-values:

Configuration Values
=====================

The configurable options that can be placed in conf.py are:

.. confval:: ipython_savefig_dir

   The directory in which to save the figures. This is
   relative to the
   Sphinx source directory. The default is `html_static_path`.

.. confval:: ipython_rgxin

   The compiled regular expression to denote the start of
   IPython input lines.
   The default is `re.compile('In \\[(\\d+)\\]:\\s?(.*)\\s*')`.
   You shouldn't need to change this.

.. confval:: ipython_warning_is_error

   [Default to True]
   Fail the build if something unexpected happen, for example
   if a block raise an exception but does not have the
   `:okexcept:` flag. The exact behavior of
   what is considered strict, may change between the sphinx
   directive version.

.. confval:: ipython_rgxout

   The compiled regular expression to denote the start of
   IPython output lines. The default is
   `re.compile('Out\\[(\\d+)\\]:\\s?(.*)\\s*')`.
   You shouldn't need to change this.

.. confval:: ipython_promptin

    The string to represent the IPython input prompt in the generated ReST.
    The default is ``'In [%d]:'``. This expects that the line
    numbers are used in the prompt.

.. confval:: ipython_promptout

    The string to represent the IPython prompt in the generated ReST. The
    default is ``'Out [%d]:'``. This expects that the line numbers are used
    in the prompt.

.. confval:: ipython_mplbackend

    A `str` which specifies if the embedded Sphinx shell should import
    :mod:`matplotlib` and if so, which backend it should use.
    The value is  passed to :func:`matplotlib.use` before any lines in
    :confval:`ipython_execlines` are executed.
    If not specified in conf.py, then the default value of 'agg' is
    used. To use the IPython directive without matplotlib as a dependency, set
    the value to `None`. It may end up that :mod:`matplotlib` is still imported
    if the user specifies so in :confval:`ipython_execlines` or makes use of the
    `@savefig` pseudo decorator.

.. confval:: ipython_execlines

    A `list` of `str` given as arguments to the function :func:`exec`
    in the embedded Sphinx shell.
    Typical usage is to ensure all common dependencies of the package have
    been properly imported.
    Set this to an empty list if you wish to have no imports always available.

    If omitted from conf.py altogether, then the default value of::

       ['import numpy as np', 'import matplotlib.pyplot as plt']

    is used.

.. confval:: ipython_holdcount

    When the `@suppress` pseudo-decorator is used, the execution count can be
    incremented or not. The default behavior is to hold the execution count,
    corresponding to a value of `True`. Set this to `False` to increment
    the execution count after each suppressed command.

As an example, to use the IPython directive when `matplotlib` is not available,
one sets the backend to `None`::

    ipython_mplbackend = None


See Also
---------

One may find it useful to reference the relevant documentation from the
`Sphinx`_  project and Docutils.

.. _Sphinx: `<http://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-restructuredtext-domain>`

.. seealso::

   `The Sphinx documentation project <http://www.sphinx-doc.org/en/master/>`_
      Sphinx has phenomenal documentation and provides a good reference when
      working with rst files.
      In addition the source for each page of the documentation is easily
      obtainable from the "Show Source" button.

.. seealso::

   `<http://docutils.sourceforge.net/docs/ref/rst/directives.html#image>`_
      Image Options for rst directives --- from docutils.

.. Vim: set et:
