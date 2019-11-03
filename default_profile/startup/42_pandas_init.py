#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=====================
Pandas Initialization
=====================

As of version 0.25, there's currently a large number of options that can
be set to modify Pandas' behavior.

An example of this::

    In [8]: pd.options
    Out[8]: <pandas._config.config.DictWrapper at 0x1f2facfdd68
            compute=<pandas._config.config.DictWrapper at 0x1f2fbfc1d30
            use_bottleneck=True,
            use_numexpr=True>,
            display=<pandas._config.config.DictWrapper at 0x1f2fbfc1c18
                    chop_threshold=None,
                    colheader_justify='right',
                    column_space=12,
                    date_dayfirst=False,
                    date_yearfirst=False,
                    encoding='utf-8',
                    expand_frame_repr=False,
                    float_format=None,
            html=<pandas._config.config.DictWrapper at 0x1f2fbfc1c50
                border=1,
                table_schema=True,
                use_mathjax=True>,
            large_repr='truncate',
            latex=<pandas._config.config.DictWrapper at 0x1f2fbfc1c50
                 escape=True,
                 longtable=False,
                 multicolumn=True,
                 multicolumn_format='l',
                 multirow=False,
                 repr=False>,
            max_categories=8,
            max_columns=None,
            max_colwidth=25,
            max_info_columns=100,
            max_info_rows=1690785,
            max_rows=30,
            max_seq_items=50,
            memory_usage=True,
            min_rows=10,
            multi_sparse=True,
            notebook_repr_html=True,
            pprint_nest_depth=3,
            precision=6,
            show_dimensions='truncate',
            unicode=<pandas._config.config.DictWrapper at 0x1f2fbfc1c50
                    ambiguous_as_wide=False,
                    east_asian_width=False>,
                    width=80>,
            io=<pandas._config.config.DictWrapper at 0x1f2fbfc1d30
            excel=<pandas._config.config.DictWrapper at 0x1f2fce37f98
            ods=<pandas._config.config.DictWrapper at 0x1f2fce37ac8
                 reader='auto'>,
            xls=<pandas._config.config.DictWrapper at 0x1f2fce37978
                 reader='auto',
                 writer='auto'>,
            xlsm=<pandas._config.config.DictWrapper at 0x1f2fce37ac8
                  reader='auto',
                  writer='auto'>,
            xlsx=<pandas._config.config.DictWrapper at 0x1f2fce37978
                  reader='auto',
                  writer='auto'>>,
            hdf=<pandas._config.config.DictWrapper at 0x1f2fce379e8
                default_format=None,
                dropna_table=False>,
            parquet=<pandas._config.config.DictWrapper at 0x1f2fce37978
                    engine='auto'>>,
            mode=<pandas._config.config.DictWrapper at 0x1f2fbfc1c18
                    chained_assignment=None,
                    sim_interactive=False,
                    use_inf_as_na=False,
                    use_inf_as_null=False>,
                    plotting=<pandas._config.config.DictWrapper at
                    0x1f2fbfc1d30
                    backend='matplotlib',
                    matplotlib=<pandas._config.config.DictWrapper at
                    0x1f2fce37978
                    register_converters=True>>>


Here's an interesting blurb from pandas/docs/conf.py::

    import pandas as pd
    # This ensures correct rendering on system with console encoding != utf8
    # (windows). It forces pandas to encode its output reprs using utf8
    # wherever the docs are built. The docs' target is the browser, not
    # the console, so this is fine.
    pd.options.display.encoding="utf8"


See Also
--------
.. seealso::

    https://realpython.com/python-pandas-tricks/#1-configure-options-settings-at-interpreter-startup

"""
import logging

# from default_profile.util import module_log
# PANDAS_LOGGER = logging.getLogger('default_profile.startup').getChild('42_pandas_init')
# PANDAS_LOGGER.addHandler(logging.StreamHandler().setLevel(logging.INFO))
# PANDAS_LOGGER.setLevel(logging.INFO)
ROOT_HANDLER_PD = logging.StreamHandler().setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, style='%', format='%(created)f : %(module)s : %(levelname)s : %(message)s',
        handlers=[ROOT_HANDLER_PD])


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
        'display': {
            'colheader_justify': 'right',
            'encoding': 'utf-8',
            'expand_frame_repr': False,  # Don't wrap to multiple pages
            'html.table_schema': True,
            'max_columns': None,
            'max_colwidth': 25,
            'max_rows': 30,
            'max_seq_items': 50,
            # Max length of printed sequence 'precision': 4,
            'show_dimensions': 'truncate',
        },
        'mode': {
            'chained_assignment': None
            # Controls SettingWithCopyWarning
        }
    }

    # XXX: Did i mean to do this twice?
    for category, option in options.items():
        for op, value in option.items():
            pd.set_option(f'{category}.{op}', value)  # Python 3.6+


class DisplayHTML:
    """Display HTML representation of multiple objects"""

    template = """
    <div style="float: left; padding: 10px;">
    <p style='font-family:"Courier New", Courier, monospace'>{0}</p>{1}
    </div>
    """

    def __init__(self, *args):
        self.args = args

    def _repr_html_(self):
        return '\n'.join(
            self.template.format(a,
                                 eval(a)._repr_html_()) for a in self.args)

    def __repr__(self):
        return '\n\n'.join(a + '\n' + repr(eval(a)) for a in self.args)


if __name__ == '__main__':
    name = 'default_profile.startup.pandas_init'
    # PANDAS_LOGGER = module_log.stream_logger(logger=name,
    #                                          log_level=logging.INFO)

    try:  # Import numexpr before pandas if possible
        import numexpr
    except (ImportError, ModuleNotFoundError):
        pass

    try:
        import pandas as pd
    except (ImportError, ModuleNotFoundError):
        logging.error('Pandas not installed.')
    else:
        pandas_init()
