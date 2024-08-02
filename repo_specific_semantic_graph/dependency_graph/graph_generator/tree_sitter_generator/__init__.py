import traceback
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm
from tree_sitter import Node as TS_Node

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.graph_generator import BaseDependencyGraphGenerator
from dependency_graph.graph_generator.tree_sitter_generator.import_finder import (
    ImportFinder,
)
from dependency_graph.graph_generator.tree_sitter_generator.resolve_import import (
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
from dependency_graph.utils.log import setup_logger
from dependency_graph.utils.read_file import read_file_to_string

# Initialize logging
logger = setup_logger()


class TreeSitterDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = (
        Language.Python,
        Language.Java,
        Language.CSharp,
        Language.TypeScript,
        Language.JavaScript,
        Language.Kotlin,
        Language.PHP,
        Language.Ruby,
        Language.C,
        Language.CPP,
        Language.Go,
        Language.Swift,
        Language.Rust,
        Language.Lua,
        Language.Bash,
        Language.R,
    )

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
        resolver = ImportResolver(repo)

        for file in tqdm(repo.files, desc="Generating graph"):
            if not file.content.strip():
                continue

            if name := finder.find_module_name(file.file_path):
                module_map[name].append(file.file_path)
            nodes = finder.find_imports(file.content)
            import_map[(file.file_path, name)].extend(nodes)

        for (
            importer_file_path,
            importer_module_name,
        ), import_symbol_nodes in import_map.items():
            for import_symbol_node in import_symbol_nodes:
                resolved = []
                try:
                    resolved = resolver.resolve_import(
                        import_symbol_node, module_map, importer_file_path
                    )
                except Exception as e:
                    tb_str = "\n".join(traceback.format_tb(e.__traceback__))
                    logger.error(
                        f"Error {e} resolving import {import_symbol_node.text} in {importer_file_path}, will ignore: {tb_str}"
                    )

                for importee_file_path in resolved:
                    # Use read_file_to_string here to avoid non-UTF8 decoding issue
                    importer_node = finder.parser.parse(
                        read_file_to_string(importer_file_path).encode()
                    ).root_node

                    if (
                        not importee_file_path.exists()
                        or not importee_file_path.is_file()
                    ):
                        continue
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
                        start_line=import_symbol_node.start_point[0] + 1,
                        start_column=import_symbol_node.start_point[1] + 1,
                        end_line=import_symbol_node.end_point[0] + 1,
                        end_column=import_symbol_node.end_point[1] + 1,
                    )
                    D.add_relational_edge(
                        from_node,
                        to_node,
                        Edge(
                            relation=EdgeRelation.Imports,
                            location=import_location,
                        ),
                        Edge(
                            relation=EdgeRelation.ImportedBy,
                            location=import_location,
                        ),
                    )

        return D
