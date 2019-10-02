.. _ipython-sphinx-directive:

========================
IPython Sphinx Directive
========================
.. module:: sphinx_directive
   :synopsis: An enhanced extension for Sphinx and rst use.

.. highlight:: ipython
   :linenothreshold: 3

.. this one is probably overkill right?

.. |IPython| replace:: :mod:`IPython`

.. |rst| replace:: reStructured text

The |IPython| directive is a stateful shell that can be used in reStructured
text files.

The Sphinx project, for those who are unfamiliar, is used
to create documentation from valid Python source in order to generate HTML.

The generated HTML can then be uploaded online and be served as the official
documentation for software projects in the varying languages that Sphinx
supports.

The IPython directive builds on this functionality by creating an
:rst:directive:`ipython` directive. This allows for a user to, for example,
copy and paste their interactive session into an |rst| file.

While generating the HTML, the IPython Sphinx shell can also parse
and validate IPython code, syntax highlight source code that's been included
literally, and embed plots based on the live embedded data.

Specifically, the IPython Sphinx extension correctly parses standard
IPython prompts, and extracts the input and output lines to generate HTML.


Directive and options
=====================

The IPython directive takes a number of options detailed here.

.. rst:directive:: ipython

   Create an IPython directive.

   .. rst:directive:option:: doctest: Run a doctest on IPython code blocks in rst.

   .. rst:directive:option:: python: Used to indicate that the relevant code block does not have IPython prompts.

   .. rst:directive:option:: okexcept: Allow the code block to raise an exception.

   .. rst:directive:option:: okwarning: Allow the code block to emit an warning.

   .. rst:directive:option:: suppress: Silence any warnings or expected errors.

   .. rst:directive:option:: verbatim: A noop that allows for any text to be syntax highlighted as valid IPython code.

   .. rst:directive:option:: savefig: Save output from matplotlib to *outfile*.
                                      OUTFILE [IMAGE_OPTIONS]



It's important to note that all of these options can be used for the entire
directive block or they can decorate individual lines of code.

.. todo:: Hmmmm should we document those decorators using the above syntax?

   We emit warnings when we document both directives and pseudo-decorators.

One may find it useful to reference the relevant documentation from the
[Sphinx]_  project and Docutils.

.. [Sphinx] `<http://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-restructuredtext-domain>`

.. seealso::

   `The Sphinx documentation project <http://www.sphinx-doc.org/en/master/>`_ has phenomenal documentation and provides a good reference when working with rst files.


   In addition the source for each page of the documentation
   is easily obtainable from the "Show Source" button.

.. seealso::

   `Image Options for rst directives from docutils
   <http://docutils.sourceforge.net/docs/ref/rst/directives.html#image>`_ for details.

.. seealso:: :ref:`configuration-values`

   Check towards the bottom of this document to view all IPython configuration options.


.. _ipython-directive-usage:

Directive Usage
===============

These prompts will be renumbered starting at ``1`` regardless of the actual
number displayed in the source code.

For example, code blocks like the following::

  .. ipython::

     In [136]: x = 2

     In [137]: x**3
     Out[137]: 8

will be rendered as:

.. ipython::

   In [136]: x = 2

   In [137]: x**3
   Out[137]: 8

.. note::

   This tutorial should be read side-by-side with the
   `Sphinx source <../_sources/sphinxext.rst.txt>`_ that generated this
   document. With the exception of the example given above, the literal
   ReStructured Text will not be displayed alongside the rendered output.


Persisting the session across IPython directive blocks
======================================================

The state from previous code-blocks is stored, and carries over from section
to section. The IPython shell will maintain and continue to execute in the same
namespace so long as it remains in the same document.

This can be useful for documentation that may need to build on a few
lengthier examples rather than a handful of shorter snippets.

In addition, IPython's output and :data:`sys.stderr` will be
inserted at doc build time, and the prompts will be renumbered starting
from ``1``. For example, the prompt below is renumbered so as to follow the code
block from above.


.. why isn't this directive working?
.. .. ipythontb::

.. code-block:: ipythontb

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


Testing directive outputs
=========================

