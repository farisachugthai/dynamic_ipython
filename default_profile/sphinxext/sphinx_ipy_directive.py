#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING
from docutils import nodes
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.images import Image

from sphinx.errors import ExtensionError, SphinxError
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import nested_parse_with_titles  # useful to remember this exists

import IPython

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class HelloWorld(Directive):
    def run(self):
        paragraph_node = node.paragraph(text="Hello World")
        return [paragraph_node]


class IPythonDirectiveError(SphinxError):
    category = "Uh?"


def python_validator(self):
    pass


def doctest_validator(self):
    pass


def verbatim_validator(self):
    pass


class IPDirective(SphinxDirective):

    has_content = True
    required_arguments = 1
    optional_arguments = 3
    final_argument_whitespace = False
    option_spec = {  # todo
        "python": python_validator,
        "doctest": doctest_validator,
        "verbatim": verbatim_validator,
    }

    def run(self):
        # TODO
        raise NotImplementedError


# Sphinx.add_directive(IPDirective)
# aka


def setup(app):
    app.add_directive(IPDirective)
