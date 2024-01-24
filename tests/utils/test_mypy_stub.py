from textwrap import dedent

from dependency_graph.utils.mypy_stub import generate_python_stub


def test_mypy_stub():
    code = dedent(
        '''
        class A:
            """test"""
            def __init__(self):
                self.a = 1
            
            def _private_method(self):
                pass

            def a(self, b):
                """method a"""
                print('hello world')

            def b(self):
                def closure():
                    self.a()
                closure()

        def test(a):
            return A().a()
        '''
    )

    actual = generate_python_stub(code)
    expected = (
        "class A:\n"
        "    def __init__(self) -> None: ...\n"
        "    def a(self, b) -> None: ...\n"
        "    def b(self) -> None: ...\n"
        "\n"
        "def test(a): ...\n"
    )
    assert actual == expected


def test_mypy_stub_can_include_docstrings():
    code = dedent(
        '''
        class A:
            """test"""
            def __init__(self):
                self.a = 1

            def _private_method(self):
                pass

            def a(self, b):
                """method a"""
                print('hello world')

            def b(self):
                def closure():
                    self.a()
                closure()

        def test(a):
            return A().a()
        '''
    )

    actual = generate_python_stub(code, include_docstrings=True)
    expected = (
        "class A:\n"
        '    """test"""\n'
        "    def __init__(self) -> None: ...\n"
        "    def a(self, b) -> None:\n"
        '        """method a"""\n'
        "    def b(self) -> None: ...\n"
        "\n"
        "def test(a): ...\n"
    )
    assert actual == expected


def test_mypy_stub_critical_error():
    code = dedent(
        """
        print "hello world"
        """
    )

    actual = generate_python_stub(code)
    expected = dedent(
        """
        print "hello world"
        """
    )
    assert actual == expected
