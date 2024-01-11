from pathlib import Path
from textwrap import dedent

import pytest

from dependency_graph.graph_generator.jedi_generator import JediDependencyGraphGenerator
from dependency_graph.models.dependency_graph import Edge, EdgeRelation
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository

repo_suite_path = Path(__file__).parent / "code_example" / "python"


@pytest.fixture
def jedi_generator():
    return JediDependencyGraphGenerator(Language.Python)


def test_parent_relation(jedi_generator):
    repo_path = repo_suite_path / "parent_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    hierarchy = D.get_edges_by_relation(EdgeRelation.ParentOf)
    assert hierarchy
    for i, parent_relationship in enumerate(hierarchy):
        parent, child, _ = parent_relationship
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


def test_call_relation(jedi_generator):
    repo_path = repo_suite_path / "call_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    call_graph = D.get_edges_by_relation(EdgeRelation.Calls)

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
