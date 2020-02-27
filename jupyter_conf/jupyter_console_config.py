"""
=======================
Jupyter Console config
=======================

Sep 05, 2019:
This is quite the odd program.

>>> from jupyter_console.ptshell import ZMQTerminalIPythonApp, ZMQTerminalInteractiveShell

If you read the help for the ZMQTerminalInteractiveShell it indicates that you
can retrieve the global instance with ZMQTerminalInteractiveShell(self).instance.

As a guess I'd imagine this is true because that class specifically subclasses
the traitlets object, SingletonConfigurable.

Running that raised an error for me however.

And oddly, running:

>>> from traitlets.config import get_config
>>> c = get_config()

Only returned information about IPython...

So I ran some information about the ZMQTerminalIPythonApp to see if that
fared any better and::

    In [47]: jup = ZMQTerminalIPythonApp()
    In [48]: jup.aliases
    Out[48]:
    {'log-level': 'Application.log_level',
    'config': 'JupyterApp.config_file',
    'ip': 'JupyterConsoleApp.ip',
    'transport': 'JupyterConsoleApp.transport',
    'hb': 'JupyterConsoleApp.hb_port',
    'shell': 'JupyterConsoleApp.shell_port',
    'iopub': 'JupyterConsoleApp.iopub_port',
    'stdin': 'JupyterConsoleApp.stdin_port',
    'existing': 'JupyterConsoleApp.existing',
    'f': 'JupyterConsoleApp.connection_file',
    'kernel': 'JupyterConsoleApp.kernel_name',
    'ssh': 'JupyterConsoleApp.sshserver'}

Needless to say none of those aliases worked in the shell for me.
..what the hell is this?

"""
from traitlets.config import get_config

c = get_config()

# Configuration file for jupyter-console.

# -----------------------------------------------------------------------------
# ConnectionFileMixin(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------

# Mixin for configurable classes that work with connection files

# JSON file in which to store connection info [default: kernel-<pid>.json]
#
#  This file will contain the IP, ports, and authentication key needed to connect
#  clients to this kernel. By default, this file will be created in the security
#  dir of the current profile, but can be specified by absolute path.
# c.ConnectionFileMixin.connection_file = ''

# set the control (ROUTER) port [default: random]
# c.ConnectionFileMixin.control_port = 0

# set the heartbeat port [default: random]
# c.ConnectionFileMixin.hb_port = 0

# set the iopub (PUB) port [default: random]
# c.ConnectionFileMixin.iopub_port = 0

# Set the kernel's IP address [default localhost]. If the IP address is
#  something other than localhost, then Consoles on other machines will be able
#  to connect to the Kernel, so be careful!
# c.ConnectionFileMixin.ip = ''

# set the shell (ROUTER) port [default: random]
# c.ConnectionFileMixin.shell_port = 0

# set the stdin (ROUTER) port [default: random]
# c.ConnectionFileMixin.stdin_port = 0

#
# c.ConnectionFileMixin.transport = 'tcp'

# -----------------------------------------------------------------------------
# JupyterConsoleApp(ConnectionFileMixin) configuration
# -----------------------------------------------------------------------------

# Set to display confirmation dialog on exit. You can always use 'exit' or
#  'quit', to force a direct exit without any confirmation.
c.JupyterConsoleApp.confirm_exit = False

# Connect to an already running kernel
# c.JupyterConsoleApp.existing = ''

# The name of the default kernel to start.
# c.JupyterConsoleApp.kernel_name = 'python'

# Path to the ssh key to use for logging in to the ssh server.
# c.JupyterConsoleApp.sshkey = ''

# The SSH server to use to connect to the kernel.
# c.JupyterConsoleApp.sshserver = ''

# -----------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# -----------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
c.Application.log_datefmt = "%Y-%m-%d %H:%M:%S"

# The Logging format template
c.Application.log_format = "[%(name)s] %(highlevel)s %(message)s"

# Set the log level by value or name.
c.Application.log_level = 20

# -----------------------------------------------------------------------------
# JupyterApp(Application) configuration
# -----------------------------------------------------------------------------

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
# JupyterConsoleApp(ConnectionFileMixin) configuration
# ------------------------------------------------------------------------------

# Set to display confirmation dialog on exit. You can always use 'exit' or
#  'quit', to force a direct exit without any confirmation.
c.JupyterConsoleApp.confirm_exit = False

# connect to an already running kernel
# c.JupyterConsoleApp.existing = ''

# The name of the default kernel to start.
c.JupyterConsoleApp.kernel_name = "python3"

# Path to the ssh key to use for logging in to the ssh server.
# c.JupyterConsoleApp.sshkey = ''

# The SSH server to use to connect to the kernel.
# c.JupyterConsoleApp.sshserver = ''

# -----------------------------------------------------------------------------
# KernelRestarter(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------

# Monitor and autorestart a kernel.

# Whether to include every poll event in debugging output.
#
#  Has to be set explicitly, because there will be *a lot* of output.
# c.KernelRestarter.debug = False

# Whether to choose new random ports when restarting before the kernel is alive.
# c.KernelRestarter.random_ports_until_alive = True

# The number of consecutive autorestarts before the kernel is presumed dead.
# c.KernelRestarter.restart_limit = 5

# Kernel heartbeat interval in seconds.
# c.KernelRestarter.time_to_dead = 3.0

# -----------------------------------------------------------------------------
# Session(Configurable) configuration
# -----------------------------------------------------------------------------

# Object for handling serialization and sending of messages.
#
#  The Session object handles building messages and sending them with ZMQ sockets
#  or ZMQStream objects.  Objects can communicate with each other over the
#  network via Session objects, and only need to work with the dict-based IPython
#  message spec. The Session will handle serialization/deserialization, security,
#  and metadata.
#
#  Sessions support configurable serialization via packer/unpacker traits, and
#  signing with HMAC digests via the key/keyfile traits.
#
#  Parameters ----------
#
#  debug : bool
#      whether to trigger extra debugging statements
#  packer/unpacker : str : 'json', 'pickle' or import_string
#      importstrings for methods to serialize message parts.  If just
#      'json' or 'pickle', predefined JSON and pickle packers will be used.
#      Otherwise, the entire importstring must be used.
#
#      The functions must accept at least valid JSON input, and output *bytes*.
#
#      For example, to use msgpack:
#      packer = 'msgpack.packb', unpacker='msgpack.unpackb'
#  pack/unpack : callables
#      You can also set the pack/unpack callables for serialization directly.
#  session : bytes
#      the ID of this Session object.  The default is to generate a new UUID.
#  username : unicode
#      username added to message headers.  The default is to ask the OS.
#  key : bytes
#      The key used to initialize an HMAC signature.  If unset, messages
#      will not be signed or checked.
#  keyfile : filepath
#      The file containing a key.  If this is set, `key` will be initialized
#      to the contents of the file.

# Threshold (in bytes) beyond which an object's buffer should be extracted to
#  avoid pickling.
# c.Session.buffer_threshold = 1024

# Whether to check PID to protect against calls after fork.
#
#  This check can be disabled if fork-safety is handled elsewhere.
# c.Session.check_pid = True

# Threshold (in bytes) beyond which a buffer should be sent without copying.
# c.Session.copy_threshold = 65536

# Debug output in the Session
# c.Session.debug = False

# The maximum number of digests to remember.
#
#  The digest history will be culled when it exceeds this value.
# c.Session.digest_history_size = 65536

# The maximum number of items for a container to be introspected for custom
#  serialization. Containers larger than this are pickled outright.
# c.Session.item_threshold = 64

# execution key, for signing messages.
# c.Session.key = b''

# path to file containing execution key.
# c.Session.keyfile = ''

# Metadata dictionary, which serves as the default top-level metadata dict for
#  each message.
# c.Session.metadata = {}

# The name of the packer for serializing messages. Should be one of 'json',
#  'pickle', or an import name for a custom callable serializer.
# c.Session.packer = 'json'

# The UUID identifying this session.
# c.Session.session = ''

# The digest scheme used to construct the message signatures. Must have the form
#  'hmac-HASH'.
# c.Session.signature_scheme = 'hmac-sha256'

# The name of the unpacker for unserializing messages. Only used with custom
#  functions for `packer`.
# c.Session.unpacker = 'json'

# Username for the Session. Default is your system username.
# c.Session.username = 'username'
