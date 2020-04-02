#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# {{{
import asyncio
import cgitb
import logging
import math
import os
import re
import sys
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from IPython.lib.lexers import IPyLexer, IPython3Lexer, IPythonTracebackLexer

import jinja2
from jinja2.bccache import FileSystemBytecodeCache
from jinja2.environment import Environment
from jinja2.exceptions import TemplateError
from jinja2.ext import autoescape, do, with_, debug
from jinja2.loaders import ChoiceLoader, ModuleLoader, FileSystemLoader
from jinja2.lexer import get_lexer

from pygments.lexers.markup import MarkdownLexer, RstLexer
from pygments.lexers.shell import BashLexer
from pygments.lexers.textedit import VimLexer
from pygments.lexers.python import (
    NumPyLexer,
    PythonConsoleLexer,
    PythonLexer,
    PythonTracebackLexer,
)
import sphinx

from sphinx import addnodes

# from sphinx.application import Sphinx
# and i think SphinxError is actually one too
# from sphinx.environment import BuildEnvironment
# could manually start creating extensions
# from sphinx.errors import SphinxError, ExtensionError
# from sphinx.extension import Extension
from sphinx.ext.autodoc import cut_lines
from sphinx.jinja2glue import SphinxFileSystemLoader, BuiltinTemplateLoader
from sphinx.util.logging import getLogger
from sphinx.util.docfields import GroupedField
from sphinx.util.tags import Tags
from sphinx.util.template import ReSTRenderer

if TYPE_CHECKING:
    from jinja2.environment import TRIM_BLOCKS, LSTRIP_BLOCKS  # noqa
    from sphinx.application import Sphinx  # noqa
    from sphinx.domains.rst import ReSTDomain  # noqa
# }}}

import default_profile  # noqa

# from default_profile import ask_for_import
from default_profile.sphinxext.magics import CellMagicRole, LineMagicRole  # noqa

try:
    from default_profile.__about__ import __version__
except ImportError:
    import importlib_metadata

    dist = importlib_metadata.Distribution().from_name("dynamic_ipython")

# Logging: {{{

DOCS_LOGGER = logging.getLogger(name=__name__)
DOCS_HANDLER = logging.StreamHandler()
DOCS_HANDLER.setLevel(logging.INFO)
DOCS_LOGGER.handlers = []
DOCS_LOGGER.addHandler(DOCS_HANDLER)
DOCS_FILTER = logging.Filter(name=__name__)
DOCS_LOGGER.setLevel(logging.INFO)
DOCS_LOGGER.addFilter(DOCS_FILTER)

# Gotta hack at sys.path a little
DOCS = Path(__file__).resolve().parent.parent
BUILD_DIR = DOCS.joinpath("build/html")
ROOT = DOCS.parent
JUPYTER = ROOT.joinpath("jupyter_conf")

sys.path.insert(0, str(JUPYTER))
# I'll admit i don't know why i need this one
STARTUP = ROOT.joinpath("default_profile/startup")

sys.path.insert(0, str(STARTUP))

UTIL = ROOT.joinpath("default_profile/util")

sys.path.insert(0, str(UTIL))

# Add markdown to the lexer's aliases
MarkdownLexer.aliases = ["md", "markdown"]

DOCS_LOGGER = logging.getLogger(__name__)

cgitb.enable(format="text")
# -- Jinja2 ---------------------------------------------------

loop = asyncio.new_event_loop()
jinja_templates = FileSystemBytecodeCache(
    os.environ.get("TMP") + "jinja_cache", "%s.cache"
)
sphinx_root = os.path.dirname(sphinx.__file__)
sphinx_templates = os.path.join(sphinx_root, "templates", "basic")


def instantiate_jinja_loader():
    template_path = "_templates"
    try:
        loader = ChoiceLoader(
            [
                SphinxFileSystemLoader(sphinx_templates),
                SphinxFileSystemLoader(template_path),
                FileSystemLoader(template_path),
            ]
        )
    except TemplateError:
        return
    else:
        return loader


