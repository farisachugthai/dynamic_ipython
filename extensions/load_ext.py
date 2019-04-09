from IPython.core.magic import line_magic

@line_magic
def load_ext(module_str, shell=None):
    """Load an IPython extension by its module name."""
    if not module_str:
        raise UsageError('Missing module name.')
        res = self.shell.extension_manager.load_extension(module_str)
        if res == 'already loaded':
            print("The %s extension is already loaded. To reload it, use:" % module_str)
            print("%reload_ext", module_str)

        elif res == 'no load function':
           print("The %s module is not an IPython extension." % module_str)
