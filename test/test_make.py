#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

import jinja2
import pytest

# Not a good idea to have the test suite dependant on sphinx being installed
pytest.importorskip("sphinx")

from default_profile.sphinxext import make
from default_profile.sphinxext.make import generate_sphinx_app, get_git_root, setup_jinja

# Globals:

docs_root = Path('../docs')
source = docs_root.joinpath('source')
build = docs_root.joinpath('build')
templates = source.joinpath('_templates')
static = source.joinpath('_templates')


def test_setup_jinja():
    assert isinstance(setup_jinja(templates), jinja2.environment.Environment)

# Does a 'skipIf' not running locally mark exist because this is about to flaky as hell
# awh goddamn. this failed on WSL
def test_get_git_root():
    assert isinstance(get_git_root(), Path)
    assert get_git_root().exists()


# def test_generate_sphinx_app():
#     assert False
