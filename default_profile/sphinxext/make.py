#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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

"""
import argparse
import logging
import os
from pprint import pprint
import shutil
import subprocess
import sys
from typing import List, Any
import webbrowser

try:
    import sphinx
except (ImportError, ModuleNotFoundError):
    sys.exit("Sphinx documentation module not found. Exiting.")

from sphinx.jinja2glue import SphinxFileSystemLoader
from jinja2.environment import Environment

from sphinx.cmd.make_mode import build_main

from default_profile.__about__ import __version__

DOC_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_PATH = os.path.join(DOC_PATH, 'build')
SOURCE_PATH = os.path.join(DOC_PATH, 'source')
TEMPLATES_PATH = os.path.join(SOURCE_PATH, '_templates')


# Probably should initialize in a different/ better way but eh
env = Environment()

sphinx_fs = SphinxFileSystemLoader(searchpath=TEMPLATES_PATH)


def _setup_make_logging():
    logging.BASIC_FORMAT = '%(created)f : %(module)s : %(levelname)s : %(message)s'

    logger = logging.getLogger(name='docs').getChild('make')
    logger.setLevel(logging.DEBUG)
    make_handler = logging.StreamHandler(stream=sys.stdout)
    make_handler.setLevel(logging.DEBUG)
    make_handler.setFormatter(logging.Formatter(fmt=logging.BASIC_FORMAT))
    logger.addHandler(make_handler)
    return logger


def _parse_arguments(cmds=None) -> argparse.ArgumentParser:
    """Parse user arguments.

    Parameters
    ----------
    cmd : str
        Arguments provided by the user.

    Returns
    -------
    user_args : :class:`argparse.NameSpace`
        Argumemts as they've been interpreted by :mod:`argparse`.

    See Also
    --------
    :mod:`docutils.core`
        Shows a few good methods on how to programatically publish docs.

    """
    cmds = [method for method in dir(DocBuilder) if not method.startswith('_')]

    parser = argparse.ArgumentParser(
        prog="Pure Python Makefile",
        description="Dynamic IPython doc builder.",
        epilog="Commands: {}".format(', '.join(cmds))
    )

    parser.add_argument(
        'builder',
        nargs='?',
        default='html',
        # ugh this shouldn't be independent of DocBuilder.kinds
        choices=['html', 'singlehtml', 'text', 'linkcheck', 'doctest'],
        metavar='builder: ',
        help='command to run: {}'.format(',\t '.join(cmds))
    )

    parser.add_argument(
        '-j',
        '--num-jobs',
        metavar='num-jobs',
        dest='jobs',
        type=int,
        default=os.cpu_count(),
        help='Number of parallel jobs used by `sphinx-build`.'
    )

    parser.add_argument(
        '-b',
        '--open_browser',
        metavar='BROWSER',
        type=bool,
        default=False,
        dest='open_browser',
        help='Toggle opening the docs in the default'
        ' browser after a successful build.'
    )

    parser.add_argument(
        '-l',
        '--log',
        default=sys.stdout,
        type=argparse.FileType('w'),
        help='Where to write log records to. Defaults to'
        ' stdout.'
    )

    parser.add_argument(
        '-ll',
        '--log-level',
        dest='log_level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level. Defaults to INFO. Implies logging.'
    )
    # reasonably should mention what the purpose of some of these are.
    # they primarily seem like toggles since they don't provide much else
    parser.add_argument(
        '-V',
        '--verbose',
        nargs='?',
        const=True,
        default=False,
        help='Enable verbose logging and increase level to `debug`.'
    )

    parser.add_argument('--version', action='version', version=__version__)

    user_args = parser.parse_args()

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        sys.exit('Args not provided.')

    return user_args


class DocBuilder:
    """Class to wrap the different commands of this script.

    All public methods of this class can be called as parameters of the
    script.

    Attributes
    -----------
    kind : str
        The filetype :command:`make` invokes :command:`sphinx-build` to create.

    """
    MAKE_LOGGER = _setup_make_logging()

    def __init__(self, kind=None, num_jobs=1, verbosity=0):
        """Kind has to be first in case the user uses the class with a positional parameter.

        Parameters
        ----------
        kind : str, optional
            The kind of document ``sphinx-build`` will create.
            Defaults to html.
        num_jobs : int, optional
            Number of jobs to run the build in parallel with.
        verbosity : bool, optional
            Run verbosely

        Examples
        --------
        >>> d = DocBuilder('html')
        >>> print(d.kind)
        'html'

        """
        if kind is None:
            kind = 'html'
        self.kind = kind
        self.num_jobs = num_jobs
        self.verbosity = verbosity

    def __repr__(self):
        return '{}\t{}'.format(self.__class__.__name__, self.kind)

    @property
    def kinds(self):
        """Allowable sphinx-build outputs."""
        return ['html', 'singlehtml', 'text', 'linkcheck', 'doctest']

    @staticmethod
    def status(output):
        """Print output in bold. Emits ANSI escape sequences to sys.stdout"""
        print('\033[1m{0}\033[0m'.format(output))

    def cleanup(self):
        """Clean the working tree."""
        try:
            self.status('Removing previous builds…')
            shutil.rmtree('build')
        except OSError as e:
            MAKE_LOGGER.error(e)

    def sphinx_build(self):
        """Build docs.

        Examples
        --------
        >>> DocBuilder(num_jobs=4).sphinx_build('html')

        """
        if self.kind not in self.kinds:
            raise ValueError(
                'kind must be one of: {}'.format(str(self.kinds)) +
                'not {}'.format(self.kind)
            )
        cmd = ['sphinx-build', '-b', self.kind, '.', '-c', SOURCE_PATH]
        if self.num_jobs:
            cmd += ['-j', str(self.num_jobs)]
        if self.verbosity:
            cmd.append('-{}'.format('v' * self.verbosity))
        cmd += [
            '-d',
            os.path.join(BUILD_PATH, 'doctrees'),
            os.path.join(BUILD_PATH, self.kind)
        ]
        MAKE_LOGGER.debug('Cmd is ', cmd)
        return cmd

    def run(self):
        """Run :command:`sphinx-build`.

        The :attr:`check` argument to :func:`subprocess.run()`
        is not enabled so there's no
        need to catch
        :class:`subprocess.CalledProcessError()`.
        """
        self.status("Running sphinx-build.")
        output = subprocess.run(
            self.sphinx_build(),
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return output

    def open_browser(self, doc=None):
        """Open a browser tab to the provided document."""
        if doc is None:
            doc = 'index.html'
        url = os.path.join('file://', DOC_PATH, 'build', 'html', doc)
        self.status('Opening path to: {!s}'.format(url))
        webbrowser.open(url, new=2)

    @classmethod
    def html(cls):
        """Build HTML documentation.

        .. todo:: Practice making classmethods

            Double check that this is created correctly.
            Probably should review the git log if you're wondering why this is
            so bare.

        Parameters
        ----------
        cls : class
            By convention?

        """
        # so do we not set self.kind to html? Just pass it in like that?
        ret_code = cls.sphinx_build('html')

        return ret_code


def termux_hack():
    """Android permissions don't allow viewing files in app specific files."""
    try:
        shutil.copytree(
            BUILD_PATH,
            '/data/data/com.termux/files/home/storage/downloads/html'
        )
    except FileExistsError:
        try:
            shutil.rmtree(
                '/data/data/com.termux/files/home/storage/downloads/html'
            )
            shutil.copytree(
                BUILD_PATH,
                '/data/data/com.termux/files/home/storage/downloads/html'
            )
        except Exception as e:
            raise e
    except FileNotFoundError:
        MAKE_LOGGER.error("Sphinx was unable to create the build directory.")


