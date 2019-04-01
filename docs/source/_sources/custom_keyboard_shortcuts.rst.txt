Keyboard Shortcut Customization
===============================

Starting with IPython 2.0 keyboard shortcuts in command and edit mode
are fully customizable. These customizations are made using the IPython
JavaScript API. Here is an example that makes the ``r`` key available
for running a cell:

.. code:: javascript

    %%javascript

    IPython.keyboard_manager.command_shortcuts.add_shortcut('r', {
        help : 'run cell',
        help_index : 'zz',
        handler : function (event) {
            IPython.notebook.execute_cell();
            return false;
        }}
    );



.. parsed-literal::

    <IPython.core.display.Javascript at 0x10e8d1890>


There are a couple of points to mention about this API:

-  The ``help_index`` field is used to sort the shortcuts in the
   Keyboard Shortcuts help dialog. It defaults to ``zz``.
-  When a handler returns ``false`` it indicates that the event should
   stop propagating and the default action should not be performed. For
   further details about the ``event`` object or event handling, see the
   jQuery docs.
-  If you don’t need a ``help`` or ``help_index`` field, you can simply
   pass a function as the second argument to ``add_shortcut``.

.. code:: javascript

    %%javascript

    IPython.keyboard_manager.command_shortcuts.add_shortcut('r', function (event) {
        IPython.notebook.execute_cell();
        return false;
    });



.. parsed-literal::

    <IPython.core.display.Javascript at 0x1019baf90>


Likewise, to remove a shortcut, use ``remove_shortcut``:

.. code:: javascript

    %%javascript

    IPython.keyboard_manager.command_shortcuts.remove_shortcut('r');



.. parsed-literal::

    <IPython.core.display.Javascript at 0x10e8d1950>


If you want your keyboard shortcuts to be active for all of your
notebooks, put the above API calls into your
``<profile>/static/custom/custom.js`` file.
