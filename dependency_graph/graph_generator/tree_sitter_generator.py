from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.graph_generator import BaseDependencyGraphGenerator
from dependency_graph.models import PathLike
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


class TreeSitterDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = [
        Language.Python,
    ]

    def __init__(self, language: Language = Language.Python):
        super().__init__(language)

    def generate_file(
        self, code: str = None, file_path: PathLike = None, repo: Repository = None
    ) -> DependencyGraph:
        raise NotImplementedError()

    def generate(self, repo: Repository) -> DependencyGraph:
        raise NotImplementedError()