The extension supports a few limited parameters to configure the running
shell. These parameters are exposed as reStructured text options to the
``.. ipython`` directive, decorators for the source code directly, and
configurable options that are given directly to Sphinx in a projects conf.py.

For example, you can put comments in your IPython sessions, which are
reported verbatim.  There are some handy "pseudo-decorators" that let you
wrap a function with `@doctest` and utilize the :mod:`doctest` module on
the output.

The inputs are fed to an embedded IPython session and the outputs are
inserted into your documentation automatically.

If the output in your doc and the output from the embedded shell don't
match on a :mod:`doctest` assertion, an error will occur.


.. literally what does the below say?????

.. The IPython Sphinx Directive makes it possible to test the outputs that you
.. provide with your code. To do this,
.. decorate the contents in your directive block with one of the following:

.. guys are you serious this line has been in here for like 5 years

..   * list directives here

If the `@doctest` decorator is found, it will take these steps when your
documentation is built:

1. Execute the *input* lines in your IPython directive block.

2. Compare the *output* of this with the output text that you've put in the
   IPython directive block (I.E. what comes after ``Out[NN]``);

3. If there is a difference, the embedded shell will raise an error and
   halt building the documentation.

.. admonition:: Warning is Error

   All warnings are treated as errors in the default configuration which
   will lead to frequent crashes while building documentation.
   The option where this behavior can be modified, ``ipython_warning_is_error``
   is displayed in the IPython Sphinx directive module section at the
   bottom of the page.

You can `@doctest` multi-line output as well. Just be careful
when using non-deterministic inputs like random numbers in the IPython
directive.

Because your inputs are run through a live interpreter, the random numbers
that are generated on the fly will likely differ from run to run.

Therefore the output IPython will compare the present run to will likely
differ, raising errors and causing mayhem.

How can we avoid this?

Here we "seed" the random number generator for deterministic output, and
we suppress the seed line so it doesn't show up in the rendered output.:

.. ipython::

   In [133]: import numpy
   @suppress
   In [134]: numpy.random.seed(2358)
   @doctest
   In [135]: numpy.random.rand(10,2)
   Out[135]:
   array([[0.64524308, 0.59943846],
          [0.47102322, 0.8715456 ],
          [0.29370834, 0.74776844],
          [0.99539577, 0.1313423 ],
          [0.16250302, 0.21103583],
          [0.81626524, 0.1312433 ],
          [0.67338089, 0.72302393],
          [0.7566368 , 0.07033696],
          [0.22591016, 0.77731835],
          [0.0072729 , 0.34273127]])


For more information on `@suppress` and `@doctest` decorators, please refer
to the end of this file in :ref:`Pseudo-Decorators` section.


Registering Your Own Doctest Handlers
-------------------------------------

.. holy hell is this bad.
.. hey if it means anything the source code at IPython.sphinxext.custom_doctests
   is actually crystal clear

The Sphinx extension that provides support for embedded IPython code provides
a pseudo-decorator `@doctest`, which treats the input/output block as a
doctest, raising a :exc:`RuntimeError` during doc generation if
the actual output (after running the input) does not match the expected output.

An example usage is:

.. code-block:: rst

   .. ipython::

        In [1]: x = 1

        @doctest
        In [2]: x + 2
        Out[3]: 3

One can also provide arguments to the decorator. The first argument should be
the name of a custom handler. The specification of any other arguments is
determined by the handler. For example,

.. code-block:: rst

   .. ipython::

      @doctest float
      In [154]: 0.1 + 0.2
      Out[154]: 0.3

allows the actual output ``0.30000000000000004`` to match the expected output
due to a comparison with `numpy.allclose`.

This is detailed in the module :mod:`IPython.sphinxext.custom_doctests`.

Handlers should have the following function signature::

    handler(sphinx_shell, args, input_lines, found, submitted)


.. glossary::

   sphinx_shell
      Embedded Sphinx shell

   args
      The list of arguments that follow '@doctest handler_name',

   input_lines
      A list of the lines relevant to the current doctest,

   found
      A string containing the output from the IPython shell

   submitted
      A string containing the expected output from the IPython shell.


Handlers must be registered in the `doctests` dict at the end of the
:mod:`~IPython.sphinxext.custom_doctests` module.

