"""Leave the original API in place but add in a dictionary for all metadata."""
from datetime import datetime

__author__ = 'Faris Chugthai'
__copyright__ = u'Copyright (C) 2018-{} Faris Chugthai'.format(
    datetime.now().year
)
__docformat__ = 'reStructuredText'
__license__ = 'MIT'
__version_info__ = (0, 0, 2)
__version__ = ".".join(map(str, __version_info__))
metadata = {
    '__author__': 'Faris Chugthai',
    '__copyright__':
        u'Copyright (C) 2018-{} Faris Chugthai'.format(datetime.now().year),
    '__docformat__': 'reStructuredText',
    '__license__': 'MIT',
    '__version__': (0, 0, 1),
}
