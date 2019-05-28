======
README
======

.. module:: extensions-readme
   :synopsis: Summary of all IPython extensions.

Creating IPython Extensions
-------------------------------
*Summarized from "Learning IPython for Interactive Computing and Data
Visualization 1st ed.pdf"*:

   To create an extension, we need to create a Python module in a
   directory, which is in the Python path. A possibility is to put it in
   the current directory, or in your `IPython dir <IPYTHONDIR/extensions>`_

   An extension implements a :function:`load_ipython_extension(ipython)`, which
   takes the current ``InteractiveShell`` instance as an argument (and possibly
   :function:`unload_ipython_extension(ipython)`, which is called when
   the extension is unloaded). This instance can be used to register new
   magic commands, access the user namespace, execute code, and so on.
   This loading function is called when the extension is loaded, which
   happens when the

.. ipython::

  %load_ext  # or
  %reload_ext magic

command is executed. To automatically load a module when :mod:`IPython` starts,
we need to add the module name to the ``c.TerminalIPythonApp.extensions``
list in the :mod:`IPython` configuration file.

The ``InteractiveShell`` instance represents the active
IPython interpreter. Useful methods and attributes include
:function:`register_magics()`, to create new magic commands,
and ``user_ns``, to access the user namespace. You can
explore all the instance's attributes interactively from
:mod:`IPython` with tab completion. For that, you need to execute
the following command to get the current instance

.. code-block:: python3

   _ip = get_ipython()


Here are 2 useful functions for registering a magic with the global IPython
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

Parameters
----------
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

.. inheritance-diagram:: IPython.core.magic_arguments
   :parts: 3
