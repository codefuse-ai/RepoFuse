from ..module_a import foo
from ..module_a.submodule.bar import bar_function  # Absolute import
from ..module_a.submodule import *  # Wildcard import
from .quux import *

def baz_function():
    return foo.foo_function(), bar_function(), quux_function()
