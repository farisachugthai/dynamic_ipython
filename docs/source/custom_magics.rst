.. _defining_magics:

======================
Defining custom magics
======================

Creating IPython Extensions
===============================

*Summarized from "Learning IPython for Interactive Computing and Data
Visualization 1st ed.pdf"*:

   To create an extension, we need to create a Python module in a
   directory, which is in the Python path. A possibility is to put it in
   the current directory, or in your `IPython extensions dir <../../extensions>`_

   An extension implements a
   :func:`IPython.core.magics.extension.load_ipython_extension(ipython)`,
   which takes the current |ip| instance as an argument (and possibly
   :func:`IPython.core.magics.extension.unload_ipython_extension(ipython)`,
   which is called when the extension is unloaded). This instance can be used to register new
   magic commands, access the user namespace, execute code, and so on.
   This loading function is called when the extension is loaded, which
   happens when the command is executed.

   .. ipython::

      %load_ext  # or
      %reload_ext magic

   To automatically load a module when :mod:`IPython` starts,
   we need to add the module name to the ``c.TerminalIPythonApp.extensions``
   list in the :mod:`IPython` configuration file.

   The |ip| instance represents the active
   IPython interpreter. Useful methods and attributes include
   :func:`IPython.core.magic.register_magics()`, to create new magic commands,
   and ``user_ns``, to access the user namespace. You can
   explore all the instance's attributes interactively from
   :mod:`IPython` with tab completion. For that, you need to execute
   the following command to get the current instance

   .. code-block:: python3

       _ip = get_ipython()


Here are 2 useful functuons for registering a magic with the global IPython
instance.

.. code-block:: none

   In [37]: _ip.register_magic_function?
   Signature: _ip.register_magic_function(func, magic_kind='line', magic_name=None)
   Docstring:
   Expose a standalone function as magic function for IPython.

   This will create an IPython magic (line, cell or both) from a
   standalone function.  The functions should have the following
   signatures:

       + For line magics: `def f(line)`
       + For cell magics: `def f(line, cell)`
       + For a function that does both: `def f(line, cell=None)`

   In the latter case, the function will be called with `cell==None` when
   invoked as `%f`, and with cell as a string when invoked as `%%f`.

Magic Function Parameters
-------------------------
func : callable
 Function to be registered as a magic.

magic_kind : str
 Kind of magic, one of 'line', 'cell' or 'line_cell'

magic_name : optional str
 If given, the name the magic will have in the IPython namespace.  By
 default, the name of the function itself is used.

Which allows us the ability to create a magic, line or cell, out of any function.

.. code-block:: none

   In [38]: _ip.register_magics?
   Signature: _ip.register_magics(*magic_objects)
   Docstring:
   Register one or more instances of Magics.

   Take one or more classes or instances of classes that subclass the main
   :class:`~IPython.core.Magic` class, and register them with IPython to use the magic
   functions they provide.  The registration process will then ensure that
   any methods that have decorated to provide line and/or cell magics will
   be recognized with the `%x`/`%%x` syntax as a line/cell magic
   respectively.

   If classes are given, they will be instantiated with the default
   constructor.  If your classes need a custom constructor, you should
   instanitate them first and pass the instance.

   The provided arguments can be an arbitrary mix of classes and instances.

   Parameters
   ----------
   magic_objects : one or more classes or instances

Example usage exists on the official website as well.

Tldr
----
Writing the extension:

- Import the global :mod:`IPython` instance with::

   from IPython import get_ipython

- Create an object with the global ipython app with::

   _ip = get_ipython()

If you want to try out your ipython magics you can do the following:

- Load your magic with::

    ip.magic('load_ext your_magic_name')

- Run your magic with::

    ip.run_line_magic('your_magic_function', 'your_magic_arguments')

*(Optional) Access results of your magic with ip.user_ns (ipython user namespace).*

Admittedly I regularly flood my ``user_ns`` so this might not be viable in all
cases.

However in a testing situation this could prove beneficial.

Alternative Method of Defining Magics with Arguments
----------------------------------------------------
From the IPython team directly. The following is the module docstring for
:mod:`~IPython.core.magic_arguments`.

New magic functions can be defined like so::

    from IPython.core.magic_arguments import (argument, magic_arguments,
        parse_argstring)

    @magic_arguments()
    @argument('-o', '--option', help='An optional argument.')
    @argument('arg', type=int, help='An integer positional argument.')
    def magic_cool(self, arg):
        """ A really cool magic command.

    """
        args = parse_argstring(magic_cool, arg)
        ...

The `@magic_arguments` decorator marks the function as having argparse arguments.
The `@argument` decorator adds an argument using the same syntax as argparse's
`add_argument()` method. More sophisticated uses may also require the
`@argument_group` or `@kwds` decorator to customize the formatting and the
parsing.

Help text for the magic is automatically generated from the docstring and the
arguments::

    In[1]: %cool?
        %cool [-o OPTION] arg

        A really cool magic command.

        positional arguments:
          arg                   An integer positional argument.

        optional arguments:
          -o OPTION, --option OPTION
                                An optional argument.

Inheritance diagram:

.. why am i getting an error 'unknown directive type?
.. inheritance-diagram: IPython.core.magic_arguments
   :parts: 3

Writing Custom Magics
======================

:URL: https://raw.githubusercontent.com/ipython/ipython/523ed2fe58ea5ee9971d2b21df1de33b8cdfa924/docs/source/config/custommagics.rst

There are two main ways to define your own magic functions. From standalone
functions and by inheriting from a base class provided by IPython:

:class:`IPython.core.magic.Magics`

Below, there will be code displayed that demonstrates how to write an extension
and allow it to be automatically loaded.
:ref:`profile_default.startup` subdirectory of your default IPython profile.

