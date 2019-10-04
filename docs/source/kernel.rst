.. _kernel:

==============
IPython Kernel
==============
.. highlight:: ipython

.. ipython::

    from traitlets.config import get_config
    c = get_config()

Initially Provided Configuration
================================
From ``ipython kernel --generate-config``.

ConnectionFileMixin(LoggingConfigurable) configuration
------------------------------------------------------

Mixin for configurable classes that work with connection files.

:mod:`json` file in which to store connection info [default: kernel-<pid>.json]

This file will contain the IP, ports, and authentication key needed to connect
clients to this kernel.

By default, this file will be created in the security
dir of the current profile, but can be specified by absolute path.::

    c.ConnectionFileMixin.connection_file = ''

Set the control (ROUTER) port. [default: random]::

    c.ConnectionFileMixin.control_port = 0

Set the heartbeat port. [default: random]::

    c.ConnectionFileMixin.hb_port = 0

Set the iopub (PUB) port [default: random]::

    c.ConnectionFileMixin.iopub_port = 0

Set the kernel's IP address [default localhost]. If the IP address is
something other than localhost, then consoles on other machines will be able
to connect to the kernel, so be careful!::

    c.ConnectionFileMixin.ip = ''

.. todo:: Could we set a private IP if we trust the LAN?

    Need to figure out how that works.

Set the shell (ROUTER) port [default: random]. What's the difference between
the shell_port, the control_port and the hb_port?::

    c.ConnectionFileMixin.shell_port = 0

Set the stdin (ROUTER) port [default: random]::

    c.ConnectionFileMixin.stdin_port = 0

Transport.::

    c.ConnectionFileMixin.transport = 'tcp'


InteractiveShellApp(Configurable) configuration
-----------------------------------------------

A Mixin for applications that start InteractiveShell instances.

Provides configurables for loading extensions and executing files as part of
configuring a Shell environment.

The following methods should be called by the :meth:`initialize` method of the
subclass:

  - :meth:`init_path`
  - :meth:`init_shell` (to be implemented by the subclass)
  - :meth:`init_gui_pylab`
  - :meth:`init_extensions`
  - :meth:`init_code`

Execute the given command string.::

   c.InteractiveShellApp.code_to_run = ''

Run the file referenced by the :envvar:`PYTHONSTARTUP` environment variable
at IPython startup.::

   c.InteractiveShellApp.exec_PYTHONSTARTUP = True

List of files to run at IPython startup.::

   c.InteractiveShellApp.exec_files = []

Lines of code to run at IPython startup.::

   c.InteractiveShellApp.exec_lines = []

A list of dotted module names of IPython extensions to load.::

   c.InteractiveShellApp.extensions = []

Dotted module name of an IPython extension to load.::

   c.InteractiveShellApp.extra_extension = ''

A file to be run.::

   c.InteractiveShellApp.file_to_run = ''

Enable GUI event loop integration with any of ('glut', 'gtk', 'gtk2', 'gtk3',
'osx', 'pyglet', 'qt', 'qt4', 'qt5', 'tk', 'wx', 'gtk2', 'qt4').::

   c.InteractiveShellApp.gui = None

Should variables loaded at startup (by startup files, exec_lines, etc.) be
hidden from tools like `%who`?::

   c.InteractiveShellApp.hide_initial_ns = True

Configure matplotlib for interactive use with the default matplotlib backend.::

   c.InteractiveShellApp.matplotlib = None

.. todo:: We need to test for if we have an X11 server ready to help us out.

Run the module as a script.::

   c.InteractiveShellApp.module_to_run = ''

Pre-load matplotlib and numpy for interactive use, selecting a particular
matplotlib backend and loop integration.::

   c.InteractiveShellApp.pylab = None

If true, IPython will populate the user namespace with numpy, pylab, etc. and
an ``import *`` is done from numpy and pylab, when using pylab mode.

When False, pylab mode should not import any names into the user namespace.::

   c.InteractiveShellApp.pylab_import_all = True

Reraise exceptions encountered loading IPython extensions?::

   InteractiveShellApp.reraise_ipython_extension_failures = True


Jupyter Kernel Config
-----------------------

Run a kernel locally in a subprocess.

Options
-------

Arguments that take values are actually convenience aliases to full
traitlets.config.Configurables, whose aliases are listed on the help line.

For more information on full configurables, see ``--help-all``.

