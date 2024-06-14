# Dependency Graph

Construct a dependency graph of a project.

## Features

1. Multi-language support: Python, Java, C#, JavaScript, TypeScript.
2. Retrieval of cross-file context from the dependency graph.
3. Serialization/Deserialization: edge list in JSON format is supported to output the graph. The graph can also be deserialized from JSON/Dictionary.
4. Graph visualizations: [Pyvis](https://pyvis.readthedocs.io/en/latest/) and [ipysigma](https://github.com/medialab/ipysigma) interactive visualizations are supported.

Currently, the following dependency graph generator types are supported, with the corresponding languages and dependency relations:
| **Graph Generator Type** | **Supported Languages**                                   | **Supported Dependency Relations**                                                                            |
|--------------------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Jedi                     | Python                                                    | ParentOf/ChildOf, Imports/ImportedBy, BaseClassOf/DerivedClassOf, Calls/CalledBy, Instantiates/InstantiatedBy, Defines/DefinedBy |
| Tree-sitter              | Java, C#, TypeScript, JavaScript                          | Imports/ImportedBy                                                                                            |

This table summarizes the capabilities of different graph generator types, including the languages they support and the types of dependency relations they can handle.

## Install

First, install poetry via <https://python-poetry.org/docs/#installation>, then run the following command to create a Python virtual environment and install the dependencies:

```shell
poetry install
# Activate the virtual environment
poetry shell
```

## Usage

### Command line usage to construct a dependency graph

See `python -m dependency_graph -h` for help:

```shell
~ python -m dependency_graph -h
usage: __main__.py [-h] -r REPO -l LANG [-g DEPENDENCY_GRAPH_GENERATOR] [-f {edgelist,pyvis,ipysigma}] [-o OUTPUT_FILE]

Construct Dependency Graph for a given project.

options:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  The path to a local repository.
  -l LANG, --lang LANG  The language of the parsed file.
  -g DEPENDENCY_GRAPH_GENERATOR, --dependency_graph_generator DEPENDENCY_GRAPH_GENERATOR
                        The code agent type to use. Should be one of the ['jedi', 'tree_sitter']. Defaults to jedi.
  -f {edgelist,pyvis,ipysigma}, --output-format {edgelist,pyvis,ipysigma}
                        The format of the output.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The path to the output file. If not specified, will print to stdout.
```

Example:

```shell
python -m dependency_graph -r </path/to/repo> -l python -g jedi -f edgelist -o edgelist.json
```

### Python API usage

#### Construct a dependency graph

```python
from dependency_graph import construct_dependency_graph
from dependency_graph.models.language import Language
from dependency_graph.graph_generator import DependencyGraphGeneratorType
from dependency_graph.models.repository import Repository

dependency_graph_generator = DependencyGraphGeneratorType.JEDI

repo = Repository('/path/to/repo', Language.Python)
graph = construct_dependency_graph(repo, dependency_graph_generator)
```

#### Output

```python
from dependency_graph import output_dependency_graph_generator

output_dependency_graph_generator(graph, "edgelist", "graph.json")
# Or
output_dependency_graph_generator(graph, "pyvis", "graph.html")
# Or
output_dependency_graph_generator(graph, "ipysigma", "graph.html")
```

#### Retrieval

Get cross-file context of a specific file path:

```python
graph.as_retriever().get_cross_file_context("/path/into/repo")
```

Get cross-file definition of a file by line:

```python
graph.as_retriever().get_cross_file_definition_by_line("/path/into/repo")
```

#### Filtering

For example, get call graph of the project:

```python
from dependency_graph.models.graph_data import EdgeRelation


graph.get_related_edges(EdgeRelation.Calls)
```
