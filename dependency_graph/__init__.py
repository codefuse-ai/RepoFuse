from textwrap import dedent

import networkx as nx
from pyvis.network import Network

from dependency_graph.graph_generator import DependencyGraphGeneratorType
from dependency_graph.graph_generator.jedi_generator import JediDependencyGraphGenerator
from dependency_graph.graph_generator.tree_sitter_generator import (
    TreeSitterDependencyGraphGenerator,
)
from dependency_graph.models import PathLike
from dependency_graph.models.dependency_graph import DependencyGraph
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


def dump_graph_as_edgelist(graph: DependencyGraph) -> list:
    G = nx.Graph()
    for u, v, data in graph.graph.edges(data=True):
        str_u, str_v = str(u), str(v)
        if G.has_edge(str_v, str_u):
            G[str_u][str_v]["label"] += "/" + str(data["relations"])
        else:
            G.add_edge(str_u, str_v, label=str(data["relations"]))

    return list(nx.to_edgelist(G))


def dump_graph_as_pyvis_graph(graph: DependencyGraph, filename: PathLike) -> None:
    # TODO colorize different relation edges
    G = nx.Graph()
    for u, v, data in graph.graph.edges(data=True):
        str_u, str_v = str(u), str(v)
        if G.has_edge(str_v, str_u):
            G[str_u][str_v]["label"] += "/" + str(data["relations"])
        else:
            G.add_edge(str_u, str_v, label=str(data["relations"]))

    nt = Network(height="1000px", width="100%", notebook=False, select_menu=True)
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
