============================================
Welcome to Dynamic IPython's documentation!
============================================

:date: |today|

.. highlight:: ipython

.. moduleauthor:: Faris Chugthai

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
``pipenv install -e .``

If a non-pipenv installation is desired for some reason, a fully 
specified installation could look like.

.. code-block:: bash

   python3 setup.py build
   python3 -m pip install -U --user pip -e .

As one can see this gets complicated very quickly, and as a 
result, installation via pipenv is the recommended method.


See Also
----------

For commands that are more related to the interactive aspect of the shell,
see the following.

.. ipython:: python
   :verbatim:

   from IPython import get_ipython
   _ip = get_ipython()
   help(_ip)  # doctest: +SKIP
   dir(_ip):  # doctest: +SKIP

Which features descriptions of functions relevant to startup such as
:func:`IPython.core.interactiveshell.register_magic_function` and literally
every option available through the `%config` magic.

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
   IPython Logger <startup/ipython-logger>
   Help Helpers <startup/help_helpers.rst>
   Clipboard <startup/clipboard>
   Aliases <startup/aliases>
   FZF <startup/fzf>
   Setup Readline <startup/setup_readline>
   prompt_toolkit <startup/prompt_toolkit>
   Toolbar <startup/toolbar>
   Lexer <startup/lexer>
   Numpy <startup/41_numpy>
   Eventloops <startup/eventloops>


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


Extensions
--------------

In addition this repository handles a growing number of IPython extensions.

Some of the bundled extensions provide a more usable `PAGER` for users on
Window than the one provided by `pydoc`.

.. index:: %magic

.. automodule:: default_profile.extensions
    :synopsis: Write additions to the IPython ecosystem and additional magics.

Here are the varying `%magic` extensions that are bundled with this
portion of the repository.

.. toctree::
   :maxdepth: 1
   :glob:
   :titlesonly:
   :caption: Extensions

   Pandas CSV <extensions/pandas_csv>
   repr_requests <extensions/repr_requests>

Continue reading with the pandas extension at :ref:`extensions/pandas_csv`.


.. _util-contents:

Utilities
---------------

.. automodule:: default_profile.util
   :members:
   :undoc-members:
   :show-inheritance:


The submodules contained in this package are as follows:

Utilities Submodules
~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :glob:

   util/*
   Developers Notes <dev>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
