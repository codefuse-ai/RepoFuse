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

    assert len(cross_file_edge_list) == 27
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
            ("class", "Bar", "b.py", "InstantiatedBy", "call"),
            ("function", "bar", "b.py", "CalledBy", "call"),
            ("class", "Bar", "b.py", "ImportedBy", "main"),
            ("function", "bar", "b.py", "ImportedBy", "main"),
            ("function", "baz", "c.py", "ImportedBy", "main"),
            ("class", "Baz", "c.py", "ImportedBy", "main"),
            ("class", "Baz", "c.py", "InstantiatedBy", "call"),
            ("function", "baz", "c.py", "CalledBy", "call"),
            ("class", "Bar", "b.py", "InstantiatedBy", "test"),
            ("function", "bar", "b.py", "CalledBy", "test"),
            ("function", "baz", "c.py", "ImportedBy", "main"),
            ("class", "Baz", "c.py", "ImportedBy", "main"),
            ("class", "Baz", "c.py", "InstantiatedBy", "test"),
            ("function", "baz", "c.py", "CalledBy", "test"),
            ("class", "Bar", "b.py", "InstantiatedBy", "bar_instance_in_module"),
            ("function", "use_test_in_main", "usage.py", "Calls", "test"),
            ("function", "__init__", "usage.py", "Instantiates", "Foo"),
            ("module", "usage", "usage.py", "Imports", "Foo"),
            ("module", "usage", "usage.py", "Imports", "test"),
            ("module", "usage", "usage.py", "Imports", "global_var_in_main"),
            ("function", "use_foo", "usage.py", "Calls", "call"),
            ("function", "use_test", "usage.py", "Calls", "test"),
            ("variable", "foo", "usage.py", "Instantiates", "Foo"),
            ("module", "usage", "usage.py", "Calls", "call"),
            ("module", "usage", "usage.py", "Calls", "test"),
            ("function", "use_Foo_in_main", "usage.py", "Instantiates", "Foo"),
            ("function", "use_Foo_in_main", "usage.py", "Calls", "call"),
        ]
    )


def test_get_cross_file_definition_by_line(sample_retriever, python_repo_suite_path):
    cross_file_edge_list = sample_retriever.get_cross_file_definition_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 18
    )

    assert len(cross_file_edge_list) == 4
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
            ("class", "Bar", "b.py", "InstantiatedBy", "call"),
            ("function", "bar", "b.py", "CalledBy", "call"),
            ("class", "Bar", "b.py", "ImportedBy", "main"),
            ("function", "bar", "b.py", "ImportedBy", "main"),
        ]
    )

    cross_file_edge_list = sample_retriever.get_cross_file_definition_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 31
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
            ("class", "Bar", "b.py", "ImportedBy", "main"),
            ("function", "bar", "b.py", "ImportedBy", "main"),
            ("function", "baz", "c.py", "ImportedBy", "main"),
            ("class", "Baz", "c.py", "ImportedBy", "main"),
            ("class", "Bar", "b.py", "InstantiatedBy", "test"),
            ("function", "bar", "b.py", "CalledBy", "test"),
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
            ("class", "Baz", "c.py", "ImportedBy", "main"),
            ("function", "baz", "c.py", "ImportedBy", "main"),
            ("class", "Bar", "b.py", "ImportedBy", "main"),
            ("function", "bar", "b.py", "ImportedBy", "main"),
            ("class", "Baz", "c.py", "ImportedBy", "main"),
            ("function", "baz", "c.py", "ImportedBy", "main"),
        ]
    )


def test_get_cross_file_reference_by_line(sample_retriever, python_repo_suite_path):
    cross_file_edge_list = sample_retriever.get_cross_file_reference_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 18
    )

    assert len(cross_file_edge_list) == 6
    context = [
        (
            edge[0].type.value,
            edge[0].get_text(),
            edge[0].location.file_path.name,
            edge[2].relation.name,
            edge[1].name,
            edge[2].get_text(),
        )
        for edge in cross_file_edge_list
    ]
    assert context == unordered(
        [
            (
                "function",
                "def __init__(self):\n        self.foo = Foo()",
                "usage.py",
                "Instantiates",
                "Foo",
                "Foo",
            ),
            (
                "function",
                "def use_foo(self):\n        self.foo.call()",
                "usage.py",
                "Calls",
                "call",
                "call",
            ),
            ("variable", "foo = Foo()", "usage.py", "Instantiates", "Foo", "Foo"),
            (
                "module",
                "from main import Foo, test, global_var_in_main\n\n\ndef use_Foo_in_main():\n    foo = Foo()\n    foo.call()\n\n\ndef use_test_in_main():\n    test()\n\n\ndef use_global_var_in_main():\n    print(global_var_in_main)\n\n\nclass Usage:\n    def __init__(self):\n        self.foo = Foo()\n\n    def use_foo(self):\n        self.foo.call()\n\n    def use_test(self):\n        test()\n\n    def use_global_var_in_main(self):\n        print(global_var_in_main)\n\n\nfoo = Foo()\nfoo.call()\ntest()\n\n\nuse_Foo_in_main()\nuse_test_in_main()\nuse_global_var_in_main()\n\nusage = Usage()\nusage.use_foo()\nusage.use_test()\nusage.use_global_var_in_main()\n",
                "usage.py",
                "Calls",
                "call",
                "call",
            ),
            (
                "function",
                "def use_Foo_in_main():\n    foo = Foo()\n    foo.call()",
                "usage.py",
                "Instantiates",
                "Foo",
                "Foo",
            ),
            (
                "function",
                "def use_Foo_in_main():\n    foo = Foo()\n    foo.call()",
                "usage.py",
                "Calls",
                "call",
                "call",
            ),
        ]
    )

    cross_file_edge_list = sample_retriever.get_cross_file_reference_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 36
    )

    assert len(cross_file_edge_list) == 3
    context = [
        (
            edge[0].type.value,
            edge[0].get_text(),
            edge[0].location.file_path.name,
            edge[2].relation.name,
            edge[1].name,
            edge[2].get_text(),
        )
        for edge in cross_file_edge_list
    ]
    assert context == unordered(
        [
            (
                "function",
                "def use_test_in_main():\n    test()",
                "usage.py",
                "Calls",
                "test",
                "test",
            ),
            (
                "function",
                "def use_test(self):\n        test()",
                "usage.py",
                "Calls",
                "test",
                "test",
            ),
            (
                "module",
                "from main import Foo, test, global_var_in_main\n\n\ndef use_Foo_in_main():\n    foo = Foo()\n    foo.call()\n\n\ndef use_test_in_main():\n    test()\n\n\ndef use_global_var_in_main():\n    print(global_var_in_main)\n\n\nclass Usage:\n    def __init__(self):\n        self.foo = Foo()\n\n    def use_foo(self):\n        self.foo.call()\n\n    def use_test(self):\n        test()\n\n    def use_global_var_in_main(self):\n        print(global_var_in_main)\n\n\nfoo = Foo()\nfoo.call()\ntest()\n\n\nuse_Foo_in_main()\nuse_test_in_main()\nuse_global_var_in_main()\n\nusage = Usage()\nusage.use_foo()\nusage.use_test()\nusage.use_global_var_in_main()\n",
                "usage.py",
                "Calls",
                "test",
                "test",
            ),
        ]
    )
