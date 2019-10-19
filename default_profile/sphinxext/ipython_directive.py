# -*- coding: utf-8 -*-
"""Sphinx directive to support embedded IPython code.

IPython provides an extension for `Sphinx <http://www.sphinx-doc.org/>`_ to
highlight and run code.

This directive allows pasting of entire interactive IPython sessions, prompts
and all, and their code will actually get re-executed at doc build time, with
all prompts renumbered sequentially. It also allows you to input code as a pure
python input by giving the argument python to the directive. The output looks
like an interactive ipython section.

Here is an example of how the IPython directive can
**run** python code, at build time.

.. ipython::

   In [1]: 1+1

   In [1]: import datetime
      ...: datetime.datetime.now()

It supports IPython construct that plain
Python does not understand (like magics):

.. ipython::

   In [0]: import time

   In [0]: %timeit time.sleep(0.05)

This will also support top-level async when using IPython 7.0+

.. ipython::

   In [2]: import asyncio
      ...: print('before')
      ...: await asyncio.sleep(1)
      ...: print('after')


The namespace will persist across multiple code chucks, Let's define a variable:

.. ipython::

   In [0]: who = "World"

And now say hello:

.. ipython::

   In [0]: print('Hello,', who)

If the current section raises an exception, you can add the ``:okexcept:`` flag
to the current block, otherwise the build will fail.

.. ipython::
   :okexcept:

   In [1]: 1/0

IPython Sphinx directive module
===============================

To enable this directive, simply list it in your Sphinx ``conf.py`` file
(making sure the directory where you placed it is visible to sphinx, as is
needed for all Sphinx directives). For example, to enable syntax highlighting
and the IPython directive::

    extensions = ['IPython.sphinxext.ipython_console_highlighting',
                  'IPython.sphinxext.ipython_directive']

The IPython directive outputs code-blocks with the language 'ipython'. So
if you do not have the syntax highlighting extension enabled as well, then
all rendered code-blocks will be uncolored. By default this directive assumes
that your prompts are unchanged IPython ones, but this can be customized.
The configurable options that can be placed in conf.py are:

ipython_savefig_dir:
    The directory in which to save the figures. This is relative to the
    Sphinx source directory. The default is `html_static_path`.

ipython_rgxin:
    The compiled regular expression to denote the start of IPython input
    lines. The default is ``re.compile('In \\[(\\d+)\\]:\\s?(.*)\\s*')``. You
    shouldn't need to change this.

ipython_rgxout:
    The compiled regular expression to denote the start of IPython output
    lines. The default is ``re.compile('Out\\[(\\d+)\\]:\\s?(.*)\\s*')``. You
    shouldn't need to change this.

ipython_warning_is_error:
    [default to True]
    Oh. This must be :data:`block_parser.rgxin`. Wow.
    Fail the build if something unexpected happen, for example if a block raise
    an exception but does not have the `:okexcept:` flag. The exact behavior of
    what is considered strict, may change between the sphinx directive version.

.. caution:: ipython_warning_is_error

    [Defaults to True]

ipython_promptin:
    The string to represent the IPython input prompt in the generated rst.
    The default is ``'In [%d]:'``. This expects that the line numbers are used
    in the prompt.

ipython_promptout:
    The string to represent the IPython prompt in the generated rst. The
    default is ``'Out [%d]:'``. This expects that the line numbers are used
    in the prompt.

ipython_mplbackend:
    The string which specifies if the embedded Sphinx shell should import
    Matplotlib and set the backend. The value specifies a backend that is
    passed to `matplotlib.use()` before any lines in `ipython_execlines` are
    executed. If not specified in conf.py, then the default value of 'agg' is
    used. To use the IPython directive without matplotlib as a dependency, set
    the value to `None`.

.. warning::

    It may end up that matplotlib is still imported
    if the user specifies so in `ipython_execlines` or makes use of the
    `@savefig` pseudo decorator.

ipython_execlines:
    A list of strings to be exec'd in the embedded Sphinx shell. Typical
    usage is to make certain packages always available. Set this to an empty
    list if you wish to have no imports always available. If specified in
    ``conf.py`` as `None`, then it has the effect of making no imports available.

    If omitted from conf.py altogether, then the default value of:

        ['import numpy as np', 'import matplotlib.pyplot as plt']

    is used.

ipython_holdcount
    When the `@suppress` pseudo-decorator is used, the execution count can be
    incremented or not. The default behavior is to hold the execution count,
    corresponding to a value of `True`. Set this to `False` to increment
    the execution count after each suppressed command.

As an example, to use the IPython directive when `matplotlib` is not available,
one sets the backend to `None`::

    ipython_mplbackend = None

An example usage of the directive is:

.. code-block:: rst

    .. ipython::

        In [1]: x = 1

        In [2]: y = x**2

        In [3]: print(y)

See http://matplotlib.org/sampledoc/ipython_directive.html for additional
documentation.

Pseudo-Decorators
=================

Note: Only one decorator is supported per input. If more than one decorator
is specified, then only the last one is used.

In addition to the Pseudo-Decorators/options described at the above link,
several enhancements have been made. The directive will emit a message to the
console at build-time if code-execution resulted in an exception or warning.
You can suppress these on a per-block basis by specifying the :okexcept:
or :okwarning: options:

.. code-block:: rst

    .. ipython::
        :okexcept:
        :okwarning:

        In [1]: 1/0
        In [2]: # raise warning.

Now also contains a method for documenting traits.

.. :rst:directive::

    .. configtrait:: Application.log_datefmt

        Description goes here.

    Cross reference like this: :configtrait:`Application.log_datefmt`.


"""

# Authors
# =======
#
# - John D Hunter: original author.
# - Fernando Perez: refactoring, documentation, cleanups, port to 0.11.
# - VáclavŠmilauer <eudoxos-AT-arcig.cz>: Prompt generalizations.
# - Skipper Seabold, refactoring, cleanups, pure python addition

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# Stdlib
from io import StringIO
from typing import Any, Dict, List, Tuple
import ast
import atexit
import enum
import errno
import os
import pathlib
import re
import shutil
import sys
import tempfile
import warnings

# Third-party
from docutils.parsers.rst import directives
# from docutils.parsers.rst import Directive
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx import highlighting

# Our own
from traitlets.config import Config
from IPython import InteractiveShell
from IPython.core.profiledir import ProfileDir
from IPython.lib.lexers import IPyLexer

try:
    import matplotlib
except Exception:
    matplotlib = None


logger = logging.getLogger(__name__)


class TokenizedBlocks(enum.Enum):
    """TokenizedBlocks(enum.Enum).

    Subclasses the Enumeration class to create distinct global values.

    COMMENT : str
        The comment string.

    INPUT : ?
        the (DECORATOR, INPUT_LINE, REST) where
         DECORATOR: the input decorator (or None)
         INPUT_LINE: the input as string (possibly multi-line)
         REST : any stdout generated by the input line (not OUTPUT)

    OUTPUT : str
        The output string, possibly multi-line.

    Why was this in the `block_parser` docstring?

    """
    COMMENT = 0
    INPUT = 1
    OUTPUT = 2


# -----------------------------------------------------------------------------
# Functions and class declarations
# -----------------------------------------------------------------------------


def block_parser(part, rgxin, rgxout, fmtin, fmtout):
    """A parser for rst documents and IPython source code.

    Parameters
    ----------
    part : str
        A string of IPython text, comprised of at most one input,
        one output, comments, and blank lines.

    rgxin : probably an :class:`re.Pattern` of some kind from :mod:`re`.
    rgxout : wasn't documented. Actally I think it's those ipython_rgx* params
    fmtin :

    Returns
    -------
    blocks : list of 2 element tuples

    Notes
    -----
    The block parser parses the text into a list of 2-element tuples. I.E.:

      blocks = [ (TOKEN0, data0), (TOKEN1, data1), ...]

    where *TOKEN* is one of the attributes of `TokenizedBlocks`, namely
    :attr:`COMMENT`, :attr:`INPUT`, :attr:`OUTPUT`.

    """
    block = []
    lines = part.split('\n')
    N = len(lines)
    i = 0
    decorator = None
    while 1:

        if i == N:
            # nothing left to parse -- the last line
            break

        line = lines[i]
        i += 1
        line_stripped = line.strip()
        if line_stripped.startswith('#'):
            block.append((TokenizedBlocks.COMMENT, line))
            continue

        if line_stripped.startswith('@'):
            # Here is where we assume there is, at most, one decorator.
            # Might need to rethink this.
            decorator = line_stripped
            continue

        # does this look like an input line?
        # if rgxin
        regexin = rgxin
        matchin = rgxin.match(line)
        if matchin:
            lineno, inputline = int(matchin.group(1)), matchin.group(2)

            # the ....: continuation string
            continuation = '   %s:' % ''.join(['.'] * (len(str(lineno)) + 2))
            Nc = len(continuation)
            # input lines can continue on for more than one line, if
            # we have a '\' line continuation char or a function call
            # echo line 'print'.  The input line can only be
            # terminated by the end of the block or an output line, so
            # we parse out the rest of the input line if it is
            # multiline as well as any echo text

            rest = []
            while i < N:

                # look ahead; if the next line is blank, or a comment, or
                # an output line, we're done

                nextline = lines[i]
                matchout = rgxout.match(nextline)
                # print "nextline=%s, continuation=%s, starts=%s"%(nextline,
                # continuation, nextline.startswith(continuation))
                if matchout or nextline.startswith('#'):
                    break
                elif nextline.startswith(continuation):
                    # The default ipython_rgx* treat the space following the colon as optional.
                    # However, If the space is there we must consume it or code
                    # employing the cython_magic extension will fail to execute.
                    #
                    # This works with the default ipython_rgx* patterns,
                    # If you modify them, YMMV.
                    nextline = nextline[Nc:]
                    if nextline and nextline[0] == ' ':
                        nextline = nextline[1:]

                    inputline += '\n' + nextline
                else:
                    rest.append(nextline)
                i += 1

            block.append((TokenizedBlocks.INPUT, (decorator, inputline,
                                                  '\n'.join(rest))))
            continue

        # if it looks like an output line grab all the text to the end
        # of the block
        matchout = rgxout.match(line)
        if matchout:
            lineno, output = int(matchout.group(1)), matchout.group(2)
            if i < N - 1:
                output = '\n'.join([output] + lines[i:])

            block.append((TokenizedBlocks.OUTPUT, output))
            break

    return block


class EmbeddedSphinxShell:
    """An embedded IPython instance to run inside Sphinx.

    Attributes
    ----------
    cout : :class:`io.StringIO`
        Idk.

    IP : :class:`IPython.InteractiveShell`
        Global IPython instance.

    user_ns : dict
        I think it's a dict

    user_global_ns : dict

    tmp_profile_dir : str
        Return value of :func:`tempfile.mkdtemp`.
        Why not use a :class:`tempfile.TemporaryDirectory`.

    directive : ?
        Optionally, provide more detailed information to shell.
        this is assigned by the setup method of the IPython Directive
        to point at itself.
        So, you can access handy things at self.directive.state.

    _pyplot_imported = False
        On the first call to the `@savefig` decorator, we'll import
        `matplotlib.pyplot` as plt so we can make a call to the
        plt.gcf().savefig.

    """

    def __init__(self, exec_lines=None):
        """Initialize the *EmbeddedSphinxShell*.

        Parameters
        ----------
        exec_lines : list, Optional
            Lines to execute on startup.

        """
        self.cout = StringIO()

        if exec_lines is None:
            exec_lines = []

        # Create config object for IPython
        config = Config()
        config.HistoryManager.hist_file = ':memory:'
        config.InteractiveShell.autocall = False
        config.InteractiveShell.autoindent = False
        config.InteractiveShell.colors = 'NoColor'

        # create a profile so instance history isn't saved
        tmp_profile_dir = tempfile.mkdtemp(prefix='profile_')
        profname = 'auto_profile_sphinx_build'
        pdir = os.path.join(tmp_profile_dir, profname)
        profile = ProfileDir.create_profile_dir(pdir)

        # Create and initialize global ipython, but don't start its mainloop.
        # This will persist across different EmbeddedSphinxShell instances.
        IP = InteractiveShell.instance(config=config, profile_dir=profile)
        atexit.register(self.cleanup)

        # Store a few parts of IPython we'll need.
        self.IP = IP
        self.user_ns = self.IP.user_ns
        self.user_global_ns = self.IP.user_global_ns

        self.input = ''
        self.output = ''
        self.tmp_profile_dir = tmp_profile_dir

        self.is_verbatim = False
        self.is_doctest = False
        self.is_suppress = False

        # Optionally, provide more detailed information to shell.
        # this is assigned by the SetUp method of IPythonDirective
        # to point at itself.
        #
        # So, you can access handy things at self.directive.state
        self.directive = None

        # on the first call to the savefig decorator, we'll import
        # pyplot as plt so we can make a call to the plt.gcf().savefig
        self._pyplot_imported = False

        # Prepopulate the namespace.
        for line in exec_lines:
            self.process_input_line(line, store_history=False)

        # Saw this way further down and figured give it to the class.
        TAB = ' ' * 4

    def cleanup(self):
        """Teardown function that removes :attr:`tmp_profile_dir`."""
        try:
            shutil.rmtree(self.tmp_profile_dir, ignore_errors=True)
        except OSError as e:
            logger.error(e)


    def clear_cout(self):
        """Method of StringIO that calls seek and truncate? Idk."""
        self.cout.seek(0)
        self.cout.truncate(0)

    def process_input_line(self, line, store_history):
        """An unnecessary method that calls process_input_lines.

        Refer to 'process_input_lines' for signature.
        """
        return self.process_input_lines([line], store_history=store_history)

    def process_input_lines(self, lines, store_history=True):
        """Process the input, capturing :data:`sys.stdout`."""
        stdout = sys.stdout
        source_raw = '\n'.join(lines)
        try:
            sys.stdout = self.cout
            self.IP.run_cell(source_raw, store_history=store_history)
        finally:
            sys.stdout = stdout

    def process_image(self, decorator):
        """Processes the image directive.

        Build out an image directive like the following for example.

        .. code-block:: rst

            .. image:: somefile.png
                :width: 4in

        With an additional option like.

        .. :rst:directive:option:: savefig

            :savefig: somefile.png width=4in


        But literally why does this exist? Doesn't sphinx natively handle this?

        Parameters
        ----------
        decorator : str
            Honestly I'm not sure but I feel like it should be a bool
            indicating whether the `@savefig` decorator was used.

        """
        savefig_dir = self.savefig_dir
        source_dir = self.source_dir
        saveargs = decorator.split(' ')
        filename = saveargs[1]
        # insert relative path to image file in source
        # as absolute path for Sphinx
        # sphinx expects a posix path, even on Windows
        # TODO: This code!!!! So Sphinx expects a posix path, but when it returns
        # a POSIX path, windows can't find it and i haven't successfully used an image
        # directive since i started on NT again
        posix_path = pathlib.Path(savefig_dir, filename).as_posix()
        outfile = '/' + os.path.relpath(posix_path, source_dir)

        imagerows = ['.. image:: %s' % outfile]

        for kwarg in saveargs[2:]:
            arg, val = kwarg.split('=')
            arg = arg.strip()
            val = val.strip()
            imagerows.append('   :%s: %s' % (arg, val))

        image_file = os.path.basename(outfile)  # only return file name
        image_directive = '\n'.join(imagerows)
        return image_file, image_directive

    @staticmethod
    def status(output):
        """Print output in bold."""
        print('\033[1m{0}\033[0m'.format(output))

    def process_input(self, data, input_prompt, lineno):
        """Process data block for INPUT token.

        Callbacks for each type of token.

        Parameters
        ----------
        data : list?
            Unpacked to decorator, input, rest. Note no star?

            # The "rest" is the standard output of the input. This needs to be
            # added when in verbatim mode. If there is no "rest", then we don't
            # add it, as the new line will be added by the processed output.



        """
        decorator, input, rest = data
        image_file = None
        image_directive = None

        is_verbatim = decorator == '@verbatim' or self.is_verbatim
        is_doctest = (decorator is not None
                      and decorator.startswith('@doctest')) or self.is_doctest
        is_suppress = decorator == '@suppress' or self.is_suppress
        is_okexcept = decorator == '@okexcept' or self.is_okexcept
        is_okwarning = decorator == '@okwarning' or self.is_okwarning
        is_savefig = decorator is not None and decorator.startswith('@savefig')

        input_lines = input.split('\n')
        if len(input_lines) > 1:
            if input_lines[-1] != "":
                input_lines.append('')  # make sure there's a blank line
                # so splitter buffer gets reset

        continuation = '   %s:' % ''.join(['.'] * (len(str(lineno)) + 2))

        if is_savefig:
            image_file, image_directive = self.process_image(decorator)

        ret = []
        is_semicolon = False

        # Hold the execution count, if requested to do so.
        if is_suppress and self.hold_count:
            store_history = False
        else:
            store_history = True

        # Note: catch_warnings is not thread safe
        with warnings.catch_warnings(record=True) as ws:
            if input_lines[0].endswith(';'):
                is_semicolon = True
            # for i, line in enumerate(input_lines):
            # process the first input line
            if is_verbatim:
                self.process_input_lines([''])
                self.IP.execution_count += 1  # increment it anyway
            else:
                # only submit the line in non-verbatim mode
                self.process_input_lines(input_lines,
                                         store_history=store_history)

        if not is_suppress:
            for i, line in enumerate(input_lines):
                if i == 0:
                    formatted_line = '%s %s' % (input_prompt, line)
                else:
                    formatted_line = '%s %s' % (continuation, line)
                ret.append(formatted_line)

        if not is_suppress and len(rest.strip()) and is_verbatim:
            ret.append(rest)

        # Fetch the processed output. (This is not the submitted output.)
        self.cout.seek(0)
        processed_output = self.cout.read()
        if not is_suppress and not is_semicolon:
            ret.append(processed_output)
        elif is_semicolon:
            # Make sure there is a newline after the semicolon.
            ret.append('')

        if self.directive.state:
            filename = self.directive.state.document.current_source
            lineno = self.directive.state.document.current_line
        else:
            filename = "Unknown"
            lineno = 0

        # output any exceptions raised during execution to stdout
        # unless :okexcept: has been specified.
        if not is_okexcept and (("Traceback" in processed_output) or
                                ("SyntaxError" in processed_output)):
            s = "\nException in %s at block ending on line %s\n" % (filename,
                                                                    lineno)
            s += "Specify :okexcept: as an option in the ipython:: block to suppress this message\n"
            sys.stdout.write('\n\n>>>' + ('-' * 73))
            sys.stdout.write(s)
            sys.stdout.write(processed_output)
            sys.stdout.write('<<<' + ('-' * 73) + '\n\n')
            if self.warning_is_error:
                raise RuntimeError(
                    'Non Expected exception in `{}` line {}'.format(
                        filename, lineno))

        # output any warning raised during execution to stdout
        # unless :okwarning: has been specified.
        if not is_okwarning:
            for w in ws:
                s = "\nWarning in %s at block ending on line %s\n" % (filename,
                                                                      lineno)
                s += "Specify :okwarning: as an option in the ipython:: block to suppress this message\n"
                sys.stdout.write('\n\n>>>' + ('-' * 73))
                sys.stdout.write(s)
                sys.stdout.write(('-' * 76) + '\n')
                s = warnings.formatwarning(w.message, w.category, w.filename,
                                           w.lineno, w.line)
                sys.stdout.write(s)
                sys.stdout.write('<<<' + ('-' * 73) + '\n')
                if self.warning_is_error:
                    raise RuntimeError(
                        'Non Expected warning in `{}` line {}'.format(
                            filename, lineno))

        self.cout.truncate(0)
        return (ret, input_lines, processed_output, is_doctest, decorator,
                image_file, image_directive)

    def process_output(self, data, output_prompt, input_lines, output,
                       is_doctest, decorator, image_file):
        """Process data block for OUTPUT token.

        Recall: `data` is the submitted output, and `output` is the processed
        output from `input_lines`.

        Raises
        ------
        :exc:`RuntimeError`

        """
        if is_doctest and output is not None:

            found = output  # This is the processed output
            found = found.strip()
            submitted = data.strip()

            if self.directive is None:
                source = 'Unavailable'
                content = 'Unavailable'
            else:
                source = self.directive.state.document.current_source
                content = self.directive.content
                # Add tabs and join into a single string.
                content = '\n'.join([TAB + line for line in content])

            # Make sure the output contains the output prompt.
            ind = found.find(output_prompt)
            if ind < 0:
                e = ('output does not contain output prompt\n\n'
                     'Document source: {0}\n\n'
                     'Raw content: \n{1}\n\n'
                     'Input line(s):\n{TAB}{2}\n\n'
                     'Output line(s):\n{TAB}{3}\n\n')
                e = e.format(source,
                             content,
                             '\n'.join(input_lines),
                             repr(found),
                             TAB=TAB)
                raise RuntimeError(e)
            found = found[len(output_prompt):].strip()

            # Handle the actual doctest comparison.
            if decorator.strip() == '@doctest':
                # Standard doctest
                if found != submitted:
                    e = ('doctest failure\n\n'
                         'Document source: {0}\n\n'
                         'Raw content: \n{1}\n\n'
                         'On input line(s):\n{TAB}{2}\n\n'
                         'we found output:\n{TAB}{3}\n\n'
                         'instead of the expected:\n{TAB}{4}\n\n')
                    e = e.format(source,
                                 content,
                                 '\n'.join(input_lines),
                                 repr(found),
                                 repr(submitted),
                                 TAB=TAB)
                    raise RuntimeError(e)
            else:
                self.custom_doctest(decorator, input_lines, found, submitted)

        # When in verbatim mode, this holds additional submitted output
        # to be written in the final Sphinx output.
        # https://github.com/ipython/ipython/issues/5776
        out_data = []

        is_verbatim = decorator == '@verbatim' or self.is_verbatim
        if is_verbatim and data.strip():
            # Note that `ret` in `process_block` has '' as its last element if
            # the code block was in verbatim mode. So if there is no submitted
            # output, then we will have proper spacing only if we do not add
            # an additional '' to `out_data`. This is why we condition on
            # `and data.strip()`.

            # The submitted output has no output prompt. If we want the
            # prompt and the code to appear, we need to join them now
            # instead of adding them separately---as this would create an
            # undesired newline. How we do this ultimately depends on the
            # format of the output regex. I'll do what works for the default
            # prompt for now, and we might have to adjust if it doesn't work
            # in other cases. Finally, the submitted output does not have
            # a trailing newline, so we must add it manually.
            out_data.append("{0} {1}\n".format(output_prompt, data))

        return out_data

    def process_comment(self, data):
        """Process data fPblock for COMMENT token."""
        # Wtf is fPblock?
        if not self.is_suppress:
            return [data]

    def save_image(self, image_file):
        """Save the image file to disk."""
        self.ensure_pyplot()
        command = 'plt.gcf().savefig("%s")' % image_file
        # print 'SAVEFIG', command  # dbg
        self.process_input_line('bookmark ipy_thisdir', store_history=False)
        self.process_input_line('cd -b ipy_savedir', store_history=False)
        self.process_input_line(command, store_history=False)
        self.process_input_line('cd -b ipy_thisdir', store_history=False)
        self.process_input_line('bookmark -d ipy_thisdir', store_history=False)
        self.clear_cout()

    def process_block(self, block):
        """Process block from the block_parser and return a list of processed lines."""
        ret = []
        output = None
        input_lines = None
        lineno = self.IP.execution_count

        input_prompt = self.promptin % lineno
        output_prompt = self.promptout % lineno
        image_file = None
        image_directive = None

        found_input = False
        for token, data in block:
            if token == TokenizedBlocks.COMMENT:
                out_data = self.process_comment(data)
            elif token == TokenizedBlocks.INPUT:
                found_input = True
                (out_data, input_lines, output, is_doctest, decorator,
                 image_file,
                 image_directive) = self.process_input(data, input_prompt,
                                                       lineno)
            elif token == TokenizedBlocks.OUTPUT:
                if not found_input:
                    linenumber = 0
                    source = 'Unavailable'
                    content = 'Unavailable'
                    if self.directive:
                        linenumber = self.directive.state.document.current_line
                        source = self.directive.state.document.current_source
                        content = self.directive.content
                        # Add tabs and join into a single string.
                        content = '\n'.join([TAB + line for line in content])

                    e = ('\n\nInvalid block: Block contains an output prompt '
                         'without an input prompt.\n\n'
                         'Document source: {0}\n\n'
                         'Content begins at line {1}: \n\n{2}\n\n'
                         'Problematic block within content: \n\n{TAB}{3}\n\n')
                    e = e.format(source, linenumber, content, block, TAB=TAB)

                    # Write, rather than include in exception, since Sphinx
                    # will truncate tracebacks.
                    sys.stdout.write(e)
                    raise RuntimeError('An invalid block was detected.')
                out_data = \
                    self.process_output(data, output_prompt, input_lines,
                                        output, is_doctest, decorator,
                                        image_file)
                if out_data:
                    # Then there was user submitted output in verbatim mode.
                    # We need to remove the last element of `ret` that was
                    # added in `process_input`, as it is '' and would introduce
                    # an undesirable newline.
                    assert (ret[-1] == '')
                    del ret[-1]

            if out_data:
                ret.extend(out_data)

        # save the image files
        if image_file is not None:
            self.save_image(image_file)

        return ret, image_directive

    def ensure_pyplot(self):
        """Ensure that pyplot has been imported into the embedded IPython shell.

        Also, makes sure to set the backend appropriately if not set already.

        .. todo:: something with this function because it crashes the doc build all the time

        """
        # We are here if the @figure pseudo decorator was used. Thus, it's
        # possible that we could be here even if python_mplbackend were set to
        # `None`. That's also strange and perhaps worthy of raising an
        # exception, but for now, we just set the backend to 'agg'.

        if not self._pyplot_imported:
            if 'matplotlib.backends' not in sys.modules:
                # Then ipython_matplotlib was set to None but there was a
                # call to the @figure decorator (and ipython_execlines did
                # not set a backend).
                # raise Exception("No backend was set, but @figure was used!")
                import matplotlib
                matplotlib.use('agg')

            # Always import pyplot into embedded shell.
            self.process_input_line('import matplotlib.pyplot as plt',
                                    store_history=False)
            self._pyplot_imported = True

    def process_pure_python(self, content):
        """Content is a list of strings. It is unedited directive content.

        This runs it line by line in the InteractiveShell, prepends
        prompts as needed capturing stderr and stdout, then returns
        the content as a list as if it were IPython code.

        .. todo:: cyclomatic complexity is 17.

        """
        output = []
        savefig = False  # keep up with this to clear figure
        multiline = False  # to handle line continuation
        multiline_start = None
        fmtin = self.promptin

        ct = 0

        for lineno, line in enumerate(content):

            line_stripped = line.strip()
            if not len(line):
                output.append(line)
                continue

            # handle decorators
            if line_stripped.startswith('@'):
                output.extend([line])
                if 'savefig' in line:
                    savefig = True  # and need to clear figure
                continue

            # handle comments
            if line_stripped.startswith('#'):
                output.extend([line])
                continue

            # deal with lines checking for multiline
            continuation = u'   %s:' % ''.join(['.'] * (len(str(ct)) + 2))
            if not multiline:
                modified = u"%s %s" % (fmtin % ct, line_stripped)
                output.append(modified)
                ct += 1
                try:
                    ast.parse(line_stripped)
                    output.append(u'')
                except Exception as e:  # on a multiline
                    # let's at least note it somehow right?
                    logger.error(e)
                    multiline = True
                    multiline_start = lineno
            else:  # still on a multiline
                modified = u'%s %s' % (continuation, line)
                output.append(modified)

                # if the next line is indented, it should be part of multiline
                if len(content) > lineno + 1:
                    nextline = content[lineno + 1]
                    if len(nextline) - len(nextline.lstrip()) > 3:
                        continue
                try:
                    mod = ast.parse('\n'.join(content[multiline_start:lineno +
                                                      1]))
                    if isinstance(mod.body[0], ast.FunctionDef):
                        # check to see if we have the whole function
                        for element in mod.body[0].body:
                            if isinstance(element, ast.Return):
                                multiline = False
                    else:
                        output.append(u'')
                        multiline = False
                except Exception:
                    pass

            if savefig:  # clear figure if plotted
                self.ensure_pyplot()
                self.process_input_line('plt.clf()', store_history=False)
                self.clear_cout()
                savefig = False

        return output

    def custom_doctest(self, decorator, input_lines, found, submitted):
        """Perform a specialized doctest using a :ref:`custom_doctest`.

        Parameters
        ----------
        decorator : str
            arguments provided to `@doctest`
        input_lines : list
        found : I don't know
        submitted

        Returns
        -------
        Nothing? How? This is what I would've assumed we need to return.:

            doctest_handlers[doctest_type](self, args, input_lines, found, submitted)

        Raises
        ------
        :exc:`RuntimeError`

        """
        from .custom_doctests import doctest_handlers

        args = decorator.split()
        doctest_type = args[1]
        if doctest_type in doctest_handlers:
            doctest_handlers[doctest_type](self, args, input_lines, found, submitted)
        else:
            e = "Invalid option to @doctest: {0}".format(doctest_type)
            raise Exception(e)


class IPythonDirective(SphinxDirective):

    has_content = True
    required_arguments = 0
    optional_arguments = 4  # python, suppress, verbatim, doctest
    final_argumuent_whitespace = True
    option_spec = {
        'python': directives.unchanged,
        'suppress': directives.flag,
        'verbatim': directives.flag,
        'doctest': directives.flag,
        'okexcept': directives.flag,
        'okwarning': directives.flag
    }

    shell = None

    seen_docs = set()

    # def __init__(self):
    #     """Add an init method to this class."""
    #     super().__init__()

    def get_config_options(self):
        # contains sphinx configuration variables
        config = self.state.document.settings.env.config
        logger.debug('Config is :', config)

        config_options = {
            # get config variables to set figure output directory
            'savefig_dir': config.ipython_savefig_dir,
            'source_dir': self.state.document.settings.env.srcdir,
            # wait wtf do we ovverride the savefig dir?
            # savefig_dir = os.path.join(source_dir, savefig_dir)

            # get regex and prompt stuff
            'rgxin': re.compile(config.ipython_rgxin),
            'rgxout': re.compile(config.ipython_rgxout),
            'promptin': config.ipython_promptin,
            'promptout': config.ipython_promptout,
            'mplbackend': config.ipython_mplbackend,
            'exec_lines': config.ipython_execlines,
            'hold_count': config.ipython_holdcount,
            'warning_is_error': config.ipython_warning_is_error,
        }
        # are you allowed to do this? no.
        # return **config_options
        return config_options

    def setup(self):
        """Get configuration values."""
        (savefig_dir, source_dir, rgxin, rgxout, promptin, promptout,
         mplbackend, exec_lines, hold_count,
         warning_is_error) = self.get_config_options()

        try:
            os.makedirs(savefig_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        if self.shell is None:
            # We will be here many times.  However, when the
            # EmbeddedSphinxShell is created, its interactive shell member
            # is the same for each instance.

            if mplbackend and 'matplotlib.backends' not in sys.modules:
                import matplotlib
                matplotlib.use(mplbackend)

            # Must be called after (potentially) importing matplotlib and
            # setting its backend since exec_lines might import pylab.
            self.shell = EmbeddedSphinxShell(exec_lines)

            # Store IPython directive to enable better error messages
            self.shell.directive = self

        # reset the execution count if we haven't processed this doc
        # NOTE: this may be borked if there are multiple seen_doc tmp files
        # check time stamp?
        # Well this does bork things if you use autodoc. Changes the prompt #
        # halfway through a doc
        if not self.state.document.current_source in self.seen_docs:
            self.shell.IP.history_manager.reset()
            self.shell.IP.execution_count = 1
            self.seen_docs.add(self.state.document.current_source)

        # and attach to shell so we don't have to pass them around
        self.shell.rgxin = rgxin
        self.shell.rgxout = rgxout
        self.shell.promptin = promptin
        self.shell.promptout = promptout
        self.shell.savefig_dir = savefig_dir
        self.shell.source_dir = source_dir
        self.shell.hold_count = hold_count
        self.shell.warning_is_error = warning_is_error

        # setup bookmark for saving figures directory
        self.shell.process_input_line('bookmark ipy_savedir %s' % savefig_dir,
                                      store_history=False)
        self.shell.clear_cout()

        return rgxin, rgxout, promptin, promptout

    def teardown(self):
        # delete last bookmark
        self.shell.process_input_line('bookmark -d ipy_savedir',
                                      store_history=False)
        self.shell.clear_cout()

    def run(self):

        # TODO, any reason block_parser can't be a method of embeddable shell
        # then we wouldn't have to carry these around
        rgxin, rgxout, promptin, promptout = self.setup()

        options = self.options
        self.shell.is_suppress = 'suppress' in options
        self.shell.is_doctest = 'doctest' in options
        self.shell.is_verbatim = 'verbatim' in options
        self.shell.is_okexcept = 'okexcept' in options
        self.shell.is_okwarning = 'okwarning' in options

        # handle pure python code
        if 'python' in self.arguments:
            content = self.content
            self.content = self.shell.process_pure_python(content)

        # parts consists of all text within the ipython-block.
        # Each part is an input/output block.
        parts = '\n'.join(self.content).split('\n\n')

        lines = ['.. code-block:: ipython', '']
        figures = []

        for part in parts:
            block = block_parser(part, rgxin, rgxout, promptin, promptout)
            if len(block):
                rows, figure = self.shell.process_block(block)
                for row in rows:
                    lines.extend(
                        ['   {0}'.format(line) for line in row.split('\n')])

                if figure is not None:
                    figures.append(figure)
            else:
                message = 'Code input with no code at {}, line {}'\
                    .format(
                        self.state.document.current_source,
                        self.state.document.current_line)
                if self.shell.warning_is_error:
                    raise RuntimeError(message)
                else:
                    logger.warn(message)

        for figure in figures:
            lines.append('')
            lines.extend(figure.split('\n'))
            lines.append('')

        if len(lines) > 2:
            logger.debug('\n'.join(lines))
        else:
            # This has to do with input, not output. But if we comment
            # these lines out, then no IPython code will appear in the
            # final output.
            self.state_machine.insert_input(
                lines, self.state_machine.input_lines.source(0))

        # cleanup
        self.teardown()

        return []


def setup(app: "Sphinx") -> Dict[str, Any]:
    """Enable as a proper Sphinx directive.

    Add config values using the Sphinx api. Alternatively,
    I think we can add these into the namespace using docutils and their
    `directives`.

    Also add typing support.
    """
    app.add_directive('ipython', IPythonDirective)
    app.add_config_value('ipython_savefig_dir', 'savefig', 'env')
    # This needs to be changed to false so badly
    app.add_config_value('ipython_warning_is_error', False, 'env')
    app.add_config_value('ipython_rgxin',
                         re.compile(r'In \[(\d+)\]:\s?(.*)\s*'), 'env')
    app.add_config_value('ipython_rgxout',
                         re.compile(r'Out\[(\d+)\]:\s?(.*)\s*'), 'env')
    app.add_config_value('ipython_promptin', 'In [%d]:', 'env')
    app.add_config_value('ipython_promptout', 'Out[%d]:', 'env')

    # We could just let matplotlib pick whatever is specified as the default
    # backend in the matplotlibrc file, but this would cause issues if the
    # backend didn't work in headless environments. For this reason, 'agg'
    # is a good default backend choice.
    app.add_config_value('ipython_mplbackend', 'agg', 'env')

    # If the user sets this config value to `None`, then EmbeddedSphinxShell's
    # __init__ method will treat it as [].
    execlines = ['import numpy as np']
    if matplotlib:
        execlines.append('import matplotlib.pyplot as plt')
    app.add_config_value('ipython_execlines', execlines, 'env')

    app.add_config_value('ipython_holdcount', True, 'env')

    app.add_object_type('configtrait', 'configtrait', objname='Config option')


    # Let's see if i can get rid of ipython_console_highlighting as an extension by adding this in
    ipy2 = IPyLexer(python3=False)
    ipy3 = IPyLexer(python3=True)

    highlighting.lexers['ipython'] = ipy2
    highlighting.lexers['ipython2'] = ipy2
    highlighting.lexers['ipython3'] = ipy3

    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True}

    return metadata
