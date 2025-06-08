import importlib
import sys

def preload_modules():
    """Ensure base modules are imported before reloading."""
    import pages.home
    import pages.load
    import pages.fact
    import utils.initialize
    import utils.cross_check

def reload_modules(prefixes=("pages", "utils")):
    preload_modules()
    for name in list(sys.modules.keys()):
        if any(name.startswith(p) for p in prefixes):
            try:
                importlib.reload(sys.modules[name])
            except Exception:
                pass
