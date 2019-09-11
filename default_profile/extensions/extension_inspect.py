<<<<<<< Updated upstream
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=======================
PrettyColorfulInspector
=======================

An IPython magic function to pretty-print objects with syntax highlighting.

Updated to also pretty print the object's ``__dict__`` if it's available.

See, "Defining your own magics":

<http://ipython.org/ipython-doc/stable/interactive/reference.html#defining-your-own-magics>

For more on Pygments:

See Also
---------
pygments

`http://pygments.org/docs/quickstart/`


Usage
-----

Place this file in your IPython startup directory. The default location is:

    ~/.ipython/profile_default/startup/

NOTE for Django: Since django uses an embedded IPython shell, it may not
load your default IPython profile. You'll need to run::

    %run ~/.ipython/profile_default/startup/ipython_magic_function_inspector.py

License
-------
Original copyright (c) 2014, Brad Montgomery <brad@bradmontgomery.net>
Updated copyright (c) 2016, Brian Bugh
Released under the MIT License.
http://opensource.org/licenses/MIT

"""
from pprint import pformat

from IPython import get_ipython
from IPython.core.magic import Magics, magics_class, line_magic

from pygments import highlight
from pygments.formatters import Terminal256Formatter  # Or TerminalFormatter
from pygments.lexers import PythonLexer


@magics_class
class PrettyColorfulInspector(Magics):
    """Implementation for a magic function that inpects a given python object.

    The extension then prints a syntax-highlighted and pretty-printed
    version of the provided object.
    """

    @line_magic
    def i(self, line):
        self.inspect(line)

    @line_magic
    def inspect(self, line):
        if line:
            # Use Pygments to do syntax highlighting
            lexer = PythonLexer()
            formatter = Terminal256Formatter()

            # evaluate the line to get a python object
            python_object = self.shell.ev(line)

            # Pretty Print/Format the object
            formatted_object = pformat(python_object)

            # Print the output, but don't return anything (othewise, we'd
            # potentially get a wall of color-coded text.
            print(highlight(formatted_object, lexer, formatter).strip())

            try:
                formatted_dict = pformat(python_object.__dict__)
                print(highlight(formatted_dict, lexer, formatter).strip())
            except:
                pass


# Register with IPython
ip = get_ipython()
ip.register_magics(PrettyColorfulInspector)
||||||| merged common ancestors
=======
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=======================
PrettyColorfulInspector
=======================
.. module:: prettycolorfulinspector

:URL: https://gist.githubusercontent.com/bbugh/449f46ebb936083494556301e0ce579c/raw/e5d34c227c9b8b8ac941724938b987eddb8639fc/ipython_magic_function_inspector.py

An IPython magic function to pretty-print objects with syntax highlighting.

Updated to also pretty print the object's __dict__ if it's available.

See, "Defining your own magics":

http://ipython.org/ipython-doc/stable/interactive/reference.html#defining-your-own-magics

For more on Pygments:

http://pygments.org/docs/quickstart/

Usage
-----
Place this file in your IPython startup directory. The default location is::
    ~/.ipython/profile_default/startup/

NOTE for Django: Since django uses an embedded IPython shell, it may not
load your default IPython profile. You'll need to run:

    %run ~/.ipython/profile_default/startup/ipython_magic_function_inspector.py

License
-------
Original copyright (c) 2014, Brad Montgomery <brad@bradmontgomery.net>
Updated copyright (c) 2016, Brian Bugh
Released under the MIT License.
http://opensource.org/licenses/MIT

"""
from __future__ import print_function  # doubt this is relevant IPython is 3.5+ only

from IPython.core.magic import Magics, magics_class, line_magic
from pprint import pformat
from pygments import highlight
from pygments.formatters import Terminal256Formatter  # Or TerminalFormatter
from pygments.lexers import PythonLexer


@magics_class
class PrettyColorfulInspector(Magics):
    """Implementation for a magic function that inpects a given python object.

    The extension then prints a syntax-highlighted and pretty-printed
    version of the provided object.
    """

    @line_magic
    def i(self, line):
        self.inspect(line)

    @line_magic
    def inspect(self, line):
        if line:
            # Use Pygments to do syntax highlighting
            lexer = PythonLexer()
            formatter = Terminal256Formatter()

            # evaluate the line to get a python object
            python_object = self.shell.ev(line)

            # Pretty Print/Format the object
            formatted_object = pformat(python_object)

            # Print the output, but don't return anything (othewise, we'd
            # potentially get a wall of color-coded text.
            print(highlight(formatted_object, lexer, formatter).strip())

            try:
                formatted_dict = pformat(python_object.__dict__)
                print(highlight(formatted_dict, lexer, formatter).strip())
            except:
                pass


# Register with IPython
ip = get_ipython()
ip.register_magics(PrettyColorfulInspector)
>>>>>>> Stashed changes
