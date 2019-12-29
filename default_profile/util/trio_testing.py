"""

Whoa!::

    In [15]: trio_traiging('base16.py')
    Out[15]: <async_generator object trio_traiging at 0x7f9471739310>

"""
import sys
import trio


def trio_traiging(filename):
    async with await trio.open_file(filename) as f:
        async for line in f:
            print(line)
            yield from line


if __name__ == '__main__':
    try:
        trio.run(trio_traiging(sys.argv[1]))
    except IndexError:
        print('Give me a filename.')
