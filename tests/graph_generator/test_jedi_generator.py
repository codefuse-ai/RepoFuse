import pytest
from pytest_unordered import unordered

from dependency_graph.graph_generator.jedi_generator import JediDependencyGraphGenerator
from dependency_graph.models.graph_data import EdgeRelation
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


@pytest.fixture
def jedi_generator():
    return JediDependencyGraphGenerator(Language.Python)


def test_parent_relation(jedi_generator, python_repo_suite_path):
    repo_path = python_repo_suite_path / "parent_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    edges = D.get_related_edges(EdgeRelation.ParentOf)
    assert edges
    assert len(edges) == 4
    relations = [
        (edge[0].type.value, edge[0].name, edge[1].type.value, edge[1].name)
        for edge in edges
    ]
    assert relations == [
        ("module", "main", "class", "A"),
        ("module", "main", "function", "func"),
        ("class", "A", "function", "A.a"),
        ("function", "func", "function", "closure"),
    ]


def test_import_relation(jedi_generator, python_repo_suite_path):
    repo_path = python_repo_suite_path / "import_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

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
        ("module", "main", "variable", "VAR_Y", "y.py", "y.VAR_Y += 1"),
        ("module", "main", "function", "func_z", "z.py", "from z import func_z"),
        ("module", "main", "module", "os", "os.py", "import os"),
        ("module", "main", "class", "Path", "pathlib.py", "from pathlib import Path"),
        ("module", "main", "module", "y", "y.py", "import y"),
    ]


def test_instantiate_relation(jedi_generator, python_repo_suite_path):
    repo_path = python_repo_suite_path / "instantiate_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    edges = D.get_related_edges(EdgeRelation.Instantiates)
    assert edges
    assert len(edges) == 13

    instantiations = [
        (
            edge[0].type.value,
            edge[0].name,
            edge[1].type.value,
            edge[1].name,
            edge[1].location.file_path.name,
            edge[2].location.start_line,
        )
        for edge in edges
    ]

    assert instantiations == unordered(
        [
            ("function", "B.return_A", "class", "A", "main.py", 14),
            ("function", "B.return_A", "class", "X", "x.py", 15),
            ("function", "func_1", "class", "A", "main.py", 20),
            ("function", "func_1", "class", "X", "x.py", 21),
            ("variable", "global_class_a", "class", "A", "main.py", 25),
            ("function", "func_2", "class", "B", "main.py", 30),
            ("function", "func_2", "class", "B", "main.py", 31),
            ("module", "main", "class", "B", "main.py", 37),
            ("variable", "class_x", "class", "X", "x.py", 42),
            ("variable", "global_class_b", "class", "A", "main.py", 45),
            ("variable", "global_class_b", "class", "B", "main.py", 47),
            ("module", "main", "class", "A", "main.py", 54),
            ("module", "main", "class", "B", "main.py", 55),
        ]
    )


def test_call_relation(jedi_generator, python_repo_suite_path):
    repo_path = python_repo_suite_path / "call_relation"
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
            'from x import func_x\n\n\nclass A:\n    def a(self):\n        print("in A.a()")\n\n    def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()\n\n\ndef func():\n    A().a()\n    func_x()\n\n\nglobal_var_1 = A().b()\nglobal_var_2 = func()\n\nif __name__ == "__main__":\n    A().b()\n    func()\n',
            'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()',
            "b",
        ),
        (
            'from x import func_x\n\n\nclass A:\n    def a(self):\n        print("in A.a()")\n\n    def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()\n\n\ndef func():\n    A().a()\n    func_x()\n\n\nglobal_var_1 = A().b()\nglobal_var_2 = func()\n\nif __name__ == "__main__":\n    A().b()\n    func()\n',
            "def func():\n    A().a()\n    func_x()",
            "func",
        ),
        (
            'from x import func_x\n\n\nclass A:\n    def a(self):\n        print("in A.a()")\n\n    def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()\n\n\ndef func():\n    A().a()\n    func_x()\n\n\nglobal_var_1 = A().b()\nglobal_var_2 = func()\n\nif __name__ == "__main__":\n    A().b()\n    func()\n',
            'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()',
            "b",
        ),
        (
            'from x import func_x\n\n\nclass A:\n    def a(self):\n        print("in A.a()")\n\n    def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()\n\n\ndef func():\n    A().a()\n    func_x()\n\n\nglobal_var_1 = A().b()\nglobal_var_2 = func()\n\nif __name__ == "__main__":\n    A().b()\n    func()\n',
            "def func():\n    A().a()\n    func_x()",
            "func",
        ),
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
