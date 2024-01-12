import argparse
import json
from datetime import datetime
from pathlib import Path

from dependency_graph import (
    construct_dependency_graph,
    dump_graph_as_edgelist,
    dump_graph_as_pyvis_graph,
)
from dependency_graph.graph_generator import (
    DependencyGraphGeneratorType,
    DependencyGraph,
)
from dependency_graph.models import PathLike
from dependency_graph.models.repository import Repository
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()


OUTPUT_FORMATS = ["edgelist", "pyvis"]


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
            output = dump_graph_as_edgelist(graph)
            data = json.dumps(output)
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
        choices=OUTPUT_FORMATS,
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
    output_format: str = args.output_format

    if output_file is not None and output_file.is_dir():
        raise IsADirectoryError(f"{output_file} is a directory.")

    start_time = datetime.now()
    graph = construct_dependency_graph(repo, dependency_graph_generator)
    end_time = datetime.now()

    elapsed_time = (end_time - start_time).total_seconds()
    logger.info(f"Finished constructing the dependency graph in {elapsed_time} sec")

    output_dependency_graph(graph, output_format, output_file)
