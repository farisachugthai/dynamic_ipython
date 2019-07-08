"""Start setting up the docs build.

No try/except for the 3rd party imports because IPython and Sphinx are required
packages for building the documentation.

Override the ``__init__()`` method for the
:class:`IPython.sphinxext.ipython_directive.EmbeddedSphinxShell()`.

.. todo:: How do I override the normal IPython shell when building docs

    oh wait would it need to be a sphinx extension?
    Yeah shit it probably will.

"""
import atexit
from io import StringIO
import logging
import os
from pathlib import Path
import sys
import tempfile

from traitlets.config import Config
import IPython
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.profileapp import ProfileDir
from IPython.sphinxext.ipython_directive import EmbeddedSphinxShell
from IPython.utils.tempdir import TemporaryWorkingDirectory
# import sphinx


class EmbeddedDynamicSphinxShell(EmbeddedSphinxShell):
    """Modify the __init__ of the EmbeddedSphinxShell."""

    def __init__(self, exec_lines=None, is_doctest=False, is_suppress=False, is_verbatim=False, *args, **kwargs):
        """Why aren't those variables in the signature?"""

        self.cout = StringIO()

        if exec_lines is None:
            exec_lines = ['import IPython', 'from IPython import get_ipython', 'import profile_default', 'from gruvbox.style import GruvboxStyle']

        # Create config object for IPython
        config = Config()
        config.HistoryManager.hist_file = ':memory:'
        config.InteractiveShell.autocall = False
        config.InteractiveShell.autoindent = False
        config.InteractiveShell.colors = 'NoColor'

        # create a profile so instance history isn't saved
        # with TemporaryWorkingDirectory(prefix='profile_') as tmp_profile_dir:
        #     profname = 'auto_profile_sphinx_build'
        #     pdir = os.path.join(tmp_profile_dir,profname)
        #     profile = ProfileDir.create_profile_dir(pdir)
        # fuck we more than likely can't use the context manager because it needs
        # to be alive across the entire docbuild.

        tmp_profile_dir = tempfile.mkdtemp(prefix='profile_')
        profname = 'dynamic_doc_build'
        profile_dir = Path(tmp_profile_dir + profname)
        profile = ProfileDir.create_profile_dir(profile_dir)

        # Create and initialize global ipython, but don't start its mainloop.
        # This will persist across different EmbeddedSphinxShell instances.
        IP = InteractiveShell.instance(config=config, profile_dir=profile)
        atexit.register(self.cleanup)

        # Store a few parts of IPython we'll need.
        self.IP = IP
        self.user_ns = self.IP.user_ns
        self.user_global_ns = self.IP.user_global_ns

        self.input = ''
        self.output = ''
        self.tmp_profile_dir = tmp_profile_dir

        self.is_verbatim = is_verbatim
        self.is_doctest = is_doctest
        self.is_suppress = is_suppress

        # Optionally, provide more detailed information to shell.
        # this is assigned by the SetUp method of IPythonDirective
        # to point at itself.
        #
        # So, you can access handy things at self.directive.state
        self.directive = None

        # on the first call to the savefig decorator, we'll import
        # pyplot as plt so we can make a call to the plt.gcf().savefig
        self._pyplot_imported = False

        # Prepopulate the namespace.
        for line in exec_lines:
            self.process_input_line(line, store_history=False)


if __name__ == "__main__":
    args = sys.argv[:]
    sphinx_shell = EmbeddedDynamicSphinxShell()