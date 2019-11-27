#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration file for the Sphinx documentation builder.

:date: |today|

This file is execfile()d with the current directory set to its
containing dir.

Note that not all possible configuration values are present in this
autogenerated file.

This file does only contain a selection of the most common options. For a
full list see the documentation:

:URL: http://www.sphinx-doc.org/en/master/config

-- Path setup --------------------------------------------------------------

If extensions (or modules to document with autodoc) are in another directory,
add these directories to sys.path here. If the directory is relative to the
documentation root, use os.path.abspath to make it absolute, like shown here.


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

"""
# Stdlib imports
from datetime import datetime
import functools
from importlib import import_module
import logging
import math
import os
from pathlib import Path
from pprint import pprint
import re
import sys
import time
from typing import Dict

# Third party
import sphinx
from sphinx.ext.autodoc import cut_lines
from sphinx.util.docfields import GroupedField
from sphinx.domains.rst import ReSTDomain
from sphinx.util import logging

from IPython.lib.lexers import IPyLexer, IPythonTracebackLexer
from IPython.sphinxext import ipython_directive
from traitlets.config import Config

# On to my imports
import default_profile
from default_profile.__about__ import __version__
from default_profile import extensions, util
# from default_profile.sphinxext import ipython_directive

from default_profile.startup import *

DOCS = Path(__file__).resolve().parent.parent

# Logging
# DOCS_LOGGER = logging.getLogger('docs.source').getChild('conf')
DOCS_LOGGER = logging.getLogger(name=__name__)


def ask_for_import(mod):
    """Try/except for importing modules."""
    try:
        return import_module(mod)
    except (ImportError, ModuleNotFoundError):
        pass


ask_for_import('jinja2')


# -- Imports ---------------------------------------------------

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
    'IPython.sphinxext.ipython_directive',
    'IPython.sphinxext.ipython_console_highlighting',
    # i fucked up
    # 'default_profile.sphinxext.ipython_directive',
]

if ask_for_import('numpydoc'):
    extensions.append('numpydoc.numpydoc')
    DOCS_LOGGER.info('numpydoc in extensions')

if ask_for_import('default_profile.sphinxext.magics'):
    magics = ask_for_import('default_profile.sphinxext.magics')
    extensions.append('default_profile.sphinxext.magics')
    DOCS_LOGGER.info('magics in extensions')

if ask_for_import('flake8_rst'):
    extensions.extend([
        'flake8_rst.sphinxext.custom_roles',
    ])

# -- General Configuration ----------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:

# source_suffix = ['.rst', '.md']
source_suffix = ['.rst']

# The encoding of source files.
source_encoding = u'utf-8'

# The master toctree document.
master_doc = u'index'

# -- Project information -----------------------------------------------------

project = u'Dynamic IPython'
copyright = u'(C) 2018-{} Faris Chugthai'.format(datetime.now().year)
author = u'fac'

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
today_fmt = u'%B %d, %Y'


# The name of the default domain. Can also be None to disable a default domain.
# The default is 'py'. Those objects in other domains (whether the domain name
# is given explicitly, or selected by a default-domain directive) will have
# the domain name explicitly prepended when named (e.g., when the default
# domain is C, Python functions will be named “Python function”, not just
# “function”).
# New in version 1.0.
default_domain = u'py'

# The name of a reST role (builtin or Sphinx extension) to use as the
# default role, that is, for text marked up `like this`. This can be set to
# 'py:obj' to make `filter` a cross-reference to the Python function “filter”.
# The default is None, which doesn’t reassign the default role.

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    'build', 'Thumbs.db', '.DS_Store', 'dist', '.tox',
    '.ipynb_checkpoints', 'tags', '*.ipynb'
]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# The default role can always be set within individual documents using the
# standard reST default-role directive.
default_role = 'py:obj'

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False


# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# NOTE: lol you have to put a dot at the end otherwise all your modules will start
# with a period
modindex_common_prefix = [
    'default_profile.',
    'default_profile.extensions.',
    'default_profile.startup.',
    'default_profile.util.',
]

# -- General Output Options --------------------------------------------------

# If true, keep warnings as "system message" paragraphs in the built documents.
keep_warnings = False

# Others:

rst_prolog = """
.. |ip| replace:: :class:`~IPython.core.interactiveshell.InteractiveShell`
"""

trim_doctest_flags = True

highlight_language = 'ipython'

warning_is_error = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'pyramid'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.


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
            'localtoc.html',
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

html_js_files = ['copybutton.js']


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'dynamic_ipython'

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
manpages_url = 'https://linux.die.net/man/'

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
    'jupyter': ('https://jupyter.readthedocs.io/en/latest/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
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

ipython_savefig_dir = DOCS.joinpath('_images').__fspath__()
savefig_dir = ipython_savefig_dir

ipython_warning_is_error = False

ipython_execlines = [
    'import numpy',
    'import IPython',
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

# -------------------------------------------------------------------
# Autosummary
# -------------------------------------------------------------------

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
'''

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
import default_profile
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

from sphinx import addnodes  # noqa


def parse_event(sig, signode):
    event_sig_re = re.compile(r'([a-zA-Z-]+)\s*\((.*)\)')
    m = event_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    signode += addnodes.desc_name(name, name)
    plist = addnodes.desc_parameterlist()
    for arg in args.split(','):
        arg = arg.strip()
        plist += addnodes.desc_parameter(arg, arg)
    signode += plist
    return name


def rstjinja(app, docname, source):
    """Render our pages as a jinja template for fancy templating goodness."""
    # Make sure we're outputting HTML
    if app.builder.format != 'html':
        return
    src = source[0]
    rendered = app.builder.templates.render_string(
        src, app.config.html_context
    )
    source[0] = rendered


def del_later(app):
    """Don't know where to move this but it's an interesting way of running
    lambdas over an app to get logging statements."""
    # workaround for RTD
    from sphinx.util import logging
    logger = logging.getLogger(__name__)
    app.info = lambda *args, **kwargs: logger.info(*args, **kwargs)
    app.warn = lambda *args, **kwargs: logger.warning(*args, **kwargs)
    app.debug = lambda *args, **kwargs: logger.debug(*args, **kwargs)


def setup(app):
    """ Add in jinja templates to the site.

    Add IPython lexers from IPython and Sphinx's use of `confval` to the docs.
    Listen for the autodoc-process-docstring event and trim docstring lines.

    Add the :any:`directive` directive for the sphinx extensions themselves.
    This requires adding the ReSTDomain.

    """
    DOCS_LOGGER.info('Initializing the Sphinx instance.')
    app.connect("source-read", rstjinja)
    app.add_lexer('ipythontb', IPythonTracebackLexer)
    app.add_lexer('ipython', IPyLexer)
    app.connect('autodoc-process-docstring', cut_lines(4, what=['module']))
    app.add_object_type('confval', 'confval',
                        objname='configuration value',
                        indextemplate='pair: %s; configuration value')

    # already added and raises an error
    # app.add_domain(ReSTDomain)
    fdesc = GroupedField('parameter', label='Parameters',
                         names=['param'], can_collapse=True)
    app.add_object_type('event', 'event', 'pair: %s; event', parse_event,
                        doc_field_types=[fdesc])

    # app.add_css_file('custom.css')
    # app.add_css_file('pygments.css')
    # There's a html.addjsfile call earlier in the file
    # app.add_js_file('copybutton.js')
    app.add_object_type('directive', 'dir', 'pair: %s; directive')
