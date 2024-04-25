import pytest
from pytest_unordered import unordered

from dependency_graph import (
    construct_dependency_graph,
    DependencyGraphGeneratorType,
    Language,
)


@pytest.fixture
def sample_retriever(python_repo_suite_path):
    return construct_dependency_graph(
        python_repo_suite_path / "cross_file_context",
        DependencyGraphGeneratorType.JEDI,
        Language.Python,
    ).as_retriever()


def test_get_cross_file_context(sample_retriever, python_repo_suite_path):
    cross_file_edge_list = sample_retriever.get_cross_file_context(
        python_repo_suite_path / "cross_file_context" / "main.py"
    )

    assert len(cross_file_edge_list) == 29
    context = [
        (
            edge[0].type.value,
            edge[0].name,
            edge[0].location.start_line,
            edge[0].location.start_column,
            edge[0].location.file_path.name,
            edge[2].relation.name,
            edge[1].name,
            edge[1].location.file_path.name,
        )
        for edge in cross_file_edge_list
    ]

    assert context == unordered(
        [
            ("class", "Bar", 5, 1, "b.py", "InstantiatedBy", "Foo.call", "main.py"),
            ("function", "bar", 1, 1, "b.py", "CalledBy", "Foo.call", "main.py"),
            ("function", "bar", 1, 1, "b.py", "ImportedBy", "main", "main.py"),
            ("class", "Bar", 5, 1, "b.py", "ImportedBy", "main", "main.py"),
            ("function", "baz", 1, 1, "c.py", "ImportedBy", "main", "main.py"),
            ("class", "Baz", 5, 1, "c.py", "ImportedBy", "main", "main.py"),
            ("class", "Baz", 5, 1, "c.py", "InstantiatedBy", "Foo.call", "main.py"),
            ("function", "baz", 1, 1, "c.py", "CalledBy", "Foo.call", "main.py"),
            ("class", "Bar", 5, 1, "b.py", "InstantiatedBy", "test", "main.py"),
            ("function", "bar", 1, 1, "b.py", "CalledBy", "test", "main.py"),
            ("function", "baz", 1, 1, "c.py", "ImportedBy", "main", "main.py"),
            ("class", "Baz", 5, 1, "c.py", "ImportedBy", "main", "main.py"),
            ("class", "Baz", 5, 1, "c.py", "InstantiatedBy", "test", "main.py"),
            ("function", "baz", 1, 1, "c.py", "CalledBy", "test", "main.py"),
            (
                "class",
                "Bar",
                5,
                1,
                "b.py",
                "InstantiatedBy",
                "bar_instance_in_module",
                "main.py",
            ),
            (
                "function",
                "use_test_in_main",
                9,
                1,
                "usage.py",
                "Calls",
                "test",
                "main.py",
            ),
            (
                "function",
                "Usage.__init__",
                18,
                5,
                "usage.py",
                "Instantiates",
                "Foo",
                "main.py",
            ),
            ("module", "usage", 1, 1, "usage.py", "Imports", "Foo", "main.py"),
            ("module", "usage", 1, 1, "usage.py", "Imports", "test", "main.py"),
            (
                "module",
                "usage",
                1,
                1,
                "usage.py",
                "Imports",
                "global_var_in_main",
                "main.py",
            ),
            (
                "function",
                "Usage.use_foo",
                21,
                5,
                "usage.py",
                "Calls",
                "Foo.call",
                "main.py",
            ),
            (
                "function",
                "Usage.use_test",
                24,
                5,
                "usage.py",
                "Calls",
                "test",
                "main.py",
            ),
            ("variable", "foo", 31, 1, "usage.py", "Instantiates", "Foo", "main.py"),
            ("module", "usage", 1, 1, "usage.py", "Calls", "Foo.call", "main.py"),
            ("module", "usage", 1, 1, "usage.py", "Calls", "test", "main.py"),
            (
                "function",
                "use_Foo_in_main",
                4,
                1,
                "usage.py",
                "Instantiates",
                "Foo",
                "main.py",
            ),
            (
                "function",
                "use_Foo_in_main",
                4,
                1,
                "usage.py",
                "Calls",
                "Foo.call",
                "main.py",
            ),
            (
                "statement",
                "global_var_in_main",
                14,
                11,
                "usage.py",
                "DefinedBy",
                "global_var_in_main",
                "main.py",
            ),
            (
                "statement",
                "global_var_in_main",
                28,
                15,
                "usage.py",
                "DefinedBy",
                "global_var_in_main",
                "main.py",
            ),
        ]
    )


def test_get_cross_file_definition_by_line(sample_retriever, python_repo_suite_path):
    cross_file_edge_list = sample_retriever.get_cross_file_definition_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 18
    )

    assert len(cross_file_edge_list) == 4
    context = [
        (
            edge[0].name,
            edge[2].relation.name,
            edge[1].type.value,
            edge[1].name,
            edge[1].location.file_path.name,
        )
        for edge in cross_file_edge_list
    ]

    assert context == unordered(
        [
            ("Foo.call", "Instantiates", "class", "Bar", "b.py"),
            ("Foo.call", "Calls", "function", "bar", "b.py"),
            ("main", "Imports", "class", "Bar", "b.py"),
            ("main", "Imports", "function", "bar", "b.py"),
        ]
    )

    cross_file_edge_list = sample_retriever.get_cross_file_definition_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 31
    )

    assert len(cross_file_edge_list) == 6
    context = [
        (
            edge[0].name,
            edge[2].relation.name,
            edge[1].type.value,
            edge[1].name,
            edge[1].location.file_path.name,
        )
        for edge in cross_file_edge_list
    ]

    assert context == unordered(
        [
            ("main", "Imports", "class", "Bar", "b.py"),
            ("main", "Imports", "function", "bar", "b.py"),
            ("main", "Imports", "class", "Baz", "c.py"),
            ("main", "Imports", "function", "baz", "c.py"),
            ("test", "Instantiates", "class", "Bar", "b.py"),
            ("test", "Calls", "function", "bar", "b.py"),
        ]
    )

    cross_file_edge_list = sample_retriever.get_cross_file_definition_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 43
    )

    assert len(cross_file_edge_list) == 6
    context = [
        (
            edge[0].type.value,
            edge[0].name,
            edge[0].location.file_path.name,
            edge[2].relation.name,
            edge[1].name,
        )
        for edge in cross_file_edge_list
    ]

    assert context == unordered(
        [
            ("module", "main", "main.py", "Imports", "Bar"),
            ("module", "main", "main.py", "Imports", "bar"),
            ("module", "main", "main.py", "Imports", "Baz"),
            ("module", "main", "main.py", "Imports", "baz"),
            ("module", "main", "main.py", "Imports", "Baz"),
            ("module", "main", "main.py", "Imports", "baz"),
        ]
    )


def test_get_cross_file_reference_by_line(sample_retriever, python_repo_suite_path):
    cross_file_edge_list = sample_retriever.get_cross_file_reference_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 18
    )

    assert len(cross_file_edge_list) == 3
    context = [
        (
            edge[0].name,
            edge[2].relation.name,
            edge[1].type.value,
            edge[1].get_text(),
            edge[1].location.file_path.name,
            edge[2].get_text(),
        )
        for edge in cross_file_edge_list
    ]
    assert context == unordered(
        [
            (
                "Foo.call",
                "CalledBy",
                "function",
                "def use_foo(self):\n        self.foo.call()",
                "usage.py",
                "call",
            ),
            (
                "Foo.call",
                "CalledBy",
                "module",
                "from main import Foo, test, global_var_in_main\n\n\ndef use_Foo_in_main():\n    foo = Foo()\n    foo.call()\n\n\ndef use_test_in_main():\n    test()\n\n\ndef use_global_var_in_main():\n    print(global_var_in_main)\n\n\nclass Usage:\n    def __init__(self):\n        self.foo = Foo()\n\n    def use_foo(self):\n        self.foo.call()\n\n    def use_test(self):\n        test()\n\n    def use_global_var_in_main(self):\n        print(global_var_in_main)\n\n\nfoo = Foo()\nfoo.call()\ntest()\n\n\nuse_Foo_in_main()\nuse_test_in_main()\nuse_global_var_in_main()\n\nusage = Usage()\nusage.use_foo()\nusage.use_test()\nusage.use_global_var_in_main()\n",
                "usage.py",
                "call",
            ),
            (
                "Foo.call",
                "CalledBy",
                "function",
                "def use_Foo_in_main():\n    foo = Foo()\n    foo.call()",
                "usage.py",
                "call",
            ),
        ]
    )

    cross_file_edge_list = sample_retriever.get_cross_file_reference_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 36
    )

    assert len(cross_file_edge_list) == 4
    context = [
        (
            edge[0].name,
            edge[2].relation.name,
            edge[1].type.value,
            edge[1].get_text(),
            edge[1].location.file_path.name,
            edge[2].get_text(),
        )
        for edge in cross_file_edge_list
    ]
    assert context == unordered(
        [
            (
                "test",
                "CalledBy",
                "function",
                "def use_test_in_main():\n    test()",
                "usage.py",
                "test",
            ),
            (
                "test",
                "ImportedBy",
                "module",
                "from main import Foo, test, global_var_in_main\n\n\ndef use_Foo_in_main():\n    foo = Foo()\n    foo.call()\n\n\ndef use_test_in_main():\n    test()\n\n\ndef use_global_var_in_main():\n    print(global_var_in_main)\n\n\nclass Usage:\n    def __init__(self):\n        self.foo = Foo()\n\n    def use_foo(self):\n        self.foo.call()\n\n    def use_test(self):\n        test()\n\n    def use_global_var_in_main(self):\n        print(global_var_in_main)\n\n\nfoo = Foo()\nfoo.call()\ntest()\n\n\nuse_Foo_in_main()\nuse_test_in_main()\nuse_global_var_in_main()\n\nusage = Usage()\nusage.use_foo()\nusage.use_test()\nusage.use_global_var_in_main()\n",
                "usage.py",
                "from main import Foo, test, global_var_in_main",
            ),
            (
                "test",
                "CalledBy",
                "function",
                "def use_test(self):\n        test()",
                "usage.py",
                "test",
            ),
            (
                "test",
                "CalledBy",
                "module",
                "from main import Foo, test, global_var_in_main\n\n\ndef use_Foo_in_main():\n    foo = Foo()\n    foo.call()\n\n\ndef use_test_in_main():\n    test()\n\n\ndef use_global_var_in_main():\n    print(global_var_in_main)\n\n\nclass Usage:\n    def __init__(self):\n        self.foo = Foo()\n\n    def use_foo(self):\n        self.foo.call()\n\n    def use_test(self):\n        test()\n\n    def use_global_var_in_main(self):\n        print(global_var_in_main)\n\n\nfoo = Foo()\nfoo.call()\ntest()\n\n\nuse_Foo_in_main()\nuse_test_in_main()\nuse_global_var_in_main()\n\nusage = Usage()\nusage.use_foo()\nusage.use_test()\nusage.use_global_var_in_main()\n",
                "usage.py",
                "test",
            ),
        ]
    )
