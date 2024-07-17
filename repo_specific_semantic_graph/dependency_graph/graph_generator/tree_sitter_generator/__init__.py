from collections import defaultdict
from pathlib import Path

from tqdm import tqdm
from tree_sitter import Node as TS_Node

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.graph_generator import BaseDependencyGraphGenerator
from dependency_graph.graph_generator.tree_sitter_generator.resolve_import import (
    ImportFinder,
    ImportResolver,
)
from dependency_graph.models import PathLike
from dependency_graph.models.graph_data import (
    Node,
    NodeType,
    Location,
    EdgeRelation,
    Edge,
)
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository
from dependency_graph.utils.read_file import read_file_to_string


class TreeSitterDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = (
        # Language.Python,
        Language.Java,
        Language.CSharp,
        Language.TypeScript,
        Language.JavaScript,
    )

    def __init__(self, language: Language):
        super().__init__(language)

    def generate_file(
        self,
        repo: Repository,
        code: str = None,
        file_path: PathLike = None,
    ) -> DependencyGraph:
        raise NotImplementedError("generate_file is not implemented")

    def generate(self, repo: Repository) -> DependencyGraph:
        D = DependencyGraph(repo.repo_path, repo.language)
        module_map: dict[str, list[Path]] = defaultdict(list)
        # The key is (file_path, class_name)
        import_map: dict[tuple[Path, str], list[TS_Node]] = defaultdict(list)
        finder = ImportFinder(repo.language)
        resolver = ImportResolver(repo.language)

        for file in tqdm(repo.files, desc="Generating graph"):
            if not file.content.strip():
                continue
            name = finder.find_module_name(file.file_path)
            module_map[name].append(file.file_path)
            nodes = finder.find_imports(file.content)
            import_map[(file.file_path, name)].extend(nodes)

        for (
            importer_file_path,
            importer_class_name,
        ), importation_nodes in import_map.items():
            for importation_node in importation_nodes:
                importee_class_name = importation_node.text.decode()

                if resolved := resolver.resolve_import(
                    importee_class_name, module_map, importer_file_path
                ):
                    # FIXME We only resolve the first found class
                    importee_file_path = resolved[0]
                    # Use read_file_to_string here to avoid non-UTF8 decoding issue
                    importer_node = finder.parser.parse(
                        read_file_to_string(importer_file_path).encode()
                    ).root_node
                    importee_node = finder.parser.parse(
                        read_file_to_string(importee_file_path).encode()
                    ).root_node

                    importer_module_name = finder.find_module_name(importer_file_path)
                    importee_module_name = finder.find_module_name(importee_file_path)

                    from_node = Node(
                        type=NodeType.MODULE,
                        name=importer_module_name,
                        location=Location(
                            file_path=importer_file_path,
                            start_line=importer_node.start_point[0] + 1,
                            start_column=importer_node.start_point[1] + 1,
                            end_line=importer_node.end_point[0] + 1,
                            end_column=importer_node.end_point[1] + 1,
                        ),
                    )
                    to_node = Node(
                        type=NodeType.MODULE,
                        name=importee_module_name,
                        location=Location(
                            file_path=importee_file_path,
                            start_line=importee_node.start_point[0] + 1,
                            start_column=importee_node.start_point[1] + 1,
                            end_line=importee_node.end_point[0] + 1,
                            end_column=importee_node.end_point[1] + 1,
                        ),
                    )
                    import_location = Location(
                        file_path=importer_file_path,
                        start_line=importation_node.start_point[0] + 1,
                        start_column=importation_node.start_point[1] + 1,
                        end_line=importation_node.end_point[0] + 1,
                        end_column=importation_node.end_point[1] + 1,
                    )
                    D.add_relational_edge(
                        from_node,
                        to_node,
                        Edge(
                            relation=EdgeRelation.Imports,
                            location=import_location,
                        ),
                        Edge(
                            relation=EdgeRelation.ImportedBy, location=import_location
                        ),
                    )

        return D
