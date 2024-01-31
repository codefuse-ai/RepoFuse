from pathlib import Path
from textwrap import dedent

import networkx as nx
from ipysigma import Sigma
from pyvis.network import Network

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.graph_generator import DependencyGraphGeneratorType
from dependency_graph.graph_generator.jedi_generator import JediDependencyGraphGenerator
from dependency_graph.graph_generator.tree_sitter_generator import (
    TreeSitterDependencyGraphGenerator,
)
from dependency_graph.models import PathLike
from dependency_graph.models.graph_data import EdgeRelation
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()


def construct_dependency_graph(
    repo: Repository | PathLike,
    dependency_graph_generator: DependencyGraphGeneratorType,
    language: Language | None = None,
) -> DependencyGraph:
    if isinstance(repo, PathLike):
        if language is None:
            raise ValueError("language is required when repo is a PathLike")
        repo = Repository(repo, language)

    language = repo.language
    if dependency_graph_generator == DependencyGraphGeneratorType.JEDI:
        return JediDependencyGraphGenerator(language).generate(repo)
    elif dependency_graph_generator == DependencyGraphGeneratorType.TREE_SITTER:
        return TreeSitterDependencyGraphGenerator(language).generate(repo)


def stringify_graph(graph: DependencyGraph) -> nx.Graph:
    G = nx.DiGraph()
    for u, v, edge in graph.get_edges():
        # TODO Can we do better to relativize the path elsewhere ?
        if (
            u.location
            and u.location.file_path
            and u.location.file_path.is_relative_to(graph.repo_path)
        ):
            u.location.file_path = u.location.file_path.relative_to(graph.repo_path)
        if (
            v.location
            and v.location.file_path
            and v.location.file_path.is_relative_to(graph.repo_path)
        ):
            v.location.file_path = v.location.file_path.relative_to(graph.repo_path)
        if (
            edge.location
            and edge.location.file_path
            and edge.location.file_path.is_relative_to(graph.repo_path)
        ):
            edge.location.file_path = edge.location.file_path.relative_to(
                graph.repo_path
            )
        str_u, str_v = str(u), str(v)

        if G.has_edge(str_v, str_u):
            # e.g. add ChildOf edge to an existing ParentOf edge, the order is inverse
            G[str_v][str_u]["relations"].append(edge.to_dict())
        else:
            if not G.has_node(str_u):
                G.add_node(str_u, **u.to_dict())
            if not G.has_node(str_v):
                G.add_node(str_v, **v.to_dict())
            if not G.has_edge(str_u, str_v):
                G.add_edge(str_u, str_v, relations=[])

            G[str_u][str_v]["relations"].append(edge.to_dict())

    for u, v, data in G.edges(data="relations"):
        relation = {d['relation'] for d in data}
        G[u][v]["label"] = "/".join(relation)

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


def dump_graph_as_ipysigma_graph(graph, output_file):
    G = stringify_graph(graph)
    # G = nx.DiGraph()
    # for i, relation in enumerate(EdgeRelation):
    #     if relation.value[2] == 1:
    #         continue
    #     sub_graph = graph.get_related_subgraph(relation, relation.get_inverse_kind())
    #     G = nx.compose(G, stringify_graph(sub_graph))

    # Displaying the graph with a size mapped on degree and
    # a color mapped on a categorical attribute of the nodes
    Sigma.write_html(
        graph=G,
        node_size=G.degree,
        node_color="type",
        edge_color="label",
        clickable_edges=True,
        default_edge_type="arrow",
        path=output_file,
        fullscreen=True,
    )


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
        case "ipysigma":
            dump_graph_as_ipysigma_graph(graph, output_file)
        case _:
            raise ValueError(f"Unknown output format: {output_format}")
