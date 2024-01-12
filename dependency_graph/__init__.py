from textwrap import dedent

import networkx as nx
from pyvis.network import Network

from dependency_graph.graph_generator import DependencyGraphGeneratorType
from dependency_graph.graph_generator.jedi_generator import JediDependencyGraphGenerator
from dependency_graph.graph_generator.tree_sitter_generator import (
    TreeSitterDependencyGraphGenerator,
)
from dependency_graph.models import PathLike
from dependency_graph.models.dependency_graph import DependencyGraph, EdgeRelation
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


def construct_dependency_graph(
    repo: Repository, dependency_graph_generator: DependencyGraphGeneratorType
) -> DependencyGraph:
    language = repo.language
    if dependency_graph_generator == DependencyGraphGeneratorType.JEDI:
        return JediDependencyGraphGenerator(language).generate(repo)
    elif dependency_graph_generator == DependencyGraphGeneratorType.TREE_SITTER:
        return TreeSitterDependencyGraphGenerator(language).generate(repo)


def stringify_graph(graph: DependencyGraph) -> nx.Graph:
    G = nx.Graph()
    for u, v, edge in graph.graph.edges(data="relation"):
        str_u, str_v = str(u), str(v)
        # Ignore the edge location when stringify the graph
        str_edge = str(edge.relation)
        if G.has_edge(str_v, str_u):
            G[str_u][str_v]["label"] += "/" + str_edge
        else:
            G.add_edge(str_u, str_v, label=str_edge)
    return G


def dump_graph_as_edgelist(graph: DependencyGraph) -> list:
    G = stringify_graph(graph)
    return list(nx.to_edgelist(G))


def dump_graph_as_pyvis_graph(graph: DependencyGraph, filename: PathLike) -> None:
    nt = Network(height="1000px", width="100%", notebook=False, select_menu=True)
    colors = (
        "red",
        "blue",
        "green",
        "yellow",
        "orange",
        "purple",
        "pink",
        "brown",
        "black",
        "white",
        "gray",
        "cyan",
        "magenta",
        "teal",
        "maroon",
    )

    for i, relation in enumerate(EdgeRelation):
        if relation.value[2] == 1:
            continue
        sub_graph = graph.get_related_subgraph(relation, relation.get_inverse_kind())
        G = stringify_graph(sub_graph)
        nx.set_edge_attributes(G, colors[i], "color")
        nt.from_nx(G)

    nt.set_options(
        dedent(
            """
            const options = {
              "edges": {
                "arrows": {
                  "to": {
                    "enabled": true
                  }
                },
                "layout": {
                  "hierarchical": {
                    "enabled": true
                  }
                }
              }
            }
            """
        )
    )
    nt.save_graph(str(filename))
