.. _dev:

=================
Developer's Notes
=================

.. module:: developers-notes
   :synopsis: Notes to aid anyone interested in working with this source code.

.. highlight:: console


.. _developer-installation:

Installing
===========

All of the resources necessary for installing the contents of this repository
have been moved to the directory `tools <tools>`_.

There are environment files for Conda on both `Linux
<tools/environment_linux.txt>`_ and `Windows <tools/environment_windows.yml>`_,
`a Pipfile <tools/Pipfile>`_, `a requirements.txt <tools/requirements.txt>`_,
and another for a `development installation <tools/requirements_dev.txt>`_,
as well as a `tox.ini <tools/tox.ini>`_.

Therefore the number of files that one can use to install this repository grew
large enough that they've all been moved to their own separate folder.


Installation Assumptions
------------------------

In addition, the scripts therein make a few assumptions. One is that
the repository at `<https://github.com/farisachugthai/Gruvbox-IPython>`_
has been installed.

The other assumption, the subject of many online debates, is that the user
wants to use the text editor Neovim as their default editor.

The editor will be invoked whenever the user runs the line magic `%edit`.

If this behavior isn't desired, the following parameter needs to be
changed like so::

   from traitlets import get_config
   c = get_config()
   c.TerminalInteractiveShell.editor = 'nvim'


Building Documentation
======================

Building the HTML documentation requires Sphinx and numpydoc, both of which
can be installed using Anaconda::

    conda install sphinx numpydoc

If you installed using another distribution of Python, these dependencies
can also be installed using either ``easy_install`` or ``pip``::

    easy_install install sphinx numpydoc
    pip install sphinx numpydoc

To build the HTML documentation on Windows using :command:`cmd`, run::

    make html

From PowerShell, run.:

.. code-block:: powershell

    PS> .\make html


Setting ``&makeprg``
--------------------

While working in Vim, the following commands can be useful for building
documentation.:

.. code-block:: vim

   let &makeprg = 'sphinx-build '
   cd docs                " assuming set shellslash has been run if $OS=='Windows_NT'
   make -b html . ../build

Generally it's more difficult to specify parameters in the ``&makeprg`` option
than it is to write them out manually on the cmdline and allows for less
configurability.

Therefore it's best to leave ``&makeprg`` as minimal as possible, and if
necessary, build arguments into a mapping.

In addition, ``&makeprg`` is not an option one is allowed to set in a modeline
so it's important to take that into consideration.

.. wait can we specify everything and then override it?


:mod:`default_profile.sphinxext.magics`
---------------------------------------
.. automodule:: default_profile.sphinxext.magics

.. currentmodule:: developers_notes

:mod:`~default_profile.sphinxext.configtraits`
----------------------------------------------
.. automodule:: default_profile.sphinxext.configtraits


Utilizing Tagbar
----------------

Out of the box, Exuberant ctags and even Universal ctags
doesn't support rst documentation.

An external dependency in rst2ctags is required which can be
found at `this repo <https://github.com/jszakmeister/rst2ctags.git>`_.

.. code-block:: vim

   let g:tagbar_type_rst = {
       \ 'ctagstype': 'rst',
       \ 'ctagsbin' : expand('$HOME/src/rst2ctags/rst2ctags.py'),
       \ 'ctagsargs' : '-f - --sort=yes',
       \ 'kinds' : [
       \ 's:sections',
       \ 'i:images'
       \ ],
       \ 'sro' : '|',
       \ 'kind2scope' : {
       \ 's' : 'section',
       \ },
       \ 'sort': 0,
       \ }


Automatically well formatted config files
-----------------------------------------

Buffer searches to reformat the default config files.

.. code-block:: vim

   :%s/##/#
   :%s/#c/# c/
   :%s/^#$\n//

Should kill most linter errors.

Generating CSS
==============

Pygments can generate CSS with the following command in the shell:

.. code-block:: shell

   pygmentize -S GruvboxDarkHard -f html > _static/pygments.css