First, let us see the simplest case. The following shows how to create a line
magic, a cell one and one that works in both modes, using just plain functions:

.. ipython:: python

    from IPython.core.magic import (register_line_magic, register_cell_magic,
                                    register_line_cell_magic)

    @register_line_magic
    def lmagic(line):
        "my line magic"
        return line

    @register_cell_magic
    def cmagic(line, cell):
        "my cell magic"
        return line, cell

    @register_line_cell_magic
    def lcmagic(line, cell=None):
        "Magic that works both as %lcmagic and as %%lcmagic"
        if cell is None:
            print("Called as line magic")
            return line
        else:
            print("Called as cell magic")
            return line, cell

    # In an interactive session, we need to delete these to avoid
    # name conflicts for automagic to work on line magics.
    del lmagic, lcmagic


You can also create magics of all three kinds by inheriting from the
:class:`IPython.core.magic.Magics` class.  This lets you create magics that can
potentially hold state in between calls, and that have full access to the main
IPython object:

.. ipython:: python

    # This code can be put in any Python module, it does not require IPython
    # itself to be running already.  It only creates the magics subclass but
    # doesn't instantiate it yet.
    from __future__ import print_function
    from IPython.core.magic import (Magics, magics_class, line_magic,
                                    cell_magic, line_cell_magic)

    # The class MUST call this class decorator at creation time
    @magics_class
    class MyMagics(Magics):
        @line_magic
        def lmagic(self, line):
            """My line magic."""
            print("Full access to the main IPython object:", self.shell)
            print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
            return line

        @cell_magic
        def cmagic(self, line, cell):
            """My cell magic."""
            return line, cell

        @line_cell_magic
        def lcmagic(self, line, cell=None):
            """Magic that works both as %lcmagic and as %%lcmagic."""
            if cell is None:
                print("Called as line magic")
                return line
            else:
                print("Called as cell magic")
                return line, cell

    # In order to actually use these magics, you must register them with a
    # running IPython.

    def load_ipython_extension(ipython):
        """
        Any module file that define a function named `load_ipython_extension`
        can be loaded via `%load_ext module.path` or be configured to be
        autoloaded by IPython at startup time.
        You can register the class itself without instantiating it.  IPython will
        call the default constructor on it.
        """
        ipython.register_magics(MyMagics)

If you want to create a class with a different constructor that holds
additional state, then you should always call the parent constructor and
instantiate the class yourself before registration:

.. ipython:: python

    @magics_class
    class StatefulMagics(Magics):
        "Magics that hold additional state"

        def __init__(self, shell, data):
            # You must call the parent constructor
            super(StatefulMagics, self).__init__(shell)
            self.data = data

        # etc...

    def load_ipython_extension(ipython):
        """
        Any module file that define a function named `load_ipython_extension`
        can be loaded via `%load_ext module.path` or be configured to be
        autoloaded by IPython at startup time.
        """
        # This class must then be registered with a manually created instance,
        # since its constructor has different arguments from the default:
        magics = StatefulMagics(ipython, some_data)
        ipython.register_magics(magics)


.. note::

   In early IPython versions 0.12 and before the line magics were
   created using a :func:`define_magic` API function.  This API has been
   replaced with the above in IPython 0.13 and then completely removed
   in IPython 5.  Maintainers of IPython extensions that still use the
   :func:`define_magic` function are advised to adjust their code
   for the current API.


Complete Example
================

Here is a full example of a magic package. You can distribute magics using
setuptools, distutils, or any other distribution tools like `flit
<http://flit.readthedocs.io>`_ for pure Python packages.

.. sourcecode:: none

   .
   ├── example_magic
   │   ├── __init__.py
   │   └── abracadabra.py
   └── setup.py

.. sourcecode:: bash

   $ cat example_magic/__init__.py

.. code-block:: python

   """An example magic"""
   __version__ = '0.0.1'

   from .abracadabra import Abracadabra

   def load_ipython_extension(ipython):
       ipython.register_magics(Abracadabra)

.. sourcecode:: bash

    $ cat example_magic/abracadabra.py

.. code-block:: python

    from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)

    @magics_class
    class Abracadabra(Magics):

        @line_magic
        def abra(self, line):
            return line

        @cell_magic
        def cadabra(self, line, cell):
            return line, cell



Creating IPython Extensions
-------------------------------

*Summarized from "Learning IPython for Interactive Computing and Data Visualization 1st ed.pdf"*

:

    To create an extension, we need to create a Python module in a
    directory, which is in the Python path. A possibility is to put it in
    the current directory, or in your `IPython dir <$IPYTHONDIR/extensions>`_

    An extension implements a :func:`|ip|.load_ipython_extension(ipython)`,
    which takes the current ``|ip|`` instance as an argument (and possibly
    :func:`|ip|.unload_ipython_extension(ipython)` which is called when
    the extension is unloaded).

    This instance can be used to register new magic commands, access the user
    namespace, execute code, and so on.

    This loading function is called when the extension is loaded, which
    happens when the ``%load_ext`` or ``%reload_ext magic`` command is
    executed. To automatically load a module when IPython starts,
    we need to add the module name to the ``c.TerminalIPythonApp.extensions``
    list in the IPython configuration file.

    The |ip| instance represents the active :mod:`IPython` interpreter.
    Useful methods and attributes include |ip|:func:`register_magics()`
    , to create new magic commands, and ``user_ns``, to access the user
    namespace. You can explore all the instance's attributes interactively from
    :mod:`IPython` with tab completion. For that, you need to execute
    the following command to get the current instance.::

        from IPython import get_ipython
        ip = get_ipython()

    And then access attributes with the ``ip`` object.
