import importlib
import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import SourceFileLoader

from fs.base import FS


class VirtualFSLoader(SourceFileLoader):
    """
    A loader that uses a PyFilesystem instance to load modules
    """

    def __init__(self, fs: FS, fullname, path):
        super().__init__(fullname, path)
        self.fs = fs

    def __hash__(self):
        return hash(self.fs) ^ hash(self.name) ^ hash(self.path)

    def get_data(self, path):
        """Return the data from path as raw bytes."""
        return self.fs.readbytes(path)

    def get_source(self, fullname):
        return self.fs.readtext(self.path)


class VirtualFSFinder(MetaPathFinder):
    """
    A meta path finder that uses a PyFilesystem instance to find modules.
    It will loop through all paths in sys.path and try to find the module in the fs.
    """

    def __init__(self, fs: FS):
        self.fs = fs
        # Cache to avoid creating multiple loaders for the same module
        self.memory_loader_cache = {}

    def find_spec(self, fullname, path=None, target=None):
        # Transform module name to file path
        module_rel_path = f"{fullname.replace('.', '/')}.py"

        # Search through all paths in sys.path
        for p in sys.path:
            # Filter out non-existent sys path in the fs
            if not self.fs.exists(p):
                continue

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
