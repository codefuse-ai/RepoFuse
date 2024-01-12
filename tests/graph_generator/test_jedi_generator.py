from pathlib import Path
from textwrap import dedent

import pytest

from dependency_graph.graph_generator.jedi_generator import JediDependencyGraphGenerator
from dependency_graph.models.dependency_graph import Edge, EdgeRelation
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
    for i, edge in enumerate(edges):
        parent, child, _ = edge
        match i:
            case 0:
                assert parent.type == "module"
                assert parent.name == "main"

                assert child.type == "class"
                assert child.name == "A"
            case 1:
                assert parent.type == "module"
                assert parent.name == "main"

                assert child.type == "function"
                assert child.name == "func"
            case 2:
                assert parent.type == "function"
                assert parent.name == "func"

                assert child.type == "function"
                assert child.name == "closure"
            case 3:
                assert parent.type == "class"
                assert parent.name == "A"

                assert child.type == "function"
                assert child.name == "a"


def test_import_relation(jedi_generator):
    repo_path = repo_suite_path / "import_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    edges = D.get_related_edges(EdgeRelation.Imports)
    assert edges
    for i, edge in enumerate(edges):
        importer, exporter, relations = edge
        importations = list(
            filter(
                lambda relation: relation.relation == EdgeRelation.Imports,
                relations,
            )
        )
        assert len(importations) > 0
        importation = importations[0]
        match i:
            case 0:
                assert importer.type == "module"
                assert importer.name == "main"
                assert exporter.type == "module"
                assert exporter.name == "os"
                assert importation.get_text() == "import os"
            case 1:
                assert importer.type == "module"
                assert importer.name == "main"
                assert exporter.type == "class"
                assert exporter.name == "Path"
                assert importation.get_text() == "from pathlib import Path"
            case 2:
                assert importer.type == "module"
                assert importer.name == "main"
                assert exporter.type == "module"
                assert exporter.name == "y"
                assert importation.get_text() == "import y"
            case 3:
                assert importer.type == "module"
                assert importer.name == "main"
                assert exporter.type == "variable"
                assert exporter.name == "VAR_Y"
                assert importation.get_text() == "y.VAR_Y += 1"
            case 4:
                assert importer.type == "module"
                assert importer.name == "main"
                assert exporter.type == "function"
                assert exporter.name == "func_z"
                assert importation.get_text() == "from z import func_z"


def test_instantiate_relation(jedi_generator):
    repo_path = repo_suite_path / "instantiate_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    edges = D.get_related_edges(EdgeRelation.Instantiates)
    assert edges
    for i, edge in enumerate(edges):
        instance_owner, instance_type, relations = edge
        instantiations = list(
            filter(
                lambda relation: relation.relation == EdgeRelation.Instantiates,
                relations,
            )
        )
        assert len(instantiations) > 0
        instantiation = instantiations[0]
        match i:
            case 0:
                assert instance_owner.type == "module"
                assert instance_owner.name == "main"
                assert instance_type.type == "function"
                assert instance_type.name == "func_2"
                assert instantiation.get_text() == "func_2"
            case 1:
                assert instance_owner.type == "module"
                assert instance_owner.name == "main"
                assert instance_type.type == "function"
                assert instance_type.name == "A"
                assert instantiation.get_text() == "A"
            case 2:
                assert instance_owner.type == "module"
                assert instance_owner.name == "main"
                assert instance_type.type == "function"
                assert instance_type.name == "A"
                assert instantiation.get_text() == "class_a"
            case 3:
                assert instance_owner.type == "module"
                assert instance_owner.name == "main"
                assert instance_type.type == "function"
                assert instance_type.name == "B"
                assert instantiation.get_text() == "B"
            case 4:
                assert instance_owner.type == "function"
                assert instance_owner.name == "return_A"
                assert instance_type.type == "function"
                assert instance_type.name == "A"
                assert instantiation.get_text() == "A"
            case 5:
                assert instance_owner.type == "function"
                assert instance_owner.name == "return_A"
                assert instance_type.type == "function"
                assert instance_type.name == "A"
                assert instantiation.get_text() == "class_a"
            case 6:
                assert instance_owner.type == "function"
                assert instance_owner.name == "func_1"
                assert instance_type.type == "function"
                assert instance_type.name == "A"
                assert instantiation.get_text() == "A"
            case 7:
                assert instance_owner.type == "function"
                assert instance_owner.name == "func_1"
                assert instance_type.type == "function"
                assert instance_type.name == "A"
                assert instantiation.get_text() == "class_a"
            case 8:
                assert instance_owner.type == "function"
                assert instance_owner.name == "func_2"
                assert instance_type.type == "function"
                assert instance_type.name == "A"
                assert instantiation.get_text() == "class_a"
            case 9:
                assert instance_owner.type == "function"
                assert instance_owner.name == "func_2"
                assert instance_type.type == "function"
                assert instance_type.name == "B"
                assert instantiation.get_text() == "B"


def test_call_relation(jedi_generator):
    repo_path = repo_suite_path / "call_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    call_graph = D.get_related_edges(EdgeRelation.Calls)

    assert call_graph
    for i, call in enumerate(call_graph):
        caller, callee, relations = call
        call_sites = list(
            filter(
                lambda relation: relation.relation == EdgeRelation.Calls,
                relations,
            )
        )
        assert len(call_sites) > 0
        call_site = call_sites[0]
        match i:
            case 8:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def func_x():
                        print("in x")"""
                )
                assert callee.name == "print"
                assert call_site.get_text() == "print"
            case 4:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def a(self):
                            print("in A.a()")"""
                )
                assert callee.name == "print"
                assert call_site.get_text() == "print"

            case 6:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def closure():
                                print("in A.b()")
                                self.a()"""
                )
                assert callee.name == "print"
                assert call_site.get_text() == "print"
            case 7:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def closure():
                                print("in A.b()")
                                self.a()"""
                )
                assert callee.get_text() == dedent(
                    """\
                    def a(self):
                            print("in A.a()")"""
                )
                assert call_site.get_text() == "a"
            case 5:
                assert caller.type == "function"
                assert callee.type == "function"

                assert (
                    caller.get_text()
                    == 'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()'
                )

                assert callee.get_text() == dedent(
                    """\
                    def closure():
                                print("in A.b()")
                                self.a()"""
                )
                assert call_site.get_text() == "closure"
            case 2:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def func():
                        A().a()
                        func_x()"""
                )
                assert callee.get_text() == dedent(
                    """\
                    def a(self):
                            print("in A.a()")"""
                )
                assert call_site.get_text() == "a"
            case 3:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def func():
                        A().a()
                        func_x()"""
                )
                assert callee.get_text() == dedent(
                    """\
                    def func_x():
                        print("in x")"""
                )
                assert call_site.get_text() == "func_x"
            case 1:
                assert caller.type == "module"
                assert callee.type == "function"

                assert caller.name == "main"

                assert (
                    callee.get_text()
                    == 'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()'
                )
                assert call_site.get_text() == "b"
            case 0:
                assert caller.type == "module"
                assert callee.type == "function"

                assert caller.name == "main"

                assert callee.get_text() == dedent(
                    """\
                    def func():
                        A().a()
                        func_x()"""
                )
                assert call_site.get_text() == "func"
