================
Built-In Magics
================

.. highlight:: ipython

.. module:: built-in_magics
   :Synopsis: Summarizes IPython magics.

.. contents:: Table of Contents
    :depth: 2
    :backlinks: entry
    :local:


.. _defined_magics:

A Summary of IPython's Built In Magics
=======================================

Line:
------
- `%hist[ory]`
- `%pycat`
- `%recall`
- `%ed[it]`
- `%bookmark`
- `%run`
- `%store`
- `%save`

Cell:
-----
- `%%[write]file`
- `%%timeit`
- `%%macro`


`%timeit`
---------
.. magic:: timeit

Let's observe the example below.
:kbd:`qqq` means be very quiet.
:kbd:`r` :kbd:`5` means repeat the whole cell block 5 times.

.. ipython::
   :verbatim:

    In [20]: %%timeit -qqq -r 5
    ...:
    ...: env_var = sorted(os.environ.keys())
    ...: for i in env_var:
    ...:     match = re.match('CONDA*', i)
    ...:     if match:
    ...:         i
    Out[20]: <TimeitResult : 185 µs ± 890 ns per loop (mean ± std. dev. of 5 runs, 10000 loops each)>

    In [21]: %%timeit -qqq -r 5 -o
    ...: for i in os.environ.keys():
    ...:     match = re.match('CONDA*', i)
    ...:     if match:
    ...:         i
    Out[21]: <TimeitResult : 207 µs ± 2.31 µs per loop (mean ± std. dev. of 5 runs, 1000 loops each)>


2018-09-07

Speaking of `%%timeit` I just gave this a whirl to try and see.::

>>> %%timeit
>>> %nvim random-python-file.py +qall

Possibly a good way to profile nvim startup time.
You could also add in the option ``--startuptime anything.txt``.

Jan 31, 2019:

Now we can choose between ``%nvim file.filetype`` or `%edit` file.filetype
as well!


`%store`
---------
.. magic:: store

Here's the official help.:

    * `%store` foo > a.txt  - Store value of foo to new file a.txt

    * `%store` foo >> a.txt - Append value of foo to file a.txt

    It should be noted that if you change the value of a variable, you
    need to `%store` it again if you want to persist the new value.

    Note also that the variables will need to be pickleable; however, most basic
    python types can be safely `%store`'d.

    Also aliases can be `%store`'d across sessions.


`%save`
--------
.. magic:: save

Help docs on save.:

    Docstring:
    Save a set of lines or a macro to a given filename.

    Usage:
    %save [options] filename n1-n2 n3-n4 ... n5 .. n6 ...

    Options:

    -r: use 'raw' input.  By default, the 'processed' history is used,
    so that magics are loaded in their transformed version to valid
    Python.  If this option is given, the raw input as typed as the
    command line is used instead.

    -f: force overwrite.  If file exists, %save will prompt for overwrite
    unless -f is given.

    -a: append to the file instead of overwriting it.

    This function uses the same syntax as %history for input ranges,
    then saves the lines to the filename you specify.

    It adds a '.py' extension to the file if you don't do so yourself, and
    it asks for confirmation before overwriting existing files.

    If :kbd:`-r` option is used, the default extension is *.ipy*.


Revisiting Previously Run Commands
==================================

`%history`
----------
Access previously run commands with the `%history` magic. Note that it can
be abbreviated to `%hist` and used like so.::

   %hist ~1/

.. admonition:: Remember that ``%hist ~1`` outputs nothing!

   When using the `%hist` magic, don't forget the :kbd:`/`!


`%history` call signature
~~~~~~~~~~~~~~~~~~~~~~~~~~
By default, all input history from the current session is displayed.
Ranges of history can be indicated using the syntax:

``4``
    Line 4, current session
``4-6``
    Lines 4-6, current session
``243/1-5``
    Lines 1-5, session 243
``~2/7``
    Line 7, session 2 before current
``~8/1-~6/5``
    From the first line of 8 sessions ago, to the fifth line of 6
    sessions ago.

Multiple ranges can be specified by separating with spaces.

`%recall`
---------
.. magic:: recall

This is one of the IPython conveniences that makes you understand why
they're called *magics*.

All too often, one will run into the problem of manipulating some 
data in the REPL, and need a way of interacting with it in a manner 
similar to a pipeline.

Storing the data may be difficult, or if it simply prints out to 
console, may be impossible.

*%recall* takes the **output**, not the input, of the last run command and
auto-inserts it at the next input prompt.

As a result, this magic works as it's own pipeline.

.. tip::

   recall is also aliased to ``rep`` for repeat.

Tldr; Use the following to to reload every command you ran last session into your
current cell.

`%recall ~1/`


Output
~~~~~~~
Oddly harder than just input.
You can easily access relative previous input with `_i`,  `_ii` and `_iii_`

You can also call specific cell numbers with `_i[cell]`

But you can't call cell numbers for output. :kbd:`_` , :kbd:`__` append
:kbd:`___` access previous output.

The only way I can find output by cell is `_oh`

That returns a dict with your entire output history. so you can go `_oh.keys()`

But the cell I wanted wasn't there and wasn't saved. Huh. Print statements
might not get saved in the history. Makes sense.

In IPython run:

.. ipython::
   :verbatim:

   >>> print(Out[1])
   >>> hist_list =[]
   >>> for i in range(2):
      >>> hist_list.append(In[i])
      >>> try:
          >>> hist_list.append(Out[i])
      >>> except KeyError:
          >>> pass


Writing a file
~~~~~~~~~~~~~~
There are a handful of different ways to take IPython history and code
previously ran in the console, and save it to a file on disk.::

   In [52]: written = %history -n 31-33
       ...: %edit written
       ...:
       ...:
     31: type(n)
     32: type(len(slm))
     33: type((len(slm))/n)
     /data/data/com.termux/files/usr/lib/python3.6/site-packages/IPython/core/magics/code.py:491: UserWarning: The file where `None` was defined cannot be read or found.
     'cannot be read or found.' % data)

   The file where None was defined???

   In [64]: type(writen)
   Out[64]: NoneType

But you should be able to write history to a file by using:

.. ipython::
   :verbatim:

    %history -f file_to_write.py -n 1-3


`%%writefile`
-------------
.. magic:: writefile

Usage:

   `%%writefile` -a filename

needs both percentage signs even with ``automagic`` since it's a cell magic
the -a option is to append to a file

But don't use quotes on the file or else it won't work. IDK why not
but I kept getting `FileDoesntExistError` until i got rid of the quotes

`%%file` as a cell magic means write everything I'm about to do to a file.
If you got some crazy history filtering in there I'm sure you could go do
something like

.. ipython::
   :verbatim:

   %%file
   hist -n 5-10
   # where -n means print output too
   %%file idk
   _i31-33
   %pycat idk
   # _i31-33

`%edit`
-------
`%edit` can take cell #'s as input like hist does, and creates a file to
work with like `%%file`.

It always create temporary files unlike `%%file` so its REALLY important
to use: the following in Vim.:

.. code-block:: vim

   saveas /path/youll/remember

Outside of that little gotcha it can take functions you defined in your
:mod:`IPython` interactive namespace and you can fuck with them, modify
what you want then exit and execute until you get a final product that
deserves being saved!!

And if you do this over and over you'd end up saving like 10 files so its better
it defaults to saving in /tmp/

Interesting behavior i just noticed:

   `%edit` [file_that_doesn't_exist]

this command fails so apparently you HAVE to run it on an existing file.

Probably happens because it doesn't take filenames as arguments.

To explain that let's look at the help pages.

IPython Help Pages on `%edit`
-----------------------------
This is an example of creating a simple function inside the editor and
then modifying it. First, start up the editor::

  In [1]: edit
  Editing... done. Executing edited code...
  Out[1]: 'def foo():\n    print "foo() was defined in an editing
  session"\n'

We can then call the function foo()::

  In [2]: foo()
  foo() was defined in an editing session

Now we edit foo.  IPython automatically loads the editor with the
(temporary) file where foo() was previously defined::

  In [3]: edit foo
  Editing... done. Executing edited code...

And if we call foo() again we get the modified version::

  In [4]: foo()
  foo() has now been changed!

**tldr;** input ipython objects as arguments.
It also takes the same input for cells as history does. But wait 
how does that work?


Fun fact about edit
~~~~~~~~~~~~~~~~~~~
If you run `%edit -x` in the jupyter console it doesn't do 
anything! Fun fact.

Because it launched a GUI app you don't have bi-directional 
communication.


Honorary Mention
----------------
:func:`exec` is not a magic but I actually thought it was!

.. code-block:: none

   In [18]: exec(In[6])

:func:`exec` is a Python built-in that just takes strings, but it can
operate on history syntax.

.. ipython::
   :verbatim:

   %hist ~2/4

successfully printed the 4th line from 2 sessions ago that I wanted.


Executing Commands with Magics
==============================

Help Docs for `%run`
--------------------
Here are all the listed options for the `%run` magic.:

-t
   print timing information at the end of the run.  IPython will give
   you an estimated CPU time consumption for your script, which under
   Unix uses the resource module to avoid the wraparound problems of
   time.clock().  Under Unix, an estimate of time spent on system tasks
   is also given (for Windows platforms this is reported as 0.0).

   If -t is given, an additional ``-N<N>`` option can be given, where <N>
   must be an integer indicating how many times you want the script to
   run.  The final timing report will include total and per run results.

   For example (testing the script uniq_stable.py):

   In [1]: %run -t uniq_stable

   IPython CPU timings (estimated):
     User  :    0.19597 s.
     System:        0.0 s.

   In [2]: run -t -N5 uniq_stable

   IPython CPU timings (estimated):
   Total runs performed: 5
   Times :      Total       Per run
   User  :   0.910862 s,  0.1821724 s.
   System:        0.0 s,        0.0 s.

-d
   run your program under the control of :mod:`pdb`, the Python debugger.
   This allows you to execute your program step by step, watch variables,
   etc.  Internally, what IPython does is similar to calling::

         pdb.run('execfile("YOURFILENAME")')

   with a breakpoint set on line 1 of your file.  You can change the line
   number for this automatic breakpoint to be <N> by using the -bN option
   (where N must be an integer). For example::

         %run -d -b40 myscript

   will set the first breakpoint at line 40 in myscript.py.  Note that
   the first breakpoint must be set on a line which actually does
   something (not a comment or docstring) for it to stop execution.

   Or you can specify a breakpoint in a different file::

         %run -d -b myotherfile.py:20 myscript

   When the :mod:`pdb` debugger starts, you will see a (Pdb) prompt.  You must
   first enter :kbd:`c` to start execution up to the first
   breakpoint.

   Entering `help` gives information about the use of the debugger.  You
   can easily see the :mod:`pdb` full documentation with ``import pdb;pdb.help()``
   at a prompt.

Momentary Detour
~~~~~~~~~~~~~~~~
So this magic should create a similar output to ``%debug`` but for some reason
whenever I invoke debug, it doesn't show any relevant code when using :kbd:`l`,
:kbd:`ll`, :kbd:`list` or anything.

Unsure what I'm doing wrong, but running ``%run -d -b [line_number]`` works
perfectly enough that honestly I might not care for the time being.


Back to ``%run``!
~~~~~~~~~~~~~~~~~
-p
   run program under the control of the Python profiler module (which
   prints a detailed report of execution times, function calls, etc).

   You can pass other options after -p which affect the behavior of the
   profiler itself. See the docs for ``%prun`` for details.

   In this mode, the program's variables do NOT propagate back to the
   IPython interactive namespace (because they remain in the namespace
   where the profiler executes them).

   Internally this triggers a call to ``%prun``, see its documentation for
   details on the options available specifically for profiling.

   There is one special usage for which the text above doesn't apply:
   if the filename ends with .ipy[nb], the file is run as IPython script,
   just as if the commands were written on IPython prompt.

-m
   specify module name to load instead of script path. Similar to
   the :kbd:`-m` option for the python interpreter. Use this option
   last if you want to combine with other %run options. Unlike the
   python interpreter only source modules are allowed no .pyc or .pyo files.
   For example:

         `%run` -m example

   will run the example module.

-G
   Disable shell-like glob expansion of arguments.


`%pycat` [filename]
-------------------
.. magic:: pycat

Works like :command:`cat` but assumes a python source-code file.

Runs it through a color syntax highlighting pager.

The source code for the syntax highlighting can be found in the combination
of files in :mod:`IPython.utils.PyColorize`, :mod:`IPython.utils.coloransi`,
:mod:`IPython.core.colorable` and others.


`%bookmark`
-----------

In [13]: bookmark?

.. ipython::
   :verbatim:

    Docstring:
    Manage IPython's bookmark system.

    %bookmark <name>       - set bookmark to current dir
    %bookmark <name> <dir> - set bookmark to <dir>
    %bookmark -l           - list all bookmarks
    %bookmark -d <name>    - remove bookmark
    %bookmark -r           - remove all bookmarks

    You can later on access a bookmarked folder with::

        %cd -b <name>

    Or simply '%cd <name>' if there is no directory called <name> AND
    there is such a bookmark defined.

    Your bookmarks persist through IPython sessions, but they are
    associated with each profile.
