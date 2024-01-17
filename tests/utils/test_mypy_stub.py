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
    expected = dedent(
        '''
        class A:
            """test"""
            def __init__(self) -> None: ...
            def a(self, b) -> None: ...
            def b(self) -> None: ...
            
        def test(a): ...
        '''
    ).lstrip()
    assert actual == expected
