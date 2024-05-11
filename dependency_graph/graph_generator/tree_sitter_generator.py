import platform
import sys
from collections import defaultdict
from pathlib import Path
from textwrap import dedent

from tree_sitter import Language as TS_Language, Parser, Tree, Node as TS_Node

from dependency_graph.dependency_graph import DependencyGraph
from dependency_graph.graph_generator import BaseDependencyGraphGenerator
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

TS_LIB_PATH = Path(__file__).parent.parent / "lib"


def get_builtin_lib_path(parent_dir: Path) -> Path:
    if sys.platform.startswith("linux"):
        lib_path = parent_dir / "languages-linux-x86_64.so"
    elif sys.platform == "darwin":
        machine = platform.machine()
        if machine == "x86_64":
            lib_path = parent_dir / "languages-darwin-x86_64.dylib"
        elif machine == "arm64":
            lib_path = parent_dir / "languages-darwin-arm64.dylib"
        else:
            raise RuntimeError("Unsupported Darwin platform: " + machine)
    else:
        raise RuntimeError("Unsupported platform: " + sys.platform)
    return lib_path


class TreeSitterDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = (
        # Language.Python,
        Language.Java,
    )

    def __init__(self, language: Language):
        super().__init__(language)

    def _generate_file(
        self,
        code: str,
        file_path: PathLike,
        parser: Parser,
        ts_language: TS_Language,
        classes_map: dict[str, list[Path]],
        import_map: dict[tuple[Path, str], list[TS_Node]],
    ):
        tree: Tree = parser.parse(code.encode())

        # Find package name in the file
        query = ts_language.query(
            dedent(
                """
                (package_declaration
                [
                  (identifier) @package_name
                  (scoped_identifier) @package_name
                ])
                """
            )
        )
        captures = query.captures(tree.root_node)

        class_name = ""
        for node, _ in captures:
            package_name = node.text.decode()
            class_name = f"{package_name}.{file_path.stem}"
            classes_map[class_name].append(file_path)

        # Find import name in the file and save it to import map
        query = ts_language.query(
            dedent(
                """
                (import_declaration
                [
                  (identifier) @import_name
                  (scoped_identifier) @import_name
                ])
                """
            )
        )
        captures = query.captures(tree.root_node)

        for node, _ in captures:
            import_map[(file_path, class_name)].append(node)

    def generate_file(
        self,
        repo: Repository,
        code: str = None,
        file_path: PathLike = None,
    ) -> DependencyGraph:
        raise NotImplementedError("generate_file is not implemented")

    def generate(self, repo: Repository) -> DependencyGraph:
        lib_path = get_builtin_lib_path(TS_LIB_PATH)

        # Initialize the Tree-sitter language
        ts_language = TS_Language(str(lib_path.absolute()), str(repo.language))
        parser = Parser()
        parser.set_language(ts_language)

        D = DependencyGraph(repo.repo_path, repo.language)
        classes_map: dict[str, list[Path]] = defaultdict(list)
        # The key is (file_path, class_name)
        import_map: dict[tuple[Path, str], list[TS_Node]] = defaultdict(list)
        for file in repo.files:
            if not file.content.strip():
                continue
            self._generate_file(
                file.content,
                file.file_path,
                parser,
                ts_language,
                classes_map,
                import_map,
            )

        for (
            importer_file_path,
            importer_class_name,
        ), importee_nodes in import_map.items():
            for importee_node in importee_nodes:
                importee_class_name = importee_node.text.decode()
                if (
                    importee_class_name in classes_map
                    and classes_map[importee_class_name]
                ):
                    # We only resolve the first found class
                    importee_file_path = classes_map[importee_class_name][0]
                    importer_node = parser.parse(
                        importer_file_path.read_bytes()
                    ).root_node
                    importee_node = parser.parse(
                        importee_file_path.read_bytes()
                    ).root_node
                    from_node = Node(
                        type=NodeType.MODULE,
                        name=importer_class_name,
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
                        name=importee_class_name,
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
                        start_line=importee_node.start_point[0] + 1,
                        start_column=importee_node.start_point[1] + 1,
                        end_line=importee_node.end_point[0] + 1,
                        end_column=importee_node.end_point[1] + 1,
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
