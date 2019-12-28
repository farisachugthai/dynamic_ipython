#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from glob import glob
from shutil import Error, copytree, copystat


class CopyTree:
    """Rewrite :func:`shutil.copytree()`.

    Parameters
    ----------
    src : str (path-like)
        Directory tree to copy.
    dest : str (path-like)
        Directory to move tree to.
    symlinks : Bool, optional
        Whether to follow symlinks. Defaults to False.
    ignore : :func:`glob.glob()` pattern
        Files to not copy.
    copy_function : :mod:`shutil` copy function, optional
        Defaults to :func:`shutil.copy2`.

    Returns
    -------
    dst : TODO type
        TODO

    Notes
    -----
    Copying file access times may fail on Windows and if so ignore it.

    """

    errors = []

    def __init__(
        self, src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2
    ):
        self.src = src
        self.dst = dst
        self.symlinks = symlinks
        self.ignore = ignore
        self.copy_function = copy_function

    @property
    def destination_files(self):
        names = os.listdir(self.src)
        if self.ignore is not None:
            ignored_names = self.ignore(self.src, names)
        else:
            ignored_names = set()
        return ignored_names

    def _path_to_str(self):
        """Convert user provided :ref:`src` and :ref:dst` to str if necessary."""
        if hasattr(self.src, __fspath__):
            self.src = self.src.__fspath__()

        if hasattr(self.dst, __fspath__):
            self.dst = self.dst.__fspath__()

    def make_dest_dirs(self):
        """Create the dirs needed in the destination."""
        try:
            os.makedirs(self.dst)
        except FileExistsError:
            pass

    def copytree(self):
        """Let's try and do `shutil.copytree()` a little better.

        First let's do everyone the courtesy of checking whether `src` and `dest`
        are pathlib.Path objects.
        """
        for name in self.destination_files:
            if name in glob(self.ignore):
                continue
            srcname = os.path.join(self.src, name)
            dstname = os.path.join(self.dst, name)
            try:
                if os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    if self.symlinks:
                        # We can't just leave it to `copy_function` because legacy
                        # code with a custom `copy_function` may rely on copytree
                        # doing the right thing.
                        os.symlink(linkto, dstname)
                        copystat(srcname, dstname, follow_symlinks=not self.symlinks)
                    else:
                        # ignore dangling symlink if the flag is on
                        if not os.path.exists(linkto) and ignore_dangling_symlinks:
                            continue
                        # otherwise let the copy occurs. copy2 will raise an error
                        if os.path.isdir(srcname):
                            copytree(
                                srcname,
                                dstname,
                                self.symlinks,
                                glob(self.ignore),
                                self.copy_function,
                            )
                        else:
                            self.copy_function(srcname, dstname)
                elif os.path.isdir(srcname):
                    copytree(
                        srcname, dstname, self.symlinks, self.ignore, self.copy_function
                    )
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    self.copy_function(srcname, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                self.errors.extend(err.args[0])
            except OSError as why:
                self.errors.append((srcname, dstname, str(why)))
        try:
            copystat(self.src, self.dst)
        except OSError as why:
            if getattr(why, "winerror", None) is None:
                self.errors.append((self.src, self.dst, str(why)))
        if self.errors:  # do i need to do len(self.errors) > 0?
            raise Error(self.errors)
        return self.dst
