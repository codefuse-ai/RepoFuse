import importlib
import importlib.abc
import sys


class VirtualFSLoader(importlib.abc.Loader):
    """
    A loader that uses a PyFilesystem instance to load modules
    """

    def __init__(self, fs, module_name, module_path):
        self.fs = fs
        self.module_name = module_name
        self.module_path = module_path

    def create_module(self, spec):
        return None  # Use default module creation semantics

    def exec_module(self, module):
        # Add the file location to the module
        module.__file__ = self.module_path
        with self.fs.open(self.module_path, "r") as f:
            code = f.read()
        exec(code, module.__dict__)


class VirtualFSFinder(importlib.abc.MetaPathFinder):
    """
    A meta path finder that uses a PyFilesystem instance to find modules.
    It will loop through all paths in sys.path and try to find the module in the fs.
    """

    def __init__(self, fs):
        self.fs = fs
        # Cache to avoid creating multiple loaders for the same module
        self.memory_loader_cache = {}

    def find_spec(self, fullname, path, target=None):
        # Transform module name to file path
        module_rel_path = f"{fullname.replace('.', '/')}.py"

        # Search through all paths in sys.path
        for p in sys.path:
            module_abs_path = f"{p}/{module_rel_path}".replace("//", "/")
            if self.fs.exists(module_abs_path):
                # Use the cache to avoid re-creating MemoryFSLoader instances
                if fullname not in self.memory_loader_cache:
                    loader = VirtualFSLoader(self.fs, fullname, module_abs_path)
                    self.memory_loader_cache[fullname] = loader
                else:
                    loader = self.memory_loader_cache[fullname]

                return importlib.util.spec_from_loader(fullname, loader)

        return None
