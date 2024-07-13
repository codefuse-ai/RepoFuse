from textwrap import dedent

from dependency_graph import construct_dependency_graph, EdgeRelation
from dependency_graph.graph_generator import GraphGeneratorType
from dependency_graph.models.language import Language
from dependency_graph.models.virtual_fs.virtual_repository import (
    VirtualRepository,
)


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
        ("bar", "print", "repo/src/a.py"),
        ("bar", "foo", "repo/src/a.py"),
        ("foo", "print", "repo/src/b.py"),
    ]
