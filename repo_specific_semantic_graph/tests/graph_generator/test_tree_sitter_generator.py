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
        ("module", "app", "module", "mathUtils", "mathUtils.js", "./mathUtils"),
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
        (
            "module",
            "main.php",
            "module",
            "greeting.php",
            "greeting.php",
            "'./greeting.php'",
        ),
        (
            "module",
            "main.php",
            "module",
            "config.php",
            "config.php",
            "'helpers/config.php'",
        ),
        (
            "module",
            "main.php",
            "module",
            "functions.php",
            "functions.php",
            "'helpers/functions.php'",
        ),
        (
            "module",
            "main.php",
            "module",
            "constants.php",
            "constants.php",
            "'helpers/constants.php'",
        ),
        (
            "module",
            "main.php",
            "module",
            "constants.php",
            "constants.php",
            "'helpers/constants.php'",
        ),
    ]


def test_ruby(tree_sitter_generator, ruby_repo_suite_path):
    repo_path = ruby_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Ruby)
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
        ("module", "another_helper", "module", "helper", "helper.rb", "'helper'"),
        ("module", "main", "module", "helper", "helper.rb", "'lib/helper'"),
        (
            "module",
            "main",
            "module",
            "another_helper",
            "another_helper.rb",
            "'lib/another_helper'",
        ),
        ("module", "main", "module", "greeting", "greeting.rb", "'greeting'"),
    ]


def test_c(tree_sitter_generator, c_repo_suite_path):
    repo_path = c_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.C)
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
        ("module", "main.c", "module", "utils.h", "utils.h", '"utils.h"'),
        (
            "module",
            "main.c",
            "module",
            "net_utils.h",
            "net_utils.h",
            '"net/net_utils.h"',
        ),
        (
            "module",
            "net_utils.c",
            "module",
            "net_utils.h",
            "net_utils.h",
            '"net/net_utils.h"',
        ),
        ("module", "utils.c", "module", "utils.h", "utils.h", '"utils.h"'),
    ]


def test_cpp(tree_sitter_generator, cpp_repo_suite_path):
    repo_path = cpp_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.CPP)
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
            "greetings.cpp",
            "module",
            "greetings.hpp",
            "greetings.hpp",
            '"greetings.hpp"',
        ),
        (
            "module",
            "main.cpp",
            "module",
            "greetings.hpp",
            "greetings.hpp",
            '"greetings.hpp"',
        ),
    ]


def test_go(tree_sitter_generator, go_repo_suite_path):
    repo_path = go_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Go)
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
        ("module", "main", "module", "utils", "utils.go", '"myproject/utils"'),
        (
            "module",
            "main",
            "module",
            "anotherpackage",
            "another.go",
            '"myproject/anotherpackage"',
        ),
        ("module", "main", "module", "utils", "utils.go", '"myproject/utils"'),
        ("module", "main", "module", "utils", "utils.go", '"myproject/utils"'),
    ]


def test_swift(tree_sitter_generator, swift_repo_suite_path):
    repo_path = swift_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Swift)
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
        ("module", "MyApp", "module", "Utilities", "Utilities.swift", "Utilities"),
        ("module", "MyApp", "module", "Other", "Foo.swift", "Other.greet"),
        ("module", "MyAppTests", "module", "MyApp", "Foo.swift", "MyApp"),
        ("module", "MyAppTests", "module", "MyApp", "main.swift", "MyApp"),
    ]


def test_rust(tree_sitter_generator, rust_repo_suite_path):
    repo_path = rust_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Rust)
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
            "main",
            "module",
            "sub_module",
            "sub_module.rs",
            "my_module::sub_module::sub_function",
        ),
        (
            "module",
            "main",
            "module",
            "helper",
            "helper.rs",
            "my_other_module::helper::helper_function",
        ),
        ("module", "main", "module", "foo", "foo.rs", "crate::foo::foo"),
    ]


def test_lua(tree_sitter_generator, lua_repo_suite_path):
    repo_path = lua_repo_suite_path
    repository = Repository(repo_path=repo_path, language=Language.Lua)
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
        ("module", "init", "module", "module1", "module1.lua", "'module1'"),
        ("module", "init", "module", "module2", "module2.lua", '"submodule.module2"'),
        ("module", "init", "module", "module3", "module3.lua", '"module3"'),
        ("module", "init", "module", "module4", "module4.lua", '"module4.lua"'),
    ]
