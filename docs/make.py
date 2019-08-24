#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=======================================
Make --- Automated Documentation Builds
=======================================

.. module:: docs.make
    :synopsis: Automated Documentation Builds

Usage
======
This module has a similar API to the command :command:`sphinx-build` as it
passes user provided arguments along to it.

It simply differs in making the process simpler and allows one to run it in
the debugger if a problem arises with doc builds.


Documentation TODO
==================
Still need to add an option to recursively move the html files out of the
currently git-ignored directory `build/html/` into this directory.

Unfortunately that's probably going to be a really ugly fight.

:func:`shutil.copytree()` and :func:`os.rename()` don't allow for
dangerous overwrites like :command:`mv` does.

So we may have to :func:`os.walk()`, copy them into the correct relative
section of the directory tree, recursively delete the old
directories and attempt to not lose all the metadata along the way.


See Also
========
sphinx.cmd.build : mod
    The main entrypoint for sphinx and a good module to get comfortable with.
sphinx.cmd.make_main : mod
    The pure python replacement for a ``Makefile``.
sphinx.util.osutil : mod
    Will definitely help with your problem below.

.. todo:: Argparse update.

    Update the options you can give to the parser.

Other Random Errands Include:
=============================
#) remove python path [x]
#) Add open in browser as an option [x]
#) Fix the output for the `commands` argument when this is run with
   :data:`sys.argv` == 0

"""
import argparse
import logging
import os
from pprint import pprint
import shlex
import shutil
import subprocess
import sys
import webbrowser

try:
    import sphinx
except (ImportError, ModuleNotFoundError):
    sys.exit("Sphinx documentation module not found. Exiting.")

from IPython.core.error import UsageError

from profile_default.__about__ import __version__

DOC_PATH = os.path.dirname(os.path.abspath(__file__))
BUILD_PATH = os.path.join(DOC_PATH, 'build')
SOURCE_PATH = os.path.join(DOC_PATH, 'source')
MAKE_LOGGER = logging.getLogger(name='docs.make')
MAKE_LOGGER.setLevel(logging.DEBUG)


def _parse_arguments(cmds=None):
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
        epilog="Commands: {}".format(', '.join(cmds)))

    parser.add_argument('builder',
                        nargs='?',
                        default='html',
                        choices=['html', 'latex'],
                        metavar='builder: (html or latex)',
                        help='command to run: {}'.format(',\t '.join(cmds)))

    parser.add_argument('-j',
                        '--num-jobs',
                        metavar='num-jobs',
                        dest='jobs',
                        type=int,
                        default=os.cpu_count(),
                        help='Number of parallel jobs used by `sphinx-build`.')

    parser.add_argument('-s',
                        '--single',
                        metavar='FILENAME',
                        default=None,
                        help='filename of section or method name to build.')

    parser.add_argument('-b',
                        '--open_browser',
                        metavar='BROWSER',
                        type=bool,
                        default=False,
                        dest='open_browser',
                        help='Toggle opening the docs in the default'
                        ' browser after a successful build.')

    parser.add_argument('-l',
                        '--log',
                        default=sys.stdout,
                        type=argparse.FileType('w'),
                        help='Where to write log records to. Defaults to'
                        ' stdout.')

    parser.add_argument(
        '-ll',
        '--log-level',
        dest='log_level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level. Defaults to INFO. Implies logging.')
    # reasonably should mention what the purpose of some of these are.
    # they primarily seem like toggles since they don't provide much else
    parser.add_argument(
        '-V',
        '--verbose',
        nargs='?',
        const=True,
        default=False,
        help='Enable verbose logging and increase level to `debug`.')

    parser.add_argument('--version', action='version', version=__version__)

    user_args = parser.parse_args()

    # if len(sys.argv[1:]) == 0:
    #     parser.print_help()
    #     sys.exit()

    return user_args


class DocBuilder:
    """Class to wrap the different commands of this script.

    All public methods of this class can be called as parameters of the
    script.

    Attributes
    -----------
    builder : str
        The filetype :command:`make` invokes :command:`sphinx-build` to create.

    """
    def __init__(self, kind='html', num_jobs=1, verbosity=0):
        """Kind has to be first in case the user uses the class with a positional parameter.

        Parameters
        ----------
        kind : str, optional
            The kind of document ``sphinx-build`` will create.
        num_job : int, optional
            Number of jobs to run the build in parallel with.
        verbose : bool, optional
            Run verbosely

        Examples
        --------
        >>> d = DocBuilder('html')
        >>> print(d.kind)
        'html'

        """
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

        Parameters
        ----------
        kind : {'html', 'singlehtml', 'doctest', 'text'}
            Kind of docs to build.

        Examples
        --------
        >>> DocBuilder(num_jobs=4).sphinx_build('html')

        """
        if self.kind not in self.kinds:
            raise ValueError(
                'kind must be one of: {}'.format(str(self.kinds)) +
                'not {}'.format(self.kind))
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

    def open_browser(self, doc):
        """Open a browser tab to the provided document."""
        url = os.path.join('file://', DOC_PATH, 'build', 'html', doc)
        webbrowser.open(url, new=2)

    def html(self):
        """Build HTML documentation."""
        ret_code = self.sphinx_build('html')
        zip_fname = os.path.join(BUILD_PATH, 'html', 'pandas.zip')
        if os.path.exists(zip_fname):
            os.remove(zip_fname)

        if self.single_doc_html is not None:
            self._open_browser(self.single_doc_html)
        else:
            self._add_redirects()
        return ret_code


def termux_hack():
    """Android permissions don't allow viewing files in app specific files."""
    try:
        shutil.copytree(
            '_build/html/',
            '/data/data/com.termux/files/home/storage/downloads/html')
    except FileExistsError:
        shutil.rmtree(
            '/data/data/com.termux/files/home/storage/downloads/html')
        shutil.copytree(
            '_build/html/',
            '/data/data/com.termux/files/home/storage/downloads/html')
    except FileNotFoundError:
        MAKE_LOGGER.error("Sphinx was unable to create the build directory.")


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

    if args.open_browser:
        sphinx_shell.open_browser()
        sphinx_shell.status('Opening browser!')

    return output


if __name__ == "__main__":
    status = main()
    pprint(status)

    if os.environ.get('ANDROID_ROOT'):
        termux_hack()
