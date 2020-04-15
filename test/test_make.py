#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

# Not a good idea to have the test suite dependant on sphinx being installed
pytest.importorskip("sphinx")

from default_profile.sphinxext.make import generate_sphinx_app, get_git_root


# Does a 'skipIf' not running locally mark exist because this is about to flaky as hell
# awh goddamn. this failed on WSL
def test_get_git_root():
    assert isinstance(get_git_root(), Path)
    assert get_git_root().exists()


# def test_generate_sphinx_app():
#     assert False
