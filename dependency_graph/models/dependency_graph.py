import enum
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Optional

import networkx

from dependency_graph.models import PathLike
from dependency_graph.utils.text import slice_text


class EdgeRelation(enum.Enum):
    """The relation between two nodes"""

    # (x, y, z) represents (Relationship Category ID, Category Internal ID, Relationship Direction)
    # 1. Syntax relations
    ParentOf = (1, 0, 0)
    ChildOf = (1, 0, 1)
    Construct = (1, 1, 0)
    ConstructedBy = (1, 1, 1)
    # 2. Import relations
    Imports = (2, 0, 0)
    ImportedBy = (2, 0, 1)
    # 3. Inheritance relations
    BaseClassOf = (3, 0, 0)
    DerivedClassOf = (3, 0, 1)
    # 4. Method override relations
    Overrides = (4, 0, 0)
    OverriddenBy = (4, 0, 1)
    # 5. Method call relations
    Calls = (5, 0, 0)
    CalledBy = (5, 0, 1)
    # 6. Object instantiation relations
    Instantiates = (6, 0, 0)
    InstantiatedBy = (6, 0, 1)
    # 7. Field use relations
    Uses = (7, 0, 0)
    UsedBy = (7, 0, 1)
    # Type inference
    Type = (8, 0, 0)
    # Type = (8, 0, 1)

    def __str__(self):
        return self.name

    def get_inverse_kind(self) -> Self:
        new_value = [*self.value]
        new_value[2] = 1 - new_value[2]
        return EdgeRelation(tuple(new_value))

    def is_inverse_relationship(self, other) -> bool:
        return (
            self.value[0] == other.value[0]
            and self.value[1] == other.value[1]
            and self.value[2] != other.value[2]
        )


@dataclass
class Location:
    def __str__(self) -> str:
        signature = f"{self.file_path}"
        if any([self.start_line, self.start_column, self.end_line, self.end_column]):
            signature += f":{self.start_line}:{self.start_column}-{self.end_line}:{self.end_column}"

        return signature

    def __hash__(self) -> int:
        return hash(self.__str__())

    def get_text(self) -> str | None:
        # TODO should leverage the FileNode.content
        content = self.file_path.read_text()
        if any([self.start_line, self.start_column, self.end_line, self.end_column]):
            return None

        return slice_text(
            content, self.start_line, self.end_line, self.start_column, self.end_column
        )

    file_path: Path
    """The file path"""
    start_line: Optional[int] = None
    """The start line number, 1-based"""
    start_column: Optional[int] = None
    """The start column number, 1-based"""
    end_line: Optional[int] = None
    """The end line number, 1-based"""
    end_column: Optional[int] = None
    """The end column number, 1-based"""


@dataclass
class NodeType(str, enum.Enum):
    # TODO should nest a language to mark different type for different language
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"


@dataclass
class Node:
    def __str__(self) -> str:
        return f"{self.name}:{self.type}@{self.location}"

    def __hash__(self) -> int:
        return hash(self.__str__())

    type: NodeType
    """The type of the node"""
    name: str
    """The name of the node"""
    location: Location
    """The location of the node"""


@dataclass
class Edge:
    def __str__(self) -> str:
        signature = f"{self.relation}"
        if self.location:
            signature += f"@{self.location}"
        return signature

    def __hash__(self) -> int:
        return hash(self.__str__())

    relation: EdgeRelation
    """The relation between two nodes"""
    location: Optional[Location] = None
    """The location of the edge"""


class DependencyGraph:
    def __init__(self, repo_path: PathLike) -> None:
        self.graph = networkx.DiGraph()
        self.repo_path = Path(repo_path)

    def add_node(self, node: Node):
        if isinstance(
            node.location.file_path, Path
        ) and node.location.file_path.is_relative_to(self.repo_path):
            node.location.file_path = node.location.file_path.relative_to(
                self.repo_path.parent
            )

        self.graph.add_node(node)

    def add_relational_edge(self, n1: Node, n2: Node, r1: Edge, r2: Edge):
        self.add_node(n1)
        self.add_node(n2)
        self.graph.add_edge(n1, n2, kind=r1)
        self.graph.add_edge(n2, n1, kind=r2)
