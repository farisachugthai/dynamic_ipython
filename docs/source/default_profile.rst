:orphan:

=======================
:mod:`default_profile`
=======================

.. module:: default_profile
   :synopsis: Root of the source code


Profiles are the heart of IPython's configuration system, and as a result,
multiple profiles are included in the `default_profile` directory of the
repository.

Utilizing the IPython API: ---  Formatters
============================================

.. testsetup::

    from traitlets.config.configurable import LoggingConfigurable

::

    class BaseFormatterDoc(LoggingConfigurable):
        """A base formatter class that is configurable.

        This formatter should usually be used as the base class of all formatters. It
        is a traited :class:`Configurable` class and includes an extensible API for
        users to determine how their objects are formatted. The following logic is
        used to find a function to format an given object.

        1. The object is introspected to see if it has a method with the name
        :attr:`print_method`. If is does, that object is passed to that method
        for formatting.
        2. If no print method is found, three internal dictionaries are consulted
        to find print method: :attr:`singleton_printers`, :attr:`type_printers`
        and :attr:`deferred_printers`.

        Users should use these dictionaries to register functions that will be used
        to compute the format data for their objects (if those objects don't have the
        special print methods). The easiest way of using these dictionaries is
        through the :meth:`for_type` and :meth:`for_type_by_name` methods.

        If no function/callable is found to compute the format data, ``None`` is
        returned and this format type is not used.

        .. seealso:: :mod:`IPython.lib.pretty`.

        """

        def __init__(self, *args, **kwargs):
            """Initialize a BaseFormatter and get some Sphinx help.

            The remaining attributes from the config file are::

                c.BaseFormatter.deferred_printers = {}

                c.BaseFormatter.enabled = True

                c.BaseFormatter.singleton_printers = {}

                c.BaseFormatter.type_printers = {}

            """
            super().__init__(*args, **kwargs)

        def _example_subclass(self):
            """
            PlainTextFormatter(BaseFormatter) configuration
            -----------------------------------------------

            The default pretty-printer.

            This uses :mod:`IPython.lib.pretty` to compute the format data of
            the object.

            If the object cannot be pretty printed, :func:`repr` is used.

            See the documentation of :mod:`IPython.lib.pretty` for details on
            how to write pretty printers.  Here is a simple example::

                def dtype_pprinter(obj, p, cycle):
                    if cycle:
                        return p.text('dtype(...)')
                    if hasattr(obj, 'fields'):
                        if obj.fields is None:
                            p.text(repr(obj))
                        else:
                            p.begin_group(7, 'dtype([')
                            for i, field in enumerate(obj.descr):
                                if i > 0:
                                    p.text(',')
                                    p.breakable()
                                p.pretty(field)
                            p.end_group(7, '])')

            c.PlainTextFormatter.float_precision = ''

            Truncate large collections (lists, dicts, tuples, sets) to this size.

            Set to 0 to disable truncation.
            Default is 1000 but that floods a terminal.
            c.PlainTextFormatter.max_seq_length = 100

            Default value
            c.PlainTextFormatter.max_width = 79

            c.PlainTextFormatter.newline = '\n'

            c.PlainTextFormatter.pprint = True

            c.PlainTextFormatter.verbose = True
            """
            return repr(self.__doc__)

        def __repr__(self):
            return self._example_subclass()

        def _repr_pretty_(self, p, cycle=None):
            """ExecutionMagics has an example of how to use this method...

            Well...erhm. I guess so anyway.::

                unic = self.__str__()
                p.text(u'<TimeitResult : '+unic+u'>')

            What is p? And we don't use cycle so...
            Oh holy shit. Well if you see the string method...I'm putting this
            in a new class wtf.
            """
            p.text("<TimeitResult : " + unic + ">")
