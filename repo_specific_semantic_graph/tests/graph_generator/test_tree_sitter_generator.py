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


def test_python(tree_sitter_generator, python_repo_suite_path):
    repo_path = python_repo_suite_path / "import_relation_for_tree_sitter_test"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = tree_sitter_generator.generate(repository)
    edges = D.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 5
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
            "baz",
            "module",
            "foo",
            "foo.py",
            "from ..module_a import foo",
        ),
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
            "baz",
            "baz.py",
            "from module_b.baz import baz_function",
        ),
    ]


def test_java(tree_sitter_generator, java_repo_suite_path):
    repo_path = java_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Java)
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


def test_kotlin(tree_sitter_generator, kotlin_repo_suite_path):
    repo_path = kotlin_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Kotlin)
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
            "com.example.MainAbsolute",
            "module",
            "com.example.subpackage.Utility",
            "Utility.kt",
            "com.example.subpackage.Utility",
        ),
        (
            "module",
            "com.example.MainWildcard",
            "module",
            "com.example.subpackage.Utility",
            "Utility.kt",
            "com.example.subpackage",
        ),
    ]


def test_php(tree_sitter_generator, php_repo_suite_path):
    repo_path = php_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.PHP)
    D = tree_sitter_generator.generate(repository)
    edges = D.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 5
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
        ("module", "main", "module", "greeting", "greeting.php", "'./greeting.php'"),
        ("module", "main", "module", "config", "config.php", "'helpers/config.php'"),
        (
            "module",
            "main",
            "module",
            "functions",
            "functions.php",
            "'helpers/functions.php'",
        ),
        (
            "module",
            "main",
            "module",
            "constants",
            "constants.php",
            "'helpers/constants.php'",
        ),
        (
            "module",
            "main",
            "module",
            "constants",
            "constants.php",
            "'helpers/constants.php'",
        ),
    ]