def rsync():
    """Move docs into the right location with rsync

    Returns
    -------
    None

    """
    if shutil.which('rsync'):
        output = subprocess.run(['rsync', '-hv8r', BUILD_PATH, DOC_PATH])
        return output


def gather_sphinx_options(argv: List[str]) -> Any:
    """Gather parsed arguments and hand them to sphinx-build in a more direct manner.

    Parameters
    ----------
    argv : list
        User provided arguments

    Returns
    -------
    ret : int (? or maybe just the parsed options?)
        Return code from sphinx-build

    """
    args = _parse_arguments()
    jobs = args.jobs
    verbosity = args.verbose
    builder = args.builder

    # Necessary enough to justify not making a logrecord.
    pprint('Your sphinx-build command was: ' + str(
        ['-b', builder,
         SOURCE_PATH, BUILD_PATH,
         '-j', jobs, '-' + verbosity * 'v'
         ]))
    ret = build_main(['-b', builder, SOURCE_PATH, BUILD_PATH])
    return ret


def main():
    """Set everything up."""
    args = _parse_arguments()

    # there's a default for all arguments so no need for try/excepts
    log_level = args.log_level.upper()
    MAKE_LOGGER.setLevel(log_level)
    jobs = args.jobs
    verbosity = args.verbose
    builder = args.builder

    sphinx_shell = DocBuilder(kind=builder, num_jobs=jobs, verbosity=verbosity)
    output = sphinx_shell.run()

    if output.returncode != 0:
        print(
            'Command failed with return code: {} '.format(output.returncode)
        )
        sys.exit(output.stderr)

    if args.open_browser:
        sphinx_shell.open_browser()
        sphinx_shell.status('Opening browser!')

    return output


if __name__ == "__main__":
    # status = main()
    # pprint(status)
    # print(rsync())
    MAKE_LOGGER = _setup_make_logging()
    argv = sys.argv[1:]
    pprint(gather_sphinx_options(argv))
