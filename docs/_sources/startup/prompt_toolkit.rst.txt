==============
Prompt Toolkit
==============

.. module:: prompt_toolkit_modules
   :synopsis: Combined docs on all prompt_toolkit modules.


`~default_profile.startup.32_kb`
===========================================

.. currentmodule:: default_profile.startup.32_kb

.. _keybindings-summary:

Summary
-------

Make prompt_toolkit's keybindings more extensible.

Reminder of where you left off:

Bottom toolbar works but isn't bound to a key idk why it isn't working.
The seemingly recommended interface is to merge with merge_key_bindings
Difficult to add key_bindings after the merge though.
Mostly everything's behaving as it should however.

I'm just gonna note how much this bugs me though.::

    In [30]: p = PromptSessionKB()
    Out[30]: <PromptSessionKB>: 13

    In [31]: a = ApplicationKB()
    Out[31]: <ApplicationKB>: 24

Alright now I need to start keeping track because this is rough.::

    In [1]: _ip.pt_app.app  # Application. _ip.pt_app is the PromptSession.
    Out[1]: <prompt_toolkit.application.application.Application at 0x7f2710ac7d90>


    In [9]: _ip.pt_app.current_buffer
    AttributeError: 'PromptSession' object has no attribute 'current_buffer'

    In [2]: _ip.pt_app.app.current_buffer
    Out[2]: <Buffer(name='DEFAULT_BUFFER', text='_ip.pt_app.a...') at 139805760009696>

    In [3]: _ip.pt_app.validator

    In [4]: _ip.pt_app.app.validator
    AttributeError: 'Application' object has no attribute 'validator'

Alright so they're not the similar after all right?
From the docs.:

    Dynamically switch between Emacs and Vi mode

    The Application has an editing_mode attribute.
    We can change the key bindings by changing this attribute from
    `EditingMode.VI` to `EditingMode.EMACS`.

Guess what else has an editing_mode attribute.::

    In [5]: _ip.pt_app.editing_mode
    Out[5]: <EditingMode.VI: 'VI'>

    In [6]: _ip.pt_app.app.editing_mode
    Out[6]: <EditingMode.VI: 'VI'>


Dude `_MergedKeyBindings` are horrible.::

    In [30]: _ip.pt_app.app.key_bindings
    Out[30]: <prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f271047f340>

    In [31]: _ip.pt_app.app.key_bindings.registries
    Out[31]:
    [<prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac7b50>,
    <prompt_toolkit.key_binding.key_bindings.ConditionalKeyBindings at 0x7f2710447430>]

    In [32]: _ip.pt_app.app.key_bindings.registries[0]
    Out[32]: <prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac7b50>

    In [33]: _ip.pt_app.app.key_bindings.registries[0].registries
    Out[33]:
    [<prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac77f0>,
    <prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings at 0x7f2710ac79a0>]

    In [34]: _ip.pt_app.app.key_bindings.registries[0].registries[0]
    Out[34]: <prompt_toolkit.key_binding.key_bindings._MergedKeyBindings at 0x7f2710ac77f0>

    In [35]: _ip.pt_app.app.key_bindings.registries[0].registries[0].registries[0]
    Out[35]: <prompt_toolkit.key_binding.key_bindings.KeyBindings at 0x7f2710ac3160>

    In [36]: _ip.pt_app.app.key_bindings.registries[0].registries[0].registries[0].bindings
    Out[36]:
    [Binding(keys=(<Keys.Right: 'right'>,), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadd30>),
    Binding(keys=(<Keys.ControlE: 'c-e'>,), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadd30>),
    Binding(keys=(<Keys.ControlF: 'c-f'>,), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadd30>),
    Binding(keys=(<Keys.Escape: 'escape'>, 'f'), handler=<function load_auto_suggest_bindings.<locals>._ at 0x7f2710aadc10>)]

And you kinda can't do anything about it.::

    In [39]: did_we_make_it_better = DynamicKeyBindings(_ip.pt_app.app.key_bindings)
    Out[39]: <prompt_toolkit.key_binding.key_bindings.DynamicKeyBindings at 0x7f26f7d9ba30>

    In [40]: did_we_make_it_better.bindings
    TypeError: '_MergedKeyBindings' object is not callable

Can't extract anything from them.::

    In [42]: for i in load_key_bindings().registries[0].bindings:
        ...:     _ip.pt_app.key_bindings.add(i.keys)(i.handler)
        ...: ValueError: Invalid key: (<Keys.ControlX: 'c-x'>, 'r', 'y')

