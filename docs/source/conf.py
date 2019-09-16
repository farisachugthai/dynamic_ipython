#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration file for the Sphinx documentation builder.

This file does only contain a selection of the most common options. For a
full list see the documentation:

http://www.sphinx-doc.org/en/master/config

-- Path setup --------------------------------------------------------------

If extensions (or modules to document with autodoc) are in another directory,
add these directories to sys.path here. If the directory is relative to the
documentation root, use os.path.abspath to make it absolute, like shown here.

"""
# Stdlib imports
from datetime import datetime
from importlib import import_module
from pathlib import Path
from pprint import pprint
import functools
import logging
import math
import os
import sys
import time

# Third party
from sphinx import application
import sphinx
try:
    import ipdb
except ImportError:
    pass

from IPython.lib.lexers import IPyLexer, IPythonTracebackLexer

from traitlets.config import Config

# On to my imports
import default_profile
from default_profile.__about__ import __version__
from default_profile.startup import *

DOCS = Path(__file__).resolve().parent.parent
BUILD_DIR = DOCS.joinpath('build')
CONF_PATH = DOCS.joinpath('source')

sys.path.insert(0, DOCS)

SOURCE = Path(__file__).resolve().parent
ROOT = Path(SOURCE).parent.parent

sys.path.insert(0, ROOT.__fspath__())

default = ROOT.joinpath('default_profile')
sys.path.insert(0, default)

DOCS_LOGGER = logging.getLogger('docs.source').getChild('conf')
DOCS_LOGGER.setLevel(level=logging.DEBUG)
CONF_HANDLER = logging.StreamHandler(stream=sys.stdout)
CONF_HANDLER.setFormatter(logging.Formatter())
CONF_HANDLER.setLevel(logging.DEBUG)
DOCS_LOGGER.addHandler(CONF_HANDLER)

# Let's try setting up an embedded IPython shell from here
# This file needs debugging but I don't know where to correctly enter.
# Regardless don't give me one of the usual shells that'll be too much
c = Config()

c.InteractiveShellApp.exec_lines = [
    'from sphinx.application import Sphinx',
    'import default_profile',
    'import ipdb; ipdb.set_trace(); ipdb.pm()',
    'import numpy; import pandas as pd',
]
c.InteractiveShell.confirm_exit = False
c.TerminalIPythonApp.display_banner = False


def ask_for_import(mod):
    """Try/except for importing modules."""
    try:
        return import_module(mod)
    except (ImportError, ModuleNotFoundError):
        pass


ask_for_import('jinja2')
# app = application.Sphinx(outdir=BUILD_DIR, srcdir=SOURCE, buildername='html', confdir=SOURCE, doctreedir=BUILD_DIR)
# Yeah apparently don't do this

# your_app = application.Sphinx(outdir=BUILD_DIR, srcdir=SOURCE, buildername='html', confdir=SOURCE, doctreedir=BUILD_DIR)
# damn it wasn't even a naming issue. initializing that object jams the
# invocation of ``make html``

# -- Project information -----------------------------------------------------

project = u'Dynamic IPython'
copyright = u'(C) 2018-{} Faris Chugthai'.format(datetime.now().year)
author = u'fac'

# The short X.Y version
version = __version__
# The full version, including alpha/beta/rc tags
release = version

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.

needs_sphinx = '2.1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.githubpages',
    'sphinx.ext.ifconfig',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.linkcode',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive',
]

if ask_for_import('numpydoc'):
    extensions.append('numpydoc.numpydoc')

if ask_for_import('default_profile.sphinxext.magics'):
    magics = ask_for_import('default_profile.sphinxext.magics')
    extensions.append('default_profile.sphinxext.magics')

if ask_for_import('default_profile.sphinxext.configtraits'):
    configtraits = ask_for_import('default_profile.sphinxext.configtraits')
    extensions.append('default_profile.sphinxext.configtraits')

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'
exclude_patterns = ['build', 'dist', '.tox', '.ipynb_checkpoints', 'tags']

default_role = 'py:obj'

today_fmt = '%B %d, %Y'

pygments_style = 'sphinx'

rst_prolog = """
.. |ip| replace:: :class:`IPython.core.interactiveshell.InteractiveShell`
"""

############# Cross your fingers
add_module_names = False
############# Cross your fingers

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'pyramid'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

# This right here is why pyramid wasn't working.
# html_theme_options = {
#     "github_user": "Faris A. Chugthai",
#     "github_repo": "dynamic_ipython",
#     "github_banner": True,
# }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
html_sidebars = {
    '**':
        [
            'searchbox.html',
            'relations.html',
            'globaltoc.html',
            'sourcelink.html',
        ]
}

html_title = u'Dynamic IPython: version' + __version__

html_short_title = u'Dynamic IPython'

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

html_show_copyright = False

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

html_baseurl = u'https://farisachugthai.github.io/dynamic-ipython'

html_compact_lists = False

html_secnumber_suffix = ' '

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
# htmlhelp_basename = 'site-packages-doc'

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
# latex_documents = [
#     (master_doc, 'site-packages.tex', 'site-packages Documentation', 'fac',
#      'manual'),
# ]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'site-packages', 'site-packages Documentation', [author], 1)
]

manpages_url = 'https://linux.die.net/man/'

man_show_urls = True

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
# texinfo_documents = [
#     (master_doc, 'site-packages', 'site-packages Documentation', author,
#      'site-packages', 'One line description of project.', 'Miscellaneous'),
# ]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
# epub_title = project

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

text_newlines = 'native'

text_add_secnumbers = False

text_secnumber_suffix = ''

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'ipython': ('https://ipython.readthedocs.io/en/stable/', None),
    'prompt_toolkit':
        ('https://python-prompt-toolkit.readthedocs.io/en/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference', None),
    'matplotlib': ('https://matplotlib.org', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

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

ipython_savefig_dir = DOCS.joinpath('_images').__fspath__()
ipython_warning_is_error = False

ipython_execlines = [
    'import numpy',
    'import IPython',
    'import matplotlib as mpl',
    'import matplotlib.pyplot',
    'import pandas as pd',
    'import default_profile',
]

if ask_for_import('matplotlib'):
    HAS_MPL = True
    extensions.extend(['matplotlib.sphinxext.plot_directive'])
    ipython_execlines.append(
        'import matplotlib as mpl; import matplotlib.pyplot as plt'
    )
else:
    ipython_mplbackend = 'None'
    HAS_MPL = False

# -- autosummary -------------------------------------------------------------

autodoc_mock_imports = [
    'default_profile',
    'default_profile.util',
    'default_profile.sphinxext',
    'extensions',
]
autosummary_generate = True

autosummary_imported_members = False

autoclass_content = u'both'
autodoc_member_order = u'bysource'

autodoc_docstring_signature = True

if sphinx.version_info < (1, 8):
    autodoc_default_flags = ['members', 'undoc-members']
else:
    autodoc_default_options = {
        'members': True,
        'member-order': 'bysource',
        'special-members': '__init__',
        'exclude-members': '__weakref__',
    }

autodoc_inherit_docstrings = False

# -- autosection label extension ---------------------------------------------

autosectionlabel_prefix_document = True

# -- doctest ----------------------

doctest_global_setup = '''
import IPython
from IPython import get_ipython
_ip = get_ipython()
try:
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except Exception:
    pass
'''

# -- numpydoc extension ------------------------------------------------------

numpydoc_show_class_members = False  # Otherwise Sphinx emits thousands of warnings
numpydoc_class_members_toctree = False

# Whether to create cross-references for the parameter types in the
# Parameters, Other Parameters, Returns and Yields sections of the docstring.
# False by default.
numpydoc_xref_param_type = True

warning_is_error = False

# -- linkcode ----------------------------------------------------------------


def linkcode_resolve(domain, info):
    """Oddly this function is required for the linkcode extension."""
    if domain != 'py':
        return None
    if not info['module']:
        return None

    filename = info['module'].replace('.', '/')
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
np.random.seed(123)
"""
plot_include_source = True
plot_formats = [('png', 96), 'pdf']
plot_html_show_formats = False

