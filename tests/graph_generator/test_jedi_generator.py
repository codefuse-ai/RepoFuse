from pathlib import Path

import pytest

from dependency_graph.graph_generator.jedi_generator import JediDependencyGraphGenerator
from dependency_graph.models.graph_data import EdgeRelation
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository

repo_suite_path = Path(__file__).parent.parent / "code_example" / "python"


@pytest.fixture
def jedi_generator():
    return JediDependencyGraphGenerator(Language.Python)


def test_parent_relation(jedi_generator):
    repo_path = repo_suite_path / "parent_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    edges = D.get_related_edges(EdgeRelation.ParentOf)
    assert edges
    assert len(edges) == 4
    relations = [
        (edge[0].type, edge[0].name, edge[1].type, edge[1].name) for edge in edges
    ]
    assert relations == [
        ("module", "main", "class", "A"),
        ("module", "main", "function", "func"),
        ("class", "A", "function", "a"),
        ("function", "func", "function", "closure"),
    ]


def test_import_relation(jedi_generator):
    repo_path = repo_suite_path / "import_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    edges = D.get_related_edges(EdgeRelation.Imports)
    assert edges
    assert len(edges) == 5
    relations = [
        (edge[0].type, edge[0].name, edge[1].type, edge[1].name, edge[2].get_text())
        for edge in edges
    ]
    assert relations == [
        ("module", "main", "variable", "VAR_Y", "y.VAR_Y += 1"),
        ("module", "main", "function", "func_z", "from z import func_z"),
        ("module", "main", "module", "os", "import os"),
        ("module", "main", "class", "Path", "from pathlib import Path"),
        ("module", "main", "module", "y", "import y"),
    ]


def test_instantiate_relation(jedi_generator):
    repo_path = repo_suite_path / "instantiate_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    edges = D.get_related_edges(EdgeRelation.Instantiates)
    assert edges
    assert len(edges) == 8

    instantiations = [
        (
            edge[0].type.value,
            edge[0].name,
            edge[1].type.value,
            edge[1].name,
            edge[2].location.start_line,
        )
        for edge in edges
    ]

    assert instantiations == [
        ("function", "return_A", "class", "A", 11),
        ("function", "func_1", "class", "A", 16),
        ("variable", "global_class_a", "class", "A", 20),
        ("function", "func_2", "class", "A", 24),
        ("function", "func_2", "class", "B", 25),
        ("function", "func_2", "class", "B", 26),
        ("module", "main", "class", "B", 32),
        ("variable", "class_x", "class", "X", 37),
    ]


def test_call_relation(jedi_generator):
    repo_path = repo_suite_path / "call_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    call_graph = D.get_related_edges(EdgeRelation.Calls)

    assert call_graph
    assert len(call_graph) == 11

    calls = [
        (call[0].get_text(), call[1].get_text(), call[2].get_text())
        for call in call_graph
    ]

    assert calls == [
        (
            'def closure():\n            print("in A.b()")\n            self.a()',
            "def print(\n    *values: object,\n    sep: Optional[str] = ...,\n    end: Optional[str] = ...,\n    file: Optional[SupportsWrite[str]] = ...,\n    flush: bool = ...,\n) -> None: ...",
            "print",
        ),
        (
            'def closure():\n            print("in A.b()")\n            self.a()',
            'def a(self):\n        print("in A.a()")',
            "a",
        ),
        (
            'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()',
            'def closure():\n            print("in A.b()")\n            self.a()',
            "closure",
        ),
        (
            "def func():\n    A().a()\n    func_x()",
            'def a(self):\n        print("in A.a()")',
            "a",
        ),
        (
            "def func():\n    A().a()\n    func_x()",
            'def func_x():\n    print("in x")',
            "func_x",
        ),
        (
            None,
            'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()',
            "b",
        ),
        (None, "def func():\n    A().a()\n    func_x()", "func"),
        (
            None,
            'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()',
            "b",
        ),
        (None, "def func():\n    A().a()\n    func_x()", "func"),
        (
            'def a(self):\n        print("in A.a()")',
            "def print(\n    *values: object,\n    sep: Optional[str] = ...,\n    end: Optional[str] = ...,\n    file: Optional[SupportsWrite[str]] = ...,\n    flush: bool = ...,\n) -> None: ...",
            "print",
        ),
        (
            'def func_x():\n    print("in x")',
            "def print(\n    *values: object,\n    sep: Optional[str] = ...,\n    end: Optional[str] = ...,\n    file: Optional[SupportsWrite[str]] = ...,\n    flush: bool = ...,\n) -> None: ...",
            "print",
        ),
    ]
