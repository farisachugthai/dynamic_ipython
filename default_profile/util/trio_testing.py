#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Whoa!::

    In [15]: trio_traiging('base16.py')
    Out[15]: <async_generator object trio_traiging at 0x7f9471739310>

"""
import sys

try:
    from trio import run
except:
    from asyncio.runners import run

    trio = None
else:
    import trio


async def trio_traiging(filename):
    if trio is None:
        return
    async with await trio.open_file(filename) as f:
        async for line in f:
            print(line)
            # yield from line
            # apparently that's a no no
            yield line


if __name__ == "__main__":
    try:
        run(trio_traiging(sys.argv[1]))
    except IndexError:
        print("Give me a filename.")
