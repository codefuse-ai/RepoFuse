import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Callable

import networkx as nx

from dependency_graph.models import PathLike
from dependency_graph.models.dependency_graph import Node, Edge, EdgeRelation


class DependencyGraph:
    def __init__(self, repo_path: PathLike) -> None:
        # See https://networkx.org/documentation/stable/reference/classes/multidigraph.html
        # See also https://stackoverflow.com/questions/26691442/how-do-i-add-a-new-attribute-to-an-edge-in-networkx
        self.graph = nx.MultiDiGraph()
        self.repo_path = Path(repo_path)

        self._update_callbacks: set[Callable] = set()
        # Clear the cache of self.get_edges when the graph is updated
        self.register_update_callback(self.get_edges.cache_clear)

    def as_retriever(self) -> "DependencyGraphContextRetriever":
        return DependencyGraphContextRetriever(graph=self)

    def register_update_callback(self, callback):
        if callback not in self._update_callbacks:
            self._update_callbacks.add(callback)

    def _notify_update(self):
        for callback in self._update_callbacks:
            callback()

    def add_node(self, node: Node):
        self.graph.add_node(node)
        self._notify_update()

    def add_nodes_from(self, nodes: Iterable[Node]):
        self.graph.add_nodes_from(nodes)
        self._notify_update()

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
        filtered_edges = self.get_edges(
            edge_filter=lambda in_node, out_node, edge: edge.relation in relations
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

    def get_related_subgraph(self, *relations: EdgeRelation) -> "DependencyGraph":
        """Get a subgraph that contains all the nodes and edges that are related to the given relations.
        This subgraph is a new sub-copy of the original graph."""
        edges = self.get_related_edges(*relations)
        sub_graph = DependencyGraph(self.repo_path)
        sub_graph.add_relational_edges_from(edges)
        return sub_graph

    @lru_cache(maxsize=128)
    def get_edges(
        self,
        # the edge_filter parameter should also be hashable
        edge_filter: Callable[[Node, Node, Edge], bool] = None,
    ) -> list[tuple[Node, Node, Edge]]:
        # self.graph.edges(data="relation") is something like:
        # [(1, 2, Edge(...), (1, 2, Edge(...)), (3, 4, Edge(...)]
        if edge_filter is None:
            return list(self.graph.edges(data="relation"))

        return [
            edge for edge in self.graph.edges(data="relation") if edge_filter(*edge)
        ]

    def to_dict(self) -> dict:
        edgelist = self.get_edges()
        return {
            "repo_path": str(self.repo_path),
            "edges": [
                (edge[0].to_dict(), edge[1].to_dict(), edge[2].to_dict())
                for edge in edgelist
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(obj_dict: dict) -> "DependencyGraph":
        edges = [
            (Node.from_dict(edge[0]), Node.from_dict(edge[1]), Edge.from_dict(edge[2]))
            for edge in obj_dict["edges"]
        ]
        graph = DependencyGraph(obj_dict["repo_path"])
        graph.add_relational_edges_from(edges)
        return graph

    @staticmethod
    def from_json(json_str: str) -> "DependencyGraph":
        obj_dict = json.loads(json_str)
        return DependencyGraph.from_dict(obj_dict)


class DependencyGraphContextRetriever:
    """
    DependencyGraphRetriever provides a class to retrieve code snippets from a dependency graph in context level.
    The difference between this and the DependencyGraph is that this retrieves the context of a code, it is not dealing
    with a graph problem, while the DependencyGraph is.
    """

    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def get_cross_file_context(
        self,
        file_path: PathLike,
        edge_filter: Callable[[Node, Node, Edge], bool] = None,
    ) -> list[tuple[Node, Node, Edge]]:
        """
        Construct the cross-file context of a file
        - The in node should be located in the repo and be cross-file
        - The out node should be in the same file
        """
        file_path = Path(file_path)

        # Don't feel guilty, self.graph.get_edges is cached!
        edge_list: list[tuple[Node, Node, Edge]] = self.graph.get_edges(
            edge_filter=lambda in_node, out_node, edge: (
                in_node.location
                and in_node.location.file_path
                and in_node.location.file_path != file_path
                and in_node.location.file_path.is_relative_to(self.graph.repo_path)
            )
            and (
                out_node.location
                and out_node.location.file_path
                and out_node.location.file_path == file_path
            )
        )

        # This custom edge_filter is applied after the edge_list is constructed by self.graph.get_edges
        # because we want more cache hits on the filter called above.
        if edge_filter is not None:
            return [edge for edge in edge_list if edge_filter(*edge)]

        return edge_list

    def get_cross_file_context_by_line(
        self,
        file_path: PathLike,
        start_line: int,
    ) -> list[tuple[Node, Node, Edge]]:
        """
        Construct the cross-file context of a file
        """
        line_specific_edge_list: list[
            tuple[Node, Node, Edge]
        ] = self.get_cross_file_context(
            file_path,
            # The out node should be in the same file and located around the start line number
            # The edge should be in the same file and located before the start line
            edge_filter=lambda in_node, out_node, edge: (
                out_node.location.start_line
                and out_node.location.end_line
                and out_node.location.start_line
                <= start_line
                <= out_node.location.end_line
            )
            and (
                edge.location
                and edge.location.file_path
                and edge.location.file_path == file_path
                and edge.location.start_line
                and edge.location.start_line < start_line
            )
            and edge.relation in (EdgeRelation.CalledBy, EdgeRelation.InstantiatedBy),
        )

        importation_edge_list: list[
            tuple[Node, Node, Edge]
        ] = self.get_cross_file_context(
            file_path,
            edge_filter=lambda in_node, out_node, edge: in_node.location.start_line
            and in_node.location.start_line < start_line
            and edge.relation in (EdgeRelation.ImportedBy,),
        )

        edge_list: list[tuple[Node, Node, Edge]] = (
            line_specific_edge_list + importation_edge_list
        )
        return edge_list
