import jedi
from jedi.api.classes import Name

from dependency_graph.graph_generator import BaseDependencyGraphGenerator
from dependency_graph.models.dependency_graph import (
    DependencyGraph,
    Location,
    Node,
    EdgeRelation,
    Edge,
    NodeType,
)
from dependency_graph.models.file_node import FileNode
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


class JediDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = (Language.Python,)

    def __init__(self, language: Language = Language.Python):
        super().__init__(language)

    def _extract_parent_relation(
        self,
        script: jedi.Script,
        project: jedi.Project,
        all_names: list[Name],
        D: DependencyGraph,
        root_node: Name = None,
    ):
        for name in all_names:
            # TODO missing adding global variable
            if name.type not in (
                "class",
                "function",
            ):
                continue

            definitions = name.get_signatures() or name.goto(
                follow_imports=True, follow_builtin_imports=False
            )
            if definitions:
                definition = definitions[0]

                # Skip builtin
                # Skip definition that are not in the same file
                if (
                    definition.in_builtin_module()
                    or not definition.module_path == script.path
                ):
                    continue

            if root_node is None:
                from_type = NodeType.MODULE.value
                from_name = script.path.name
            else:
                from_type = NodeType.CLASS.value
                from_name = root_node.name

            # a Module doesn't have a location
            _from = Node(
                type=from_type,
                name=from_name,
                location=Location(
                    file_path=script.path,
                ),
            )

            to_type = NodeType(name.type).value
            to_name = name.name
            if name.type == "function" and root_node:
                to_type = NodeType.METHOD.value
                to_name = f"{root_node.name}.{name.name}"

            # Get into its class definition body and get its location
            (start_line, start_column), (end_line, end_column) = (
                name._name.tree_name.parent.start_pos,
                name._name.tree_name.parent.end_pos,
            )

            start_column += 1
            end_column += 1
            _to = Node(
                type=to_type,
                name=to_name,
                location=Location(
                    file_path=name.module_path,
                    start_line=start_line,
                    start_column=start_column,
                    end_line=end_line,
                    end_column=end_column,
                ),
            )

            D.add_node(_from)
            D.add_node(_to)

            # import relation's edge would not have location
            D.add_relational_edge(
                _from,
                _to,
                Edge(location=None, relation=EdgeRelation.ParentOf),
                Edge(location=None, relation=EdgeRelation.ChildOf),
            )

            # Get method definition in class
            if name.type == "class":
                sub_names = name.defined_names()
                # Recursive call
                self._extract_parent_relation(
                    script, project, sub_names, D, root_node=name
                )

    def _extract_import_relation(
        self,
        script: jedi.Script,
        project: jedi.Project,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        pass

    def _extract_call_relation(
        self,
        script: jedi.Script,
        project: jedi.Project,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        pass

    def _extract_instantiate_relation(
        self,
        script: jedi.Script,
        project: jedi.Project,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        pass

    def _extract_type_relation(
        self,
        script: jedi.Script,
        project: jedi.Project,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        pass

    def generate(self, repo: Repository) -> DependencyGraph:
        project = jedi.Project(repo.repo_path, load_unsafe_extensions=False)

        D = DependencyGraph(repo.repo_path)
        for file in repo.files:
            if not file.content.strip():
                continue

            script = jedi.Script(
                file.content,
                path=file.file_path,
                project=project,
            )

            all_def_names = script.get_names(
                all_scopes=False, definitions=True, references=False
            )
            self._extract_parent_relation(script, project, all_def_names, D)
            self._extract_import_relation(script, project, all_def_names, D)
            self._extract_call_relation(script, project, all_def_names, D)
            self._extract_instantiate_relation(script, project, all_def_names, D)
            self._extract_type_relation(script, project, all_def_names, D)

        return D
