import logging

try:
    import sphinx
except (ImportError, ModuleNotFoundError):
    pass

try:
    import IPython
except (ImportError, ModuleNotFoundError):
    pass

try:
    import profile_default
except (ImportError, ModuleNotFoundError):
    pass

try:
    from profile_default import startup
except (ImportError, ModuleNotFoundError):
    pass
