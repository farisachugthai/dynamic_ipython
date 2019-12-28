#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Todo:

(dynamic_ipython) 02:32:23 u0_a144@localhost Mon Oct 07 ~/projects/dynamic_ipython/default_profile/profile_debugger

$: ipdb3 ../extensions/job_control.py -c pdbrc
> /data/data/com.termux/files/home/projects/dynamic_ipython/default_profile/extensions/job_control.py(3)<module>() 2
# -*- coding: utf- 8 -*-
----> 3 import os
4 import shlex

ipdb> c

Warning! Hook 'input_prefilter' is not one of ['editor', 'synchronize_with_editor',
'shutdown_hook', 'late_startup_hook', 'show_in_pager', 'pre_prompt_hook',
'pre_run_code_hook', 'clipboard_get']

Warning! Hook 'shell_hook' is not one of ['editor', 'synchronize_with_editor',
'shutdown_hook', 'late_startup_hook', 'show_in_pager', 'pre_prompt_hook',
'pre_run_code_hook', 'clipboard_get']

The program finished and will be restarted


"""
import os
import queue
import shlex
import subprocess
import sys
import threading
import time
from subprocess import PIPE, Popen, STDOUT

import ipython_genutils

# import IPython.ipapi
from IPython import get_ipython


# from IPython.lib.editor


class IpyPopen(subprocess.Popen):
    """Subclass subprocess.Popen and give it a new __repr__."""

    def go(self):
        return self.communicate()[0]

    def __repr__(self):
        return '<IPython job "%s" PID=%d>' % (self.line, self.pid)

    def kill(self):
        kill_process(self.pid)


def startjob(job):
    """Initialize an 'IpyPopen' instance."""
    p = IpyPopen(shlex.split(job), stdout=PIPE, shell=False)
    p.line = job
    return p


class AsyncJobQ(threading.Thread):
    """An asynchronous job queue."""

    def __init__(self, q=None, output=None, *args, **kwargs):
        """Initialize the class.

        Parameters
        ----------
        output : list, optional
            ?
        q : :class:`queue.Queue`, optional

        """
        # threading.Thread.__init__(self)
        self.q = queue.Queue()
        self.output = output or []
        self.stop = False
        super().__init__(self, *args, **kwargs)

    def run(self):
        while 1:
            cmd, cwd = self.q.get()
            if self.stop:
                self.output.append("** Discarding: '%s' - %s" % (cmd, cwd))
                continue
            self.output.append("** Task started: '%s' - %s" % (cmd, cwd))

            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, cwd=cwd)
            out = p.stdout.read()
            self.output.append("** Task complete: '%s'\n" % cmd)
            self.output.append(out)

    def add(self, cmd):
        """Would this be better implemented as the dunder ``__add__``?"""
        self.q.put_nowait((cmd, os.getcwd()))

    def dumpoutput(self):
        """Would this be better implemented as the ``__iter__`` dunder?"""
        while self.output:
            item = self.output.pop(0)
            print(item)


def jobqueue_f(self, line):
    """Create a jobqueue."""
    global _jobq
    if not _jobq:
        print("Starting jobqueue - do '&some_long_lasting_system_command' to enqueue")
        _jobq = AsyncJobQ()
        _jobq.setDaemon(True)
        _jobq.start()
        ip.jobq = _jobq.add
        return
    if line.strip() == "stop":
        print("Stopping and clearing jobqueue, %jobqueue start to start again")
        _jobq.stop = True
        return
    if line.strip() == "start":
        _jobq.stop = False
        return


def jobctrl_prefilter_f(self, line):
    """Yeah we definitely gotta rewrite this one."""
    if line.startswith("&"):
        pre, fn, rest = self.split_user_input(line[1:])

        line = ip.IP.expand_aliases(fn, rest)
        if not _jobq:
            # Idk if that method is in ipython_genutils
            return "_ip.startjob(%s)" % ipython_genutils.make_quoted_expr(line)
        return "_ip.jobq(%s)" % ipython_genutils.make_quoted_expr(line)

    # raise IPython.ipapi.TryNext
    # possibly is


def jobq_output_hook(self):
    if not _jobq:
        return
    _jobq.dumpoutput()


def job_list(ip):
    """IPython doesn't have a db attribute anymore."""
    keys = ip.db.keys("tasks/*")
    ents = [ip.db[k] for k in keys]
    return ents


