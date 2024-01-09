import argparse
from pathlib import Path

from dependency_graph import (
    construct_dependency_graph,
    dump_graph_as_edgelist,
    dump_graph_as_pyvis_graph,
)
from dependency_graph.graph_generator import DependencyGraphGeneratorType
from dependency_graph.models.repository import Repository

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Construct Dependency Graph for a given project."
    )
    parser.add_argument(
        "-r",
        "--repo",
        type=Path,
        required=True,
        help="The path to a local repository.",
    )

    parser.add_argument(
        "-l", "--lang", help="The language of the parsed file.", required=True
    )

    parser.add_argument(
        "-g",
        "--dependency_graph_generator",
        type=DependencyGraphGeneratorType,
        default=DependencyGraphGeneratorType.JEDI,
        help=f"The code agent type to use. Should be one of the {[g.value for g in DependencyGraphGeneratorType]}. Defaults to {DependencyGraphGeneratorType.JEDI.value}.",
    )

    # TODO add more output format
    parser.add_argument(
        "-f",
        "--output-format",
        help="The format of the output.",
        default="edgelist",
        required=False,
    )

    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        help="The path to the output file. If not specified, will print to stdout.",
        default=None,
        required=False,
    )

    args = parser.parse_args()

    lang = args.lang
    dependency_graph_generator = args.dependency_graph_generator
    repo = Repository(args.repo, lang)
    output_file: Path = args.output_file
    output_format: Path = args.output_format

    if output_file is not None and output_file.is_dir():
        raise IsADirectoryError(f"{output_file} is a directory.")

    graph = construct_dependency_graph(repo, dependency_graph_generator)

    # TODO move to another function
    if output_format == "edgelist":
        output = dump_graph_as_edgelist(graph)
        if output_file:
            output_file.write_text(str(output))
        else:
            print(dump_graph_as_edgelist(graph))
    elif output_format == "pyvis":
        dump_graph_as_pyvis_graph(graph, output_file)
    else:
        raise ValueError(f"Unknown output format: {output_format}")
