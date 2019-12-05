"""So this code keeps raising errors and I don't know why.

Need to debug it and figure out wth is going on.

Helper to preload windows dlls to prevent dll not found errors.
Once a DLL is preloaded, its namespace is made available to any
subsequent DLL. This file originated in the numpy-wheels repo,
and is created as part of the scripts that build the wheel.

.. ipython-traceback::

    In [30]: edit _distributor_init.py
    Editing... done. Executing edited code...
    ---------------------------------------------------------------------------
    OSError
    Traceback (most recent call last)
    ~/projects/dynamic_ipython/.venv/lib/site-packages/numpy/_distributor_init.py in <module>
    24 # NOTE: would it change behavior to load ALL
    25 # DLLs at this path vs. the name restriction?
    ---> 26 WinDLL(os.path.abspath(filename))
    27 DLL_filenames.append(filename)
    28     if len (DLL_filenames) > 1:

    C:/tools/miniconda3/envs/working/Lib/ctypes/__init__.py in __init__(self, name, mode, handle, use_errno, use_last_error, winmode)
    367
    368         if handle is None:
    --> 369             self._hand
    le = _dlopen(self._name, mode)
    370         else:
    371             self._handle = handle

    OSError: [WinError 193] %1 is not a valid Win32 application

What the hell does that mean????


"""
import os
import glob


def main():
    """Alright well let's start by putting this in a contained scope like yeesh."""

    if os.name == 'nt':
        # Moving this import here becase it'll probably crash Linux
        from ctypes import WinDLL
        # convention for storing / loading the DLL from
        # numpy/.libs/, if present
        try:
            basedir = os.path.dirname(__file__)
        except:
            pass
        else:
            libs_dir = os.path.abspath(os.path.join(basedir, '.libs'))
            DLL_filenames = []
            if os.path.isdir(libs_dir):
                for filename in glob.glob(os.path.join(libs_dir,
                                                       '*openblas*dll')):
                    # NOTE: would it change behavior to load ALL
                    # DLLs at this path vs. the name restriction?
                    WinDLL(os.path.abspath(filename))
                    DLL_filenames.append(filename)
        if len(DLL_filenames) > 1:
            import warnings
            warnings.warn("loaded more than 1 DLL from .libs:\n%s" %
                          "\n".join(DLL_filenames),
                          stacklevel=1)


if __name__ == "__main__":
    main()
