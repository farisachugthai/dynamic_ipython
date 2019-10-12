=================
IPython Startup
=================
.. module:: startup
   :synopsis: Index the startup files.

These are the auto-generated API docs for IPython's startup.


.. toctree::
   :maxdepth: 1
   :titlesonly:
   :caption: List of IPython startup files

   rehashx
   easy_import
   ipython-logger
   help_helpers
   aliases
   fzf
   setup_readline
   41_numpy
   42_pandas
   matplotlib_rc
   sysexcept


IPython Config
==============

Before delving into the startup files, the API for the main IPython config file
will be discussed.

This is simply the file that's generated when ``ipython --generate-config``
is run on the command line.

.. automodule:: default_profile.ipython_config
   :synopsis: First module executed from userspace in IPython startup.
   :members:
   :undoc-members:
   :show-inheritance:


Startup
=======

The first script to run invokes `%rehashx` which initializes
:mod:`IPython` with all of the commands that the system shell knows.

By invoking `%rehashx` at the beginning of startup, all system commands
are added as well, which regularly adds well over 1000 commands to the shell.

The IPython team cleverly remembers to also check the environment variable
:envvar:`PATHEXT` on Windows devices as it indicates to the system which
files are executable without requiring the typical Unix file permissions
system.

Continue reading on at :doc:`rehashx`.
