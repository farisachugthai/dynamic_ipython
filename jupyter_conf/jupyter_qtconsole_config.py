"""Configuration file for jupyter-qtconsole."""
import logging
import os
from pathlib import Path
import shutil
import sys

import traitlets
from traitlets.config import get_config

# I think we can safely assume this one
try:

    from jupyter_core.paths import get_home_dir

    from jupyter_client.manager import KernelManager, start_new_kernel

    # Something in this is throwing an error
    from jupyter_client.session import Session
except ImportError:
    sys.exit()

try:
    from gruvbox.gruvbox import GruvboxStyle
except ImportError:
    GruvboxStyle = None


# Globals:

home = get_home_dir()
c = get_config()

logging.basicConfig(level=logging.WARNING)


# ------------------------------------------------------------------------------
# ConnectionFileMixin(LoggingConfigurable) configuration
# ------------------------------------------------------------------------------

# Mixin for configurable classes that work with connection files

# JSON file in which to store connection info [default: kernel-<pid>.json]

# This file will contain the IP, ports, and authentication key needed to connect
# clients to this kernel. By default, this file will be created in the security
# dir of the current profile, but can be specified by absolute path.
# c.ConnectionFileMixin.connection_file = ''

# set the control (ROUTER) port [default: random]
# c.ConnectionFileMixin.control_port = 0

# set the heartbeat port [default: random]
# c.ConnectionFileMixin.hb_port = 0

# set the iopub (PUB) port [default: random]
# c.ConnectionFileMixin.iopub_port = 0

# Set the kernel's IP address [default localhost]. If the IP address is
# something other than localhost, then Consoles on other machines will be able
# to connect to the Kernel, so be careful!
# c.ConnectionFileMixin.ip = ''

# set the shell (ROUTER) port [default: random]
# c.ConnectionFileMixin.shell_port = 0

# set the stdin (ROUTER) port [default: random]
# c.ConnectionFileMixin.stdin_port = 0

# c.ConnectionFileMixin.transport = 'tcp'

# -----------------------------------------------------------------------------
# KernelManager(ConnectionFileMixin) configuration
# -----------------------------------------------------------------------------

# Manages a single kernel in a subprocess on this host.
#
#  This version starts kernels with Popen.

# Should we autorestart the kernel if it dies.
# c.KernelManager.autorestart = True

# DEPRECATED: Use kernel_name instead.
#
#  The Popen Command to launch the kernel. Override this if you have a custom
#  kernel. If kernel_cmd is specified in a configuration file, Jupyter does not
#  pass any arguments to the kernel, because it cannot make any assumptions about
#  the arguments that the kernel understands. In particular, this means that the
#  kernel does not receive the option --debug if it given on the Jupyter command
#  line.
# c.KernelManager.kernel_cmd = []

# Time to wait for a kernel to terminate before killing it, in seconds.
# c.KernelManager.shutdown_wait_time = 5.0

# -----------------------------------------------------------------------------
# ZMQTerminalIPythonApp(JupyterApp,JupyterConsoleApp) configuration
# -----------------------------------------------------------------------------

# Where did this go?

# -----------------------------------------------------------------------------
# ZMQTerminalInteractiveShell(SingletonConfigurable) configuration
# -----------------------------------------------------------------------------

# Text to display before the first prompt. Will be formatted with variables
#  {version} and {kernel_banner}.
c.ZMQTerminalInteractiveShell.banner = ""

# c.ZMQTerminalInteractiveShell.callable_image_handler = None

# Set to display confirmation dialog on exit. You can always use 'exit' or
#  'quit', to force a direct exit without any confirmation.
# Jupyter Console is complaining that ZMQTerminal doesn't recognize this option?
# c.ZMQTerminalInteractiveShell.confirm_exit = False

# Shortcut style to use at the prompt. 'vi' or 'emacs'.
# c.ZMQTerminalInteractiveShell.editing_mode = 'emacs'

# The name of a Pygments style to use for syntax highlighting
try:
    from gruvbox.style import GruvboxDarkHard
except (ImportError, ModuleNotFoundError):
    c.ZMQTerminalInteractiveShell.highlighting_style = "friendly"
else:
    c.ZMQTerminalInteractiveShell.highlighting_style = "Gruvbox"

# Override highlighting format for specific tokens
# c.ZMQTerminalInteractiveShell.highlighting_style_overrides = {}

# How many history items to load into memory
c.ZMQTerminalInteractiveShell.history_load_length = 5000

# Whether to include output from clients other than this one sharing the same
#  kernel.
#
#  Outputs are not displayed until enter is pressed.
c.ZMQTerminalInteractiveShell.include_other_output = True

# Timeout (in seconds) for giving up on a kernel's is_complete response.
#
#  If the kernel does not respond at any point within this time, the kernel will
#  no longer be asked if code is complete, and the console will default to the
#  built-in is_complete test.
# c.ZMQTerminalInteractiveShell.kernel_is_complete_timeout = 1

# Timeout for giving up on a kernel (in seconds).
#
#  On first connect and restart, the console tests whether the kernel is running
#  and responsive by sending kernel_info_requests. This sets the timeout in
#  seconds for how long the kernel can take before being presumed dead.
# c.ZMQTerminalInteractiveShell.kernel_timeout = 60

# Preferred object representation MIME type in order.  First matched MIME type
#  will be used.
# c.ZMQTerminalInteractiveShell.mime_preference = ['image/png', 'image/jpeg', 'image/svg+xml']

# Prefix to add to outputs coming from clients other than this one.
#
#  Only relevant if include_other_output is True.
# c.ZMQTerminalInteractiveShell.other_output_prefix = '[remote] '

# Use simple fallback prompt. Features may be limited.
# c.ZMQTerminalInteractiveShell.simple_prompt = False

# Command to invoke an image viewer program when you are using 'stream' image
#  handler.  This option is a list of string where the first element is the
#  command itself and reminders are the options for the command.  Raw image data
#  is given as STDIN to the program.
# c.ZMQTerminalInteractiveShell.stream_image_handler = []

# Command to invoke an image viewer program when you are using 'tempfile' image
#  handler.  This option is a list of string where the first element is the
#  command itself and reminders are the options for the command.  You can use
#  {file} and {format} in the string to represent the location of the generated
#  image file and image format.
# c.ZMQTerminalInteractiveShell.tempfile_image_handler = []

# Use 24bit colors instead of 256 colors in prompt highlighting. If your
#  terminal supports true color, the following command should print 'TRUECOLOR'
#  in orange: printf "\x1b[38;2;255;100;0mTRUECOLOR\x1b[0m\n"
c.ZMQTerminalInteractiveShell.true_color = True

# Whether to use the kernel's is_complete message handling. If False, then the
#  frontend will use its own is_complete handler.
# c.ZMQTerminalInteractiveShell.use_kernel_is_complete = True

# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
c.Application.log_datefmt = "%Y-%m-%d %H:%M:%S"

# The Logging format template
c.Application.log_format = "%(pid)s [%(name)s] %(highlevel)s %(message)s"

# Set the log level by value or name.
c.Application.log_level = 20

# ------------------------------------------------------------------------------
# JupyterApp(Application) configuration
# ------------------------------------------------------------------------------

# Base class for Jupyter applications

# Answer yes to any prompts.
# c.JupyterApp.answer_yes = False

# Full path of a config file.
# c.JupyterApp.config_file = ''

# Specify a config file to load.
# c.JupyterApp.config_file_name = ''

# Generate default config file.
# c.JupyterApp.generate_config = False

# ------------------------------------------------------------------------------
# JupyterQtConsoleApp(JupyterApp,JupyterConsoleApp) configuration
# ------------------------------------------------------------------------------

# Whether to display a banner upon starting the QtConsole.
c.JupyterQtConsoleApp.display_banner = False

# Start the console window with the menu bar hidden.
# c.JupyterQtConsoleApp.hide_menubar = False

# Start the console window maximized.
# c.JupyterQtConsoleApp.maximize = False

