#!/usr/bin/env python
# -*- coding: utf-8 -*-
# {{{
import argparse
import codecs
import locale
import os
import pprint
import shutil
import subprocess
import sys
from pathlib import Path
from typing import (IO, TYPE_CHECKING, Any, AnyStr, Callable, Dict, List,
                    Optional, Union)

import jinja2
import sphinx
from docutils import nodes
from docutils.core import publish_doctree
from jinja2.environment import Environment
from jinja2.exceptions import TemplateError
from jinja2.ext import autoescape, do, with_
from jinja2.lexer import get_lexer
# 'FileSystemBytecodeCache': < class 'jinja2.bccache.FileSystemBytecodeCache' >,
from jinja2.loaders import FileSystemLoader
from jinja2.nodes import EvalContext
from jinja2.runtime import Context
from pygments.lexers.markup import MarkdownLexer, RstLexer
from pygments.lexers.python import (NumPyLexer, PythonConsoleLexer,
                                    PythonLexer, PythonTracebackLexer)
from pygments.lexers.shell import BashLexer
from pygments.lexers.textedit import VimLexer
# side effect: registers roles and directives
from sphinx import directives  # noqa
from sphinx import roles  # noqa
from sphinx import package_dir
from sphinx.application import Sphinx
# theme_factory = HTMLThemeFactory(self.app)
# Then make this
from sphinx.builders.html import StandaloneHTMLBuilder
# from sphinx.cmd.build import build_main
# from sphinx.cmd.build import handle_exception
from sphinx.cmd.make_mode import Make
from sphinx.config import Config
from sphinx.environment import (CONFIG_CHANGED_REASON, CONFIG_OK,
                                BuildEnvironment)
from sphinx.environment.adapters.asset import ImageAdapter
# This could be super useful
# from sphinx.environment.adapters.toctree import TocTree
from sphinx.errors import ApplicationError, ConfigError
# , ExtensionError
from sphinx.events import EventManager, core_events
from sphinx.io import SphinxStandaloneReader, read_doc
from sphinx.jinja2glue import BuiltinTemplateLoader, SphinxFileSystemLoader
from sphinx.locale import __
from sphinx.parsers import RSTParser
from sphinx.util import import_object, progress_message, rst, status_iterator
from sphinx.util.build_phase import BuildPhase
from sphinx.util.console import bold  # type: ignore
from sphinx.util.docfields import GroupedField
# from sphinx.util.console import (  # type: ignore
#   colorize, color_terminal
# )
from sphinx.util.docutils import (docutils_namespace, patch_docutils,
                                  sphinx_domains)
from sphinx.util.i18n import CatalogInfo, CatalogRepository, docname_to_domain
# 'CatalogInfo': < class 'sphinx.util.i18n.CatalogInfo' >,
# 'CatalogRepository': < class 'sphinx.util.i18n.CatalogRepository' >,
# this is good to be aware of
# from sphinx.util.inspect import getdoc
from sphinx.util.logging import getLogger
from sphinx.util.osutil import SEP, ensuredir, relative_uri, relpath
# this is used alongside multiprocessing.connection.Connection
# from sphinx.util.parallel import ParallelTasks
from sphinx.util.parallel import (ParallelTasks, SerialTasks, make_chunks,
                                  parallel_available)
from sphinx.util.tags import Tags
from sphinx.util.template import ReSTRenderer

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata


# from sphinx.registry


if TYPE_CHECKING:
    from jinja2.environment import TRIM_BLOCKS, LSTRIP_BLOCKS  # noqa
    from sphinx.domains.rst import ReSTDomain  # noqa
# }}}


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
        # ugh this shouldn't be independent of DocBuilder.kinds
        choices=[cmds],
        # choices=["html", "singlehtml", "text", "linkcheck", "doctest"],
        metavar="builder",
        help="command to run: {}".format(",\t ".join(cmds)),
    )

    parser.add_argument(
        "-s", "--sourcedir", default=Path.cwd(), help="Sourcedir to pass to Sphinx",
    )

    parser.add_argument(
        "-d", "--destdir", default=None, help="Sphinx Build Dir",
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
        metavar="browser",
        type=bool,
        default=False,
        dest="open_browser",
        help="Toggle opening the docs in the default"
        " browser after a successful build. (boolean)",
    )

    parser.add_argument(
        "-l",
        "--log",
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="Where to write log records to. Defaults to stdout.",
    )

    parser.add_argument(
        "-ll",
        "--log-level",
        dest="log_level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level. If logging is specified, defaults to INFO.",
    )
    # reasonably should mention what the purpose of some of these are.
    # they primarily seem like toggles since they don't provide much else
    parser.add_argument(
        "-v",
        "--verbose",
        nargs="?",
        const=True,
        default=False,
        help="Enable verbose logging and increase level to `debug`.",
    )

    dist = metadata.Distribution().from_name("dynamic_ipython")
    __version__ = dist.version
    parser.add_argument("--version", action="version", version=__version__)

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        # This is actually annoying
        # raise argparse.ArgumentError(None, "Args not provided.")
        sys.exit()

    return parser


def parse(app: Sphinx, text: str, docname: str = "index") -> nodes.document:
    """Parse a string as reStructuredText with Sphinx application."""
    try:
        app.env.temp_data["docname"] = docname
        reader = SphinxStandaloneReader()
        reader.setup(app)
        parser = RSTParser()
        parser.set_application(app)
        with sphinx_domains(app.env):
            return publish_doctree(
                text,
                path.join(app.srcdir, docname + ".rst"),
                reader=reader,
                parser=parser,
                settings_overrides={"env": app.env, "gettext_compact": True},
            )
    finally:
        app.env.temp_data.pop("docname", None)


class DocBuilder:
    def __init__(
        self, kind=None, num_jobs=1, verbosity=0, root: Optional[os.PathLike] = None
    ):
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

    def sphinx_build(self, kind, BUILD_PATH: Optional[os.PathLike] = None):
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

    def open_browser(self, doc: Optional[os.PathLike] = None):
        """Open a browser tab to the provided document.

        :param doc: path to index.html
        :type: str
        """
        if doc is None:
            doc = "index.html"
        url = os.path.join("file://", self.root, "build", "html", doc)
        self.status("Opening path to: {!s}".format(url))
        import webbrowser

        webbrowser.open(url, new=2)


class Runner:
    """Initializes a `DocBuilder` and proxies sphinx-build subcommands."""

    def __init__(self, *args, **kwargs):
        """Initialized with the same args as `DocBuilder`."""
        self._builder = DocBuilder(*args, **kwargs)

    @property
    def __builder(self):
        return self._builder

    def __repr__(self):
        return self.__class__.__name__

    def html(self):
        return self.__builder.run("html")

    def man(self):
        return self.__builder.run("man")

    def doctest(self):
        return self.__builder.run("doctest")

    def texinfo(self):
        return self.__builder.run("texinfo")

    def singlehtml(self):
        return self.__builder.run("singlehtml")

    def text(self):
        return self.__builder.run("text")

    def linkcheck(self):
        return self.__builder.run("linkcheck")

    def _run(self, kind):
        """Proxy to `DocBuilder.run`.

        Conventionally, methods beginning with :kbd:`_` are module private.
        This method is not. It's prefixed with a :kbd:`_` to avoid showing
        up in the epilog of the `argparse.ArgumentParser`.

        .. seealso:: `_parse_arguments`

        """
        return self.__builder.run(kind)

    def __call__(self, kind):
        return self.run(kind)


def generate_autosummary(**kwargs):
    from sphinx.ext.autosummary.generate import generate_autosummary_docs

    generate_autosummary_docs(**kwargs)


class UserSphinxAdditions:
    def __init__(self, sphinx: Sphinx):
        self.sphinx = sphinx

    @classmethod
    def additions(self, method, **kwargs):
        if not hasattr(self.sphinx, "method"):
            raise AttributeError

        getattr(self.sphinx, "method")(**kwargs)


def generate_sphinx_app(
    root: os.PathLike, namespace: Optional[argparse.Namespace] = None
):
    """Generate the primary Sphinx application object that drives the project.

    Parameters
    ----------
    root : str or pathlib.Path
        The root of the repositories docs
    namespace : arparse.NameSpace
        User provided arments.

    Returns
    -------
    app : Sphinx
        :class:`sphinx.application.Sphinx` instance.

    """
    srcdir = confdir = Path(root).joinpath("source")
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
        pprint.pprint(exc)
        return 2


def get_jinja_loader(template_path: os.PathLike) -> jinja2.loaders.FileSystemLoader:
    if template_path is None:
        template_path = "_templates"
    elif isinstance(template_path, Path):
        template_path = [template_path.iterdir()]
    try:
        loader = FileSystemLoader(template_path, followlinks=True)
    except TemplateError:
        return
    return loader


def setup_jinja(path_to_template: os.PathLike) -> jinja2.environment.Environment:
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
    def __init__(
        self,
        source_dir: os.PathLike,
        build_dir: os.PathLike,
        builder: List,
        *args: List,
        **kwargs: Dict,
    ):
        super().__init__(source_dir, build_dir, builder, *args)
        self.source_dir = source_dir
        self.build_dir = build_dir

    def run(self, **kwargs):
        super().run(**kwargs)

    def __repr__(self):
        return self.__class__.__name__


def create_sphinx_config(confdir: os.PathLike) -> Config:
    """Create a sphinx.config.Config object which isn't utilized currently.

    Simply here as a thorough method to check for syntax errors.
    """
    tags = Tags()
    try:
        return Config.read(confdir, tags)
    except ConfigError:
        print(*sys.exc_info())


def main(repo_root: os.PathLike, argv=None):
    """Create the required objects to simulate the sphinx make-main command.

    Create a `jinja2.Environment`, a `sphinx.project.Project`,
    `sphinx.jinja2glue.SphinxFileSystemLoader`.

    """
    if argv is None:
        argv = sys.argv[1:]
    user_parser = _parse_arguments()
    user_args = user_parser.parse_args(argv)
    doc_root = Path(repo_root).joinpath("docs")
    conf_path = doc_root.joinpath("source")
    sphinx.locale.setlocale(locale.LC_ALL, "")
    sphinx.locale.init_console(os.path.join(package_dir, "locale"), "sphinx")

    config = create_sphinx_config(conf_path)

    template_path = doc_root.joinpath("source/_templates")
    env = setup_jinja(template_path)

    if user_args.log:
        logger.setLevel(30)
        logger.info(f"git root was: {repo_root}")
        logger.info(f"jinja env: {env}")
    generate_sphinx_app(doc_root, user_args)


def get_git_root() -> Path:
    try:
        almost = codecs.decode(
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"]), "utf-8"
        )
        return Path(almost.rstrip())
    except subprocess.CalledProcessError as e:
        print(e)
        return Path.cwd()


if __name__ == "__main__":
    git_root = get_git_root()
    sys.exit(main(git_root))
