from pathlib import Path

import pytest
from default_profile.sphinxext.make import generate_sphinx_app, get_git_root


# Does a 'skipIf' not running locally mark exist because this is about to flaky as hell
def test_get_git_root():
    """Check that the git root given is the git root I hardcode."""
    assert get_git_root() == Path('~/projects/dynamic_ipython').expanduser()


def test_generate_sphinx_app():
    assert False
