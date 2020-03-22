==============
System Aliases
==============

.. currentmodule:: default_profile.startup.20_aliases

To date there are well over 100 aliases manually added to the shell.

These aliases depend on the operating system used as Linux OSes will default
to a :command:`bash` system shell, and Windows will have :command:`dosbatch` or
:command:`powershell` shells.

The Magic System
================

.. magic:: alias

.. magic:: unalias

This document will summarize the specific use of the `%alias` and `%unalias` 
magics.

.. _aliases-overview:

Overview
--------

This module utilizes ``_ip``, the global |ip|
instance, and fills the ``user_ns`` with aliases that are available
in a typical system shell.

Unfortunately, the exact definition of what a system shell is, what language
it responds to, and it's ability to receive and pass along input and output
in pipelines will vary greatly.

As a result, the module needs to test the user's OS, what shell they're using
and what executables are available on the :envvar:`PATH`.

On Unix platforms, it is assumed that the user is using a bash shell.

However on Windows, it is possible that the user has a shell that runs
:command:`dosbatch`, :command:`powershell`, or :command:`bash`.

As a result, the environment variable :envvar:`COMSPEC` will be checked,
and if present, that value is used.

.. _aliases-attributes:

Attributes
----------

ip : |ip|
    A global object representing the active IPython session.
    Contains varying packages as well as the current global namespace.
    Doesn't need to be defined in advance during an interactive session.


.. _aliases-parmeters:

Parameters
----------

:kbd:`%l` : Command-line argument.
   The remainder of the user's input. Commonly referred to in the Jupyter
   documentation as the remaining 'cell'.
   You can use the :kbd:`%l` specifier in an `%alias` definition
   to represent the whole line when the alias is called.

:kbd:`%s` : Command line argument
   A required positional parameter can be given to the alias.


Variable Expansion
==================

From the official IPython documentation.

.. ipython::
   :verbatim:

   In [2]: %alias bracket echo "Input in brackets: <%l>"
   In [3]: bracket hello world
   Input in brackets: <hello world>

Note that we quote when in the configuration file but when running `%alias`
interactively the syntax.

.. ipython::
   :verbatim:

   %alias alias_name cmd

Doesn't require quoting.

Aliases expand Python variables just like system calls using :kbd:`!` 
or :kbd:`!!` do: all expressions prefixed with :kbd:`$` get expanded.
For details of the semantic rules, see :pep:`215` as this is the library used
by IPython for variable expansion.

Meaning that it behaves similarly to the parameter :kbd:`$*`
in typical POSIX shells.

.. seealso::

   :mod:`IPython.core.alias`
       Module where the alias functionality for IPython is defined and the basic
       implementation scaffolded.

.. I think that :command:`declare -f` could have a nice tie in to
   `inspect.is_function` or whatever.

Linux Aliases
-------------

Aliases that have either:

- Only been tested on Linux

- Only natively exist on Linux

- Clobber an existing Windows command

   - cmd has a few overlapping commands like :command:`find`.

   - powershell intentionally has many aliases that match `busybox`
     aliases, with commands like :command:`ls` and :command:`curl` already mapped to
     pwsh builtins.

Packages such as ConEmu or Cmder allow a large number of GNU/Linux built-ins to
exist on Windows, and as a result, the list may not be comprehensive and it may
be that a reasonable portion of these aliases can be successfully executed from
a shell such as Cygwin, MSys2, MinGW, Git on Windows or the Windows Subsystem
for Linux.


Whitespace in Aliases
----------------------

In order to make new subcommands in a way similar to how git allows one to come
up with aliases, I first tried using whitespace in the alias.:

    ('git last', 'git log -1 HEAD %l')

However that simply registers the word ``git`` as an alias and then sends ``git
last`` to the underlying shell, which it may or may not recognize.

Therefore I tried using a hyphen to separate the words, but the python
interpreter uses hyphens as well as whitespace to separate keywords, and as a
result, would split the alias in the middle of the command.

Examples
--------
:

   In [58]: %git_staged?
   Object `staged` not found.

   In [60]: %git_staged?
   Object `%git_staged` not found.


.. _aliases-api-docs:

API Docs
--------

.. function:: validate_alias

   Check attributes and formatting of Alias string.
   Verifies alias through the name and cmd attributes.

   :param alias : Alias
       Alias to verify

   :return nargs:

   :raises `InvalidAliasError`:


.. class:: Alias(alias)

   After a sufficient amount of time, the definition of an alias needed to be
   built on, and a new alias class was defined in this module.

   It is initialized with a mapping of 'name' to 'cmds'.


.. class:: CommonAliases(dict=None)

   A dictionary mapping aliases to system commands, this class implements most
   of the functionality in the module.

   .. method:: git

      100+ git aliases.

      Aliases of note.

      - gcls: git clone [url]

         - This uses the ``%s`` argument to indicate it requires 1 and only 1
           argument as git clone does

      - Note this is in contrast to gcl, or git clone, as that can have
        additional options specified

      - gcim: git commit --message [message]

         - Also uses ``%s``

      Unless otherwise noted every alias uses :kbd:`%l` to allow the user to specify
      any relevant options or flags on the command line as necessary.

      :returns user_aliases : A list of tuples
         The format of IPython aliases got taken it's logical conclusion
         and probably pushed a little further than that.



Autogenerated Documentation
---------------------------

.. automodule:: default_profile.startup.20_aliases
   :synopsis: Generate OS specific aliases to aide in use as a system shell.
   :members:
   :undoc-members:
   :show-inheritance:

