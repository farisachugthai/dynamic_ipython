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
