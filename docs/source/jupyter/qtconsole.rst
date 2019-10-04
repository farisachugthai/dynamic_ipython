Jupyter QTConsole
=================

.. module:: jupyter_conf.jupyter_qtconsole_config
    :synopsis: Set up QTConsole.


connectionFileMixin(LoggingConfigurable) configuration
------------------------------------------------------

:class:`~qtconsole.connectionFileMixin` --- Mixin for configurable
classes that work with connection files

:mod:`json` file in which to store connection info.

[default: kernel-<pid>.json]

This file will contain the IP, ports, and authentication key needed to connect
clients to this kernel. By default, this file will be created in the security
dir of the current profile, but can be specified by absolute path.::

   c.ConnectionFileMixin.connection_file = ''

Set the control (ROUTER) port [default: random]::

   c.ConnectionFileMixin.control_port = 0

Set the heartbeat port [default: random]::

   c.ConnectionFileMixin.hb_port = 0

Set the iopub (PUB) port [default: random]::

   c.ConnectionFileMixin.iopub_port = 0

Set the kernel's IP address [default localhost]. If the IP address is
something other than localhost, then Consoles on other machines will be able
to connect to the Kernel, so be careful!::

   c.ConnectionFileMixin.ip = ''

Set the shell (ROUTER) port [default: random]::

   c.ConnectionFileMixin.shell_port = 0

Set the stdin (ROUTER) port [default: random]::

   c.ConnectionFileMixin.stdin_port = 0


Initializing Jupyter QTConsole
--------------------------------

The initial entry point for :command:`jupyter-qtconsole` is in the following::

    from qtconsole.qtconsole.app import main
    # Also there's just a lot going on there
    from qtconsole import qtconsole
    the_sauce = dir(qtconsole)


Display
-------

The following is from the Jupyter QTConsole help.

For example, if using the IPython kernel, there are functions available for
object display::

    In [4]: from IPython.display import display
    In [5]: from IPython.display import display_png, display_svg

Python objects can simply be passed to these functions and the appropriate
representations will be displayed in the console as long as the objects know
how to compute those representations. The easiest way of teaching objects how
to format themselves in various representations is to define special methods
such as: ``_repr_svg_`` and ``_repr_png_``. IPython's display formatters
can also be given custom formatter functions for various types::

    In [#]: from IPython import get_ipython
    In [6]: ip = get_ipython()
    In [7]: png_formatter = ip.display_formatter.formatters['image/png']
    In [8]: png_formatter.for_type(Foo, foo_to_png)

For further details, see :mod:`IPython.core.formatters`.
