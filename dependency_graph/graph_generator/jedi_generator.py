import jedi
from jedi.api.classes import Name

from dependency_graph.graph_generator import BaseDependencyGraphGenerator
from dependency_graph.models.dependency_graph import (
    DependencyGraph,
    Location,
    Node,
    EdgeRelation,
    Edge,
)
from dependency_graph.models.file_node import FileNode
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


class JediDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = [
        Language.Python,
    ]

    def __init__(self, language: Language = Language.Python):
        super().__init__(language)

    def _extract_import_relation(
        self, file: FileNode, project: jedi.Project, D: DependencyGraph
    ):
        script = jedi.Script(
            file.content,
            path=file.file_path,
            project=project,
        )

        all_scopes_names = script.get_names(
            all_scopes=True, definitions=False, references=True
        )

        for name in all_scopes_names:  # type: Name
            # Skip self
            if name.name == "self":
                continue

            definitions = name.get_signatures() or name.goto(
                follow_imports=True, follow_builtin_imports=False
            )
            if definitions:
                definition = definitions[0]

                # Skip builtin
                # Skip definition that are not in the project folder
                # Skip definition that are in the same file
                if (
                    definition.in_builtin_module()
                    or (
                        definition.module_path
                        and definition.module_path.is_relative_to(project.path)
                    )
                    or definition.module_path == file.file_path
                ):
                    continue

                # Lines in Jedi are always 1-based and columns are always zero based.
                ref_node = Node(
                    name=name.name,
                    location=Location(
                        file_path=file.file_path,
                        start_line=name.line,
                        start_column=name.column + 1,
                        end_line=name.line,
                        end_column=name.column + 1 + len(name.name),
                    ),
                )
                def_node = Node(
                    name=definition.name,
                    location=Location(
                        file_path=definition.module_path,
                        start_line=definition.line,
                        start_column=definition.column + 1,
                        end_line=definition.line,
                        end_column=definition.column + 1 + len(definition.name),
                    ),
                )

                D.add_node(ref_node)
                D.add_node(def_node)

                # import relation's edge would not have location
                D.add_relational_edge(
                    ref_node,
                    def_node,
                    Edge(location=None, relation=EdgeRelation.Imports),
                    Edge(location=None, relation=EdgeRelation.ImportedBy),
                )

    def generate(self, repo: Repository) -> DependencyGraph:
        project = jedi.Project(repo.repo_path, load_unsafe_extensions=False)

        D = DependencyGraph()
        # TODO implement more
        for file in repo.files:
            if not file.content.strip():
                continue

            self._extract_import_relation(file, project, D)

        return D
