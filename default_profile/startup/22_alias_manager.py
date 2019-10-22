class DynamicAliasManager(AliasManager):
    """Doesn't currently display info the way I want but it's a start."""
    shell = InteractiveShellABC()
    def __init__(self, ip=None, **kwargs):
        self.ip = get_ipython()
        super().__init__(shell=self.ip, **kwargs)
    def __repr__(self):
        return ''.format(reprlib.repr(self.aliases))
    def __iter__(self):
        return iter(self.aliases)
    def __call__(self):
        return self.init_aliases()
        
