=======================
Keybindings in IPython
=======================

.. module:: ipython_keybindings
    :synopsis: Module for managing keybindings in IPython.

Interactively Binding Keys
==========================
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
==============================

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


The documentation also shows a way of adding a Conditional Filter
*a la Prompt Toolkit* to the Enter key. Looks like it invokes some
:class:`prompt_toolkit.application.Buffer()` type code.

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
--------------------------------------------
There are 2 different sections on rebinding keys from Prompt Toolkit.

The first time it's mentioned is in the :doc:`prompt_toolkit.asking_for_input` document.:

Adding custom key bindings
~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    key bindings doesn’t print anything, then it can be handled directly
    without nesting functions.

Enable key bindings according to a condition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:

    Often, some key bindings can be enabled or disabled according to a certain
    condition. For instance, the Emacs and Vi bindings will never be active at
    the same time, but it is possible to switch between Emacs and Vi bindings
    at run time.

    In order to enable a key binding according to a certain condition, we have
    to pass it a Filter, usually a Condition instance. (Read more about filters.)::

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
a new set of keybindings that blends together Emacs insert mode and Vim command mode.

Ideally this would be tied together as 1 set of keybindings so that we don't run into
key binding collisions. A :class:`prompt_toolkit.key_bindings.DynamicKeyBindings`
might be useful. Bring it together with :func:`prompt_toolkit.key_bindings.merge_key_bindings`:

    The Application has an editing_mode attribute. We can change the key
    bindings by changing this attribute from EditingMode.VI to EditingMode.EMACS.::

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

Read more about key bindings …

Using control-space for completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:

    An popular short cut that people sometimes use it to use control-space for
    opening the autocompletion menu instead of the tab key. This can be done
    with the following key binding.::

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
::

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

    .. lol what is that typo. mean thread???

    Further, when “x” is pressed, we set a cancel flag, which stops the progress.
    It would also be possible to send SIGINT to the mean thread, but that’s not
    always considered a clean way of cancelling something.

    In the example above, we also display a toolbar at the bottom which shows the
    key bindings.


Conditional Key Bindings
~~~~~~~~~~~~~~~~~~~~~~~~
Then again as a more advanced section.:

    It is also possible to combine multiple registries. We do this in the default
    key bindings. There are some registries that contain Emacs bindings, while
    others contain the Vi bindings. They are merged together using a
    :class:`prompt_toolkit.bindings.MergedRegistry``.

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


What happened here?
====================
.. don't let this go into the final commit

I wanted to try experimenting with the code to dynamically set up a toggle
between Emacs and Vim.

I didn't think that when the docstring said "DynamicKeyBindings takes a callable"
that they meant the IPython global instance.

But I was curious what would happen.

Doing so actually created an embedded IPython instance that you can now toggle on and off.

And IPython allows you to do so with their ``dummy_mode`` attribute; which I've never
known about. The lack of a useful docstring to introspect the object with didn't help at all.

So maybe check out the source code for :mod:`IPython.terminal.embed`. But yeah I have
no idea what the fuck happened here.::

    In[7]: prompt_toolkit.key_binding.DynamicKeyBindings(_ip)
    Out[7]: <prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings at 0x189d84cae10>
    In[8]: t = prompt_toolkit.key_binding.DynamicKeyBindings(_ip)
      ...:
    In[9]: t?
    Type:        DynamicKeyBindings
    String form: <prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings object at 0x00000189D84CA160>
    File:        c:\tools\miniconda3\envs\dynamic\lib\site-packages\prompt_toolkit\key_binding\key_bindings.py
    Docstring:
    KeyBindings class that can dynamically returns any KeyBindings.

    :param get_key_bindings: Callable that returns a :class:`.KeyBindings` instance.

    In[10]: t
    Out[10]: <prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings at 0x189d84ca160>
    In[11]: dir(t)
    Out[11]:
    ['_DynamicKeyBindings__version',
     '__abstractmethods__',
     '__class__',
     '__delattr__',
     '__dict__',
     '__dir__',
     '__doc__',
     '__eq__',
     '__format__',
     '__ge__',
     '__getattribute__',
     '__gt__',
     '__hash__',
     '__init__',
     '__init_subclass__',
     '__le__',
     '__lt__',
     '__module__',
     '__ne__',
     '__new__',
     '__reduce__',
     '__reduce_ex__',
     '__repr__',
     '__setattr__',
     '__sizeof__',
     '__str__',
     '__subclasshook__',
     '__weakref__',
     '_abc_impl',
     '_dummy',
     '_last_child_version',
     '_update_cache',
     '_version',
     'bindings',
     'get_bindings_for_keys',
     'get_bindings_starting_with_keys',
     'get_key_bindings']
    In[12]: t.bindings
    Python 3.7.3 (default, Apr 24 2019, 15:29:51) [MSC v.1915 64 bit (AMD64)]
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.5.0 -- An enhanced Interactive Python. Type '?' for help.

    In [10]: >? exi
    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    C:\tools\miniconda3\envs\dynamic\lib\site-packages\prompt_toolkit\key_binding\key_bindings.py in <module>
    ----> 1 exi

    NameError: name 'exi' is not defined

    In [11]: >? exit

    Out[12]: []
    In[13]: type(t)
    Out[13]: prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings
    In[14]: t.get_key_bindings()
    Python 3.7.3 (default, Apr 24 2019, 15:29:51) [MSC v.1915 64 bit (AMD64)]
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.5.0 -- An enhanced Interactive Python. Type '?' for help.

    In [12]: >? exit

    In[15]: t.get_key_bindings?
    Signature:
    t.get_key_bindings(
        header='',
        local_ns=None,
        module=None,
        dummy=None,
        stack_depth=1,
        global_ns=None,
        compile_flags=None,
        **kw,
    )
    Type:            InteractiveShellEmbed
    String form:     <IPython.terminal.embed.InteractiveShellEmbed object at 0x00000189D8331860>
    File:            c:\tools\miniconda3\envs\dynamic\lib\site-packages\ipython\terminal\embed.py
    Docstring:       <no docstring>
    Class docstring: An enhanced, interactive shell for Python.
    Init docstring:
    Create a configurable given a config config.

    Parameters
    ----------
    config : Config
        If this is empty, default values are used. If config is a
        :class:`Config` instance, it will be used to configure the
        instance.
    parent : Configurable instance, optional
        The parent Configurable instance of this object.

    Notes
    -----
    Subclasses of Configurable must call the :meth:`__init__` method of
    :class:`Configurable` *before* doing anything else and using
    :func:`super`::

        class MyConfigurable(Configurable):
            def __init__(self, config=None):
                super(MyConfigurable, self).__init__(config=config)
                # Then any other code you need to finish initialization.

    This ensures that instances will be configured properly.
    Call docstring:
    Activate the interactive interpreter.

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

    In[16]: _ip.dummy_mode?
    Type:        bool

Source code for creating IPython shortcuts
==========================================

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
