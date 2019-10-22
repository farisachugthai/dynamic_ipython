#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create an installable package for this repository.

Setuptools + Setup
==================

The file in which we make this project:

#) Installable from pypi
#) An official python package
#) Able to import modules from one folder above itself....

``bdist_conda``
----------------

Now let's add support for ``python setup.py bdist_conda``.

Ran that command with a :kbd:`-h` flag and got these 2 relevant options.

  --buildnum          The build number of the conda package. Defaults to
                      0, or the ``conda_buildnum`` specified in the `setup`
                      function. The command line flag overrides the option to
                      `setup`.
  --anaconda-upload   Upload the finished package to anaconda.org



See Also
--------
.. seealso::

    numpy.distutils.core
    numpy.distutils.misc_utils

`Conda builds with a recipe
<https://docs.conda.io/projects/conda-build/en/latest/user-guide/recipes/build-without-recipe.html>`_

Here's a really good one to check out.:

>>> from conda.cli.main_package import make_tarbz2
>>> import pydoc
>>> pydoc.ttypager(make_tarbz2.__doc__)


"""
import codecs
import logging
import os
from pathlib import Path
from runpy import run_path, run_module
from shutil import rmtree
# Why does Coc keep complaining about resolving the import sys???
import sys

from setuptools import setup, find_packages, Command, Extension

# how are we allowed to do this you can't force a dependency before installation
# from default_profile import __about__.__version__
# Conda Support: {{{1

try:
    import distutils.command.bdist_conda
except (ImportError, ModuleNotFoundError):
    distclass = None,
else:
    distclass = distutils.command.bdist_conda.CondaDistribution

# Metadata: {{{1
from default_profile.__about__ import __version__
NAME = 'dynamic_ipython'
AUTHOR = "Faris Chugthai"
EMAIL = "farischugthai@gmail.com"
DESCRIPTION = "An IPython configuration system."
LICENSE = "MIT"
KEYWORDS = [
    "ipython", "configuration", "ipython_extensions", "jupyter", "frameworks"
]
URL = "https://github.com/farisachugthai/dynamic_ipython"
REQUIRES_PYTHON = '>=3.6.0'

VERSION = __version__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONF_PATH = os.path.dirname(os.path.abspath('docs'))
BUILD_PATH = os.path.join(CONF_PATH, 'build')
SOURCE_PATH = os.path.join(CONF_PATH, 'source')

README = os.path.join(ROOT_PATH, '', 'README.rst')
REQUIRED = [
    'IPython>=7.7', 'prompt_toolkit', 'numpy', 'pandas', 'jinja2', 'traitlets',
    'pygments', 'matplotlib'
]

EXTRAS = {
    'develop': ['pipenv', 'flake8>=3.7.1', 'pylint', 'yapf>=0.27.0'],
    'docs': [
        'sphinx>=2.2',
        # Project uses reStructuredText, so ensure that the docutils get
        # installed or upgraded on the target machine
        'docutils>=0.3',
        'numpydoc>=0.9',
        'flake8-rst',
    ],
    'test': ['pytest', 'tox', 'nose']
}

with codecs.open(README, encoding="utf-8") as f:
    LONG_DESCRIPTION = "\n" + f.read()
# }}}}


class UploadCommand(Command):  # {{{1
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []
    root = Path(__file__).parent

    @staticmethod
    def status(output):
        """Print output in bold."""
        print('\033[1m{0}\033[0m'.format(output))

    def initialize_options(self):
        """Initialize upload options."""
        pass

    def finalize_options(self):
        """Finalize upload options."""
        pass

    def run(self):
        """Upload package."""
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(str(self.root), 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')

        # I really dislike the idea of forking a new process from python to make
        # a new python process....will this work the same way with exec(compile)?
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(
            sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(__version__))
        os.system('git push --tags')

        sys.exit()


# }}}
# Where the magic happens: {{{1

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/restructuredtext',
    python_requires=REQUIRES_PYTHON,
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    url=URL,
    packages=find_packages(where='.'),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    test_suite='test',
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },
    license=LICENSE,

    # https://www.python.org/dev/peps/pep-0345/#platform-multiple-use
    # A Platform specification describing an operating system supported by the
    # distribution which is not listed in the "Operating System" Trove
    # classifiers. See "Classifier" below.#
    # Platform='Linux',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Environment :: Console',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Android',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'OperatingSystem ::POSIX:: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
    # project home page, if any
    project_urls={
        "Bug Tracker":
        "https://www.github.com/farisachugthai/dynamic_ipython/issues",
        "Documentation": "https://farisachugthai.github.io/dynamic_ipython",
        "Source Code": "https://www.github.com/farisachugthai/dynamic_ipython",
    }
    # could also include long_description, download_url, classifiers, etc.
)

# Vim: set fdm=marker:
