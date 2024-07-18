import pytest

from dependency_graph import (
    TreeSitterDependencyGraphGenerator,
    Language,
    Repository,
    EdgeRelation,
)


@pytest.fixture
def tree_sitter_generator():
    return TreeSitterDependencyGraphGenerator()


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


def test_c_sharp(tree_sitter_generator, c_sharp_repo_suite_path):
    repo_path = c_sharp_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.CSharp)
    D = tree_sitter_generator.generate(repository)
    edges = D.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 4
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
        ("module", "MyApp", "module", "MyApp.Models", "Person.cs", "MyApp.Models"),
        (
            "module",
            "MyApp",
            "module",
            "MyApp.Services",
            "GreetingService.cs",
            "MyApp.Services",
        ),
        ("module", "MyApp", "module", "MyLibrary", "MathLibrary.cs", "MyLibrary"),
        (
            "module",
            "MyApp.Services",
            "module",
            "MyApp.Models",
            "Person.cs",
            "MyApp.Models",
        ),
    ]


def test_javascript(tree_sitter_generator, javascript_repo_suite_path):
    repo_path = javascript_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.JavaScript)
    D = tree_sitter_generator.generate(repository)
    edges = D.get_related_edges(EdgeRelation.Imports)
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
        ("module", "index", "module", "utilA", "utilA.js", "./utils/utilA"),
        ("module", "index", "module", "utilB", "utilB.js", "./utils/utilB"),
        (
            "module",
            "index",
            "module",
            "Component",
            "Component.js",
            "./components/Component",
        ),
    ]


def test_typescript(tree_sitter_generator, typescript_repo_suite_path):
    repo_path = typescript_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.TypeScript)
    D = tree_sitter_generator.generate(repository)
    edges = D.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 4
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
        ("module", "index", "module", "index", "index.ts", "./utils"),
        ("module", "index", "module", "another", "another.ts", "./utils/another"),
        ("module", "index", "module", "service", "service.ts", "./services/service"),
        ("module", "service", "module", "index", "index.ts", "../utils"),
    ]