--debug
    set log level to logging.DEBUG (maximize logging output)

--kernel=<Unicode> (KernelApp.kernel_name)
    Default: 'python3'
    The name of a kernel type to start

--ip=<Unicode> (KernelManager.ip)
    Default: ''
    Set the kernel's IP address [default localhost]. If the IP address is
    something other than localhost, then Consoles on other machines will be able
    to connect to the Kernel, so be careful!

Class parameters
----------------

Parameters are set from command-line arguments of the form:
``--Class.trait=value``.

This line is evaluated in Python, so simple expressions
are allowed, e.g.::

   C.a=range(3)

For setting C.a=[0,1,2].

KernelApp options
-----------------

--KernelApp.answer_yes=<Bool>
    Default: `False`
    Answer yes to any prompts.

--KernelApp.config_file=<Unicode>
    Default: ''
    Full path of a config file.

--KernelApp.config_file_name=<Unicode>
    Default: ''
    Specify a config file to load.

--KernelApp.generate_config=<Bool>
    Default: `False`
    Generate default config file.

--KernelApp.kernel_name=<Unicode>
    Default: 'python3'
    The name of a kernel type to start

--KernelApp.log_datefmt=<Unicode>
    Default: '%Y-%m-%d %H:%M:%S'
    The date format used by logging formatters for %(asctime)s

--KernelApp.log_format=<Unicode>
    Default: '[%(name)s]%(highlevel)s %(message)s'
    The Logging format template

--KernelApp.log_level=<Enum>
    Default: 30
    Choices: (0, 10, 20, 30, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    Set the log level by value or name.

KernelManager options
---------------------

--KernelManager.autorestart=<Bool>
    Default: True
    Should we autorestart the kernel if it dies.

--KernelManager.connection_file=<Unicode>
    Default: ''
    :mod:`JSON` file in which to store connection info
    [default: kernel-<pid>.json]
    This file will contain the IP, ports, and authentication key needed to
    connect clients to this kernel. By default, this file will be created in the
    security dir of the current profile, but can be specified by absolute path.

--KernelManager.control_port=<Int>
    Default: 0
    set the control (ROUTER) port [default: random]

--KernelManager.hb_port=<Int>
    Default: 0
    set the heartbeat port [default: random]

--KernelManager.iopub_port=<Int>
    Default: 0
    set the iopub (PUB) port [default: random]

--KernelManager.ip=<Unicode>
    Default: ''
    Set the kernel's IP address [default localhost]. If the IP address is
    something other than localhost, then Consoles on other machines will be able
    to connect to the Kernel, so be careful!

--KernelManager.kernel_cmd=<List>
    Default: []
    DEPRECATED: Use kernel_name instead.
    The :class:`subprocess.Popen` Command to launch the kernel.
    Override this if you have a custom kernel.
    If kernel_cmd is specified in a configuration file, Jupyter does not
    pass any arguments to the kernel, because it cannot make any assumptions
    about the arguments that the kernel understands. In particular, this means
    that the kernel does not receive the option --debug if it given on the
    Jupyter command line.

--KernelManager.shell_port=<Int>
    Default: 0
    set the shell (ROUTER) port [default: random]

--KernelManager.shutdown_wait_time=<Float>
    Default: 5.0
    Time to wait for a kernel to terminate before killing it, in seconds.

--KernelManager.stdin_port=<Int>
    Default: 0
    set the :data:`sys.stdin` (ROUTER) port [default: random]

--KernelManager.transport=<CaselessStrEnum>
    Default: 'tcp'
    Choices: ['tcp', 'ipc']

KernelSpecManager options
-------------------------

--KernelSpecManager.ensure_native_kernel=<Bool>
    Default: `True`
    If there is no Python kernelspec registered and the IPython kernel is
    available, ensure it is added to the spec list.

--KernelSpecManager.kernel_spec_class=<Type>
    Default: 'jupyter_client.kernelspec.KernelSpec'
    The kernel spec class.  This is configurable to allow subclassing of the
    KernelSpecManager for customized behavior.

--KernelSpecManager.whitelist=<Set>
    Default: :func:`set`
    Whitelist of allowed kernel names.
    By default, all installed kernels are allowed.


Autogenerated Documentation
----------------------------

.. automodule:: default_profile.ipython_kernel_config
   :members:
   :undoc-members:
   :show-inheritance:
