#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install the repo as a python package.

Notes
------

.. envvar:: PIP_VERBOSE

    Who knew that this was a recognized thing? As is PIP_QUIET!


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

import distutils
import setuptools
from distutils.errors import DistutilsArgError, DistutilsError
from setuptools import setup, find_packages, Command
from setuptools.command.easy_install import chmod, current_umask, find_distributions
from setuptools.dist import Distribution
from setuptools.msvc import PlatformInfo, RegistryInfo, SystemInfo, EnvironmentInfo

try:
    import pkg_resources
except ImportError:
    sys.exit('pkg_resources not found but is a hard requirement. Please install with.:'
             '`python3.8 -m pip install -U pkg_resources`.')

logging.basicConfig()
dist = Distribution()

if len(sys.argv) == 1:
    dist.print_commands()


# TODO: i feel like building up the distribution instance could be informative
# dist.include(py_modules=["x"])


def parse_command_line():
    """Process features after parsing command line options"""
    _Distribution = setuptools.monkey.get_unpatched(distutils.core.Distribution)
    _distribution: setuptools.Distribution = _Distribution()
    result = dist.parse_command_line()
    # if dist.features: dist._finalize_features()
    print('\n\n\n****')
    print(result)
    return _distribution


# Btw all that d.parse_command_line is doing is this ^---

try:
    parse_command_line()
except DistutilsArgError:
    print("No args provided.")
except TypeError:  # path was supposed to be path not NoneType
    print("No args.")

try:  # new replacement for the pkg_resources API
    from importlib import metadata as importlib_metadata
except ImportError:
    try:
        import importlib_metadata

        our_dist = importlib_metadata.distribution("dynamic_ipython")
    except ImportError:
        importlib_metadata = None
except importlib_metadata.PackageNotFoundError:
    pass

# DON'T GET RID OF THIS. This took a while to debug and honestly it was an accident.
# Incorrectly installing the package will leave the package partially installed
# leading to software half running and creating deeply confusing tracebacks
try:
    from default_profile.__about__ import __version__
    from default_profile import ModuleNotFoundError
except ImportError:  # noqa
    __version__ = "0.0.2"

# That might be risky
# __path__ = find_packages()

# Conda Support:

try:
    import distutils.command.bdist_conda
except ImportError:
    distclass = (None,)
    bdist_conda = None
else:
    distclass = distutils.command.bdist_conda.CondaDistribution


# }}}

# Wrangling with Setuptools: {{{

def check_installed_modules(requirement):
    try:
        return pkg_resources.get_distribution(requirement)
    except pkg_resources.DistributionNotFoundError as e:
        logging.error(e)


def install(wheel_dirs=None):
    """Install wheels. Thanks Wheel!

    Old `~inspect.Signature` was.:

        def install(requirements, requirements_file=None, wheel_dirs=None,
                    force=False, list_files=False, dry_run=False):

    :param wheel_dirs: A list of directories to search for wheels.
    """
    # If no wheel directories specified, use the WHEELPATH environment
    # variable, or the current directory if that is not set.
    if not wheel_dirs:
        wheelpath = os.getenv("WHEELPATH")
        if wheelpath:
            wheel_dirs = wheelpath.split(os.pathsep)
        else:
            wheel_dirs = [os.path.curdir]

    # Get a list of all valid wheels in wheel_dirs
    all_wheels = []
    for d in wheel_dirs:
        for w in os.listdir(d):
            if w.endswith('.whl'):
                # XXX: is this necessary?
                # from setuptools.wheel import Wheel might work
                wheel = check_installed_modules('wheel')
                if wheel is None:
                    return
                from wheel.wheelfile import WheelFile
                wf = WheelFile(os.path.join(d, w))
                if wf.compatible:
                    all_wheels.append(wf)

    return all_wheels


def find_dist():
    return list(find_distributions(os.path.abspath(".")))


def msft():
    if not platform.platform().startswith('Win'):
        return
    # These actually sequentially require each other. Like why guys.
    pinfo = PlatformInfo('amd64')
    rinfo = RegistryInfo(pinfo)
    sinfo = SystemInfo(rinfo)  # XXX this can raise
    einfo = EnvironmentInfo(sinfo)
    return einfo


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

# Note: I don't think you can put versions in here.
# "jedi>=0.14.0",
# A line like ^---- raised for me
REQUIRED = [
    "IPython",
    "curio",
    "docutils",
    "importlib_metadata",
    "ipykernel",
    "ipyparallel",
    "jedi",
    "jinja2",
    "nbformat",
    "py",
    "pyfzf",
    "pygments",
    "pyperclip",
    "pyzmq",
    "requests",
    "setuptools",
    "traitlets",
    "trio",
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
    "test": ["pytest", "testpath", "nose", "matplotlib"],
}


# }}}

# setuptools.Command: {{{
try:
    from flake8.main.setuptools_command import Flake8
except ImportError:
    Flake8 = None
else:
    # Could reasonably update cmdclass but haven't seen that work yet.
    other_cmdclass = {"flake8": Flake8}

# signature: BuildDoc(dist)
# Docstring:
# Distutils command to build Sphinx documentation.
# The Sphinx build can then be triggered from distutils, and some Sphinx
# options can be set in ``setup.py`` or ``setup.cfg`` instead of Sphinx own
# configuration file.
# For instance, from `setup.py`:
# this is only necessary when not using setuptools/distribute
try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    BuildDoc = None
else:
    other_cmdclass.update({'build_sphinx': BuildDoc})
    # name = 'My project'
    # version = '1.2'
    # release = '1.2.0'
    # setup(
    #         name=name,
    #         author='Bernard Montgomery',
    #         version=release,
    #         cmdclass=cmdclass,
    #         # these are optional and override conf.py settings
    #         command_options={
    #         'build_sphinx': {
    #         'project': ('setup.py', name),
    #         'version': ('setup.py', version),
    #         'release': ('setup.py', release)}},                             )


class UploadCommand(Command):
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

    @property
    def path_metadata(self):
        # At this point i'm kind just blindly flailing about
        egg_info = "dynamic_ipython.egg-info"
        base_dir = os.path.dirname(os.path.abspath(egg_info))
        metadata = pkg_resources.PathMetadata(base_dir, egg_info)
        return metadata

    @property
    def dist(self):
        egg_install_cmd = self.get_finalized_command("egg_info")
        distribution = pkg_resources.Distribution(egg_install_cmd.egg_base,
                                                  self.path_metadata, egg_install_cmd.egg_name,
                                                  egg_install_cmd.egg_version)
        return distribution

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
        # setup()
        self.run_command("egg_info")
        self.status("Uploading the package to PyPI via Twine...")
        os.system("twine upload dist/*")
        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(__version__))
        os.system("git push --tags")
        sys.exit()

    def write_script(self, script_name, contents, mode="t"):
        """Write an executable file to the scripts directory"""
        self.log.info("Installing %s script to %s", script_name, self.install_dir)
        target = os.path.join(self.install_dir, script_name)
        self.outfiles.append(target)

        if not self.dry_run:
            pkg_resources.ensure_directory(target)
            with open(target, "w" + mode) as f:
                f.write(contents)
            chmod(target, 0o777 - current_umask())


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
        # in which i add parameters based on running this script through pdb
        # packages=find_packages(where="default_profile"),
        # no! this HAS to be a dict
        # as oddly ubiquitious as the package=find_packages() thing is though,
        # package_dir is WAY more lenient. it recursively adds EVERYTHING
        # It's kinda set up as an either or tho
        # nvm this didn't work at all
        # package_dir={"default_profile": ""},

        packages=find_packages(where="default_profile"),
        src_root='default_profile',
        tests_require=EXTRAS['test'],
        # py_modules=find_packages(where="default_profile"),
        platforms="any",
        requires=REQUIRED,  # in what way is this different than install_requires?
        entry_points={
            "console_scripts": ["ip=default_profile.profile_debugger:debug.main"],
        },
        # i dont even understand what error this raised but let's leave this
        # commented out
        # setup_requires=["pkg_resources", "pipenv"],

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
        cmdclass={"upload": UploadCommand},
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

except DistutilsError:
    raise

# }}}

# Vim: set fdm=marker fdls=0:
