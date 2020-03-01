============================================
Welcome to Dynamic IPython's documentation!
============================================

:date: |today|

.. highlight:: ipython

.. moduleauthor:: Faris Chugthai

.. module:: root_index
   :synopsis: Main landing page for the documentation.


Startup Scripts
================

This repository hosts startup scripts that can be used during
IPython's startup.

The scripts add well over 1000 aliases to the namespace, import commonly used
modules, instantiate exception hooks from `cgitb`, format a `traceback`,
import readline to add additional keybindings as well as checking for pyreadline
for Windows users, lex documents with the `pygments` library and stylize the
REPL as a  result, add multiple application specific loggers, and more.

Heavy use of `prompt_toolkit` and Jedi's respective APIs are utilized here.

As both libraries as well as pygments are explicit dependencies of IPython,
no additional installation is required for those features.

Specifically, new completers are added to the shell to handle fuzzy completion
as well as autocompletion of paths and executables.


.. _root-extensions:

Extensions
==========

In addition this repository handles a growing number of IPython extensions.

Some of the bundled extensions provide a more usable `PAGER` for users on
Window than the one provided by `pydoc`, others modify runtime behavior of

To see more, continue reading about :ref:`extensions`.


Portability
============

Portability was a major factor while writing these scripts.

Therefore, any script should work on:

- Ubuntu
- Android
- Windows 10

On Windows 10, the scripts have been primarily tested in powershell
windows or in a shell with either ConEmu or Cmder.

As a result, there may be unexpected behavior that arises when running the
following scripts while within in an unmodified :command:`cmd` shell.


Motivation
===========

The intent was to create a system that worked on any relatively
modern platform.

I regularly use :mod:`IPython` as a system shell in comparison to the
typical Bash shell that Unix OSes provide. While a terminal provides a
huge number of powerful commands and the ability to pipe them together,
Bash still has a number of inconsistencies and oddities in its behavior.

Installation
============

This repository can be installed in the following manner.:

.. ipython::
   :verbatim:

   python setup.py build
   pip install -U -e .

However, that unfortunately assumes one has admin access to wherever pip
installs files globally, and that the :command:`python` command points to
python3.7. In most cases it does not.

If one has :command:`pipenv` installed, an easier installation could be

.. ipython::
   :verbatim:

   pipenv install -e .

If a non-pipenv installation is desired for some reason, a fully specified
installation could look like.

.. ipython::
   :verbatim:

   python3.7 setup.py build
   python3.7 -m pip install -U --user pip -e .

As one can see this gets complicated very quickly, and as a result,
installation via pipenv is the recommended method.


Assumptions
===========

Neovim is the default editor.

If this behavior isn't desired, the following parameter needs to be
changed like so::

   from traitlets import get_config
   c = get_config()
   c.TerminalInteractiveShell.editor = 'nvim'

See Also
----------

For further reading, feel free to see the output of any of the following.

.. ipython::
   :verbatim:

   >>> from IPython.core.interactiveshell import InteractiveShell
   >>> help(InteractiveShell)

Which features descriptions of functions relevant to startup such as
:func:`IPython.core.interactiveshell.register_magic_function` and literally
every option available through the `%config` magic.

For commands that are more related to the interactive aspect of the shell,
see the following.

.. ipython::
   :verbatim:

   >>> from IPython import get_ipython
   >>> _ip = get_ipython()
   >>> help(_ip)  # doctest: +SKIP
   >>> dir(_ip):  # doctest: +SKIP

In addition, there's an abundance of documentation online in the
form of rst docs and :abbr:`ipynb` notebooks.

.. _root-toc:

Table of Contents
==================

{% if single_doc and single_doc.endswith('.rst') -%}
.. toctree::
    :maxdepth: 3
    :titlesonly:
 
    {{ single_doc[:-4] }}
{% elif single_doc %}
.. autosummary::
    :toctree: reference/api/
 
    {{ single_doc }}
{% else -%}
.. toctree::
    :maxdepth: 3
    :hidden:
    :titlesonly:
{% endif %}

Startup
-------

.. toctree::
   :titlesonly:
   :maxdepth: 2
   :caption: IPython Startup

   Startup <startup/index>
   rehashx <startup/rehashx>
   ipython-logger <startup/ipython-logger>
   help_helpers <startup/help_helpers.rst>
   clipboard <startup/clipboard>
   aliases <startup/aliases>
   fzf <startup/fzf>
   setup_readline <startup/setup_readline>
   prompt_toolkit <startup/prompt_toolkit>
   41_numpy <startup/41_numpy>
   eventloops <startup/eventloops>


.. _sphinxext-package:

Sphinx Extensions
-----------------

The `default_profile.sphinxext` package.

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :caption: sphinx

   sphinxext/ipython_sphinx_directive
   sphinxext/lexer
   sphinxext/custom_doctests
   sphinxext/magics
   sphinxext/make


Remaining API
-------------

.. toctree::
   :titlesonly:
   :caption: Remaining API
   :maxdepth: 2

   IPython Utilities <util/index>
   Extensions <extensions/index>
   Developers Notes <dev>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
