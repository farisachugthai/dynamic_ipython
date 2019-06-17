=================
Developer's Notes
=================

.. tip::

   While working in Vim, the following commands can be useful for building documentation.

Building Documentation
======================

.. highlight:: vim

.. code-block::

   :let &makeprg = 'sphinx-build '
   :cd docs                " assuming set shellslash has been run if necessary
   :make -b html . ../build

Generally it's more difficult to specify parameters in the ``makeprg`` option
than it is to write them out manually on the cmdline.

In addition, ``makeprg`` is not an option one is allowed to set in a modeline.

.. there's not a clean way to do this but
.. Vim: set makeprg=sphinx-build -b html . ../build
.. damnit i don't think you're allowed to set it in a modeline!
.. besides we needed
.. let &makeprg = 'sphinx-build -b html . ../build'
