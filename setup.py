#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create an installable package for the utilities repository.

Largely based off of the work done by @kennethreitz in his `setup.py`_
repository.

_`Kenneth Reitz setup.py template <https://raw.githubusercontent.com/kennethreitz/setup.py/master/setup.py>`

.. see also::

    numpy.distutils.core
    numpy.distutils.misc_utils


"""
import codecs
import os
from pathlib import Path
import sys
from shutil import rmtree

from setuptools import setup, find_packages, Command

from profile_default import __about__

# Metadata: {{{1
NAME = 'dynamic_ipython'
AUTHOR = "Faris Chugthai"
EMAIL = "farischugthai@gmail.com"
DESCRIPTION = "A gruvbox colorscheme for pygments."
LICENSE = "MIT"
KEYWORDS = ["ipython", "configuration", "pygments"]
URL = "https://github.com/farisachugthai/dynamic_ipython"
REQUIRES_PYTHON = '>=3.6.0'

VERSION = __about__.__version__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONF_PATH = os.path.dirname(os.path.abspath('docs'))
BUILD_PATH = os.path.join(CONF_PATH, 'build')
SOURCE_PATH = os.path.join(CONF_PATH, 'source')

REQUIRED = ['IPython']

EXTRAS = {
    'develop': ['flake8', 'pylint', 'yapf'],
    'docs': [
        'sphinx',
        # Project uses reStructuredText, so ensure that the docutils get
        # installed or upgraded on the target machine
        'docutils>=0.3',
        'numpydoc',
        'flake8-rst',
    ]
}

with codecs.open(os.path.join(ROOT_PATH, "README.rst"), encoding="utf-8") as f:
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
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(
            sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(__about__.__version__))
        os.system('git push --tags')

        sys.exit()


# }}}
# Where the magic happens: {{{1
setup(
    name=NAME,
    version=__about__.__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/restructuredtext',
    python_requires=REQUIRES_PYTHON,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
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
    # setup_requires=['nose>=1.0'],
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
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
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
