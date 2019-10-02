=======
API Doc
=======

.. module:: ipython_directive
   :synopsis: API docs for the IPython directive.

As stated on the `Sphinx documentation
<http://www.sphinx-doc.org/en/master/extdev/markupapi.html#docutils.parsers.rst.Directive>`_

Directives are handled by classes derived from
``docutils.parsers.rst.Directive``.

They have to be registered by an extension using
:meth:`.Sphinx.add_directive` or :meth:`.Sphinx.add_directive_to_domain`.

.. module:: docutils.parsers.rst

.. class:: Directive

The markup syntax of the new directive is determined by the follow five class
attributes:

.. autoattribute:: required_arguments
.. autoattribute:: optional_arguments
.. autoattribute:: final_argument_whitespace
.. autoattribute:: option_spec

Option validator functions take a single parameter, the option argument
(or ``None`` if not given), and should validate it or convert it to the
proper form.  They raise :exc:`ValueError` or :exc:`TypeError` to indicate
failure.

There are several predefined and possibly useful validators in the
:mod:`docutils.parsers.rst.directives` module.

.. autoattribute:: has_content

New directives must implement the :meth:`run` method:

.. method:: run()

This method must process the directive arguments, options and content, and
return a list of Docutils/Sphinx nodes that will be inserted into the
document tree at the point where the directive was encountered.

Instance attributes that are always set on the directive are:

.. attribute:: name

   The directive name (useful when registering the same directive
   class under multiple names).

.. attribute:: arguments

   The arguments given to the directive, as a list.

.. attribute:: options

   The options given to the directive, as a dictionary mapping
   option names to validated/converted values.

.. attribute:: content

   The directive content, if given, as a :class:`.ViewList`.

.. attribute:: lineno

   The absolute line number on which the directive appeared. This
   is not always a useful value; use :attr:`srcline` instead.

.. attribute:: content_offset

   Internal offset of the directive content. Used when calling
``nested_parse`` (see below).

.. attribute:: block_text

   The string containing the entire directive.

.. attribute:: state
               state_machine

   The state and state machine which controls the parsing. Used for
   ``nested_parse``.


.. autosummary:: IPython.sphinx.ipython_directive.IPythonDirective
