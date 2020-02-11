#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
from pathlib import Path
from pprint import pprint
import shutil
import subprocess
import sys
from typing import List, Any
import webbrowser

if sys.version_info < (3, 7):
    from default_profile import ModuleNotFoundError

try:
    import sphinx
except (ImportError, ModuleNotFoundError):
    sys.exit("Sphinx documentation module not found. Exiting.")

from sphinx.application import Sphinx
from sphinx.cmd.make_mode import build_main
from sphinx.errors import ApplicationError
from sphinx.jinja2glue import SphinxFileSystemLoader
from sphinx.project import Project

# from jinja2.constants import TRIM_BLOCKS, LSTRIP_BLOCKS
from jinja2.environment import Environment
from jinja2.exceptions import TemplateError
from jinja2.ext import autoescape, do, with_
from jinja2.loaders import FileSystemLoader
from jinja2.lexer import get_lexer

from default_profile import ask_for_import
from default_profile.__about__ import __version__


def _setup_make_logging():
    """Setup the logging. Add a filter with no args to allow everything."""
    BASIC_FORMAT = "[%(created)f %(module)s ] %(levelname)s  %(message)s"

    logger = logging.getLogger(name="docs.sphinxext").getChild("make")
    logger.setLevel(logging.DEBUG)
    make_handler = logging.StreamHandler(stream=sys.stdout)
    make_handler.setLevel(logging.DEBUG)
    make_handler.setFormatter(logging.Formatter(fmt=BASIC_FORMAT))
    logger.addHandler(make_handler)
    logger.addFilter(logging.Filter())
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
    cmds = [method for method in dir(DocBuilder) if not method.startswith("_")]

    parser = argparse.ArgumentParser(
        prog="Pure Python Makefile",
        description="Dynamic IPython doc builder.",
        epilog="Commands: {}".format(", ".join(cmds)),
    )

    parser.add_argument(
        "builder",
        nargs="?",
        default="html",
        # ugh this shouldn't be independent of DocBuilder.kinds
        choices=["html", "singlehtml", "text", "linkcheck", "doctest"],
        metavar="builder: ",
        help="command to run: {}".format(",\t ".join(cmds)),
    )

    parser.add_argument(
        "-j",
        "--num-jobs",
        metavar="num-jobs",
        dest="jobs",
        type=int,
        default=os.cpu_count(),
        help="Number of parallel jobs used by `sphinx-build`.",
    )

    parser.add_argument(
        "-b",
        "--open_browser",
        metavar="BROWSER",
        type=bool,
        default=False,
        dest="open_browser",
        help="Toggle opening the docs in the default"
        " browser after a successful build.",
    )

    parser.add_argument(
        "-l",
        "--log",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="Where to write log records to. Defaults to" " stdout.",
    )

    parser.add_argument(
        "-ll",
        "--log-level",
        dest="log_level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level. Defaults to INFO. Implies logging.",
    )
    # reasonably should mention what the purpose of some of these are.
    # they primarily seem like toggles since they don't provide much else
    parser.add_argument(
        "-V",
        "--verbose",
        nargs="?",
        const=True,
        default=False,
        help="Enable verbose logging and increase level to `debug`.",
    )

    parser.add_argument("--version", action="version", version=__version__)

    user_args = parser.parse_args()

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        # This is actually annoying
        # raise argparse.ArgumentError(None, "Args not provided.")
        sys.exit()

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
            kind = "html"
        self.kind = kind
        self.num_jobs = num_jobs
        self.verbosity = verbosity

    def __repr__(self):
        return "{}\t{}".format(self.__class__.__name__, self.kind)

    @property
    def kinds(self):
        """Allowable sphinx-build outputs."""
        return ["html", "singlehtml", "text", "linkcheck", "doctest"]

    @staticmethod
    def status(output):
        """Print output in bold. Emits ANSI escape sequences to sys.stdout"""
        print("\033[1m{0}\033[0m".format(output))

    def cleanup(self):
        """Clean the working tree."""
        try:
            self.status("Removing previous builds…")
            shutil.rmtree("build")
        except OSError as e:
            self.MAKE_LOGGER.error(e)

    def sphinx_build(self):
        """Build docs.

        Examples
        --------
        >>> DocBuilder(num_jobs=4).sphinx_build('html')

        """
        if self.kind not in self.kinds:
            raise ValueError(
                "kind must be one of: {}".format(str(self.kinds))
                + "not {}".format(self.kind)
            )
        cmd = ["sphinx-build", "-b", self.kind, ".", "-c", SOURCE_PATH]
        if self.num_jobs:
            cmd += ["-j", str(self.num_jobs)]
        if self.verbosity:
            cmd.append("-{}".format("v" * self.verbosity))
        cmd += [
            "-d",
            os.path.join(BUILD_PATH, "doctrees"),
            os.path.join(BUILD_PATH, self.kind),
        ]
        self.MAKE_LOGGER.debug("Cmd is ", cmd)
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
            doc = "index.html"
        url = os.path.join("file://", DOC_PATH, "build", "html", doc)
        self.status("Opening path to: {!s}".format(url))
        webbrowser.open(url, new=2)


def termux_hack():
    """Android permissions don't allow viewing files in app specific files."""
    try:
        shutil.copytree(
            BUILD_PATH, "/data/data/com.termux/files/home/storage/downloads/html"
        )
    except FileExistsError:
        try:
            shutil.rmtree("/data/data/com.termux/files/home/storage/downloads/html")
            shutil.copytree(
                BUILD_PATH, "/data/data/com.termux/files/home/storage/downloads/html"
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
    if shutil.which("rsync"):
        output = subprocess.run(["rsync", "-hv8r", BUILD_PATH, DOC_PATH])
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
    pprint(
        "Your sphinx-build command was: "
        + str(
            ["-b", builder, SOURCE_PATH, BUILD_PATH, "-j", jobs, "-" + verbosity * "v"]
        )
    )
    ret = ["-b", builder, SOURCE_PATH, BUILD_PATH]
    return ret


def generate_sphinx_app():

    srcdir = confdir = "source"
    doctreedir = "build/.doctrees"
    outdir = "build/html"
    app = Sphinx(
        buildername="html",
        srcdir=srcdir,
        outdir=outdir,
        doctreedir=doctreedir,
        confdir=confdir,
    )
    return app


def setup_jinja():
    """Use jinja to set up the Sphinx environment."""
    TRIM_BLOCKS = True
    LSTRIP_BLOCKS = True
    template_path = "_templates"
    try:
        loader = FileSystemLoader(template_path)
    except TemplateError:
        return
    env = Environment(
        trim_blocks=TRIM_BLOCKS,
        lstrip_blocks=LSTRIP_BLOCKS,
        loader=FileSystemLoader(template_path),
        extensions=["jinja2.ext.i18n", autoescape, do, with_],
        enable_async=True,
    )
    return env


def main(repo_root=None):
    # Probably should initialize in a different/ better way but eh
    if ask_for_import("jinja2"):
        env = setup_jinja()
    else:
        env = Environment()

    lexer = setup_jinja()
    project = Project(repo_root, source_suffix="rst")
    # sphinx_fs = SphinxFileSystemLoader(searchpath=project.templates_path)
    build_opts = gather_sphinx_options([])
    build_main(build_opts)


if __name__ == "__main__":

    logger = _setup_make_logging()
    git_root = subprocess.run(["git", "rev-parse", "--show-root"]).stdout
    logger.debug(f"git root was: {git_root}")
    sys.exit(main(git_root))
