from b import Bar, bar


def foo():
    print("Function foo in a")


class Foo:
    def __init__(self):
        print("Class Foo instantiated in a")

    def call(self):
        bar_instance = Bar()
        bar()
        foo()
        print(
            "--get_cross_file_context_by_line from here should not include the context below--"
        )
        from c import Baz, baz

        Baz()
        baz()


def test():
    bar_instance = Bar()
    bar()
    foo()
    print(
        "--get_cross_file_context_by_line from here should not include the context below--"
    )
    from c import Baz, baz

    Baz()
    baz()


if __name__ == "__main__":
    foo_instance_in_module = Foo()
    bar_instance_in_module = Bar()
    foo()
