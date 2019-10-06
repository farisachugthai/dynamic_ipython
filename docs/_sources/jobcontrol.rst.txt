.. _job-control:

=================================================================
Job Control --- Preliminary "job control" extensions for IPython.
=================================================================

.. module:: job_control
    :synopsis: Provide job control for IPython.

Synopsis
--------
**job-control** [*options*]

Requires python 2.4 (or separate 'subprocess' module).
This provides 2 features, launching background jobs and killing
foreground jobs from another IPython instance.

Usage:

[ipython]|2> import jobctrl
[ipython]|3> &ls
            <3> <jobctrl.IpyPopen object at 0x00D87FD0>
[ipython]|4> _3.go
-----------> _3.go()
ChangeLog
IPython
MANIFEST.in
README
README_Windows.txt

...

Killing foreground tasks:

Launch IPython instance, run a blocking command:

[Q:/ipython]|1> import jobctrl
[Q:/ipython]|2> cat

Now launch a new IPython prompt and kill the process:

IPython 0.8.3.svn.r2919   [on Py 2.5]
[Q:/ipython]|1> import jobctrl
[Q:/ipython]|2> %tasks
6020: 'cat ' (Q:\ipython)
[Q:/ipython]|3> %kill
SUCCESS: The process with PID 6020 has been terminated.
[Q:/ipython]|4>

.. note::
    You don't need to specify PID for ``%kill`` if only one task is running.


Quickstart
----------

Import module 'jobctrl' to launch and interact with background processes by
prepending system commands with :kbd:`&`, or to kill foreground tasks
that are preventing you from continuing with your work and are just
too stubborn to die with the usual :kbd:`Ctrl-C`.

Alternatively, load it as an extension with::

   %load_ext jobctrl

Killing foreground tasks
------------------------

Launch IPython instance, run a blocking command::

    [Q:/ipython]|1> import jobctrl
    [Q:/ipython]|2> cat

Observe that it starts blocking.

Now launch a new IPython prompt and kill the :command:`cat` process::

    IPython 0.8.3.svn.r2919   [on Py 2.5]
    [Q:/ipython]|1> import jobctrl
    [Q:/ipython]|2> %tasks
    6020: 'cat ' (Q:\ipython)
    [Q:/ipython]|3> %kill
    SUCCESS: The process with PID 6020 has been terminated.
    [Q:/ipython]|4>

(You don't need to specify PID for `%kill` if only one task is running)

Note that only the processes that are launched when 'jobctrl' is enabled are affected.

Background jobs
---------------

See the example below. "IPython job" object is just a very thin wrapper over
:class:`subprocess.Popen` object, with an added ``__repr__``
and "go" method.::

    [ipython]|1> import jobctrl
    [ipython]|2> &ls C*
             <2> <IPython job "ls C*">
    [ipython]|3> &ls e*
             <3> <IPython job "ls e*">
    [ipython]|4> &ls e*
             <4> <IPython job "ls e*">
    [ipython]|5> &ls RE*
             <5> <IPython job "ls RE*">

    [ipython]|7> _2.go
    -----------> _2.go()
    ChangeLog
    [ipython]|8> _3.go
    -----------> _3.go()
    eggsetup.py
    [ipython]|9> _5.go
    -----------> _5.go()
    README
    README_Windows.txt
    [ipython]|10> _4.go
    ------------> _4.go()
    eggsetup.py


Note how "jobs" are just objects in the output history. You can use all the
:class:`subprocess.Popen` methods on the object, but this example
just uses "go".

See `<http://docs.python.org/library/subprocess.html#popen-objects>`_.

Net radio example
-----------------

Here's another example:

I want to make a `%macro` called 'radio_trance' that launches :command:`VLC` on
a net radio stream. I have the "vlc" alias that points to the actual binary of
vlc, so I launch it via the alias::

    [ipython]|1> import jobctrl
    [ipython]|2> vlc http://di.fm/mp3/trance.pls

But this blocks the ipython window, while I want to listen to
it in the background!

I check out the command history to get the expanded version of the command::

    [ipython]|3> hist
    1: import jobctrl
    2: _ip.system("q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls")
    3: _ip.magic("hist ")

I copy-paste the command string from line #2 (and add :kbd:`&` to make it
a background process::

    [ipython]|4> &q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls
             <4> <IPython job "q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls">

(Note that this is unnecessarily hard. In fact, with the new recursive
`%alias` expansion, you can do this simply with aliases without having
to resort to manual copy-paste)

So far so good, I can hear the music playing in the background!

Now I'll make a `%macro` that both imports jobctrl and launches vlc
(lines 1 and 4), and `%store` it::

    [ipython]|5> hist
    1: import jobctrl
    2: _ip.system("q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls")
    3: _ip.magic("hist ")
    4: _ip.startjob("q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls")
    5: _ip.magic("hist ")

    [ipython]|6> macro radio_trance 1 4
    Macro `radio_trance` created. To execute, type its name (without quotes).
    Macro contents:
    import jobctrl
    _ip.startjob("q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls")

    [ipython]|7> store radio_trance
    Stored 'radio_trance' (Macro)

Now I restart ipython and try the `%macro`::

    Q:\ipython>python IPython.py -p sh
    Py 2.5 (r25:51908, Sep 19 2006, 09:52:17) [MSC v.1310 32 bit (Intel)] IPy 0.7.3.svn
    [ipython]|1> radio_trance
             <1> Executing Macro...
             <3> <IPython job "q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls">
    [ipython]|4> hist
    1: radio_trance
    2: import jobctrl
    3: _ip.startjob("q:/opt/VLC/vlc.exe http://di.fm/mp3/trance.pls")
    4: _ip.magic("hist ")

And verify that it works.


Killing jobs
------------

So now we know how to background jobs, but how do we end them?::

    [ipython]|1> &rad_trance
             <1> <IPython job "q:/opt/VLC/vlc.exe http://di.fm/mp3/harddance.pls " PID=196>
    [ipython]|2> # this music is boring me.... I want it to stop right now!
    [ipython]|3> _1.kill
    -----------> _1.kill()
    SUCCESS: The process with PID 196 has been terminated.


See Also
--------

See the source of `jobctrl.py
<https://github.com/ipython/ipython/blob/0.10.2/IPython/Extensions/jobctrl.py>`_

.. todo:: Document IPython.lib.backgroundjobs

   That module will probably be as, if not more, fruitful than this one.

Autogenerated
--------------

.. automodule:: default_profile.extensions.job_control
    :members:
    :undoc-members:
    :show-inheritance:
