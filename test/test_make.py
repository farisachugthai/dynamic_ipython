#!/usr/bin/env python
# -*- coding: utf-8 -*-
from default_profile.sphinxext.make import (
    generate_sphinx_app,
    get_git_root,
    setup_jinja,
)
from default_profile.sphinxext import make
from pathlib import Path

# import jinja2
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
import pytest

# Not a good idea to have the test suite dependant on sphinx being installed
pytest.importorskip("sphinx")


# Globals:

docs_root = Path("../docs")
source = docs_root.joinpath("source")
build = docs_root.joinpath("build")
templates = source.joinpath("_templates")
static = source.joinpath("_templates")


# TODO: do some more comprehensive checks on this crucial instances once we understand them better
def test_get_jinja_loader():
    assert isinstance(make.get_jinja_loader(str(templates)), FileSystemLoader)


def test_setup_jinja():
    assert isinstance(setup_jinja(str(templates)), Environment)


# Does a 'skipIf' not running locally mark exist because this is about to flaky as hell
# awh goddamn. this failed on WSL
def test_get_git_root():
    assert isinstance(get_git_root(), Path)
    assert get_git_root().exists()


# def test_maker():
#     assert make.Maker(source, build, ['html'])
