==========================
IPython_InteractiveShell
==========================
Created Saturday 03 March 2018

`<https://github.com/ipython/ipython/blob/master/IPython/core/interactiveshell.py>`_

Subclasses of |ip|
==================

Lines 436-451

Here's some interesting line from the source code.

.. code-block:: python3

        # Subcomponents of InteractiveShell
        alias_manager = Instance('IPython.core.alias.AliasManager', allow_none=True)
        prefilter_manager = Instance('IPython.core.prefilter.PrefilterManager', allow_none=True)
        builtin_trap = Instance('IPython.core.builtin_trap.BuiltinTrap', allow_none=True)
        display_trap = Instance('IPython.core.display_trap.DisplayTrap', allow_none=True)
        extension_manager = Instance('IPython.core.extensions.ExtensionManager', allow_none=True)
        payload_manager = Instance('IPython.core.payload.PayloadManager', allow_none=True)
        history_manager = Instance('IPython.core.history.HistoryAccessorBase', allow_none=True)
        magics_manager = Instance('IPython.core.magic.MagicsManager', allow_none=True)
        profile_dir = Instance('IPython.core.application.ProfileDir', allow_none=True)

        @property
        def profile(self):
            if self.profile_dir is not None:
                name = os.path.basename(self.profile_dir.location)
            return name.replace('profile_','')


Traitlets
---------
.. ipython:: python

    In [3]: traitlets.Instance?
    Init signature: traitlets.Instance(klass=None, args=None, kw=None, \*\*kwargs)
    Docstring:
    A trait whose value must be an instance of a specified class.

    The value can also be an instance of a subclass of the specified class.

    Subclasses can declare default classes by overriding the klass attribute
    Init docstring:
    Construct an Instance trait.

    This trait allows values that are instances of a particular
    class or its subclasses.  Our implementation is quite different
    from that of enthough.traits as we don't allow instances to be used
    for klass and we handle the ``args`` and ``kw`` arguments differently.

    Parameters
    ----------
    klass : class, str
        The class that forms the basis for the trait.  Class names
        can also be specified as strings, like 'foo.bar.Bar'.
    args : tuple
        Positional arguments for generating the default value.
    kw : dict
        Keyword arguments for generating the default value.
    allow_none : bool [ default False ]
        Indicates whether None is allowed as a value.

    Notes
    -----
    If both ``args`` and ``kw`` are None, then the default value is None.
    If ``args`` is a tuple and ``kw`` is a dict, then the default is
    created as ``klass(*args, **kw)``.  If exactly one of ``args`` or ``kw`` is
    None, the None is replaced by ``()`` or ``{}``, respectively.
    File:           ~/virtualenvs/utilities/lib/python3.7/site-packages/traitlets/traitlets.py
    Type:           type
    Subclasses:     ForwardDeclaredInstance, Container, Dict
