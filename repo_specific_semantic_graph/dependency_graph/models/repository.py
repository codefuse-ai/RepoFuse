from functools import cached_property
from pathlib import Path

from git import Repo, InvalidGitRepositoryError, GitCommandError, NoSuchPathError

from dependency_graph.models import PathLike
from dependency_graph.models.file_node import FileNode
from dependency_graph.models.language import Language
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()


class Repository:
    _git_repo: Repo = None
    repo_path: Path = None
    language: Language

    code_file_extensions: dict[Language, tuple[str]] = {
        Language.CSharp: (".cs", ".csx"),
        Language.Python: (".py", ".pyi"),
        Language.Java: (".java",),
        Language.JavaScript: (".js", ".jsx"),
        Language.TypeScript: (".ts", ".tsx"),
    }

    def __init__(self, repo_path: PathLike, language: Language) -> None:
        if isinstance(repo_path, str):
            self.repo_path = Path(repo_path).expanduser().absolute()
        else:
            self.repo_path = repo_path.expanduser().absolute()

        self.language = language

        if self.repo_path.is_file():
            raise NotADirectoryError(f"Repo path {self.repo_path} is not a directory")

        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repo path {self.repo_path} does not exist")

        if self.language not in self.code_file_extensions:
            raise ValueError(
                f"Language {self.language} is not supported to get code files"
            )

        try:
            self._git_repo = Repo(repo_path)
        except (InvalidGitRepositoryError, NoSuchPathError):
            # The repo is not a git repo, just ignore
            pass

    @cached_property
    def files(self) -> set[FileNode]:
        files: set[FileNode] = set()
        # Loop through the file extensions
        for extension in self.code_file_extensions[self.language]:
            # Use rglob() with a pattern to match the file extension
            rglob_file_list = list(self.repo_path.rglob(f"*{extension}"))

            # Get the git-ignored files
            ignored_files = []

            if self._git_repo:
                try:
                    ignored_files = self._git_repo.ignored(
                        *list(self.repo_path.rglob(f"*{extension}"))
                    )
                except OSError:
                    # If the git command argument list is too long, it will raise an OSError.
                    # In this case, we will invoke the API by iterating through the files one by one
                    logger.warn(
                        f"git command argument list is too long, invoking the API by iterating through the files one by one"
                    )
                    for file in rglob_file_list:
                        ignored_files.extend(self._git_repo.ignored(file))
                except GitCommandError:
                    pass

            # Add the files to the set filtering out git-ignored files
            files.update(
                [
                    FileNode(file)
                    for file in rglob_file_list
                    if str(file) not in ignored_files
                ]
            )

        return files
