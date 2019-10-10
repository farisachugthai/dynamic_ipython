#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============
repr_requests
=============

.. magic:: _repr_request


Utilize the :meth:`IPython.core.interactiveshell.InteractiveShell._repr_pretty`
method to generate a :func:`IPython.display.display`
for a requests.models.Response objects.

"""
import sys

from IPython import get_ipython


def repr_request(r, p, cycle):
    """Generate a :func:`repr` for requests.models.Response objects."""
    p.text('{} {}\n'.format(r.status_code, r.url))
    p.text('headers: ')
    for name in sorted(r.headers):
        p.text('  {}: {}\n'.format(name, r.headers[name]))
    p.text('\nbody ({}):\n'.format(r.headers.get('content-type', 'unknown')))
    try:
        p.pretty(r.json())
    except ValueError:
        try:
            if len(r.text) > 1024:
                p.text(r.text[:1024])
                p.text('...[%i bytes]' % len(r.content))
            else:
                p.text(r.text)
        except Exception:
            if len(r.content) > 1024:
                p.pretty(r.content[:1024])
                p.text('...[%i bytes]' % len(r.content))
            else:
                p.pretty(r.content)


def load_ipython_extension(ip):
    """Load the pretty printed Response objects."""
    ip.display_formatter.formatters['text/plain'].for_type(
        'requests.models.Response', repr_request
    )


if __name__ == "__main__":
    shell = get_ipython()

    if shell is not None:
        try:
            import requests
        except (ImportError, ModuleNotFoundError):
            sys.exit()
        else:
            load_ipython_extension(shell)
