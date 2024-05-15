from functools import cached_property
from pathlib import Path

from dependency_graph.utils.log import setup_logger
from dependency_graph.models import PathLike

# Initialize logging
logger = setup_logger()


class FileNode:
    file_path: Path
    _content: str

    def __init__(self, file_path: PathLike):
        self.file_path = Path(file_path).expanduser().absolute()

    @cached_property
    def content(self) -> str:
        # TODO Compare file timestamp to detect file changes made by others
        try:
            self._content = self.file_path.resolve().read_text()
        except UnicodeDecodeError:
            logger.error(
                f"File {self.file_path} is not UTF-8 encoded. Returning empty string."
            )
            self._content = ""
        return self._content

    def write_content(self, content: str) -> None:
        self.file_path.write_text(content)
        self._content = content
        del self.__dict__["content"]  # Invalidate the cache