jinja_loader = instantiate_jinja_loader()


def create_jinja_env():
    """Use jinja to set up the Sphinx environment."""
    TRIM_BLOCKS = True
    LSTRIP_BLOCKS = True
    template_path = "_templates"
    env = Environment(
        trim_blocks=TRIM_BLOCKS,
        lstrip_blocks=LSTRIP_BLOCKS,
        autoescape=jinja2.select_autoescape(
            disabled_extensions=("txt",), default_for_string=True, default=True
        ),
        extensions=[
            "jinja2.ext.i18n",
            autoescape,
            do,
            with_,
            debug,
            "jinja2.ext.loopcontrols",
            "jinja2.ext.do",
        ],
        enable_async=True,
        bytecode_cache=jinja_templates,
        loader=jinja_loader,
    )
    return env


try:
    lexer = get_lexer(create_jinja_env())
except (TemplateError, TemplateSyntaxError):
    pass

# with open(os.path.join(DOCS, "source", "index.rst")) as f:
#     t = jinja2.Template(f.read())
# with open(os.path.join(DOCS, "source", "index.rst.ignore"), "w") as f:
#     f.write(t.render())


@jinja2.contextfunction
def get_exported_names(context):
    """View the exported vars from the jinja2 context."""
    return sorted(context.exported_vars)


# -- Extensions ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.

needs_sphinx = "2.1.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.config",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.coverage",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    "sphinx.ext.extlinks",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "IPython.sphinxext.ipython_directive",
    "default_profile.sphinxext.magics",
    "matplotlib.sphinxext.plot_directive",
    "matplotlib.sphinxext.mathmpl",
    "flake8_rst.sphinxext.custom_roles",
    "numpydoc.numpydoc",
    "recommonmark",
]

# -- General Configuration ----------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

renderers = ReSTRenderer(templates_path)

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "restructuredtext",
    ".md": "markdown",
}

# The encoding of source files.
source_encoding = u"utf-8"

# The master toctree document.
master_doc = u"index"

# -- Project information -----------------------------------------------------

project = u"Dynamic IPython"
copyright = u"(C) 2018-{} Faris Chugthai".format(datetime.now().year)
author = u"fac"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

# The short X.Y version
version = __version__
# The full version, including alpha/beta/rc tags
release = version
# primary_domain

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
# language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = u"%B %d, %Y"

# The name of the default domain. Can also be None to disable a default domain.
# The default is 'py'. Those objects in other domains (whether the domain name
# is given explicitly, or selected by a default-domain directive) will have
# the domain name explicitly prepended when named (e.g., when the default
# domain is C, Python functions will be named “Python function”, not just
# “function”).
# New in version 1.0.
default_domain = u"py"

# The name of a reST role (builtin or Sphinx extension) to use as the
# default role, that is, for text marked up `like this`. This can be set to
# 'py:obj' to make `filter` a cross-reference to the Python function “filter”.
# The default is None, which doesn’t reassign the default role.

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "build",
    "Thumbs.db",
    ".DS_Store",
    "dist",
    ".tox",
    ".ipynb_checkpoints",
    "tags",
    "*.ipynb",
]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# The default role can always be set within individual documents using the
# standard reST default-role directive.
default_role = "py:obj"

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

# A list of ignored prefixes for module index sorting.
# NOTE: lol you have to put a dot at the end otherwise all your modules will start
# with a period
# modindex_common_prefix = [
#     "default_profile.",
#     "default_profile.extensions.",
#     "default_profile.startup.",
#     "default_profile.util.",
# ]

# -- General Output Options --------------------------------------------------

# If true, keep warnings as "system message" paragraphs in the built documents.
keep_warnings = False

# Others:

rst_prolog = """
.. |ip| replace:: :class:`~IPython.core.interactiveshell.InteractiveShell`
"""

trim_doctest_flags = True

highlight_language = "python"

warning_is_error = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

# html_theme = "pyramid"
html_theme = "scrolls"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
html_sidebars = {
    "**": [
        "searchbox.html",
        "relations.html",
        "localtoc.html",
        "globaltoc.html",
        "sourcelink.html",
    ]
}

html_title = u"Dynamic IPython"

html_short_title = u"Dynamic IPython"

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

html_show_copyright = False

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

html_baseurl = u"https://farisachugthai.github.io/dynamic-ipython"

html_compact_lists = False

html_secnumber_suffix = " "

# html_js_files = ["copybutton.js"]

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "dynamic_ipython"

# -- Options for LaTeX output ------------------------------------------------

# latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#
# 'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#
# 'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#
# 'preamble': '',

# Latex figure (float) alignment
#
# 'figure_align': 'htbp',
# }

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
manpages_url = "https://linux.die.net/man/"

man_show_urls = True

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)

# -- Options for Epub output ----------------------------------------

# Bibliographic Dublin Core info.

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
# epub_exclude_files = ['search.html']

# -- Options for text output -------------------------------------------------

text_newlines = "native"

text_add_secnumbers = False

text_secnumber_suffix = ""

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Double the original cache limit
intersphinx_cache_limit = 10

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "ipython": ("https://ipython.readthedocs.io/en/stable/", None),
    "prompt_toolkit": ("https://python-prompt-toolkit.readthedocs.io/en/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "matplotlib": ("https://matplotlib.org", None),
    "jupyter": ("https://jupyter.readthedocs.io/en/latest/", None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Viewcode ----------------------------------------------------------------
"""Viewcode:

Apr 28, 2019: RemovedInSphinx30Warning:
``viewcode_import`` was renamed to ``viewcode_follow_imported_members``.
Please update your configuration.


viewcode-find-source(app, modname)

    New in version 1.8.

    Find the source code for a module. An event handler for this event
    should return a tuple of the source code itself and a dictionary of
    tags. The dictionary maps the name of a class, function, attribute, etc.
    to a tuple of its type, the start line number, and the end line number.
    The type should be one of “class”, “def”, or “other”.

    Parameters
        app – The Sphinx application object.
        modname – The name of the module to find source code for.

viewcode-follow-imported(app, modname, attribute)

    New in version 1.8.
    Find the name of the original module for an attribute.

    Parameters
        app – The Sphinx application object.
        modname – The name of the module that the attribute belongs to.
        attribute – The name of the member to follow.

"""

viewcode_follow_imported_members = False

# -- IPython directive -------------------------------------------------------

ipython_savefig_dir = BUILD_DIR.joinpath("_images").__fspath__()
savefig_dir = ipython_savefig_dir

ipython_warning_is_error = False

ipython_execlines = [
    "import numpy",
    "import IPython",
    "import default_profile",
    "import matplotlib as mpl",
    "import matplotlib.pyplot",
]

# -------------------------------------------------------------------
# Autosummary
# -------------------------------------------------------------------

autosummary_generate = True

autosummary_imported_members = False

# autoclass_content = u'both'
autodoc_member_order = u"bysource"

autodoc_docstring_signature = True

if sphinx.version_info < (1, 8):
    autodoc_default_flags = ["members", "undoc-members"]
else:
    autodoc_default_options = {
        "members": True,
        "member-order": "bysource",
        "undoc-members": True,
        "special-members": "__init__",
    }

autodoc_inherit_docstrings = False

# -- autosection label extension ---------------------------------------------

autosectionlabel_prefix_document = True

# -- doctest ----------------------

doctest_global_setup = """
import default_profile
import IPython
from IPython import get_ipython
_ip = get_ipython()
try:
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except Exception:
    pass
"""

# -- numpydoc extension ------------------------------------------------------

# Otherwise Sphinx emits thousands of warnings
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False

# Whether to create cross-references for the parameter types in the
# Parameters, Other Parameters, Returns and Yields sections of the docstring.
# False by default.
numpydoc_xref_param_type = True

# -- linkcode ----------------------------------------------------------------


def linkcode_resolve(domain, info):
    """Oddly this function is required for the linkcode extension."""
    if domain != "py":
        return None
    if not info["module"]:
        return None

    filename = info["module"].replace(".", "/")
    return "https://github.com/farisachugthai/dynamic_ipython/%s.py" % filename


# Plot style
# ------------------------------------------------------------------------------

# Nabbed from scipy:
# https://github.com/scipy/scipy-sphinx-theme/blob/master/conf.py

plot_pre_code = """
import numpy as np
# import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import default_profile
np.random.seed(123)
"""
plot_include_source = True
plot_formats = [("png", 96), "pdf"]
plot_html_show_formats = False
# Not sure if this is a good idea because it usually works in source or one of
# the dirs in source
# plot_basedir = docs_root
# plot_working_directory = docs_root
plot_apply_rcparams = True

phi = (math.sqrt(5) + 1) / 2

font_size = 13 * 72 / 96.0  # 13 px

plot_rcparams = {
    "font.size": font_size,
    "axes.titlesize": font_size,
    "axes.labelsize": font_size,
    "xtick.labelsize": font_size,
    "ytick.labelsize": font_size,
    "legend.fontsize": font_size,
    "figure.figsize": (3 * phi, 3),
    "figure.subplot.bottom": 0.2,
    "figure.subplot.left": 0.2,
    "figure.subplot.right": 0.9,
    "figure.subplot.top": 0.85,
    "figure.subplot.wspace": 0.4,
    "text.usetex": False,
}

# Not from scpy but mpl related anyway
plot_html_show_source_link = True

# -- Setup -------------------------------------------------------------------


def parse_event(sig, signode):
    """Add 'event' event to Sphinx."""
    event_sig_re = re.compile(r"([a-zA-Z-]+)\s*\((.*)\)")
    m = event_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    signode += addnodes.desc_name(name, name)
    plist = addnodes.desc_parameterlist()
    for arg in args.split(","):
        arg = arg.strip()
        plist += addnodes.desc_parameter(arg, arg)
    signode += plist
    return name


def rstjinja(app, docname, source):
    """Render our pages as a jinja template for fancy templating goodness."""
    # Make sure we're outputting HTML
    if app.builder.format != "html":
        return
    src = source[0]
    rendered = app.builder.templates.render_string(src, app.config.html_context)
    source[0] = rendered


def setup(app):
    """Add in jinja templates to the site.

    Add IPython lexers from IPython and Sphinx's use of `confval` to the docs.
    Listen for the autodoc-process-docstring event and trim docstring lines.

    Add the :any:`directive` directive for the sphinx extensions themselves.
    This requires adding the ReSTDomain.

    """
    DOCS_LOGGER.info("Initializing the Sphinx instance.")

    cgitb.enable(format="text")
    app.connect("source-read", rstjinja)
    app.add_lexer("ipython", IPyLexer)
    app.add_lexer("py3tb", PythonTracebackLexer)
    app.add_lexer("python3", PythonLexer)
    app.add_lexer("python", PythonLexer)
    app.add_lexer("pycon", PythonConsoleLexer)
    app.add_lexer("markdown", MarkdownLexer)
    app.add_lexer("rst", RstLexer)
    app.add_lexer("vim", VimLexer)
    app.add_lexer("numpy", NumPyLexer)
    app.connect("autodoc-process-docstring", cut_lines(4, what=["module"]))
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )

    # already added and raises an error
    # app.add_domain(ReSTDomain)
    fdesc = GroupedField(
        "parameter", label="Parameters", names=["param"], can_collapse=True
    )
    app.add_object_type(
        "event", "event", "pair: %s; event", parse_event, doc_field_types=[fdesc]
    )

    # app.add_css_file("custom.css")
    # already was added in a template
    # app.add_css_file('pygments.css')
    # There's a html.addjsfile call earlier in the file
    # app.add_js_file("copybutton.js")
    app.add_object_type("directive", "dir", "pair: %s; directive")
    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
