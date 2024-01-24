from pathlib import Path
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
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()

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
        str_edge = str(edge)
        if G.has_edge(str_v, str_u):
            G[str_u][str_v]["label"] += "/" + str_edge
        else:
            G.add_edge(str_u, str_v, label=str_edge)
    return G


def dump_graph_as_pyvis_graph(graph: DependencyGraph, filename: PathLike) -> None:
    nt = Network(height="1200px", width="100%", notebook=False, select_menu=True)
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
                    "enabled": true,
                    "parentCentralization": true,
                    "direction": "UD",
                    "sortMethod": "directed",
                    "shakeTowards": "leaves"
                  }
                }
              }
            }
            """
        )
    )
    nt.save_graph(str(filename))


def output_dependency_graph(
    graph: DependencyGraph, output_format: str, output_file: PathLike = None
):
    """
    Outputs the dependency The graph outputted to a file or stdout.

    :param graph: The dependency graph to output.
    :param output_format: The format in which to output the graph (e.g., "edgelist" or "pyvis").
    :param output_file: The file path to write the graph to. If None, outputs to stdout.
    """
    logger.info(
        f"Outputting the dependency graph in {output_file if output_file else 'stdout'} with format {output_format}"
    )

    match output_format:
        case "edgelist":
            data = graph.to_json()
            if output_file:
                output_file = Path(output_file)
                output_file.write_text(data)
            else:
                print(data)
        case "pyvis":
            if output_file is None:
                raise ValueError(
                    "You must specify an output file for the pyvis format."
                )
            dump_graph_as_pyvis_graph(graph, output_file)
        case _:
            raise ValueError(f"Unknown output format: {output_format}")
