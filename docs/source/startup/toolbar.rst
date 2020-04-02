==================================================
:mod:`~default_profile.startup.33_bottom_toolbar`
==================================================

.. currentmodule:: default_profile.startup.33_bottom_toolbar

This module begins the section of the repository that entails more advanced
customization of prompt_toolkit.

Lower level constructs like widgets, toolbars and eventually the Layout classes
are utilized quite heavily.


.. admonition:: Be careful what the bottom toolbar is set to.

   It's not very difficult to crash the entire application as a result of
   giving it the wrong type.

The |ip|\.`pt_app.bottom_toolbar` type is expected to be some kind of
`FormattedText`. Unfortunately, feeding it an already populated control like a
`FormattedTextToolbar` will break the application.

Don't run.:

.. parsed-literal::

    bottom_toolbar = FormattedTextToolbar(bottom_text)
    shell.pt_app.bottom_toolbar = bottom_toolbar

Note that a similar expression is used to assign the `BottomToolbar`
to the shell's *pt_app.bottom_toolbar* attribute.::

   from prompt_toolkit.formatted_text import FormattedText
   from IPython import get_ipython

   bottom_text = BottomToolbar()
   bottom_toolbar = FormattedText(bottom_text.rerender())

However, the `FormattedText` in and of itself doesn't provide any functionality.
A `FormattedText` object is simply a subclass of `list`. The value is provided
in defining a method ``__pt_formatted_text__``.

As a result, `BottomToolbar` also defines this method and as a result an
instance of the class can be passed directly as an assignment to the
``_ip.pt_app.bottom_toolbar``.

Examples
--------

.. code-block:: python

   >>> import time
   >>> from pathlib import Path
   >>> from default_profile.startup import bottom_toolbar_mod
   >>> if bottom_toolbar_mod is not None:
   >>>    from default_profile.startup.bottom_toolbar_mod
   >>>    bt = BottomToolbar(get_app())
   >>>    print(bt)
          <BottomToolbar:>
   >>>    bt()
          f" [F4] Vi: {current_vi_mode!r} \n  cwd: {Path.cwd().stem!r}\n Clock: {time.ctime()!r}"


Toolbar API
-----------

.. automodule:: default_profile.startup.33_bottom_toolbar
   :synopsis: Generate a toolbar using lower-level controls.
   :members:
   :undoc-members:
   :show-inheritance:


