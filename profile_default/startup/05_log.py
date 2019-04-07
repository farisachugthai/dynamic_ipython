#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a logfile for the day and append to it if one already exists.

Collects both the input and output of every command run through the IPython
interpreter and prepends a timestamp to commands.

The timestamp is particularly convenient for concurrent instances of IPy.

.. versionchanged:: Changed :func:`_ip.magic()` to :func:`_ip.run_line_magic()`

.. todo::

    - Consider using datetime instead of time. Not pertinent though.
    - Explore both the built-in logging module and IPython logging subclass.
    - Truncate output if it exceeds a certain threshold.
        - Run dir(np) or dir(pd) a couple of times and the logs become
        swamped.
    - Possibly change that section under the shebang to also include 3
    double quotes and in the comment add system info like py version, venv,
    conda, any of the 1000000 things you could add.

See Also
----------
For further reading, feel free to see the output of any of the following

.. code-block:: python3

    >>> from IPython.core.interactiveshell import InteractiveShell
    >>> help(InteractiveShell)

Which features descriptions of functions relevant to startup such as
``register_magic_function()`` and literally every option available
through
the ``%config`` magic.

For commands that are more related to the interactive aspect of the
shell,
see the following

.. code-block:: python3

    >>> from IPython import get_ipython()
    >>> _ip = get_ipython()
    >>> help(_ip)
    >>> dir(_ip)

In addition, there's an abundance of documentation online in the
form of rst docs and ipynb notebooks.


Also I nabbed the source code for that logger class we use.

