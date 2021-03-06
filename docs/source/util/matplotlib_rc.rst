.. _matplotlib-startup:

==================
Matplotlib Startup
==================

.. highlight:: python3

We'll begin documenting the configuration for :mod:`matplotlib` and how the
built-in :mod:`matplotlib.pyplot` API can be utilized for
IPython's configuration.

.. ipython::

   In [16]: import matplotlib as mpl

   In [17]: mpl.pyplot.rc
   Out[17]: <function matplotlib.pyplot.rc(group, \*\*kwargs)>

   In [18]: # pdoc mpl.pyplot.rc

Where the `%pdoc` magic produces:

   Class docstring:
       Set the current rc params.  *group* is the grouping for the rc, e.g.,
       for ``lines.linewidth`` the group is ``lines``, for
       ``axes.facecolor``, the group is ``axes``, and so on.  Group may
       also be a list or tuple of group names, e.g., (*xtick*, *ytick*).
       *kwargs* is a dictionary attribute name/value pairs, e.g.,::

         rc('lines', linewidth=2, color='r')

       sets the current rc params and is equivalent to::

         rcParams['lines.linewidth'] = 2
         rcParams['lines.color'] = 'r'

       The following aliases are available to save typing for interactive
       users:

       =====   =================
       Alias   Property
       =====   =================
       'lw'    'linewidth'
       'ls'    'linestyle'
       'c'     'color'
       'fc'    'facecolor'
       'ec'    'edgecolor'
       'mew'   'markeredgewidth'
       'aa'    'antialiased'
       =====   =================

       Thus you could abbreviate the above rc command as::

             rc('lines', lw=2, c='r')


       Note you can use python's kwargs dictionary facility to store
       dictionaries of default parameters.  e.g., you can customize the
       font rc as follows::

         font = {'family' : 'monospace',
                 'weight' : 'bold',
                 'size'   : 'larger'}

         rc('font', **font)  # pass in the font dict as kwargs

       This enables you to easily switch between several configurations.  Use
       ``matplotlib.style.use('default')`` or :func:`~matplotlib.rcdefaults` to
       restore the default rc params after changes.
   Call docstring:
       Call self as a function.


Well that's neat!

So fun fact: If you write a :func:`print` statement in a code-block
it'll generate error as no code is saved and you essentially created an
empty block.

But running `%pdoc` will actually output a classes docstring to your terminal
in the middle of a sphinx build!
