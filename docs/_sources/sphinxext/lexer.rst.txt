.. _console_lexer:

=========================
New IPython Console Lexer
=========================

.. versionadded:: 2.0.0

The :mod:`IPython` console lexer has been rewritten and now supports
syntax highglighting and documentation builds for a :mod:`traceback`
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
`ipython` and `ipython3`.

.. wait what changed? Are we saying that in the past it used to insert lexers into pygments through the name ipython? Because that sounds like what it does now?

As a result, code blocks such as:

.. code-block:: rst

    .. code-block:: ipython

        In [1]: 2**2
        Out[1]: 4

will continue to work as before, but now, they will also properly highlight
tracebacks.  For pure IPython code, the same lexer will also work:

.. code-block:: rst

    .. code-block:: ipython

        x = ''.join(map(str, range(10)))
        !echo $x


Using the IPython Lexer in a Sphinx Project
===========================================

Let's see an example of how to utilize the Sphinx project along
with the IPython console lexer to highlight a :mod:`traceback` and
document issues any users may run into while working with some
particular piece of software.

In the ``conf.py`` file that running :command:`sphinx-quickstart` will
generate, let's add a `setup` function.

.. function:: setup

   Configures the sphinx shell that autogenerates documentation as needed.

For a project that hasn't defined a `setup` function in the
``conf.py`` file, define a function that accepts a
`sphinx.application.Sphinx` object like so.::

   def setup(app):
      """Use the IPyLexer."""
    app.add_lexer('ipythontb', IPythonTracebackLexer)
    app.add_lexer('ipy', IPyLexer)

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

Use ``ipy`` or some other non-conflicting value.

**WAIT WHAT? Read this out loud and tell me it doesn't make sense.**

Since the first line of the block did not begin with a standard IPython
console prompt, the entire block is assumed to consist of IPython code
instead.


See Also
--------
.. seealso::

   :mod:`IPython.sphinxext.ipython_console_highlighting`
   :mod:`IPython.sphinxext.ipython_directive`


To learn more about the IPython lexer and how it works in reStructured text
documents parsed by Docutils or Sphinx, see :doc:`sphinxext`.