In [2]: _ip.logger??
Type:        Logger
String form: <IPython.core.logger.Logger object at 0x7a689ae160>
File:        /data/data/com.termux/files/usr/lib/python3.7/site-packages/IPython/core/logger.py
Source:
class Logger(object):
    #A Logfile class with different policies for file creation

    def __init__(self, home_dir, logfname='Logger.log', loghead=u'',
                 logmode='over'):

        # this is the full ipython instance, we need some attributes from it
        # which won't exist until later. What a mess, clean up later...
        self.home_dir = home_dir

        self.logfname = logfname
        self.loghead = loghead
        self.logmode = logmode
        self.logfile = None

        # Whether to log raw or processed input
        self.log_raw_input = False

        # whether to also log output
        self.log_output = False

        # whether to put timestamps before each log entry
        self.timestamp = False

        # activity control flags
        self.log_active = False

    # logmode is a validated property
    def _set_mode(self,mode):
        if mode not in ['append','backup','global','over','rotate']:
            raise ValueError('invalid log mode %s given' % mode)
        self._logmode = mode

    def _get_mode(self):
        return self._logmode

    logmode = property(_get_mode,_set_mode)

    def logstart(self, logfname=None, loghead=None, logmode=None,
                 log_output=False, timestamp=False, log_raw_input=False):
        # Generate a new log-file with a default header.

        # Raises RuntimeError if the log has already been started

        if self.logfile is not None:
            raise RuntimeError('Log file is already active: %s' %
                               self.logfname)

        # The parameters can override constructor defaults
        if logfname is not None: self.logfname = logfname
        if loghead is not None: self.loghead = loghead
        if logmode is not None: self.logmode = logmode

        # Parameters not part of the constructor
        self.timestamp = timestamp
        self.log_output = log_output
        self.log_raw_input = log_raw_input

        # init depending on the log mode requested
        isfile = os.path.isfile
        logmode = self.logmode

        if logmode == 'append':
            self.logfile = io.open(self.logfname, 'a', encoding='utf-8')

        elif logmode == 'backup':
            if isfile(self.logfname):
                backup_logname = self.logfname+'~'
                # Manually remove any old backup, since os.rename may fail
                # under Windows.
                if isfile(backup_logname):
                    os.remove(backup_logname)
                os.rename(self.logfname,backup_logname)
            self.logfile = io.open(self.logfname, 'w', encoding='utf-8')

        elif logmode == 'global':
            self.logfname = os.path.join(self.home_dir,self.logfname)
            self.logfile = io.open(self.logfname, 'a', encoding='utf-8')

        elif logmode == 'over':
            if isfile(self.logfname):
                os.remove(self.logfname)
            self.logfile = io.open(self.logfname,'w', encoding='utf-8')

        elif logmode == 'rotate':
            if isfile(self.logfname):
                if isfile(self.logfname+'.001~'):
                    old = glob.glob(self.logfname+'.*~')
                    old.sort()
                    old.reverse()
                    for f in old:
                        root, ext = os.path.splitext(f)
                        num = int(ext[1:-1])+1
                        os.rename(f, root+'.'+repr(num).zfill(3)+'~')
                os.rename(self.logfname, self.logfname+'.001~')
            self.logfile = io.open(self.logfname, 'w', encoding='utf-8')

        if logmode != 'append':
            self.logfile.write(self.loghead)

        self.logfile.flush()
        self.log_active = True

    def switch_log(self,val):
        # Switch logging on/off. val should be ONLY a boolean.

        if val not in [False,True,0,1]:
            raise ValueError('Call switch_log ONLY with a boolean argument, '
                             'not with: %s' % val)

        label = {0:'OFF',1:'ON',False:'OFF',True:'ON'}

        if self.logfile is None:
            print('
Logging hasn't been started yet (use logstart for that).

%logon/%logoff are for temporarily starting and stopping logging for a logfile
which already exists. But you must first start the logging process with
%logstart (optionally giving a logfile name).')

        else:
            if self.log_active == val:
                print('Logging is already',label[val])
            else:
                print('Switching logging',label[val])
                self.log_active = not self.log_active
                self.log_active_out = self.log_active

    def logstate(self):
        # Print a status message about the logger.
        if self.logfile is None:
            print('Logging has not been activated.')
        else:
            state = self.log_active and 'active' or 'temporarily suspended'
            print('Filename       :', self.logfname)
            print('Mode           :', self.logmode)
            print('Output logging :', self.log_output)
            print('Raw input log  :', self.log_raw_input)
            print('Timestamping   :', self.timestamp)
            print('State          :', state)

    def log(self, line_mod, line_ori):
        # Write the sources to a log.

        # Inputs:

        # - line_mod: possibly modified input, such as the transformations made
        #   by input prefilters or input handlers of various kinds. This should
        #   always be valid Python.

        # - line_ori: unmodified input line from the user. This is not
        #   necessarily valid Python.

        # Write the log line, but decide which one according to the
        # log_raw_input flag, set when the log is started.
        if self.log_raw_input:
            self.log_write(line_ori)
        else:
            self.log_write(line_mod)

    def log_write(self, data, kind='input'):
        # Write data to the log file, if active

        #print 'data: %r' % data # dbg
        if self.log_active and data:
            write = self.logfile.write
            if kind=='input':
                if self.timestamp:
                    write(time.strftime('# %a, %d %b %Y %H:%M:%S\n', time.localtime()))
                write(data)
            elif kind=='output' and self.log_output:
                odata = u'\n'.join([u'#[Out]# %s' % s
                                   for s in data.splitlines()])
                write(u'%s\n' % odata)
            self.logfile.flush()

    def logstop(self):
        # Fully stop logging and close log file.

        # In order to start logging again, a new logstart() call needs to be
        # made, possibly (though not necessarily) with a new filename, mode and
        # other options.

        if self.logfile is not None:
            self.logfile.close()
            self.logfile = None
        else:
            print("Logging hadn't been started.")
        self.log_active = False

    # For backwards compatibility, in case anyone was using this.
    close_log = logstop





"""
from __future__ import print_function

from os import path
import time

from IPython import get_ipython


def session_logger(_ip):
    """Log all input and output for an IPython session.

    Saves the commands as valid IPython code. Note that this is not
    necessarily valid python code.

    The commands are appended to a file in the directory of the
    profile in :envvar:`$IPYTHONDIR` or fallback ~/.ipython. This file is
    named based on the date.

    Parameters
    -----------
    _ip : |ip|
        Global IPython instance.

    """
    log_dir = _ip.profile_dir.log_dir
    fname = 'log-' + _ip.profile + '-' + time.strftime('%Y-%m-%d') + ".py"
    filename = path.join(log_dir, fname)
    notnew = path.exists(filename)

    try:
        _ip.run_line_magic('logstart', '-to %s append' % filename)
        # added -t to get timestamps
        if notnew:
            _ip.logger.log_write(u"# =================================\n")
        else:
            _ip.logger.log_write(u"#!/usr/bin/env python\n")
            _ip.logger.log_write(u"# " + fname + "\n")
            _ip.logger.log_write(u"# IPython automatic logging file\n")
            _ip.logger.log_write(u"# " + time.strftime('%H:%M:%S') + "\n")
            _ip.logger.log_write(u"# =================================\n")
            print(" Logging to " + filename)
    except RuntimeError:
        print(" Already logging to " + _ip.logger.logfname)


if __name__ == "__main__":
    _ip = get_ipython()
    session_logger(_ip)
