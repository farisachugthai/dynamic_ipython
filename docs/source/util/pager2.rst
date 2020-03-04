==========================================
:mod:`~default_profile.util.pager2` module
==========================================
.. highlight:: python

.. currentmodule:: default_profile.util.pager2

Rewrite the module that creates the ``%pycat`` magic.

In it's current implementation, the pager gives Windows a dumb terminal and
never checks for whether :command:`less` is on the :envvar:`PATH` or
if the user has a pager they wanna implement!


Original Implementation
========================

Below is the source code for how the original :magic:`pycat` was implemented.:

.. testsetup::

    from IPython import get_ipython
    from IPython.core import page
    from IPython.core.magic import line_magic
    from IPython.core.error import UsageError
    self.shell = get_ipython()

.. ipython::
   :doctest:

   @line_magic
   def pycat(self, parameter_s=''):
       """Show a syntax-highlighted file through a pager.

       This magic is similar to the cat utility, but it will assume the file
       to be Python source and will show it with syntax highlighting.
       This magic command can either take a local filename, an url,
       an history range (see %history) or a macro as argument:

       %pycat myscript.py
       %pycat 7-27
       %pycat myMacro
       %pycat http://www.example.com/myscript.py

       """
       if not parameter_s:
           raise UsageError('Missing filename, URL, input history range, '
                            'or macro.')

       try :
           cont = self.shell.find_user_code(parameter_s, skip_encoding_cookie=False)
       except (ValueError, IOError):
           print("Error: no such file, variable, URL, history range or macro")
           return

       page.page(self.shell.pycolorize(source_to_unicode(cont)))


Implementing the rewrite
========================

It might be best if we design this using traitlets.
They have the linking functions in the utils directory
so that we can observe if :data:`sphinxify_docstring` changes, or
the value of :envvar:`EDITOR` changes, or handful of other things that we'll
be expected to respond to.


Revisions
----------

Still considering different ways of designing a new Windows specific pager
on IPython. It's a bit difficult as the default implementation is over 10
years old, and it seems to mirror a similar setup from :mod:`pydoc` where a
Windows user who doesn't have :envvar:`PAGER` set will use a home-brewed
:command:`more` lite type pager.

However, I haven't found anywhere in the docs where this is mentioned which
is frustrating, in addition to the fact that both APIs are written with no
ability to change or configure things in mind.


Working Implementation
======================

Oct 28, 2019:

Just ran this in the shell and I'm really pleased with it.

It utilizes the :attr:`autocall` functionality of IPython, works with the
``pycolorize`` utils, uses the `page` core function.

If the user doesn't provide an argument, then just show them the last input
they gave us especially since that var is **guaranteed** to always
be there.

.. testsetup::

   import IPython
   from IPython import get_ipython
   from IPython.core.magic import line_magic

I believe that this magic gets loaded automatically on startup now.

.. ipython::
   :verbatim:

    In [105]: @line_magic
         ...: def p(shell=None, s=None):
         ...:     if shell is None:
         ...:         shell = get_ipython()
         ...:     if s is None:
         ...:         IPython.core.page.page(shell.pycolorize(_i))
         ...:     else:
         ...:         IPython.core.page.page(shell.pycolorize(shell.find_user_code(s, skip_encoding_cookie=True)))


.. _pydoc-bug:

Original Pydoc Implementation and Errors
----------------------------------------

Running pydoc with PAGER set on Windows doesn't catch the KeyboardInterrupt...

.. ipython::
   :verbatim:

   $ pydoc FRAMEOBJECTS
   Traceback (most recent call last):
   File "C:/tools/miniconda3/lib/runpy.py", line 193, in _run_module_as_main
      "__main__", mod_spec)
   File "C:/tools/miniconda3/lib/runpy.py", line 85, in _run_code
      exec(code, run_globals)
      elif request in self.topics: self.showtopic(request)
   File "C:/tools/miniconda3/lib/pydoc.py", line 2021, in showtopic
      return self.showtopic(target, more_xrefs)
   File "C:/tools/miniconda3/lib/pydoc.py", line 2037, in showtopic
      pager(doc)
   File "C:/tools/miniconda3/lib/pydoc.py", line 1449, in pager
      pager(text)
   File "C:/tools/miniconda3/lib/pydoc.py", line 1462, in <lambda>
      return lambda text: tempfilepager(plain(text), use_pager)
   File "C:/tools/miniconda3/lib/pydoc.py", line 1519, in tempfilepager
      os.system(cmd + ' "' + filename + '"')
   KeyboardInterrupt

Outside of the stupid traceback, that command worked perfectly for me.

I have :envvar:`PAGER` set on Windows {which I realize isn't typical},
however we should re-use this implementation entirely and cut
`IPython.core.page.page` out.

Also worth noting `IPython.core.payloadpage.page`.::

   In [63]: pydoc.pipepager(inspect.getdoc(arg), os.environ.get('PAGER'))

Despite the source code of the std lib stating that pipes are completely
broken on windows, this worked just fine for me.

Define arg as an object like if you pass a string it'll give you the help
message for a str.

:mod:`inspect` has a million more methods and pydoc does too so possibly change
the :func:`inspect.getdoc` part, but honestly that one line is 80% of the way to
what I've been trying to do.

Autogenerated Pager Docs
========================

.. automodule:: default_profile.util.pager2
   :synopsis: Rewrite how IPython utilizes the pager on Windows.
   :members:
   :undoc-members:
   :show-inheritance:
