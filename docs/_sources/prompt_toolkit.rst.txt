Configuring Prompt Toolkit in IPython
=====================================

Here's the original implementation for pt_app.

This shows us where the entry point for prompt_toolkit is in IPython.

``ip.init_**`` gives a ton of
different places, seemingly to muck around.

.. code-block:: none

   Signature: ip.init_prompt_toolkit_cli()
   Docstring: <no docstring>
   Source:
       def init_prompt_toolkit_cli(self):
           if self.simple_prompt:
               # Fall back to plain non-interactive output for tests.
               # This is very limited.
               def prompt():
                   prompt_text = "".join(x[1] for x in self.prompts.in_prompt_tokens())
                   lines = [input(prompt_text)]
                   prompt_continuation = "".join(x[1] for x in self.prompts.continuation_prompt_tokens())
                   while self.check_complete('\n'.join(lines))[0] == 'incomplete':
                       lines.append( input(prompt_continuation) )
                   return '\n'.join(lines)
               self.prompt_for_code = prompt
               return

           # Set up keyboard shortcuts
           key_bindings = create_ipython_shortcuts(self)

           # Pre-populate history from IPython's history database
           history = InMemoryHistory()
           last_cell = u""
           for __, ___, cell in self.history_manager.get_tail(self.history_load_length,
                                                           include_latest=True):
               # Ignore blank lines and consecutive duplicates
               cell = cell.rstrip()
               if cell and (cell != last_cell):
                   history.append_string(cell)
                   last_cell = cell

           self._style = self._make_style_from_name_or_cls(self.highlighting_style)
           self.style = DynamicStyle(lambda: self._style)

           editing_mode = getattr(EditingMode, self.editing_mode.upper())

           self.pt_app = PromptSession(
                               editing_mode=editing_mode,
                               key_bindings=key_bindings,
                               history=history,
                               completer=IPythonPTCompleter(shell=self),
                               enable_history_search = self.enable_history_search,
                               style=self.style,
                               include_default_pygments_style=False,
                               mouse_support=self.mouse_support,
                               enable_open_in_editor=self.extra_open_editor_shortcuts,
                               color_depth=(ColorDepth.TRUE_COLOR if self.true_color else None),
                               **self._extra_prompt_options())

The `prompt toolkit tutorial`_ does a fairly thorough job of explaining how most
everything here works.

.. _`prompt toolkit tutorial`: https://prompt-toolkit.read-the-docs.com/prompts/

Where we come in is by taking the `self.pt_app` object and initializing an
instance of the module's class :class:`prompt_toolkit.key_bindings.KeyBindings()`
