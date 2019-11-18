===========
Subcommands
===========

.. module:: subcommands
   :synopsis: The variety of subcommands that can be given to ipython

Subcommands in IPython and Jupyter.

There's a ton that could be done here. A todo for now.

Well I guess sub-apps would be a better name for it but whatever.

Mostly here to note that I think the 'editor' hook doesn't work the way
it's supposed to if you want to configure it.

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


So there we have instructions to use the invocation ``ipython-history``.::

   $: ipython-history -h
   ipython-history: command not found


Erhm. That's confusing.

So how does the `history` command work?


IPython History API
-------------------

Interact with the IPython :mod:`sqlite3` database.

.. program:: history

.. option:: trim

       Trim the IPython history database to the last 1000 entries.

.. option:: clear

       Clear the IPython history database, deleting all entries.


So where is this initially implemented?

.. todo:: ipython-history command line definition

       Where in the source code is this set up?

Also the original implementation only defines 2 options for the subcommand.

But it would be nice to have options like ``backup`` and `grep` or something.

There are a handful of *nice to have* but ultimately pointless functions in
:mod:`IPython.utils` so why not take advantage?
