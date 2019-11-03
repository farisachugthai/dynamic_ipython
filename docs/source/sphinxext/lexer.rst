.. _console_lexer:

=========================
New IPython Console Lexer
=========================

.. versionadded:: 2.0.0

The :mod:`IPython` console lexer has been rewritten and now supports
syntax highlighting and documentation builds for a :mod:`traceback`
with customized input/output prompts. An entire suite of lexers is now
available at :mod:`IPython.lib.lexers`. These include:

.. py:class:: IPythonLexer

  Lexers for pure IPython (python + magic/shell commands)

.. py:class:: IPython3Lexer

  Lexers for pure IPython (python + magic/shell commands)

.. py:class:: IPythonPartialTracebackLexer

  Supports 2.x and 3.x via the keyword `python3`. The partial traceback
  lexer reads everything but the Python code appearing in a traceback.

.. py:class:: IPythonTracebackLexer

  Supports 2.x and 3.x via the keyword `python3`.
  The full lexer combines the partial lexer with an IPython lexer.

.. py:class:: IPythonConsoleLexer

  A lexer for IPython console sessions, with support for tracebacks.
  Supports 2.x and 3.x via the keyword `python3`.

.. py:class:: IPyLexer

  A friendly lexer which examines the first line of text and from it,
  decides whether to use an IPython lexer or an IPython console lexer.
  Supports 2.x and 3.x via the keyword `python3`.


IPython Console Highlighting
============================

Previously, the :class:`IPythonConsoleLexer` class was available at
:mod:`IPython.sphinxext.ipython_console_hightlight`.  It was inserted
into Pygments' list of available lexers under the name ``ipython``.


.. note::
   It should be mentioned that this name is inaccurate, since an IPython
   console session is not the same as IPython code (which itself is a
   superset of the Python language).

Now, the Sphinx extension inserts two console lexers into Pygments' list of
available lexers. Both are `IPyLexer` instances under the names:
*ipython* and *ipython3*.


As a result, code blocks such as:

.. code-block:: rst

    .. code-block:: ipython

        In [1]: 2**2
        Out[1]: 4

Will continue to work as before, but now, they will also properly highlight
tracebacks.  For pure IPython code, the same lexer will also work:

.. code-block:: rst

    .. code-block:: ipython

        x = ''.join(map(str, range(10)))
        !echo $x


Using the IPython Lexer in a Sphinx Project
===========================================

.. todo fix wording these 2 paragraphs are clunky

Let's see an example of how to document issues users may run into while
working with some particular piece of software by utilizing they
Sphinx project along with the IPython console lexer to highlight
a :mod:`traceback`.

Running :command:`sphinx-quickstart` will generate a ``conf.py`` file
in the directory that a user indicates is the ``sourcedir`` for a Sphinx
application.

Inside of that ``conf.py`` file, let's add a `setup` function to extend the
lexers available to use.

.. function:: setup

   Configures the sphinx shell that autogenerates documentation as needed.

For a project that hasn't defined a `setup` function in the
``conf.py`` file, define a function that accepts a
`sphinx.application.Sphinx` object like so.::

   def setup(app):
       """Use the IPyLexer."""
       app.add_lexer('ipythontb', IPythonTracebackLexer)
       app.add_lexer('ipython', IPyLexer)

By placing these options in our `setup` function, we can add 'ipython' and
'ipythontb' as options to various directives, such as :rst:dir:`sourcecode` and
:rst:dir:`code-block`.

Now one can use the following in an .rst file.

.. code-block:: rst

   .. code-block:: ipythontb

      In [1]: x = 1/0

      ZeroDivisionError: invalid syntax

Although the names can be confusing (as mentioned above), their
continued use is, in part, to maintain backwards compatibility and to
aid typical usage.

If a project needs to make Pygments aware of more than
just the :class:`IPyLexer` class, then one should not make the
:class:`IPyLexer` class available under the name `ipython`.

.. why not? I really don't know what the hell this is trying to say.


See Also
--------
.. seealso::

   :mod:`IPython.sphinxext.ipython_console_highlighting`
   :mod:`IPython.sphinxext.ipython_directive`


To learn more about the IPython lexer and how it works in reStructured text
documents parsed by Docutils or Sphinx, see :doc:`ipython_sphinx_directive`.