phi = (math.sqrt(5) + 1) / 2

font_size = 13 * 72 / 96.0  # 13 px

plot_rcparams = {
    'font.size': font_size,
    'axes.titlesize': font_size,
    'axes.labelsize': font_size,
    'xtick.labelsize': font_size,
    'ytick.labelsize': font_size,
    'legend.fontsize': font_size,
    'figure.figsize': (3 * phi, 3),
    'figure.subplot.bottom': 0.2,
    'figure.subplot.left': 0.2,
    'figure.subplot.right': 0.9,
    'figure.subplot.top': 0.85,
    'figure.subplot.wspace': 0.4,
    'text.usetex': False,
}

# -- Setup -------------------------------------------------------------------


def rstjinja(app, docname, source):
    """
    Render our pages as a jinja template for fancy templating goodness.
    """
    # Make sure we're outputting HTML
    if app.builder.format != 'html':
        return
    src = source[0]
    rendered = app.builder.templates.render_string(
        src, app.config.html_context
    )
    source[0] = rendered


def setup(app):
    """Add pyramid CSS to the docs.

    I thought we had a problem with abspath previous to this? Well regardless
    drop it. Plus we have pathlib all over so simply utilize that.

    """
    app.connect("source-read", rstjinja)
    app.add_lexer('ipythontb', IPythonTracebackLexer())
    app.add_lexer('ipython', IPyLexer())
