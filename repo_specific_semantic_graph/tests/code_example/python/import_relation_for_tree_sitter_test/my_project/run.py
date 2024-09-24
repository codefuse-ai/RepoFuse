from module_a.foo import foo_function  # Absolute import
from module_a.submodule.bar import bar_function as bar_alias_func, bar_function_1
from module_b.baz import baz_function  # Absolute import

print(bar_alias_func())
print(bar_function_1())

print(foo_function())
print(baz_function())