Gotta be honest I felt very creative working my way up to that one.
If we can't do that, lets keep working at the individual bindings.::

    In [43]: i.keys
    Out[43]: (<Keys.ControlX: 'c-x'>, 'r', 'y')
    In [44]: type(i.keys)
    Out[44]: tuple
    In [45]: i.keys[0]
    Out[45]: <Keys.ControlX: 'c-x'>

So far so good?::

    In [57]: c = ""
    ...: for j in i.keys:
    ...:     c += Keys(j)
    ...: ValueError: 'r' is not a valid Keys
        During handling of the above exception, another exception occurred:
        ValueError: 'r' is not a valid Keys

Yup. We have to redefine what a key is.


Fun with Vim
------------

Dude these are all the vi modes prompt_toolkit has...lol
So I just checked. Wanna know what it does?
They're basically Enums that get compared to ``editing_mode.input_mode``.::

    from prompt_toolkit.filters.app import (
        vi_selection_mode,
        vi_recording_macro,
        vi_register_names,
        vi_mode,
        vi_replace_mode,
        vi_waiting_for_text_object_mode,
        vi_insert_mode,
        vi_search_direction_reversed,
        vi_navigation_mode,
        vi_digraph_mode,
        vi_insert_multiple_mode,
    )

.. automodule:: default_profile.startup.32_kb
   :synopsis: Begin reworking prompt_toolkit's keybindings.
   :members:
   :undoc-members:
   :show-inheritance:


`~default_profile.startup.33_bottom_toolbar`
=============================================

This module begins the section of the repository that entails more advanced
customization of prompt_toolkit.

Lower level constructs like widgets, toolbars and eventually the Layout classes
are utilized quite heavily.

.. admonition:: Be careful what the bottom toolbar is set to.

   It's not very difficult to crash the entire application as a result of
   giving it the wrong type.

The |ip|\.`pt_app.bottom_toolbar` type is expected to be some kind of
FormattedText. Unfortunately, feeding it an already populated control like a
FormattedTextToolbar will break the application.

Don't run.::

    bottom_toolbar = FormattedTextToolbar(bottom_text)
    shell.pt_app.bottom_toolbar = bottom_toolbar

.. automodule:: default_profile.startup.33_bottom_toolbar
   :synopsis: Generate a toolbar using lower-level controls.
   :members:
   :undoc-members:
   :show-inheritance:


:mod:`~default_profile.startup.35_lexer`
===========================================

.. currentmodule:: default_profile.startup.35_lexer

Build our lexer in addition to utilizing already built ones.

Pygments, IPython, prompt_toolkit, Jinja2 and Sphinx all come
with their own concepts of lexers which doesn't include
the built-in modules.:

- :mod:`parser`

- :mod:`token`

- :mod:`tokenizer`

- :mod:`re`

- :mod:`ast`

So it'd be tough to say we're at a lack of tools!

.. class:: IPythonConfigurableLexer

   A class to merge the seemingly disjoint APIs of IPython, traitlets,
   prompt_toolkit and pygments.

   TODO: The `IPython.terminal.lexer.IPythonPTLexer` also should have a few
   of these attributes as well.

    And here's how you join the bridge.

.. class:: PygmentsLexer(Lexer):

   Lexer that calls a pygments lexer.

   Example::

      from pygments.lexers.html import HtmlLexer
      lexer = PygmentsLexer(HtmlLexer)

   Note: Don't forget to also load a Pygments compatible style. E.g.::

      from prompt_toolkit.styles.from_pygments import style_from_pygments_cls
      from pygments.styles import get_style_by_name
      style = style_from_pygments_cls(get_style_by_name('monokai'))

   :param pygments_lexer_cls: A `Lexer` from Pygments.
   :param sync_from_start: Start lexing at the start of the document. This
      will always give the best results, but it will be slow for bigger
      documents. (When the last part of the document is display, then the
      whole document will be lexed by Pygments on every key stroke.) It is
      recommended to disable this for inputs that are expected to be more
      than 1,000 lines.
   :param syntax_sync: `SyntaxSync` object.


.. automodule:: default_profile.startup.35_lexer
   :synopsis: Generate a lexer to provide syntax highlighting in the REPL.
   :members:
   :undoc-members:
   :show-inheritance:


:mod:`~default_profile.startup.ptoolkit`
===========================================

.. automodule:: default_profile.startup.ptoolkit
   :synopsis: Generate a more generalized class to interact with prompt_toolkit.
   :members:
   :undoc-members:
   :show-inheritance:


:mod:`~default_profile.startup.completions`
===========================================

.. automodule:: default_profile.startup.completions
   :members:
   :undoc-members:
   :show-inheritance:
