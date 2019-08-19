=========
Debuggers
=========

Notes:

The module :mod:`IPython.core.debugger` didn't prove to be very fruitful at
first. There was an interesting example of :mod:`reprlib` however!::

     # The stdlib debugger internally uses a modified repr from the `repr`
     # module, that limits the length of printed strings to a hardcoded
     # limit of 30 characters.  That much trimming is too aggressive, let's
     # at least raise that limit to 80 chars, which should be enough for
     # most interactive uses.
     try:
         try:
             from reprlib import aRepr  # Py 3
         except ImportError:
             from repr import aRepr  # Py 2
         aRepr.maxstring = 80
     except:
         # This is only a user-facing convenience, so any error we encounter
         # here can be warned about but can be otherwise ignored.  These
         # printouts will tell us about problems if this API changes
         import traceback
         traceback.print_exc()


The real meat of what you're looking for was in :mod:`IPython.terminal.debugger`.

**class TerminalPdb(Pdb):**

That's honestly 99% of the way to exactly what anyone would want.

It even showed me a *simpler* and more effective way of setting the
prompt_toolkit attribute for |ip|!::

      self.pt_app = PromptSession(...)

I'll admit I'm a little at fault for simply binding any prompt_toolkit classes
I wanted to the |ip| instance instead of an actual
:class:`prompt_toolkit.PromptSession`.

But wow did they do this in a clever way!::

     self.pt_app = PromptSession(
         message=(lambda: PygmentsTokens(get_prompt_tokens())),
         editing_mode=getattr(EditingMode, self.shell.editing_mode.upper()),
         key_bindings=kb,
         history=self.shell.debugger_history,
         completer=self._ptcomp,
         enable_history_search=True,
         mouse_support=self.shell.mouse_support,
         complete_style=self.shell.pt_complete_style,
         style=self.shell.style,
         inputhook=self.shell.inputhook,
         color_depth=self.shell.color_depth,
     )

``editing_mode = getattr(EditingMode, self.shell.editing_mode.upper())``

seems too simple for something I've never thought of!

The initialization of the :class:`prompt_toolkit.PromptSession` class
happens in the method :ref:`IPython.terminal.debugger.TerminalPdb.pt_init`. 

It's a mighty unwieldy class, and it would do
a lot better if we simply sub-classed the
:ref:`IPython.terminal.debugger.TerminalPdb` class and then broke up that
method into like 20 separate and easily modifiable parts.
