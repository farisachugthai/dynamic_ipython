.. _ipython_keybindings:

=======================
Keybindings in IPython
=======================

.. module:: ipython_keybindings
    :synopsis: Module for managing keybindings in IPython.

Run in shell
-------------
If we would like to add extra keybindings to the IPython shell, we can utilize
a few functions built into the :mod:`IPython.terminal.interactiveshell` module,
in addition, to utilizing the expansive :mod:`prompt_toolkit` library.

First we'll initialize a global instance of the shell.

Then import the function :func:`~IPython.terminal.interactiveshell.create_ipython_shortcuts`
and initialize a :class:`~prompt_toolkit.key_binding.key_bindings.KeyBindings`
instance.

The attributes associated with :func:`~IPython.terminal.interactiveshell.create_ipython_shortcuts`
are as follows:


.. ipython:: python

    >>> from IPython import get_ipython
    >>> from IPython.terminal.interactiveshell import create_ipython_shortcuts
    >>> ip = get_ipython()
    >>> c = create_ipython_shortcuts(ip)
    >>> # This will give you the following methods
    >>> print(dir(c))
        ['_KeyBindings__version',
        ...
        '_abc_impl',
        '_clear_cache',
        '_get_bindings_for_keys_cache',
        '_get_bindings_starting_with_keys_cache'
        '_version',
        'add',
        'add_binding',
        'bindings',
        'get_bindings_for_keys',
        'get_bindings_starting_with_keys',
        'remove',
        'remove_binding']


That file also gives a good example of how to bind keys.


Original File Implementation
----------------------------

Go to the IPython root dir. This could be named something to the effect of
`<~/miniconda3/lib/python3.7/site-packages/IPython/>`_

To find it programtically, one can use::

   >>> from IPython.paths import get_ipython_package_dir
   >>> print(get_ipython_package_dir())

Then navigate to the root of that directory.

``%cd /usr/lib/python3.7/site-packages/IPython``

Go to the terminal package.
``%cd terminal``
``%pycat shortcuts``

Up at the top you have the keybindings :mod:`IPython` ships with listed
for ya!

Official IPython Documentation
------------------------------

.. code-block:: python3

    from prompt_toolkit.key_binding.registry import Registry
    from prompt_toolkit.key_binding.defaults import load_key_bindings
    from IPython import get_ipython
    from prompt_toolkit.enums import DEFAULT_BUFFER
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.filters import HasFocus, HasSelection, ViInsertMode
    ip = get_ipython()
    insert_mode = ViInsertMode()

    def insert_unexpected(event):
        """From the IPython examples on keybinding configuration."""
        buf = event.current_buffer
        buf.insert_text('The Spanish Inquisition')
        # Register the shortcut if IPython is using prompt_toolkit
        if getattr(ip, 'pt_cli'):
            registry = ip.pt_cli.application.key_bindings_registry

            registry.add_binding(Keys.ControlN,
                     filter=(HasFocus(DEFAULT_BUFFER)
                                  & ~HasSelection()
                             & insert_mode))(insert_unexpected)


Continue on in this fashion for as long as you need IPython barely comes
with any keybindings. I'm going to drop 1 that I thought was interesting
though.
*Also because i didn't know or remember these were keybindings.*

.. code-block:: python3

   # Ctrl+J == Enter, seemingly
   registry.add_binding(Keys.ControlJ,
                        filter=(HasFocus(DEFAULT_BUFFER)
                        & ~HasSelection()
                        & insert_mode
                        ))
                        (return_handler)

Pure Prompt Toolkit Way of Rebinding Keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
From the pt docs:

    It is also possible to combine multiple registries. We do this in the default
    key bindings. There are some registries that contain Emacs bindings, while
    others contain the Vi bindings. They are merged together using a ``MergedRegistry``.

    We also have a ``ConditionalRegistry`` object that can enable/disable a group
    of key bindings at once.

    .. code-block:: python3

        r = Registry()

        @r.add_binding(Keys.ControlX, Keys.ControlC, filter=INSERT)
        def handler(event):
            """A quick snippet to give you a flavor of the syntax.

            Gotta figure out what's up with that filter param over there.
            02/24/2019: The ``filter`` parameter is optional it just helps specify things.

            Luckily I think that keybindings actually don't need function bodies
            The decorator's doing all the heavy lifting for ya! I think...
            """
            # Handle ControlX-ControlC key sequence.
            pass

        def check_defaults():
            """What are the default keybindings we have here?

            Err I suppose I should say what does Prompt Toolkit export by default
            because I'm not 100% sure that ip imports everything or doesn't modify
            anything along the way.
            """
            registry = load_key_bindings()
            print(registry.key_bindings)


Source code for creating IPython shortcuts
------------------------------------------

.. ipython:: python

   >>> %pycat shortcuts.py

Module to define and register Terminal IPython shortcuts with
:mod:`prompt_toolkit`

Copyright (c) IPython Development Team.
Distributed under the terms of the Modified BSD License.

.. code-block:: python3

   import warnings
   import signal
   import sys
   from typing import Callable

   from prompt_toolkit.enums import DEFAULT_BUFFER, SEARCH_BUFFER
   from prompt_toolkit.filters import (HasFocus, HasSelection, Condition,
       ViInsertMode, EmacsInsertMode, HasCompletions)
   from prompt_toolkit.filters.cli import ViMode, ViNavigationMode
   from prompt_toolkit.keys import Keys
   from prompt_toolkit.key_binding.bindings.completion import display_completions_like_readline

   from IPython.utils.decorators import undoc

   @undoc
   @Condition
   def cursor_in_leading_ws(cli):
       before = cli.application.buffer.document.current_line_before_cursor
       return (not before) or before.isspace()

   def register_ipython_shortcuts(registry, shell):
       """Set up the prompt_toolkit keyboard shortcuts for IPython"""
       insert_mode = ViInsertMode() | EmacsInsertMode()

       if getattr(shell, 'handle_return', None):
           return_handler = shell.handle_return(shell)
       else:
           return_handler = newline_or_execute_outer(shell)

       # Ctrl+J == Enter, seemingly
       registry.add_binding(Keys.ControlJ,
                            filter=(HasFocus(DEFAULT_BUFFER)
                                    & ~HasSelection()
                                    & insert_mode
                           ))(return_handler)

       registry.add_binding(Keys.ControlBackslash)(force_exit)

       registry.add_binding(Keys.ControlP,
                            filter=(ViInsertMode() & HasFocus(DEFAULT_BUFFER)
                           ))(previous_history_or_previous_completion)

       registry.add_binding(Keys.ControlN,
                            filter=(ViInsertMode() & HasFocus(DEFAULT_BUFFER)
                           ))(next_history_or_next_completion)

       registry.add_binding(Keys.ControlG,
                            filter=(HasFocus(DEFAULT_BUFFER) & HasCompletions()
                           ))(dismiss_completion)

       registry.add_binding(Keys.ControlC, filter=HasFocus(DEFAULT_BUFFER)
                           )(reset_buffer)

       registry.add_binding(Keys.ControlC, filter=HasFocus(SEARCH_BUFFER)
                           )(reset_search_buffer)

       supports_suspend = Condition(lambda cli: hasattr(signal, 'SIGTSTP'))
       registry.add_binding(Keys.ControlZ, filter=supports_suspend
                           )(suspend_to_bg)

       # Ctrl+I == Tab
       registry.add_binding(Keys.ControlI,
                            filter=(HasFocus(DEFAULT_BUFFER)
                                    & ~HasSelection()
                                    & insert_mode
                                    & cursor_in_leading_ws
                           ))(indent_buffer)

       registry.add_binding(Keys.ControlO,
                            filter=(HasFocus(DEFAULT_BUFFER)
                                   & EmacsInsertMode()))(newline_autoindent_outer(shell.input_splitter))

       registry.add_binding(Keys.F2,
                            filter=HasFocus(DEFAULT_BUFFER)
                           )(open_input_in_editor)

       if shell.display_completions == 'readlinelike':
           registry.add_binding(Keys.ControlI,
                                filter=(HasFocus(DEFAULT_BUFFER)
                                        & ~HasSelection()
                                        & insert_mode
                                        & ~cursor_in_leading_ws
                               ))(display_completions_like_readline)

       if sys.platform == 'win32':
           registry.add_binding(Keys.ControlV,
                                filter=(
                                HasFocus(
                                DEFAULT_BUFFER) & ~ViMode()
                               ))(win_paste)
