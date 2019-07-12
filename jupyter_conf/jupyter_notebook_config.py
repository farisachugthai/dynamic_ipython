#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configuration file for jupyter-notebook."""
from traitlets.config import get_config

c = get_config()

# -----------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# -----------------------------------------------------------------------------

# This is an application.

# The date format used by logging formatters for %(asctime)s
c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

# The Logging format template
c.Application.log_format = '[%(name)s]%(highlevel)s %(message)s'

# Set the log level by value or name.
c.Application.log_level = 30

# Reraise exceptions encountered loading server extensions?
c.NotebookApp.reraise_server_extension_failures = True

# Don't run the del because then Sphinx doesn't get the docstring.
# del jupyter_specific_configs

# Specify Where to open the notebook on startup. This is the `new` argument
# passed to the standard library method `webbrowser.open`. The behaviour is not
# guaranteed, but depends on browser support. Valid values are:

# - 2 opens a new tab,
# - 1 opens a new window,
# - 0 opens in an existing window.

# See the `webbrowser.open` documentation for details.
c.NotebookApp.webbrowser_open_new = 1

# -----------------------------------------------------------------------------
# ConnectionFileMixin(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------

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
# This version starts kernels with Popen.

# Should we autorestart the kernel if it dies.
#c.KernelManager.autorestart = True

# DEPRECATED: Use kernel_name instead.
#
#  The Popen Command to launch the kernel. Override this if you have a custom
#  kernel. If kernel_cmd is specified in a configuration file, Jupyter does not
#  pass any arguments to the kernel, because it cannot make any assumptions about
#  the arguments that the kernel understands. In particular, this means that the
#  kernel does not receive the option --debug if it given on the Jupyter command
#  line.
#c.KernelManager.kernel_cmd = []

# Time to wait for a kernel to terminate before killing it, in seconds.
#c.KernelManager.shutdown_wait_time = 5.0

# -----------------------------------------------------------------------------
# Session(Configurable) configuration
# -----------------------------------------------------------------------------

# Object for handling serialization and sending of messages.

# The Session object handles building messages and sending them with ZMQ sockets
# or ZMQStream objects.  Objects can communicate with each other over the
# network via Session objects, and only need to work with the dict-based IPython
# message spec. The Session will handle serialization/deserialization, security,
# and metadata.
#
# Sessions support configurable serialization via packer/unpacker traits, and
# signing with HMAC digests via the key/keyfile traits.

# Parameters ----------

# debug : bool
#     whether to trigger extra debugging statements
# packer/unpacker : str : 'json', 'pickle' or import_string
#     importstrings for methods to serialize message parts.  If just
#     'json' or 'pickle', predefined JSON and pickle packers will be used.
#     Otherwise, the entire importstring must be used.

#      The functions must accept at least valid JSON input, and output *bytes*.

#      For example, to use msgpack:
#      packer = 'msgpack.packb', unpacker='msgpack.unpackb'
# pack/unpack : callables
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
# avoid pickling.
# c.Session.buffer_threshold = 1024

# Whether to check PID to protect against calls after fork.

# This check can be disabled if fork-safety is handled elsewhere.
# c.Session.check_pid = True

# Threshold (in bytes) beyond which a buffer should be sent without copying.
# c.Session.copy_threshold = 65536

# Debug output in the Session
# c.Session.debug = False

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
#c.Session.session = ''

# The digest scheme used to construct the message signatures. Must have the form
#  'hmac-HASH'.
#c.Session.signature_scheme = 'hmac-sha256'

# The name of the unpacker for unserializing messages. Only used with custom
#  functions for `packer`.
#c.Session.unpacker = 'json'

# Username for the Session. Default is your system username.
# c.Session.username = 'username'

# -----------------------------------------------------------------------------
# MultiKernelManager(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------

# A class for managing multiple kernels.

# The name of the default kernel to start
# c.MultiKernelManager.default_kernel_name = 'python3'

# The kernel manager class.  This is configurable to allow subclassing of the
# KernelManager for customized behavior.
# c.MultiKernelManager.kernel_manager_class = 'jupyter_client.ioloop.IOLoopKernelManager'

# -----------------------------------------------------------------------------
# MappingKernelManager(MultiKernelManager) configuration
# -----------------------------------------------------------------------------

# A KernelManager that handles notebook mapping and HTTP error handling

# Whether messages from kernels whose frontends have disconnected should be
# buffered in-memory.

#  When True (default), messages are buffered and replayed on reconnect, avoiding
#  lost messages due to interrupted connectivity.

#  Disable if long-running kernels will produce too much output while no
#  frontends are connected.
#c.MappingKernelManager.buffer_offline_messages = True

# Whether to consider culling kernels which are busy. Only effective if
# cull_idle_timeout > 0.
#c.MappingKernelManager.cull_busy = False

# Whether to consider culling kernels which have one or more connections. Only
# effective if cull_idle_timeout > 0.
#c.MappingKernelManager.cull_connected = False

# Timeout (in seconds) after which a kernel is considered idle and ready to be
# culled. Values of 0 or lower disable culling. Very short timeouts may result
# in kernels being culled for users with poor network connections.
# c.MappingKernelManager.cull_idle_timeout = 0

# The interval (in seconds) on which to check for idle kernels exceeding the
# cull timeout value.
c.MappingKernelManager.cull_interval = 3000

# Timeout for giving up on a kernel (in seconds).

# On starting and restarting kernels, we check whether the kernel is running and
# responsive by sending kernel_info_requests. This sets the timeout in seconds
# for how long the kernel can take before being presumed dead.  This affects the
# MappingKernelManager (which handles kernel restarts)  and the
#  ZMQChannelsHandler (which handles the startup).
#c.MappingKernelManager.kernel_info_timeout = 60

# c.MappingKernelManager.root_dir = ''

# -----------------------------------------------------------------------------
# ContentsManager(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------
# Base class for serving files and directories.
# -----------------------------------------------------------------------------
#  This serves any text or binary file, as well as directories, with special
#  handling for JSON notebook documents.
#
#  Most APIs take a path argument, which is always an API-style unicode path, and
#  always refers to a directory.
#
#  - unicode, not url-escaped
#  - '/'-separated
#  - leading and trailing '/' will be stripped
#  - if unspecified, path defaults to '',
#    indicating the root path.

# This serves any text or binary file, as well as directories, with special
# handling for JSON notebook documents.

# Most APIs take a path argument, which is always an API-style unicode path, and
# always refers to a directory.

# Allow access to hidden files
c.ContentsManager.allow_hidden = True

# c.ContentsManager.checkpoints = None

# c.ContentsManager.checkpoints_class = 'notebook.services.contents.checkpoints.Checkpoints'

# c.ContentsManager.checkpoints_kwargs = {}

# handler class to use when serving raw file requests.

# Default is a fallback that talks to the ContentsManager API, which may be
# inefficient, especially for large files.

# Local files-based ContentsManagers can use a StaticFileHandler subclass, which
# will be much more efficient.

# Access to these files should be Authenticated.
# c.ContentsManager.files_handler_class = 'notebook.files.handlers.FilesHandler'

# Extra parameters to pass to files_handler_class.

# For example, StaticFileHandlers generally expect a `path` argument specifying
# the root directory from which to serve files.
# c.ContentsManager.files_handler_params = {}

# Glob patterns to hide in file and directory listings.
c.ContentsManager.hide_globs = [
    '__pycache__', '*.pyc', '*.pyo', '.DS_Store', '*.so', '*.dylib', '*~',
    '.git'
]

# Python callable or importstring thereof To be called on a contents model prior to save.

# This can be used to process the structure, such as removing notebook outputs
# or other side effects that should not be saved.

# It will be called as (all arguments passed by keyword)::

#     hook(path=path, model=model, contents_manager=self)

# - model: the model to be saved. Includes file contents.
#   Modifying this dict will affect the file that is stored.
# - path: the API path of the save destination
# - contents_manager: this ContentsManager instance
# c.ContentsManager.pre_save_hook = None

