from main import Foo, test, global_var_in_main


def use_Foo_in_main():
    foo = Foo()
    foo.call()


def use_test_in_main():
    test()


def use_global_var_in_main():
    print(global_var_in_main)


class Usage:
    def __init__(self):
        self.foo = Foo()

    def use_foo(self):
        self.foo.call()

    def use_test(self):
        test()

    def use_global_var_in_main(self):
        print(global_var_in_main)


foo = Foo()
foo.call()
test()


use_Foo_in_main()
use_test_in_main()
use_global_var_in_main()

usage = Usage()
usage.use_foo()
usage.use_test()
usage.use_global_var_in_main()
