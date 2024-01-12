from pathlib import Path

import jedi
from jedi.api.classes import Name

from dependency_graph.graph_generator import (
    BaseDependencyGraphGenerator,
    DependencyGraphGeneratorType,
)
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
from dependency_graph.utils.log import setup_logger

# Initialize logging
logger = setup_logger()


class JediDependencyGraphGenerator(BaseDependencyGraphGenerator):
    supported_languages: tuple[Language] = (Language.Python,)

    def __init__(self, language: Language = Language.Python):
        super().__init__(language)

    def _convert_name_pos_to_location(self, name: Name) -> Location | None:
        """helper function for creating location"""
        if name is None:
            return None

        location_params = {"file_path": name.module_path}
        start_pos = name.get_definition_start_position()
        end_pos = name.get_definition_end_position()
        if start_pos:
            location_params.update(
                start_line=start_pos[0],
                start_column=start_pos[1] + 1,  # Convert to 1-based indexing
            )

        if end_pos:
            location_params.update(
                end_line=end_pos[0],
                end_column=end_pos[1] + 1,  # Convert to 1-based indexing
            )
        return Location(**location_params)

    def _convert_name_to_node(self, name: Name, node_type: NodeType) -> Node:
        """helper function for creating nodes"""
        location = self._convert_name_pos_to_location(name)
        return Node(
            type=node_type,
            name=name.name,
            location=location,
        )

    def _update_graph(
        self,
        D: DependencyGraph,
        from_name: Name,
        from_type: NodeType,
        to_name: Name,
        to_type: NodeType,
        edge_name: Name
        | None,  # Edge name can be None as not all relation have a location
        edge_relation: EdgeRelation,
        inverse_edge_relation: EdgeRelation,
    ):
        """helper function for updating the graph"""
        from_node = self._convert_name_to_node(from_name, from_type)
        to_node = self._convert_name_to_node(to_name, to_type)

        edge_location = self._convert_name_pos_to_location(edge_name)
        D.add_relational_edge(
            from_node,
            to_node,
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
            self._update_graph(
                D=D,
                from_name=parent,
                from_type=NodeType(parent.type).value,
                # TODO the name should be added with is class name if this is a method
                to_name=name,
                to_type=NodeType(name.type).value,
                edge_name=None,
                edge_relation=EdgeRelation.ParentOf,
                inverse_edge_relation=EdgeRelation.ChildOf,
            )

    def _extract_import_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
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
                from_name=script.get_context(),
                from_type=NodeType.MODULE.value,
                # TODO the name should be added with is class name if this is a method
                to_name=definition,
                to_type=NodeType.VARIABLE.value
                if definition.type == "statement"
                else NodeType(definition.type).value,
                edge_name=name,
                edge_relation=EdgeRelation.Imports,
                inverse_edge_relation=EdgeRelation.ImportedBy,
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
                from_name=caller,
                from_type=NodeType(caller.type).value,
                # TODO the name should be added with is class name if this is a method
                to_name=callee,
                to_type=NodeType.FUNCTION.value,
                edge_name=name,
                edge_relation=EdgeRelation.Calls,
                inverse_edge_relation=EdgeRelation.CalledBy,
            )

    def _extract_instantiate_relation(
        self,
        script: jedi.Script,
        all_names: list[Name],
        D: DependencyGraph,
    ):
        for name in all_names:
            if name.type not in ("statement", "param"):
                continue

            # Skip self
            if name.name == "self":
                continue

            # TODO a variable can also have an instance of another
            if name.parent().type not in ("class", "module", "function"):
                continue

            instance_types = name.infer()
            if not instance_types:
                continue

            instance_type = instance_types[0]
            # Skip builtin types
            if instance_type.in_builtin_module():
                continue

            instance_owner = name.parent()
            # Use the helper function to update the graph
            self._update_graph(
                D=D,
                from_name=instance_owner,
                from_type=NodeType(instance_owner.type).value,
                # TODO the name should be added with is class name if this is a method
                to_name=instance_type,
                to_type=NodeType.FUNCTION.value,
                edge_name=name,
                edge_relation=EdgeRelation.Instantiates,
                inverse_edge_relation=EdgeRelation.InstantiatedBy,
            )

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

            try:
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

                all_def_ref_names = script.get_names(
                    all_scopes=True, definitions=False, references=True
                )
                self._extract_instantiate_relation(script, all_def_ref_names, D)
                self._extract_type_relation(script, all_def_names, D)
            except Exception as e:
                logger.warn(
                    f"Error while generating graph of type {DependencyGraphGeneratorType.JEDI.value} for {file.file_path}, will ignore it. Error: {e}"
                )

        return D
