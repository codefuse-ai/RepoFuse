import pytest

from dependency_graph import Language, Repository, PathLike
from dependency_graph.graph_generator import BaseDependencyGraphGenerator


class DummyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages = (Language.Java,)

    def generate_file(
        self,
        repo: Repository,
        code: str = None,
        file_path: PathLike = None,
    ):
        return None

    def generate(self, repository: Repository):
        return None


def test_graph_generator_can_validate_language(python_repo_suite_path):
    repo = Repository(repo_path=python_repo_suite_path, language=Language.Python)
    generator = DummyGraphGenerator()
    with pytest.raises(
        ValueError,
        match="Language python is not supported by graph generator DummyGraphGenerator",
    ):
        generator.generate(repo)
