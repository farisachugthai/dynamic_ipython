#!
"""Initialize the whole repository.

Now we're getting into the weird parts of how Python distributes things
and I'm beginning to question whether I need to make a setuptools.Distribution
or a namespace package or any of the 1000 ways you can do this.

Running the below in the ``git rev-parse --show-prefix == .`` showed some
good signs though::

>>> for i in pkg_resources.find_distributions('.'):
...     print(i)
...
dynamic-ipython 0.0.1


"""
import logging
import sys
from os.path import abspath, dirname, join
from pkg_resources import declare_namespace
from setuptools import find_packages, find_namespace_packages

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

REPO_ROOT = dirname(abspath(__file__))

declare_namespace(REPO_ROOT)

found_packages = find_packages(where='.')
found_namespace_packages = find_namespace_packages(where='.')

logging.debug('Found packages were: {}'.format(found_packages))
logging.debug('Found namespace packages were: {}'.format(found_namespace_packages))

logging.debug('Sys.path before:' + str(sys.path))
sys.path = sys.path + [REPO_ROOT]
logging.debug('Sys path after:' + str(sys.path))
