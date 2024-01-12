import enum
from dataclasses import dataclass
from pathlib import Path
from typing import Self, Optional, Iterable

import networkx as nx

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
        loc = [self.start_line, self.start_column, self.end_line, self.end_column]
        if any([l is not None for l in loc]):
            signature += f":{self.start_line}:{self.start_column}-{self.end_line}:{self.end_column}"

        return signature

    def __hash__(self) -> int:
        return hash(self.__str__())

    def get_text(self) -> str | None:
        # TODO should leverage the FileNode.content
        content = self.file_path.read_text()
        loc = [self.start_line, self.start_column, self.end_line, self.end_column]
        if any([l is None for l in loc]):
            return None

        return slice_text(
            content, self.start_line, self.start_column, self.end_line, self.end_column
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
    VARIABLE = "variable"


@dataclass
class Node:
    def __str__(self) -> str:
        return f"{self.name}:{self.type}@{self.location}"

    def __hash__(self) -> int:
        return hash(self.__str__())

    def get_text(self) -> str | None:
        return self.location.get_text()

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

    def get_text(self) -> str | None:
        return self.location.get_text()

    def get_inverse_edge(self) -> Self:
        return Edge(
            relation=self.relation.get_inverse_kind(),
            location=self.location,
        )

    relation: EdgeRelation
    """The relation between two nodes"""
    location: Optional[Location] = None
    """The location of the edge"""


class DependencyGraph:
    def __init__(self, repo_path: PathLike) -> None:
        # See https://networkx.org/documentation/stable/reference/classes/multidigraph.html
        # See also https://stackoverflow.com/questions/26691442/how-do-i-add-a-new-attribute-to-an-edge-in-networkx
        self.graph = nx.MultiDiGraph()
        self.repo_path = Path(repo_path)

    def add_node(self, node: Node):
        self.graph.add_node(node)

    def add_nodes_from(self, nodes: Iterable[Node]):
        self.graph.add_nodes_from(nodes)

    def add_relational_edge(self, n1: Node, n2: Node, r1: Edge, r2: Edge | None = None):
        """Add a relational edge between two nodes.
        r2 can be None to indicate this is a unidirectional edge."""
        self.add_node(n1)
        self.add_node(n2)
        self.graph.add_edge(n1, n2, relation=r1)
        if r2 is not None:
            self.graph.add_edge(n2, n1, relation=r2)

    def add_relational_edges_from(
        self, edges: Iterable[tuple[Node, Node, Edge, Edge | None]]
    ):
        """Add relational edges.
        r2 can be None to indicate this is a unidirectional edge."""
        for e in edges:
            assert len(e) in (3, 4), f"Invalid edges length: {e}, should be 3 or 4"
            self.add_relational_edge(*e)

    def get_related_edges(
        self, *relations: EdgeRelation
    ) -> list[tuple[Node, Node, Edge]]:
        # self.graph.edges(data="relation") is something like:
        # [(1, 2, Edge(...), (1, 2, Edge(...)), (3, 4, Edge(...)]
        filtered_edges = list(
            filter(
                lambda edge: edge and edge[2].relation in relations,
                self.graph.edges(data="relation"),
            )
        )
        # Sort by edge's location
        return sorted(filtered_edges, key=lambda e: e[2].location.__str__())

    def get_related_nodes(
        self, node: Node, *relations: EdgeRelation
    ) -> list[Node] | None:
        """Get the related nodes of the given node by the given relations.
        If the given node is not in the graph, return None."""
        if node not in self.graph:
            return None

        return [
            edge[1]
            for edge in self.graph.edges(node, data="relation")
            if edge[2].relation in relations
        ]

    def get_related_subgraph(self, *relations: EdgeRelation) -> Self:
        """Get a subgraph that contains all the nodes and edges that are related to the given relations.
        This subgraph is a new sub-copy of the original graph."""
        edges = self.get_related_edges(*relations)
        sub_graph = DependencyGraph(self.repo_path)
        sub_graph.add_relational_edges_from(edges)
        return sub_graph
