from pathlib import Path

from dependency_graph import (
    construct_dependency_graph,
    DependencyGraphGeneratorType,
)
from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.models.graph_data import (
    Node,
    Location,
    EdgeRelation,
    NodeType,
)
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository

repo_suite_path = Path(__file__).parent / "code_example" / "python"


def test_get_related_edges():
    repository = Repository(repo_path=repo_suite_path, language=Language.Python)
    graph = construct_dependency_graph(repository, DependencyGraphGeneratorType.JEDI)
    edges = graph.get_related_edges(
        EdgeRelation.Calls,
    )
    assert isinstance(edges, list)
    assert len(edges) > 0


def test_get_related_nodes():
    repository = Repository(repo_path=repo_suite_path, language=Language.Python)
    graph = construct_dependency_graph(repository, DependencyGraphGeneratorType.JEDI)
    nodes = graph.get_related_nodes(
        Node(
            type=NodeType.MODULE,
            name="main",
            location=Location(
                file_path=repo_suite_path / "parent_relation" / "main.py",
                start_line=1,
                start_column=1,
                end_line=26,
                end_column=1,
            ),
        ),
        EdgeRelation.ParentOf,
    )
    assert isinstance(nodes, list)
    assert len(nodes) > 0


def test_get_related_subgraph():
    repository = Repository(repo_path=repo_suite_path, language=Language.Python)
    graph = construct_dependency_graph(repository, DependencyGraphGeneratorType.JEDI)
    subgraph = graph.get_related_subgraph(EdgeRelation.Calls)
    assert isinstance(subgraph, DependencyGraph)
    assert len(subgraph.graph) > 0
