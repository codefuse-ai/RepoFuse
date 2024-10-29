import networkx as nx
import pytest
from fs.memoryfs import MemoryFS
from pytest_unordered import unordered

from dependency_graph import (
    construct_dependency_graph,
    GraphGeneratorType,
    VirtualPath,
)
from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.models.graph_data import (
    Node,
    Location,
    EdgeRelation,
    NodeType,
)
from dependency_graph.models.language import Language


@pytest.fixture
def sample_graph(python_repo_suite_path):
    return construct_dependency_graph(
        python_repo_suite_path,
        GraphGeneratorType.JEDI,
        Language.Python,
    )


@pytest.fixture
def sample_java_graph(java_repo_suite_path):
    return construct_dependency_graph(
        java_repo_suite_path,
        GraphGeneratorType.TREE_SITTER,
        Language.Java,
    )


def test_get_related_edges(sample_graph):
    edges = sample_graph.get_related_edges(
        EdgeRelation.Calls,
    )
    assert isinstance(edges, list)
    assert len(edges) > 0


def test_get_related_edges_by_node(sample_graph, python_repo_suite_path):
    edge_list = sample_graph.get_related_edges_by_node(
        Node(
            type=NodeType.MODULE,
            name="main",
            location=Location(
                file_path=python_repo_suite_path / "parent_relation" / "main.py",
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
    assert isinstance(graph.languages[0], Language)
    assert sample_graph.languages == graph.languages


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


def test_merge_graph(sample_graph: DependencyGraph, sample_java_graph: DependencyGraph):
    all_nodes = (
        sample_graph.graph.number_of_nodes() + sample_java_graph.graph.number_of_nodes()
    )
    all_edages = (
        sample_graph.graph.number_of_edges() + sample_java_graph.graph.number_of_edges()
    )
    sample_graph.compose_all(sample_java_graph)
    assert sample_graph.languages == unordered((Language.Python, Language.Java))
    assert sample_graph.graph.number_of_nodes() == all_nodes
    assert sample_graph.graph.number_of_edges() == all_edages


def test_merge_graph_with_same_node():
    mem_fs = MemoryFS()
    cpp_graph = DependencyGraph.from_dict(
        {
            "repo_path": "/unknown_repo",
            "languages": ["cpp"],
            "edges": [
                [
                    {
                        "type": "module",
                        "name": "grid.h",
                        "location": {
                            "file_path": VirtualPath(mem_fs, "/unknown_repo/grid.h"),
                            "start_line": 1,
                            "start_column": 1,
                            "end_line": 1,
                            "end_column": 18,
                        },
                    },
                    {
                        "type": "module",
                        "name": "cell.h",
                        "location": {
                            "file_path": VirtualPath(mem_fs, "/unknown_repo/cell.h"),
                            "start_line": 1,
                            "start_column": 1,
                            "end_line": 1,
                            "end_column": 1,
                        },
                    },
                    {
                        "relation": "Imports",
                        "location": {
                            "file_path": VirtualPath(mem_fs, "/unknown_repo/grid.h"),
                            "start_line": 1,
                            "start_column": 10,
                            "end_line": 1,
                            "end_column": 18,
                        },
                    },
                ],
            ],
        }
    )

    c_graph = DependencyGraph.from_dict(
        {
            "repo_path": "/unknown_repo",
            "languages": ["c"],
            "edges": [
                [
                    {
                        "type": "module",
                        "name": "grid.h",
                        "location": {
                            "file_path": VirtualPath(mem_fs, "/unknown_repo/grid.h"),
                            "start_line": 1,
                            "start_column": 1,
                            "end_line": 1,
                            "end_column": 18,
                        },
                    },
                    {
                        "type": "module",
                        "name": "cell.h",
                        "location": {
                            "file_path": VirtualPath(mem_fs, "/unknown_repo/cell.h"),
                            "start_line": 1,
                            "start_column": 1,
                            "end_line": 1,
                            "end_column": 1,
                        },
                    },
                    {
                        "relation": "Imports",
                        "location": {
                            "file_path": VirtualPath(mem_fs, "/unknown_repo/grid.h"),
                            "start_line": 1,
                            "start_column": 10,
                            "end_line": 1,
                            "end_column": 18,
                        },
                    },
                ],
            ],
        }
    )

    cpp_graph.compose_all(c_graph)
    assert cpp_graph.languages == unordered((Language.C, Language.CPP))
    assert cpp_graph.graph.number_of_nodes() == 2
    assert cpp_graph.graph.number_of_edges() == 1