# Use a plaintext widget instead of rich text (plain can't print/save).
# c.JupyterQtConsoleApp.plain = False

# path to a custom CSS stylesheet
# c.JupyterQtConsoleApp.stylesheet = ''


def ConsoleWidgetDoc():
    """
    -----------------------------------------------------------------------
    consoleWidget(NewBase) configuration

    -----------------------------------------------------------------------

    An abstract base class for console-type widgets. This class has functionality
     for:

         * Maintaining a prompt and editing region
         * Providing the traditional Unix-style console keyboard shortcuts
         * Performing tab completion
         * Paging text
         * Handling ANSI escape codes

    ConsoleWidget also provides a number of utility methods that will be
    convenient to implementors of a console-style widget.

    Surprisingly windows handles this correctly
    Whether to process ANSI escape codes.::

        c.ConsoleWidget.ansi_codes = True

    The following is for ConsoleWidget.buffer_size:

    The maximum number of lines of text before truncation. Specifying a non-
    positive number disables text truncation (not recommended).

    Here's some inspiration for decorating the console.:

    >>> from qtconsole import styles
    >>> styles.default_template

    I think it's :mod:`JSON` but it doesn't load from :func:`json.loads`.
    Here's what it looks like.

    .. todo:: don't do this

    .. ipython::
        :okexcept:

    >>> json.loads(styles.default_template)
    >>> from pprint import pprint
    >>> pprint(styles.default_template)

    """
    pass


c.ConsoleWidget.ansi_codes = True

# The maximum number of lines of text before truncation. Specifying a non-
#  positive number disables text truncation (not recommended).
c.ConsoleWidget.buffer_size = 1000

# The height of the console at start time in number of characters (will double
#  with `vsplit` paging)
c.ConsoleWidget.console_height = 50

# The width of the console at start time in number of characters (will double
#  with `hsplit` paging)
c.ConsoleWidget.console_width = 120

# Whether to automatically execute on syntactically complete input.
#
# If False, Shift-Enter is required to submit each execution. Disabling this is
# mainly useful for non-Python kernels, where the completion check would be
# wrong.
# c.ConsoleWidget.execute_on_complete_input = True

# The font family to use for the console. On OSX this defaults to Monaco, on
#  Windows the default is Consolas with fallback of Courier, and on other
#  platforms the default is Monospace.

# I wonder if we can give multiple values
# We cant. Also don't use this it's genuinely impossible to read
c.ConsoleWidget.font_family = "Source Code Pro "
# c.ConsoleWidget.font_family = "Hack"


# The font size. If unconfigured, Qt will be entrusted with the size of the
#  font.
c.ConsoleWidget.font_size = 11

# The type of completer to use. Valid values are:
#
#  'plain'   : Show the available completion as a text list
#              Below the editing area.
#  'droplist': Show the completion in a drop down list navigable
#              by the arrow keys, and from which you can select
#              completion by pressing Return.
#  'ncurses' : Show the completion as a text list which is navigable by
#              `tab` and arrow keys.
c.ConsoleWidget.gui_completion = "droplist"

# Whether to include output from clients other than this one sharing the same
#  kernel.
#
#  Outputs are not displayed until enter is pressed.
# Now needs to be true due to jupyter-vim plugin
c.ConsoleWidget.include_other_output = True

# The type of underlying text widget to use. Valid values are 'plain', which
#  specifies a QPlainTextEdit, and 'rich', which specifies a QTextEdit.
c.ConsoleWidget.kind = "rich"

# Prefix to add to outputs coming from clients other than this one.
#
#  Only relevant if include_other_output is True.
c.ConsoleWidget.other_output_prefix = "[Nvim:] "

# The type of paging to use. Valid values are:
#
#  'inside'
#     The widget pages like a traditional terminal.
#  'hsplit'
#     When paging is requested, the widget is split horizontally. The top
#     pane contains the console, and the bottom pane contains the paged text.
#  'vsplit'
#     Similar to 'hsplit', except that a vertical splitter is used.
#  'custom'
#     No action is taken by the widget beyond emitting a
#     'custom_page_requested(str)' signal.
#  'none'
#     The text is written directly to the console.
c.ConsoleWidget.paging = "vsplit"

