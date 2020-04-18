#!#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest


class TokenTests(unittest.TestCase):
    """Tests tokenization. Start off with plain Python interpreter tests."""
    def test_backslash(self):
        # Backslash means line continuation:
        x = 1 + 1
        self.assertEqual(x, 2, "backslash for line continuation")

        # Backslash does not means continuation in comments :\
        x = 0
        self.assertEqual(x, 0, "backslash ending comment")

    def test_string_literals(self):
        x = ""
        y = ""
        self.assertTrue(len(x) == 0 and x == y)
        x = "'"
        y = "'"
        self.assertTrue(len(x) == 1 and x == y and ord(x) == 39)
        x = '"'
        y = '"'
        self.assertTrue(len(x) == 1 and x == y and ord(x) == 34)
        x = 'doesn\'t "shrink" does it'
        y = 'doesn\'t "shrink" does it'
        self.assertTrue(len(x) == 24 and x == y)
        x = 'does "shrink" doesn\'t it'
        y = 'does "shrink" doesn\'t it'
        self.assertTrue(len(x) == 24 and x == y)
        x = """
The "quick"
brown fox
jumps over
the 'lazy' dog.
"""
        y = "\nThe \"quick\"\nbrown fox\njumps over\nthe 'lazy' dog.\n"
        self.assertEqual(x, y)
        y = """
The "quick"
brown fox
jumps over
the 'lazy' dog.
"""
        self.assertEqual(x, y)
        y = "\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the 'lazy' dog.\n\
"

        self.assertEqual(x, y)
        y = "\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the 'lazy' dog.\n\
"

        self.assertEqual(x, y)

    def test_ellipsis(self):
        x = ...
        self.assertTrue(x is Ellipsis)
        self.assertRaises(SyntaxError, eval, ".. .")

    def test_eof_error(self):
        samples = ("def foo(", "\ndef foo(", "def foo(\n")
        for s in samples:
            with self.assertRaises(SyntaxError) as cm:
                compile(s, "<test>", "exec")
            self.assertIn("unexpected EOF", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