# c.ContentsManager.root_dir = '/'

# The base name used when creating untitled directories.
# oooo we should totally set this to a tempdir so that we don't have to bother with this anymore
# c.ContentsManager.untitled_directory = 'Untitled Folder'

# The base name used when creating untitled files.
# c.ContentsManager.untitled_file = 'untitled'

# The base name used when creating untitled notebooks.
# c.ContentsManager.untitled_notebook = 'Untitled'

# -----------------------------------------------------------------------------
# FileManagerMixin(Configurable) configuration
# -----------------------------------------------------------------------------

# Mixin for ContentsAPI classes that interact with the filesystem.

# Provides facilities for reading, writing, and copying both notebooks and
# generic files.

# Shared by FileContentsManager and FileCheckpoints.

# Note ---- Classes using this mixin must provide the following attributes:

# root_dir : unicode
#     A directory against against which API-style paths are to be resolved.

# log : logging.Logger

# By default notebooks are saved on disk on a temporary file and then if
# succefully written, it replaces the old ones. This procedure, namely
# 'atomic_writing', causes some bugs on file system whitout operation order
# enforcement (like some networked fs). If set to False, the new notebook is
# written directly on the old one which could fail (eg: full filesystem or quota
# )
# c.FileManagerMixin.use_atomic_writing = True

# -----------------------------------------------------------------------------
# FileContentsManager(FileManagerMixin,ContentsManager) configuration
# -----------------------------------------------------------------------------

# If True (default), deleting files will send them to the platform's
# trash/recycle bin, where they can be recovered. If False, deleting files
# really deletes them.
# c.FileContentsManager.delete_to_trash = True

# Python callable or importstring thereof to be called on the path of a file just saved.
# This can be used to process the file on disk, such as converting the notebook
# to a script or HTML via nbconvert.

#  It will be called as (all arguments passed by keyword)::
#
#      hook(os_path=os_path, model=model, contents_manager=instance)
#
#  - path: the filesystem path to the file just written - model: the model
#  representing the file - contents_manager: this ContentsManager instance
#c.FileContentsManager.post_save_hook = None

# to be called on the path of a file just saved.

# c.FileContentsManager.root_dir = ''

# DEPRECATED, use post_save_hook. Will be removed in Notebook 5.0
#c.FileContentsManager.save_script = False

# -----------------------------------------------------------------------------
# NotebookNotary(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------

# A class for computing and verifying notebook signatures.

# The hashing algorithm used to sign notebooks.
# c.NotebookNotary.algorithm = 'sha256'

# The sqlite file in which to store notebook signatures. By default, this will
# be in your Jupyter data directory. You can set it to ':memory:' to disable
# sqlite writing to the filesystem.
# c.NotebookNotary.db_file = ''

# The secret key with which notebooks are signed.
# c.NotebookNotary.secret = b''

# The file where the secret key is stored.
# c.NotebookNotary.secret_file = ''

# A callable returning the storage backend for notebook signatures. The default
# uses an SQLite database.
# c.NotebookNotary.store_factory = traitlets.Undefined

# -----------------------------------------------------------------------------
# KernelSpecManager(LoggingConfigurable) configuration
# -----------------------------------------------------------------------------

# If there is no Python kernelspec registered and the IPython kernel is
# available, ensure it is added to the spec list.
# c.KernelSpecManager.ensure_native_kernel = True

# The kernel spec class.  This is configurable to allow subclassing of the
# KernelSpecManager for customized behavior.
# c.KernelSpecManager.kernel_spec_class = 'jupyter_client.kernelspec.KernelSpec'

# Whitelist of allowed kernel names.

# By default, all installed kernels are allowed.
# c.KernelSpecManager.whitelist = set()

# -----------------------------------------------------------------------------
# NteractConfig(Configurable) configuration
# -----------------------------------------------------------------------------

# The nteract application configuration object

# Remote URL for loading assets
# c.NteractConfig.asset_url = ''

# Google Analytics tracking code
# c.NteractConfig.ga_code = ''
