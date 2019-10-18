.. _sphinx-api-docs:

===============
Sphinx API docs
===============

Sphinx Package
==============

.. automodule:: IPython.sphinxext
   :synopsis: The IPython sphinx package.
   :members:
   :undoc-members:
   :show-inheritance:


Package submodules
==================

.. automodule:: default_profile.sphinxext.ipython_directive
   :synopsis: The IPython sphinx directive.
   :members:
   :undoc-members:
   :show-inheritance:

In addition, here's the longest comment ever. This info totally qualifies
for inclusion in the documentation IMO and I don't know why it's only
a side-note.

.. currentmodule:: default_profile.sphinxext.ipython_directive

.. autoclass:: EmbeddedSphinxShell

In :func:`EmbeddedSphinxShell.run`, the elements of `ret` are eventually
combined such that '' entries correspond to newlines. So if
`processed_output` is equal to '', then the adding it to `ret`
ensures that there is a blank line between consecutive inputs
that have no outputs, as in::

   In [1]: x = 4

   In [2]: x = 5

When there is processed output, it has a '\n' at the tail end. So
adding the output to `ret` will provide the necessary spacing
between consecutive input/output blocks, as in::

   In [1]: x
   Out[1]: 5

   In [2]: x
   Out[2]: 5

When there is :data:`sys.stdout` from the input, it also has a '\n' at the
tail end, and so this ensures proper spacing as well. E.g.:

   In [1]: print x
   5

   In [2]: x = 5

When in verbatim mode, `processed_output` is empty (because
nothing was passed to `IP`. Sometimes the submitted code block has
an ``Out[]`` portion and sometimes it does not.

When it does not, we need to ensure proper spacing, so we have to add
:kbd:`''` to `ret`.

However, if there is an ``Out[]`` in the submitted code, then we do
not want to add a newline as `process_output` has stuff to add.
The difficulty is that `process_input` doesn't know if
`process_output` will be called---so it doesn't know if there is
Out[] in the code block. The requires that we include a hack in
`process_block`. See the comments there.
