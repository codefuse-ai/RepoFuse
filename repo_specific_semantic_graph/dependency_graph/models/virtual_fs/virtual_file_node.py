from dependency_graph.models.file_node import FileNode
from dependency_graph.models.virtual_fs.virtual_path import VirtualPath


class VirtualFileNode(FileNode):
    def __init__(self, file_path: VirtualPath):
        super().__init__(file_path)
        self.file_path = file_path

    def write_content(self, content: str) -> None:
        raise NotImplementedError(
            "Write operation is not permitted for VirtualFileNode."
        )
