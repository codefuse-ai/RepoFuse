from textwrap import dedent

from dependency_graph import construct_dependency_graph, EdgeRelation
from dependency_graph.graph_generator import GraphGeneratorType
from dependency_graph.models.language import Language
from dependency_graph.models.virtual_fs.virtual_repository import VirtualRepository


def test_construct_jedi_graph_on_virtual_repo():
    dependency_graph_generator = GraphGeneratorType.JEDI
    repo = VirtualRepository(
        "repo",
        Language.Python,
        [
            (
                "src/a.py",
                dedent(
                    """
                    from b import foo
                    
                    def bar():
                        print("hello")
                        foo()
                    """
                ),
            ),
            (
                "src/b.py",
                dedent(
                    """
                    def foo():
                        print("hello")
                    """
                ),
            ),
            (
                "src/c.py",
                dedent(
                    """
                    from pkg_not_exist import module
                    """
                ),
            ),
        ],
    )
    graph = construct_dependency_graph(repo, dependency_graph_generator)
    call_graph = graph.get_related_edges(EdgeRelation.Calls)
    assert call_graph
    assert len(call_graph) == 3

    calls = [
        (call[0].name, call[1].name, str(call[2].location.file_path))
        for call in call_graph
    ]

    assert calls == [
        ("bar", "print", "/repo/src/a.py"),
        ("bar", "foo", "/repo/src/a.py"),
        ("foo", "print", "/repo/src/b.py"),
    ]


def test_construct_tree_sitter_graph_on_virtual_repo(java_repo_suite_path):
    dependency_graph_generator = GraphGeneratorType.TREE_SITTER
    virtual_files = [
        (str(f.relative_to(java_repo_suite_path)), f.read_text())
        for f in java_repo_suite_path.rglob("*.java")
    ]
    repo = VirtualRepository(
        "repo",
        Language.Java,
        virtual_files,
    )

    graph = construct_dependency_graph(repo, dependency_graph_generator)
    edges = graph.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 3
    relations = [
        (
            edge[0].type.value,
            edge[0].name,
            edge[1].type.value,
            edge[1].name,
            edge[1].location.file_path.name,
            edge[2].get_text(),
        )
        for edge in edges
    ]
    assert relations == [
        (
            "module",
            "com.example.main.Main",
            "module",
            "com.example.util.Greetings",
            "Greetings.java",
            "com.example.util.Greetings",
        ),
        (
            "module",
            "com.example.main.Main",
            "module",
            "com.example.models.User",
            "User.java",
            "com.example.models.User",
        ),
        (
            "module",
            "com.example.main.MainWithStarImport",
            "module",
            "com.example.models.User",
            "User.java",
            "com.example.models",
        ),
    ]


def test_construct_tree_sitter_graph_on_python_virtual_repo(python_repo_suite_path):
    repo_path = python_repo_suite_path / "import_relation_for_tree_sitter_test"
    dependency_graph_generator = GraphGeneratorType.TREE_SITTER
    virtual_files = [
        (str(f.relative_to(repo_path)), f.read_text()) for f in repo_path.rglob("*.py")
    ]
    repo = VirtualRepository(
        "repo",
        Language.Python,
        virtual_files,
    )

    graph = construct_dependency_graph(repo, dependency_graph_generator)
    edges = graph.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 7
    relations = [
        (
            edge[0].type.value,
            edge[0].name,
            edge[1].type.value,
            edge[1].name,
            edge[1].location.file_path.name,
            edge[2].get_text(),
        )
        for edge in edges
    ]
    assert relations == [
        ("module", "bar", "module", "foo", "foo.py", "from module_a import foo"),
        ("module", "baz", "module", "foo", "foo.py", "from ..module_a import foo"),
        (
            "module",
            "baz",
            "module",
            "bar",
            "bar.py",
            "from ..module_a.submodule.bar import bar_function",
        ),
        (
            "module",
            "baz",
            "module",
            "__init__",
            "__init__.py",
            "from ..module_a.submodule import *",
        ),
        (
            "module",
            "run",
            "module",
            "foo",
            "foo.py",
            "from module_a.foo import foo_function",
        ),
        (
            "module",
            "run",
            "module",
            "bar",
            "bar.py",
            "from module_a.submodule.bar import bar_function as bar_alias_func, bar_function_1",
        ),
        (
            "module",
            "run",
            "module",
            "baz",
            "baz.py",
            "from module_b.baz import baz_function",
        ),
    ]
