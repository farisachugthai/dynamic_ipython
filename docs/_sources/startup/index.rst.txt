=================
IPython's Startup
=================

These are the auto-generated API docs for IPython's startup.

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :caption: List of IPython startup files

   rehashx
   easy_import
   ipython-logger
   help_helpers
   aliases
   41_numpy
   42_pandas
   sysexcept

The first script to run invokes `%rehashx` which initializes
:mod:`IPython` with all of the commands that the system shell knows.

By invoking `%rehashx` at the beginning of startup, all system commands
are added as well, which regularly adds well over 1000 commands to the shell.

The IPython team cleverly remembers to also check the environment variable
:envvar:`PATHEXT` on Windows devices as it indicates to the system which
files are executable without requiring the typical Unix file permissions
system.

Continue reading on at :doc:`rehashx`.
