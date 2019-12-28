#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging

ROOT_HANDLER_PD = logging.StreamHandler(sys.stdout)
ROOT_HANDLER_PD.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    style="%",
    format="%(created)f %(module)s %(levelname)s %(message)s",
    handlers=[ROOT_HANDLER_PD],
)


def pandas_init():
    """Define options for :mod:`pandas` startup.

    .. tip::

        Don't set `start.options['show_dimensions'] to ``False``.
        ``'show_dimensions'`` means show the size of the `pd.DataFrame` object.

    ``truncate`` indicates to only display it when the DataFrame is...
    well truncated. [1]_

    .. [1] https://pandas.pydata.org/pandas-docs/stable/user-guide/options.html

    """
    options = {
        "display": {
            "colheader_justify": "right",
            "encoding": "utf-8",
            "expand_frame_repr": False,  # Don't wrap to multiple pages
            "html.table_schema": True,
            "max_columns": None,
            "max_colwidth": 25,
            "max_rows": 30,
            "max_seq_items": 50,
            # Max length of printed sequence 'precision': 4,
            "show_dimensions": "truncate",
        },
        "mode": {
            "chained_assignment": None
            # Controls SettingWithCopyWarning
        },
    }

    # XXX: Did i mean to do this twice?
    for category, option in options.items():
        for op, value in option.items():
            pd.set_option(f"{category}.{op}", value)  # Python 3.6+

    pd.plotting.register_matplotlib_converters()


class DisplayHTML:
    """Display HTML representation of multiple objects"""

    template = """
    <div style="float: left; padding: 10px;">
    <p style='font-family:'DejaVu Sans Mono',
    "Courier New", Courier, monospace'>{0}</p>{1}
    </div>
    """

    def __init__(self, *args):
        self.args = args

    def _repr_html_(self):
        return "\n".join(
            self.template.format(a, eval(a)._repr_html_()) for a in self.args
        )

    def __repr__(self):
        return "\n\n".join(a + "\n" + repr(eval(a)) for a in self.args)


if __name__ == "__main__":
    try:  # Import numexpr before pandas if possible
        import numexpr
    except (ImportError, ModuleNotFoundError):
        pass

    try:
        import pandas as pd
    except (ImportError, ModuleNotFoundError):
        logging.error("Pandas not installed.")
    else:
        pandas_init()
