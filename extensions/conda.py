#!/usr/bin/env python3
"""Ensure that the conda magic works as intended on Windows.

In the IPython source code there's currently a function in the module in
the `packaging <~/src/ipython/IPython/core/magics/packaging.py>`_ package
that asks whether they find the current conda env correctly on Windows.

At a first glance it's actually smarter than the way that I was finding it
with environment variables but let's check.::

    def _is_conda_environment():
        # TODO: does this need to change on windows?
        conda_history = os.path.join(sys.prefix, 'conda-meta', 'history')
        return os.path.exists(conda_history)

"""
