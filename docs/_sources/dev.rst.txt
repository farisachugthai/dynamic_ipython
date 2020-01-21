.. _dev:

=================
Developer's Notes
=================

.. module:: developers-notes
   :synopsis: Notes to aid anyone interested in working with this source code.

.. highlight:: bash

.. _developer-installation:

Installing
===========

In your console of choice, create a virtual environment.
This can be done with::

   virtualenv ~/.local/share/virtualenvs/dynamic_ipython --python=/usr/bin/python3.7

Then run::

   python setup.py build
   pip install -U -e .

If you'd like to build the docs, change the pip command to::

   pip install -U -e .[docs]

And likewise for the tests.


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


Sphinx Directives
-----------------

Here's a little info from the Sphinx website.

.. confval:: trim_doctest_flags

   If true, doctest flags (comments looking like ``# doctest: FLAG, ...``) at
   the ends of lines and ``<BLANKLINE>`` markers are removed for all code
   blocks showing interactive Python sessions (i.e. doctests).  Default is
   ``True``.  See the extension :mod:`~sphinx.ext.doctest` for more
   possibilities of including doctests.

.. confval:: highlight_language

   The default language to highlight source code in.  The default is
   ``'python3'``.  The value should be a valid Pygments lexer name, see
   :ref:`code-examples` for more details.

   .. versionadded:: 0.5

   .. versionchanged:: 1.4
      The default is now ``'default'``. It is similar to ``'python3'``;
      it is mostly a superset of ``'python'`` but it fallbacks to
      ``'none'`` without warning if failed.  ``'python3'`` and other
      languages will emit warning if failed.  If you prefer Python 2
      only highlighting, you can set it back to ``'python'``.


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


Utilizing Tagbar
----------------

Out of the box, Exuberant ctags and even Universal ctags
do not support rst documentation in tag files.

An external dependency, ``rst2ctags``, is required. It can be
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

.. code-block:: bash

   pygmentize -S GruvboxDarkHard -f html > _static/pygments.css


Linting
========

.. code-block:: bash

   flake8-rst --config=setup.cfg --show-source --statistics --doctest docs/source/**/*.rst --rst-directives=ipython --tee --output-file=flake8_output.log

