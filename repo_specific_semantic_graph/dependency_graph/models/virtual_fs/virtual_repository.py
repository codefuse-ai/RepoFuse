from __future__ import annotations

from collections import namedtuple
from typing import Iterable

from fs.memoryfs import MemoryFS

from dependency_graph.models import PathLike
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository
from dependency_graph.models.virtual_fs.virtual_file_node import VirtualFileNode
from dependency_graph.models.virtual_fs.virtual_path import VirtualPath

# Define the VirtualFile named tuple
VirtualFile = namedtuple("VirtualFile", ["relative_path", "content"])


class VirtualRepository(Repository):
    def __init__(
        self,
        repo_path: PathLike,
        language: Language,
        virtual_files: list[VirtualFile],  # Use the named tuple for typing
    ):
        self.fs = MemoryFS()
        # Make sure the repo path is absolute
        self.repo_path = VirtualPath(self.fs, "/", repo_path)
        self.repo_path.mkdir(parents=True)

        self._all_file_paths = []
        for file_path, content in virtual_files:
            # Strip the leading slash on the file path
            p = VirtualPath(self.fs, self.repo_path / file_path.lstrip("/"))
            if p.suffix in self.code_file_extensions[language]:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
                self._all_file_paths.append(p)

        super().__init__(self.repo_path, language)

    @property
    def files(self) -> set[VirtualFileNode]:
        files: set[VirtualFileNode] = set(
            [VirtualFileNode(file_path) for file_path in self._all_file_paths]
        )
        return files

    @files.setter
    def files(self, file_nodes: Iterable[VirtualFileNode]):
        """Setter to update the virtual files in the repository."""
        # Clear existing files
        self._all_file_paths.clear()

        for file_node in file_nodes:
            p = VirtualPath(self.fs, file_node.file_path)
            self._all_file_paths.append(p)
