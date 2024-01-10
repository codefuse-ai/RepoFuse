from dependency_graph.graph_generator import BaseDependencyGraphGenerator
from dependency_graph.models.dependency_graph import DependencyGraph
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


class TreeSitterDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = [
        Language.Python,
    ]

    def __init__(self, language: Language = Language.Python):
        super().__init__(language)

    def generate(self, repo: Repository) -> DependencyGraph:
        raise NotImplementedError()