def magic_tasks(self, line):
    """ Show a list of tasks.

    A 'task' is a process that has been started in IPython when 'jobctrl'
    extension is enabled.

    Tasks can be killed with `%kill`.

    '%tasks clear' clears the task list (from stale tasks)

    Notes
    -----
    IPython doesn't have a getapi() method nor does it have a db attribute.

    """
    ip = self.getapi()
    if line.strip() == "clear":
        for k in ip.db.keys("tasks/*"):
            print("Clearing", ip.db[k])
            del ip.db[k]
        return

    ents = job_list(ip)
    if not ents:
        print("No tasks running")
    for pid, cmd, cwd, t in ents:
        dur = int(time.time() - t)
        print("%d: '%s' (%s) %d:%02d" % (pid, cmd, cwd, dur / 60, dur % 60))


def magic_kill(self, line):
    """Kill a task

    Without args, either kill one task (if only one running) or show list (if many)
    With arg, assume it's the process id.

    %kill is typically (much) more powerful than trying to terminate
    a process with ctrl+C.
    """
    ip = self.getapi()
    jobs = job_list(ip)

    if not line.strip():
        if len(jobs) == 1:
            kill_process(jobs[0][0])
        else:
            magic_tasks(self, line)
        return

    try:
        pid = int(line)
        kill_process(pid)
    except ValueError:
        magic_tasks(self, line)


if sys.platform == "win32":
    shell_internal_commands = [
        "break chcp cls copy ctty date del erase"
        "dir md mkdir path prompt rd rmdir start time type ver vol "
    ]
    PopenExc = WindowsError
else:
    # todo linux commands
    shell_internal_commands = []
    PopenExc = OSError


def determine_use_shell(command, all_shell_commands):
    """Refactor jobctrl_shellcmd."""
    cmdname = command.split(None, 1)[0]
    if (
        cmdname in all_shell_commands
        or "|" in command
        or ">" in command
        or "<" in command
    ):
        return True


def jobctrl_shellcmd(ip, cmd):
    """:func:`os.system` replacement.

    Stores process info to db['tasks/t1234'].
    """
    cmd = cmd.strip()
    use_shell = determine_use_shell(cmd, shell_internal_commands)

    jobentry = None
    # There HAS to be a better way of doing this
    try:
        p = Popen(cmd, shell=use_shell)
    except PopenExc:
        if use_shell:
            # try with os.system
            os.system(cmd)
            return
        else:
            # have to go via shell, sucks
            p = Popen(cmd, shell=True)

    jobentry = "tasks/t" + str(p.pid)
    # ipython doesn't have a db attribute anymore
    # ip.db[jobentry] = (p.pid, cmd, os.getcwd(), time.time())
    p.communicate()


def install():
    """Set up job control for the IPython instance."""
    # needed to make startjob visible as _ip.startjob('blah')
    ip.startjob = startjob
    ip.set_hook("input_prefilter", jobctrl_prefilter_f)
    ip.set_hook("shell_hook", jobctrl_shellcmd)
    # ip.expose_magic('kill', magic_kill)
    # ip.expose_magic('tasks', magic_tasks)
    # ip.expose_magic('jobqueue', jobqueue_f)
    ip.set_hook("pre_prompt_hook", jobq_output_hook)


if __name__ == "__main__":
    if os.name == "nt":

        def kill_process(pid):
            os.system("taskkill /F /PID %d" % pid)

    else:

        def kill_process(pid):
            os.system("kill -9 %d" % pid)

    _jobq = None
    ip = get_ipython()

    install()
