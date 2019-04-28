.. _defining_magics:

Defining custom magics
======================

:URL: https://raw.githubusercontent.com/ipython/ipython/523ed2fe58ea5ee9971d2b21df1de33b8cdfa924/docs/source/config/custommagics.rst

There are two main ways to define your own magic functions: from standalone
functions and by inheriting from a base class provided by IPython:
:class:`IPython.core.magic.Magics`. Below we show code you can place in a file
that you load from your configuration, such as any file in the ``startup``
subdirectory of your default IPython profile.

First, let us see the simplest case. The following shows how to create a line
magic, a cell one and one that works in both modes, using just plain functions:

.. sourcecode:: python

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

.. sourcecode:: python

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
            "my line magic"
            print("Full access to the main IPython object:", self.shell)
            print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
            return line

        @cell_magic
        def cmagic(self, line, cell):
            "my cell magic"
            return line, cell

        @line_cell_magic
        def lcmagic(self, line, cell=None):
            "Magic that works both as %lcmagic and as %%lcmagic"
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
        """
        # You can register the class itself without instantiating it.  IPython will
        # call the default constructor on it.
        ipython.register_magics(MyMagics)

If you want to create a class with a different constructor that holds
additional state, then you should always call the parent constructor and
instantiate the class yourself before registration:

.. sourcecode:: python

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


.. sourcecode:: bash

   .
   ├── example_magic
   │   ├── __init__.py
   │   └── abracadabra.py
   └── setup.py

.. sourcecode:: bash

   $ cat example_magic/__init__.py
   """An example magic"""
   __version__ = '0.0.1'

   from .abracadabra import Abracadabra

   def load_ipython_extension(ipython):
       ipython.register_magics(Abracadabra)

.. sourcecode:: bash

    $ cat example_magic/abracadabra.py
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

*Summarized from "Learning IPython for Interactive Computing and Data Visualization 1st ed.pdf""*

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

    The |ip| instance represents the active
    :mod:`IPython` interpreter. Useful methods and attributes include
    :func:`|ip|.register_magics()`, to create new magic commands,
    and ``user_ns``, to access the user namespace. You can
    explore all the instance's attributes interactively from
    :mod:`IPython` with tab completion. For that, you need to execute
    the following command to get the current instance

    .. code-block:: python3

        from IPython import get_ipython
        ip = get_ipython()

    And then access attributes with the ``ip`` object.