# ------------------------------------------------------------------------------
# HistoryConsoleWidget(ConsoleWidget) configuration
# ------------------------------------------------------------------------------

# A ConsoleWidget that keeps a history of the commands that have been executed
#  and provides a readline-esque interface to this history.

c.HistoryConsoleWidget.history_lock = True

# ------------------------------------------------------------------------------
# FrontendWidget(HistoryConsoleWidget,BaseFrontendMixin) configuration
# ------------------------------------------------------------------------------

# A Qt frontend for a generic Python kernel.
c.FrontendWidget.banner = ""

# Whether to clear the console when the kernel is restarted
# c.FrontendWidget.clear_on_kernel_restart = True

# Whether to ask for user confirmation when restarting kernel
# c.FrontendWidget.confirm_restart = True

# Whether to draw information calltips on open-parentheses.
# c.FrontendWidget.enable_calltips = True

# ------------------------------------------------------------------------------
# IPythonWidget(FrontendWidget) configuration
# ------------------------------------------------------------------------------

# Dummy class for config inheritance. Destroyed below.

# ------------------------------------------------------------------------------
# JupyterWidget(IPythonWidget) configuration
# ------------------------------------------------------------------------------

# A FrontendWidget for a Jupyter kernel.

# A command for invoking a GUI text editor. If the string contains a {filename}
# format specifier, it will be used. Otherwise, the filename will be appended to
# the end the command. To use a terminal text editor, the command should launch
# a new terminal, e.g. ``"gnome-terminal -- vim"``.

# Shit we have to specify the terminal too? This just got 40000 more complicated.
# Gotta determine OS, version, what terminal I'm using ugh
if os.name != "Windows-NT":
    if shutil.which("nvim-qt"):
        c.JupyterWidget.editor = "nvim-qt"
    else:
        c.JupyterWidget.editor = "nvim"
else:
    if shutil.which("nvim-qt"):
        c.JupyterWidget.editor = "nvim-qt.exe"
    else:
        c.JupyterWidget.editor = "nvim.exe"

# The editor command to use when a specific line number is requested. The string
# should contain two format specifiers: {line} and {filename}. If this parameter
# is not specified, the line number option to the %edit magic will be ignored.

# Uh gotta check the man page h/o. So you can do it with -c for command, or +
# Let's do -c because + with no argument sends you to the end of file
c.JupyterWidget.editor_line = "-c {line} -- {filename}"

# c.JupyterWidget.in_prompt = 'In [<span class="in-prompt-number">%i</span>]: '

# c.JupyterWidget.input_sep = '\n'

# c.JupyterWidget.out_prompt = 'Out[<span class="out-prompt-number">%i</span>]: '

# c.JupyterWidget.output_sep = ''

# c.JupyterWidget.output_sep2 = ''

# A CSS stylesheet. The stylesheet can contain classes for:
#      1. Qt: QPlainTextEdit, QFrame, QWidget, etc
#      2. Pygments: .c, .k, .o, etc. (see PygmentsHighlighter)
#      3. QtConsole: .error, .in-prompt, .out-prompt, etc
# c.JupyterWidget.style_sheet = ''

# If not empty, use this Pygments style for syntax highlighting. Otherwise, the
#  style sheet is queried for Pygments style information.

if GruvboxStyle is None:
    c.JupyterWidget.syntax_style = "Solarized Dark"
else:
    c.JupyterWidget.syntax_style = "GruvboxStyle"

# ------------------------------------------------------------------------------
# KernelManager(ConnectionFileMixin) configuration
# ------------------------------------------------------------------------------

# Manages a single kernel in a subprocess on this host.
#
# This version starts kernels with Popen.

# Should we autorestart the kernel if it dies.
# c.KernelManager.autorestart = True

