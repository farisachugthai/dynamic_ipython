=======================
Keybindings in IPython
=======================

.. module:: Keybindings
   :synopsis: Document the way keybindings are set up.

.. highlight:: ipython
   :linenothreshold: 5


This document will summarize how to rebind keys in IPython since IPython 5.0.

Interactively Binding Keys
==========================
If we would like to add extra keybindings to the IPython shell, we can utilize
a few functions built into the :mod:`IPython.terminal.interactiveshell` module,
in addition, to utilizing the expansive :mod:`prompt_toolkit` library.

First we'll initialize a global instance of the shell.

Then import the function
:func:`IPython.terminal.interactiveshell.create_ipython_shortcuts()`
and initialize a
:class:`prompt_toolkit.key_binding.key_bindings.KeyBindings()`
instance.

The attributes associated with
:func:`IPython.terminal.interactiveshell.create_ipython_shortcuts()`
are as follows:

.. ipython::
   :verbatim:

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


Original File Implementation
----------------------------
Let's first check out how keybindings were originally implemented to give
ourselves a frame of reference.:

.. ipython::

   In [1]: from IPython.paths import get_ipython_package_dir
   In [2]: get_ipython_package_dir()

Go to the directory where IPython is installed. You can use the code above
to check its location.

This could be named something to the effect of
``~/miniconda3/lib/python3.7/site-packages/IPython/`` for example.

Then navigate to the root of that directory and go to the terminal package.

.. ipython::
   :verbatim:

    %cd /usr/lib/python3.7/site-packages/IPython
    %cd terminal
    %pycat shortcuts

Up at the top you have the keybindings :mod:`IPython` ships with!


Official IPython Documentation
==============================
Before we dive straight into the source code, let's check out how IPython
describes the process of re-binding keys.

The source code provides this example:


Pure Prompt Toolkit Way of Rebinding Keys
--------------------------------------------
There are 3 different sections in the Prompt Toolkit Official Documentation
on how to rebind keys using the package.


Adding custom key bindings
~~~~~~~~~~~~~~~~~~~~~~~~~~
The first time it's mentioned is in the asking_for_input document.:

    By default, every prompt already has a set of key bindings which implements
    the usual Vi or Emacs behaviour.

    We can extend this by passing another KeyBindings instance to the
    key_bindings argument of the prompt() function or the PromptSession class.

    An example of a prompt that prints 'hello world' when Control-T is pressed.::

        from prompt_toolkit import prompt
        from prompt_toolkit.application import run_in_terminal
        from prompt_toolkit.key_binding import KeyBindings

        bindings = KeyBindings()

        @bindings.add('c-t')
        def _(event):
            " Say 'hello' when `c-t` is pressed. "
            def print_hello():
                print('hello world')
            run_in_terminal(print_hello)

        @bindings.add('c-x')
        def _(event):
            " Exit when `c-x` is pressed. "
            event.app.exit()

        text = prompt('> ', key_bindings=bindings)
        print('You said: %s' % text)

    Note that we use run_in_terminal() for the first key binding. This ensures
    that the output of the print-statement and the prompt don’t mix up. If the
    key bindings doesn't print anything, then it can be handled directly
    without nesting functions.

Enable key bindings according to a condition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Then key_bindings are discussed in the context of being filtered through
certain conditions.:

    Often, some key bindings can be enabled or disabled according to a certain
    condition. For instance, the Emacs and Vi bindings will never be active at
    the same time, but it is possible to switch between Emacs and Vi bindings
    at run time.

    In order to enable a key binding according to a certain condition, we have
    to pass it a Filter, usually a Condition instance.::

        from prompt_toolkit import prompt
        from prompt_toolkit.filters import Condition
        from prompt_toolkit.key_binding import KeyBindings

        bindings = KeyBindings()

        @Condition
        def is_active():
            " Only activate key binding on the second half of each minute. "
            return datetime.datetime.now().second > 30

        @bindings.add('c-t', filter=is_active)
        def _(event):
            # ...
            pass

        prompt('> ', key_bindings=bindings)


Dynamically switch between Emacs and Vi mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is the part I'm most interested in, as we're going to try coming up with
a new set of keybindings that blends together Emacs insert mode and
Vim command mode.

Ideally this would be tied together as 1 set of keybindings so that we don't
run into key binding collisions. A
:class:`prompt_toolkit.key_bindings.DynamicKeyBindings()`
might be useful. Bring it together with
:func:`prompt_toolkit.key_bindings.merge_key_bindings()`:

    The Application has an editing_mode attribute. We can change the key
    bindings by changing this attribute from EditingMode.VI to
    EditingMode.EMACS.::

        from prompt_toolkit import prompt
        from prompt_toolkit.application.current import get_app
        from prompt_toolkit.filters import Condition
        from prompt_toolkit.key_binding import KeyBindings

        def run():
            # Create a set of key bindings.
            bindings = KeyBindings()

            # Add an additional key binding for toggling this flag.
            @bindings.add('f4')
            def _(event):
                " Toggle between Emacs and Vi mode. "
                app = event.app

                if app.editing_mode == EditingMode.VI:
                    app.editing_mode = EditingMode.EMACS
                else:
                    app.editing_mode = EditingMode.VI

            # Add a toolbar at the bottom to display the current input mode.
            def bottom_toolbar():
                " Display the current input mode. "
                text = 'Vi' if get_app().editing_mode == EditingMode.VI else 'Emacs'
                return [
                    ('class:toolbar', ' [F4] %s ' % text)
                ]

            prompt('> ', key_bindings=bindings, bottom_toolbar=bottom_toolbar)

        run()



Using control-space for completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Here's a general overview with more examples on how to rebind keys.:

    A popular short cut that people sometimes use is :kbd:`Ctrl` :kbd:`Space`
    for opening the autocompletion menu instead of the tab key.
    This can be done with the following key binding.::

        kb = KeyBindings()

        @kb.add('c-space')
        def _(event):
            " Initialize autocompletion, or select the next completion. "
            buff = event.app.current_buffer
            if buff.complete_state:
                buff.complete_next()
            else:
                buff.start_completion(select_first=False)


Progress Bar Section
~~~~~~~~~~~~~~~~~~~~
This continues in the section on progress bars.::

    from prompt_toolkit import HTML
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.patch_stdout import patch_stdout
    from prompt_toolkit.shortcuts import ProgressBar

    import time

    bottom_toolbar = HTML(' <b>[f]</b> Print "f" <b>[x]</b> Abort.')

    # Create custom key bindings first.
    kb = KeyBindings()
    cancel = [False]

    @kb.add('f')
    def _(event):
        print('You pressed `f`.')

    @kb.add('x')
    def _(event):
        " Send Abort (control-c) signal. "
        cancel[0] = True
        os.kill(os.getpid(), signal.SIGINT)

    # Use `patch_stdout`, to make sure that prints go above the
    # application.
    with patch_stdout():
        with ProgressBar(key_bindings=kb, bottom_toolbar=bottom_toolbar) as pb:
            for i in pb(range(800)):
                time.sleep(.01)

                # Stop when the cancel flag has been set.
                if cancel[0]:
                    break

    Notice that we use patch_stdout() to make printing text possible while the
    progress bar is displayed. This ensures that printing happens above the
    progress bar.

    Further, when “x” is pressed, we set a cancel flag, which stops the progress.
    It would also be possible to send SIGINT to the main thread, but that’s not
    always considered a clean way of cancelling something.

    In the example above, we also display a toolbar at the bottom which shows the
    key bindings.


Conditional Key Bindings
~~~~~~~~~~~~~~~~~~~~~~~~
Then again as a more advanced section.:

    It is also possible to combine multiple registries. We do this in the default
    key bindings. There are some registries that contain Emacs bindings, while
    others contain the Vi bindings. They are merged together using a
    :class:`prompt_toolkit.bindings.MergedRegistry`.

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


Reviewing Source Code
---------------------
Whew! Well that was a lot take in. But now we'll move from their official documents
to simply the source code where this is implemented.


Load all default keybindings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
From :mod:`prompt_toolkit.key_bindings.bindings.defaults`::

     def load_key_bindings():
         # Create a KeyBindings object that contains the default key bindings.
         all_bindings = merge_key_bindings([
             # Load basic bindings.
             load_basic_bindings(),

             # Load emacs bindings.
             load_emacs_bindings(),
             load_emacs_search_bindings(),

             # Load Vi bindings.
             load_vi_bindings(),
             load_vi_search_bindings(),
         ])

         return merge_key_bindings([
             # Make sure that the above key bindings are only active if the
             # currently focused control is a `BufferControl`. For other controls, we
             # don't want these key bindings to intervene. (This would break "ptterm"
             # for instance, which handles 'Keys.Any' in the user control itself.)
             ConditionalKeyBindings(all_bindings, buffer_has_focus),

             # Active, even when no buffer has been focused.
             load_mouse_bindings(),
             load_cpr_bindings(),
         ])

That's literally everything. IPython chooses to add their own stuff
during :ref:`IPython.terminal.ptutil.create_ipython_shortcuts` but if you
choose to create your own registry then you get access to everything.

It might not be hard to bind to if we do it the same way we did with
that one :class:`pathlib.Path` class.

Literally::

    from IPython import get_ipython
    from prompt_toolkit.key_binding import merge_key_bindings, KeyBindings
    from prompt_toolkit.key_binding.defaults import load_key_bindings

    class KeyBindingsManager:

        def __init__(self, shell=None):
            if _ip is None:
                _ip = get_ipython()
            self.registry = KeyBindings

Once the user initializes that class, then your
:class:`prompt_toolkit.key_bindings.keybinding.KeyBindings()`
statement in the ``__init__`` func was execute and you'll have access
to everything. Cool!::

   registry = load_key_bindings()
   dir(registry.key_bindings)


Ptpython and autocorrection
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is simply a different way to conceptualize key bindings that I hadn't
seen before and found pretty creative.::

    corrections = {
        'impotr': 'import',
        'pritn': 'print',
    }

    @repl.add_key_binding(' ')
    def _(event):
        ' When a space is pressed. Check & correct word before cursor. '
        b = event.cli.current_buffer
        w = b.document.get_word_before_cursor()

        if w is not None:
            if w in corrections:
                b.delete_before_cursor(count=len(w))
                b.insert_text(corrections[w])

        b.insert_text(' ')


Side Effects
====================
I wanted to try experimenting with the code to dynamically set up a toggle
between Emacs and Vim.

I didn't think that when the docstring said "**DynamicKeyBindings**
take a callable" that they meant the IPython global instance.

But I was curious what would happen.

Doing so actually created an embedded IPython instance that you can now
toggle on and off.

.. ipython::
   :verbatim:

   Type:        DynamicKeyBindings
   Docstring:
   KeyBindings class that can dynamically returns any KeyBindings.

   :param get_key_bindings: Callable that returns a :class:`.KeyBindings` instance.

The help for :func:`prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings.get_key_bindings()`:

.. ipython::
   :verbatim:

   print(help(t.get_key_bindings))
   Signature: t.get_key_bindings(header='', local_ns=None, module=None, dummy=None, stack_depth=1, global_ns=None, compile_flags=None, \*\*kw,)

   Type:            InteractiveShellEmbed
   Docstring:       <no docstring>
   Class docstring: An enhanced, interactive shell for Python.

   __call__(self,header='',local_ns=None,module=None,dummy=None) -> Start
   the interpreter shell with the given local and global namespaces, and
   optionally print a header string at startup.

   The shell can be globally activated/deactivated using the
   dummy_mode attribute. This allows you to turn off a shell used
   for debugging globally.

   However, *each* time you call the shell you can override the current
   state of dummy_mode with the optional keyword parameter 'dummy'. For
   example, if you set dummy mode on with IPShell.dummy_mode = True, you
   can still have a specific call work by making it as IPShell(dummy=False).


Source code for creating IPython shortcuts
==========================================

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
