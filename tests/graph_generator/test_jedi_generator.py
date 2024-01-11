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


def test_call_relation(jedi_generator):
    repo_path = repo_suite_path / "call_relation"
    repository = Repository(repo_path=repo_path, language=Language.Python)
    D = jedi_generator.generate(repository)

    call_graph = D.get_edges_by_relation(EdgeRelation.Calls)

    assert call_graph
    for i, call in enumerate(call_graph):
        caller, callee, call_site_d = call
        call_site = call_site_d["relation"]
        match i:
            case 0:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def func_x():
                        print("in x")"""
                )
                assert callee.name == "print"
                assert call_site.get_text() == "print"
            case 1:
                assert caller.type == "function"
                assert callee.type == "function"

                assert caller.get_text() == dedent(
                    """\
                    def a(self):
                            print("in A.a()")"""
                )
                assert callee.name == "print"
                assert call_site.get_text() == "print"
            case 2:
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
            case 3:
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
            case 4:
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
            case 5:
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
            case 6:
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
            case 7:
                assert caller.type == "module"
                assert callee.type == "function"

                assert caller.name == "main"

                assert (
                    callee.get_text()
                    == 'def b(self):\n        def closure():\n            print("in A.b()")\n            self.a()\n\n        closure()'
                )
                assert call_site.get_text() == "b"
            case 8:
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
