#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install the repo as a python package.

.. tip::
    Always have a fallback for determining version.
    If using an import from your repo doesn't work, then depending on that
    will give a `None` for version to setuptools.setup().

    Libraries like importlib_metadata exist for this purpose.

"""

# Imports: {{{
import codecs
import logging
import os
import sys
import platform
from pathlib import Path
from shutil import rmtree

import distutils  # noqa
import setuptools  # noqa
from setuptools.dist import Distribution
from setuptools import setup, find_packages, Command
from distutils.errors import DistutilsArgError

logging.basicConfig()

# This is useful
d = Distribution()

# Obviously there's a ton more we can do here
# try:
#     from setuptools.wheel import (
#         Wheel,
#     )  # this module imports posixpath but that worked on win32 for me???
# except ImportError:
#     Wheel = None

if len(sys.argv) == 0:
    d.print_commands()

try:
    d.parse_command_line()
except DistutilsArgError:
    print("No args provided.")
except TypeError:  # path was supposed to be path not NoneType
    print("No args.")

try:
    from pkg_resources import find_distributions
except ImportError:
    pass
else:
    # check this one out
    listdist = list(find_distributions(os.path.abspath(".")))
    try:
        dist = listdist[0]
    except IndexError:
        pass

try:  # new replacement for the pkg_resources API
    import importlib_metadata

    our_dist = importlib_metadata.distribution("dynamic_ipython")
except ImportError:
    importlib_metadata = None
except importlib_metadata.PackageNotFoundError:
    pass

# }}}

# Metadata: {{{

# DON'T GET RID OF THIS. This took a while to debug and honestly it was an accident.
# Incorrectly installing the package will leave the package partially installed
# leading to software half running and creating deeply confusing tracebacks
try:
    from default_profile.__about__ import __version__
    from default_profile import ModuleNotFoundError
except ImportError:  # noqa
    __version__ = "0.0.2"

__path__ = find_packages()

# }}}

# Conda Support: {{{

try:
    import distutils.command.bdist_conda
except ImportError:
    distclass = (None,)
    bdist_conda = None
else:
    distclass = distutils.command.bdist_conda.CondaDistribution

# }}}

# Metadata: {{{
NAME = "dynamic_ipython"
AUTHOR = "Faris Chugthai"
EMAIL = "farischugthai@gmail.com"
DESCRIPTION = "An IPython configuration system."
LICENSE = "MIT"
KEYWORDS = ["ipython", "configuration", "ipython_extensions", "jupyter", "frameworks"]
URL = "https://github.com/farisachugthai/dynamic_ipython"
REQUIRES_PYTHON = ">=3.6.0"

VERSION = __version__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
CONF_PATH = os.path.dirname(os.path.abspath("docs"))
BUILD_PATH = os.path.join(CONF_PATH, "build")
SOURCE_PATH = os.path.join(CONF_PATH, "source")

README = os.path.join(ROOT_PATH, "", "README.rst")

with codecs.open(README, encoding="utf-8") as f:
    LONG_DESCRIPTION = "\n" + f.read()


# TODO: How to do conditionals? Only windows needs pyreadline
REQUIRED = [
    "IPython>=7.12",
    "ipykernel",
    "curio",
    "importlib-metadata",
    "pyfzf",
    "pyperclip",
    "trio",
    "pygments",
    # 'pyreadline',
    "jinja2",
    "jedi",
    "pyzmq",
    "traitlets", 'requests', 'docutils', 'py'
]

if platform.platform().startswith("Win"):
    REQUIRED.append("pyreadline")
    REQUIRED.append("colorama")


EXTRAS = {
    "develop": ["pipenv", "pandas", "matplotlib", ],
    "docs": [
        "sphinx>=2.2",
        "matplotlib>=3.0.0",
        "numpydoc>=0.9",
        "flake8-rst",
        "recommonmark",
    ],
    "test": ["ipyparallel", "pytest", "testpath", "nose", "matplotlib"],
}

# }}}


class UploadCommand(Command):  # {{{
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []
    root = Path(__file__).parent

    @staticmethod
    def status(output):
        """Print output in bold."""
        print("\033[1m{0}\033[0m".format(output))

    def initialize_options(self):
        """Initialize upload options."""
        pass

    def finalize_options(self):
        """Finalize upload options."""
        pass

    def run(self):
        """Upload package."""
        try:
            self.status("Removing previous builds...")
            rmtree(os.path.join(str(self.root), "dist"))
        except OSError:
            logging.warning("Could not remove previous builds")

        self.status("Building Source and Wheel (universal) distribution...")
        # I really dislike the idea of forking a new process from python to make
        # a new python process....will this work the same way with exec(compile)?
        # os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))
        setup()
        self.status("Uploading the package to PyPI via Twine...")
        os.system("twine upload dist/*")
        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(__version__))
        os.system("git push --tags")
        sys.exit()


# }}}

# Where the magic happens: {{{
try:
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/restructuredtext",
        python_requires=REQUIRES_PYTHON,
        author=AUTHOR,
        author_email=EMAIL,
        maintainer=AUTHOR,
        maintainer_email=EMAIL,
        url=URL,
        packages=find_packages(where="."),
        entry_points={
            "console_scripts": ["ip=default_profile.profile_debugger:debug.main"],
        },
        # namespace_packages=["default_profile", "default_profile.sphinxext"],
        install_requires=REQUIRED,
        extras_require=EXTRAS,
        test_suite="test",
        include_package_data=True,
        package_data={
            # If any package contains *.txt or *.rst files, include them:
            "": ["*.txt", "*.rst"],
        },
        license=LICENSE,
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            "Environment :: Console",
            "Framework :: IPython",
            "Framework :: Jupyter",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: Android",
            "Operating System :: Microsoft :: Windows :: Windows 10",
            "Operating System :: POSIX:: Linux",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: Implementation :: CPython",
        ],
        # $ setup.py publish support.
        cmdclass={"upload": UploadCommand, },
        # project home page, if any
        project_urls={
            "Bug Tracker": "https://www.github.com/farisachugthai/dynamic_ipython/issues",
            "Documentation": "https://farisachugthai.github.io/dynamic_ipython",
            "Source Code": "https://www.github.com/farisachugthai/dynamic_ipython",
        }
        # could also include long_description, download_url, classifiers, etc.
    )
except DistutilsArgError:
    d.print_commands()

# }}}

# Vim: set fdm=marker fdls=0:
