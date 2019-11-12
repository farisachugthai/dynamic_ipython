""" Simply gonna jot this down fast.

Sorry for the sloppiness
"""
import sys
from inspect import getdoc

from prompt_toolkit.shortcuts import print_formatted_text as print


if __name__ == "__main__":
    _, *args = sys.argv[:]
    if len(args) > 0:
        print(getdoc(*args))
    else:
        sys.exit('Need to provide an argument.')
