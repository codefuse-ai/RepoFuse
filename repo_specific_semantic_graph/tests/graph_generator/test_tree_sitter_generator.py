import pytest

from dependency_graph import (
    TreeSitterDependencyGraphGenerator,
    Language,
    Repository,
    EdgeRelation,
)


@pytest.fixture
def tree_sitter_generator():
    return TreeSitterDependencyGraphGenerator(Language.Java)


def test_java(tree_sitter_generator, java_repo_suite_path):
    repo_path = java_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Java)
    D = tree_sitter_generator.generate(repository)
    edges = D.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 2
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
    ]
