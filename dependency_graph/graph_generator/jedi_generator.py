from pathlib import Path

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
from dependency_graph.models.language import Language
from dependency_graph.models.repository import Repository


class JediDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = (Language.Python,)

    def __init__(self, language: Language = Language.Python):
        super().__init__(language)

    # New helper function for creating nodes
    def _update_graph(
        self,
        D: DependencyGraph,
        from_type: NodeType,
        from_name: str,
        from_path: Path,
        from_start_pos: tuple[int, int] | None,
        from_end_pos: tuple[int, int] | None,
        to_type: NodeType,
        to_name: str,
        to_path: Path,
        to_start_pos: tuple[int, int] | None,
        to_end_pos: tuple[int, int] | None,
        edge_relation: EdgeRelation,
        inverse_edge_relation: EdgeRelation,
        edge_location: Location | None,
    ):
        from_location_params = {"file_path": from_path}
        if from_start_pos:
            from_location_params.update(
                start_line=from_start_pos[0],
                start_column=from_start_pos[1] + 1,  # Convert to 1-based indexing
            )

        if from_end_pos:
            from_location_params.update(
                end_line=from_end_pos[0],
                end_column=from_end_pos[1] + 1,  # Convert to 1-based indexing
            )

        _from = Node(
            type=from_type,
            name=from_name,
            location=Location(**from_location_params),
        )

        to_location_params = {"file_path": to_path}
        if to_start_pos:
            to_location_params.update(
                start_line=to_start_pos[0],
                start_column=to_start_pos[1] + 1,  # Convert to 1-based indexing
            )

        if to_end_pos:
            to_location_params.update(
                end_line=to_end_pos[0],
                end_column=to_end_pos[1] + 1,  # Convert to 1-based indexing
            )

        _to = Node(
            type=to_type,
            name=to_name,
            location=Location(**to_location_params),
        )

        D.add_node(_from)
        D.add_node(_to)
        D.add_relational_edge(
            _from,
            _to,
            Edge(relation=edge_relation, location=edge_location),
            Edge(relation=inverse_edge_relation, location=edge_location),
        )

    def _extract_parent_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
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

            parent = name.parent()
            # Use the helper function to update the graph
            self._update_graph(
                D=D,
                from_type=NodeType(parent.type).value,
                from_name=parent.name,
                from_path=parent.module_path,
                from_start_pos=parent.get_definition_start_position(),  # Modules do not have a start or end position
                from_end_pos=parent.get_definition_end_position(),
                to_type=NodeType(name.type).value,
                # TODO the name should be added with is class name if this is a method
                to_name=name.name,
                to_path=name.module_path,
                to_start_pos=name.get_definition_start_position(),
                to_end_pos=name.get_definition_end_position(),
                edge_relation=EdgeRelation.ParentOf,
                inverse_edge_relation=EdgeRelation.ChildOf,
                edge_location=None,
            )

    def _extract_import_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        """
        TODO should we add import relation for the following case? In this case, all_scopes should be True
        def test():
            import os
            os.chdir(os.path.dirname(__file__))
        """
        for name in all_names:
            definitions = name.get_signatures() or name.goto(
                follow_imports=True, follow_builtin_imports=False
            )
            if not definitions:
                continue

            definition = definitions[0]

            # Skip instantiation, this should be dealt with in the instantiate relation
            if definition.type == "instance":
                continue

            # Skip definition that are in the same file
            if definition.module_path == script.path:
                continue

            # Use the helper function to update the graph
            self._update_graph(
                D=D,
                from_type=NodeType.MODULE.value,
                from_name=script.get_context().name,
                from_path=script.get_context().module_path,
                from_start_pos=None,
                from_end_pos=None,
                to_type=NodeType.VARIABLE.value
                if definition.type == "statement"
                else NodeType(definition.type).value,
                to_name=definition.name,
                to_path=definition.module_path,
                to_start_pos=definition.get_definition_start_position(),
                to_end_pos=definition.get_definition_end_position(),
                edge_relation=EdgeRelation.Imports,
                inverse_edge_relation=EdgeRelation.ImportedBy,
                edge_location=Location(
                    file_path=name.module_path,
                    start_line=name.get_definition_start_position()[0],
                    # Convert to 1-based indexing
                    start_column=name.get_definition_start_position()[1] + 1,
                    end_line=name.get_definition_end_position()[0],
                    end_column=name.get_definition_end_position()[1] + 1,
                ),
            )

    def _extract_call_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            callers = name.goto(follow_imports=True, follow_builtin_imports=True)
            if not callers:
                continue

            callee = callers[0]

            if not callee or callee.type != "function":
                continue

            # Find caller, caller should be a function
            if name.parent().type not in ("function", "module"):
                continue
            caller = name.parent()

            # Use the helper function to update the graph
            self._update_graph(
                D=D,
                from_type=NodeType(caller.type).value,
                from_name=caller.name,
                from_path=caller.module_path,
                # TODO find function position
                from_start_pos=caller.get_definition_start_position(),
                from_end_pos=caller.get_definition_end_position(),
                to_type=NodeType.FUNCTION.value,
                # TODO the name should be added with is class name if this is a method
                to_name=callee.name,
                to_path=callee.module_path,
                to_start_pos=callee.get_definition_start_position(),
                to_end_pos=callee.get_definition_end_position(),
                edge_relation=EdgeRelation.Calls,
                inverse_edge_relation=EdgeRelation.CalledBy,
                edge_location=Location(
                    file_path=name.module_path,
                    start_line=name.get_definition_start_position()[0],
                    # Convert to 1-based indexing
                    start_column=name.get_definition_start_position()[1] + 1,
                    end_line=name.get_definition_end_position()[0],
                    end_column=name.get_definition_end_position()[1] + 1,
                ),
            )

    def _extract_instantiate_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            if name.type not in ("class", "instance"):
                continue

    def _extract_type_relation(
        self,
        script: jedi.Script,
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
                all_scopes=True, definitions=True, references=False
            )
            self._extract_parent_relation(script, all_def_names, D)
            self._extract_import_relation(script, all_def_names, D)

            all_ref_names = script.get_names(
                all_scopes=True, definitions=False, references=True
            )
            self._extract_call_relation(script, all_ref_names, D)
            self._extract_instantiate_relation(script, all_def_names, D)
            self._extract_type_relation(script, all_def_names, D)

        return D
