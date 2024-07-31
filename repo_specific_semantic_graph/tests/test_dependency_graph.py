from pathlib import Path

import pytest
import networkx as nx

from dependency_graph import (
    construct_dependency_graph,
    GraphGeneratorType,
)
from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.models.graph_data import (
    Node,
    Location,
    EdgeRelation,
    NodeType,
)
from dependency_graph.models.language import Language

repo_suite_path = Path(__file__).parent / "code_example" / "python"


@pytest.fixture
def sample_graph(python_repo_suite_path):
    return construct_dependency_graph(
        python_repo_suite_path,
        GraphGeneratorType.JEDI,
        Language.Python,
    )


def test_get_related_edges(sample_graph):
    edges = sample_graph.get_related_edges(
        EdgeRelation.Calls,
    )
    assert isinstance(edges, list)
    assert len(edges) > 0


def test_get_related_edges_by_node(sample_graph):
    edge_list = sample_graph.get_related_edges_by_node(
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
    assert isinstance(edge_list, list)
    assert len(edge_list) > 0
    assert isinstance(edge_list[0], tuple)
    assert isinstance(edge_list[0][0], Node)


def test_get_related_subgraph(sample_graph):
    subgraph = sample_graph.get_related_subgraph(EdgeRelation.Calls)
    assert isinstance(subgraph, DependencyGraph)
    assert len(subgraph.graph) > 0


def test_serialization_and_deserialization(sample_graph):
    json_str = sample_graph.to_json()
    graph = DependencyGraph.from_json(json_str)
    assert nx.utils.graphs_equal(sample_graph.graph, graph.graph)
    assert sample_graph.repo_path == graph.repo_path
    assert sample_graph.language == graph.language


def test_get_topological_sorting(sample_graph):
    sorted_nodes = list(sample_graph.get_topological_sorting())
    assert len(sorted_nodes) == sample_graph.graph.number_of_nodes()


def test_get_topological_sorting_to_deal_with_cyclic_import(python_repo_suite_path):
    """
    a -> b means a is imported by b
    For the following dependency graph:

      a.py <---- b.py
        /         ^
       v          |
      d.py ----> c.py
        |
        v
      e.py

     x.py <---- y.py <---- z.py
    """
    repo_path = python_repo_suite_path / "cyclic_import"
    graph = construct_dependency_graph(
        repo_path,
        GraphGeneratorType.TREE_SITTER,
        Language.Python,
    )
    sorted_nodes = list(graph.get_topological_sorting(EdgeRelation.ImportedBy))
    sorted_files = [
        str(node.location.file_path.relative_to(repo_path)) for node in sorted_nodes
    ]
    # The graph should be cyclic
    assert not nx.is_directed_acyclic_graph(graph.graph)
    assert sorted_files == [
        "z.py",
        "y.py",
        "x.py",
        "a.py",
        "d.py",
        "c.py",
        "b.py",
        "e.py",
    ]
