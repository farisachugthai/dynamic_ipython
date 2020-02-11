==============
Prompt Toolkit
==============

.. module:: prompt_toolkit_modules
   :synopsis: Combined docs on all prompt_toolkit modules.


`~default_profile.startup.31_yank_last_arg`
===========================================

.. automodule:: default_profile.startup.31_yank_last_arg
   :members:
   :undoc-members:
   :show-inheritance:


`~default_profile.startup.32_kb`
===========================================

.. automodule:: default_profile.startup.32_kb
   :members:
   :undoc-members:
   :show-inheritance:


`~default_profile.startup.33_bottom_toolbar`
=============================================

.. automodule:: default_profile.startup.33_bottom_toolbar
   :members:
   :undoc-members:
   :show-inheritance:


`~default_profile.startup.34_completion`
===========================================

.. currentmodule:: default_profile.startup.34_completion

This module sets up different `Completer` classes for use. After setting
up `readline` to use the :kbd:`TAB` key in `30_readline`, we can now use
the `jedi` API, the :class:`~prompt_toolkit.completion.Completer` classes
from prompt_toolkit and the built-in :class:`rlcompleter.Completer` class
to aide us as well.

Auto-Suggestions
------------------
In addition, `prompt_toolkit` provides a class
:class:`prompt_toolkit.auto_suggest.AutoSuggestFromHistory` to give
completions in a similar manner to the fish shell.

.. automodule:: default_profile.startup.34_completion
   :synopsis: add new completions to the shell to speed up autocompletion.
   :members:
   :undoc-members:
   :show-inheritance:


`~default_profile.startup.35_lexer`
===========================================

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

.. automodule:: default_profile.startup.35_lexer
   :synopsis: Generate a lexer to provide syntax highlighting in the REPL.
   :members:
   :undoc-members:
   :show-inheritance:


`~default_profile.startup.36_ptutils`
===========================================

.. automodule:: default_profile.startup.36_ptutils
   :members:
   :undoc-members:
   :show-inheritance:
