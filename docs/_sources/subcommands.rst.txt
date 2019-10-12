===========
Subcommands
===========

.. module:: subcommands
   :synopsis: The variety of subcommands that can be given to ipython

Subcommands in IPython and Jupyter.

Theres a ton that could be done here. A todo for now.


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
