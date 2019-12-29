import shutil

from IPython.core.getipython import get_ipython
from IPython.core.magic import Magics, line_magic, magics_class

from .packaging import _is_conda_environment


def conda():
    """Simpler re-implemented line magic."""
    conda = shutil.which("conda")
    if conda.endswith("bat"):
        conda = "call " + conda
    # %sx conda
