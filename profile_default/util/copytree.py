import os
import shutil
from shutil import Error
import stat

class CopyTree:

    errors = []

    def __init__(self, src, dst, symlinks=False, ignore=None,
                 copy_function=shutil.copy2):
        self.src = src
        self.dst = dst
        self.symlinks = symlinks
        self.ignore = ignore
        self.copy_function= copy_function

    @property
    def destination_files(self):
        names = os.listdir(self.src)
        if self.ignore is not None:
            ignored_names = self.ignore(self.src, names)
        else:
            ignored_names = set()
        return ignored_names

    def _str_to_path(self):
        if hasattr(self.src, __fspath__):
            self.src = self.src.__fspath__()

        if hasattr(self.dst, __fspath__):
            self.dst = self.dst.__fspath__()

    def make_dest_dirs(self):
        try:
            os.makedirs(self.dst)
        except FileExistsError:
            pass

    def copytree(src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2):
        """Let's try and do `shutil.copytree()` a little better.

        First let's do everyone the courtesy of checking whether `src` and `dest`
        are pathlib.Path objects.
        """
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    if symlinks:
                        # We can't just leave it to `copy_function` because legacy
                        # code with a custom `copy_function` may rely on copytree
                        # doing the right thing.
                        os.symlink(linkto, dstname)
                        copystat(srcname, dstname, follow_symlinks=not symlinks)
                    else:
                        # ignore dangling symlink if the flag is on
                        if not os.path.exists(linkto) and ignore_dangling_symlinks:
                            continue
                        # otherwise let the copy occurs. copy2 will raise an error
                        if os.path.isdir(srcname):
                            copytree(srcname, dstname, symlinks, ignore,
                                     copy_function)
                        else:
                            copy_function(srcname, dstname)
                elif os.path.isdir(srcname):
                    copytree(srcname, dstname, symlinks, ignore, copy_function)
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    copy_function(srcname, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                errors.extend(err.args[0])
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
        try:
            copystat(src, dst)
        except OSError as why:
            # Copying file access times may fail on Windows
            if getattr(why, 'winerror', None) is None:
                errors.append((src, dst, str(why)))
        if errors:
            raise Error(errors)
        return dst
