import os
from pathlib import Path

from IPython.core.magic import line_magic


@line_magic
def touch(f):
    if f.endswith('py'):
        return Path(f).touch(mode=0o755)
    else:
        return Path(f).touch()
        
    
@line_magic
def unset(arg):
    return os.environ.unsetenv(arg)
