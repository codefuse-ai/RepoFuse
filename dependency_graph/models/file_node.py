from functools import cached_property
from pathlib import Path

from dependency_graph.models import PathLike


class FileNode:
    file_path: Path
    _content: str

    def __init__(self, file_path: PathLike):
        self.file_path = Path(file_path).expanduser().absolute()

    @cached_property
    def content(self) -> str:
        # TODO Compare file timestamp to detect file changes made by others
        self._content = self.file_path.read_text()
        return self._content

    def write_content(self, content: str) -> None:
        self.file_path.write_text(content)
        self._content = content
        del self.__dict__["content"]  # Invalidate the cache
