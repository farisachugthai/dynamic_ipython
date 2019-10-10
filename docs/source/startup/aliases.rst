==============
System Aliases
==============

To date there are well over 100 aliases manually added to the shell.

These aliases depend on the operating system used as Linux OSes will default
to a :command:`bash` system shell, and Windows will have :command:`dosbatch` or
:command:`powershell` shells.


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


.. _aliases-notes:

Notes
------

When writing aliases, an `%alias` definition can take various string
placeholders. As per the official documentation:


.. _aliases-attributes:

Attributes
----------

_ip : |ip|
    A global object representing the active IPython session.
    Contains varying packages as well as the current global namespace.
    Doesn't need to be defined in advance during an interactive session.


.. _aliases-parmeters:

`%alias` magic
==============
.. magic:: alias

The official IPython documentation notes::

    In [2]: %alias bracket echo "Input in brackets: <%l>"
    In [3]: bracket hello world
    Input in brackets: <hello world>

Note that we quote when in the configuration file but when running `%alias`
interactively the syntax '`%alias` alias_name cmd' doesn't require quoting.

Aliases expand Python variables just like system calls using ! or !!
do: all expressions prefixed with '$' get expanded.  For details of
the semantic rules, see :pep:`215`:

This is the library used by IPython for variable expansion.

Parameters
----------
``%l`` : Command-line argument.
    You can use the ``%l`` specifier in an ``%alias`` definition
    to represent the whole line when the alias is called.

Meaning that it behaves similarly to the parameter :kbd:`$*`
in typical POSIX shells.

Alternatively the parameter:
``%s``
can be given.

.. todo:: Does the magic directive allow for one to document parameters and
          the like? If not, it should!

See Also
--------
.. seealso::

   :mod:`IPython.core.alias`
       Module where the alias functionality for IPython is defined and the basic
       implementation scaffolded.


.. todo:: Define alias

   A function that wraps around |ip| and
   :func:`IPython.core.interactiveshell.InteractiveShell.MagicsManager.define_alias`
   and checks for whether the executable is on the :envvar:`PATH` all in one swoop.


Below is the source code for the function
:func:`IPython.core.magics.define_alias()` that is invoked here.::

   def define_alias(self, name, cmd):
       # Define a new alias after validating it.
       # This will raise an :exc:`AliasError` if there are validation
       # problems.
       caller = Alias(shell=self.shell, name=name, cmd=cmd)
       self.shell.magics_manager.register_function(caller, magic_kind='line',
       magic_name=name)


Roadmap
-------

Create a class with instance attributes for `sys.platform`.
Break linux up like so::

    class AliasOSAgnostic:

        def __init__(self):
            self._sys.platform = sys.platform().lower()

        @property
        def has_alias(self):
            return ....

    class LinuxAlias(AliasOSAgnostic):

        def busybox(self):
            aliases = [
                ('cd', 'cd foo %l'),
                ...
                ('ls', 'ls -F --color=always %l)
            ]

        def standardubuntu(self):
            aliases = [
                ('ag', 'ag -l %l')
                ('rg', 'way too many options')
            ]

Then maybe implement either a factory function or a factory manager but
I haven't fleshed that part out in my head.

This may have to take the backburner as I reorganize the rest of
the repo.


If you're breaking up Linux functionality, may I recommend the
following man page to reference?:


   BASH-BUILTINS(7)          Miscellaneous Information Manual          BASH-BUILTINS(7)

   NAME
         bash-builtins - bash built-in commands, see bash(1)

   SYNOPSIS
         bash defines the following built-in commands: :, ., [, alias, bg, bind,
         break, builtin, case, cd, command, compgen, complete, continue,
         declare, dirs, disown, echo, enable, eval, exec, exit, export, fc, fg,
         getopts, hash, help, history, if, jobs, kill, let, local, logout, popd,
         printf, pushd, pwd, read, readonly, return, set, shift, shopt, source,
         suspend, test, times, trap, type, typeset, ulimit, umask, unalias,
         unset, until, wait, while.


I think that :command:`declare -f` could have a nice tie in to
`inspect.is_function()` or whatever.


.. _aliases-api-docs:

Autogenerated Documentation
---------------------------

.. automodule:: default_profile.startup.20_aliases
   :members:
   :undoc-members:
   :show-inheritance:
