"""Directives and roles for documenting traitlets config options.

============
Configtraits
============

.. :rst:directive::

    .. configtrait:: Application.log_datefmt

        Description goes here.

    Cross reference like this: :configtrait:`Application.log_datefmt`.

There's an example use.
"""


def setup(app):
    app.add_object_type('configtrait', 'configtrait', objname='Config option')
    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True}
    return metadata
