:orphan:

=====
Todo
=====

.. module:: todo
   :synopsis: List of improvements

Subcommands in IPython and Jupyter.
===================================

.. program:: ipython

There's a ton that could be done here.
Well I guess sub-apps would be a better name for it but whatever.

Mostly here to note that I think the 'editor' :mod:`~IPython.core.hooks`
doesn't work the way it's supposed to if you want to configure it.

If you run `%edit` in the shell it doesn't provide any arguments, but
it'll complain that it needs a function that accepts 4 positional parameters.

I'm pretty confident it isn't just me calling the function wrong too.
Try this.::

   from IPython import get_ipython
   ip = get_ipython()
   ip.hooks['editor'].chain
   # inspect your hooks look normal
   from IPython.core.hooks import fix_error_editor
   ip.hooks['editor'].add(fix_error_editor)
   %edit # --> complains that it needs 3 more positional parameters

Before I noticed this, I wrote a function that only accepts 1 positional arg,
*which btw...it was the filename duh. I don't know or care what column
number I start at???* and takes optional keyword arguments.

Said the function was getting called wrong as it only accepted 1 positional
and was being called with 4. *sigh*.


.. _history-app:

IPython history
===============

.. cmdoption:: history

Here's some seemingly inconsistent behavior.

.. code-block:: shell
   :emphasize-lines: 1

   $: ipython history
   No subcommand specified. Must specify one of: dict_keys(['trim', 'clear'])
   Manage the IPython history database.

.. code-block:: rst

   Subcommands
   -----------
   Subcommands are launched as `ipython-history cmd [args]`. For information
   on using subcommand 'cmd', do: `ipython-history cmd -h`.


So there we have instructions to use the invocation ``ipython-history``.

.. code-block:: bash

   $: ipython-history -h
   ipython-history: command not found

Erhm. That's confusing.
So how does the `history` command work?

IPython History API
===================

Interact with the IPython :mod:`sqlite3` database.

.. cmdoption:: trim

   Trim the IPython history database to the last 1000 entries.

.. cmdoption:: clear

   Clear the IPython history database, deleting all entries.

Also the original implementation only defines 2 options for the subcommand.

But it would be nice to have options like ``backup`` and :command:`grep`
or something. *Though to be fair the :class:`~IPython.utils.text.SList` class
has a 'grep' method.*

There are a handful of *nice to have* but ultimately pointless functions in
:mod:`IPython.utils` so why not take advantage?


Writing Magics For Our Users
=============================

In the documentation, it specifies the requirements for a magic.
And I quote the ``custommagics`` document.:

   There are two main ways to define your own magic functions: from standalone
   functions and by inheriting from a base class provided by IPython,
   :class:`~IPython.core.magic.Magics`.

It then gives an example.

.. code-block:: ipython

    from IPython.core.magic import (Magics, magics_class,
                                    line_magic,cell_magic, line_cell_magic)

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
            "Magic that works both as %lmagic and as %%cmagic"
            if cell is None:
                print("Called as line magic")
                return line
            else:
                print("Called as cell magic")
                return line, cell
    # In order to actually use these magics, you must register them with a
    # running IPython instance.
    def load_ipython_extension(ipython):
        """
        Any module file that define a function named `load_ipython_extension`
        can be loaded via `%load_ext module.path` or be configured to be
        autoloaded by IPython at startup time.
        """
        # You can register the class itself without instantiating it.  IPython will
        # call the default constructor on it.
        ipython.register_magics(MyMagics)


How can we rewrite the magic implementation so that the decorator `magics_class`
isn't required anymore?

Like if they pass us a string can we not just feed it to our own home-brewed
wrapper function? Off the top of my head I'm guessing something like this.::

   arg, _ = sys.argv[1:]
   if not hasattr(arg, 'load_ext'):   # or whatever interface is expected

      @magics_class
      @functools.wraps
      def wrapped(*args, **kwargs):
          return *args, **kwargs

   shell.register_magic('MyMagic')   # <---- incorrectly passed as a str

   # But in the register_magic method we would do:

   class InteractiveShell:

      ...
      def register_magic(self, *args, **kwargs):
          # Run that interface check with
          if not hasattr(arg, 'load_ext'):   # or whatever interface is expected
              # and then call the wrapped function with the args that were passed to us

              ...
              # the usual stuff


I'm sure that I poorly executed that here; however, after some deliberation,
would it be that hard to do?

Prompt Toolkit
===============

Modify the KeyBindings classes so that the following works.::

    if shell.editing_mode == 'vi':
        # kb.add(load_vi_bindings(), filter=(has_focus(DEFAULT_BUFFER)))
        for i in load_vi_bindings().bindings:
            kb.add(i, filter=(has_focus(DEFAULT_BUFFER)))
    else:
        for i in load_basic_bindings():
            kb.add(i, filter=(has_focus(DEFAULT_BUFFER)))

    # don't do this one of these keys steals <C-d>
    kb = merge_key_bindings([
        load_cpr_bindings(),
        load_basic_bindings(),
        load_mouse_bindings(),
        kb,
    ])

Currently every part fails.::

   kb.add(load_vi_bindings())

   TypeError: object of type 'ConditionalKeyBindings' has no len()

Uh that's really confusing but when you go to
prompt_toolkit.key_binding.key_bindings you'll see a ...wow I can't find the
method that this came from. Whatever. Next!::

   In [39]: from prompt_toolkit.key_binding.defaults import load_basic_bindings
   In [40]: for i in load_basic_bindings():
       ...:     print(i)
       ...:
            TypeError: 'KeyBindings' object is not iterable


This doesn't even feel internally consistent. Alright let's play by his rules.::

   In [42]: _ip.pt_app.app.key_bindings.add()
   AttributeError: '_MergedKeyBindings' object has no attribute 'add'

So if I merge my key bindings at any point I shoot myself in the foot from
adding more later?

Holy hell.


:magic:`alias_magic`
====================

`%alias_magic` is really convenient and makes it possible to create really
short monikers for rather complicated mixes of shell scripts and object-oriented
python. But it doesn't copy over the __doc__ from the old magic.

There's a ton of good information that gets lost going from `%edit` to `%ed` and
`%history` to `%hist`. Anything we can do about that?

