========================================
Make --- Automated Documentation Builder
========================================

Usage
------

While still being actively worked on, the ideal usage would begin with the user
in the `<../docs>`_ directory of the repository and running.:

.. code-block:: console

    python3 sphinx_extensions/make html

Where *html* can be replaced with one of *html*, *singlehtml*, *doctest* or
*linkcheck*. Not all :command:`sphinx-build` options are currently supported.

Moving output files
-------------------

>>> import shutil
>>> from os.path import join as pjoin
>>> import subprocess
>>> BUILD_DIR = pjoin('build', 'html')
>>> if shutil.which('rsync'):
    >>> subprocess.run(['rsync', '-hv8r', BUILD_DIR, '.'])

You could even add one of the *delete on destination* options that rsync has.

One of them specifies to delete anything at the destination not in source.
Obviously be careful beforehand but that could be a really simple way to
automatically keep the documentation fresh.

Todo
-----
Incorporate this in.

>>> from sphinx.application import Sphinx
>>> srcdir=confdir='source'
>>> doctreedir='build/.doctrees'
>>> outdir='build/html'
>>> app = Sphinx(buildername='html', srcdir=srcdir, outdir=outdir, doctreedir=doctreedir, confdir=confdir)


See Also
--------
.. seealso::

   sphinx.cmd.build
      The main entrypoint for sphinx and a good module to get comfortable with.
   sphinx.cmd.make_main
      The pure python replacement for a ``Makefile``.
   sphinx.util.osutil


Notes
-----
Wait why don't we just do something like:

>>> import sphinx
>>> from sphinx.cmd.build import make

Or whatever it's called and run that? It'd be way easier...
