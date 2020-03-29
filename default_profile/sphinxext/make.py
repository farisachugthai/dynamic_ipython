#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import codecs
import locale
import os
import pathlib
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

import importlib_metadata

# from jinja2.constants import TRIM_BLOCKS, LSTRIP_BLOCKS
import jinja2
from jinja2.environment import Environment
from jinja2.exceptions import TemplateError
from jinja2.ext import autoescape, do, with_
from jinja2.loaders import FileSystemLoader

import sphinx
from sphinx.application import Sphinx

# from sphinx.cmd.build import build_main
# from sphinx.cmd.build import handle_exception
from sphinx.cmd.make_mode import Make
from sphinx.errors import ApplicationError

# from sphinx.jinja2glue import SphinxFileSystemLoader
# from sphinx.util.console import (  # type: ignore
#   colorize, color_terminal
# )
from sphinx.util.docutils import patch_docutils, docutils_namespace
from sphinx.util.logging import getLogger

# from sphinx.ext.apidoc import create
# from sphinx.ext.autosummary.generate import

if sys.version_info < (3, 7):
    pass

logger = getLogger(name=__name__)


def _parse_arguments() -> argparse.ArgumentParser:
    """Parse user arguments.

    Returns
    -------
    user_args : :class:`argparse.NameSpace`
        Argumemts as they've been interpreted by :mod:`argparse`.

    See Also
    --------
    :mod:`docutils.core`
        Shows a few good methods on how to programatically publish docs.

    """
    cmds = [method for method in dir(Runner) if not method.startswith("_")]

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
        "-s", "--sourcedir", default=Path.cwd(), help="Sourcedir to pass to Sphinx",
    )

    parser.add_argument(
        "-d", "--destdir", default=None, help="Sourcedir to pass to Sphinx",
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

    dist = importlib_metadata.Distribution().from_name("dynamic_ipython")
    __version__ = dist.version
    parser.add_argument("--version", action="version", version=__version__)

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        # This is actually annoying
        # raise argparse.ArgumentError(None, "Args not provided.")
        sys.exit()

    return parser


class DocBuilder:
    def __init__(self, kind=None, num_jobs=1, verbosity=0, root=None):
        if kind is None:
            kind = "html"
        self.kind = kind
        self.num_jobs = num_jobs
        self.verbosity = verbosity
        self.root = root if root is not None else os.getcwd()

    def __repr__(self):
        return "{}\t{}".format(self.__class__.__name__, self.kind)

    def __call__(self, kind):
        return self.run(kind)

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
            logger.error(e)

    def sphinx_build(self, kind, BUILD_PATH=None):
        """Build docs.

        Examples
        --------
        >>> DocBuilder(num_jobs=4).sphinx_build('html')

        """
        BUILD_PATH = (
            BUILD_PATH if BUILD_PATH is not None else Path.cwd().joinpath("build")
        )
        if kind not in self.kinds:
            raise ValueError(
                "kind must be one of: {}".format(str(self.kinds))
                + "not {}".format(kind)
            )
        cmd = ["sphinx-build", "-b", kind, ".", "-c", self.root]
        if self.num_jobs:
            cmd += ["-j", str(self.num_jobs)]
        if self.verbosity:
            cmd.append("-{}".format("v" * self.verbosity))
        cmd += [
            "-d",
            os.path.join(BUILD_PATH, "doctrees"),
            os.path.join(BUILD_PATH, kind),
        ]
        logger.debug("Cmd is ", cmd)
        return cmd

    def run(self, kind):
        """Run :command:`sphinx-build`.

        The :attr:`check` argument to :func:`subprocess.run()`
        is not enabled so there's no need to catch
        :class:`subprocess.CalledProcessError()`.
        """
        # Shit is that really the only time you gotta catch it?
        self.status("Running sphinx-build.")
        return (
            codecs.decode(
                subprocess.run(
                    self.sphinx_build(kind),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                ).stdout,
                "utf-8",
            ).strip(),
        )

    def open_browser(self, doc=None):
        """Open a browser tab to the provided document.
        :rtype: object
        """
        if doc is None:
            doc = "index.html"
        url = os.path.join("file://", self.root, "build", "html", doc)
        self.status("Opening path to: {!s}".format(url))
        webbrowser.open(url, new=2)


class Runner:
    def __init__(self, **kwargs):
        self.builder = DocBuilder(**kwargs)

    def html(self):
        return self.builder.run("html")

    def man(self):
        return self.builder.run("man")

    def doctest(self):
        return self.builder.run("doctest")

    def texinfo(self):
        return self.builder.run("texinfo")


def generate_autosummary(**kwar):
    from sphinx.ext.autosummary.generate import generate_autosummary_docs

    generate_autosummary_docs(**kwar)


def generate_sphinx_app(root, namespace):
    """Generate the primary Sphinx application object that drives the project.

    Parameters
    ----------
    root : str
        The root of the repositories docs
    namespace : arparse.NameSpace
        User provided arments.

    Returns
    -------
    app : Sphinx
        :class:`sphinx.application.Sphinx` instance.

    """
    srcdir = confdir = root.joinpath("source")
    doctreedir = "build/.doctrees"
    outdir = "build/html"
    if hasattr(namespace, "verbosity"):
        if namespace.verbosity < 20:
            verbosity = 2
        elif namespace.verbosity < 40:
            verbosity = 1
        else:
            verbosity = 0
    else:
        verbosity = 0
    try:
        with patch_docutils(confdir), docutils_namespace():
            app = Sphinx(
                buildername=namespace.builder
                if namespace.builder is not None
                else "html",
                srcdir=srcdir,
                outdir=outdir,
                doctreedir=doctreedir,
                confdir=confdir,
                parallel=namespace.jobs,
                verbosity=verbosity,
            )
            app.build()
            return app.statuscode

    except ApplicationError:
        raise
    except (Exception, KeyboardInterrupt) as exc:
        # handle_exception(app, namespace, exc)
        return 2


def get_jinja_loader(template_path=None):
    if template_path is None:
        template_path = "_templates"
    try:
        loader = FileSystemLoader(template_path)
    except TemplateError:
        return
    return loader


def setup_jinja(path_to_template: pathlib.Path) -> jinja2.environment.Environment:
    """Use jinja to set up the Sphinx environment."""
    TRIM_BLOCKS = True
    LSTRIP_BLOCKS = True
    loader = get_jinja_loader(path_to_template)
    env = Environment(
        trim_blocks=TRIM_BLOCKS,
        lstrip_blocks=LSTRIP_BLOCKS,
        loader=loader,
        extensions=["jinja2.ext.i18n", autoescape, do, with_],
        enable_async=True,
    )
    return env


class Maker(Make):
    def __init__(self, source_dir, build_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_dir = source_dir
        self.build_dir = build_dir

    def run_generic_build(self, **kwargs):
        # TODO
        pass

    def __repr__(self):
        return self.__class__.__name__


def main(repo_root=None):
    """Create the required objects to simulate the sphinx make-main command.

    Create a `jinja2.Environment`, a `sphinx.project.Project`,
    `sphinx.jinja2glue.SphinxFileSystemLoader`.

    .. todo:: Need to create tags for use in `sphinx.config.eval_config_file`.

    """
    # Probably should initialize in a different/ better way but eh
    # build_opts = gather_sphinx_options()
    user_parser = _parse_arguments()
    user_args = user_parser.parse_args()
    doc_root = Path(repo_root).joinpath("docs")
    template_path = doc_root.joinpath("source/_templates")
    env = setup_jinja(template_path)

    if user_args.log:
        logger.setLevel(30)
        logger.info(f"git root was: {repo_root}")
        logger.info(f"jinja env: {env}")
    generate_sphinx_app(doc_root, user_args)


def get_git_root():
    try:
        almost = codecs.decode(
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"]), "utf-8"
        )
        return almost.rstrip()
    except subprocess.CalledProcessError as e:
        print(e)
        return os.getcwd()


if __name__ == "__main__":
    git_root = get_git_root()
    locale.setlocale(locale.LC_ALL, "")
    sys.exit(main(git_root))