# DEPRECATED: Use kernel_name instead.
#
# The Popen Command to launch the kernel. Override this if you have a custom
# kernel. If kernel_cmd is specified in a configuration file, Jupyter does not
# pass any arguments to the kernel, because it cannot make any assumptions about
# the arguments that the kernel understands. In particular, this means that the
# kernel does not receive the option --debug if it given on the Jupyter command
# line.
# c.KernelManager.kernel_cmd = []

# Time to wait for a kernel to terminate before killing it, in seconds.
# c.KernelManager.shutdown_wait_time = 5.0

# ------------------------------------------------------------------------------
# KernelRestarter(LoggingConfigurable) configuration
# ------------------------------------------------------------------------------

# Monitor and autorestart a kernel.

# Whether to include every poll event in debugging output.
#
# Has to be set explicitly, because there will be *a lot* of output.
# c.KernelRestarter.debug = False

# Whether to choose new random ports when restarting before
# the kernel is alive.
# c.KernelRestarter.random_ports_until_alive = True

# The number of consecutive autorestarts before the kernel is presumed dead.
# c.KernelRestarter.restart_limit = 5

# Kernel heartbeat interval in seconds.
# c.KernelRestarter.time_to_dead = 3.0

# ------------------------------------------------------------------------------
# Session(Configurable) configuration
# ------------------------------------------------------------------------------

# Object for handling serialization and sending of messages.
#
# The Session object handles building messages and sending them with ZMQ sockets
# or ZMQStream objects.  Objects can communicate with each other over the
# network via Session objects, and only need to work with the dict-based IPython
# message spec. The Session will handle serialization/deserialization, security,

# and metadata.
#
# Sessions support configurable serialization via packer/unpacker traits, and
# signing with HMAC digests via the key/keyfile traits.
#
# Parameters ----------
#
# debug : bool
#     whether to trigger extra debugging statements
# packer/unpacker : str : 'json', 'pickle' or import_string
#     importstrings for methods to serialize message parts.  If just
#     'json' or 'pickle', predefined JSON and pickle packers will be used.
#     Otherwise, the entire importstring must be used.
#
#     The functions must accept at least valid JSON input, and output *bytes*.
#
#     For example, to use msgpack:
#     packer = 'msgpack.packb', unpacker='msgpack.unpackb'
# pack/unpack : callables
#     You can also set the pack/unpack callables for serialization directly.
# session : bytes
#     the ID of this Session object.  The default is to generate a new UUID.
# username : unicode
#     username added to message headers.  The default is to ask the OS.
# key : bytes
#     The key used to initialize an HMAC signature.  If unset, messages
#     will not be signed or checked.
# keyfile : filepath
#     The file containing a key.  If this is set, `key` will be initialized
#     to the contents of the file.

# Threshold (in bytes) beyond which an object's buffer should be extracted to
# avoid pickling.
# c.Session.buffer_threshold = 1024

# Whether to check PID to protect against calls after fork.

# This check can be disabled if fork-safety is handled elsewhere.
# c.Session.check_pid = True

# Threshold (in bytes) beyond which a buffer should be sent without copying.
# c.Session.copy_threshold = 65536

# Debug output in the Session
c.Session.debug = True

# The maximum number of digests to remember.
# The digest history will be culled when it exceeds this value.
# c.Session.digest_history_size = 65536

# The maximum number of items for a container to be introspected for custom
# serialization. Containers larger than this are pickled outright.
# c.Session.item_threshold = 64

# execution key, for signing messages.
# c.Session.key = b''

# path to file containing execution key.
# c.Session.keyfile = ''

# Metadata dictionary, which serves as the default top-level metadata dict for
# each message.
# c.Session.metadata = {}

# The name of the packer for serializing messages. Should be one of 'json',
# 'pickle', or an import name for a custom callable serializer.
# c.Session.packer = 'json'

# The UUID identifying this session.
# c.Session.session = ''

# The digest scheme used to construct the message signatures. Must have the form
# 'hmac-HASH'.
# c.Session.signature_scheme = 'hmac-sha256'

# The name of the unpacker for unserializing messages. Only used with custom
# functions for `packer`.
# c.Session.unpacker = 'json'

# Username for the Session. Default is your system username.
c.Session.username = "faris"