.. todo:: doctest handlers

   I quite honestly don't know how you're supposed to add handlers
   to the dict though.

But here's the sauce::

   # dict of allowable doctest handlers. The key represents the first argument
   # that must be given to @doctest in order to activate the handler.
   doctests = {
       'float': float_doctest,
   }


Another demonstration of multi-line input and output.:

.. ipython::
   :verbatim:

   In [106]: print(x)
   jdh

   In [109]: for i in range(10):
      .....:     print(i)
      .....:
      .....:
   0
   1
   2
   3
   4
   5
   6
   7
   8
   9


Most of the "pseudo-decorators" can be used as options to IPython
mode.  For example, to setup matplotlib's ``pylab`` but suppress the
output, you can set things up in the following way.

When using the matplotlib ``use`` directive, it should
occur before any import of pylab.  This will not show up in the
rendered docs, but the commands will be executed in the embedded
interpreter and subsequent line numbers will be incremented to reflect
the inputs::


  .. ipython::
     :suppress:

     In [144]: from matplotlib.pylab import *
     In [145]: ion()

.. ipython::
   :suppress:

   In [144]: from matplotlib.pylab import *
   In [145]: ion()

Likewise, you can set ``:doctest:`` or ``:verbatim:`` to apply these
settings to the entire block.  For example,

.. ipython::
   :verbatim:

   In [9]: cd mpl/examples/
   /home/jdhunter/mpl/examples

   In [10]: pwd
   Out[10]: '/home/jdhunter/mpl/examples'


   In [14]: cd mpl/examples/<TAB>
   mpl/examples/animation/        mpl/examples/misc/
   mpl/examples/api/              mpl/examples/mplot3d/
   mpl/examples/axes_grid/        mpl/examples/pylab_examples/
   mpl/examples/event_handling/   mpl/examples/widgets

   In [14]: cd mpl/examples/widgets/
   /home/msierig/mpl/examples/widgets

   In [15]: !wc *
       2    12    77 README.txt
      40    97   884 buttons.py
      26    90   712 check_buttons.py
      19    52   416 cursor.py
     180   404  4882 menu.py
      16    45   337 multicursor.py
      36   106   916 radio_buttons.py
      48   226  2082 rectangle_selector.py
      43   118  1063 slider_demo.py
      40   124  1088 span_selector.py
     450  1274 12457 total

