.. currentmodule:: default_profile.startup.completions

===========================================
:mod:`~default_profile.startup.completions`
===========================================

Use both `jedi` and `prompt_toolkit` to aide `IPython` in generating completions.

The function from this module that will be easiest for end users to utilize is.:

.. function:: create_pt_completers()
   :noindex:

    Return a `~prompt_toolkit.completion.MergedCompleter` combining all of
    the public facing completers initialized in this module.
    This includes all of the concrete
    `prompt_toolkit.completion.Completers` as well as subclasses of the
    abstract base class.

This creates a combination of almost all of prompt_toolkits completion
mechanisms and combines them.

.. data:: combined_completers

    A ThreadedCompleter instantiated with a MergedCompleter that combines
    FuzzyWordCompleter, FuzzyCompleter, PathCompleter, WordCompleter
    and IPython's IPythonPTCompleter.

In addition, auto-suggestions are generated in a manner similar to fish from an
`prompt_toolkit.auto_suggest.AutoSuggestFromHistory` instance wrapped in
a `prompt_toolkit.auto_suggest.ThreadedAutoSuggest` instance as this
dramatically speeds the completions up.


See Also -- prompt_toolkit docs
===============================

:doc:`prompt_toolkit`
   More documentation on use of the prompt_toolkit API.


Completions API
===============

.. automodule:: default_profile.startup.completions
   :synopsis: Autocompletion for the REPL.
   :members:
   :undoc-members:
   :show-inheritance:

