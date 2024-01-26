import pytest

from dependency_graph import (
    construct_dependency_graph,
    DependencyGraphGeneratorType,
    Language,
)
from dependency_graph.models.graph_data import (
    EdgeRelation,
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

    assert len(cross_file_edge_list) == 9
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

    assert context == [
        ("function", "bar", "b.py", "ImportedBy", "main"),
        ("function", "bar", "b.py", "CalledBy", "call"),
        ("class", "Bar", "b.py", "ImportedBy", "main"),
        ("class", "Bar", "b.py", "InstantiatedBy", "call"),
        ("class", "Bar", "b.py", "InstantiatedBy", "bar_instance_in_module"),
        ("function", "baz", "c.py", "ImportedBy", "main"),
        ("function", "baz", "c.py", "CalledBy", "call"),
        ("class", "Baz", "c.py", "ImportedBy", "main"),
        ("class", "Baz", "c.py", "InstantiatedBy", "call"),
    ]


def test_get_cross_file_context_by_line(sample_retriever, python_repo_suite_path):
    cross_file_edge_list = sample_retriever.get_cross_file_context_by_line(
        python_repo_suite_path / "cross_file_context" / "main.py", 16
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

    assert context == [
        ("function", "bar", "b.py", "CalledBy", "call"),
        ("function", "bar", "b.py", "ImportedBy", "main"),
        ("class", "Bar", "b.py", "InstantiatedBy", "call"),
        ("class", "Bar", "b.py", "ImportedBy", "main"),
    ]
