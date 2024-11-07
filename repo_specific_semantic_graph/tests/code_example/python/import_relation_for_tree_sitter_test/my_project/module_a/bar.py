from module_a import foo  # Absolute import
from . import qux
from .. import module_b


def bar():
    print(foo.foo_function())
    print(qux.qux_function())