You can create one or more pyplot plots and insert them with the
`@savefig`` decorator.

For more information on `@savefig` decorator, please refer to the end of this
page in :ref:`Pseudo-Decorators` section.

.. ipython::

   @savefig plot_simple.png width=4in
   In [151]: plot([1,2,3]);

   # use a semicolon to suppress the output
   @savefig hist_simple.png width=4in
   In [151]: hist(np.random.randn(10000), 100);

In a subsequent session, we can update the current figure with some
text, and then resave.:

.. ipython::

   In [151]: ylabel('number')

   In [152]: title('normal distribution')

   @savefig hist_with_text.png width=4in
   In [153]: grid(True)

You can also have function definitions included in the source.

.. ipython::

   In [3]: def square(x):
      ...:     """
      ...:     An overcomplicated square function as an example.
      ...:     """
      ...:     if x < 0:
      ...:         x = abs(x)
      ...:     y = x * x
      ...:     return y
      ...:

Then call it from a subsequent section.

.. ipython::

   In [4]: square(3)
   Out [4]: 9

   In [5]: square(-2)
   Out [5]: 4


**Why does the sentence below appear no less than 3 times in this doc?**

For more information on the ``@doctest`` decorator, please refer to the end of
this page in the :ref:`Pseudo-Decorators` section.


Writing Pure Python Code
------------------------

Pure python code is supported by the optional argument `python`. In this
pure
python syntax you do not include the output from the python interpreter. The
following markup::

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

We can even plot from python, using the `@savefig` decorator, as well as
suppress output with a semicolon.:

.. ipython:: python

   @savefig plot_simple_python.png width=4in
   plot([1,2,3]);

For more information on `@savefig` decorator, please refer to the end of
this page in Pseudo-Decorators section.

.. todo:: Alright instead of repeating ourselves multiple times and noting
          that sys.stderr gets inserted, can we show an example of the
          :class:`IPython.lib.IPythonTraceback` lexer?

Similarly, :data:`sys.stderr` is inserted.:

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

The following section attempts to execute faulty code, namely the calling
the functions ``ioff()`` and ``ion`` which haven't been defined.


.. todo:: Remove this sentence below like wth?

   Let's at least print the literal text and then show how we suppress the error
   rather than just silently doing so.

If you don't see the next code block then we can surmise that the
`@suppress` decorator is behaving as expected.:

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



Configuring the Build Environment
=================================

I want to put this in the docstrings of those functions with the `env`
parameter that kept tripping me up. (ref)

.. glossary::

   environment
      A structure where information about all documents under the root is saved,
      and used for cross-referencing.  The environment is pickled after the
      parsing stage, so that successive runs only need to read and parse new and
      changed documents.


Supported Pseudo-Decorators
============================

Here are the supported decorators, and any optional arguments they
take.  Some of the decorators can be used as options to the entire
block (e.g. `@verbatim` and `@suppress`), and some only apply to the
line just below them (eg `@savefig`).:

.. _pseudo-decorators:

Decorators Glossary
-------------------------

.. glossary::

   @suppress
       Execute the IPython input block, but :dfn:`@suppress` the input and output
       block from the rendered output.  Also, can be applied to the entire
       ``.. ipython`` block as a directive option with ``:suppress:``.

   @verbatim
       Insert the input and output block in :dfn:`@verbatim`, but auto-increment
       the line numbers. Internally, the interpreter will be fed an empty
       string, so it is a no-op that keeps line numbering consistent.
       Also, can be applied to the entire ``.. ipython`` block as a
       directive option with ``:verbatim:``.

   @savefig
      Save the target of the directive to :dfn:`outfile`.
      *I think I'm just gonna rewrite this entire paragraph.*
      Save the figure to the static directory and insert it into the
      document, possibly binding it into a mini-page and/or putting
      code/figure label/references to associate the code and the figure.
      Takes args to pass to the image directive (*scale*,
      *width*, etc can be ``**kwargs``)

   @doctest
      Compare the pasted in output in the IPython block with the output
      generated at doc build time, and raise errors if they don't
      match. Also, can be applied to the entire ``.. ipython`` block as a
      directive option with ``:doctest:``.

   @suppress
      execute the ipython input block, but suppress the input and output
      block from the rendered output.  Also, can be applied to the entire
      ``..ipython`` block as a directive option with ``:suppress:``.

   @okexcept
      Actually is this a decorator?

   @okwarning
      What about this one?

   @python
      This can't be.


.. todo:: Document the magics.py sphinx extension!!

   The ``.. magic::`` directive doesn't appear to be documented at all.


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

.. confval:: ipython_warning_is_error: [default to True]

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

    The string which specifies if the embedded Sphinx shell should import
    Matplotlib and set the backend. The value specifies a backend that is
    passed to `matplotlib.use()` before any lines in `ipython_execlines` are
    executed. If not specified in conf.py, then the default value of 'agg' is
    used. To use the IPython directive without matplotlib as a dependency, set
    the value to `None`. It may end up that matplotlib is still imported
    if the user specifies so in `ipython_execlines` or makes use of the
    `@savefig` pseudo decorator.

.. confval:: ipython_execlines

    A list of strings to be exec'd in the embedded Sphinx shell. Typical
    usage is to make certain packages always available. Set this to an empty
    list if you wish to have no imports always available. If specified in
    ``conf.py`` as `None`, then it has the effect of making no imports available.

    If omitted from conf.py altogether, then the default value of::

       ['import numpy as np', 'import matplotlib.pyplot as plt']

    is used.

.. confval:: ipython_holdcount

    When the `@suppress` pseudo-decorator is used, the execution count can be
    incremented or not. The default behavior is to hold the execution count,
    corresponding to a value of `True`. Set this to `False` to increment
    the execution count after each suppressed command.

As an example, to use the IPython directive when `matplotlib` is not available,
one sets the backend to `None`:

    `ipython_mplbackend` = `None`


To view the API documentation, continue reading at `sphinx_ipython_api`.

.. Vim: set et:
