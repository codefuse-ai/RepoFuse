import enum
from abc import ABC, abstractmethod

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.models import PathLike
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


class GraphGeneratorType(str, enum.Enum):
    """
    Graph generator type
    """

    JEDI = "jedi"
    TREE_SITTER = "tree_sitter"


class BaseDependencyGraphGenerator(ABC):
    supported_languages: tuple[Language] = ()

    def __init__(self, language: Language):
        if language not in self.supported_languages:
            raise ValueError(
                f"Language {language} is not supported by graph generator {self.__class__.__name__}"
            )

    @abstractmethod
    def generate_file(
        self,
        repo: Repository,
        code: str = None,
        file_path: PathLike = None,
    ) -> DependencyGraph:
        """
        Generate Repo-Specific Semantic Graph for a file.
        Should provide either code or file_path
        """
        ...

    @abstractmethod
    def generate(self, repo: Repository) -> DependencyGraph:
        ...
