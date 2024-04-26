# Dependency Graph

Construct a dependency graph of a project

## Install

```shell
poetry install
```

## Usage

### Command line usage

help:

```shell
python -m dependency_graph -h
```

### Python usage

```python
from dependency_graph import construct_dependency_graph
from dependency_graph.models.language import Language
from dependency_graph.graph_generator import DependencyGraphGeneratorType
from dependency_graph.models.repository import Repository

dependency_graph_generator = DependencyGraphGeneratorType.JEDI

repo = Repository('/path/to/repo', Language.Python)
graph = construct_dependency_graph(repo, dependency_graph_generator)
graph
```