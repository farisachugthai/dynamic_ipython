#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create an installable package for this repository.

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

.. todo:: Why does the .egg_info/ dir get dropped in the cwd?

.. todo::
    When you run `%run setup.py` it raises this error.

    .. code-block:: py3tb

        File "/root/.local/share/virtualenvs/dynamic_ipython-DV6OEPaX/lib/python3.8/site-packages/IPython/core/ultratb.py", line 1151, in get_records
        return _fixed_getinnerframes(etb, number_of_lines_of_context, tb_offset)
        File "/root/.local/share/virtualenvs/dynamic_ipython-DV6OEPaX/lib/python3.8/site-packages/IPython/core/ultratb.py", line 319, in wrapped
        return f(*args, **kwargs)
        File "/root/.local/share/virtualenvs/dynamic_ipython-DV6OEPaX/lib/python3.8/site-packages/IPython/core/ultratb.py", line 353, in _fixed_getinnerframes
        records = fix_frame_records_filenames(inspect.getinnerframes(etb, context))
        File "/usr/lib64/python3.8/inspect.py", line 1503, in getinnerframes
        frameinfo = (tb.tb_frame,) + getframeinfo(tb, context)
        AttributeError: 'tuple' object has no attribute 'tb_frame'
        INFO:root:
        Unfortunately, your original traceback can not be constructed.

        An exception has occurred, use %tb to see the full traceback.
"""
from setuptools.dist import Distribution
from setuptools import setup, find_packages, Command, Extension, PackageFinder
from distutils.errors import DistutilsArgError
import codecs
import logging
import os
from pathlib import Path
from runpy import run_path, run_module
from shutil import rmtree
import sys

logging.basicConfig()


# This is useful
d = Distribution()
if len(sys.argv) == 0:
    d.print_commands()

try:
    d.parse_command_line()
except DistutilsArgError:
    print("No args provided.")


# Obviously there's a ton more we can do here
# try:
#     from setuptools.wheel import (
#         Wheel,
#     )  # this module imports posixpath but that worked on win32 for me???
# except ImportError:
#     Wheel = None

try:
    from pkg_resources import find_distributions
except ImportError:
    pass
else:
    # check this one out
    eggdist = list(find_distributions(os.path.abspath(".")))

try:  # new replacement for the pkg_resources API
    import importlib_metadata
except ImportError:
    importlib_metadata = None
else:
    our_dist = importlib_metadata.distribution("dynamic_ipython")
    # TODO:
    dynamic_entry_point = importlib_metadata.EntryPoint("foo", "bar", "dynamic_ipython")


# Metadata: {{{1

try:
    from default_profile.__about__ import __version__
    from default_profile import ModuleNotFoundError
except ImportError:  # noqa
    __version__ = "0.0.2"

# Conda Support: {{{1

try:
    import distutils.command.bdist_conda
except ImportError:
    distclass = (None,)
else:
    distclass = distutils.command.bdist_conda.CondaDistribution

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
    "IPython>=7.10",
]

EXTRAS = {
    "develop": ["pipenv", "pandas", "matplotlib", ],
    "docs": ["sphinx>=2.2", "matplotlib>=3.0.0", "numpydoc>=0.9", ],
    "test": ["pytest", "testpath", ],
}

# }}}}


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
# Where the magic happens: {{{1

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
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],
    # using this temporarily
    entry_points={
        "console_scripts": ["ip=default_profile.profile_debugger:debug.main"],
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    test_suite="test",
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"],
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
)  # }}}

# Vim: set fdm=marker:
